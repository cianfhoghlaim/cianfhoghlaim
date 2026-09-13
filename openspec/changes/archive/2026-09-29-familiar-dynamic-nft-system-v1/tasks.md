# Tasks: Familiar Dynamic NFT System

## Stage 0 — Pre-flight
- [ ] T0.1 — Confirm changes 1 + 2 (Celtic Mythology + Ogham Stones) are merged
- [ ] T0.2 — Create the new spec dir

## Stage 1 — Convex tables
- [ ] T1.1 — Add `familiars.ts`
- [ ] T1.2 — Add `anam_particles.ts`
- [ ] T1.3 — Add `familiar_evolution_log.ts`
- [ ] T1.4 — Run `mise run convex:dev`

## Stage 2 — Fibo enablement
- [ ] T2.1 — Flip `local/image/fibo: true` in `deployment-choice.yaml`
- [ ] T2.2 — Create `bonneagar/stacks/fibo-server/`
- [ ] T2.3 — Add `fibo-server` Komodo procedure
- [ ] T2.4 — Add `fibo-server` Infisical item
- [ ] T2.5 — Run `mise run cic:stack-doctor`

## Stage 3 — Anam Progression Agent
- [ ] T3.1 — Create `anam_progression_agent.py`
- [ ] T3.2 — Register in `AGENT_REGISTRY`
- [ ] T3.3 — Run `mise run agents:smoke`

## Stage 4 — Marimo generator
- [ ] T4.1 — Create `notebooks/38_familiar_generator.py`
- [ ] T4.2 — Run `mise run notebook:familiar`

## Stage 5 — AG-UI Familiar card
- [ ] T5.1 — Create `familiar-card.tsx`
- [ ] T5.2 — Wire to CopilotKit AG-UI runtime

## Stage 6 — x402-gated endpoint
- [ ] T6.1 — Create `evolve.tsx`
- [ ] T6.2 — Wire to x402 hybrid educational credential flow

## Stage 7 — Validation + handoff
- [ ] T7.1 — Run `mise run lint:skills`
- [ ] T7.2 — Run `openspec validate 2026-09-29-familiar-dynamic-nft-system-v1 --strict`
- [ ] T7.3 — Run `mise run sync:all`
- [ ] T7.4 — Update `.agents/skills/familiar-dynamic-nft-system/SKILL.md`