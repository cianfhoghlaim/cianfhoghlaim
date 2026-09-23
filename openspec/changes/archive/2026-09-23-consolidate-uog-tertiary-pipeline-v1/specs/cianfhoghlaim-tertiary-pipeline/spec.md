# cianfhoghlaim-tertiary-pipeline Specification

## Purpose

The `cianfhoghlaim-tertiary-pipeline` is the canonical capability
that systematises the **tertiary-education pipeline** (the
University-of-Galway / Ollscoil-na-Gaillimhe instance of the broader
British-Isles-Education-Pipeline BIEP v3 umbrella, per
`openspec/specs/british-isles-education-pipeline-v3/spec.md`).

This spec supersedes the per-repo `kcg-pipeline` spec
(formerly in `~/dev/kings_college_galway/openspec/specs/kcg-pipeline/`,
now retired). It is the umbrella for all 14 UoG DLT sources + the
4-tier BAML schema + the per-module CocoIndex factory + the
Students' Union ADK agents + the authenticated regexam.nuigalway.ie
+ Canvas pipelines.

The stage taxonomy: `'primary' | 'jc' | 'sc' | 'tertiary'` (renamed
from `'university'` per the `pipeline-naming-taxonomy` change). The
tertiary stage covers universities + TUs + QQI/FET + apprenticeships.

## Requirements

## ADDED Requirements

### Requirement: 4-tier tertiary pipeline schema

The system SHALL provide a 4-tier `College → School → Programme →
Module` BAML schema at
`baml_src/british_isles/ireland/tertiary/university_extraction.baml`
with 5 extraction functions: `ExtractCollege`, `ExtractSchool`,
`ExtractProgramme`, `ExtractModule`, `ExtractModuleHandbook`.

The `Module` class SHALL have 23 fields including the 4 new ones
(`learning_outcomes[]`, `reading_list[]`, `past_paper_urls[]`,
`handbook_pdf_url?`).

#### Scenario: Module extraction covers all 23 fields including the 4 new ones

- **WHEN** the operator runs `python -m baml_src.british_isles.ireland.tertiary.university_extraction`
- **THEN** the `Module` class has 23 fields including the 4 new ones
- **AND** `bun run ccc:search "Module class"` returns exactly 1 hit (no duplicates)

### Requirement: Per-tier DLT sources

The system SHALL provide 15 DLT sources in
`dlt_sources/british_isles/ireland/tertiary/uog/` covering the 4
tiers + the per-tier deep extractions + the authenticated surfaces:

1. `academic_calendar.py` (moved from KCG)
2. `governance_minutes.py` (moved from KCG)
3. `press_releases.py` (moved from KCG)
4. `programme_catalog.py` (moved from KCG, renamed)
5. `research_outputs.py` (moved from KCG)
6. `colleges.py` (NEW)
7. `schools.py` (NEW)
8. `programmes.py` (NEW)
9. `modules.py` (NEW)
10. `module_handbooks.py` (NEW)
11. `reading_lists.py` (NEW)
12. `past_papers.py` (NEW)
13. `regexam_papers.py` (NEW — authenticated)
14. `canvas_materials.py` (NEW — authenticated)
15. `_base.py` + `__init__.py`

#### Scenario: All 14 DLT sources run end-to-end

- **WHEN** the operator runs `pn dlt_pipeline --source uog_<name>` for all 14 sources
- **THEN** each source emits ≥1 row (Phase 1: local cache via `USE_LOCAL_SCRAPES=true`; Phase 2: live scrape)

### Requirement: Per-tier CocoIndex flows

The system SHALL provide 10 CocoIndex v1 flows + a per-module factory
at `cocoindex_flows/british_isles/ireland/tertiary/uog/`:

1. `_shared.py` — the `create_uog_module_flow(config: UoGTertiaryConfig)` factory
2. `_modules.yaml` — the 1,500-row module config
3. `colleges_flow.py`
4. `schools_flow.py`
5. `programme_flow.py` (moved from KCG `courses_flow.py`)
6. `governance_flow.py` (moved from KCG)
7. `press_releases_flow.py`
8. `research_outputs_flow.py`
9. `module_flow.py` (factory-rendered per module)
10. `module_handbook_flow.py`
11. `reading_list_flow.py`
12. `past_paper_flow.py`

#### Scenario: Factory emits ≥1,500 module CocoIndex Apps

- **WHEN** the operator runs `python -m cocoindex_flows.british_isles.ireland.tertiary.uog._shared`
- **THEN** `create_uog_module_flow(config)` is called for every row in `_modules.yaml` (≥1,500 calls)
- **AND** each call returns a `coco.App` instance with `name=f"uog_<module_id>_flow"`

### Requirement: Students' Union case studies

The system SHALL provide 5 specialist Google ADK `LlmAgent` instances +
1 root orchestrator + 5 pure-Python `FunctionTool`s at
`agents/meaisinfhoghlaim/educational/students_union/` (moved from
ciandlithe). The 5 specialists are:

1. `clubs_socs_agent` — Clubs & Societies Registration review
2. `grants_funding_agent` — Grants & Funding triage
3. `class_rep_aggregator_agent` — Class Rep Feedback aggregation
4. `complaints_welfare_agent` — Complaints & Welfare triage
5. `elections_agent` — Election & Referendum workflow

Plus 1 root orchestrator `students_union_root_agent` at
`agents/meaisinfhoghlaim/educational/students_union/root_agent.py`
that exposes the 5 specialists as `sub_agents` and includes a
`classify_su_query(query)` intent classifier. The root becomes the
13th specialist in the 12-agent fleet (per
`agent-fleet-orchestration/SKILL.md`).

#### Scenario: All 5 SU specialists construct cleanly + the fleet registry includes them

- **WHEN** the operator runs `python agents/meaisinfhoghlaim/educational/students_union/_smoke_test.py`
- **THEN** the smoke test exits 0 with "All 5 SU case-study tools + 5 agents + root_agent + classifier pass."
- **AND** `agents/agent_registry.py` registers `students_union_root_agent` as the 13th fleet specialist

### Requirement: Authenticated UoG portal (regexam.nuigalway.ie + Canvas)

The system SHALL provide a per-user authenticated UoG portal pipeline
with:

- 3 GOLD_STANDARD stacks (`regexam-nuig` + `canvas-nuig` + `uo-portal-vault`)
- 2 DLT sources (`regexam_papers.py` + `canvas_materials.py`)
- 1 ADK 5-stage SequentialAgent (`uoa_portal_pipeline` at `agents/uoa_portal/portal_agent.py`)
- 1 CopilotKit UI action pair (`list_uoa_modules` + `download_uoa_subset`)
- 1 marimo notebook (`notebooks/_shared/tertiary/uog_explorer.py`)
- 1 BAML extraction class (`baml_src/british_isles/ireland/tertiary/uoa_portal_content.baml`)

The per-user credential vault at `bonneagar/stacks/uo-portal-vault/`
provisions per-user secrets via Locket + Infisical at
`infisical://dev-baile/cianfhoghlaim/{regexam-nuig,canvas-nuig}/<user>/{username,password}`.
The 1-time unlock procedure (`komodo run unlock-uo-portal --user <u>`)
opens Chromium + drives the M365 OAuth flow + captures the AppProxy
cookies + writes them to
`/stedding/user_profiles/<u>/{regexam,canvas}/cookies.json`.

The Canvas DLT source SHALL attempt the REST API with a Personal
Access Token first (self-service, no IT involvement) and fall back to
Patchright + M365 OAuth if the PAT endpoint is disabled by UoG IT.

#### Scenario: Chrome DevTools MCP PoC validates the M365 login flow

- **WHEN** the operator runs the Chrome DevTools MCP PoC against `https://regexam.nuigalway.ie/...`
- **THEN** the M365 OAuth redirect is captured + the 2 AppProxy cookies are documented + the regexam search form structure is mapped
- **AND** `komodo deploy regexam-nuig && komodo deploy canvas-nuig && komodo deploy uo-portal-vault` succeeds

#### Scenario: Canvas PAT-first with M365 fallback (no IT involvement)

- **WHEN** a UoG student runs `python -m dlt_sources.british_isles.ireland.tertiary.uog.canvas_materials`
- **THEN** the source first tries the Canvas REST API at `https://canvas.universityofgalway.ie/api/v1/users/self/courses` with the user's PAT
- **AND** if the PAT endpoint returns 401/403 (e.g. UoG IT disabled self-service PAT), the source automatically falls back to Patchright + M365 OAuth cookies
- **AND** the operator never needs to ask UoG IT for either approach

### Requirement: Retirement of the KCG sister-repo

The system SHALL retire `github.com/cianfhoghlaim/ollscoil-na-gaillimhe`
and delete `~/dev/kings_college_galway/` after the merge. Per the
`pipeline-sister-repo-handoff` umbrella, the KCG sister-repo's
case-study-sister mission is fully replaced by the new
`dlt_sources/british_isles/ireland/tertiary/uog/` package.

#### Scenario: GitHub API deletion + local removal succeed

- **WHEN** the operator runs `gh repo delete cianfhoghlaim/ollscoil-na-gaillimhe && rm -rf ~/dev/kings_college_galway/`
- **THEN** both exit 0
- **AND** `git grep kings_college_galway` returns 0 in cianfhoghlaim
- **AND** `git grep ollscoil-na-gaillimhe` returns 0 in cianfhoghlaim

### Requirement: Extraction of the SU package from ciandlithe

The system SHALL extract `ciandlithe/agents/adk/students_union/` (and
the 2 notebooks + 1 spec + 3 mise tasks) into cianfhoghlaim's
`agents/meaisinfhoghlaim/educational/students_union/`. The SU
package is UoG-specific and was misfiled in ciandlithe per the
case-study-sister design.

#### Scenario: ciandlithe's SU deletion lands clean

- **WHEN** the operator archives `openspec/changes/<YYYY-MM-DD>-remove-students-union-from-ciandlithe-v1/` in ciandlithe
- **THEN** `ls ciandlithe/agents/adk/students_union/` fails (dir removed)
- **AND** `git grep students_union` in ciandlithe returns 0 (only in updated README/AGENTS/LICENSE references)

### Requirement: Firecrawl budget allocations for the tertiary pipeline

The system SHALL allocate monthly Firecrawl credits for the tertiary
pipeline:

| Pipeline | Monthly credits |
|:--|--:|
| `dlt:regexam_nuig_papers` | 60 |
| `dlt:regexam_nuig_marking` | 60 |
| `dlt:canvas_nuig_files` | 80 |
| `dlt:canvas_nuig_video` | 40 |
| `dlt:uog_colleges` | 40 |
| `dlt:uog_schools` | 40 |
| `dlt:uog_programmes` | 80 |
| `dlt:uog_modules` | 120 |
| `dlt:uog_module_handbooks` | 80 |
| `dlt:uog_reading_lists` | 40 |
| `dlt:uog_past_papers` | 40 |
| `dlt:uog_press_releases` | 40 |
| `dlt:uog_governance_minutes` | 40 |
| `dlt:uog_research_outputs` | 40 |
| **Total** | **800** |

#### Scenario: Budget linter passes

- **WHEN** the operator runs `mise run lint:firecrawl-budget`
- **THEN** the budget linter exits 0
- **AND** no pipeline exceeds 150% of its allocation

### Requirement: Dagster orchestration across 5 layers

The system SHALL provide Dagster assets in the 5-layer pattern
(per `dagster-5-layer-component-architecture/spec.md`):

- **1_ingestion/tertiary/uog/** — 14 DLT asset entries
- **2_materials/tertiary/uog/** — 14 BAML extraction assets; 6 RAGAS asset checks
- **3_model_lifecycle/tertiary/uog/** — embedder routing + OCR ensemble for handbooks
- **4_asset_generation/tertiary/uog/** — 10 CocoIndex App assets + firecrawl budget
- **5_agent_ops/tertiary/uog/** — 2 ADK agents + 1 schedule + 1 sensor + 1 RAGAS evaluator

#### Scenario: pn runs the 5-phase pattern end-to-end

- **WHEN** the operator runs `mise run oideachais:tertiary:full-pipeline`
- **THEN** the 5 phases run in order (Ingestion → Extraction → Embedding → ibis logging → Analytics)
- **AND** the RAGAS asset checks pass with score ≥ 0.70
- **AND** the LanceDB chunks land in the canonical table `cianfhoghlaim.tertiary.uog.<module_id>_chunks`

### Requirement: Per-college marimo dashboards

The system SHALL provide 25 marimo notebooks at
`notebooks/_shared/tertiary/`:

- `uog_explorer.py` — overview
- `00_uog_tertiary_overview.py` — 6 tabs
- `01_uog_college_<college-id>.py` × 4 — one per college
- `02_uog_programme_<programme-id>_top_20.py` × 20 — top programmes
- `03_uog_past_papers_explorer.py` — past papers explorer
- `04_uog_module_handbook_explorer.py` — handbooks explorer
- `students_union_adk_case_studies.py` — the 5 SU case studies
- `students_union_tertiary_integration.py` — SU × tertiary integration

#### Scenario: All 25 notebooks render with real UoG data

- **WHEN** the operator runs `marimo edit notebooks/_shared/tertiary/<notebook>.py` for any of the 25
- **THEN** the notebook renders without errors
- **AND** the data tabs query the live LanceDB tables at `md:cianfhoghlaim.tertiary.uog.<table>`
