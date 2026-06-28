# SpacetimeDB Cookbook — KCG Summary

## What It Is
The SpacetimeDB Cookbook is a curated collection of runnable example projects demonstrating real-time multiplayer patterns with SpacetimeDB. It covers web requests, multi-position updates, Unity chat, OIDC auth, VoIP, and the publish workflow. Each project is a self-contained module with its own README walking through schema, reducers, and client code.

## Why This Matters for Kings' College Galway
The `sruth/tuatha/` educational MMO borrows heavily from the cookbook's patterns — especially the **web-request-example** (which maps to our `sruth/tuatha/ui` Babylon.js client connecting to a SpacetimeDB server) and **multiple-position-updates** (which mirrors the spatial sync of student avatars in the Celtic-themed classroom). **unity-chat-system** informs our text-chat system between students and AI NPCs. The cookbook's **oidc-test** example also informs how we plan to use Pocket ID for federated identity.

## Key Patterns Preserved
- **web-request-example/README.md** — SpacetimeDB web client with request/response pattern
- **web-request-example/frontend/README.md** — Frontend wiring for the web example
- **voip-test/README.md** — Voice-over-IP testing harness for in-game audio
- **unity-chat-system/README.md** — Unity-based chat client (mirrors Babylon.js chat)
- **multiple-position-updates/README.md** — High-frequency position sync (avatars, particles)
- **oidc-test/README.md** — OpenID Connect authentication flow
- **spacetime-publish-workflow/README.md** — Publishing modules to SpacetimeDB cloud

## Source Files
Full source code removed (2026-06-06). The 306 deleted files include the Rust server modules (`Cargo.toml`, `Cargo.lock`, `*.rs`, `*.wat`), TypeScript clients (`package.json`, `*.ts`, `*.tsx`, `tsconfig.json`, `node_modules/`), Unity project files (`Assets/`, `ProjectSettings/`, `Packages/`), and supporting assets. Available at <https://github.com/SpacetimeDB/cookbook>.

## What Was Removed
- Rust source: `*.rs`, `Cargo.toml`, `Cargo.lock`
- TypeScript/JavaScript: `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `package.json`, `package-lock.json`, `yarn.lock`, `tsconfig.json`
- Unity project: `Assets/`, `ProjectSettings/`, `Packages/`, `*.unity`, `*.prefab`
- Web frontend build outputs: `node_modules/`, `dist/`, `build/`
- Lockfiles: `Cargo.lock`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- CI / repo config: `.github/`, `.gitignore`, `.editorconfig`
- License files (project LICENSE removed — see upstream)
