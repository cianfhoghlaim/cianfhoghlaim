# Babylon.js Game Client

Documentation for the Tuath Celtic MMO web game client built with Babylon.js 7.

## Overview

The game client provides a 3D browser-based experience for the Celtic educational MMO. It integrates with:

- **TanStack Start** - React UI wrapper and routing
- **SpacetimeDB** - Real-time multiplayer state synchronization
- **FastAPI Backend** - REST API for game data and authentication

### Key Features

- WebGPU rendering with WebGL2 fallback
- Third-person camera with collision detection
- Zone-based world with lazy loading
- Real-time multiplayer at 20Hz position sync
- WASD + mouse controls (matching Godot client)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TanStack Start UI                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    game.tsx                            │  │
│  │  - Canvas element                                      │  │
│  │  - Loading screen                                      │  │
│  │  - Game UI overlays (quest tracker, minimap, chat)    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                    initTuathGame()
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                    Game Client (index.ts)                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    TuathGame                             ││
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐            ││
│  │  │ GameEngine│  │SceneManager│ │SpacetimeDB │            ││
│  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘            ││
│  │        │              │              │                   ││
│  │  ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐            ││
│  │  │ Engine    │  │ BaseZone  │  │ Subscriptions           ││
│  │  │ Scene     │  │ Zones     │  │ Reducers  │            ││
│  │  └───────────┘  └───────────┘  └───────────┘            ││
│  │                                                          ││
│  │  ┌───────────┐  ┌───────────┐                           ││
│  │  │ Player    │  │ Camera    │                           ││
│  │  │ Controller│  │ Controller│                           ││
│  │  └───────────┘  └───────────┘                           ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Integration with TanStack Start

```tsx
// routes/game.tsx
import { useEffect, useRef, useState } from 'react';
import { initTuathGame, type TuathGame, type ZoneId } from '../../game/client/src';
import { useAuth } from '../hooks/useAuth';

function GamePage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const gameRef = useRef<TuathGame | null>(null);
  const { sessionId } = useAuth();

  useEffect(() => {
    if (!canvasRef.current) return;

    const initGame = async () => {
      const game = await initTuathGame({
        canvas: canvasRef.current!,
        sessionToken: sessionId ?? undefined,
        initialZone: 'gaeltacht',
        onConnected: () => console.log('Connected to SpacetimeDB'),
        onZoneChange: (zoneId) => console.log('Zone changed:', zoneId),
      });

      gameRef.current = game;
      await game.start();
    };

    initGame();

    return () => {
      gameRef.current?.dispose();
    };
  }, [sessionId]);

  return <canvas ref={canvasRef} className="w-full h-full" />;
}
```

### Standalone Initialization

```typescript
import { initTuathGame } from '@tuath/game-client';

const game = await initTuathGame({
  canvas: document.querySelector('canvas')!,
  sessionToken: 'jwt-token-from-siwe',
  initialZone: 'gaeltacht',
  onConnected: () => { /* multiplayer ready */ },
  onDisconnected: () => { /* handle disconnect */ },
  onZoneChange: (zoneId) => { /* update UI */ },
  onLoadProgress: (progress) => { /* update loading bar */ },
});

await game.start();

// Later...
await game.loadZone('alba');
game.stop();
game.dispose();
```

---

## Engine Setup

### WebGPU/WebGL2 Fallback

The engine automatically selects the best available renderer:

```typescript
// engine.ts
export async function createGameEngine(config: EngineConfig): Promise<GameEngine> {
  let engine: AbstractEngine;
  let isWebGPU = false;

  // Try WebGPU first
  if (renderer === 'webgpu' || renderer === 'auto') {
    const webGPUSupported = await WebGPUEngine.IsSupportedAsync;
    if (webGPUSupported) {
      engine = new WebGPUEngine(canvas, {
        antialias: true,
        adaptToDeviceRatio: true,
        stencil: true,
        powerPreference: 'high-performance',
      });
      await engine.initAsync();
      isWebGPU = true;
    }
  }

  // Fallback to WebGL2
  if (!engine) {
    engine = new Engine(canvas, true, {
      adaptToDeviceRatio: true,
      stencil: true,
      preserveDrawingBuffer: true,
      powerPreference: 'high-performance',
    });
  }

  return { engine, scene, isWebGPU, ... };
}
```

### Engine Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `canvas` | HTMLCanvasElement | required | Target canvas element |
| `renderer` | 'webgpu' \| 'webgl2' \| 'auto' | 'auto' | Preferred renderer |
| `targetFps` | number | 60 | Frame rate limit |
| `antialias` | boolean | true | Enable anti-aliasing |
| `adaptivePixelRatio` | boolean | true | Adapt to device pixel ratio |
| `enableInspector` | boolean | false | Enable Babylon.js inspector |

### Checking Renderer

```typescript
const game = await initTuathGame({ ... });
console.log('Using WebGPU:', game.isWebGPU);
```

---

## Scene Manager

The scene manager handles zone lifecycle and asset loading.

### Zone Registry

Zones are lazy-loaded for performance:

```typescript
// scene-manager.ts
private zoneRegistry: ZoneRegistry = {
  gaeltacht: () => import('../scenes/gaeltacht'),
  alba: () => import('../scenes/alba'),
  cymru: () => import('../scenes/cymru'),
};
```

### Zone Loading

```typescript
// Loading a zone with progress tracking
await game.loadZone('alba');

// Progress callback
const game = await initTuathGame({
  onLoadProgress: (progress) => {
    console.log(`Loading: ${progress}%`);
  },
});
```

### Zone Types

| Zone ID | Display Name | Celtic Name | Language |
|---------|--------------|-------------|----------|
| `gaeltacht` | Irish Gaeltacht | An Ghaeltacht | Irish |
| `alba` | Scottish Highlands | Alba | Scottish Gaelic |
| `cymru` | Wales | Cymru | Welsh |

---

## Zone Development

### Base Zone Class

All zones extend `BaseZone`:

```typescript
// scenes/base-zone.ts
export abstract class BaseZone {
  protected scene: Scene;
  protected config: ZoneConfig;

  // Environment
  protected sunLight: DirectionalLight | null = null;
  protected ambientLight: HemisphericLight | null = null;
  protected terrain: AbstractMesh | null = null;

  // State
  protected currentRegion: SubRegion | null = null;
  protected currentWeather: Weather;
  protected currentTimeOfDay: TimeOfDay;

  // Lifecycle methods
  abstract createTerrain(): Promise<void>;
  abstract createNpcs(): Promise<void>;
  abstract createInteractables(): Promise<void>;

  // Player events
  onPlayerEnter(playerId: string): void { ... }
  onPlayerExit(playerId: string): void { ... }

  // Environment
  setWeather(weather: Weather): void { ... }
  setTimeOfDay(time: TimeOfDay): void { ... }
}
```

### Zone Configuration

```typescript
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
```

### Sub-Regions

Zones are divided into sub-regions for multiplayer optimization:

```typescript
export interface SubRegion {
  id: string;
  displayName: string;
  celticName: string;
  spawnPoint: Vector3;
  bounds: { min: Vector3; max: Vector3 };
}

// Example
const GAELTACHT_REGIONS: SubRegion[] = [
  {
    id: 'village',
    displayName: 'Baile Beag',
    celticName: 'Baile Beag',
    spawnPoint: new Vector3(0, 0, 0),
    bounds: {
      min: new Vector3(-100, 0, -100),
      max: new Vector3(100, 50, 100),
    },
  },
  // ...
];
```

### Weather System

```typescript
type Weather = 'clear' | 'cloudy' | 'rainy' | 'foggy' | 'stormy';

// Change weather in a zone
const zone = game.sceneManager.getCurrentZone();
zone?.setWeather('rainy');
```

### Time of Day

```typescript
type TimeOfDay = 'dawn' | 'morning' | 'noon' | 'afternoon' | 'dusk' | 'night';

zone?.setTimeOfDay('dusk');
```

---

## Player Controller

The player controller handles local player movement with physics.

### Controls

| Key | Action |
|-----|--------|
| W | Move forward |
| S | Move backward |
| A | Strafe left |
| D | Strafe right |
| Space | Jump |
| Shift | Sprint |
| E | Interact |
| Mouse | Camera rotation (pointer locked) |
| Scroll | Camera zoom |

### Configuration

```typescript
export interface PlayerConfig {
  moveSpeed: number;        // Default: 5.0 units/sec
  sprintMultiplier: number; // Default: 1.8x
  jumpForce: number;        // Default: 8.0
  gravity: number;          // Default: 20.0
  turnSpeed: number;        // Default: 5.0 rad/sec
  groundCheckDistance: number; // Default: 0.2
}
```

### Player API

```typescript
// Get position
const position = game.player.getPosition();

// Set position (teleport)
game.player.setPosition(new Vector3(10, 0, 20));

// Rotate player
game.player.rotate(Math.PI / 4); // 45 degrees

// Check states
const grounded = game.player.getIsGrounded();
const sprinting = game.player.getIsSprinting();

// Get transform node (for attaching objects)
const playerNode = game.player.getRootNode();
```

### Network Sync

Position updates are sent at 20Hz (50ms interval):

```typescript
// Automatic sync via callback
player.setPositionUpdateCallback((position, rotation) => {
  network.updatePosition(
    { x: position.x, y: position.y, z: position.z },
    rotation
  );
});
```

---

## Camera Controller

Third-person camera with collision detection.

### Configuration

```typescript
export interface CameraConfig {
  distance: number;        // Default: 5.0
  minDistance: number;     // Default: 2.0
  maxDistance: number;     // Default: 15.0
  heightOffset: number;    // Default: 1.5 (above player)
  sensitivity: number;     // Default: 0.005
  smoothing: number;       // Default: 0.1 (lower = smoother)
  minBeta: number;         // Min vertical angle (radians)
  maxBeta: number;         // Max vertical angle
  enableCollision: boolean; // Default: true
}
```

### Camera API

```typescript
// Set target (usually player)
game.camera.setTarget(game.player.getRootNode());

// Get camera direction (for UI indicators)
const forward = game.camera.getForwardDirection();

// Get camera rotation
const alpha = game.camera.getAlpha();

// Set zoom distance
game.camera.setDistance(8.0);

// Reset camera
game.camera.reset();
```

### Collision Detection

Camera automatically moves closer when obstructed:

```typescript
private handleCollision(targetPosition: Vector3): void {
  const ray = new Ray(targetPosition, cameraDirection, this.targetDistance);
  const pickInfo = this.scene.pickWithRay(ray, (mesh) => {
    return mesh.checkCollisions && !mesh.name.startsWith('Player');
  });

  if (pickInfo?.hit && pickInfo.distance < this.targetDistance) {
    desiredDistance = Math.max(this.config.minDistance, pickInfo.distance - 0.5);
  }
}
```

---

## SpacetimeDB Integration

Real-time multiplayer via WebSocket connection.

### Configuration

```typescript
export const SPACETIMEDB_CONFIG: SpacetimeConfig = {
  uri: 'wss://spacetimedb.tuath.cianfhoghlaim.dev',
  moduleName: 'tuath-game',
};
```

### Connection Lifecycle

```typescript
// Connect with SIWE token
const network = createSpacetimeClient({
  uri: 'wss://...',
  sessionToken: 'jwt-from-siwe',
  onConnect: () => console.log('Connected'),
  onDisconnect: () => console.log('Disconnected'),
});

await network.connect();

// Later
network.disconnect();
```

### Subscriptions

Players subscribe to entities in their zone:

```typescript
// Automatic subscription to zone players
network.onPositionUpdate((entityPosition) => {
  // Update remote player mesh position
  remotePlayer.position = new Vector3(
    entityPosition.position.x,
    entityPosition.position.y,
    entityPosition.position.z
  );
});

// Subscribe to NPCs
network.onNpcUpdate((npc) => {
  // Update NPC state
});
```

### Reducers

Send state changes to the database:

```typescript
// Update player position (called at 20Hz)
network.updatePosition(
  { x: position.x, y: position.y, z: position.z },
  rotation
);

// Enter a zone
network.enterZone('gaeltacht', 'village');

// Leave current zone
network.leaveZone();

// Send chat message
network.sendMessage('Dia duit!');
```

### Zone Presence

Track players in the current zone:

```typescript
network.onZonePresenceChange((presence) => {
  console.log(`${presence.playerId} entered ${presence.zoneId}/${presence.subRegionId}`);
});
```

---

## Data Types

### Player

```typescript
interface Player {
  id: string;
  name: string;
  position: Position;
  rotation: number;
  zoneId: string;
  level: number;
  xp: number;
}
```

### Entity Position

```typescript
interface EntityPosition {
  entityId: string;
  position: Position;
  rotation: number;
  velocity: Position;
  timestamp: number;
  regionBucket: string;
}
```

### NPC

```typescript
interface Npc {
  id: string;
  name: string;
  celticName: string;
  position: Position;
  zoneId: string;
  dialogueId: string;
  isInteractable: boolean;
}
```

---

## Performance Tips

### 1. Zone Loading

- Zones are lazy-loaded - only the current zone is in memory
- Use `onLoadProgress` to show loading UI during transitions
- Preload adjacent zones for seamless transitions (future)

### 2. Network Optimization

- Position sync at 20Hz (50ms) balances smoothness vs bandwidth
- Only subscribe to entities in current region bucket
- Use dead reckoning for interpolation between updates

### 3. Rendering

- WebGPU provides ~40% performance improvement over WebGL2
- Use LOD (Level of Detail) for distant objects
- Batch draw calls by grouping similar materials

### 4. Memory Management

```typescript
// Always dispose when component unmounts
useEffect(() => {
  return () => {
    gameRef.current?.dispose();
  };
}, []);
```

---

## Debugging

### Enable Babylon.js Inspector

```typescript
const game = await initTuathGame({
  enableInspector: import.meta.env.DEV,
});

// Toggle in-game
scene.debugLayer.show();
scene.debugLayer.hide();
```

### Console Logging

All game client logs are prefixed:

```
[Tuath] Game started
[SceneManager] Loading zone: gaeltacht
[SpacetimeDB] Connected
[Player] Interacting with: StandingStone_01
```

### Check Renderer

```javascript
console.log('WebGPU:', game.isWebGPU);
console.log('Engine:', game.engine.engine.constructor.name);
```

---

## File Structure

```
game/client/
├── package.json               # Babylon.js + SpacetimeDB deps
├── tsconfig.json
└── src/
    ├── index.ts               # Main exports, initTuathGame
    ├── babylon/
    │   ├── engine.ts          # WebGPU/WebGL2 setup
    │   └── scene-manager.ts   # Zone lifecycle
    ├── entities/
    │   ├── player-controller.ts  # Local player
    │   └── camera-controller.ts  # Third-person camera
    ├── scenes/
    │   ├── base-zone.ts       # Abstract zone class
    │   ├── gaeltacht.ts       # Irish zone
    │   ├── alba.ts            # Scottish zone
    │   └── cymru.ts           # Welsh zone
    └── network/
        └── spacetime-client.ts # SpacetimeDB SDK wrapper
```

---

## Related Documentation

- [Architecture](./ARCHITECTURE.md) - System overview
- [Frontend](./FRONTEND.md) - TanStack Start integration
- [SpacetimeDB Guide](../../taighde/game/docs/SPACETIMEDB_GUIDE.md) - Multiplayer backend
- [API Reference](./API.md) - Backend endpoints
