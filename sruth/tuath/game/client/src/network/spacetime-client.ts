/**
 * SpacetimeDB Client
 *
 * Real-time multiplayer connection for the Tuath Celtic MMO.
 * Uses SpacetimeDB TypeScript SDK with DbConnection builder pattern.
 */

import { DbConnection } from '@clockworklabs/spacetimedb-sdk';

export interface SpacetimeConfig {
  /** SpacetimeDB WebSocket URL */
  uri: string;
  /** Module name (tuath-game) */
  moduleName: string;
  /** Session token from SIWE authentication */
  sessionToken?: string;
  /** Callbacks */
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
}

export interface Position {
  x: number;
  y: number;
  z: number;
}

export interface Player {
  id: string;
  name: string;
  position: Position;
  rotation: number;
  zoneId: string;
  level: number;
  xp: number;
}

export interface EntityPosition {
  entityId: string;
  position: Position;
  rotation: number;
  velocity: Position;
  timestamp: number;
  regionBucket: string;
}

export interface ZonePresence {
  playerId: string;
  zoneId: string;
  subRegionId: string;
  enteredAt: number;
}

export interface Npc {
  id: string;
  name: string;
  celticName: string;
  position: Position;
  zoneId: string;
  dialogueId: string;
  isInteractable: boolean;
}

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

export class SpacetimeClient {
  private connection: DbConnection | null = null;
  private config: SpacetimeConfig;
  private state: ConnectionState = 'disconnected';

  // Event handlers
  private playerHandlers: Set<(player: Player) => void> = new Set();
  private positionHandlers: Set<(position: EntityPosition) => void> = new Set();
  private zonePresenceHandlers: Set<(presence: ZonePresence) => void> = new Set();
  private npcHandlers: Set<(npc: Npc) => void> = new Set();

  // Local state
  private localPlayerId: string | null = null;
  private currentZoneId: string | null = null;

  constructor(config: SpacetimeConfig) {
    this.config = config;
  }

  /**
   * Connect to SpacetimeDB
   */
  async connect(): Promise<void> {
    if (this.state === 'connected' || this.state === 'connecting') {
      return;
    }

    this.state = 'connecting';
    console.log('[SpacetimeDB] Connecting to:', this.config.uri);

    try {
      const builder = DbConnection.builder()
        .withUri(this.config.uri)
        .withModuleName(this.config.moduleName)
        .onConnect(() => {
          this.state = 'connected';
          console.log('[SpacetimeDB] Connected');
          this.config.onConnect?.();
          this.setupSubscriptions();
        })
        .onDisconnect(() => {
          this.state = 'disconnected';
          console.log('[SpacetimeDB] Disconnected');
          this.config.onDisconnect?.();
        })
        .onConnectError((error) => {
          this.state = 'error';
          console.error('[SpacetimeDB] Connection error:', error);
          this.config.onError?.(new Error(String(error)));
        });

      // Add session token if available (from SIWE)
      if (this.config.sessionToken) {
        builder.withCredentials(this.config.sessionToken);
      }

      this.connection = builder.build();
    } catch (error) {
      this.state = 'error';
      throw error;
    }
  }

  /**
   * Setup table subscriptions
   */
  private setupSubscriptions(): void {
    if (!this.connection) return;

    const db = this.connection.db;

    // Subscribe to Player table
    db.Player?.onInsert((player: Player) => {
      this.playerHandlers.forEach((handler) => handler(player));
    });

    db.Player?.onUpdate((oldPlayer: Player, newPlayer: Player) => {
      this.playerHandlers.forEach((handler) => handler(newPlayer));
    });

    // Subscribe to EntityPosition table
    db.EntityPosition?.onInsert((position: EntityPosition) => {
      this.positionHandlers.forEach((handler) => handler(position));
    });

    db.EntityPosition?.onUpdate((oldPos: EntityPosition, newPos: EntityPosition) => {
      this.positionHandlers.forEach((handler) => handler(newPos));
    });

    // Subscribe to ZonePresence table
    db.ZonePresence?.onInsert((presence: ZonePresence) => {
      this.zonePresenceHandlers.forEach((handler) => handler(presence));
    });

    // Subscribe to NPC table
    db.Npc?.onInsert((npc: Npc) => {
      this.npcHandlers.forEach((handler) => handler(npc));
    });

    console.log('[SpacetimeDB] Subscriptions setup complete');
  }

  /**
   * Subscribe to nearby players in a region
   */
  subscribeToRegion(regionBucket: string): void {
    if (!this.connection) return;

    this.connection
      .subscriptionBuilder()
      .subscribe([
        `SELECT * FROM EntityPosition WHERE region_bucket = '${regionBucket}'`,
        `SELECT * FROM ZonePresence WHERE zone_id = '${this.currentZoneId}'`,
      ]);
  }

  /**
   * Subscribe to a specific zone
   */
  subscribeToZone(zoneId: string): void {
    if (!this.connection) return;

    this.currentZoneId = zoneId;

    this.connection
      .subscriptionBuilder()
      .subscribe([
        `SELECT * FROM ZonePresence WHERE zone_id = '${zoneId}'`,
        `SELECT * FROM Npc WHERE zone_id = '${zoneId}'`,
      ]);
  }

  // ============ Reducer Calls ============

  /**
   * Update player position (called at 20Hz)
   */
  updatePosition(position: Position, rotation: number): void {
    if (!this.connection || !this.localPlayerId) return;

    this.connection.callReducer('update_position', {
      player_id: this.localPlayerId,
      x: position.x,
      y: position.y,
      z: position.z,
      rotation,
    });
  }

  /**
   * Enter a zone
   */
  enterZone(zoneId: string, subRegionId: string): void {
    if (!this.connection || !this.localPlayerId) return;

    this.connection.callReducer('enter_zone', {
      player_id: this.localPlayerId,
      zone_id: zoneId,
      sub_region_id: subRegionId,
    });

    this.subscribeToZone(zoneId);
  }

  /**
   * Leave current zone
   */
  leaveZone(): void {
    if (!this.connection || !this.localPlayerId || !this.currentZoneId) return;

    this.connection.callReducer('leave_zone', {
      player_id: this.localPlayerId,
      zone_id: this.currentZoneId,
    });
  }

  /**
   * Send heartbeat (for presence tracking)
   */
  heartbeat(): void {
    if (!this.connection || !this.localPlayerId) return;

    this.connection.callReducer('heartbeat', {
      player_id: this.localPlayerId,
    });
  }

  /**
   * Interact with NPC
   */
  interactWithNpc(npcId: string): void {
    if (!this.connection || !this.localPlayerId) return;

    this.connection.callReducer('interact_with_npc', {
      player_id: this.localPlayerId,
      npc_id: npcId,
    });
  }

  // ============ Event Handlers ============

  onPlayerUpdate(handler: (player: Player) => void): () => void {
    this.playerHandlers.add(handler);
    return () => this.playerHandlers.delete(handler);
  }

  onPositionUpdate(handler: (position: EntityPosition) => void): () => void {
    this.positionHandlers.add(handler);
    return () => this.positionHandlers.delete(handler);
  }

  onZonePresenceUpdate(handler: (presence: ZonePresence) => void): () => void {
    this.zonePresenceHandlers.add(handler);
    return () => this.zonePresenceHandlers.delete(handler);
  }

  onNpcUpdate(handler: (npc: Npc) => void): () => void {
    this.npcHandlers.add(handler);
    return () => this.npcHandlers.delete(handler);
  }

  // ============ Getters ============

  getState(): ConnectionState {
    return this.state;
  }

  isConnected(): boolean {
    return this.state === 'connected';
  }

  getLocalPlayerId(): string | null {
    return this.localPlayerId;
  }

  setLocalPlayerId(playerId: string): void {
    this.localPlayerId = playerId;
  }

  /**
   * Disconnect from SpacetimeDB
   */
  disconnect(): void {
    if (this.connection) {
      this.connection.disconnect();
      this.connection = null;
    }
    this.state = 'disconnected';
  }
}

// Default SpacetimeDB configuration
export const SPACETIMEDB_CONFIG = {
  uri: import.meta.env?.VITE_SPACETIMEDB_URI || 'ws://localhost:3000',
  moduleName: 'tuath-game',
};

/**
 * Create a SpacetimeDB client with default configuration
 */
export function createSpacetimeClient(
  config: Partial<SpacetimeConfig> = {}
): SpacetimeClient {
  return new SpacetimeClient({
    ...SPACETIMEDB_CONFIG,
    ...config,
  });
}
