# Change: upgrade-to-adk2-pillars-1-2-3-v1

## Why

The existing 24-agent fleet uses ADK 1.x patterns (`google-adk>=1.17.0`,
`LlmAgent + FunctionTool + keyword routing`). The `docs/google_examples/adk2-tutorial/`
+ `docs/google_examples/agent-valley-archive/` provide 3 Pillar ADK 2.x
patterns + a 5-floor memory ladder twin that map directly onto the
cianfhoghlaim agent fleet.

The `pyproject.toml` bump to `google-adk>=2.5.0,<3` is the hard migration:
the 24 existing agents continue to work (LlmAgent + FunctionTool are
backwards-compatible), but the 3 Pillar patterns become available:

- Pillar 1 (Workflow): 3 explicit graphs replace keyword-routed agent dispatch
- Pillar 2 (Collaborative): `sub_agents=[...]` + `mode="single_turn"` for the
  3 root orchestrators (SU + K-12 teacher + K-12 student)
- Pillar 3 (Dynamic): `@node(parallel_worker=True)` + recursive `ctx.run_node`
  for the 5 deep-research pipelines (aistear → primary → jc → sc → tertiary)

The agent-valley-archive's 4-floor memory ladder becomes cianfhoghlaim's
5-floor education ladder (visit → visitor → student → stage → valley)
mapped to the 5 BIEP v3 stages.

## What Changes

### Code — modified (~30 files)

- `pyproject.toml` — bump `google-adk>=1.17.0` → `google-adk>=2.5.0,<3`
- `agents/agent_registry.py` — register the 2 new roots + 3 workflows + 5 deep-research (10 new fleet entries: priority 15-24)
- `agents/routing_keywords.py` — add keyword buckets for the workflow patterns
- `agents/meaisinfhoghlaim/educational/students_union/root_agent.py` — add `mode="single_turn"` (Pillar 2)
- The 24 existing agents: unchanged at the source level (ADK 1.x LlmAgent + FunctionTool
  patterns remain backwards-compatible under ADK 2.x)

### Code — new (~50 files)

**Pillar-1 Workflow graphs (3 files)**:
- `agents/workflows/__init__.py`
- `agents/workflows/teacher_daily_workflow.py` (plan_today → lesson_planner → assessment_scorer → sen_pastoral)
- `agents/workflows/student_secondary_workflow.py` (load_subjects → homework_tracker → cba_planner → study_plan → exam_timetable)
- `agents/workflows/tertiary_personal_workflow.py` (load_profile → uoa_portal → students_union_root)

**Pillar-2 Root orchestrators (2 files)**:
- `agents/meaisinfhoghlaim/educational/teachers/_root.py` (teacher_root with 5 sub_agents)
- `agents/meaisinfhoghlaim/educational/students_jc/_root.py` (student_root with 5 sub_agents)

**Pillar-3 Dynamic deep-research (5 files)**:
- `agents/workflows/aistear_deep_research.py` (4 Aistear themes)
- `agents/workflows/primary_deep_research.py` (12 primary areas)
- `agents/workflows/jc_deep_research.py` (18 JC subjects)
- `agents/workflows/sc_deep_research.py` (40+ SC subjects)
- `agents/workflows/tertiary_deep_research.py` (4 UoG colleges + 18 schools)

**Pydantic I/O + Memory governance (5 files)**:
- `agents/meaisinfhoghlaim/_shared/__init__.py` (EducationRequest + SpecialistInput + DecomposerOutput + DeepResearchBriefing + the 5-floor ladder)
- `agents/meaisinfhoghlaim/_shared/schemas.py` (embedded in __init__)
- `agents/meaisinfhoghlaim/educational/_archive/__init__.py`
- `agents/meaisinfhoghlaim/educational/_archive/agent.py` (Vesper + the Workflow)
- `agents/meaisinfhoghlaim/educational/_archive/state.py` (the 5 keys + HOUSE)
- `agents/meaisinfhoghlaim/educational/_archive/memory.py` (burn() + list_floor() + archive_today())
- `agents/meaisinfhoghlaim/educational/_archive/topics.py`
- `agents/meaisinfhoghlaim/educational/_archive/_stages.py`

**Marimo walkthroughs (8 files)**:
- `notebooks/_shared/education/walkthroughs/adk2_01_graph_lesson_planner.py`
- `notebooks/_shared/education/walkthroughs/adk2_02_collaborative_teacher_root.py`
- `notebooks/_shared/education/walkthroughs/adk2_03_dynamic_aistear_research.py`
- `notebooks/_shared/education/walkthroughs/adk2_04_memory_ladder.py`
- `notebooks/_shared/education/walkthroughs/adk2_05_bq_warehouse.py`
- `notebooks/_shared/education/walkthroughs/adk2_06_schemas.py`
- `notebooks/_shared/education/walkthroughs/adk2_07_walk_script.py`
- `notebooks/_shared/education/walkthroughs/adk2_08_capstone_decision_tree.py`

**Preflight + Walk scripts (2 files)**:
- `scripts/preflight_education.py`
- `scripts/walk_education.py`

**New skill (1 file)**:
- `.agents/skills/adk2-pillars/SKILL.md`

**READMEs updated (4 files)**:
- `README.md` (root)
- `agents/meaisinfhoghlaim/AGENTS.md`
- `agents/README.md`
- `dlt_sources/AGENTS.md`

### New openspec specs (2 files)

- `openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/specs/adk2-pillars-orchestration/spec.md`
- `openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/cross-repo-sync.md`

## Out of scope (follow-up changes)

1. `openspec/changes/2026-09-24-adk2-bq-memory-bank-v1/` — Phase 2: switch from InMemoryMemoryService to VertexAiMemoryBankService
2. `openspec/changes/2026-09-25-adk2-cognee-cross-edges-v1/` — Phase 3: Cognee cross-stage edges (Teacher teaches Module etc.)
3. The `students_union` rename to `students_union_postprimary` (post-primary only) — out of scope, separate change

## Dependencies

`Blocked by (soft): 2026-09-23-consolidate-uog-tertiary-pipeline-v1/` (the tertiary tier baseline
that the ADK 2 tertiary_personal_workflow builds on).
`Blocked by (soft): 2026-09-23-k12-teacher-student-pipeline-v1/` (the K-12 tier baseline
that the ADK 2 teacher_root + student_root build on).
`Affected repos: cianfhoghlaim (single repo)`.

## Cross-repo sync

Single-repo change (everything in `cianfhoghlaim/`). No sister-repo coordination
required.

## Verification

1. `uv run python scripts/preflight_education.py` exits 0 (all 5 preflight rows pass)
2. `uv run python scripts/walk_education.py` exits 0 (all 5 chapters pass)
3. `openspec validate 2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1 --strict` exits 0
4. `python3 -c "import ast; [ast.parse(open(f).read()) for f in glob.glob('agents/workflows/*.py')]"` exits 0
5. The 24-agent fleet + 3 workflows + 5 deep-research pipelines are registered in `agents/agent_registry.py`
6. `grep -l "google.adk.agents.LlmAgent" agents/meaisinfhoghlaim/educational/` still returns the existing 10 specialist files (backwards-compatible)
7. `git commit + push` lands `ad404a20c...upgrade-to-adk2-pillars-1-2-3-v1: hard bump ADK 1 → 2.x + 3 Pillar refactor + agent-valley twin`
