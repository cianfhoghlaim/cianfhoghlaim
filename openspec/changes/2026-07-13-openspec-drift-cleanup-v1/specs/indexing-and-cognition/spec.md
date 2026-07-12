# Spec Delta — indexing-and-cognition

This delta modifies existing requirements in the `indexing-and-cognition` capability (renamed `sruth.oideachais.cocoindex_flows.X` → `oideachais.cocoindex_flows.X` + renamed `sruth.meaisinfhoghlaim.agents` → `meaisinfhoghlaim.agents`) and adds one new requirement to codify the v4 namespace convention.

## ADDED Requirements

### Requirement: Openspec spec text uses v4 namespace convention (no `sruth.X` drift)

The `indexing-and-cognition` capability spec SHALL use the v4 namespace convention throughout. Concretely:

1. **CocoIndex CLI invocations** in scenarios SHALL use the v4 form: `uv run cocoindex update oideachais.cocoindex_flows.<flow>:<symbol>` (NOT `uv run cocoindex update sruth.oideachais.cocoindex_flows.<flow>:<symbol>`). The `sruth.oideachais.*` namespace no longer exists post-v4.
2. **Agent inventory imports** SHALL use the v4 form: `import meaisinfhoghlaim.agents` (NOT `import sruth.meaisinfhoghlaim.agents`). The 13 `.py` modules (`root_agent.py`, `curriculum_agent.py`, etc.) SHALL be discoverable via `meaisinfhoghlaim.agents.<module_name>`.

#### Scenario: A spec contributor edits the indexing-and-cognition spec

- **GIVEN** a contributor wants to add a new scenario to the indexing-and-cognition spec at `openspec/specs/indexing-and-cognition/spec.md`
- **WHEN** the contributor writes a CocoIndex CLI invocation
- **THEN** the invocation SHALL use the v4 form `uv run cocoindex update oideachais.cocoindex_flows.<flow>:<symbol>`
- **AND** if the contributor writes an agent inventory import, it SHALL use the v4 form `meaisinfhoghlaim.agents` (NOT `sruth.meaisinfhoghlaim.agents`)

#### Scenario: The cocoindex CLI invocation uses the v4 path

- **GIVEN** the v4 CocoIndex flow at `cocoindex/codebase_indexing.py` exposing `CodebaseIndex`
- **WHEN** the `bun run ccc:index` task runs
- **THEN** it SHALL invoke `uv run cocoindex update oideachais.cocoindex_flows.codebase_indexing:CodebaseIndex`
- **AND** it SHALL write the `codebase_chunks` LanceDB table to the `codebase` asset group
- **AND** the legacy `sruth.oideachais.cocoindex_flows.codebase_indexing:CodebaseIndex` invocation SHALL fail with `ModuleNotFoundError`

#### Scenario: The agent inventory is importable from the v4 path

- **GIVEN** the 13 `.py` modules under `agents/*.py` (root_agent + 12 specialists)
- **WHEN** a consumer does `import meaisinfhoghlaim.agents`
- **THEN** the import succeeds
- **AND** the `MODEL_LAYER_AGENTS` tuple lists exactly the 13 module basenames: `root_agent`, `curriculum_agent`, `translation_agent`, `corpus_agent`, `research_agent`, `education_research_agent`, `bunchloch_research_agent`, `geospatial_agent`, `statistics_agent`, `curriculum_comparison_agent`, `agui_curriculum_agent`, `mcp_curriculum_agent`, `voice_agent`

#### Scenario: The openspec drift cleanup baseline is preserved

- **GIVEN** the `2026-07-13-openspec-drift-cleanup-v1` change has landed
- **WHEN** `grep -rE "sruth\.oideachais\.cocoindex_flows|sruth\.meaisinfhoghlaim\.agents" openspec/specs/indexing-and-cognition/spec.md` runs
- **THEN** the count of `sruth.*` refs in canonical-positive contexts is 0
- **AND** `openspec validate indexing-and-cognition --strict` returns valid (the spec was already valid before this drift cleanup)