/**
 * Gaeltacht Zone
 *
 * Irish-speaking regions featuring:
 * - Connemara (Conamara)
 * - Dingle Peninsula (Corca Dhuibhne)
 * - Donegal Gaeltacht (Gaoth Dobhair)
 * - Aran Islands (Oileáin Árann)
 * - Ring of Kerry (Ciarraí)
 *
 * This zone mirrors the Godot client's GaeltachtZone for visual parity.
 */

import { Vector3, Color3, Color4, Scene } from '@babylonjs/core';
import { BaseZone, type ZoneConfig, type SubRegion } from '../base-zone';

// Sub-regions within the Gaeltacht
const GAELTACHT_REGIONS: SubRegion[] = [
  {
    id: 'conamara',
    displayName: 'Connemara',
    celticName: 'Conamara',
    spawnPoint: new Vector3(0, 2, 0),
    bounds: {
      min: new Vector3(-250, 0, -250),
      max: new Vector3(250, 100, 250),
    },
  },
  {
    id: 'corca_dhuibhne',
    displayName: 'Dingle Peninsula',
    celticName: 'Corca Dhuibhne',
    spawnPoint: new Vector3(100, 2, 100),
    bounds: {
      min: new Vector3(-200, 0, -200),
      max: new Vector3(200, 80, 200),
    },
  },
  {
    id: 'gaoth_dobhair',
    displayName: 'Donegal Gaeltacht',
    celticName: 'Gaoth Dobhair',
    spawnPoint: new Vector3(-100, 2, 50),
    bounds: {
      min: new Vector3(-300, 0, -200),
      max: new Vector3(200, 120, 300),
    },
  },
  {
    id: 'oileain_arann',
    displayName: 'Aran Islands',
    celticName: 'Oileáin Árann',
    spawnPoint: new Vector3(50, 2, -100),
    bounds: {
      min: new Vector3(-100, 0, -150),
      max: new Vector3(150, 50, 100),
    },
  },
  {
    id: 'ciarrai',
    displayName: 'Ring of Kerry',
    celticName: 'Ciarraí',
    spawnPoint: new Vector3(-50, 2, 100),
    bounds: {
      min: new Vector3(-200, 0, -150),
      max: new Vector3(200, 100, 250),
    },
  },
];

// Zone configuration matching Godot's connemara.tscn
const GAELTACHT_CONFIG: ZoneConfig = {
  zoneId: 'gaeltacht',
  displayName: 'Gaeltacht',
  celticName: 'An Ghaeltacht',
  language: 'irish',
  subRegions: GAELTACHT_REGIONS,
  defaultWeather: 'cloudy',
  defaultTimeOfDay: 'morning',
  ambientTrack: 'gaeltacht_wind',
  musicTrack: 'gaeltacht_theme',
  fogDensity: 0.002, // Matches Godot volumetric_fog_density
  ambientColor: new Color3(0.6, 0.65, 0.7), // Matches Godot ambient_light_color
  skyColor: new Color4(0.4, 0.5, 0.6, 1), // Matches Godot sky_top_color
};

export default class GaeltachtZone extends BaseZone {
  constructor(scene: Scene) {
    super(scene, GAELTACHT_CONFIG);
  }

  /**
   * Create Gaeltacht-specific environment
   */
  protected override async createEnvironment(): Promise<void> {
    await super.createEnvironment();

    // Configure sun for Irish weather (often overcast)
    if (this.sunLight) {
      // Matches Godot's DirectionalLight3D settings
      this.sunLight.position = new Vector3(0, 50, 0);
      this.sunLight.direction = new Vector3(0, -0.866, -0.5);
      this.sunLight.diffuse = new Color3(1, 0.95, 0.9);
      this.sunLight.intensity = 0.8;
    }

    // Irish sky - often grey and atmospheric
    if (this.ambientLight) {
      this.ambientLight.diffuse = new Color3(0.6, 0.65, 0.7);
      this.ambientLight.groundColor = new Color3(0.5, 0.55, 0.5);
      this.ambientLight.intensity = 0.5;
    }

    // Fog settings for atmospheric Irish weather
    this.scene.fogMode = Scene.FOGMODE_EXP2;
    this.scene.fogDensity = 0.002;
    this.scene.fogColor = new Color3(0.7, 0.75, 0.8);
  }

  /**
   * Create Gaeltacht terrain (bogland, rolling hills)
   */
  protected override async createTerrain(): Promise<void> {
    await super.createTerrain();

    // Update terrain material for Irish bogland
    if (this.terrain?.material) {
      const material = this.terrain.material as StandardMaterial;
      // Heather and bogland colors
      material.diffuseColor = new Color3(0.25, 0.35, 0.2);
      material.specularColor = new Color3(0.05, 0.05, 0.05);
    }
  }

  /**
   * Handle region-specific changes
   */
  protected override onRegionChange(region: SubRegion): void {
    super.onRegionChange(region);

    // Update ambient track based on region
    switch (region.id) {
      case 'conamara':
        console.log('[Gaeltacht] Playing Conamara ambience');
        break;
      case 'oileain_arann':
        console.log('[Gaeltacht] Playing Aran Islands ambience (ocean waves)');
        break;
      case 'corca_dhuibhne':
        console.log('[Gaeltacht] Playing Dingle ambience');
        break;
      default:
        console.log('[Gaeltacht] Playing default ambience');
    }
  }
}

// Re-export types
export { GAELTACHT_REGIONS, GAELTACHT_CONFIG };

// Import StandardMaterial for terrain
import { StandardMaterial } from '@babylonjs/core';
