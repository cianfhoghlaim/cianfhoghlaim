# SpacetimeDB Guide

Comprehensive guide to using SpacetimeDB for real-time multiplayer in the Tuath Celtic MMO.

## Overview

SpacetimeDB is a real-time database platform that combines database and server functionality. It enables:
- Real-time data synchronization via WebSockets
- Server-side logic with Reducers
- Automatic client code generation
- Horizontal scaling for multiplayer games

### Reference Materials

| Resource | Path |
|----------|------|
| Core Library | `taighde/game/SpacetimeDB/` |
| TypeScript SDK | `taighde/game/spacetimedb-typescript-sdk/` |
| Cookbook | `taighde/game/spacetimedb-cookbook/` |
| Workshop | `taighde/game/hophacks-spacetimedb-workshop/` |

---

## Core Concepts

### Tables

Tables define your game state schema:

```rust
// server/src/lib.rs

use spacetimedb::{spacetimedb, ReducerContext, Identity, Timestamp};

#[spacetimedb(table)]
pub struct Player {
    #[primarykey]
    pub id: u64,

    #[unique]
    pub identity: Identity,

    pub name: String,
    pub position_x: f32,
    pub position_y: f32,
    pub position_z: f32,
    pub rotation_y: f32,
    pub zone_id: String,
    pub sub_region: String,
    pub xp: u32,
    pub level: u16,
    pub created_at: Timestamp,
    pub updated_at: Timestamp,
}

#[spacetimedb(table)]
pub struct ChatMessage {
    #[autoinc]
    #[primarykey]
    pub id: u64,

    pub sender_id: u64,
    pub zone_id: String,
    pub content: String,
    pub timestamp: Timestamp,
}
```

### Reducers

Reducers are server-side functions that modify state:

```rust
// server/src/reducers.rs

use spacetimedb::{spacetimedb, ReducerContext, Identity, Timestamp};
use crate::{Player, ChatMessage};

#[spacetimedb(reducer)]
pub fn create_player(ctx: ReducerContext, name: String) -> Result<(), String> {
    // Check if player already exists
    if Player::filter_by_identity(&ctx.sender).is_some() {
        return Err("Player already exists".to_string());
    }

    // Validate name
    if name.len() < 2 || name.len() > 20 {
        return Err("Name must be 2-20 characters".to_string());
    }

    // Generate unique ID
    let id = Player::iter().count() as u64 + 1;

    // Create player
    Player::insert(Player {
        id,
        identity: ctx.sender,
        name,
        position_x: 0.0,
        position_y: 0.0,
        position_z: 0.0,
        rotation_y: 0.0,
        zone_id: "gaeltacht".to_string(),
        sub_region: "village".to_string(),
        xp: 0,
        level: 1,
        created_at: ctx.timestamp,
        updated_at: ctx.timestamp,
    })?;

    Ok(())
}

#[spacetimedb(reducer)]
pub fn update_position(
    ctx: ReducerContext,
    position_x: f32,
    position_y: f32,
    position_z: f32,
    rotation_y: f32,
) -> Result<(), String> {
    // Find player by identity
    let mut player = Player::filter_by_identity(&ctx.sender)
        .ok_or("Player not found")?;

    // Update position
    player.position_x = position_x;
    player.position_y = position_y;
    player.position_z = position_z;
    player.rotation_y = rotation_y;
    player.updated_at = ctx.timestamp;

    // Save changes
    Player::update_by_id(&player.id, player)?;

    Ok(())
}

#[spacetimedb(reducer)]
pub fn enter_zone(
    ctx: ReducerContext,
    zone_id: String,
    sub_region: String,
) -> Result<(), String> {
    let mut player = Player::filter_by_identity(&ctx.sender)
        .ok_or("Player not found")?;

    // Validate zone
    let valid_zones = ["gaeltacht", "alba", "cymru"];
    if !valid_zones.contains(&zone_id.as_str()) {
        return Err("Invalid zone".to_string());
    }

    player.zone_id = zone_id;
    player.sub_region = sub_region;
    player.updated_at = ctx.timestamp;

    Player::update_by_id(&player.id, player)?;

    Ok(())
}

#[spacetimedb(reducer)]
pub fn send_chat(
    ctx: ReducerContext,
    content: String,
) -> Result<(), String> {
    let player = Player::filter_by_identity(&ctx.sender)
        .ok_or("Player not found")?;

    // Validate content
    if content.is_empty() || content.len() > 500 {
        return Err("Message must be 1-500 characters".to_string());
    }

    ChatMessage::insert(ChatMessage {
        id: 0, // autoinc
        sender_id: player.id,
        zone_id: player.zone_id.clone(),
        content,
        timestamp: ctx.timestamp,
    })?;

    Ok(())
}
```

### Subscriptions

Clients subscribe to relevant data subsets:

```rust
// Subscription queries define what data clients receive

#[spacetimedb(subscription)]
pub fn players_in_zone(zone_id: String, sub_region: String) {
    // Subscribe to players in same zone/region
    Player::filter_by_zone_id(&zone_id)
        .filter(|p| p.sub_region == sub_region)
}

#[spacetimedb(subscription)]
pub fn zone_chat(zone_id: String) {
    // Subscribe to chat in current zone
    ChatMessage::filter_by_zone_id(&zone_id)
}
```

---

## TypeScript Client

### Connection Setup

```typescript
// network/spacetime-client.ts

import { SpacetimeDBClient, Identity } from '@clockworklabs/spacetimedb-sdk';
import { Player, ChatMessage } from './module_bindings';

export class GameClient {
  private client: SpacetimeDBClient;
  private identity: Identity | null = null;

  constructor() {
    this.client = new SpacetimeDBClient(
      'wss://spacetime.clockworklabs.net',
      'tuath-celtic-mmo',
    );
  }

  async connect(): Promise<void> {
    // Load or generate identity
    const storedIdentity = localStorage.getItem('spacetime_identity');

    if (storedIdentity) {
      this.identity = Identity.fromString(storedIdentity);
    }

    return new Promise((resolve, reject) => {
      this.client.onConnect((identity, token) => {
        this.identity = identity;
        localStorage.setItem('spacetime_identity', identity.toString());
        localStorage.setItem('spacetime_token', token);
        resolve();
      });

      this.client.onError((error) => {
        reject(error);
      });

      this.client.connect(this.identity?.toString());
    });
  }

  disconnect(): void {
    this.client.disconnect();
  }
}
```

### Subscribing to Data

```typescript
// network/subscriptions.ts

import { Player, ChatMessage } from './module_bindings';

export function setupSubscriptions(
  client: GameClient,
  zoneId: string,
  subRegion: string,
): void {
  // Subscribe to players in zone
  client.subscribe([
    `SELECT * FROM Player WHERE zone_id = '${zoneId}' AND sub_region = '${subRegion}'`,
  ]);

  // Subscribe to chat
  client.subscribe([
    `SELECT * FROM ChatMessage WHERE zone_id = '${zoneId}' ORDER BY timestamp DESC LIMIT 100`,
  ]);
}

// Handle player updates
Player.onInsert((player: Player) => {
  console.log('Player joined:', player.name);
  gameScene.spawnPlayer(player);
});

Player.onUpdate((oldPlayer: Player, newPlayer: Player) => {
  gameScene.updatePlayer(newPlayer);
});

Player.onDelete((player: Player) => {
  console.log('Player left:', player.name);
  gameScene.removePlayer(player.id);
});

// Handle chat messages
ChatMessage.onInsert((message: ChatMessage) => {
  chatUI.addMessage(message);
});
```

### Calling Reducers

```typescript
// network/reducers.ts

import {
  create_player,
  update_position,
  enter_zone,
  send_chat,
} from './module_bindings';

export async function createPlayer(name: string): Promise<void> {
  await create_player(name);
}

export async function updatePosition(
  x: number,
  y: number,
  z: number,
  rotY: number,
): Promise<void> {
  await update_position(x, y, z, rotY);
}

export async function enterZone(
  zoneId: string,
  subRegion: string,
): Promise<void> {
  await enter_zone(zoneId, subRegion);
}

export async function sendChatMessage(content: string): Promise<void> {
  await send_chat(content);
}
```

---

## Position Synchronization

### Rate-Limited Updates

```typescript
// network/position-sync.ts

const SYNC_RATE = 20; // 20 updates per second
const POSITION_THRESHOLD = 0.1; // meters
const ROTATION_THRESHOLD = 0.01; // radians

export class PositionSync {
  private lastSentPosition = { x: 0, y: 0, z: 0 };
  private lastSentRotation = 0;
  private syncInterval: number | null = null;

  start(getPosition: () => Position): void {
    this.syncInterval = window.setInterval(() => {
      const pos = getPosition();

      if (this.shouldSync(pos)) {
        updatePosition(pos.x, pos.y, pos.z, pos.rotY);
        this.lastSentPosition = { x: pos.x, y: pos.y, z: pos.z };
        this.lastSentRotation = pos.rotY;
      }
    }, 1000 / SYNC_RATE);
  }

  private shouldSync(pos: Position): boolean {
    const dx = pos.x - this.lastSentPosition.x;
    const dy = pos.y - this.lastSentPosition.y;
    const dz = pos.z - this.lastSentPosition.z;
    const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);

    const rotDelta = Math.abs(pos.rotY - this.lastSentRotation);

    return distance > POSITION_THRESHOLD || rotDelta > ROTATION_THRESHOLD;
  }

  stop(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }
  }
}
```

### Interpolation for Smooth Movement

```typescript
// entities/remote-player.ts

import { Vector3 } from '@babylonjs/core';

export class RemotePlayer {
  private targetPosition: Vector3;
  private currentPosition: Vector3;
  private targetRotation: number = 0;
  private currentRotation: number = 0;
  private interpolationSpeed: number = 10;

  constructor(initialPosition: Vector3) {
    this.currentPosition = initialPosition.clone();
    this.targetPosition = initialPosition.clone();
  }

  setTarget(x: number, y: number, z: number, rotY: number): void {
    this.targetPosition.set(x, y, z);
    this.targetRotation = rotY;
  }

  update(deltaTime: number): void {
    // Lerp position
    this.currentPosition = Vector3.Lerp(
      this.currentPosition,
      this.targetPosition,
      this.interpolationSpeed * deltaTime,
    );

    // Lerp rotation
    this.currentRotation = this.lerpAngle(
      this.currentRotation,
      this.targetRotation,
      this.interpolationSpeed * deltaTime,
    );

    // Update mesh
    this.mesh.position = this.currentPosition;
    this.mesh.rotation.y = this.currentRotation;
  }

  private lerpAngle(current: number, target: number, t: number): number {
    let diff = target - current;

    // Handle wrap-around
    while (diff > Math.PI) diff -= 2 * Math.PI;
    while (diff < -Math.PI) diff += 2 * Math.PI;

    return current + diff * t;
  }
}
```

---

## Zone-Based Subscriptions

### Efficient Data Loading

```typescript
// network/zone-manager.ts

export class ZoneSubscriptionManager {
  private currentZone: string | null = null;
  private currentRegion: string | null = null;

  async enterZone(
    client: GameClient,
    zoneId: string,
    subRegion: string,
  ): Promise<void> {
    // Unsubscribe from old zone
    if (this.currentZone) {
      await this.leaveZone(client);
    }

    // Update server state
    await enter_zone(zoneId, subRegion);

    // Subscribe to new zone data
    await client.subscribe([
      // Players in same region
      `SELECT * FROM Player WHERE zone_id = '${zoneId}' AND sub_region = '${subRegion}'`,

      // Players in adjacent regions (for seamless transitions)
      `SELECT * FROM Player WHERE zone_id = '${zoneId}' AND sub_region IN (${this.getAdjacentRegions(subRegion).map(r => `'${r}'`).join(',')})`,

      // Zone chat
      `SELECT * FROM ChatMessage WHERE zone_id = '${zoneId}' ORDER BY timestamp DESC LIMIT 50`,

      // Zone NPCs
      `SELECT * FROM NPC WHERE zone_id = '${zoneId}'`,

      // Zone interactables
      `SELECT * FROM Interactable WHERE zone_id = '${zoneId}'`,
    ]);

    this.currentZone = zoneId;
    this.currentRegion = subRegion;
  }

  private async leaveZone(client: GameClient): Promise<void> {
    // Clear subscriptions (SpacetimeDB handles this automatically)
    this.currentZone = null;
    this.currentRegion = null;
  }

  private getAdjacentRegions(region: string): string[] {
    // Define region adjacency map
    const adjacencyMap: Record<string, string[]> = {
      village: ['forest', 'coast'],
      forest: ['village', 'mountain'],
      coast: ['village', 'harbor'],
      mountain: ['forest'],
      harbor: ['coast'],
    };

    return adjacencyMap[region] || [];
  }
}
```

---

## Module Deployment

### Building and Publishing

```bash
# Build the module
cd server
spacetime build

# Deploy to SpacetimeDB Cloud
spacetime publish tuath-celtic-mmo

# Or deploy to self-hosted instance
spacetime publish tuath-celtic-mmo --host ws://localhost:3000

# Generate TypeScript bindings
spacetime generate --lang typescript --out-dir ../client/src/module_bindings
```

### Cargo.toml Configuration

```toml
# server/Cargo.toml

[package]
name = "tuath-server"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
spacetimedb = "0.8"
log = "0.4"
serde = { version = "1.0", features = ["derive"] }

[profile.release]
lto = true
opt-level = "z"
```

---

## Testing

### Unit Tests

```rust
// server/src/tests.rs

#[cfg(test)]
mod tests {
    use super::*;
    use spacetimedb_testing::TestContext;

    #[test]
    fn test_create_player() {
        let ctx = TestContext::new();

        // Create player
        let result = create_player(ctx.make_reducer_context(), "TestPlayer".to_string());
        assert!(result.is_ok());

        // Verify player exists
        let player = Player::filter_by_identity(&ctx.sender).unwrap();
        assert_eq!(player.name, "TestPlayer");
        assert_eq!(player.level, 1);
    }

    #[test]
    fn test_update_position() {
        let ctx = TestContext::new();

        // Create player first
        create_player(ctx.make_reducer_context(), "TestPlayer".to_string()).unwrap();

        // Update position
        let result = update_position(
            ctx.make_reducer_context(),
            10.0, 5.0, 20.0, 1.57,
        );
        assert!(result.is_ok());

        // Verify position
        let player = Player::filter_by_identity(&ctx.sender).unwrap();
        assert_eq!(player.position_x, 10.0);
        assert_eq!(player.position_z, 20.0);
    }
}
```

### Integration Tests

```typescript
// tests/integration/spacetimedb.test.ts

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { GameClient } from '../src/network/spacetime-client';

describe('SpacetimeDB Integration', () => {
  let client: GameClient;

  beforeAll(async () => {
    client = new GameClient();
    await client.connect();
  });

  afterAll(() => {
    client.disconnect();
  });

  it('should create player', async () => {
    await createPlayer('IntegrationTestPlayer');

    // Wait for subscription update
    await new Promise(resolve => setTimeout(resolve, 100));

    const players = Player.all();
    const player = players.find(p => p.name === 'IntegrationTestPlayer');

    expect(player).toBeDefined();
    expect(player?.level).toBe(1);
  });

  it('should update position', async () => {
    await updatePosition(5.0, 0.0, 10.0, 0.0);

    await new Promise(resolve => setTimeout(resolve, 100));

    const player = Player.filterByIdentity(client.identity);
    expect(player?.position_x).toBeCloseTo(5.0);
    expect(player?.position_z).toBeCloseTo(10.0);
  });
});
```

---

## Performance Considerations

### Subscription Optimization

```rust
// Use indexed columns for subscription queries
#[spacetimedb(table)]
pub struct Player {
    #[primarykey]
    pub id: u64,

    #[unique]
    pub identity: Identity,

    #[index(btree)]  // Index for zone queries
    pub zone_id: String,

    #[index(btree)]  // Index for region queries
    pub sub_region: String,

    // ...
}
```

### Reducing Data Transfer

```rust
// Only update changed fields
#[spacetimedb(reducer)]
pub fn update_position_minimal(
    ctx: ReducerContext,
    x: f32,
    z: f32,
    rot: f32,
) -> Result<(), String> {
    // Only x, z, rotation - skip y (usually ground level)
    let mut player = Player::filter_by_identity(&ctx.sender)
        .ok_or("Player not found")?;

    player.position_x = x;
    player.position_z = z;
    player.rotation_y = rot;
    // Don't update timestamp for position (reduces overhead)

    Player::update_by_id(&player.id, player)?;
    Ok(())
}
```

---

## Related Documentation

- [Game Client](../../sruth/tuath/docs/GAME_CLIENT.md) - Babylon.js integration
- [Architecture](../../sruth/tuath/docs/ARCHITECTURE.md) - System overview
- [Cookbook Examples](../spacetimedb-cookbook/) - More examples
