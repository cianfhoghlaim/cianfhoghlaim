# Adding New Game Zones

Guide for creating new zones in the Tuath Celtic MMO Babylon.js game client.

## Overview

Zones are the game world regions representing Celtic language areas. Each zone has:
- Terrain and environment
- NPCs and interactables
- Sub-regions for multiplayer optimization
- Weather and time-of-day systems

### Existing Zones

| Zone ID | Display Name | Language |
|---------|--------------|----------|
| `gaeltacht` | An Ghaeltacht | Irish |
| `alba` | Alba | Scottish Gaelic |
| `cymru` | Cymru | Welsh |

---

## Creating a New Zone

### Step 1: Define Zone Configuration

```typescript
// scenes/my-zone.ts

import { Vector3, Color3, Color4 } from '@babylonjs/core';
import { BaseZone, type ZoneConfig, type SubRegion } from './base-zone';

// Sub-regions for multiplayer bucketing
export const MY_ZONE_REGIONS: SubRegion[] = [
  {
    id: 'village',
    displayName: 'Village Center',
    celticName: 'Lár an Bhaile',
    spawnPoint: new Vector3(0, 0, 0),
    bounds: {
      min: new Vector3(-100, 0, -100),
      max: new Vector3(100, 50, 100),
    },
  },
  {
    id: 'forest',
    displayName: 'Sacred Grove',
    celticName: 'An Doire Naofa',
    spawnPoint: new Vector3(150, 0, 0),
    bounds: {
      min: new Vector3(100, 0, -100),
      max: new Vector3(300, 50, 100),
    },
  },
  {
    id: 'coast',
    displayName: 'Coastal Path',
    celticName: 'Cosán na Mara',
    spawnPoint: new Vector3(-150, 0, 0),
    bounds: {
      min: new Vector3(-300, 0, -100),
      max: new Vector3(-100, 50, 100),
    },
  },
];

// Zone configuration
export const MY_ZONE_CONFIG: ZoneConfig = {
  zoneId: 'my_zone',
  displayName: 'My New Zone',
  celticName: 'Mo Cheantar Nua',
  language: 'irish',  // or 'scottish-gaelic', 'welsh'
  subRegions: MY_ZONE_REGIONS,
  defaultWeather: 'cloudy',
  defaultTimeOfDay: 'morning',
  ambientTrack: 'audio/ambient/my_zone.mp3',
  musicTrack: 'audio/music/my_zone_theme.mp3',
  fogDensity: 0.02,
  ambientColor: new Color3(0.3, 0.4, 0.35),
  skyColor: new Color4(0.6, 0.7, 0.8, 1),
};
```

### Step 2: Implement Zone Class

```typescript
// scenes/my-zone.ts (continued)

import {
  Scene,
  Vector3,
  MeshBuilder,
  StandardMaterial,
  Color3,
  Texture,
  TransformNode,
} from '@babylonjs/core';

export default class MyZone extends BaseZone {
  constructor(scene: Scene) {
    super(scene, MY_ZONE_CONFIG);
  }

  /**
   * Create the zone's terrain
   */
  protected async createTerrain(): Promise<void> {
    // Create ground
    const ground = MeshBuilder.CreateGround(
      'ground',
      { width: 500, height: 500, subdivisions: 64 },
      this.scene
    );

    const groundMaterial = new StandardMaterial('groundMat', this.scene);
    groundMaterial.diffuseTexture = new Texture(
      'textures/terrain/grass.jpg',
      this.scene
    );
    (groundMaterial.diffuseTexture as Texture).uScale = 50;
    (groundMaterial.diffuseTexture as Texture).vScale = 50;
    ground.material = groundMaterial;
    ground.checkCollisions = true;

    ground.parent = this.terrainNode;
    this.terrain = ground;

    // Add height variations using heightmap (optional)
    // await this.applyHeightmap('textures/terrain/my_zone_height.png');
  }

  /**
   * Create NPCs in the zone
   */
  protected async createNpcs(): Promise<void> {
    // Create NPC spawn points
    const npcSpawns = [
      {
        id: 'npc_elder',
        name: 'Elder Seamus',
        celticName: 'Séamas an tSeanóir',
        position: new Vector3(5, 0, 10),
        dialogueId: 'elder_greeting',
      },
      {
        id: 'npc_merchant',
        name: 'Merchant Caitlin',
        celticName: 'Caitlín an Ceannai',
        position: new Vector3(-15, 0, 5),
        dialogueId: 'merchant_wares',
      },
    ];

    for (const spawn of npcSpawns) {
      const npc = await this.createNpc(spawn);
      npc.parent = this.npcsNode;
    }
  }

  /**
   * Create interactable objects
   */
  protected async createInteractables(): Promise<void> {
    // Standing stones (Celtic monuments)
    const stonePositions = [
      new Vector3(20, 0, 20),
      new Vector3(22, 0, 18),
      new Vector3(18, 0, 22),
    ];

    for (let i = 0; i < stonePositions.length; i++) {
      const stone = MeshBuilder.CreateCylinder(
        `standing_stone_${i}`,
        { height: 3, diameterTop: 0.3, diameterBottom: 0.5 },
        this.scene
      );
      stone.position = stonePositions[i];
      stone.position.y = 1.5;

      // Mark as interactable
      stone.metadata = {
        interactable: true,
        interactionType: 'examine',
        dialogueId: 'standing_stone_examine',
      };

      stone.checkCollisions = true;
      stone.parent = this.interactablesNode;
    }

    // Quest item
    const questItem = await this.createQuestItem({
      id: 'ancient_scroll',
      name: 'Ancient Scroll',
      celticName: 'Scríbhinn Ársa',
      position: new Vector3(25, 1, 25),
      questId: 'first_words',
    });
    questItem.parent = this.interactablesNode;
  }

  /**
   * Called when player enters the zone
   */
  onPlayerEnter(playerId: string): void {
    super.onPlayerEnter(playerId);

    // Zone-specific entry logic
    console.log(`[MyZone] Player ${playerId} entered`);

    // Trigger ambient audio
    this.playAmbientAudio();

    // Show welcome message (if first visit)
    // this.showWelcomeMessage(playerId);
  }

  /**
   * Called when player exits the zone
   */
  onPlayerExit(playerId: string): void {
    super.onPlayerExit(playerId);

    // Cleanup
    console.log(`[MyZone] Player ${playerId} exited`);
  }
}
```

### Step 3: Register Zone in Scene Manager

```typescript
// babylon/scene-manager.ts

export type ZoneId = 'gaeltacht' | 'alba' | 'cymru' | 'my_zone';

export interface ZoneRegistry {
  gaeltacht: () => Promise<{ default: new (scene: Scene) => BaseZone }>;
  alba: () => Promise<{ default: new (scene: Scene) => BaseZone }>;
  cymru: () => Promise<{ default: new (scene: Scene) => BaseZone }>;
  my_zone: () => Promise<{ default: new (scene: Scene) => BaseZone }>;
}

export class SceneManager {
  private zoneRegistry: ZoneRegistry = {
    gaeltacht: () => import('../scenes/gaeltacht'),
    alba: () => import('../scenes/alba'),
    cymru: () => import('../scenes/cymru'),
    my_zone: () => import('../scenes/my-zone'),  // Add here
  };
}
```

### Step 4: Update Zone Names

```typescript
// In your UI code
const ZONE_NAMES: Record<ZoneId, string> = {
  gaeltacht: 'An Ghaeltacht',
  alba: 'Alba',
  cymru: 'Cymru',
  my_zone: 'Mo Cheantar Nua',
};
```

---

## Zone Features

### Weather System

```typescript
// Change weather
zone.setWeather('rainy');

// Weather types
type Weather = 'clear' | 'cloudy' | 'rainy' | 'foggy' | 'stormy';
```

Weather implementation in BaseZone:
```typescript
setWeather(weather: Weather): void {
  this.currentWeather = weather;

  switch (weather) {
    case 'foggy':
      this.scene.fogMode = Scene.FOGMODE_EXP2;
      this.scene.fogDensity = 0.05;
      this.scene.fogColor = new Color3(0.9, 0.9, 0.9);
      break;
    case 'rainy':
      this.enableRainParticles();
      this.scene.fogDensity = 0.02;
      break;
    // ...
  }
}
```

### Time of Day

```typescript
// Change time
zone.setTimeOfDay('dusk');

// Time types
type TimeOfDay = 'dawn' | 'morning' | 'noon' | 'afternoon' | 'dusk' | 'night';
```

Implementation:
```typescript
setTimeOfDay(time: TimeOfDay): void {
  this.currentTimeOfDay = time;

  const lightSettings = {
    dawn: { intensity: 0.4, color: new Color3(1.0, 0.7, 0.5) },
    morning: { intensity: 0.7, color: new Color3(1.0, 0.95, 0.9) },
    noon: { intensity: 1.0, color: new Color3(1.0, 1.0, 1.0) },
    afternoon: { intensity: 0.8, color: new Color3(1.0, 0.95, 0.85) },
    dusk: { intensity: 0.5, color: new Color3(1.0, 0.6, 0.4) },
    night: { intensity: 0.1, color: new Color3(0.4, 0.5, 0.7) },
  };

  const setting = lightSettings[time];
  this.sunLight.intensity = setting.intensity;
  this.sunLight.diffuse = setting.color;
}
```

### Sub-Regions

Sub-regions optimize multiplayer by limiting subscription scope:

```typescript
// Define clear boundaries
const region: SubRegion = {
  id: 'village',
  displayName: 'Village Center',
  celticName: 'Lár an Bhaile',
  spawnPoint: new Vector3(0, 0, 0),
  bounds: {
    min: new Vector3(-100, 0, -100),
    max: new Vector3(100, 50, 100),
  },
};

// In SpacetimeDB, players only subscribe to their region bucket
network.enterZone('my_zone', 'village');
```

---

## Asset Loading

### Textures

```typescript
// Place textures in public/textures/
const texture = new Texture('textures/terrain/grass.jpg', this.scene);
```

### 3D Models

```typescript
import { SceneLoader } from '@babylonjs/core';
import '@babylonjs/loaders/glTF';

// Load GLTF model
const result = await SceneLoader.ImportMeshAsync(
  '',
  'models/',
  'npc_model.glb',
  this.scene
);
const npcMesh = result.meshes[0];
```

### Audio

```typescript
import { Sound } from '@babylonjs/core';

// Background music
const music = new Sound(
  'theme',
  'audio/music/my_zone_theme.mp3',
  this.scene,
  null,
  { loop: true, autoplay: true, volume: 0.5 }
);

// Ambient sounds
const ambient = new Sound(
  'ambient',
  'audio/ambient/forest.mp3',
  this.scene,
  null,
  { loop: true, autoplay: true, volume: 0.3 }
);
```

---

## NPC Implementation

### Creating NPCs

```typescript
private async createNpc(config: NpcConfig): Promise<TransformNode> {
  const npcNode = new TransformNode(`npc_${config.id}`, this.scene);
  npcNode.position = config.position;

  // Create NPC mesh (placeholder or loaded model)
  const body = MeshBuilder.CreateCapsule(
    `npc_${config.id}_body`,
    { height: 1.8, radius: 0.3 },
    this.scene
  );
  body.position.y = 0.9;
  body.parent = npcNode;

  // Apply material
  const material = new StandardMaterial(`npc_${config.id}_mat`, this.scene);
  material.diffuseColor = new Color3(0.8, 0.6, 0.4);
  body.material = material;

  // Mark as interactable
  body.metadata = {
    interactable: true,
    interactionType: 'talk',
    npcId: config.id,
    npcName: config.name,
    celticName: config.celticName,
    dialogueId: config.dialogueId,
  };

  return npcNode;
}
```

### NPC Interaction

When player presses E near an NPC:
```typescript
// In player-controller.ts
private handleInteraction(): void {
  const ray = new Ray(origin, worldForward, 3.0);
  const pickInfo = this.scene.pickWithRay(ray, (mesh) => {
    return mesh.metadata?.interactable === true;
  });

  if (pickInfo?.hit && pickInfo.pickedMesh) {
    const metadata = pickInfo.pickedMesh.metadata;

    if (metadata.interactionType === 'talk') {
      // Trigger dialogue via game client
      this.onNpcInteraction?.(metadata.npcId, metadata.dialogueId);
    }
  }
}
```

---

## Testing Zones

### Visual Testing

```bash
cd sruth/tuath/ui
pnpm dev
```

Navigate to `/game` and use zone loading:
```typescript
await game.loadZone('my_zone');
```

### Collision Testing

Enable debug rendering:
```typescript
// In engine.ts when enableInspector is true
if (enableInspector) {
  scene.debugLayer.show();
}
```

### Performance Testing

Monitor frame rate and draw calls:
```typescript
scene.registerBeforeRender(() => {
  console.log('FPS:', engine.getFps().toFixed());
  console.log('Draw calls:', scene.getActiveMeshes().length);
});
```

---

## Best Practices

1. **Keep zones modular**: Each zone should be self-contained
2. **Use lazy loading**: Zones are loaded on demand via dynamic imports
3. **Optimize meshes**: Use LOD for distant objects
4. **Limit draw calls**: Batch similar materials
5. **Test on low-end devices**: Ensure 30+ FPS on integrated graphics
6. **Include fallbacks**: Handle missing assets gracefully

---

## Related Documentation

- [Game Client](../../01-game-design/GAME_CLIENT.md) - Full client documentation
- [Architecture](../../ANALYSIS.md) - System overview
- [SpacetimeDB Guide](../../04-game-tech/reference/guides/SPACETIMEDB_GUIDE.md) - Multiplayer integration
