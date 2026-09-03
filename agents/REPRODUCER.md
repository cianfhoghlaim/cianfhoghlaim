# Agents Reproducer — How to Reproduce the Agent Fleet

> **Operator's quick-start** — 6 commands from cold to green.
> Reproduces the 12-agent fleet + 8 NCCA subject specialists + 3
> educational agents on `bunchloch` (MacBook M4) or `arm1-oci`
> (Oracle Cloud Free Tier, Frankfurt).

## Pre-flight checks (4 outputs to verify)

Before running the reproducer, verify these 4:

```bash
# 1. mise is installed
mise --version
# Expected: 2026.x.x

# 2. bun is installed
bun --version
# Expected: 1.x.x

# 3. uv is installed
uv --version
# Expected: 0.x.x

# 4. Infisical vault is reachable
curl -fsS https://infisical.cianfhoghlaim.ie/api/health
# Expected: 200 OK
```

If any check fails, see the [Troubleshooting](#troubleshooting)
section.

## The 6-command sequence

### Command 1 — Install toolchain

```bash
mise install
```

Installs Python 3.12, uv, bun, dagger, pulumi, duckdb, sops,
opencode.

### Command 2 — Install Python deps

```bash
uv sync
```

Installs all Python dependencies from `pyproject.toml`.

### Command 3 — Install bun deps

```bash
bun install
```

Installs all bun/TS dependencies.

### Command 4 — Hydrate secrets

```bash
bun run secrets:env  # resolves .infisical.env → .env
bun run secrets:init  # syncs .env → dev-baile Infisical vault
```

The two commands ensure `.env` is populated from the canonical
`dev-baile` Infisical vault.

### Command 5 — Run the agent fleet smoke tests

```bash
mise run agents:smoke
```

Runs the 3 test files (`test_agent_fleet_smoke.py` +
`test_agent_wiring_audit.py` + `test_agent_registry_smoke.py`).
Expected: 12 scenarios pass.

### Command 6 — Run the reproducer script

```bash
bash scripts/reproducers/agents-fleet-reproducer.sh
```

The reproducer script verifies:

- All 12 agents load via `AGENT_REGISTRY`
- All 8 NCCA subject agents load via `agents.tuatha.<slug>_agent`
- All 3 educational agents load via
  `agents.meaisinfhoghlaim.educational.<slug>_agent`
- The 5-layer observability contract passes
- The 5-backend memory layer resolves to a backend

Expected: 6 OK lines printed.

## Total time

- Cold start (no toolchain): ~10 min
- Warm start (toolchain installed): ~3 min

## Verification (post-reproduce)

After the 6 commands complete, verify:

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
grep -n "langfuse_client\|cognee_client\|letta_client\|graphiti_client\|falkordb_client\|memgraph_client" agents/{adk,agno}/<slug>_agent.py
# Expected: 0 matches
```

## Troubleshooting

### "AGENT_FLEET_DISABLE_WIRE=1 — all wire_agent calls will return a no-op wire"

This warning is expected in CI. To force the wire-up to actually
run, unset the env var:

```bash
unset AGENT_FLEET_DISABLE_WIRE
unset AGENT_FLEET_DISABLE_MEMORY
unset SUBJECT_AGENT_DISABLE_WIRE
```

### "get_default_memory_layer(): all 5 concrete backends unreachable"

This warning is expected on a fresh dev host where none of the
5 concrete backends are running. The factory falls through to the
in-memory fallback, which is fine for the smoke tests.

To start a real backend, see the agent-platform-cluster IaC:

```bash
km run procedure deploy-agent-platform-cluster-bunchloch
```

### "agents.agent_registry not in sys.modules"

This is a load-order issue. The reproducer script handles the
load order correctly. If you see this in a custom test, ensure
`agents/agent_registry.py` is loaded before
`agents/tuatha/wiring.py`.

## Cross-references

- [`agents/AGENTS.md`](../AGENTS.md) — the quadrant overview
- [`agents/STATUS.md`](../STATUS.md) — current state of each agent
- [`agents/DEVELOPMENT.md`](../DEVELOPMENT.md) — how to add a new agent
- [`bonneagar/deploy-runbooks/agent-fleet-bunchloch-2026-08.md`](../../bonneagar/deploy-runbooks/agent-fleet-bunchloch-2026-08.md) — operator runbook for bunchloch
- [`bonneagar/deploy-runbooks/agent-fleet-arm1-oci-2026-08.md`](../../bonneagar/deploy-runbooks/agent-fleet-arm1-oci-2026-08.md) — operator runbook for arm1-oci