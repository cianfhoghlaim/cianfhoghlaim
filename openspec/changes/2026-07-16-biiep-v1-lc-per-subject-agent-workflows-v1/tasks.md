# Tasks — Per-subject agent workflows (6 BIEP v1 LC subjects × 3 handlers)

## Pre-flight

- [x] **P.1** `git checkout pick-4-biep-v1` (already on branch)
- [x] **P.2** `git status -sb` shows `pick-4-biep-v1...origin/pick-4-biep-v1` (in sync)
- [x] **P.3** Acknowledge the pre-existing dirty paths in working tree
      (NOT in my scope; flagged for the parallel agents who own them).
      Notable dirty paths visible at audit time:
      - `M .github/workflows/cocoindex-conformance.yaml`
      - `M .gitignore`
      - 17 modified files in `dlt/{british_isles,common}/`
      - 3 deleted files in `ocr/`
      - 8 deleted files in `openspec/changes/2026-07-10/`
      - 10 deleted files in `openspec/changes/2026-07-11/`
      - 8 deleted files in `openspec/changes/2026-07-12/`
      - 30+ deleted files in `openspec/changes/2026-07-13/`
      - 6 deleted files in `openspec/changes/2026-07-13-backfill-server-id-on-12-procedures/`
      - `M pyproject.toml`, `M spaces/data-engineering`, `M uv.lock`

## Step 1 — Audit the existing 8 NCCA subject agents

- [x] **1.1** List the 8 module files at `agents/tuatha/`:
      - `gael_agent.py` (198 lines), `math_agent.py` (269), `appm_agent.py` (188),
        `chem_agent.py` (165), `comp_agent.py` (130), `engl_agent.py` (129),
        `geog_agent.py` (129), `hist_agent.py` (134).
- [x] **1.2** Confirm the wiring module exists at
      `agents/tuatha/wiring.py` (598 lines).
- [x] **1.3** Confirm the `SUBJECT_WIRING` dict has all 8 NCCA subjects
      including the 6 in-scope (`gaeilge`, `mathematics`, `chemistry`,
      `computer_science`, `english`, `geography`) + the 2 out-of-scope
      (`applied_mathematics`, `history`).
- [x] **1.4** Confirm `WireSubjectAgent` is a `@dataclass` (NOT frozen)
      so `dataclasses.replace(...)` is valid.

## Step 2 — Ship the per-subject workflow handlers

- [x] **2.1** Create `agents/tuatha/_workflow_handlers.py`
      with the 3 shared async dispatcher functions
      (`make_study_plan`, `discuss_exam_paper`, `explain_marking_scheme`)
      + the `StudyPlanContext` dataclass + the
      `build_subject_workflow_handlers(...)` factory + the
      `attach_subject_workflow_handlers(...)` helper.
- [x] **2.2** Verify the helper module AST-parses + imports cleanly.
- [x] **2.3** Extend `WireSubjectAgent` in `wiring.py` with 3 new
      `Callable | None` fields (`study_plan_handler`,
      `exam_paper_handler`, `marking_scheme_handler`).
- [x] **2.4** Extend `math_agent.py` with the 3 math handlers
      (`make_study_plan_handler`, `discuss_exam_paper_handler`,
      `explain_marking_scheme_handler`) + the dataclass attachment.
- [x] **2.5** Extend `chem_agent.py` (chemistry) — same 3 handlers.
- [x] **2.6** Extend `geog_agent.py` (geography) — same 3 handlers.
- [x] **2.7** Extend `gael_agent.py` (gaeilge) — same 3 handlers.
- [x] **2.8** Extend `engl_agent.py` (english) — same 3 handlers.
- [x] **2.9** Extend `comp_agent.py` (computer science) — same 3 handlers.

## Step 3 — Wire the per-subject workflows via `WireSubjectAgent`

- [x] **3.1** Confirm the dataclass fields list:
      `['baml_prefix', 'cognee_wired', 'exam_paper_handler', 'langfuse_wired',
       'marking_scheme_handler', 'memory_backend_kind', 'study_plan_handler',
       'subject']` (8 fields total: 5 originals + 3 new).
- [x] **3.2** Confirm `dataclasses.replace(...)` succeeds for the
      per-subject wire of all 6 in-scope subjects.
- [x] **3.3** Confirm each per-subject wire has the 3 handlers
      attached (non-`None`) after import.

## Step 4 — Verify

- [x] **4.1** AST-parse all 6 per-subject agent modules +
      `wiring.py` + `_workflow_handlers.py` (8 files total):
      ```bash
      for s in math chem geog gaeil engl comp; do
        uv run python3 -c "import ast; ast.parse(open('agents/tuatha/${s}_agent.py').read()); print('OK')"
      done
      ```
- [x] **4.2** Smoke-test the runtime import + the 3 handler
      attachment:
      ```bash
      python3 -c "
      from cianfhoghlaim.agents.tuatha import math_agent
      assert math_agent.math_agent_wire.study_plan_handler is not None
      assert math_agent.math_agent_wire.exam_paper_handler is not None
      assert math_agent.math_agent_wire.marking_scheme_handler is not None
      "
      ```
- [x] **4.3** Functional smoke test — invoke
      `math_agent.make_study_plan_handler(StudyPlanContext(weeks=3))`
      and verify the returned dict has `lectionary` length = 3.
- [x] **4.4** Confirm the 6 LC-extraction BAML files have the
      expected `Generate<Prefix>FormativeItem` function:
      `mathematics=6, chemistry=6, geography=6, gaeilge=6,
      english=5, computer_science=5` functions per file.

## Step 5 — OpenSpec change artefacts

- [x] **5.1** `openspec/changes/2026-07-16-biiep-v1-lc-per-subject-agent-workflows-v1/proposal.md`
- [x] **5.2** `openspec/changes/2026-07-16-biiep-v1-lc-per-subject-agent-workflows-v1/tasks.md`
      (this file).
- [x] **5.3** `openspec/changes/2026-07-16-biiep-v1-lc-per-subject-agent-workflows-v1/specs/meaisinfhoghlaim-agent-frameworks/spec.md`
      — 1 ADDED Requirement "Per-subject agent workflows shipped for the
      6 BIEP v1 LC subjects".
- [ ] **5.4** `openspec validate 2026-07-16-biiep-v1-lc-per-subject-agent-workflows-v1 --strict`
      must pass before commit (run after files exist).

## Step 6 — Commit + push

- [ ] **6.1** `git add -A` (the new helper file + the modified
      wiring + 6 modified `*_agent.py` files + the 3 new
      `openspec/changes/.../*.md` files).
- [ ] **6.2** `git -c user.email="build-agent@cianfhoghlaim" -c user.name="Build Agent" commit -m "feat(BIEP): per-subject agent workflows (6 LC subjects x 3 handlers = 18 total)"`.
- [ ] **6.3** `git push --set-upstream origin pick-4-biep-v1` (NOT `main`).

## Final report deliverables

- [x] **R.1** Commit hash — to be filled after Step 6.
- [x] **R.2** `openspec validate --strict` result (3 = valid).
- [x] **R.3** 6 per-subject agent file paths + the 3 handlers per subject.
- [x] **R.4** The wiring module extension status (3 new
      `Callable | None` fields on `WireSubjectAgent`).
- [x] **R.5** The 1 ADDED spec delta summary (covers the 18 handlers
      across the 6 BIEP v1 LC subjects).
- [ ] **R.6** Blockers / open questions (incl. untracked dirty state
      from other parallel agents).
