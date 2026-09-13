# Change: Familiar Dynamic NFT System (Cúchulainn/Sétanta Evolution on Convex + Fibo)

## Why

The Web3 Gamified Education & Asset Generation research (~40KB) proposes
a "Celtic Knowledge Grid" with dynamic NFT Familiars (Cúchulainn evolves
from Sétanta via the warp spasm / ríastrad mechanic). The platform has:

- ✅ Convex backend (`web/apps/cianfhoghlaim-mmo/convex/`)
- ✅ x402 hybrid educational credential (Convex.badges + credentialAnchors)
- ✅ mcp-ui / CopilotKit runtime
- ✅ Bria Fibo slot in MODEL_REGISTRY (disabled)
- ✅ 8 NCCA subject specialists

But is MISSING:
- ❌ Convex `familiars` table
- ❌ Convex `anam_particles` table (Anam progression state)
- ❌ Fibo enablement in `deployment-choice.yaml`
- ❌ `fibo-server` Docker stack
- ❌ Celtic-themed Familiar evolution logic
- ❌ `anam_progression_agent.py`

This change fills the gap.

## What changes

- **Familiar Dynamic NFT System** (NEW capability
  `familiar-dynamic-nft-system`): 3 Convex tables (familiars,
  anam_particles, familiar_evolution_log) + 1 agent +
  1 marimo generator + 1 AG-UI component + 1 x402 endpoint.

- **Fibo enablement** (capability
  `centralized-model-registry`): flip
  `local/image/fibo` from `false` → `true` in
  `deployment-choice.yaml`.

- **fibo-server Docker stack** (capability
  `infrastructure-stacks`): new 6-file GOLD_STANDARD stack
  at `bonneagar/stacks/fibo-server/`.

- **Celtic-themed evolution stages** (capability
  `cianfhoghlaim-educational-mmo`): the Sétanta → Cúchulainn
  evolution mapped to 6 learning levels.

- **Anam Progression Agent** (capability
  `meaisinfhoghlaim-agent-frameworks`): new ADK agent with
  6 tools: `mint_familiar`, `evolve_familiar`, `get_anam_state`,
  `claim_daily_anchor`, `gacha_roll`, `query_familiar_lineage`.

## Out of scope

- The Web3 token / financial layer (explicitly rejected).
- The Solana / Token-2022 mechanics.
- The SpacetimeDB backend (per ADR-1).

## Dependencies

```markdown
## Dependencies

`Blocked by: 2026-09-01-celtic-mythology-content-system-v1` (needs the deity mapping + mythology BAML).

`Blocked by: 2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1` (x402 wiring).

`Blocked by (soft): 2026-09-08-ogham-celtic-stones-pipeline-v1` (Anam particles from Ogham stones flow into Familiar evolution).

`Affected repos: cianfhoghlaim`
```

## Impact

- Affected specs:
  - NEW: `familiar-dynamic-nft-system` (7 ADDED Requirements)
  - `cianfhoghlaim-educational-mmo` (1 ADDED Requirement)
  - `centralized-model-registry` (1 ADDED Requirement)
  - `deployment-control-panel` (1 ADDED Requirement)
  - `infrastructure-stacks` (1 ADDED Requirement)
- Affected code/config:
  - `deployment-choice.yaml` (1 line flip)
  - `bonneagar/stacks/fibo-server/` (NEW; 6 GOLD_STANDARD files)
  - `web/apps/cianfhoghlaim-mmo/convex/familiars.ts` (NEW)
  - `web/apps/cianfhoghlaim-mmo/convex/anam_particles.ts` (NEW)
  - `web/apps/cianfhoghlaim-mmo/convex/familiar_evolution_log.ts` (NEW)
  - `agents/meaisinfhoghlaim/educational/anam_progression_agent.py` (NEW)
  - `notebooks/38_familiar_generator.py` (NEW)
  - `web/apps/cianfhoghlaim-mmo/src/components/familiar-card.tsx` (NEW)
  - `web/apps/cianfhoghlaim-mmo/src/routes/api/familiars/evolve.tsx` (NEW)