/**
 * Tuath Game Client
 *
 * Babylon.js web client for the Tuath Celtic MMO.
 * Provides a unified API for the TanStack Start UI to integrate with.
 */

import { Vector3 } from '@babylonjs/core';

// Core exports
export { createGameEngine, getRendererInfo, type GameEngine, type EngineConfig } from './babylon/engine';
export { SceneManager, type ZoneId, type SceneManagerConfig } from './babylon/scene-manager';

// Network exports
export {
  SpacetimeClient,
  createSpacetimeClient,
  SPACETIMEDB_CONFIG,
  type SpacetimeConfig,
  type Player,
  type EntityPosition,
  type ZonePresence,
  type Npc,
  type ConnectionState,
} from './network/spacetime-client';

// Entity exports
export { PlayerController, type PlayerConfig, type InputState } from './entities/player-controller';
export { CameraController, type CameraConfig } from './entities/camera-controller';

// Zone exports
export { BaseZone, type ZoneConfig, type SubRegion, type Weather, type TimeOfDay } from './scenes/base-zone';

// Zone implementations (for direct import if needed)
export { default as GaeltachtZone, GAELTACHT_CONFIG, GAELTACHT_REGIONS } from './scenes/gaeltacht';
export { default as AlbaZone, ALBA_CONFIG, ALBA_REGIONS } from './scenes/alba';
export { default as CymruZone, CYMRU_CONFIG, CYMRU_REGIONS } from './scenes/cymru';

// ============ High-Level API ============

import { createGameEngine, type GameEngine } from './babylon/engine';
import { SceneManager, type ZoneId } from './babylon/scene-manager';
import { SpacetimeClient, createSpacetimeClient } from './network/spacetime-client';
import { PlayerController } from './entities/player-controller';
import { CameraController } from './entities/camera-controller';

export interface TuathGameConfig {
  /** Canvas element for rendering */
  canvas: HTMLCanvasElement;
  /** SpacetimeDB WebSocket URI */
  spacetimeUri?: string;
  /** Session token from SIWE auth */
  sessionToken?: string;
  /** Initial zone to load */
  initialZone?: ZoneId;
  /** Callbacks */
  onConnected?: () => void;
  onDisconnected?: () => void;
  onZoneChange?: (zoneId: ZoneId) => void;
  onLoadProgress?: (progress: number) => void;
}

export interface TuathGame {
  /** Game engine */
  engine: GameEngine;
  /** Scene manager */
  sceneManager: SceneManager;
  /** Network client */
  network: SpacetimeClient;
  /** Local player controller */
  player: PlayerController;
  /** Camera controller */
  camera: CameraController;
  /** Start the game */
  start: () => Promise<void>;
  /** Stop the game */
  stop: () => void;
  /** Dispose all resources */
  dispose: () => void;
  /** Load a zone */
  loadZone: (zoneId: ZoneId) => Promise<void>;
  /** Is WebGPU enabled? */
  isWebGPU: boolean;
}

/**
 * Initialize the Tuath game client
 *
 * This is the main entry point for integrating the game with the UI.
 *
 * @example
 * ```typescript
 * const game = await initTuathGame({
 *   canvas: canvasRef.current,
 *   sessionToken: siweSession.token,
 *   initialZone: 'gaeltacht',
 *   onConnected: () => console.log('Connected!'),
 * });
 *
 * await game.start();
 * ```
 */
export async function initTuathGame(config: TuathGameConfig): Promise<TuathGame> {
  const {
    canvas,
    spacetimeUri,
    sessionToken,
    initialZone = 'gaeltacht',
    onConnected,
    onDisconnected,
    onZoneChange,
    onLoadProgress,
  } = config;

  // Create game engine
  const engine = await createGameEngine({
    canvas,
    renderer: 'auto',
    targetFps: 60,
    antialias: true,
    enableInspector: import.meta.env?.DEV,
  });

  // Create scene manager
  const sceneManager = new SceneManager({
    engine: engine.engine,
    scene: engine.scene,
    onLoadProgress,
    onZoneChange,
  });

  // Create network client
  const network = createSpacetimeClient({
    uri: spacetimeUri,
    sessionToken,
    onConnect: onConnected,
    onDisconnect: onDisconnected,
  });

  // Create player controller
  const player = new PlayerController(engine.scene);

  // Create camera controller
  const camera = new CameraController(engine.scene);
  camera.setTarget(player.getRootNode());

  // Wire up network position sync
  player.setPositionUpdateCallback((position, rotation) => {
    network.updatePosition(
      { x: position.x, y: position.y, z: position.z },
      rotation
    );
  });

  // Handle network position updates for remote players
  network.onPositionUpdate((entityPosition) => {
    // TODO: Update remote player positions
    console.log('[Game] Remote player update:', entityPosition.entityId);
  });

  return {
    engine,
    sceneManager,
    network,
    player,
    camera,
    isWebGPU: engine.isWebGPU,

    async start() {
      // Connect to SpacetimeDB
      await network.connect();

      // Load initial zone
      await sceneManager.loadZone(initialZone);

      // Set player spawn position
      const zone = sceneManager.getCurrentZone();
      if (zone) {
        const spawnPoint = zone.getSpawnPoint();
        player.setPosition(spawnPoint);
        zone.onPlayerEnter(network.getLocalPlayerId() ?? 'local');
      }

      // Start render loop
      engine.start();

      console.log('[Tuath] Game started');
    },

    stop() {
      engine.stop();
      console.log('[Tuath] Game stopped');
    },

    dispose() {
      engine.stop();
      player.dispose();
      camera.dispose();
      sceneManager.dispose();
      network.disconnect();
      engine.dispose();
      console.log('[Tuath] Game disposed');
    },

    async loadZone(zoneId: ZoneId) {
      // Notify current zone of exit
      const currentZone = sceneManager.getCurrentZone();
      if (currentZone) {
        currentZone.onPlayerExit(network.getLocalPlayerId() ?? 'local');
        network.leaveZone();
      }

      // Load new zone
      await sceneManager.loadZone(zoneId);

      // Set player spawn position
      const zone = sceneManager.getCurrentZone();
      if (zone) {
        const spawnPoint = zone.getSpawnPoint();
        player.setPosition(spawnPoint);
        zone.onPlayerEnter(network.getLocalPlayerId() ?? 'local');
        network.enterZone(zoneId, zone.getCurrentRegion()?.id ?? 'default');
      }
    },
  };
}

// Re-export Vector3 for convenience
export { Vector3 };
