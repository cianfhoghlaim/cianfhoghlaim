# `meaisinfhoghlaim-agent-frameworks` MODIFIED — per-subject agent workflows (BIEP v1)

## ADDED Requirements

### Requirement: Per-subject agent workflows shipped for the 6 BIEP v1 LC subjects

The system SHALL ship 3 user-facing per-subject workflow handlers
for each of the 6 BIEP v1 Leaving Certificate subjects
(**Mathematics, Chemistry, Geography, Gaeilge, English, Computer
Science**) — 18 handlers in total — wired through the existing
`WireSubjectAgent` dataclass in
`cianfhoghlaim/agents/tuatha/wiring.py`.

The 3 per-subject handlers are:

1. **`make_study_plan_handler(ctx: StudyPlanContext) -> dict`** —
   produces a per-subject lectionary (a per-week list of NCCA LO +
   per-LO `Generate<Subject>FormativeItem` BAML call) + a
   per-student progress summary that downstream marimo notebooks +
   RAGAS evaluations can read.
2. **`discuss_exam_paper_handler(exam_paper_id: str) -> dict`** —
   loads the past-paper items + matching `*_marking_scheme_lookup`
   entries by `lo_code` + emits a per-LO discussion crosswalk + a
   flat `analysis` summary.
3. **`explain_marking_scheme_handler(marking_scheme_id: str) ->
   dict`** — loads the NCCA marking-scheme text + the related past-
   paper items + generates an exemplar practice item via
   `*_formative_item_generate_tool` + optionally scores a sample
   attempt via `*_response_score_tool`.

The 3 handlers consume the existing per-subject tool callables
(`*_syllabus_lookup_tool`, `*_past_paper_lookup_tool`,
`*_marking_scheme_lookup_tool`, `*_formative_item_generate_tool`,
`*_response_score_tool`) that the existing 8 NCCA subject agents
already export (they were wired in T4 + Feat C).

The 3 handlers SHALL be exposed on the existing
`<slug>_agent_wire` (`WireSubjectAgent`) dataclass — via 3 new
`Callable | None` fields (`study_plan_handler`,
`exam_paper_handler`, `marking_scheme_handler`) added with default
`None`. The fields are filled at module-load time via
`dataclasses.replace(wire_subject_agent(_X_WIRING), ...)` calls in
each of the 6 per-subject agent modules.

The shared async dispatcher functions live in
`cianfhoghlaim/agents/tuatha/_workflow_handlers.py` so the 3
handler bodies are not duplicated across the 6 per-subject modules
(`build_subject_workflow_handlers(wiring, syllabus, past_paper,
marking_scheme, formative_item, response_score)` returns a
`SubjectWorkflowHandlers` triple; `attach_subject_workflow_handlers
(wire, handlers)` returns a new `WireSubjectAgent` with the 3
callables attached).

The 2 out-of-scope NCCA subjects (Applied Mathematics + History)
remain unwired for these handlers (they are deliberately excluded
per the user's locked plan — the BIEP flagship is the
6-subject LC pipeline, not the 8-subject NCCA surface). When a
future change wants to extend the per-subject workflow surface
to those subjects it SHALL add the analogous `make_*_handler` +
`discuss_*_handler` + `explain_*_handler` functions to the
respective `appm_agent.py` / `hist_agent.py` modules using the
same `_workflow_handlers` factory.

#### Scenario: `WireSubjectAgent` exposes the 3 new handler fields

- **GIVEN** the
      `cianfhoghlaim/agents/tuatha/wiring.py` module
- **WHEN** an agent runs
      `python3 -c "from cianfhoghlaim.agents.tuatha.wiring import WireSubjectAgent; print(sorted(WireSubjectAgent.__dataclass_fields__))"`
- **THEN** the printed field names SHALL contain exactly these 3 new
      ones (in any order):
      - `study_plan_handler`
      - `exam_paper_handler`
      - `marking_scheme_handler`
- **AND** the 3 new fields SHALL default to `None` (back-compat
      with the T4 smoke tests that construct `WireSubjectAgent`
      without handlers).

#### Scenario: All 6 in-scope per-subject agents attach the 3 handlers

- **GIVEN** any of the 6 in-scope subjects
      (`mathematics`, `chemistry`, `geography`, `gaeilge`,
      `english`, `computer_science`)
- **WHEN** an agent imports the corresponding
      `*_agent.py` module
- **THEN** the `<slug>_agent_wire` instance SHALL expose
      non-`None` `study_plan_handler` + `exam_paper_handler` +
      `marking_scheme_handler` callables.

#### Scenario: `make_study_plan_handler` returns a per-subject lectionary

- **GIVEN** `from cianfhoghlaim.agents.tuatha import math_agent`
- **WHEN** an agent invokes
      `await math_agent.make_study_plan_handler(StudyPlanContext(level="lc_hl", topic="differentiation", weeks=3))`
- **THEN** the returned dict SHALL contain:
      - `subject == "mathematics"`
      - `level == "lc_hl"`
      - `weeks == 3`
      - `lectionary` list of length 3, each entry with the keys
        `week`, `lo_code`, `topic`, `difficulty`,
        `formative_item`
      - `progress` dict with `agent == "agent.math.explain"` + the
        Langfuse trace-name convention.

#### Scenario: `discuss_exam_paper_handler` returns a per-subject discussion

- **GIVEN** `from cianfhoghlaim.agents.tuatha import chem_agent`
- **WHEN** an agent invokes
      `await chem_agent.discuss_exam_paper_handler("chemistry.paper2")`
- **THEN** the returned dict SHALL contain:
      - `subject == "chemistry"`
      - `exam_paper_id == "chemistry.paper2"`
      - `items` list (possibly empty if BAML client not
        generated in the dev env)
      - `marking_schemes` list (per matched `lo_code`)
      - `analysis.items_discussed` + `analysis.marking_schemes_crosswalked`
        numeric fields.
- **AND** the handler SHALL NOT raise when BAML is unavailable —
      it returns the dict with empty `items` + a graceful
      `analysis` summary.

#### Scenario: `explain_marking_scheme_handler` returns a per-subject explanation

- **GIVEN** `from cianfhoghlaim.agents.tuatha import gael_agent`
- **WHEN** an agent invokes
      `await gael_agent.explain_marking_scheme_handler("LC-GAEL-LO-3.1")`
- **THEN** the returned dict SHALL contain:
      - `subject == "gaeilge"`
      - `marking_scheme_id == "LC-GAEL-LO-3.1"`
      - `scheme` (the marking-scheme lookup result — may have
        an `error` key if LO not found in the local DB)
      - `rationale.explanation_en` (the canonical Irish-med
        rationale template)
      - `rationale.explanation_ga` (the secondary Irish-language
        rationale)
      - `exemplar_formative_item` (the BAML-generated practice
        item — may have an `error` key if BAML client not
        generated)
      - `related_past_paper_items` (truncated to 5).

#### Scenario: The 18 handlers consume `Generate<Subject>FormativeItem`

- **GIVEN** any of the 6 per-subject BAML files at
      `cianfhoghlaim/baml/education/subjects/qpack_<subject>.baml`
- **WHEN** an agent runs
      `grep -E "^function" cianfhoghlaim/baml/education/subjects/qpack_<subject>.baml`
- **THEN** the output SHALL include the
      `Generate<Subject>FormativeItem` function (used by the
      per-subject `*_formative_item_generate_tool` that each
      handler delegates to).
- **AND** the BAML file SHALL contain at least 5 `function`
      declarations total (the canonical 6: `QuestPack`,
      `Extract<Subject>LOStatement`, optional `Extract<Subject>GaStatement`,
      `FormativeItem`, `Score<Subject>FormativeResponse`,
      `Validate<Subject>QuestPack`).

## MODIFIED Requirements

*(no prior requirements are modified — this delta is a pure
ADDED Requirement that extends the existing "8 NCCA subject
agent definitions wired to Layer 5" contract with the user-facing
workflow surface; the `Langfuse callbacks wired at agent
construction time`, `Cognify emit step pushes to oideachais_lc_<subject>`,
`StorageBackend Protocol enforced on subject agents`, and
`MemoryBackend Protocol contract` requirements remain unchanged.)*

## Cross-references

- [`cianfhoghlaim/agents/tuatha/_workflow_handlers.py`](../../../cianfhoghlaim/agents/tuatha/_workflow_handlers.py) —
  the 3 shared async dispatchers + the dataclass attacher.
- [`cianfhoghlaim/agents/tuatha/wiring.py`](../../../cianfhoghlaim/agents/tuatha/wiring.py) —
  the `WireSubjectAgent` dataclass (now extended with the 3
  `Callable | None` handler fields).
- The 6 per-subject agent modules:
  [`math_agent.py`](../../../cianfhoghlaim/agents/tuatha/math_agent.py),
  [`chem_agent.py`](../../../cianfhoghlaim/agents/tuatha/chem_agent.py),
  [`geog_agent.py`](../../../cianfhoghlaim/agents/tuatha/geog_agent.py),
  [`gael_agent.py`](../../../cianfhoghlaim/agents/tuatha/gael_agent.py),
  [`engl_agent.py`](../../../cianfhoghlaim/agents/tuatha/engl_agent.py),
  [`comp_agent.py`](../../../cianfhoghlaim/agents/tuatha/comp_agent.py).
- The 6 LC-extraction BAML files at
  `cianfhoghlaim/baml/education/subjects/qpack_<subject>.baml`.
- The BIEP v1 flagship spec:
  [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md).
