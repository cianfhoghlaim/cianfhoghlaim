/**
 * Player Controller
 *
 * Local player movement and physics for the Tuath Celtic MMO.
 * Uses Babylon.js CharacterController pattern with WASD controls.
 * Key bindings match Godot client for cross-platform consistency.
 */

import {
  Scene,
  Vector3,
  Quaternion,
  TransformNode,
  MeshBuilder,
  StandardMaterial,
  Color3,
  ActionManager,
  ExecuteCodeAction,
  type AbstractMesh,
  Ray,
} from '@babylonjs/core';

export interface PlayerConfig {
  /** Movement speed (units/second) */
  moveSpeed: number;
  /** Sprint multiplier */
  sprintMultiplier: number;
  /** Jump force */
  jumpForce: number;
  /** Gravity */
  gravity: number;
  /** Turn speed (radians/second) */
  turnSpeed: number;
  /** Ground check distance */
  groundCheckDistance: number;
}

export interface InputState {
  forward: boolean;
  backward: boolean;
  left: boolean;
  right: boolean;
  jump: boolean;
  sprint: boolean;
  interact: boolean;
}

const DEFAULT_CONFIG: PlayerConfig = {
  moveSpeed: 5.0,
  sprintMultiplier: 1.8,
  jumpForce: 8.0,
  gravity: 20.0,
  turnSpeed: 5.0,
  groundCheckDistance: 0.2,
};

export class PlayerController {
  private scene: Scene;
  private config: PlayerConfig;

  // Node hierarchy
  private rootNode: TransformNode;
  private mesh: AbstractMesh;

  // Physics state
  private velocity: Vector3 = Vector3.Zero();
  private isGrounded = false;
  private isJumping = false;

  // Input state
  private input: InputState = {
    forward: false,
    backward: false,
    left: false,
    right: false,
    jump: false,
    sprint: false,
    interact: false,
  };

  // Network sync
  private lastSyncTime = 0;
  private syncInterval = 50; // 20Hz = 50ms
  private onPositionUpdate?: (position: Vector3, rotation: number) => void;

  // Key bindings (matching Godot)
  private keyMap: Record<string, keyof InputState> = {
    KeyW: 'forward',
    KeyS: 'backward',
    KeyA: 'left',
    KeyD: 'right',
    Space: 'jump',
    ShiftLeft: 'sprint',
    ShiftRight: 'sprint',
    KeyE: 'interact',
  };

  constructor(scene: Scene, config: Partial<PlayerConfig> = {}) {
    this.scene = scene;
    this.config = { ...DEFAULT_CONFIG, ...config };

    // Create player node hierarchy
    this.rootNode = new TransformNode('PlayerRoot', scene);
    this.mesh = this.createPlayerMesh();

    // Setup input handling
    this.setupInput();

    // Register update loop
    scene.registerBeforeRender(() => this.update());
  }

  /**
   * Create a placeholder player mesh (capsule shape)
   */
  private createPlayerMesh(): AbstractMesh {
    // Create a capsule-like shape for the player
    const body = MeshBuilder.CreateCapsule(
      'PlayerBody',
      {
        height: 1.8,
        radius: 0.4,
        tessellation: 16,
        subdivisions: 1,
      },
      this.scene
    );

    // Position so bottom is at origin
    body.position.y = 0.9;
    body.parent = this.rootNode;

    // Simple material
    const material = new StandardMaterial('PlayerMaterial', this.scene);
    material.diffuseColor = new Color3(0.2, 0.6, 0.8); // Celtic blue
    material.specularColor = new Color3(0.1, 0.1, 0.1);
    body.material = material;

    // Enable collisions
    body.checkCollisions = true;

    return body;
  }

  /**
   * Setup keyboard input handling
   */
  private setupInput(): void {
    // Keyboard down
    window.addEventListener('keydown', (event) => {
      const action = this.keyMap[event.code];
      if (action) {
        this.input[action] = true;
        event.preventDefault();
      }
    });

    // Keyboard up
    window.addEventListener('keyup', (event) => {
      const action = this.keyMap[event.code];
      if (action) {
        this.input[action] = false;
      }
    });

    // Pointer lock for mouse look
    this.scene.getEngine().getRenderingCanvas()?.addEventListener('click', () => {
      this.scene.getEngine().getRenderingCanvas()?.requestPointerLock();
    });
  }

  /**
   * Main update loop (called every frame)
   */
  private update(): void {
    const deltaTime = this.scene.getEngine().getDeltaTime() / 1000;

    // Ground check
    this.checkGround();

    // Calculate movement direction
    const moveDirection = this.calculateMoveDirection();

    // Apply movement
    this.applyMovement(moveDirection, deltaTime);

    // Apply gravity and jumping
    this.applyGravity(deltaTime);

    // Apply velocity to position
    this.applyVelocity(deltaTime);

    // Handle interaction
    if (this.input.interact) {
      this.input.interact = false; // One-shot
      this.handleInteraction();
    }

    // Network sync at 20Hz
    this.syncPosition();
  }

  /**
   * Check if player is grounded
   */
  private checkGround(): void {
    const origin = this.rootNode.position.clone();
    origin.y += 0.1; // Start slightly above feet

    const ray = new Ray(origin, Vector3.Down(), this.config.groundCheckDistance + 0.1);
    const pickInfo = this.scene.pickWithRay(ray, (mesh) => {
      return mesh !== this.mesh && mesh.checkCollisions;
    });

    this.isGrounded = pickInfo?.hit ?? false;
  }

  /**
   * Calculate movement direction from input
   */
  private calculateMoveDirection(): Vector3 {
    const direction = Vector3.Zero();

    if (this.input.forward) direction.z += 1;
    if (this.input.backward) direction.z -= 1;
    if (this.input.left) direction.x -= 1;
    if (this.input.right) direction.x += 1;

    // Normalize diagonal movement
    if (direction.length() > 0) {
      direction.normalize();
    }

    // Transform direction to world space based on rotation
    const rotationQuaternion = Quaternion.RotationYawPitchRoll(
      this.rootNode.rotation.y,
      0,
      0
    );
    const worldDirection = Vector3.Zero();
    direction.rotateByQuaternionToRef(rotationQuaternion, worldDirection);

    return worldDirection;
  }

  /**
   * Apply horizontal movement
   */
  private applyMovement(direction: Vector3, deltaTime: number): void {
    if (direction.length() === 0) {
      // Decelerate when no input
      this.velocity.x *= 0.9;
      this.velocity.z *= 0.9;
      return;
    }

    // Calculate speed
    let speed = this.config.moveSpeed;
    if (this.input.sprint && this.isGrounded) {
      speed *= this.config.sprintMultiplier;
    }

    // Apply movement
    this.velocity.x = direction.x * speed;
    this.velocity.z = direction.z * speed;
  }

  /**
   * Apply gravity and handle jumping
   */
  private applyGravity(deltaTime: number): void {
    // Jumping
    if (this.input.jump && this.isGrounded && !this.isJumping) {
      this.velocity.y = this.config.jumpForce;
      this.isJumping = true;
      this.isGrounded = false;
    }

    // Reset jump state when landing
    if (this.isGrounded && this.isJumping) {
      this.isJumping = false;
    }

    // Apply gravity when airborne
    if (!this.isGrounded) {
      this.velocity.y -= this.config.gravity * deltaTime;
    } else if (this.velocity.y < 0) {
      this.velocity.y = 0;
    }
  }

  /**
   * Apply velocity to position
   */
  private applyVelocity(deltaTime: number): void {
    const movement = this.velocity.scale(deltaTime);
    this.rootNode.position.addInPlace(movement);

    // Clamp to ground when grounded
    if (this.isGrounded && this.rootNode.position.y < 0) {
      this.rootNode.position.y = 0;
    }
  }

  /**
   * Handle interaction input
   */
  private handleInteraction(): void {
    // Raycast forward to find interactable objects
    const origin = this.rootNode.position.clone();
    origin.y += 1.0; // Eye height

    const forward = new Vector3(0, 0, 1);
    const rotationQuaternion = Quaternion.RotationYawPitchRoll(
      this.rootNode.rotation.y,
      0,
      0
    );
    const worldForward = Vector3.Zero();
    forward.rotateByQuaternionToRef(rotationQuaternion, worldForward);

    const ray = new Ray(origin, worldForward, 3.0);
    const pickInfo = this.scene.pickWithRay(ray, (mesh) => {
      return mesh.metadata?.interactable === true;
    });

    if (pickInfo?.hit && pickInfo.pickedMesh) {
      console.log('[Player] Interacting with:', pickInfo.pickedMesh.name);
      // Emit interaction event
    }
  }

  /**
   * Sync position to network at 20Hz
   */
  private syncPosition(): void {
    const now = performance.now();
    if (now - this.lastSyncTime < this.syncInterval) {
      return;
    }

    this.lastSyncTime = now;

    if (this.onPositionUpdate) {
      this.onPositionUpdate(
        this.rootNode.position.clone(),
        this.rootNode.rotation.y
      );
    }
  }

  // ============ Public API ============

  /**
   * Set player position
   */
  setPosition(position: Vector3): void {
    this.rootNode.position = position;
    this.velocity = Vector3.Zero();
  }

  /**
   * Set player rotation (Y axis only)
   */
  setRotation(rotation: number): void {
    this.rootNode.rotation.y = rotation;
  }

  /**
   * Rotate player by delta
   */
  rotate(deltaYaw: number): void {
    this.rootNode.rotation.y += deltaYaw;
  }

  /**
   * Get current position
   */
  getPosition(): Vector3 {
    return this.rootNode.position.clone();
  }

  /**
   * Get current rotation (Y axis)
   */
  getRotation(): number {
    return this.rootNode.rotation.y;
  }

  /**
   * Get the root transform node
   */
  getRootNode(): TransformNode {
    return this.rootNode;
  }

  /**
   * Get the player mesh
   */
  getMesh(): AbstractMesh {
    return this.mesh;
  }

  /**
   * Is player currently grounded?
   */
  getIsGrounded(): boolean {
    return this.isGrounded;
  }

  /**
   * Is player currently sprinting?
   */
  getIsSprinting(): boolean {
    return this.input.sprint && this.isGrounded;
  }

  /**
   * Set callback for position updates (network sync)
   */
  setPositionUpdateCallback(callback: (position: Vector3, rotation: number) => void): void {
    this.onPositionUpdate = callback;
  }

  /**
   * Dispose player controller
   */
  dispose(): void {
    this.mesh.dispose();
    this.rootNode.dispose();
  }
}
