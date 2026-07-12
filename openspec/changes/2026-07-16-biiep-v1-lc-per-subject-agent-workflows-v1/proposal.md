# Per-subject agent workflows for the 6 BIEP v1 LC subjects

## Why

The BIEP v1 flagship (`2026-07-06-british-isles-education-pipeline-v1`,
now archived) shipped the 6-subject LC data pipeline (Mathematics +
Chemistry + Geography + Gaeilge + English + Computer Science) — NCCA
syllabi + SEC past papers + NCCA marking schemes through BAML
extraction + Dagster assets + CocoIndex v1 embeddings + marimo
notebooks + MotherDuck Dives.

The 8 NCCA subject ADK agents were already wired in T4 (the
`2026-07-10-wire-8-subject-agents-cognify-langfuse-v1` change, Feat C)
— they have the canonical
`oideachais_lc_<subject>` Cognee dataset, the
`agent.<module_slug>.<verb>` Langfuse trace name, the BAML
`Generate<Subject>FormativeItem` function lookup, and the `<slug>_agent_wire`
Pydantic-bypass handle.

What's missing is the **user-facing workflow surface**. The student
asks "give me a 12-week study plan for HL Maths", or "discuss the 2024
Paper 2", or "explain the marking scheme for LO 2.4" — and the agents
need to *do* something with the existing tools. This change ships the
3 per-subject workflow handlers that bind the existing tool callables
into reusable async coroutines:

| # | Workflow handler | What it does | Maps to |
|:--|:--|:--|:--|
| 1 | `make_study_plan_handler(ctx)` | Per-subject lectionary + per-student progress | The student's "give me a 12-week plan" query |
| 2 | `discuss_exam_paper_handler(paper_id)` | Past-paper items + matching marking schemes + practice items | The student's "discuss 2024 Paper 2" query |
| 3 | `explain_marking_scheme_handler(lo_code)` | NCCA scheme + related items + exemplar + sample score | The student's "explain the marking for LO 2.4" query |

The 3 handlers are parameterised by the existing
`SubjectAgentWiring` (the storage-memory-facade work in `4d2fe8a2`)
+ the 5 per-subject tool callables (`*_syllabus_lookup_tool` +
`*_past_paper_lookup_tool` + `*_marking_scheme_lookup_tool` +
`*_formative_item_generate_tool` + `*_response_score_tool`). They live
in a small shared module
`agents/tuatha/_workflow_handlers.py` to avoid
duplicating the 3 dispatcher functions across the 6 per-subject
files (which would have been ~720 LOC of near-identical code).

## What changes

| File | Status | Lines |
|:--|:--|--:|
| `openspec/changes/2026-07-16-biiep-v1-lc-per-subject-agent-workflows-v1/proposal.md` | NEW | this file |
| `openspec/changes/2026-07-16-biiep-v1-lc-per-subject-agent-workflows-v1/tasks.md` | NEW | step-by-step recap |
| `openspec/changes/2026-07-16-biiep-v1-lc-per-subject-agent-workflows-v1/specs/meaisinfhoghlaim-agent-frameworks/spec.md` | NEW (1 ADDED Requirement) | the per-subject workflow handlers contract |
| `agents/tuatha/_workflow_handlers.py` | NEW | the 3 shared async dispatcher functions + the dataclass attacher |
| `agents/tuatha/wiring.py` | MODIFIED | +3 Callable fields on `WireSubjectAgent` |
| `agents/tuatha/math_agent.py` | MODIFIED | +3 math handlers + dataclass attachment |
| `agents/tuatha/chem_agent.py` | MODIFIED | +3 chem handlers + dataclass attachment |
| `agents/tuatha/geog_agent.py` | MODIFIED | +3 geog handlers + dataclass attachment |
| `agents/tuatha/gael_agent.py` | MODIFIED | +3 gaeilge handlers + dataclass attachment |
| `agents/tuatha/engl_agent.py` | MODIFIED | +3 english handlers + dataclass attachment |
| `agents/tuatha/comp_agent.py` | MODIFIED | +3 computer-science handlers + dataclass attachment |

18 handlers shipped (3 per subject × 6 in-scope subjects). 2 out-of-
scope subjects (Applied Mathematics + History) are deliberately
excluded per the user's locked plan.

## How — the 5-step ship sequence

### Step 1 — Audit the existing 8 NCCA subject agents

The 8 in-scope NCCA subject ADK agents live at
`agents/tuatha/`:

| Subject | Module | Lines |
|:--|:--|--:|
| Mathematics | `math_agent.py` | 269 → ~330 after this change |
| Chemistry | `chem_agent.py` | 165 → ~225 |
| Geography | `geog_agent.py` | 129 → ~189 |
| Gaeilge | `gael_agent.py` | 198 → ~258 |
| English | `engl_agent.py` | 129 → ~189 |
| Computer Science | `comp_agent.py` | 130 → ~190 |
| *Applied Mathematics* | `appm_agent.py` | 188 (out of scope) |
| *History* | `hist_agent.py` | 134 (out of scope) |

The existing wiring module is `wiring.py` (598 → ~640 lines after
the +3 Callable fields on `WireSubjectAgent`).

### Step 2 — Ship the per-subject workflow handlers

3 per-subject handler factory functions live in the new shared
module `_workflow_handlers.py`. Each handler takes the per-subject
`SubjectAgentWiring` + the 5 per-subject tool callables and returns
an async callable. The 6 `*_agent.py` files then attach the 3
returned handlers to their `WireSubjectAgent` via
`dataclasses.replace` at module-load time:

```python
math_agent_workflow_handlers = build_subject_workflow_handlers(
    wiring=_MATH_WIRING,
    syllabus_lookup_fn=math_syllabus_lookup_tool,
    past_paper_lookup_fn=math_past_paper_lookup_tool,
    marking_scheme_lookup_fn=math_marking_scheme_lookup_tool,
    formative_item_fn=math_formative_item_generate_tool,
    response_score_fn=math_response_score_tool,
)

math_agent_wire = attach_subject_workflow_handlers(
    wire_subject_agent(_MATH_WIRING),
    math_agent_workflow_handlers,
)
```

The 18 handlers consume the BAML
`Generate<Subject>FormativeItem` function (resolved at module load
by the existing `resolve_baml_function(...)` helper) via the
existing `*_formative_item_generate_tool` wrapper — which under-
the-hood calls the BAML function with the canonical
`lo_code + difficulty + level + topic` parameter set.

### Step 3 — Wire the per-subject workflows via `WireSubjectAgent`

The existing `WireSubjectAgent` dataclass in `wiring.py` gets 3 new
`Callable | None` fields with default `None` (back-compat with the
T4 lazy-import smoke tests):

```python
@dataclass
class WireSubjectAgent:
    subject: SubjectAgentWiring
    langfuse_wired: bool = False
    cognee_wired: bool = False
    memory_backend_kind: str | None = None
    baml_prefix: str | None = None

    # --- BIEP v1 per-subject workflow handlers ---
    study_plan_handler: Callable[..., Awaitable[dict]] | None = None
    exam_paper_handler: Callable[..., Awaitable[dict]] | None = None
    marking_scheme_handler: Callable[..., Awaitable[dict]] | None = None
```

The dataclass is **not** frozen (no `@dataclass(frozen=True)`), so
`dataclasses.replace(...)` returns a new `WireSubjectAgent` with the
3 handlers attached while leaving the original untouched.

### Step 4 — Verify

The 4 verification gates:

1. All 6 per-subject agent modules + the helper module + the wiring
   module AST-parse (8 files total).
2. All 6 per-subject `WireSubjectAgent` instances have non-`None`
   `study_plan_handler` + `exam_paper_handler` +
   `marking_scheme_handler` after import.
3. The 6 LC-extraction BAML files (`qpack_{mathematics,chemistry,
   geography,gaeilge,english,computer_science}.baml`) have the
   expected `Generate<Prefix>FormativeItem` function (5-6 functions
   each).
4. A functional smoke test that invokes
   `math_agent.make_study_plan_handler(...)` returns a well-formed
   study-plan dict (3 weekly entries with `lo_code` + difficulty +
   `formative_item`).

### Step 5 — OpenSpec change artefacts

1. `proposal.md` (this file)
2. `tasks.md` — the 5-step ship sequence
3. `specs/meaisinfhoghlaim-agent-frameworks/spec.md` — 1 ADDED
   Requirement declaring the per-subject workflow handlers contract

## Out of scope (already owned by other agents / openspec changes)

1. **The 8 NCCA subject agents themselves** — owned by the Feat C
   change (`2026-07-10-wire-8-subject-agents-cognify-langfuse-v1`)
   + T4's lazy-import work. This change EXTENDS `WireSubjectAgent`
   but does not modify the agent construction logic, the Tool
   surface, the BAML prefix resolution, or the storage/memory
   facade.
2. **The 6 LC-extraction BAML files** — owned by the British-Isles
   Education Pipeline (`2026-07-06-british-isles-education-pipeline-v1`)
   flagship. Not touched.
3. **The 2 out-of-scope subjects (Applied Mathematics + History)** —
   out of scope per the user's locked plan (the BIEP flagship is
   the 6-subject pipeline, not the 8-subject NCCA surface).
4. **The marimo notebook surface** — the per-subject BIEP notebooks
   at `notebooks/` are owned by
   `oideachais-marimo-dashboards`. They consume the 3 workflow
   handlers via the new fields on `WireSubjectAgent` once they
   load the agent module — no notebook edits in this change.
5. **CopilotKit + AG-UI wiring of the 3 handlers to the front-end** —
   downstream change; the handler signatures are JSON-serialisable
   `dict` returns + `dict[str, Any]` ctx inputs so a future agent
   binds them to CopilotKit `useRenderTool` slots.
6. **The 42 `lc5/lc6` Dagster assets + the 24 BIEP CocoIndex v1 flows** —
   owned by the flagship change.

## Acceptance gates

- [x] 6 per-subject NCCA subject agents (math, chem, geog, gael,
      engl, comp) each have 3 new workflow handlers attached
      (18 handlers total).
- [x] `WireSubjectAgent` extended with 3 new `Callable | None`
      fields (`study_plan_handler`, `exam_paper_handler`,
      `marking_scheme_handler`); the dataclass is still mutable
      (back-compat with T4).
- [x] All 6 per-subject agent modules AST-parse.
- [x] `wiring.py` AST-parses with the 3 new fields.
- [x] `_workflow_handlers.py` AST-parses + imports cleanly.
- [x] The 6 per-subject BAML files have the expected
      `Generate<Subject>FormativeItem` function (5-6 functions
      each).
- [x] Functional smoke test: `math_agent.make_study_plan_handler`
      returns a 3-week lectionary with the expected schema.
- [x] `openspec validate 2026-07-16-biiep-v1-lc-per-subject-agent-workflows-v1 --strict`
      passes.
- [x] Committed + pushed to `origin/pick-4-biep-v1` (NOT `main`).

## Dependencies

`Blocked by (soft): 2026-07-10-wire-8-subject-agents-cognify-langfuse-v1`
— the Feat C change shipped the per-subject wiring + the
`WireSubjectAgent` dataclass + the storage/memory facade. This
change EXTENDS that dataclass with 3 new fields. The blocker does
NOT need to archive first (the 3 new fields are `Callable | None`
with default `None`, so they back-compat with the Feat C smoke
tests that don't read these fields).

`Blocked by (soft): 4d2fe8a2` (storage-memory-facade commit) —
the per-subject `SubjectAgentWiring` is consumed by the new
`_workflow_handlers.build_subject_workflow_handlers(...)`. Back-
compat with the 6 `*_agent.py` modules that already import
`get_wiring("<ncca_subject>")`.

`Related but not blocking: 2026-07-13-openspec-drift-cleanup-v1`
— that change shipped the `meaisinfhoghlaim-agent-frameworks` spec
that this change now MODIFIES with 1 ADDED Requirement.

`Affected repos: cianfhoghlaim` (single-repo change; no
cross-repo-sync.md needed).
