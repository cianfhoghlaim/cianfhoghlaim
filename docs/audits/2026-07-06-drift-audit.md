# Cianfhoghlaim Monorepo Drift Audit — 2026-07-06

> **Scope:** Full audit of `.agents/skills/`, `openspec/`, and
> `cianfhoghlaim/notebooks/` after the v4 consolidation (2026-06-28) and
> the user's removal of ~14 KCG-specific skills + the tuatha/agents/adk/
> cluster (2026-07-06). Produced to inform the
> `2026-07-06-drift-cleanup-and-v4-alignment` and
> `2026-07-06-british-isles-education-pipeline-v1` openspec changes.

## TL;DR

| Surface | Total | Healthy | Drift | Delete / Archive |
|---|--:|--:|--:|--:|
| **`.agents/skills/` SKILL.md files** | 235 → **58 after user removals** | ~14 (real KCG) | ~20 | **24** (vendor bloat kept for later cleanup) |
| **`openspec/` capability specs** | 56 | ~20 | ~30 (incl. 2 phantom) | — (REWRITE in place) |
| **`openspec/` pending changes** | 66 | ~22 active | ~12 partial | **~30 ARCHIVE** |
| **`cianfhoghlaim/notebooks/`** | 89 (88 marimo + 1 empty `.ipynb`) → **91 after law/01 + chemistry.py user mods** | 3 | ~50 | — (user removed candidates; update remainder) |
| **LC pipelines (6 subjects)** | existing | **5 healthy (maths, chem, geo, gaeilge, CS)** | **English missing** | — (English needs wiring) |

**Big surprise:** LC pipelines for **5 of 6** priority subjects (maths, chem,
geo, gaeilge, CS) are **already working** — `lc5_documents` DLT source, BAML
extraction, CocoIndex flow, and Dagster assets all exist. Only **English** is
missing the lc5 wiring. The bulk of remaining work is:

1. **Cleanup drift** (skills path rewrites + notebook PEP 723 / DuckDB /
   no-secrets pass)
2. **Wire English** (small ~20 LOC + 5 asset defs)
3. **Consolidate** the 2 parallel BAML function sets + 2 parallel DLT source
   families for the same 6 subjects
4. **v1-conformance** the 6 CocoIndex subject flows (`lancedb.mount_table_target`)
5. **Add gov.ie circulars** DLT source (genuinely new — no source today)
6. **Rewrite the 16 leaving_cert subject notebooks** so they read from
   `md:oideachais` DuckLake (currently hardcoded sample data)
7. **MotherDuck Dives + Flights** for the analytics layer

---

## 1. Skills Audit (post-user-removal)

### Inventory after user deletions (2026-07-06)

- **58 skills remaining** (was 72 top-level + 235 SKILL.md files including
  references)
- **User removed 14 KCG-specific skills** → backed up at `.agents/skills_backup/`
  (NOT deleted; user can restore any):
  `cianfhoghlaim-mmo`, `dagger-pipelines`, `dagger`, `effect-ts`, `feast`,
  `infrastructure-stacks-documentation`, `infrastructure-stacks`,
  `ncca-formative-assessment`, `cianfhoghlaim-cocoindex-v1`, `cianfhoghlaim-email-triage`,
  `cianfhoghlaim-leabharlann`, `olake`, `orpc`, `pulumi`
- **User also deleted** the `agents/tuatha/agents/adk/` cluster (5 files
  incl. `root_agent.py`, `celtic_tutor.py`, `mythology_narrator.py`,
  `quest_guide.py`, `research_assistant.py`)

### Remaining 58 skills

```
ag-ui, agent-fleet-orchestration, agent-memory-systems, agent-observability,
agentic-frontend-frameworks, agno, apple-photos-ingestion, babylonjs, baml,
better-auth, browser-tools, ccc, change-detection, cloudflare, cocoindex,
cognee, convex, copilotkit, crawl4ai, dagster, dignified-python, dlt,
dlthub, dlthub-router, duckdb, ducklake, falkordb, firecrawl, firecrawl-cli,
garage, google-adk, graphiti, graphiti-core, hono, huggingface, ibis,
iceberg-lakekeeper, improve-skills, INDEXING_AND_COGNITION.md, komodo,
lancedb, langfuse, lint-skills.sh, litellm, marimo, memgraph, mlflow, modal,
motherduck, pangolin, pydantic, ragas, risingwave, secrets-management,
setup-secrets, tanstack-start, unsloth
```

### Drift in remaining skills

| Skill | Drift | Action |
|---|---|---|
| `dlt` | References `sruth/cianfhoghlaim/dlt_sources/` (line 45, 66) and `cianfhoghlaim.data_platform` (lines 48-50) — pre-v4 paths | **REWRITE** to `cianfhoghlaim/dlt/` |
| `cocoindex` | References `sruth/cianfhoghlaim/cocoindex_flows/` (14+ sites: L51, L56, L64-68, L80-82, L100-102, L618, L629) and `sruth/crypteolas/cocoindex_flows/` (L86) | **REWRITE** to `cianfhoghlaim/cocoindex/` |
| `dagster` | `cianfhoghlaim.data_platform.dagster_defs.definitions` (top-level) | **REWRITE** to `cianfhoghlaim.orchestration.definitions` |
| `baml` | References `sruth/cianfhoghlaim/baml_src/`, `sruth/cianfhoghlaim/dlt_sources/ireland/` | **REWRITE** to `cianfhoghlaim/baml/`, `cianfhoghlaim/dlt/british_isles/ireland/` |
| `secrets-management` | `infisical://dev-baile/sruth/cianfhoghlaim/OPENAI_API_KEY` (L33, L200) | **FIX URI** to `infisical://dev-baile/cianfhoghlaim/OPENAI_API_KEY` |
| `agent-fleet-orchestration` | References deleted `agents/tuatha/agents/adk/*.py` cluster | **REWRITE** to reflect tuatha adk cluster removed |
| `change-detection` | `sruth/cianfhoghlaim/sources.yaml` | **REWRITE** to `cianfhoghlaim/dlt/sources.yaml` |
| `agent-memory-systems`, `agent-observability`, `agentic-frontend-frameworks` | Various `sruth/<quadrant>/...` refs | **REWRITE** to `cianfhoghlaim/<area>/...` |
| `garage`, `iceberg-lakekeeper`, `apple-photos-ingestion`, `komodo`, `pangolin` | KCG-specific, mostly accurate; minor `bonneagar/` references in docs | **MINOR FIX** |
| `dlthub`, `dlthub-router`, `setup-secrets` | Wrong paradigm (dltHub Platform, `.dlt/secrets.toml`) | **USER KEPT** — keep but add deprecation banner |
| `ccc` | Self-deprecates ("retires 2026-07-15"); user kept | **UPDATE banner** to point at user-retained replacement |
| `graphiti-core` | Stale v0.5.0 (2025-04) | **USER KEPT** — keep but add banner pointing at `graphiti/` |
| Vendor over-bloat (motherduck, huggingface, cloudflare, marimo, copilotkit) | 20+16+8+14+16 subskills of marketing-tier / upstream material | **USER KEPT** — keep, but add British-Isles Education context to the canonical 5 per family |

### Plan

For every remaining skill, update the body to:

1. Reflect current v4 paths (`cianfhoghlaim/...`, NOT `sruth/<quadrant>/...`)
2. Reference the British-Isles Education pipeline where relevant (the 6 LC
   subjects + gov.ie circulars are the project's current focus)
3. Remove broken cross-references to deleted skills
4. Add the canonical marimo + DuckDB + Ibis + CocoIndex + DuckLake + LanceDB
   stack invocation pattern in the canonical example sections
5. Move Infisical URI references off the `sruth/` prefix
6. Update `frontmatter.description:` to reflect the project's current goals

---

## 2. OpenSpec Audit

### Inventory

- **56 capability specs** in `openspec/specs/` (AGENTS.md says **36** — already stale)
- **66 pending changes** in `openspec/changes/` (excluding `archive/`)
- **100 archived changes** in `openspec/changes/archive/`
- **143 spec deltas** inside pending changes; **43 still reference `sruth/*` ghost paths**
- **11 plan files** in `openspec/plans/` (all `status: research`)
- **4 research dirs** in `openspec/research/` (historical, fine)

### Phantom specs (advertised in AGENTS.md + project.md but don't exist as dirs)

- `celtic-data-engineering-pipeline`
- `gradio-ensemble-pattern`

The `celtic-data-engineering-patterns` change created deltas for these but
never landed the canonical specs.

### Specs with `Purpose: TBD` placeholder

12 specs have `Purpose: TBD`:
- `celtic-asset-generation`
- `official-media-{pipeline,marimo,fediverse}`
- `author-archive-{credit-budget,cross-corpus-kg,multi-target,pipeline,ui-grounding,uog-coursework,web-scraping}`

### Top stale specs (need REWRITE)

| Spec | LOC | `sruth/` refs |
|---|--:|--:|
| `cianfhoghlaim-pipeline/spec.md` | 1,598 | **107** |
| `meaisinfhoghlaim-platform/spec.md` | 872 | **92** |
| `tuatha-platform/spec.md` | — | **61** (already deprecated alias per AGENTS.md:23) |
| `croilar-data-engineering/spec.md` | 328 | **35** |
| `agentic-frontend-frameworks/spec.md` | — | **17** |
| `infrastructure-stacks/spec.md` | 910 | 31 (path-only: `infrastructure/stacks/` → `bonneagar/stacks/`) |
| `cianfhoghlaim-leabharlann/spec.md` | — | 9 |

### Ready to ARCHIVE (~30 changes)

**8 fully done:**
`2026-06-29-bonneagar-v4-canonical-and-stack-migration`, `modernize-meaisin-cliste`,
`skills-metadata-cleanup`, `2026-07-03-specs-and-session-9-health-report`,
`2026-06-29-restore-heritage-corpus-and-expand-readme`,
`extend-culture-heritage-to-8-articles`, `ingest-culture-heritage`, plus the 4
`browserbase-phase-{1a,1b,2,3}-decisions`.

**~22 superseded by v4:**
`refactor-quadrants-to-sruth`, `refactor-dlt-dagster-2026-stack-align`,
`consolidate-external-libs-into-tuatha`, `croilar-personas-to-streams`,
`lateralise-dlt-sources-to-domains`,
`ireland-primary-jc-dlt-baml-and-full-stack-demo`,
`consolidate-embedding-batcher`, `fix-broken-imports-and-baml`,
`stale-pipelines-cleanup`, `datasets-cleanup`,
`archive-celtic-baml-orphans`, `cianfhoghlaim-stack-polish`,
`cianfhoghlaim-agent-services`, `complete-cognee-knowledge-graph`,
`four-directory-indexing-and-standards`,
`docs-skills-consolidation-pipeline`, `celtic-data-engineering-patterns`,
`refactor-dlt-cocoindex-baml-dagster-with-pdf-pipeline`,
`croilar-revitalisation`, `baml-reorganize-by-cluster`,
`dagger-monorepo-integration`, `leaving-cert-2026`.

### Keep and continue

`2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs` (67/84),
`2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops` (0/148),
`2026-07-02-add-{lancedb-and-logfire,marimo,agent-surface}-stacks`,
`2026-07-02-replace-private-images-and-bring-wave2`,
`2026-07-02-bunchloch-stack-bootstrap`, `2026-07-02-public-about-route`,
`2026-07-03-infrastructure-foundation`,
`2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams` (10/25),
`2026-07-04-dev-env-setup-latest-packages-and-wire-25-notebooks` (28/6),
`add-openclaw-stack-and-channel-fanout`,
`add-openchamber-stack-and-opencode-ui`,
`deploy-llama-swap-v166-stack`, `deploy-v4-ocr-vlm-on-m4-max`,
`litellm-minimax-vendor-derisking`, `ncca-leaving-cert-syllabi-corpus` (9/27),
`wire-v4-models-into-litellm-config`,
`wire-6-stage-pdf-pipeline-to-production`,
`rewrite-cianfhoghlaim-leaving-cert-v2` (55/151),
`cianfhoghlaim-educational-mmo-v1` (90/2),
`croilar-portfolio` (18/16).

---

## 3. Notebooks Audit (post-user-removal)

### Inventory

- **91 notebook files** (`*.py` + 1 `*.ipynb` empty)
- Only **3 healthy** (~3%): `sources_load.py`,
  `meaisinfhoghlaim/{01_leabharlann_descriptive,02_dpre_lag_analysis}.py`
- **17 hardcoded secrets** across ~7 files
- **13 notebooks with hardcoded `/Users/...` paths**
- **3 notebooks** have PEP 723 inline deps; **88 do not**

### Per-subject coverage (6 priority subjects)

| Subject | Notebook | Quality |
|---|---|---|
| **Mathematics** | `dashboards/leaving_cert/05_mathematics_analysis.py` (117 LOC) | DRIFT — hardcoded path, in-memory |
| **Chemistry** | `dashboards/leaving_cert/01_chemistry_analysis.py` (203 LOC) | DRIFT — richest (11 cells, 5 BAML calls) |
| **Geography** | `dashboards/leaving_cert/04_geography_analysis.py` (106 LOC) | DRIFT |
| **Gaeilge** | `dashboards/leaving_cert/03_gaeilge_analysis.py` (114 LOC) | DRIFT — handles no-`en/`-subdir quirk |
| **English** | `dashboards/leaving_cert/06_en_vs_ga_comparison.py` (90 LOC) | DRIFT |
| **Computer Science** | `dashboards/leaving_cert/02_computer_science_analysis.py` (101 LOC) | DRIFT |

User kept all 9 root-level stubs (`notebooks/leaving_cert/{chemistry,mathematics,gaeilge,english,computer_science,applied_mathematics,geography,history,diagram_library}.py`) and the 9 speedrun/ crypto notebooks. These need to be **updated** to fit the current stack and goals (per user direction), not deleted.

### Plan for notebooks

For every remaining notebook:

1. **Add PEP 723 inline deps** at the top (the standard `marimo` block)
2. **Replace `pandas`-only analytics with DuckDB + Ibis** where applicable
3. **Use `mo.sql(engine=md:oideachais)`** for federated lakehouse queries
4. **Replace hardcoded `/Users/...` paths with env vars**
   (`CIANFHOGHLAIM_LEAVING_CERT_ROOT`,
   `CIANFHOGHLAIM_LAKEHOUSE_DUCKDB`, `MOTHERDUCK_TOKEN`)
5. **Remove hardcoded secrets** (Garage keys, PG `devpassword`) — use Infisical
6. **Wire to live lakehouse tables** (`md:cianfhoghlaim.leaving_cert.<subject>.*`,
   `md:cianfhoghlaim.lc.<subject>.<level>_<lang>`) where the source data exists
7. **Update docstrings + references** to reflect British-Isles Education
   pipeline goals

---

## 4. Existing LC Pipeline Audit (6 Priority Subjects)

> **The surprise finding: most of the data plumbing already works.**

### v4 layout (corrected)

| Brief claimed | Actual path |
|:--|:--|
| `dlt_sources/` | `cianfhoghlaim/dlt/` |
| `baml_src/` | `cianfhoghlaim/baml/` (with `baml_src` symlink → `baml/`) |
| `cocoindex_flows/` | `cianfhoghlaim/cocoindex/` |
| `dagster_defs/assets/` | `cianfhoghlaim/orchestration/defs/{1_ingestion,2_materials,3_model_lifecycle,4_asset_generation,5_agent_ops}/...` |

### Per-subject coverage matrix

| Subject | DLT source | BAML schema | CocoIndex flow | Dagster assets | Notebook | Sample PDFs | Status |
|:--|:--|:--|:--|:--|:--|:--|:--|
| **Mathematics** | ✓ `lc5_documents`; (✓) `subjects/mathematics/sources.py` | ✓ `qpack_mathematics.baml` + `ExtractCurriculumSyllabus` | ✓ `mathematics_embedding.py` | ✓ all 5 stages | ✓ `05_mathematics_analysis.py` (drift) | 16 PDFs | **HEALTHY** |
| **Chemistry** | ✓ | ✓ | ✓ | ✓ | ✓ (drift) | 16 PDFs | **HEALTHY** |
| **Geography** | ✓ | ✓ | ✓ | ✓ | ✓ (drift) | 19 PDFs + 1 JPG | **HEALTHY** |
| **Gaeilge** | ✓ (5 resources, fada asset_check) | ✓ + `ExtractCrossLinguisticConcept` | ✓ | ✓ | ✓ (drift) | 11 PDFs (flat) | **HEALTHY** (most mature) |
| **English** | ✗ **NOT in `LC5_SUBJECTS` tuple; flat-dir layout breaks `_scan_subject`** | ✓ | ✓ | ✗ **MISSING all 5 lc5 asset defs** | ✓ (drift) | 8 PDFs (flat) | **PARTIAL** — small fix |
| **Computer Science** | ✓ | ✓ | ✓ | ✓ | ✓ (drift) | 11 PDFs | **HEALTHY** |

### Existing gaps to close

1. **English lc5 wiring** — extend `dlt/filesystem/leaving_cert_source.py:48`
   (add `"english"` to `LC5_SUBJECTS`) + add a 3rd branch to `_scan_subject`
   for the flat layout + extend the asset factory at `lc5_assets.py:154`
   to emit 5 more assets.
2. **Two parallel BAML function sets** for the same 3 LC doc kinds — fold the
   `baml/education/pdfs/*` legacy set into `baml/education/lc_extraction/*`.
3. **Two parallel DLT source families** for the same 8 subjects — migrate
   the 8 `subjects/<s>/sources.py` files to call the canonical BAML fn names.
4. **6 CocoIndex subject flows are R4-non-conformant** — they yield dicts
   manually instead of using `lancedb.mount_table_target`. `root_pdfs_embedding.py`
   is the canonical template to copy.
5. **No `gov.ie` education circulars DLT source** — `baml/processing/circular_extraction.baml`
   exists but no DLT source + no Dagster asset wires it. **Genuine new work.**
6. **`dlt/british_isles/ireland/education/curriculum.py` (972 LOC) vs
   `curriculum_source.py` (972 LOC)** — byte-for-byte identical size; likely an
   exact duplicate.
7. **Stubs to delete**: `dlt/british_isles/ireland/education/exam_source_update.py`
   (0 bytes), `oide_{all_subjects,subject,gaeilge}.py` (36-54 LOC),
   `british_isles/{jersey,guernsey,isle_of_man}/education/*.py` (1-2 KB stubs).

### British Isles cross-nation scaffolding already in place

- `baml/education/cross_nation/multi_nation_curriculum.baml` already defines
  `Nation` (IE/EN/SC/WA/NI/IM), `NationEducationLevel` (~24 levels),
  `QualificationBoard` (SEC/NCCA/AQA/Edexcel/OCR/SQA/WJEC/CCEA),
  `CrossNationCurriculumSpec`, `ExtractCrossNationSpec`, `AlignOutcomes`,
  `CompareCurricula`, `MapLevelEquivalence`, `TranslateEducationalContent`.
- `dlt/british_isles/{england,scotland,wales,northern_ireland}/education/` —
  5-8 partial sources per nation; none wired to a `defs.yaml`.
- Crown Dependencies (Jersey/Guernsey/IoM) are 1-2 KB stubs.

---

## 5. Health Score — Before & After

| Surface | Before (2026-07-06) | After both changes |
|---|--:|--:|
| Skills | 58 (≈14 healthy, ≈20 drift, ≈24 vendor kept) | **~58 v4-aligned** + British-Isles context |
| OpenSpec specs | 56 (20 healthy, 30 drift, 2 phantom) | **~30 canonical, no drift** |
| OpenSpec pending changes | 66 (22 active, 30 ARCHIVE) | **~25 active, all v4-aligned** |
| Notebooks | 91 (3 healthy, 25 dead, 50 drift, 13 hardcoded paths) | **91 marimo, ~85% on-pattern** |
| LC pipelines for 6 subjects | 5 healthy + 1 missing (English) | **6 healthy, all consolidated, all v1-conformant** |
| gov.ie circulars | No DLT source | **New DLT + BAML + Dagster + Dive** |
| MotherDuck Dives | 0 for syllabus/exam | **4 new Dives (topics, difficulty, marking, circulars)** |