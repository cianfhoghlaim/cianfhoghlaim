# Agent-Fleet Deploy Runbook — bunchloch (2026-08)

> **Operator's quick-start** for deploying the 12-agent fleet +
> the 8 NCCA subject specialists + the 3 educational agents to
> `bunchloch` (MacBook M4).

## Overview

This runbook bundles the new `agents/` wiring layer into a
4-stage omnibus Komodo procedure:
`deploy-agent-fleet-bunchloch.toml`.

Reference: openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1

## Pre-flight (4 outputs to verify)

1. **Mise toolchain installed**:
   ```bash
   mise --version
   # Expected: 2026.x.x
   ```

2. **bun installed**:
   ```bash
   bun --version
   # Expected: 1.x.x
   ```

3. **uv installed**:
   ```bash
   uv --version
   # Expected: 0.x.x
   ```

4. **Komodo Core reachable**:
   ```bash
   curl -fsS http://komodo.cianfhoghlaim.ie/api/health
   # Expected: 200 OK
   ```

## The 5-command sequence

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

### Command 4 — Run the agent fleet smoke tests

```bash
mise run agents:smoke
```

Expected: 12 scenarios pass.

### Command 5 — Run the omnibus procedure

```bash
km run procedure deploy-agent-fleet-bunchloch
```

Expected:
- Stage 1: pre-reqs verified (4 cross-cutting prerequisites)
- Stage 2: 8 supporting stacks deployed
- Stage 3: 3 agent surfaces deployed
- Stage 4: health verify (12 + 8 + 3 agents reachable)

## Total time

- Cold start (no toolchain): ~15 min
- Warm start (toolchain installed): ~5 min
- Procedure runtime: ~10 min

## Post-archive verification

After the omnibus procedure completes:

```bash
# 12-agent fleet
python -c "from cianfhoghlaim.agents import AGENT_REGISTRY; print(len(AGENT_REGISTRY))"
# Expected: 20 (12 main + 8 NCCA subject)

# 5-layer observability
python -c "from cianfhoghlaim.agents.observability_hooks import verify_5_layer_contract; print(all(verify_5_layer_contract().values()))"
# Expected: True

# 5-backend memory layer
python -c "from cianfhoghlaim.agents.memory_layer import get_default_memory_layer; print(get_default_memory_layer().kind)"
# Expected: one of {cognee, graphiti, lancedb, falkordb, memgraph, in_memory_fallback}

# Direct-import audit
mise run agents:audit
# Expected: 0 violations
```

## Rollback

```bash
km run procedure rollback deploy-agent-fleet-bunchloch
```

The rollback procedure tears down Stages 4, 3, 2 in reverse order.

## Cross-references

- [`agents/AGENTS.md`](../../../agents/AGENTS.md) — the quadrant overview
- [`agents/REPRODUCER.md`](../../../agents/REPRODUCER.md) — how to reproduce the fleet from cold
- `bonneagar/komodo/procedures/deploy-agent-fleet-bunchloch.toml` — the omnibus procedure
- `bonneagar/komodo/procedures/server_id_legend.md` — the server_id convention