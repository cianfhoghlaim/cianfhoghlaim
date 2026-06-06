# SpacetimeDB — KCG Summary

## What It Is
SpacetimeDB is a real-time, multiplayer database engine that combines a relational database with a game server — eliminating the client/server boundary. Created by Clockwork Labs, it enables sub-millisecond state synchronization for multiplayer applications.

## Why This Matters for Kings' College Galway

The `tuatha/` educational MMO uses SpacetimeDB for real-time multiplayer state management — student positions in the virtual classroom, collaborative problem-solving sessions, and shared educational game state. Its SQL-based API means curriculum data from DuckDB/Iceberg tables can be queried directly from game logic. The TypeScript SDK integrates with Babylon.js for 3D rendering in the browser.

## Key Patterns

- **Server-authoritative state**: All game state lives in SpacetimeDB; clients send commands, not state changes
- **SQL-as-game-loop**: Game logic is written as SQL modules that execute on state changes
- **TypeScript SDK**: `@clockworklabs/spacetimedb-sdk` enables browser-based multiplayer
- **Zero-networking-code**: SpacetimeDB handles WebSocket connections, serialization, and state sync automatically

## Integration

- Connects to the curriculum knowledge graph (Cognee/Graphiti) for quest prerequisite data
- Uses the LiteLLM gateway for AI-driven NPC dialogue
- Serves the `tuatha/ui` Babylon.js frontend via WebSocket

## Source Files
This directory contains documentation only. Full source code was removed (2026-06-05) — it is available at <https://github.com/clockworklabs/SpacetimeDB>.
