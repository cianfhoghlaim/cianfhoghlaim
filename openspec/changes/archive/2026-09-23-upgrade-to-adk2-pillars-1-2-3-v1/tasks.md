# Tasks: 2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1

## 1. Stage 1A — pyproject bump + Pydantic I/O + memory governance (4 files)

- [ ] **A1** `pyproject.toml` — bump `google-adk>=1.17.0` → `google-adk>=2.5.0,<3`
- [ ] **A2** `agents/meaisinfhoghlaim/_shared/__init__.py` — NEW: EducationStage + EducationRole + EducationRequest + SpecialistInput + SpecialistResponse + DecomposerOutput + ResearchFinding + DeepResearchBriefing + STAGE_TO_FLOOR + VISIT/VISITOR/STUDENT/VALLEY + burn()
- [ ] **A3** `agents/meaisinfhoghlaim/_shared/__init__.py` — the Pydantic I/O schemas (Conditions, BundledRunData) + the SpecialistInput/Response schemas
- [ ] **A4** `agents/meaisinfhoghlaim/_shared/__init__.py` — the 5-floor ladder mapping (stage_to_floor dict)

## 2. Stage 1B — Pillar-2 root orchestrators (4 files)

- [ ] **B1** `agents/meaisinfhoghlaim/educational/teachers/_root.py` — NEW: teacher_root with 5 sub_agents + lazy-load
- [ ] **B2** `agents/meaisinfhoghlaim/educational/students_jc/_root.py` — NEW: student_root with 5 sub_agents + lazy-load
- [ ] **B3** `agents/meaisinfhoghlaim/educational/students_union/root_agent.py` — MODIFY: add `mode="single_turn"`
- [ ] **B4** `agents/agent_registry.py` — register the 2 new roots + the 3 Pillar-1 workflows + the 5 Pillar-3 deep-research (10 new fleet entries, priority 15-24)
- [ ] **B5** `agents/routing_keywords.py` — add 10 new keyword buckets for the workflow + collaborative patterns

## 3. Stage 1C — Pillar-1 Workflow graphs (3 files)

- [ ] **C1** `agents/workflows/__init__.py` — NEW: re-exports the 3 graphs + the 5 deep-research pipelines
- [ ] **C2** `agents/workflows/teacher_daily_workflow.py` — NEW: Workflow(edges=[(START, plan_today, lesson_planner, assessment_scorer, sen_pastoral)])
- [ ] **C3** `agents/workflows/student_secondary_workflow.py` — NEW: Workflow(edges=[(START, load_subjects, homework_tracker, cba_planner, study_plan, exam_timetable)])
- [ ] **C4** `agents/workflows/tertiary_personal_workflow.py` — NEW: Workflow(edges=[(START, load_profile, uoa_portal, students_union_root)])

## 4. Stage 1D — Pillar-3 Dynamic deep-research (5 files)

- [ ] **D1** `agents/workflows/aistear_deep_research.py` — NEW: decompose → parallel_worker research → synthesize (4 Aistear themes)
- [ ] **D2** `agents/workflows/primary_deep_research.py` — NEW: decompose → parallel_worker research → synthesize (12 primary areas)
- [ ] **D3** `agents/workflows/jc_deep_research.py` — NEW: decompose → parallel_worker research → synthesize (18 JC subjects)
- [ ] **D4** `agents/workflows/sc_deep_research.py` — NEW: decompose → parallel_worker research → synthesize (40+ SC subjects)
- [ ] **D5** `agents/workflows/tertiary_deep_research.py` — NEW: decompose → recursive @node research → synthesize (4 UoG colleges + 18 schools + MAX_DEPTH=2)

## 5. Stage 1E — Agent Valley education twin (8 files)

- [ ] **E1** `agents/meaisinfhoghlaim/educational/_archive/__init__.py` — re-exports + 5-floor ladder
- [ ] **E2** `agents/meaisinfhoghlaim/educational/_archive/agent.py` — Vesper the archivist + the classify_intent / recall / answer / archive_today / list_floor graph + the archive_workflow Workflow
- [ ] **E3** `agents/meaisinfhoghlaim/educational/_archive/state.py` — the 5 ladder keys (VISIT, VISITOR, STUDENT, VALLEY, VISIT_COUNT) + the HOUSE prompt
- [ ] **E4** `agents/meaisinfhoghlaim/educational/_archive/_stages.py` — the stage_to_floor mapping (separated to break the circular import)
- [ ] **E5** `agents/meaisinfhoghlaim/educational/_archive/memory.py` — burn() + list_floor() + archive_today() (Phase 1 InMemory, Phase 2 Vertex)
- [ ] **E6** `agents/meaisinfhoghlaim/educational/_archive/topics.py` — TOPICS tuple (what the archive is allowed to keep)
- [ ] **E7** `scripts/preflight_education.py` — NEW: 5-row preflight (google-adk version + 5 keys + 3 Pillar-1 workflows + 5 Pillar-3 deep-research + 3 root orchestrators)
- [ ] **E8** `scripts/walk_education.py` — NEW: the 5-chapter walk (slip → drawer → tower → season → valley)

## 6. Stage 1F — 8 marimo walkthrough notebooks (8 files)

- [ ] **F1** `notebooks/_shared/education/walkthroughs/adk2_01_graph_lesson_planner.py`
- [ ] **F2** `notebooks/_shared/education/walkthroughs/adk2_02_collaborative_teacher_root.py`
- [ ] **F3** `notebooks/_shared/education/walkthroughs/adk2_03_dynamic_aistear_research.py`
- [ ] **F4** `notebooks/_shared/education/walkthroughs/adk2_04_memory_ladder.py`
- [ ] **F5** `notebooks/_shared/education/walkthroughs/adk2_05_bq_warehouse.py`
- [ ] **F6** `notebooks/_shared/education/walkthroughs/adk2_06_schemas.py`
- [ ] **F7** `notebooks/_shared/education/walkthroughs/adk2_07_walk_script.py`
- [ ] **F8** `notebooks/_shared/education/walkthroughs/adk2_08_capstone_decision_tree.py`

## 7. Stage 1G — README updates + new skill (5 files)

- [ ] **G1** `.agents/skills/adk2-pillars/SKILL.md` — NEW: the 3 Pillar router skill
- [ ] **G2** `README.md` — MODIFY: add the ADK 2 + agent-valley paragraph after the "sprawling on purpose" paragraph
- [ ] **G3** `agents/meaisinfhoghlaim/AGENTS.md` — MODIFY: add the ADK 2 + archive paragraph after the OCR/HTR paragraph
- [ ] **G4** `agents/README.md` — MODIFY: add the ADK 2 + 3 Pillar paragraph after the polyglot-agent paragraph
- [ ] **G5** `dlt_sources/AGENTS.md` — MODIFY: add the ADK 2 + season.csv + burn() paragraph after the cross-jurisdiction paragraph

## 8. Stage 1H — Openspec change + verification + commit + push (4 files)

- [ ] **H1** `openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/specs/adk2-pillars-orchestration/spec.md`
- [ ] **H2** `openspec validate --strict` exits 0
- [ ] **H3** `openspec archive --yes`
- [ ] **H4** `git add -A && git commit && git push`
