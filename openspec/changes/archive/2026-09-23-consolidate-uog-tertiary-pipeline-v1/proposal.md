# Change: consolidate-uog-tertiary-pipeline-v1

## Why

Three workstreams converge on a single tertiary-level pipeline at
University of Galway (Ollscoil na Gaillimhe):

1. **KCG/ollscoil-na-gaillimhe retirement.** The `kings_college_galway`
   sister repo (publicly at `github.com/cianfhoghlaim/ollscoil-na-gaillimhe`)
   ships 5 UoG public-surface DLT sources + 4 BAML files + 2 CocoIndex
   flows + an OSINT allowlist. The sister-repo split was a temporary
   case-study sandbox; per the user's reverted-split directive the
   pipeline moves wholesale into cianfhoghlaim's monorepo.

2. **Students' Union extraction from ciandlithe.** The
   `ciandlithe/agents/adk/students_union/` package is UoG-specific
   (5 SU specialist ADK agents + 1 root orchestrator + 5 pure-Python
   tools) and was misfiled in ciandlithe per the case-study-sister
   design. It moves to
   `agents/meaisinfhoghlaim/educational/students_union/` and becomes
   the 13th specialist in the 12-agent fleet.

3. **Authenticated UoG portal (regexam.nuigalway.ie + Canvas).**
   The previous plans (Layer 0 Chrome DevTools MCP PoC + Layer 1
   GOLD_STANDARD stacks + Layer 2 ADK vision-language agent + Layer 3
   Cognee + marimo) fold into this umbrella change so the per-user
   credential vault + the CopilotKit subset picker ship with the
   same openspec archive.

The BIEP v3 per-subject factory pattern (per
`cocoindex_flows/biep_parity/ireland_lc_factory.py`) scales up: at the
tertiary level, the analogous unit is the **module** (~1,500 modules
per university), with the hierarchy College → School → Programme →
Module. The CocoIndex factory emits one CocoIndex App per module from
a `_modules.yaml` config.

## What Changes

### Code — new (~70 files)

**Tier 1 — DLT sources**
- `dlt_sources/british_isles/ireland/tertiary/uog/__init__.py`
- `dlt_sources/british_isles/ireland/tertiary/uog/_base.py` (the
  UogPipelineBase + TertiaryPipelineBase consolidation)
- `dlt_sources/british_isles/ireland/tertiary/uog/academic_calendar.py`
  (moved from KCG)
- `dlt_sources/british_isles/ireland/tertiary/uog/governance_minutes.py`
  (moved from KCG, renamed from `university_council_minutes.py`)
- `dlt_sources/british_isles/ireland/tertiary/uog/press_releases.py`
  (moved from KCG)
- `dlt_sources/british_isles/ireland/tertiary/uog/programme_catalog.py`
  (moved from KCG, renamed from `course_catalog.py`)
- `dlt_sources/british_isles/ireland/tertiary/uog/research_outputs.py`
  (moved from KCG)
- `dlt_sources/british_isles/ireland/tertiary/uog/colleges.py` (NEW)
- `dlt_sources/british_isles/ireland/tertiary/uog/schools.py` (NEW)
- `dlt_sources/british_isles/ireland/tertiary/uog/programmes.py` (NEW)
- `dlt_sources/british_isles/ireland/tertiary/uog/modules.py` (NEW)
- `dlt_sources/british_isles/ireland/tertiary/uog/module_handbooks.py`
  (NEW; per-module PDF download + OCR via the BIEP v2 4-path ensemble)
- `dlt_sources/british_isles/ireland/tertiary/uog/reading_lists.py`
  (NEW; per-module reading list extraction)
- `dlt_sources/british_isles/ireland/tertiary/uog/past_papers.py`
  (NEW; per-module regexam.nuigalway.ie links via the per-user vault)
- `dlt_sources/british_isles/ireland/tertiary/uog/regexam_papers.py`
  (NEW; the regexam authenticated scraper)
- `dlt_sources/british_isles/ireland/tertiary/uog/canvas_materials.py`
  (NEW; the Canvas REST API + Patchright fallback)

**Tier 2 — BAML schemas**
- `baml_src/british_isles/ireland/tertiary/university_extraction.baml`
  (refactored: 4 classes — College, School, Programme, Module —
  with the 5 functions ExtractCollege/School/Programme/Module/ModuleHandbook)
- `baml_src/british_isles/ireland/tertiary/academic_calendar.baml`
- `baml_src/british_isles/ireland/tertiary/governance_minute.baml`
- `baml_src/british_isles/ireland/tertiary/press_release.baml`
- `baml_src/british_isles/ireland/tertiary/research_output.baml`
- `baml_src/british_isles/ireland/tertiary/module_handbook.baml`
- `baml_src/british_isles/ireland/tertiary/reading_list.baml`
- `baml_src/british_isles/ireland/tertiary/past_paper.baml`
- `baml_src/british_isles/ireland/tertiary/uoa_portal_content.baml`

**Tier 3 — CocoIndex flows**
- `cocoindex_flows/british_isles/ireland/tertiary/uog/_shared.py`
  (the `create_uog_module_flow(config: UoGTertiaryConfig)` factory)
- `cocoindex_flows/british_isles/ireland/tertiary/uog/_modules.yaml`
  (~1,500 row config)
- `cocoindex_flows/british_isles/ireland/tertiary/uog/colleges_flow.py`
- `cocoindex_flows/british_isles/ireland/tertiary/uog/schools_flow.py`
- `cocoindex_flows/british_isles/ireland/tertiary/uog/programme_flow.py`
  (renamed from KCG `courses_flow.py`)
- `cocoindex_flows/british_isles/ireland/tertiary/uog/governance_flow.py`
- `cocoindex_flows/british_isles/ireland/tertiary/uog/press_releases_flow.py`
- `cocoindex_flows/british_isles/ireland/tertiary/uog/research_outputs_flow.py`
- `cocoindex_flows/british_isles/ireland/tertiary/uog/module_flow.py`
  (the per-module factory-rendered flow)
- `cocoindex_flows/british_isles/ireland/tertiary/uog/module_handbook_flow.py`
- `cocoindex_flows/british_isles/ireland/tertiary/uog/reading_list_flow.py`
- `cocoindex_flows/british_isles/ireland/tertiary/uog/past_paper_flow.py`

**Tier 4 — ADK agents**
- `agents/meaisinfhoghlaim/educational/students_union/__init__.py`
  (moved from ciandlithe)
- `agents/meaisinfhoghlaim/educational/students_union/root_agent.py`
- `agents/meaisinfhoghlaim/educational/students_union/config.py`
- `agents/meaisinfhoghlaim/educational/students_union/class_rep_aggregator_agent.py`
- `agents/meaisinfhoghlaim/educational/students_union/clubs_socs_agent.py`
- `agents/meaisinfhoghlaim/educational/students_union/complaints_welfare_agent.py`
- `agents/meaisinfhoghlaim/educational/students_union/elections_agent.py`
- `agents/meaisinfhoghlaim/educational/students_union/grants_funding_agent.py`
- `agents/meaisinfhoghlaim/educational/students_union/tools/__init__.py`
- `agents/meaisinfhoghlaim/educational/students_union/tools/class_rep_themer.py`
- `agents/meaisinfhoghlaim/educational/students_union/tools/clubs_socs_validator.py`
- `agents/meaisinfhoghlaim/educational/students_union/tools/complaint_router.py`
- `agents/meaisinfhoghlaim/educational/students_union/tools/election_validator.py`
- `agents/meaisinfhoghlaim/educational/students_union/tools/grants_matcher.py`
- `agents/uoa_portal/portal_agent.py` (the 5-stage SequentialAgent)
- `agents/uoa_portal/tools/uoa_browse.py`
- `agents/uoa_portal/tools/uoa_vision.py`
- `agents/uoa_portal/tools/stream_to_lakehouse.py`
- `agents/uoa_portal/tools/baml_extract_uoa_portal.py`
- `agents/uoa_portal/tools/cocoindex_upsert.py`

**Tier 5 — Bonneagar stacks (6-file GOLD_STANDARD per stack)**
- `bonneagar/stacks/regexam-nuig/{compose,sidecar,secrets.env,pangolin,blueprint}.yaml` + `.env.example`
- `bonneagar/stacks/canvas-nuig/{compose,sidecar,secrets.env,pangolin,blueprint}.yaml` + `.env.example`
- `bonneagar/stacks/uo-portal-vault/{compose,sidecar,secrets.env,pangolin,blueprint}.yaml` + `.env.example`

**Tier 6 — marimo notebooks (25 total)**
- `notebooks/_shared/tertiary/uog_explorer.py` (moved from KCG)
- `notebooks/_shared/tertiary/00_uog_tertiary_overview.py` (NEW)
- `notebooks/_shared/tertiary/01_uog_college_<college-id>.py` × 4
- `notebooks/_shared/tertiary/02_uog_programme_<programme-id>_top_20.py` × 20
- `notebooks/_shared/tertiary/03_uog_past_papers_explorer.py`
- `notebooks/_shared/tertiary/04_uog_module_handbook_explorer.py`
- `notebooks/_shared/tertiary/students_union_adk_case_studies.py`
  (moved from ciandlithe; cross-repo `sys.path` hack removed)
- `notebooks/_shared/tertiary/students_union_tertiary_integration.py`
  (moved + renamed; references
  `dlt_sources.british_isles.ireland.tertiary.uog` directly)

**Tier 7 — Dagster orchestration (per layer)**
- `orchestration/defs/1_ingestion/tertiary/uog/{academic_calendar,
  governance_minutes, press_releases, programme_catalog,
  research_outputs, colleges, schools, programmes, modules,
  module_handbooks, reading_lists, past_papers, regexam_papers,
  canvas_materials}.py`
- `orchestration/defs/2_materials/tertiary/uog/` (14 BAML extraction assets)
- `orchestration/defs/3_model_lifecycle/tertiary/uog/` (3 embedder routing)
- `orchestration/defs/4_asset_generation/tertiary/uog/` (10 CocoIndex assets + budget)
- `orchestration/defs/5_agent_ops/tertiary/uog/` (2 ADK agents + schedule + sensor + RAGAS)

**Tier 8 — Scripts + tests + openspec**
- `scripts/cognee_ingest_uoa_portal.py`
- `scripts/osint_allowlists/ireland_tertiary.yaml`
- `scripts/lint_osint_allowlists.py` (extended)
- `tests/tertiary/test_uog_smoke.py`
- `tests/agents/students_union/test_smoke.py`
- `openspec/specs/cianfhoghlaim-tertiary-pipeline/spec.md`
- `openspec/specs/retire-kcg-sister-repo/spec.md`
- `openspec/specs/extract-students-union-from-ciandlithe/spec.md`
- `.agents/skills/uoa-tertiary-pipeline/SKILL.md`

### Code — modified (~15 files)

- `dlt_sources/british_isles/ireland/university/` → rename to
  `tertiary/` (5 sources + `__init__.py`)
- `baml_src/british_isles/ireland/education/university/` → rename to
  `baml_src/british_isles/ireland/tertiary/` (the BAML extraction)
- `dlt_sources/common/site_crawler.py` (+4 ScrapePolicy rows)
- `dlt_sources/common/__init__.py`
- `baml_src/_shared/provider_router.py`
- `baml_src/clients.baml`
- `orchestration/defs/4_budget/firecrawl_budget_asset.py` (+4 budget rows)
- `orchestration/defs/sensors/uoa_portal_sensor.py`
- `orchestration/partitions.py`
- `mise.toml` (add `oideachais:tertiary:*` + `oideachais:uoa-portal:*`)
- `meaisinfhoghlaim/models/model_registry.py`
- `meaisinfhoghlaim/models/registry.py`
- `agents/agent_registry.py` (register the 13th fleet specialist)
- `agents/meaisinfhoghlaim/AGENTS.md`
- `openspec/AGENTS.md` (update the priority specs table)
- `openspec/specs/british-isles-education-pipeline-v3/spec.md:698`
  (rename `'university'` → `'tertiary'`)
- `openspec/specs/cianfhoghlaim-university-deep-extraction/spec.md`
  (DEPRECATED notice)
- `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts`
  (+2 actions: `list_uoa_modules` + `download_uoa_subset`)
- `opencode.json` (register `uoa_portal_pipeline` +
  `students_union_root_agent` agents)

### Code — deleted

- `~/dev/kings_college_galway/` (entire local dir)
- `github.com/cianfhoghlaim/ollscoil-na-gaillimhe` (GitHub repo via
  `gh repo delete`)
- `ciandlithe/agents/adk/students_union/` (entire dir)
- `ciandlithe/notebooks/students_union_adk_case_studies.py`
- `ciandlithe/notebooks/students_union_kcg_integration.py`
- `ciandlithe/openspec/specs/ciandlithe-adk-students-union/spec.md`
- `ciandlithe/mise.toml` lines ~330-336 (the 3 SU mise tasks)
- `openspec/specs/kcg-pipeline/spec.md` (replaced by
  `openspec/specs/cianfhoghlaim-tertiary-pipeline/spec.md`)

## Out of scope (follow-up changes)

1. **`openspec/changes/<id>-extend-tertiary-to-7-other-ireland-universities-v1/`**
   — TCD + UCD + UCC + UL + DCU + Maynooth + RCSI (via the
   `cianfhoghlaim-university-deep-extraction` factory at
   `dlt_sources/british_isles/ireland/_university_deep_factory.py`).
2. **`openspec/changes/<id>-uoa-portal-canvas-rest-api-v1/`** — once
   UoG IT confirms self-service PAT policy, switch the Canvas DLT
   source from Patchright fallback to REST primary.
3. **`openspec/changes/<id>-update-students-union-constitution-v1/`**
   — when SU updates its bylaws, only
   `agents/meaisinfhoghlaim/educational/students_union/config.py`
   needs editing.

## Dependencies

`Blocked by: none` (this is the foundational consolidation).
`Blocked by (soft): pipeline-sister-repo-handoff` (the umbrella
sister-handoff change is the canonical cross-repo sync mechanism
this change uses; not blocking per the topo ordering).
`Affected repos: cianfhoghlaim + ciandlithe + (GitHub API deletion
of) github.com/cianfhoghlaim/ollscoil-na-gaillimhe`.

## Cross-repo sync

Per the convention at `openspec/AGENTS.md:281`, the 3 repos MUST be
committed/archived in this order:

1. **cianfhoghlaim first** — commit + archive this umbrella change
   (creates the receiving locations: the new tertiary pipeline +
   the SU package + the authenticated stacks + the ADK agents)
2. **ciandlithe second** — open + archive
   `openspec/changes/<YYYY-MM-DD>-remove-students-union-from-ciandlithe-v1/`
   (deletes the SU code from ciandlithe cleanly; references
   cianfhoghlaim's receiving locations)
3. **GitHub repo deletion last** —
   `gh repo delete cianfhoghlaim/ollscoil-na-gaillimhe` returns 204
4. **Local dir removal last** — `rm -rf ~/dev/kings_college_galway`

The ciandlithe removal change is documented inline in this
`cross-repo-sync.md`.

## Verification

```bash
# 1. Strict openspec validation
cd ~/dev/cianfhoghlaim
openspec validate 2026-09-23-consolidate-uog-tertiary-pipeline-v1 --strict
# Expected: exit 0

# 2. BAML codegen
baml-cli generate --from baml_src
# Expected: exit 0 (the 8 tertiary BAML files compile)

# 3. KCG naming artifacts are gone
git grep kings_college_galway    # Expected: 0 matches
git grep ollscoil-na-gaillimhe   # Expected: 0 matches
git grep "uog_pipeline_base"     # Expected: 0 matches

# 4. ciandlithe SU extraction
git grep students_union          # Expected: only in updated README/AGENTS/LICENSE pointers

# 5. Sync health
mise run lint:skills
mise run lint:drift-docs
mise run lint:osint
mise run lint:firecrawl-budget
mise run sync:all
mise run lint:openspec
# Expected: all exit 0

# 6. UoG smoke test
python tests/tertiary/test_uog_smoke.py
# Expected: exit 0

# 7. SU smoke test (the moved ciandlithe package)
python agents/meaisinfhoghlaim/educational/students_union/_smoke_test.py
# Expected: "All 5 SU case-study tools + 5 agents + root_agent + classifier pass."

# 8. Stack deploy
komodo deploy regexam-nuig
komodo deploy canvas-nuig
komodo deploy uo-portal-vault
# Expected: all exit 0

# 9. Sister-repo retirement
gh repo delete cianfhoghlaim/ollscoil-na-gaillimhe
rm -rf ~/dev/kings_college_galway
ls ~/dev/kings_college_galway
# Expected: No such file or directory
```
