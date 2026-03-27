/**
 * Cymru Zone
 *
 * Wales region featuring:
 * - Snowdonia (Eryri)
 * - Pembrokeshire (Sir Benfro)
 * - Anglesey (Ynys Môn)
 * - Cardiff (Caerdydd)
 * - Brecon Beacons (Bannau Brycheiniog)
 *
 * Mirrors the Godot client's CymruZone for visual parity.
 */

import { Vector3, Color3, Color4, Scene, StandardMaterial } from '@babylonjs/core';
import { BaseZone, type ZoneConfig, type SubRegion } from '../base-zone';

const CYMRU_REGIONS: SubRegion[] = [
  {
    id: 'snowdonia',
    displayName: 'Snowdonia',
    celticName: 'Eryri',
    spawnPoint: new Vector3(0, 2, 0),
    bounds: {
      min: new Vector3(-250, 0, -250),
      max: new Vector3(250, 200, 250),
    },
  },
  {
    id: 'pembrokeshire',
    displayName: 'Pembrokeshire',
    celticName: 'Sir Benfro',
    spawnPoint: new Vector3(-120, 2, 100),
    bounds: {
      min: new Vector3(-200, 0, -100),
      max: new Vector3(100, 80, 200),
    },
  },
  {
    id: 'anglesey',
    displayName: 'Anglesey',
    celticName: 'Ynys Môn',
    spawnPoint: new Vector3(100, 2, -80),
    bounds: {
      min: new Vector3(-100, 0, -150),
      max: new Vector3(200, 50, 100),
    },
  },
  {
    id: 'cardiff',
    displayName: 'Cardiff',
    celticName: 'Caerdydd',
    spawnPoint: new Vector3(80, 2, 80),
    bounds: {
      min: new Vector3(-100, 0, -100),
      max: new Vector3(150, 60, 150),
    },
  },
  {
    id: 'brecon_beacons',
    displayName: 'Brecon Beacons',
    celticName: 'Bannau Brycheiniog',
    spawnPoint: new Vector3(-50, 2, -50),
    bounds: {
      min: new Vector3(-200, 0, -200),
      max: new Vector3(150, 150, 150),
    },
  },
];

const CYMRU_CONFIG: ZoneConfig = {
  zoneId: 'cymru',
  displayName: 'Cymru',
  celticName: 'Cymru',
  language: 'welsh',
  subRegions: CYMRU_REGIONS,
  defaultWeather: 'cloudy',
  defaultTimeOfDay: 'morning',
  ambientTrack: 'cymru_wind',
  musicTrack: 'cymru_theme',
  fogDensity: 0.002,
  ambientColor: new Color3(0.6, 0.65, 0.7),
  skyColor: new Color4(0.4, 0.5, 0.6, 1),
};

export default class CymruZone extends BaseZone {
  constructor(scene: Scene) {
    super(scene, CYMRU_CONFIG);
  }

  protected override async createEnvironment(): Promise<void> {
    await super.createEnvironment();

    // Welsh weather - similar to Irish but with mountain influence
    if (this.sunLight) {
      this.sunLight.position = new Vector3(0, 50, 0);
      this.sunLight.direction = new Vector3(-0.4, -0.866, -0.3);
      this.sunLight.diffuse = new Color3(1, 0.95, 0.9);
      this.sunLight.intensity = 0.75;
    }

    if (this.ambientLight) {
      this.ambientLight.diffuse = new Color3(0.6, 0.65, 0.7);
      this.ambientLight.groundColor = new Color3(0.5, 0.55, 0.5);
      this.ambientLight.intensity = 0.5;
    }

    // Mountain mist
    this.scene.fogMode = Scene.FOGMODE_EXP2;
    this.scene.fogDensity = 0.002;
    this.scene.fogColor = new Color3(0.7, 0.75, 0.8);
  }

  protected override async createTerrain(): Promise<void> {
    await super.createTerrain();

    if (this.terrain?.material) {
      const material = this.terrain.material as StandardMaterial;
      // Welsh mountain grass
      material.diffuseColor = new Color3(0.25, 0.4, 0.2);
      material.specularColor = new Color3(0.05, 0.05, 0.05);
    }
  }

  protected override onRegionChange(region: SubRegion): void {
    super.onRegionChange(region);

    switch (region.id) {
      case 'snowdonia':
        console.log('[Cymru] Playing Snowdonia ambience (mountain winds)');
        break;
      case 'pembrokeshire':
        console.log('[Cymru] Playing Pembrokeshire ambience (coastal)');
        break;
      case 'anglesey':
        console.log('[Cymru] Playing Anglesey ambience (druid isle)');
        break;
      default:
        console.log('[Cymru] Playing default ambience');
    }
  }
}

export { CYMRU_REGIONS, CYMRU_CONFIG };
