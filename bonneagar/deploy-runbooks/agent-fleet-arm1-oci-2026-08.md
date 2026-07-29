# Agent-Fleet Deploy Runbook — arm1-oci (2026-08)

> **Operator's quick-start** for deploying the 12-agent fleet +
> the 8 NCCA subject specialists + the 3 educational agents to
> `arm1-oci` (Oracle Cloud Free Tier, Frankfurt).

## Overview

This runbook bundles the new `agents/` wiring layer into a
6-stage omnibus Komodo procedure with `preflight:arm-oci` as
Stage 1:
`deploy-agent-fleet-arm1-oci.toml`.

Reference: openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1

## Pre-flight (5 outputs to verify)

1. **Mise toolchain installed**:
   ```bash
   mise --version
   ```

2. **bun installed**:
   ```bash
   bun --version
   ```

3. **uv installed**:
   ```bash
   uv --version
   ```

4. **WARP + Locket reachable**:
   ```bash
   curl -fsS https://locket.cianfhoghlaim.ie/api/health
   # Expected: 200 OK
   ```

5. **`preflight:arm-oci` passes**:
   ```bash
   bun run preflight:arm-oci --strict --emit-md
   # Expected: ALL CHECKS PASSED
   ```

## The 6-command sequence

### Command 1 — Install toolchain

```bash
mise install
```

### Command 2 — Install Python deps

```bash
uv sync
```

### Command 3 — Install bun deps

```bash
bun install
```

### Command 4 — Hydrate secrets

```bash
bun run secrets:env  # resolves .infisical.env → .env
bun run secrets:init  # syncs .env → dev-baile Infisical vault
```

### Command 5 — Run the agent fleet smoke tests

```bash
mise run agents:smoke
```

Expected: 12 scenarios pass.

### Command 6 — Run the omnibus procedure

```bash
km run procedure deploy-agent-fleet-arm1-oci
```

Expected:
- Stage 1: `preflight:arm-oci` passes + 4 cross-cutting prerequisites verified
- Stage 2: control-plane foundation (pangolin + langfuse + observability)
- Stage 3: 8 supporting stacks deployed
- Stage 4: 3 agent surfaces deployed
- Stage 5: Pangolin routes applied (12 + 8 + 3 agents)
- Stage 6: 3 health endpoints return 200

## Total time

- Cold start (no toolchain): ~25 min
- Warm start (toolchain installed): ~15 min
- Procedure runtime: ~15 min

## Post-archive verification

After the omnibus procedure completes:

```bash
# 3 health endpoints (the canonical contract)
curl -fsS https://hermes.cianfhoghlaim.ie/api/health
curl -fsS https://openclaw.cianfhoghlaim.ie/api/health
curl -fsS https://openchamber.cianfhoghlaim.ie/api/health
# Expected: 200 OK each

# 12-agent fleet
python -c "from cianfhoghlaim.agents import AGENT_REGISTRY; print(len(AGENT_REGISTRY))"
# Expected: 20

# 5-layer observability
python -c "from cianfhoghlaim.agents.observability_hooks import verify_5_layer_contract; print(all(verify_5_layer_contract().values()))"
# Expected: True

# 5-backend memory layer
python -c "from cianfhoghlaim.agents.memory_layer import get_default_memory_layer; print(get_default_memory_layer().kind)"
# Expected: one of {cognee, graphiti, lancedb, falkordb, memgraph, in_memory_fallback}
```

## Rollback

```bash
km run procedure rollback deploy-agent-fleet-arm1-oci
```

The rollback procedure tears down Stages 6, 5, 4, 3, 2 in reverse
order. Stage 1 (preflight) is not rolled back.

## Cross-references

- [`agents/AGENTS.md`](../../../agents/AGENTS.md) — the quadrant overview
- [`agents/REPRODUCER.md`](../../../agents/REPRODUCER.md) — how to reproduce the fleet from cold
- `bonneagar/komodo/procedures/deploy-agent-fleet-arm1-oci.toml` — the omnibus procedure
- `bonneagar/komodo/procedures/server_id_legend.md` — the server_id convention
- `bonneagar/deploy-runbooks/openclaw-hermes-bunchloch-local-2026-07.md` — the prior bunchloch runbook