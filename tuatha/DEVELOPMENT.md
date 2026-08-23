# DEVELOPMENT — `tuatha` — How to Add a New Agent

> **The British Isles Formative Assessment MMO.** A focused
> how-to-add-an-agent doc for the 4 agent types in the new
> `tuatha/` sub-project.

---

## The 4 agent types

The new `tuatha/` project has 4 agent types:

1. **NCCA subject agents** (8 of them, in `tuatha/subjects/`)
2. **Educational agents** (3 of them, in `tuatha/agents/educational/`)
3. **BIEP hackathon features** (4 of them, in `tuatha/agents/hackathon/`)
4. **Media_intel pipeline** (1 of it, in `tuatha/agents/media_intel/`)

Each agent has a slightly different architecture. The pattern
for each is below.

---

## Pattern 1 — Add a new NCCA subject agent

### When to use

When you want to add a new subject to the 8 NCCA Leaving
Certificate subjects (e.g., a 9th subject, or a new sub-specialty).

### Steps

1. **Create the BAML contract** at
   `tuatha/baml/qpack_<subject>.baml` (the per-subject BAML
   client). Pattern: copy from
   `tuatha/baml/qpack_mathematics.baml` and adapt the
   `Generate<Subject>FormativeItem`,
   `Generate<Subject>QuestPack`,
   `Score<Subject>FormativeResponse` functions.

2. **Create the 5 per-subject tools** at
   `tuatha/tools/<subject>_<tool>.py` (8 subjects × 5 tools = 40
   files). Pattern: copy from
   `tuatha/tools/mathematics_syllabus_lookup.py` and adapt the
   LanceDB query, the BAML function call, the return type.

3. **Create the subject agent** at
   `tuatha/subjects/<subject>.py`. Pattern: copy from
   `tuatha/subjects/mathematics.py` and adapt the 5 tool imports
   + the agent name + the system instruction.

4. **Register the subject** in
   `tuatha/subjects/__init__.py` (the re-export surface) +
   `tuatha/__init__.py` (the canonical re-export).

5. **Add the DLT source** at
   `tuatha/dlt/<category>/<subject>.py` (5 categories: syllabus /
   past_paper / marking_scheme / formative_item /
   response_score).

6. **Add the Dagster asset** in
   `tuatha/dagster/per_subject.py`.

7. **Add the CocoIndex App** in
   `tuatha/cocoindex/per_subject.py`.

8. **Add the marimo notebook** in
   `tuatha/notebooks/per_subject.py`.

9. **Add the test** in
   `tuatha/tests/test_subject_router_smoke.py` (the existing
   canonical 20-smoke-test pattern).

10. **Update the openspec spec** at
    `openspec/specs/tuatha-british-isles-mmo/spec.md` to add the
    new subject.

11. **Run the 6 quality gates** + commit + push.

### Example: Adding a 9th subject "Physics"

```bash
# 1. Create the BAML contract
cp tuatha/baml/qpack_mathematics.baml tuatha/baml/qpack_physics.baml
# (edit the 3 function bodies to reference the Physics syllabus)

# 2. Create the 5 tools
for tool in syllabus_lookup past_paper_lookup marking_scheme_lookup formative_item_generate response_score; do
  cp tuatha/tools/mathematics_${tool}.py tuatha/tools/physics_${tool}.py
  # (edit the LanceDB query + the BAML function call)
done

# 3. Create the subject agent
cp tuatha/subjects/mathematics.py tuatha/subjects/physics.py
# (edit the 5 tool imports + the system instruction)

# 4-9. Register + add the DLT/Dagster/CocoIndex/marimo/test
# (follow the 8-step recipe above)

# 10. Update the openspec spec
# (add a new ADDED Requirement to the per-subject list)

# 11. Run the 6 quality gates
openspec validate --all --strict
mise run lint:registry
ruff check
```

---

## Pattern 2 — Add a new educational agent

### When to use

When you want to add a 4th educational agent (beyond the 3
existing: academic_history_agent + celtic_grammar_agent +
celtic_morphology_agent).

### Steps

1. **Create the BAML contract** at
   `tuatha/baml/<educational_agent>.baml` (per the academic
   history / celtic grammar / celtic morphology pattern).

2. **Create the agent** at
   `tuatha/agents/educational/<educational_agent>.py`.

3. **Register the agent** in
   `tuatha/agents/educational/__init__.py` +
   `tuatha/agents/__init__.py` +
   `tuatha/__init__.py`.

4. **Add the DLT source** at
   `tuatha/dlt/educational/<agent>.py`.

5. **Add the Dagster asset** in
   `tuatha/dagster/educational.py`.

6. **Add the CocoIndex App** in
   `tuatha/cocoindex/educational.py`.

7. **Add the marimo notebook** in
   `tuatha/notebooks/educational.py`.

8. **Add the test** in
   `tuatha/tests/test_<educational_agent>.py`.

9. **Update the openspec spec** at
   `openspec/specs/tuatha-british-isles-mmo/spec.md`.

10. **Run the 6 quality gates** + commit + push.

---

## Pattern 3 — Add a new BIEP hackathon feature

### When to use

When you want to add a 5th BIEP hackathon feature (beyond the 4
existing: marking_grader + adaptive_tutor +
equivalency_generator + curriculum_change_sensor).

### Steps

1. **Create the BAML contract** at
   `tuatha/baml/<feature>.baml` (per the existing
   marking_grader.baml + adaptive_tutor.baml +
   equivalency_table.baml pattern).

2. **Create the feature** at
   `tuatha/agents/hackathon/<feature>.py`.

3. **Register the feature** in
   `tuatha/agents/hackathon/__init__.py` +
   `tuatha/agents/__init__.py` +
   `tuatha/__init__.py`.

4. **Add the DLT source** at
   `tuatha/dlt/hackathon/<feature>.py`.

5. **Add the Dagster asset** in
   `tuatha/dagster/hackathon.py`.

6. **Add the CocoIndex App** in
   `tuatha/cocoindex/hackathon.py`.

7. **Add the marimo notebook** in
   `tuatha/notebooks/hackathon.py`.

8. **Add the test** in
   `tuatha/tests/test_<feature>.py`.

9. **Update the openspec spec** at
   `openspec/specs/tuatha-british-isles-mmo/spec.md`.

10. **Run the 6 quality gates** + commit + push.

---

## Pattern 4 — Modify the media_intel pipeline

### When to use

When you want to add a new per-medium extractor function to the
10-tool `media_descriptor_agent` (beyond the 5 existing
extractors: comic / prose / animation / gameplay /
official_document).

### Steps

1. **Create the new per-medium BAML contract** at
   `tuatha/baml/media_descriptor.baml` (add a new function
   alongside the existing 5).

2. **Update the BAML registry** at
   `tuatha/baml/clients.baml` (add the new client if needed).

3. **Add the new BAML extractor function wrapper** at
   `tuatha/agents/media_intel/media_descriptor_agent.py` (add a
   new async function alongside the existing 5).

4. **Register the new tool** in
   `tuatha/agents/media_intel/__init__.py` (add to the imports +
   `__all__`).

5. **Add the new FunctionTool** to the
   `media_descriptor_agent` tools list (in the
   `LlmAgent(tools=[...])` constructor).

6. **Update the `media_descriptor_agent`'s system instruction** to
   document the new tool.

7. **Add the test** in
   `tuatha/tests/test_media_intel_agent.py` (test the new
   extractor's 7-axis MediaDescriptor emission).

8. **Update the openspec spec** at
   `openspec/specs/tuatha-british-isles-mmo/spec.md` to document
   the new tool.

9. **Run the 6 quality gates** + commit + push.

---

## Cross-cutting invariants (apply to every pattern)

- **The BAML contract is the single source of truth** for
  every extractor (per `centralized-schema-registry`)
- **Every model string routes through
  `MODEL_REGISTRY.resolve(family, role)`** (no hardcoded model
  strings)
- **Every BAML function emits to Pydantic + Zod + Convex +
  DuckLake DDL** per the codegen contract
- **Per-source `rights_holder` + `licence` are declared
  correctly** (CC-BY-SA-4.0 for Wikipedia, OGL-3.0 for UK gov, PSI
  for Éire gov, Crown copyright for Acts, fair-use-description
  for the NCCA PDFs)
- **Concurrent-write safety**: every file edit uses the
  `git status/diff` → edit → `git status/diff` → `git add <path>`
  protocol
- **No `git add -A`** (concurrent agents may have M files; never
  scoop them)
- **No commit + push unless explicitly asked**

---

## The 6 quality gates (run every time)

```bash
# G1: openspec validate --strict (this project's change)
openspec validate $(grep -oP "2026-08-25-tuatha-british-isles-mmo-consolidation-v1" openspec/changes/*/proposal.md 2>/dev/null | head -1) --strict

# G2: openspec validate --all --strict
openspec validate --all --strict

# G3: mise run lint:registry (0 hardcoded model strings)
mise run lint:registry

# G4: ruff check
ruff check

# G5: mypy
uv run mypy tuatha/

# G6: Python import (no circular import)
uv run python -c "
from tuatha import (
    math_agent, appm_agent, chem_agent, comp_agent,
    engl_agent, gael_agent, geog_agent, hist_agent,
    academic_history_agent, celtic_grammar_agent, celtic_morphology_agent,
    marking_grader_agent, adaptive_tutor_agent, equivalency_generator_agent, curriculum_change_sensor_agent,
    media_descriptor_agent,
    TuathaOrchestrator, CianfhoghlaimOperator,
)
print('G6 PASS')
"
```

---

## The `tuatha` package layout reminder

```
tuatha/                              # the new independent repo
├── README.md
├── AGENTS.md                          # the developer quick-reference (you are here)
├── DEVELOPMENT.md                     # this file
├── pyproject.toml
├── mise.toml
├── LICENSE
├── docker-compose.yml
├── docs/                              # the 4 canonical docs
├── tests/                             # the 4 test files
├── openspec/                          # the project-local openspec
├── .devcontainer/
├── .github/workflows/ci.yml
├── .gitignore
├── .dockerignore
├── tuatha/                            # the canonical Python sub-namespace
│   ├── __init__.py                    # the re-export surface
│   ├── config.py                       # the LiteLLM + Langfuse + Cognee + Letta config
│   ├── routing.py                      # the SubjectAgentWiring factory
│   ├── orchestrator.py                 # the TuathaOrchestrator
│   ├── operator.py                     # the CianfhoghlaimOperator
│   ├── cross_subject.py                # the cross-subject specialist
│   ├── workflows.py                    # the 4 per-subject workflow handlers
│   ├── callbacks/                      # the canonical callbacks
│   ├── mcp_server/                     # the MCP server
│   ├── subjects/                       # the 8 NCCA subject agents
│   ├── tools/                          # the 40 per-subject tools
│   ├── agents/
│   │   ├── educational/                # the 3 educational agents
│   │   ├── media_intel/                # the 10-tool ADK agent
│   │   └── hackathon/                   # the 4 BIEP hackathon features
│   ├── baml/                           # the BAML surface
│   ├── dlt/                            # the DLT sources
│   ├── dagster/                        # the Dagster asset groups
│   ├── cocoindex/                      # the CocoIndex v1 Apps
│   ├── notebooks/                      # the marimo notebooks
│   ├── badges/                         # the credential system
│   └── ci/                             # the CI layer
└── tuatha/old/                         # the archive
    ├── prior_top_level_tuasha/         # (preserved for reference)
    ├── scattered_agents_tuasha/        # (preserved for reference)
    └── legacy_theming/                 # the hard-archived legacy theming
```

---

## The cross-repo surface

The `tuatha/` project lives at
`/Users/cianmacandeisigh/dev/kings_college_galway/tuatha/` —
a sub-dir of the parent `kings_college_galway/` (the cianfhoghlaim
+ leabharlann + bonneagar monorepo). The new project is designed
to become its own independent GitHub repo at
`github.com/cianmacandeisigh/tuatha.git` (per the 2026-08-25
consolidation change).

The cross-repo references are:
- `agents/agent_registry.py:AGENT_REGISTRY` — the
  `media_descriptor_agent` entry's `module_path` is
  `tuatha.agents.media_intel.media_descriptor_agent` (re-routed
  from the prior `agents.meaisinfhoghlaim.media_intel.*` location)
- The back-compat shim at
  `agents/meaisinfhoghlaim/media_intel/__init__.py` re-exports
  the canonical symbols from the new location
- The sibling repos `kings_college_galway/leabharlann/` +
  `kings_college_galway/bonneagar/` are unchanged

---

## License

MIT (permissive).
