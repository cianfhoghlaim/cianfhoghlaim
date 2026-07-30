# 2026-08-15-agent-definitions-sync-loop-v1

## Why

The 9-layer pull-based sync architecture (knowledge-sync-loop-v1 + 4
follow-ups for path drift, Dagster, BAML, stacks, DLT) covers 12 of
the 14 knowledge surfaces. The next-biggest remaining gap is the
**agent definitions surface** - the 188 .py agent files in 7
subdirs (agents/ + agents/adk/ + agents/agno/ + agents/api/ +
agents/tools/ + agents/tuatha/ + agents/meaisinfhoghlaim/) plus
the 5 AGENTS.md files.

Agent definition drift is silent: when a developer adds a new agent
to the 12-agent fleet but doesn't register it in `agent_registry.py`
+ doesn't update the routing keywords + doesn't add an AGENTS.md,
the breakage doesn't surface until the next agent registration
test. The 8 NCCA subject specialists (in agents/tuatha/agents/) are
particularly prone to drift because they were added incrementally.

This change extends the sync loop with **Layer 10 - sync:agents**
that closes the agent definitions gap.

## What changes

### Section A - The Layer 10 sync loop (5 layers + orchestrator)

5 sub-layers: agents-drift, agents-ccc, agents-cognee, agents-test,
agents-lint, plus the orchestrator sync:agents.

### Section B - The new artifacts

6 new scripts (sync/agents-*.sh), 1 new skill
(agents-sync), 25th CCC guide (agent-fleet-search), 14th Cognee
cluster (agent_definitions), agents_sync_health Dagster asset,
notebooks/29_agents_sync_dashboard.py, and
cognee_ingest_agent_definitions.py.

## Dependencies

```yaml
Blocked by: 2026-08-15-knowledge-sync-loop-v1
Blocked by (soft): 2026-08-15-stacks-sync-loop-v1
Blocked by (soft): 2026-08-15-dlt-sync-loop-v1
Affected repos: cianfhoghlaim
```
