/**
 * Camera Controller
 *
 * Third-person camera for the Tuath Celtic MMO.
 * Follows the player with smooth interpolation and collision detection.
 */

import {
  Scene,
  Vector3,
  ArcRotateCamera,
  type TransformNode,
  Ray,
} from '@babylonjs/core';

export interface CameraConfig {
  /** Distance from target */
  distance: number;
  /** Minimum distance */
  minDistance: number;
  /** Maximum distance */
  maxDistance: number;
  /** Height offset from target */
  heightOffset: number;
  /** Mouse sensitivity */
  sensitivity: number;
  /** Camera smoothing (0-1, lower = smoother) */
  smoothing: number;
  /** Minimum vertical angle (radians) */
  minBeta: number;
  /** Maximum vertical angle (radians) */
  maxBeta: number;
  /** Enable collision detection */
  enableCollision: boolean;
}

const DEFAULT_CONFIG: CameraConfig = {
  distance: 5.0,
  minDistance: 2.0,
  maxDistance: 15.0,
  heightOffset: 1.5,
  sensitivity: 0.005,
  smoothing: 0.1,
  minBeta: 0.1,
  maxBeta: Math.PI / 2 - 0.1,
  enableCollision: true,
};

export class CameraController {
  private scene: Scene;
  private config: CameraConfig;
  private camera: ArcRotateCamera;
  private target: TransformNode | null = null;

  // Camera state
  private targetDistance: number;
  private currentDistance: number;
  private isPointerLocked = false;

  constructor(scene: Scene, config: Partial<CameraConfig> = {}) {
    this.scene = scene;
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.targetDistance = this.config.distance;
    this.currentDistance = this.config.distance;

    // Create arc rotate camera
    this.camera = new ArcRotateCamera(
      'ThirdPersonCamera',
      -Math.PI / 2, // Alpha (horizontal rotation)
      Math.PI / 3, // Beta (vertical angle)
      this.config.distance,
      Vector3.Zero(),
      scene
    );

    this.setupCamera();
    this.setupInput();

    // Register update loop
    scene.registerBeforeRender(() => this.update());
  }

  /**
   * Setup camera properties
   */
  private setupCamera(): void {
    // Rotation limits
    this.camera.lowerBetaLimit = this.config.minBeta;
    this.camera.upperBetaLimit = this.config.maxBeta;

    // Distance limits
    this.camera.lowerRadiusLimit = this.config.minDistance;
    this.camera.upperRadiusLimit = this.config.maxDistance;

    // Smooth movement
    this.camera.inertia = 0.7;

    // Disable default camera controls (we handle input ourselves)
    this.camera.inputs.clear();

    // Attach to canvas but without default inputs
    this.camera.attachControl(
      this.scene.getEngine().getRenderingCanvas()!,
      true
    );
  }

  /**
   * Setup mouse input for camera rotation
   */
  private setupInput(): void {
    const canvas = this.scene.getEngine().getRenderingCanvas();
    if (!canvas) return;

    // Pointer lock state
    document.addEventListener('pointerlockchange', () => {
      this.isPointerLocked = document.pointerLockElement === canvas;
    });

    // Mouse move for camera rotation
    canvas.addEventListener('mousemove', (event) => {
      if (!this.isPointerLocked) return;

      const deltaX = event.movementX * this.config.sensitivity;
      const deltaY = event.movementY * this.config.sensitivity;

      // Rotate camera
      this.camera.alpha -= deltaX;
      this.camera.beta += deltaY;

      // Clamp beta
      this.camera.beta = Math.max(
        this.config.minBeta,
        Math.min(this.config.maxBeta, this.camera.beta)
      );
    });

    // Mouse wheel for zoom
    canvas.addEventListener('wheel', (event) => {
      const delta = event.deltaY * 0.01;
      this.targetDistance = Math.max(
        this.config.minDistance,
        Math.min(this.config.maxDistance, this.targetDistance + delta)
      );
      event.preventDefault();
    });
  }

  /**
   * Update camera each frame
   */
  private update(): void {
    if (!this.target) return;

    // Calculate target position with height offset
    const targetPosition = this.target.position.clone();
    targetPosition.y += this.config.heightOffset;

    // Smooth camera target position
    this.camera.target = Vector3.Lerp(
      this.camera.target,
      targetPosition,
      this.config.smoothing
    );

    // Handle camera collision
    if (this.config.enableCollision) {
      this.handleCollision(targetPosition);
    } else {
      // Smooth distance interpolation
      this.currentDistance = this.currentDistance +
        (this.targetDistance - this.currentDistance) * this.config.smoothing;
      this.camera.radius = this.currentDistance;
    }
  }

  /**
   * Handle camera collision with environment
   */
  private handleCollision(targetPosition: Vector3): void {
    // Calculate camera direction from target
    const cameraDirection = this.camera.position.subtract(targetPosition).normalize();

    // Cast ray from target to camera position
    const ray = new Ray(targetPosition, cameraDirection, this.targetDistance);
    const pickInfo = this.scene.pickWithRay(ray, (mesh) => {
      // Ignore player and non-collision meshes
      return mesh.checkCollisions && !mesh.name.startsWith('Player');
    });

    // Adjust distance if collision detected
    let desiredDistance = this.targetDistance;
    if (pickInfo?.hit && pickInfo.distance < this.targetDistance) {
      desiredDistance = Math.max(this.config.minDistance, pickInfo.distance - 0.5);
    }

    // Smooth distance interpolation
    this.currentDistance = this.currentDistance +
      (desiredDistance - this.currentDistance) * this.config.smoothing * 2;
    this.camera.radius = this.currentDistance;
  }

  // ============ Public API ============

  /**
   * Set the camera target (usually the player)
   */
  setTarget(target: TransformNode): void {
    this.target = target;
    this.camera.target = target.position.clone();
    this.camera.target.y += this.config.heightOffset;
  }

  /**
   * Get the camera
   */
  getCamera(): ArcRotateCamera {
    return this.camera;
  }

  /**
   * Get camera forward direction (for player rotation)
   */
  getForwardDirection(): Vector3 {
    // Get direction camera is looking (without vertical component)
    const forward = new Vector3(
      Math.sin(this.camera.alpha),
      0,
      Math.cos(this.camera.alpha)
    );
    return forward.normalize();
  }

  /**
   * Get camera alpha (horizontal rotation)
   */
  getAlpha(): number {
    return this.camera.alpha;
  }

  /**
   * Set camera distance
   */
  setDistance(distance: number): void {
    this.targetDistance = Math.max(
      this.config.minDistance,
      Math.min(this.config.maxDistance, distance)
    );
  }

  /**
   * Reset camera to default position
   */
  reset(): void {
    this.camera.alpha = -Math.PI / 2;
    this.camera.beta = Math.PI / 3;
    this.targetDistance = this.config.distance;
  }

  /**
   * Dispose camera controller
   */
  dispose(): void {
    this.camera.dispose();
  }
}
