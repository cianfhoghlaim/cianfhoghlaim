/**
 * Alba Zone
 *
 * Scottish Highlands region featuring:
 * - Highlands (A' Ghaidhealtachd)
 * - Isle of Skye (An t-Eilean Sgitheanach)
 * - Loch Ness (Loch Nis)
 * - Edinburgh (Dùn Èideann)
 * - Outer Hebrides (Na h-Eileanan Siar)
 *
 * Mirrors the Godot client's AlbaZone for visual parity.
 */

import { Vector3, Color3, Color4, Scene, StandardMaterial } from '@babylonjs/core';
import { BaseZone, type ZoneConfig, type SubRegion } from '../base-zone';

const ALBA_REGIONS: SubRegion[] = [
  {
    id: 'highlands',
    displayName: 'Scottish Highlands',
    celticName: "A' Ghaidhealtachd",
    spawnPoint: new Vector3(0, 2, 0),
    bounds: {
      min: new Vector3(-300, 0, -300),
      max: new Vector3(300, 150, 300),
    },
  },
  {
    id: 'isle_of_skye',
    displayName: 'Isle of Skye',
    celticName: 'An t-Eilean Sgitheanach',
    spawnPoint: new Vector3(150, 2, 80),
    bounds: {
      min: new Vector3(-150, 0, -100),
      max: new Vector3(200, 100, 200),
    },
  },
  {
    id: 'loch_ness',
    displayName: 'Loch Ness',
    celticName: 'Loch Nis',
    spawnPoint: new Vector3(-80, 2, 120),
    bounds: {
      min: new Vector3(-200, 0, -100),
      max: new Vector3(100, 80, 250),
    },
  },
  {
    id: 'edinburgh',
    displayName: 'Edinburgh',
    celticName: 'Dùn Èideann',
    spawnPoint: new Vector3(100, 2, -100),
    bounds: {
      min: new Vector3(-150, 0, -200),
      max: new Vector3(200, 60, 100),
    },
  },
  {
    id: 'outer_hebrides',
    displayName: 'Outer Hebrides',
    celticName: 'Na h-Eileanan Siar',
    spawnPoint: new Vector3(-150, 2, 0),
    bounds: {
      min: new Vector3(-250, 0, -150),
      max: new Vector3(50, 50, 150),
    },
  },
];

const ALBA_CONFIG: ZoneConfig = {
  zoneId: 'alba',
  displayName: 'Alba',
  celticName: 'Alba',
  language: 'scottish-gaelic',
  subRegions: ALBA_REGIONS,
  defaultWeather: 'cloudy',
  defaultTimeOfDay: 'morning',
  ambientTrack: 'alba_wind',
  musicTrack: 'alba_theme',
  fogDensity: 0.003, // Misty Scottish atmosphere
  ambientColor: new Color3(0.55, 0.6, 0.65),
  skyColor: new Color4(0.35, 0.45, 0.55, 1), // Darker, more dramatic sky
};

export default class AlbaZone extends BaseZone {
  constructor(scene: Scene) {
    super(scene, ALBA_CONFIG);
  }

  protected override async createEnvironment(): Promise<void> {
    await super.createEnvironment();

    // Scottish highlands - dramatic lighting
    if (this.sunLight) {
      this.sunLight.position = new Vector3(0, 50, 0);
      this.sunLight.direction = new Vector3(-0.3, -0.866, -0.4);
      this.sunLight.diffuse = new Color3(0.95, 0.9, 0.85);
      this.sunLight.intensity = 0.7;
    }

    if (this.ambientLight) {
      this.ambientLight.diffuse = new Color3(0.55, 0.6, 0.65);
      this.ambientLight.groundColor = new Color3(0.4, 0.45, 0.4);
      this.ambientLight.intensity = 0.45;
    }

    // Highland mist
    this.scene.fogMode = Scene.FOGMODE_EXP2;
    this.scene.fogDensity = 0.003;
    this.scene.fogColor = new Color3(0.6, 0.65, 0.7);
  }

  protected override async createTerrain(): Promise<void> {
    await super.createTerrain();

    if (this.terrain?.material) {
      const material = this.terrain.material as StandardMaterial;
      // Highland heather and grass
      material.diffuseColor = new Color3(0.3, 0.35, 0.25);
      material.specularColor = new Color3(0.05, 0.05, 0.05);
    }
  }

  protected override onRegionChange(region: SubRegion): void {
    super.onRegionChange(region);

    switch (region.id) {
      case 'highlands':
        console.log('[Alba] Playing Highlands ambience (wind, bagpipes distant)');
        break;
      case 'isle_of_skye':
        console.log('[Alba] Playing Skye ambience (coastal winds)');
        break;
      case 'loch_ness':
        console.log('[Alba] Playing Loch Ness ambience (water, mysterious)');
        break;
      default:
        console.log('[Alba] Playing default ambience');
    }
  }
}

export { ALBA_REGIONS, ALBA_CONFIG };
