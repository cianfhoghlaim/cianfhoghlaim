/**
 * Scene Manager
 *
 * Manages scene lifecycle, zone transitions, and asset loading
 * for the Tuath Celtic MMO web client.
 */

import {
  Scene,
  AssetsManager,
  type AbstractEngine,
} from '@babylonjs/core';

import type { BaseZone } from '../scenes/base-zone';

export type ZoneId = 'gaeltacht' | 'alba' | 'cymru';

export interface ZoneRegistry {
  gaeltacht: () => Promise<{ default: new (scene: Scene) => BaseZone }>;
  alba: () => Promise<{ default: new (scene: Scene) => BaseZone }>;
  cymru: () => Promise<{ default: new (scene: Scene) => BaseZone }>;
}

export interface SceneManagerConfig {
  engine: AbstractEngine;
  scene: Scene;
  onLoadProgress?: (progress: number) => void;
  onZoneChange?: (zoneId: ZoneId) => void;
}

export class SceneManager {
  private engine: AbstractEngine;
  private scene: Scene;
  private currentZone: BaseZone | null = null;
  private currentZoneId: ZoneId | null = null;
  private assetsManager: AssetsManager;
  private onLoadProgress?: (progress: number) => void;
  private onZoneChange?: (zoneId: ZoneId) => void;

  // Lazy-loaded zone modules
  private zoneRegistry: ZoneRegistry = {
    gaeltacht: () => import('../scenes/gaeltacht'),
    alba: () => import('../scenes/alba'),
    cymru: () => import('../scenes/cymru'),
  };

  constructor(config: SceneManagerConfig) {
    this.engine = config.engine;
    this.scene = config.scene;
    this.onLoadProgress = config.onLoadProgress;
    this.onZoneChange = config.onZoneChange;

    this.assetsManager = new AssetsManager(this.scene);
    this.setupAssetsManager();
  }

  private setupAssetsManager(): void {
    this.assetsManager.onProgress = (remainingCount, totalCount) => {
      const progress = ((totalCount - remainingCount) / totalCount) * 100;
      this.onLoadProgress?.(progress);
    };

    this.assetsManager.onFinish = () => {
      this.onLoadProgress?.(100);
    };
  }

  /**
   * Load a zone by ID
   */
  async loadZone(zoneId: ZoneId): Promise<void> {
    // Skip if already in this zone
    if (this.currentZoneId === zoneId) {
      return;
    }

    console.log(`[SceneManager] Loading zone: ${zoneId}`);

    // Cleanup current zone
    if (this.currentZone) {
      await this.unloadCurrentZone();
    }

    // Load zone module dynamically
    const zoneLoader = this.zoneRegistry[zoneId];
    if (!zoneLoader) {
      throw new Error(`Unknown zone: ${zoneId}`);
    }

    this.onLoadProgress?.(0);

    try {
      const { default: ZoneClass } = await zoneLoader();
      this.currentZone = new ZoneClass(this.scene);
      this.currentZoneId = zoneId;

      // Initialize the zone
      await this.currentZone.initialize();

      this.onZoneChange?.(zoneId);
      console.log(`[SceneManager] Zone loaded: ${zoneId}`);
    } catch (error) {
      console.error(`[SceneManager] Failed to load zone: ${zoneId}`, error);
      throw error;
    }
  }

  /**
   * Unload the current zone
   */
  private async unloadCurrentZone(): Promise<void> {
    if (this.currentZone) {
      console.log(`[SceneManager] Unloading zone: ${this.currentZoneId}`);
      await this.currentZone.dispose();
      this.currentZone = null;
      this.currentZoneId = null;
    }
  }

  /**
   * Get the current zone
   */
  getCurrentZone(): BaseZone | null {
    return this.currentZone;
  }

  /**
   * Get the current zone ID
   */
  getCurrentZoneId(): ZoneId | null {
    return this.currentZoneId;
  }

  /**
   * Get the assets manager for loading resources
   */
  getAssetsManager(): AssetsManager {
    return this.assetsManager;
  }

  /**
   * Dispose the scene manager
   */
  dispose(): void {
    if (this.currentZone) {
      this.currentZone.dispose();
    }
    this.assetsManager.reset();
  }
}
