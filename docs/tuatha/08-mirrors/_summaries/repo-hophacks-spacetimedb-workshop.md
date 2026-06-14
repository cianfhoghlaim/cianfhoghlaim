# hophacks-spacetimedb-workshop — KCG Summary

## What It Is
A SpacetimeDB TypeScript + React quickstart chat application, originally built as a HopHacks workshop example. Demonstrates multiplayer real-time chat using SpacetimeDB as the game server with a Vite + React + TypeScript frontend and a Rust module backend. Based on the official SpacetimeDB TypeScript quickstart guide.

## Why This Matters for Kings' College Galway
The `tuatha/` educational MMO's multiplayer classroom chat system is directly modeled on this workshop example. The Rust server module pattern (`server-rs/src/lib.rs`) shows how to define SpacetimeDB tables, reducers, and scheduled operations — the same pattern used for the MMO's quiz response system, student presence tracking, and collaborative problem-solving sessions. The React frontend shows how the `@clockworklabs/spacetimedb-sdk` connects to a SpacetimeDB server with auto-generated module bindings.

## Key Patterns Preserved
- **README.md** — Project overview and SpacetimeDB quickstart guide references
- **server-rs/README.md** — Rust module server documentation

## Source Files
Full source code removed (2026-06-06). The 30 deleted files include TypeScript source (`*.ts`, `*.tsx`), Rust source (`*.rs`, `Cargo.toml`, `.cargo/config.toml`), build config (`tsconfig.json`, `vite.config.ts`, `package.json`, `package-lock.json`), React components and styles, SVG assets, and the `LICENSE` file. Available at <https://github.com/clockworklabs/hophacks-spacetimedb-workshop>.

## What Was Removed
- TypeScript/JavaScript: `*.ts`, `*.tsx`, `*.js`, `*.jsx`
- Rust: `*.rs`, `Cargo.toml`
- Build config: `tsconfig.json`, `vite.config.ts`, `package.json`, `package-lock.json`
- Assets: `*.svg`, `*.css`, `*.html`
- Repo config: `.gitignore`, `.cargo/config.toml`
- License file
