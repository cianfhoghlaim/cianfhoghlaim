/**
 * Base Zone
 *
 * Abstract base class for all Celtic zones in the Tuath MMO.
 * Provides common functionality for environment, terrain, and player management.
 */

import {
  Scene,
  Vector3,
  Color3,
  Color4,
  DirectionalLight,
  HemisphericLight,
  MeshBuilder,
  StandardMaterial,
  CubeTexture,
  type AbstractMesh,
  type TransformNode,
} from '@babylonjs/core';

export type Weather = 'clear' | 'cloudy' | 'rainy' | 'foggy' | 'stormy';
export type TimeOfDay = 'dawn' | 'morning' | 'noon' | 'afternoon' | 'dusk' | 'night';

export interface SubRegion {
  id: string;
  displayName: string;
  celticName: string;
  spawnPoint: Vector3;
  bounds: { min: Vector3; max: Vector3 };
}

export interface ZoneConfig {
  zoneId: string;
  displayName: string;
  celticName: string;
  language: 'irish' | 'scottish-gaelic' | 'welsh';
  subRegions: SubRegion[];
  defaultWeather: Weather;
  defaultTimeOfDay: TimeOfDay;
  ambientTrack: string;
  musicTrack: string;
  fogDensity: number;
  ambientColor: Color3;
  skyColor: Color4;
}

export abstract class BaseZone {
  protected scene: Scene;
  protected config: ZoneConfig;

  // Environment
  protected sunLight: DirectionalLight | null = null;
  protected ambientLight: HemisphericLight | null = null;
  protected skybox: AbstractMesh | null = null;
  protected terrain: AbstractMesh | null = null;

  // State
  protected currentRegion: SubRegion | null = null;
  protected currentWeather: Weather;
  protected currentTimeOfDay: TimeOfDay;
  protected playerCount = 0;

  // Node containers
  protected environmentNode: TransformNode | null = null;
  protected terrainNode: TransformNode | null = null;
  protected npcsNode: TransformNode | null = null;
  protected interactablesNode: TransformNode | null = null;

  constructor(scene: Scene, config: ZoneConfig) {
    this.scene = scene;
    this.config = config;
    this.currentWeather = config.defaultWeather;
    this.currentTimeOfDay = config.defaultTimeOfDay;
  }

  /**
   * Initialize the zone
   */
  async initialize(): Promise<void> {
    console.log(`[Zone] Initializing: ${this.config.displayName} (${this.config.celticName})`);

    // Set scene clear color
    this.scene.clearColor = this.config.skyColor;

    // Create node hierarchy
    this.createNodeHierarchy();

    // Create environment
    await this.createEnvironment();

    // Create terrain
    await this.createTerrain();

    // Setup spawn points
    this.setupSpawnPoints();

    // Set default region
    if (this.config.subRegions.length > 0) {
      this.currentRegion = this.config.subRegions[0];
    }

    console.log(`[Zone] Ready: ${this.config.displayName}`);
  }

  /**
   * Create the node hierarchy for organization
   */
  protected createNodeHierarchy(): void {
    this.environmentNode = new TransformNode('Environment', this.scene);
    this.terrainNode = new TransformNode('Terrain', this.scene);
    this.npcsNode = new TransformNode('NPCs', this.scene);
    this.interactablesNode = new TransformNode('Interactables', this.scene);
  }

  /**
   * Create environment (sky, lights, fog)
   */
  protected async createEnvironment(): Promise<void> {
    // Directional light (sun)
    this.sunLight = new DirectionalLight(
      'sunLight',
      new Vector3(-0.5, -1, -0.5),
      this.scene
    );
    this.sunLight.intensity = 0.8;
    this.sunLight.diffuse = new Color3(1, 0.95, 0.9);

    // Ambient light
    this.ambientLight = new HemisphericLight(
      'ambientLight',
      new Vector3(0, 1, 0),
      this.scene
    );
    this.ambientLight.intensity = 0.5;
    this.ambientLight.diffuse = this.config.ambientColor;
    this.ambientLight.groundColor = this.config.ambientColor.scale(0.5);

    // Fog
    this.scene.fogMode = Scene.FOGMODE_EXP2;
    this.scene.fogDensity = this.config.fogDensity;
    this.scene.fogColor = new Color3(
      this.config.skyColor.r,
      this.config.skyColor.g,
      this.config.skyColor.b
    );

    // Skybox (procedural for now, can be replaced with HDR)
    this.skybox = MeshBuilder.CreateBox('skybox', { size: 1000 }, this.scene);
    const skyboxMaterial = new StandardMaterial('skyboxMat', this.scene);
    skyboxMaterial.backFaceCulling = false;
    skyboxMaterial.disableLighting = true;
    skyboxMaterial.diffuseColor = new Color3(0, 0, 0);
    skyboxMaterial.specularColor = new Color3(0, 0, 0);
    skyboxMaterial.emissiveColor = new Color3(
      this.config.skyColor.r * 0.5,
      this.config.skyColor.g * 0.5,
      this.config.skyColor.b * 0.5
    );
    this.skybox.material = skyboxMaterial;
    this.skybox.infiniteDistance = true;

    if (this.environmentNode) {
      this.sunLight.parent = this.environmentNode;
      this.ambientLight.parent = this.environmentNode;
      this.skybox.parent = this.environmentNode;
    }
  }

  /**
   * Create terrain - override in subclass for specific terrain
   */
  protected async createTerrain(): Promise<void> {
    // Default ground plane
    this.terrain = MeshBuilder.CreateGround(
      'ground',
      { width: 500, height: 500, subdivisions: 64 },
      this.scene
    );

    const groundMaterial = new StandardMaterial('groundMat', this.scene);
    groundMaterial.diffuseColor = new Color3(0.2, 0.35, 0.2); // Celtic green
    groundMaterial.specularColor = new Color3(0.1, 0.1, 0.1);
    this.terrain.material = groundMaterial;
    this.terrain.receiveShadows = true;
    this.terrain.checkCollisions = true;

    if (this.terrainNode) {
      this.terrain.parent = this.terrainNode;
    }
  }

  /**
   * Setup spawn points for each sub-region
   */
  protected setupSpawnPoints(): void {
    // Spawn points are defined in config.subRegions
    // They can be visualized in debug mode
  }

  /**
   * Get spawn point for a region (or default)
   */
  getSpawnPoint(regionId?: string): Vector3 {
    if (regionId) {
      const region = this.config.subRegions.find((r) => r.id === regionId);
      if (region) {
        return region.spawnPoint.clone();
      }
    }

    // Default spawn point
    return this.config.subRegions[0]?.spawnPoint.clone() ?? new Vector3(0, 2, 0);
  }

  /**
   * Set the current sub-region
   */
  setRegion(regionId: string): void {
    const region = this.config.subRegions.find((r) => r.id === regionId);
    if (region) {
      this.currentRegion = region;
      this.onRegionChange(region);
    }
  }

  /**
   * Called when region changes - override for custom behavior
   */
  protected onRegionChange(region: SubRegion): void {
    console.log(`[Zone] Region changed to: ${region.displayName} (${region.celticName})`);
  }

  /**
   * Called when a player enters the zone
   */
  onPlayerEnter(playerId: string): void {
    this.playerCount++;
    console.log(`[Zone] Player ${playerId} entered ${this.config.celticName}`);
  }

  /**
   * Called when a player exits the zone
   */
  onPlayerExit(playerId: string): void {
    this.playerCount = Math.max(0, this.playerCount - 1);
    console.log(`[Zone] Player ${playerId} exited ${this.config.celticName}`);
  }

  /**
   * Set weather
   */
  setWeather(weather: Weather): void {
    this.currentWeather = weather;
    this.updateWeatherEffects();
  }

  /**
   * Update weather effects based on current weather
   */
  protected updateWeatherEffects(): void {
    // Override in subclass for weather-specific effects
    switch (this.currentWeather) {
      case 'foggy':
        this.scene.fogDensity = this.config.fogDensity * 3;
        break;
      case 'rainy':
        this.scene.fogDensity = this.config.fogDensity * 2;
        break;
      case 'cloudy':
        this.scene.fogDensity = this.config.fogDensity * 1.5;
        if (this.sunLight) this.sunLight.intensity = 0.6;
        break;
      case 'clear':
      default:
        this.scene.fogDensity = this.config.fogDensity;
        if (this.sunLight) this.sunLight.intensity = 0.8;
        break;
    }
  }

  /**
   * Set time of day
   */
  setTimeOfDay(time: TimeOfDay): void {
    this.currentTimeOfDay = time;
    this.updateTimeOfDayEffects();
  }

  /**
   * Update lighting based on time of day
   */
  protected updateTimeOfDayEffects(): void {
    // Override in subclass for time-specific effects
    if (!this.sunLight || !this.ambientLight) return;

    switch (this.currentTimeOfDay) {
      case 'dawn':
        this.sunLight.intensity = 0.4;
        this.sunLight.diffuse = new Color3(1, 0.7, 0.5);
        this.ambientLight.intensity = 0.3;
        break;
      case 'morning':
        this.sunLight.intensity = 0.7;
        this.sunLight.diffuse = new Color3(1, 0.9, 0.8);
        this.ambientLight.intensity = 0.4;
        break;
      case 'noon':
        this.sunLight.intensity = 1.0;
        this.sunLight.diffuse = new Color3(1, 1, 0.95);
        this.ambientLight.intensity = 0.5;
        break;
      case 'afternoon':
        this.sunLight.intensity = 0.8;
        this.sunLight.diffuse = new Color3(1, 0.95, 0.9);
        this.ambientLight.intensity = 0.5;
        break;
      case 'dusk':
        this.sunLight.intensity = 0.4;
        this.sunLight.diffuse = new Color3(1, 0.6, 0.4);
        this.ambientLight.intensity = 0.3;
        break;
      case 'night':
        this.sunLight.intensity = 0.1;
        this.sunLight.diffuse = new Color3(0.5, 0.5, 0.7);
        this.ambientLight.intensity = 0.2;
        break;
    }
  }

  // ============ Getters ============

  getConfig(): ZoneConfig {
    return this.config;
  }

  getCurrentRegion(): SubRegion | null {
    return this.currentRegion;
  }

  getPlayerCount(): number {
    return this.playerCount;
  }

  getWeather(): Weather {
    return this.currentWeather;
  }

  getTimeOfDay(): TimeOfDay {
    return this.currentTimeOfDay;
  }

  /**
   * Dispose the zone and cleanup resources
   */
  dispose(): void {
    console.log(`[Zone] Disposing: ${this.config.displayName}`);

    this.skybox?.dispose();
    this.terrain?.dispose();
    this.sunLight?.dispose();
    this.ambientLight?.dispose();

    this.environmentNode?.dispose();
    this.terrainNode?.dispose();
    this.npcsNode?.dispose();
    this.interactablesNode?.dispose();
  }
}
