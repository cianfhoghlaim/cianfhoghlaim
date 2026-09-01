# Agents Development — How to Add a New Agent

> **The 8-step recipe** for adding a new agent to the
> Cianfhoghlaim agent fleet. Mirrors the canonical
> `agents/tuatha/wiring.py:SubjectAgentWiring` pattern but
> extended for the 12-agent fleet.

## The 8-step recipe

### Step 1 — Decide the framework

Pick one of the 5 frameworks:

- **Custom** — query routing + LiteLLM orchestration
- **ADK** (Google Agent Development Kit) — single-agent specialists
- **Agno** — multi-agent coordination (LoopAgent, SequentialAgent)
- **Pipecat** — voice/audio (deferred)
- **CopilotKit** — front-end consumer (deferred)

For most cases, use ADK. Use Custom for the root orchestrator. Use
Agno for multi-agent pipelines.

### Step 2 — Add the agent name to the routing keywords

Edit `agents/routing_keywords.py` and add a new entry:

```python
"my_new_agent": [
    "my domain keyword 1", "my domain keyword 2", "my domain keyword 3",
],
```

The routing keywords tell the root_agent when to dispatch to your
new agent. Add at least 3 keywords.

### Step 3 — Add the AgentFleetWiring entry

Edit `agents/agent_registry.py` and add a new entry:

```python
"my_new_agent": AgentFleetWiring(
    agent_name="my_new_agent",
    module_slug="my_new",
    module_path="cianfhoghlaim.agents.adk.my_new_agent",
    framework=AgentFramework.ADK,
    display_name="My New Agent",
    baml_prefix="MyNew",
    langfuse_trace_name="agent.my_new.search",
    cognee_dataset="oideachais_my_new",
    letta_agent_id="cianfhoghlaim-my-new-agent",
    litellm_routing_key="my_new",
),
```

The 8 fields are required. The `agent_name` MUST match the
routing keyword key.

### Step 4 — Create the agent module

Create `agents/adk/my_new_agent.py` (or `agents/agno/` for Agno
agents):

```python
"""My New Agent — the canonical implementation."""
from __future__ import annotations

from cianfhoghlaim.agents.wiring import (
    AgentFleetWiring, get_wiring, wire_agent,
)

# Build the LlmAgent (ADK) or the team (Agno)
my_new_agent = LlmAgent(
    name="my_new_agent",
    description="...",
    instruction="...",
    # ...
)

# Attach the wiring (graceful — never raises on missing dep)
wire = wire_agent(get_wiring("my_new_agent"))
my_new_agent.wire = wire
```

The wire-up is a 1-liner. The `wire` field reports which
dependencies were successfully wired.

### Step 5 — Wire the observability + memory (optional)

If your agent needs custom observability hooks (e.g. a custom
RAGAS dataset), edit `agents/observability_hooks.py` and add the
hook.

If your agent needs a custom memory backend (e.g. a dedicated
Cognee dataset), edit `agents/memory_layer.py` and add the backend.

For most agents, the default wiring is sufficient.

### Step 6 — Add a shared async dispatcher (optional)

If your agent has a user-facing workflow handler, add it to
`agents/_workflow_handlers.py`. The 4 dispatchers are:

- `dispatch_study_plan` — per-subject study plan
- `dispatch_deep_research` — long-form research
- `dispatch_literature_review` — literature review
- `dispatch_summary` — content summary

If your agent needs a new dispatcher, add it here.

### Step 7 — Add the agent to the CelticAgentOpsComponent

Edit `orchestration/components/layer5_agent_ops.py` and add the
agent to the `CelticAgentOpsComponent._append_routing_keywords`
method. The component auto-mounts the agent as a Dagster asset.

### Step 8 — Run the smoke tests

Run the new test files to verify the wiring:

```bash
mise run agents:smoke
mise run agents:audit
```

Expected output:

- `test_get_default_memory_layer_returns_implementation`: PASS
- `test_add_episode_round_trips`: PASS
- `test_verify_5_layer_contract`: PASS
- `test_register_agent`: PASS

If any test fails, the smoke test reports the failing scenario
with a clear error message.

## Common pitfalls

### Pitfall 1 — Direct imports from observability/memory clients

**Bad**:
```python
from langfuse import Langfuse  # NEVER import directly
client = Langfuse()
```

**Good**:
```python
from cianfhoghlaim.agents.wiring import wire_agent, get_wiring
wire = wire_agent(get_wiring("my_new_agent"))  # uses canonical hooks
```

The `agents/test_agent_wiring_audit.py` direct-import audit
catches this.

### Pitfall 2 — Raising on missing dependency

**Bad**:
```python
try:
    import langfuse
except ImportError:
    raise  # NEVER raise on missing dep
```

**Good**:
```python
try:
    import langfuse
    langfuse_wired = True
except ImportError:
    langfuse_wired = False
```

The `wire_agent()` function handles this for you.

### Pitfall 3 — Hard-coded framework

**Bad**:
```python
from google.adk.agents import LlmAgent  # only ADK
```

**Good**:
```python
framework = AGENT_REGISTRY["my_new_agent"].framework
if framework == AgentFramework.ADK:
    from google.adk.agents import LlmAgent
elif framework == AgentFramework.AGNO:
    from agno import Agent
```

The `AgentFleetWiring.framework` field tells you which framework
to use.

### Pitfall 4 — Module slug vs agent name mismatch

The `module_slug` is the file-name slug (e.g. `my_new`). The
`agent_name` is the canonical name (e.g. `my_new_agent`). The
canonical `module_path` is `f"cianfhoghlaim.agents.adk.{module_slug}_agent"`.

## Verification checklist

After adding a new agent, verify ALL these:

- [ ] `python -c "from cianfhoghlaim.agents import AGENT_REGISTRY; assert 'my_new_agent' in AGENT_REGISTRY"` exits 0
- [ ] `python -c "from cianfhoghlaim.agents.adk import my_new_agent; assert my_new_agent.wire is not None"` exits 0
- [ ] `mise run agents:smoke` passes all 12 scenarios
- [ ] `mise run agents:audit` reports 0 violations
- [ ] `openspec validate <change-id> --strict` passes (if you added an openspec change)
- [ ] `bun run validate-stacks` passes (if you added IaC)

## Cross-references

- [`agents/AGENTS.md`](../AGENTS.md) — the quadrant overview
- [`agents/STATUS.md`](../STATUS.md) — current state of each agent
- [`agents/REPRODUCER.md`](../REPRODUCER.md) — how to reproduce the agent fleet
- [`openspec/AGENTS.md`](../../openspec/AGENTS.md) — openspec workflow