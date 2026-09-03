## MODIFIED Requirements

### Requirement: 8 NCCA subject agent definitions wired to Layer 5

The system SHALL mount each of the 8 NCCA subject agents
(`gael_agent`, `math_agent`, `appm_agent`, `chem_agent`,
`comp_agent`, `engl_agent`, `geog_agent`, `hist_agent`) at
`cianfhoghlaim/orchestration/defs/5_agent_ops/adk/<slug>_agent/defs.yaml`
under the 5-layer KCG Components pattern.

Per the Feat C addendum (2026-07-10), each mount SHALL also
expose two additional top-level attribute blocks in addition to
the 5 Dagster assets: a `cognify` block configuring the per-
subject Cognee dataset (`oideachais_lc_<subject>`) and a
`langfuse_callbacks` block configuring the canonical trace name
(`agent.<module_slug>.<verb>`). Both blocks are populated by the
L5 Component at scaffold time — operator-managed defs.yaml files
MUST keep both blocks in sync with the canonical naming rule.

The `ROUTING_KEYWORDS` map at
`cianfhoghlaim/agents/routing_keywords.py` SHALL expose a seed
bucket for each of the 8 subjects with at least the NCCA canonical
name (`gaeilge`, `mathematics`, `applied_mathematics`,
`chemistry`, `computer_science`, `english`, `geography`,
`history`); the full bucket is appended by
`CelticAgentOpsComponent._append_routing_keywords()` at scaffold
time.

#### Scenario: math_agent mounts on L5 + routes by keyword + has cognify + langfuse blocks

- **GIVEN** `defs/5_agent_ops/adk/math_agent/defs.yaml`
- **WHEN** `dg list defs | grep math_agent` runs
- **THEN** the 5 math_agent assets are visible in the
  output
- **AND** `ROUTING_KEYWORDS["math_agent"]` contains
  `"mathematics"`
- **AND** `defs.yaml.attributes.cognify.dataset` equals
  `"oideachais_lc_mathematics"`
- **AND** `defs.yaml.attributes.langfuse_callbacks.trace_name`
  equals `"agent.math.explain"`

## ADDED Requirements

### Requirement: Letta memory wired at agent construction time

The system SHALL bind the ``LettaMemoryService`` (from
`cianfhoghlaim/storage/letta_memory.py`) at module-construction
time on every one of the 8 NCCA subject agents. The wire-up
SHALL be exposed as the module-level ``<slug>_agent_wire``
attribute holding a ``WireSubjectAgent`` instance with the
``memory_backend_kind`` field set to either
``"protocol"`` (when ``get_default_backend()`` was reachable) or
``None`` (when the protocol could not be imported).

The wire-up MUST NOT pull in `google.genai`, `litellm`, or
`baml` at module-import time (the underlying imports are lazy).

#### Scenario: math_agent_wire is populated at import time

- **GIVEN** `python3 -c "from cianfhoghlaim.agents.tuatha import math_agent"`
- **WHEN** the import resolves
- **THEN** `math_agent.math_agent_wire.baml_prefix == "Math"`
- **AND** `math_agent.math_agent_wire.subject.cognee_dataset == "oideachais_lc_mathematics"`
- **AND** no `ImportError` is raised during construction

### Requirement: Langfuse callbacks wired at agent construction time

The system SHALL bind the Langfuse tracer (from
`cianfhoghlaim/observability/langfuse_config.py`) at module-
construction time on every one of the 8 NCCA subject agents, via
the module-level ``<slug>_agent_open_trace`` function. The function
opens a trace with the canonical name
``agent.<module_slug>.<verb>`` (default verb = ``"explain"``).

When the ``langfuse`` package is not installed the function MUST
return a no-op context manager that yields ``None`` — it MUST NOT
raise.

#### Scenario: gael_agent_open_trace uses the canonical trace name

- **GIVEN** `from cianfhoghlaim.agents.tuatha import gael_agent`
- **WHEN** `gael_agent.gael_agent_open_trace(verb="explain")`
  is entered
- **THEN** the trace name (in normal Langfuse environments)
  equals `"agent.gael.explain"`
- **AND** when Langfuse is unavailable the context exits cleanly
  and yields `None`

### Requirement: Cognify emit step pushes to oideachais_lc_<subject>

The system SHALL push every LLM response of the 8 NCCA subject
agents into the canonical Cognee dataset
``oideachais_lc_<subject>``, where ``<subject>`` is the
canonical NCCA subject slug (not the file-name slug). The emit
hook is exposed as the module-level
``<slug>_agent_emit_to_cognee(response, query)`` async function
and returns the top-5 closest historical responses for the
given query.

When the ``cognee`` package is not installed the function MUST
return ``[]`` without raising.

The 5 subjects whose Cognee datasets differ from the
historical `oideachais_<subject>` naming convention are
now consistent with `agent-memory-systems`.

#### Scenario: chem_agent emits to oideachais_lc_chemistry

- **GIVEN** `chem_agent.chem_agent_open_trace` has been called for a query
- **WHEN** `chem_agent.chem_agent_emit_to_cognee(<response>, <query>)` runs
- **AND** the `cognee` package is installed
- **THEN** the response is added to the `oideachais_lc_chemistry` dataset
- **AND** the returned hits come from the same dataset with
  `top_k = 5`

#### Scenario: emit_to_cognee is graceful on missing cognee

- **GIVEN** the `cognee` package is not installed
- **WHEN** `chem_agent.chem_agent_emit_to_cognee("resp", "q")` runs
- **THEN** the function returns `[]`
- **AND** no exception is raised

### Requirement: StorageBackend Protocol enforced on subject agents

The system SHALL enforce the `MemoryBackend` Protocol contract on
the 8 NCCA subject agents: no subject agent module MAY import
`oideachais.storage.graphiti_client` or
`oideachais.storage.falkordb_client` directly. Every subject
agent MUST depend on the abstraction via
`from cianfhoghlaim.storage.memf import get_default_backend`.

#### Scenario: no direct graphiti_client / falkordb_client imports

- **GIVEN** any of the 8 `<slug>_agent.py` modules at
  `cianfhoghlaim/agents/tuatha/`
- **WHEN** `grep -n "graphiti_client\|falkordb_client" <agent>.py`
  runs
- **THEN** the output SHALL be empty (0 matches)
- **AND** the subject agents import
  `from cianfhoghlaim.storage.memf import get_default_backend` when
  they need a concrete backend
