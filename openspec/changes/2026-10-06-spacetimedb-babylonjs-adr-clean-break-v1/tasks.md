# Tasks: SpacetimeDB + Babylon.js ADR Clean Break

## Stage 0 — Pre-flight
- [ ] T0.1 — Confirm changes 1, 2, 3, 4, 5 are merged
- [ ] T0.2 — Create the new spec dir

## Stage 1 — Document the ADRs
- [ ] T1.1 — Create `openspec/specs/tuatha-platform/adr-001-spacetimedb-rejection.md`
- [ ] T1.2 — Create `openspec/specs/tuatha-platform/adr-002-babylonjs-retirement.md`
- [ ] T1.3 — Create `openspec/specs/tuatha-platform/spec.md`

## Stage 2 — Archive the orphaned Rust crates
- [ ] T2.1 — Create `bonneagar/iac/_archive/rust-crates-2026-10/`
- [ ] T2.2 — Move `agents/api/_rust_crates/stdb-modules/tuath-game/` to archive
- [ ] T2.3 — Move `agents/api/_rust_crates/services/nft-relayer/` to archive
- [ ] T2.4 — Move `agents/api/_rust_crates/solana/` to archive
- [ ] T2.5 — Update `agents/api/_rust_crates/Cargo.toml`
- [ ] T2.6 — Verify no active code references the archived crates
- [ ] T2.7 — Run `mise run cargo:check`

## Stage 3 — Retire Babylon.js
- [ ] T3.1 — Search for `@babylonjs/*` imports in `web/apps/tuatha-ui/`
- [ ] T3.2 — Remove all Babylon.js imports from `web/apps/tuatha-ui/`
- [ ] T3.3 — Remove `@babylonjs/*` packages from `package.json`
- [ ] T3.4 — Update `.agents/skills/babylonjs/SKILL.md`
- [ ] T3.5 — Run `bun run turbo dev`

## Stage 4 — Validate + handoff
- [ ] T4.1 — Run `mise run lint:skills`
- [ ] T4.2 — Run `mise run lint:drift-docs`
- [ ] T4.3 — Run `openspec validate 2026-10-06-spacetimedb-babylonjs-adr-clean-break-v1 --strict`
- [ ] T4.4 — Run `mise run sync:all`