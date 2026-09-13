# Change: `cianchosaint-handoff-v1` — Sister-repo handoff & cianfhoghlaim focus

> **Original user question (verbatim, 2026-08-28):**
> *"can you use ccc to compare what we have already moved from cianfhoghlaim to our other sister repositories like tuatha and bonneagar and ciandlithe and cianchosaint and gemini_hackathon and identify how best to ensure that we can refactor cianfhoghlaim now to focus on its priorities but make sure nothing is lost useful to the other repositories."*

> **Author:** cianfhoghlaim build-agent
> **Verified-by:** filesystem inventory on 2026-09-12 (post the `2026-08-24-wave-*` cascade)
> **Companion plan:** `openspec/plans/2026-08-24-dlt-deep-analysis-v2.md` §Phase 2.2 (sister-repo carveout)
> **Wave boundary respected:** this change is **ADDED** to the canonical surface; it does NOT modify any existing openspec spec deltas (per `centralize-cross-cutting-docs`).

## Why

Cianfhoghlaim today is **104 GB**, **41,610 files**, **505,785 ccc-indexed chunks**, with **1,994 .py files under `dlt_sources/`**, **333 .baml files**, **213 YAML + 77 .py under `orchestration/defs/`**, **88 marimo notebooks**, **95 Docker Compose stacks under `bonneagar/stacks/`**, **14 web apps**, and **102 openspec specs**. The platform has grown to absorb:

- The full **British-Isles Education Pipeline** (BIEP — 6 LC subjects + gov.ie circulars + 7 CocoIndex flows + 42 Dagster assets + 6 marimo notebooks + 4 MotherDuck Dives + daily Flight — per `british-isles-education-pipeline`)
- The **CIANCHEILTIS** Celtic bilingual umbrella (PR0.1–0.9 already landed — `2026-09-06-ciancheiltis-v1`)
- The **CIANCHOSAINT** defence/policing/intelligence-oversight fork (genuinely living in `~/dev/cianchosaint/` with 246 dlt_sources .py files + 13 openspec changes + 33 specs)
- The **CIANDLITHE** visual/digital-art sister (8 web apps for coroner/health/legal)
- The **GEMINI HACKATHON** Google Cloud demo (Cloud Run deploy, BAML extracts, gradio UI)
- The **TUATHA** BI Educational MMO + 8 NCCA subject agents (existing at both `agents/tuatha/` and the standalone `~/dev/tuatha/`)

Refactoring cianfhoghlaim now requires a **verified inventory** (NOT docs/claims per the trust-gap memory `kcg-fabricated-openspec-archive-biep-v3`) of:

1. **What is canonically cianfhoghlaim** — the LC/JC/British-Isles education platform hub. Must stay.
2. **What is owned by each sister repo** — already moved, must not regress.
3. **What is shared-stack** — the 4-tier model provider chain + BAML + CocoIndex + LanceDB + DuckLake + Dagster patterns that must stay synchronized across forks.

This change records the verified inventory (filesystem-proven, not claimed) and defines two new openspec specs that codify (a) the cianfhoghlaim canonical surface and (b) the shared-stack interface that all sister repos must satisfy.

## What changes

### 1. New umbrella spec `sister-shared` (the shared-stack contract)

Adds `openspec/specs/sister-shared/spec.md` as the canonical contract that every sister repo must satisfy. **5 Requirements** covering:

- **Shared-1 — 4-tier ModelProviderRouter**: every sister repo's `baml_src/clients.baml` MUST declare exactly 3 named clients (`Primary`, `Fallback`, `Emergency`) routed through a `baml_src/_shared/provider_router.py` (or sister-local equivalent). CVerified: cianchosaint already has this (`clients.baml` lines 24-65) — cianfhoghlaim has `clients.baml` with named clients but **without** the `_shared/provider_router.py` module. **Gap to close**: cianfhoghlaim must add `baml_src/_shared/provider_router.py` before archive.
- **Shared-2 — JurisdictionPipelineBase wholesale-copy**: every sister repo's `dlt_sources/{sister}_cross/jurisdiction_pipeline_base.py` MUST be a wholesale copy of the canonical cianfhoghlaim version (`dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py`), with sister-local cohort extensions appended. **CVerified**: cianchosaint has it at `dlt_sources/_cross/jurisdiction_pipeline_base.py` (60 lines vs cianfhoghlaim's 34) with 8 cohort extensions for `law_enforcement/{england,guernsey,ireland,isle_of_man,jersey,northern_ireland,scotland}`. ciandlithe has it at `dlt_sources/_cross/jurisdiction_pipeline_base.py` (alongside `5_stage_registry.py` + `5_stage_runner.py` + `connection.py` + `legal_registry.py` + `registry_api.py` + `registry_loader.py`).
- **Shared-3 — cocoindex_flows/_shared wholesale-copy**: every sister repo's `cocoindex_flows/_shared/` MUST contain `_lifespan.py` + `cli.py` + `cocoindex_query_api.py` + `languages.py` + `repo_embedding.py` + `repo_type_detector.py` + `reranker.py` (the 7 canonical modules). **CVerified**: cianfhoghlaim has all 7 (plus `caighdean_standardize.py` which is a Celtic-language addition); cianchosaint has 6 (missing `caighdean_standardize.py` — correct, cianchosaint is not a Celtic pipeline); ciancheiltis inherits via the canonical dlt path.
- **Shared-4 — openspec workflow**: every sister repo MUST have `openspec/AGENTS.md` + `openspec/changes/` + `openspec/specs/` matching the cianfhoghlaim 6-file change-bundle convention. **CVerified**: cianfhoghlaim (336-line `openspec/AGENTS.md` + 102 specs + 346 archived + 38 pending), cianchosaint (~13 changes + 24 archived + 33 specs), ciancheiltis (1 change + 2 specs), ciandlithe (8 changes + 8 specs), tuatha (separate openspec at `tuatha/openspec/`), gemini_hackathon (separate openspec at `gemini_hackathon/openspec/`).
- **Shared-5 — bonneagar/stacks/ intersection**: every sister repo that ships its own IaC MUST carry the canonical 6-file GOLD_STANDARD pattern (`compose.yaml` + `sidecar.yaml` + `secrets.env` + `pangolin.yaml` + `blueprint.yaml` + `.env.example`). **CVerified**: cianfhoghlaim `bonneagar/stacks/litellm/` has all 6; cianchosaint `bonneagar/stacks/litellm/` has all 6 with an explicit `# CIANCHOSAINT wholesale-copy of cianfhoghlaim/cianfhoghlaim @ main branch. Migrated to cianchosaint: 2026-08-23` header at the top of `config/config.yaml`.

### 2. New umbrella spec `cianfhoghlaim` (the canonical surface)

Adds `openspec/specs/cianfhoghlaim/spec.md` codifying the canonical BIEP-hub surface. **4 Requirements** covering:

- **Canonical-1 — British-Isles Education Pipeline (BIEP)** stays in cianfhoghlaim: the 6 LC subjects (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science) + gov.ie circulars + the 7 CocoIndex flows under `cocoindex_flows/british_isles/{england,guernsey,ireland,isle_of_man,jersey,northern_ireland,scotland,wales}` + the 42 Dagster assets under `orchestration/defs/2_materials/{ireland_education, england_education, scotland_education, wales_education, guernsey_education, jersey_education, isle_of_man_education, northern_ireland_education, biiep_v3}` + the 6 marimo notebooks at `notebooks/10_biep_pipeline_lakehouse_*` + the 4 MotherDuck Dives at `motherduck/dives/bci*_dive.py` + the daily Flight at `motherduck/flights/british_isles_daily_sync_flight.py`. **CVerified**: all paths exist (see "Inventory" section below).
- **Canonical-2 — CIANCHEILTIS bilingual alignment** stays in cianfhoghlaim as the umbrella marker `ciancheiltis/` (with its carved-out sibling at `~/dev/ciancheiltis/`): 6 CocoIndex flows under `cocoindex_flows/british_isles/uk/{ciancheiltis_en_cy_embedding, ciancheiltis_en_ga_roi_embedding, ciancheiltis_en_ga_ni_embedding, ciancheiltis_en_gd_embedding, ciancheiltis_en_gv_embedding, ciancheiltis_en_ga_eu_embedding}.py` + 6 marimo notebooks + 6 MotherDuck Dives + 6 daily Flights (per `2026-09-06-ciancheiltis-v1` change). **CVerified**: all 6 ciancheiltis files exist in `cocoindex_flows/british_isles/uk/`; all 6 Dives exist (`ciancheiltis_en_cy_dive.py` … `ciancheiltis_en_ga_eu_dive.py`); all 6 Flights exist (`ciancheiltis_en_cy_flight.py` … `ciancheiltis_en_ga_eu_flight.py`).
- **Canonical-3 — Tuatha BI Educational MMO + 8 NCCA subject agents** stays in cianfhoghlaim as `agents/tuatha/{math_agent, chem_agent, geog_agent, engl_agent, gael_agent, hist_agent, appm_agent, comp_agent}.py` (8 NCCA subjects × 6 BAML contracts per `2026-08-25-tuatha-british-isles-mmo-consolidation-v1`). **CVerified**: 8 subject files exist under `agents/tuatha/` + 14 `agents/tuatha/tools/{<sub>_*}.py` files + `agents/tuatha/agents/{orchestrator, cross_subject_agent, cianfhoghlaim_operator}.py`. **Standalone `~/dev/tuatha/` is NOT canonical** — it is a phase-1 experiment and will be superseded by the in-platform tuatha once the Wave-2 cascade lands.
- **Canonical-4 — Bonneagar IaC subdirectory** stays in cianfhoghlaim as `bonneagar/` (95 Docker Compose stacks + Komodo resource-syncs + Pangolin + Infisical clients — per the `2026-06-29-bonneagar-iac-merge-komodo-pangolin-infisical` change). **CVerified**: `bonneagar/stacks/` has 95 entries; `bonneagar/iac/`, `bonneagar/komodo/`, `bonneagar/pangolin/`, `bonneagar/blueprints/`, `bonneagar/dagger/`, `bonneagar/deploy-runbooks/` exist. The standalone `~/repos/bonneagar/` (with `.git_disabled`) is **NOT canonical** — it is an experimental carveout that was disabled per the recent `242c0e9c9 docs(openspec): record the bonneagar carveout as superseded by the mirror model` commit.

### 3. New openspec change bundle (`./`)

This change directory itself is **the artefact** — no code is added; the change is documentation + spec.

- `proposal.md` (this file)
- `tasks.md` (concrete per-asset actions, with REAL verification commands)
- `specs/cianfhoghlaim/spec.md` ADDED delta (4 Requirements — the canonical surface)
- `specs/sister-shared/spec.md` ADDED delta (5 Requirements — the shared-stack contract)

### 4. Sister-repo drift discovered (catalogued for follow-up openspec changes)

The inventory revealed **7 distinct drifts** that warrant their own openspec changes:

1. **`baml_src/_shared/provider_router.py` missing in cianfhoghlaim** (vs cianchosaint) → requires `2026-09-XX-shared-provider-router-bridge-v1`.
2. **`orchestration/defs/__init__.py` missing in cianchosaint** (only 1 sensor file present) → requires `2026-09-XX-cianchosaint-orchestration-init-v1` to mirror the cianfhoghlaim 5-layer defs shape.
3. **`import dlt_sources` instead of `import dlt`** in 3 cianfhoghlaim files (`orchestration/defs/2_materials/eu_multilingual/{english,irish}_coverage_monitor.py` + `language_alignment_mapper.py`) → already tracked by `2026-08-24-wave-1-dlt-sources-domain-restructure-v1`, but the trust-gap memory claims the wave did not fully land (verified: the 3 broken files still exist).
4. **`agents/cianchosaint/` does not exist in cianfhoghlaim** — the 8-tuatha agents are integrated into `agents/tuatha/`, but the cianchosaint-specific 7 agents (ga_root_agent, met_root_agent, psni_root_agent, self_improvement_agent + 3 specialist subgroups) live ONLY in the sister repo. **Decision**: keep them there (Canonical-3 says tuatha stays in cianfhoghlaim; cianchosaint agents are sister-owned).
5. **`web/apps/ciafagent-*`** (9 apps in cianchosaint) vs `web/apps/_oideachais_apps/`, `web/apps/cianfhoghlaim-{leaving-cert,mmo,web}`, `web/apps/tuatha-{ui,demo}`, `web/apps/{biiep-agent, croilar-web, croilar-portal, game_showcase}` (14 apps in cianfhoghlaim) — no overlap, no drift.
6. **`baml_src/baml_client/`** does NOT exist in cianfhoghlaim's working tree (the `baml-py>=0.222.0` package generates it on `baml-cli generate` — verified by `find /Users/cianmacandeisigh/dev/cianfhoghlaim -name "baml_client" -type d` returning only worktree + stedding copies, no top-level package). The trust-gap memory's claim about a missing `__init__.py` is **moot** because the directory itself is generated, not committed. Verified.
7. **`stedding/` content** — cianfhoghlaim's `stedding/` is 7 GB+ of uncommitted scratch + corpora + notebooks + test outputs (the BIEP "lakehouse" sandbox); cianchosaint's `stedding/` is 3 small JSON files (`gaffer_graph.json` + `sync-reports/` + `trl-assessments/`). **Decision**: stedding is local cache, NEVER canonical; do not lift it.

## Inventory (filesystem-verified, 2026-09-12)

### Cianfhoghlaim — `/Users/cianmacandeisigh/dev/cianfhoghlaim/` (104 GB, 41,610 indexed files)

| Surface | Path | Verified count | Owner |
|:--|:--|--:|:--|
| BIEP DLT sources | `dlt_sources/british_isles/{england,guernsey,ireland,isle_of_man,jersey,northern_ireland,scotland,wales}/{education,law,medicine,statistics,university,ncca_root_pdfs.py}` | (subset of 1,994) | **CANONICAL** (Canonical-1) |
| BAML schemas | `baml_src/{british_isles,celtic,american_nations,commonwealth,european_nations,european_union,processing,shared}/` | 333 .baml + 42 .py | **CANONICAL** + **Shared-1** (clients.baml) |
| CocoIndex flows | `cocoindex_flows/{british_isles,education,subjects,celtic,commonwealth,american_nations,european_nations,european_union,knowledge_graph,media,infrastructure,cultural_heritage,cv,vernacular,portfolio}/` | 120 .py | **CANONICAL** + **Shared-3** (`_shared`) |
| Dagster orchestration | `orchestration/defs/{1_ingestion,2_materials,3_model_lifecycle,4_asset_generation,4_budget,4_memory,5_agent_ops}/` + `orchestration/sensors/` + `orchestration/components/` | 213 .yaml + 77 .py + 14 sensors + 11 components | **CANONICAL** |
| NCCA + Education agents | `agents/adk/{lc_subject_agent,jc_subject_agent,alevel_subject_agent,gcse_subject_agent,subjects/lc/{mathematics,chemistry,geography,gaeilge,english,physics,biology,applied_mathematics}.py, agui_curriculum_agent, curriculum_agent, ...}` | 30 .py | **CANONICAL** |
| Tuatha BI Educational MMO agents | `agents/tuatha/{math_agent,chem_agent,geog_agent,engl_agent,gael_agent,hist_agent,appm_agent,comp_agent,subject_router}.py` + `agents/tuatha/agents/{orchestrator,cross_subject_agent,cianfhoghlaim_operator}.py` + 14 `agents/tuatha/tools/{sub}_*.py` | ~35 .py | **CANONICAL** (Canonical-3) |
| Meaisínfhoghlaim OCR/HTR | `meaisinfhoghlaim/{ocr/ensemble, ocr/models (24 OCR models), alignment, evaluation, training, backends, certificate, datasets, process, quality, federated, document_factory}/` | (full stack) | **CANONICAL** + **Shared** (via `agents/meaisinfhoghlaim/firecrawl_mcp` wholesale-copied to cianchosaint + ciandlithe) |
| marimo notebooks | `notebooks/00_*.py` + `notebooks/01_corpus/...` + `notebooks/10_biep_pipeline_lakehouse_*.py` (BIEP) + `notebooks/13_official_media_*.py` + ciancheiltis notebooks | 88 .py | **CANONICAL** |
| MotherDuck Dives + Flights | `motherduck/dives/` (BIEP + ciancheiltis + sub-nations +) + `motherduck/flights/` | (multiple) | **CANONICAL** |
| Web apps | `web/apps/{cianfhoghlaim-web, cianfhoghlaim-leaving-cert, cianfhoghlaim-mmo, biiep-agent, oideachais, oideachais-dashboard, tuatha-ui, tuatha-demo, croilar-portal, croilar-web, game_showcase, _oideachais_apps}/` | 14 apps | **CANONICAL** |
| Bonneagar IaC | `bonneagar/{stacks (95), iac, komodo, pangolin, blueprints, dagger, deploy-runbooks, locket-shim}/` | 95 stacks | **CANONICAL** (Canonical-4) |
| Observability | `observability/{agent_tracing, env_config, fastapi_middleware, langfuse_config, logfire_config, logging, mlflow_config, ocr, platform_tracer, ragas_evaluator, unified_tracer}.py` | 13 modules | **CANONICAL** |
| OpenSpec | `openspec/{AGENTS.md (336 lines), changes (38 pending), changes/archive (346), specs (102)}` | full openspec workflow | **CANONICAL** |
| Local leaves | `ciancheiltis/` (sister marker), `leaving_certificate/` (corpus), `data/`, `stedding/`, `cloud/terraform/`, `sruth/`, `ai-that-works/` | — | **CANONICAL** (local) |

### Cianchosaint — `/Users/cianmacandeisigh/dev/cianchosaint/` (1.5 GB, sister repo, `github.com/cianfhoghlaim/cianchosaint.git`)

| Surface | Path | Verified count | Owner |
|:--|:--|--:|:--|
| Defence/policing DLT sources | `dlt_sources/law_enforcement/{england,guernsey,ireland,isle_of_man,jersey,northern_ireland,scotland,wales}/{AGENTS.md,_factory.py}` + `dlt_sources/cianchosaint/{uk/{bailo,cyberchef,gaffer,government,intelligence_agencies,intelligence_oversight,military,policing,stroom}, ireland/{defence_forces,law}, bipp_v2, common, crown_dependencies, funders, historical_associations, ni, political_parties, politicians, uk, wikipedia_archives}` | 246 .py (all of dlt_sources) | **SISTER-OWNED** (cianchosaint owns defence/policing/intel) |
| BAML schemas | `baml_src/cianchosaint/{ireland,political_parties,politics,processing}/` + `baml_src/_shared/{provider_router,langfuse_client,ragas_evaluator,bailo_integration,gaffer_integration,langfuse_prompt_resolver}.py + gemini_deep_research.baml + provider_router_config.yaml + templates/` | 36 .baml + 9 .py | **SISTER-OWNED** |
| CocoIndex flows | `cocoindex_flows/cianchosaint/{_factory,ireland,source_policy_aggregator,vlm_pipeline_aggregator}.py` + `_shared/` (6 of 7 — missing `caighdean_standardize.py`, correct) | (sister stack) | **SISTER-OWNED** + **Shared-3** |
| Orchestration | `orchestration/defs/licence_enforcement_sensor.py` (1 sensor, NO `__init__.py` — drift #2) | 1 .py | **SISTER-OWNED** + **DRIFT** |
| Agents | `agents/cianchosaint/{ga_root_agent,met_root_agent,psni_root_agent,self_improvement_agent,_base,ga_specialists,met_specialists,psni_specialists}.py` + `agents/adk/{celtic_tutor_agent,curriculum_comparison_agent,litellm_agent,tuatha_root_agent,agent_registry,config}.py` + `agents/meaisinfhoghlaim/firecrawl_mcp/` (wholesale copy) | 14+ .py | **SISTER-OWNED** |
| Bonneagar stacks (subset) | `bonneagar/stacks/{bailo,changedetection,crawl4ai,gaffer,infisical,komodo,lakehouse,langfuse,litellm,locket,motherduck,openchamber,pangolin,stagehand,unsloth-serve}/` | 15 stacks | **SISTER-OWNED** + **Shared-5** (litellm config.yaml carries `# CIANCHOSAINT wholesale-copy of cianfhoghlaim/cianfhoghlaim @ main branch. Migrated to cianchosaint: 2026-08-23` header) |
| Web apps | `web/apps/{ciafagent-api, ciafagent-cyberchef, ciafagent-ga-internal, ciafagent-ga-public, ciafagent-met-internal, ciafagent-met-public, ciafagent-psni-internal, ciafagent-psni-public, ciafagent-self-host}/` | 9 ciafagent apps | **SISTER-OWNED** |
| OpenSpec | `openspec/{AGENTS.md (with TRL section), changes (13), changes/archive (24), specs (~33)}` | 13 + 24 + 33 | **SISTER-OWNED** + **Shared-4** |
| HMGCC reference | `hmgcc/Eligibility of technology readiness levels (TRL).md` | 1 ref doc | **SISTER-OWNED** |

### Ciancheiltis — `/Users/cianmacandeisigh/dev/ciancheiltis/` (1 MB, sister repo, `github.com/cianfhoghlaim/ciancheiltis.git`)

| Surface | Path | Verified count | Owner |
|:--|:--|--:|:--|
| DLT sources | `dlt_sources/{cultural_heritage,language,lexicographic,common,_cross,_shared}/` | (subset) | **SISTER-OWNED** + **Shared-2** |
| Meaisínfhoghlaim models | `meaisinfhoghlaim/models/src/` | (sister stack) | **SISTER-OWNED** |
| Context (Irish) | `context/gaeilge/` | (corpus) | **SISTER-OWNED** |
| Observability | `observability/{__init__,logging}.py` | 2 modules | **SISTER-OWNED** (lean version) |
| OpenSpec | `openspec/{changes (1), changes/archive, specs (2: adk-deep-research-control-plane, ciancheiltis-dlt-sources-split)}` | 1 + 0 + 2 | **SISTER-OWNED** + **Shared-4** |
| **NOT present** | (NO `baml_src/`, `cocoindex_flows/`, `orchestration/`, `web/`, `notebooks/`, `bonneagar/`, `motherduck/`) | — | (deliberately lean per the ciancheiltis carveout — sister owns the Celtic-language content, not the platform patterns) |

### Ciandlithe — `/Users/cianmacandeisigh/dev/ciandlithe/` (1.9 GB, sister repo)

| Surface | Path | Verified count | Owner |
|:--|:--|--:|:--|
| DLT sources | `dlt_sources/{ciandlithe,crown_dependencies,england,ireland,northern_ireland,scotland,uk,wales,common,_cross,law}/` | (subset of 1,994 ÷) | **SISTER-OWNED** (visual/digital-art + coroner/health/legal slice) |
| BAML schemas | `baml_src/ciandlithe/{case_studies,corpus,courts,ireland,medicine,processing}/` | (subset) | **SISTER-OWNED** |
| CocoIndex flows | `cocoindex_flows/{ciandlithe,infrastructure,_shared}/` | (subset) | **SISTER-OWNED** + **Shared-3** |
| **EMPTY dirs** | `orchestration/` (0 files), `motherduck/` (0 files), `notebooks/` (0 files), `mise-tasks/` (0 files), `templates/` (0 files) | — | **DRIFT** (ciandlithe ships no orchestration; deliberately lean) |
| Web apps | `web/apps/{ciandlithe-coroner, ciandlithe-health-complain, ciandlithe-inquest, ciandlithe-legal-aid, ciandlithe-piab, ciandlithe-self-rep, ciandlithe-wrc}/` | 7 apps | **SISTER-OWNED** |
| Bonneagar stacks (subset) | `bonneagar/{iac, komodo, pangolin, stacks}/` | (subset) | **SISTER-OWNED** + **Shared-5** |
| OpenSpec | `openspec/{changes (8: ciandlithe-{repo-foundation,toolchain-repair,bipp-v2-crossref,blig-v1-spec,langfuse-prompt-mirror,leabharlann-corpus-ingest,ragas-eval}+ 2026-08-24-ciandlithe-init), changes/archive, specs (8)}` | 8 + 0 + 8 | **SISTER-OWNED** + **Shared-4** |

### Gemini Hackathon — `/Users/cianmacandeisigh/dev/gemini_hackathon/` (5.1 GB, sister repo)

| Surface | Path | Verified count | Owner |
|:--|:--|--:|:--|
| BAML extracts (NOT baml_src) | `baml_extracts/` is the real directory; `baml_src` is a **symlink** → `baml_extracts` (verified: `baml_src -> baml_extracts`) | 10+ .baml + 9 .py | **SISTER-OWNED** (different layout — extract-style, not schema-style) |
| CocoIndex flows | `cocoindex_flows/{_factory,_shared,education (1 file: lc6_extraction_app.py), equivalency, ireland, pdf, uk_ncce}/` | (subset) | **SISTER-OWNED** |
| DLT pipelines (NOT dlt_sources) | `dlt_pipelines/{_base,_shared.py,_subject_base.py,corpus_downloader.py,ireland/,official_doc_fetcher.py,pdf_downloader.py,pdf_page_metadata.py}/` | (subset) | **SISTER-OWNED** (different layout — pipeline-style, not source-style) |
| Orchestration | `orchestration/defs/{3_model_lifecycle}/` (only 1 layer) | (subset) | **SISTER-OWNED** (lean) |
| Python package | `gemini_hackathon/` (29+ submodules: agents, assets, backend.py, certificate, journey, knowledge_graph, ledger, memory, model_registry.py, models, observability.py, ocr.py, ocr_ensemble.py, progression, secrets_loader.py, session, sources.py, subnations.py, syllabus, theming.py) | 29+ | **SISTER-OWNED** |
| Backend (FastAPI) | `gemini_hackathon_backend/{main.py, agents/, catalog/, lakehouse/, observability.py, pyproject.toml, tests/}/` | (subset) | **SISTER-OWNED** |
| Gradio UI | `gemini_hackathon_gradio/` | (subset) | **SISTER-OWNED** |
| **NO** `agents/`, **NO** `bonneagar/`, **NO** `_shared/` providers | (different layout — Cloud Run deploy target, not platform hub) | — | (deliberate — gemini_hackathon is a Google Cloud demo, not a platform sister) |

### Tuatha — `/Users/cianmacandeisigh/dev/tuatha/` (1.7 GB, sister repo, 27 commits, MIT-licensed, last commit 2026-09-12)

| Surface | Path | Verified count | Owner |
|:--|:--|--:|:--|
| Python package | `tuatha/` (the package) + `sources/` (the rung-1 ingest layer) + `data/lancedb/` | (full standalone) | **SISTER-OWNED** (standalone MIT-licensed) |
| DLT | `tuatha/dlt/{formative_item, marking_scheme, past_paper, response_score, syllabus, _shared, per_subject.py}/` | (subset) | **SISTER-OWNED** |
| BAML | `tuatha/baml/{adaptive_tutor, anam_capture, anam_xmen, clients, equivalency_generator, gemini_deep_research, marking_grader, media_descriptor, qpack_accounting}.baml` | 9 .baml | **SISTER-OWNED** |
| CocoIndex | `tuatha/cocoindex/{anam, cross_subject, hackathon, media_intel, per_subject}.py` | 5 .py | **SISTER-OWNED** |
| Dagster | `tuatha/dagster/{anam, anam_observability, anchor_assets, educational, hackathon, media_intel, observation, per_subject}.py` | 8 .py | **SISTER-OWNED** |
| Agents | `tuatha/agents/{adk, api, educational, hackathon, media_intel}/` | (subset) | **SISTER-OWNED** |
| Asset generation | `tuatha/asset_generation/{fibo, image_gen, invoke, vlm}/` | (subset) | **SISTER-OWNED** |
| **Standalone** — separate from cianfhoghlaim's in-platform `agents/tuatha/` | — | — | (Phase-1 experiment; will be superseded by in-platform tuatha once Wave-2 cascade lands — Canonical-3) |

### Bonneagar — `/Users/cianmacandeisigh/repos/bonneagar/` (2.4 GB, **NOT a git repo** — `.git_disabled`)

| Surface | Path | Verified count | Owner |
|:--|:--|--:|:--|
| Disabled standalone carveout | `compose/`, `ansible/`, `mcp/`, `scraping/`, `scripts/`, `docs/`, `pulumi/`, `tutorials/`, `mise.toml`, `pyproject.toml`, `package.json`, `bun.lock`, `README`, `AGENTS.md`, `openspec/` | (subset) | **NOT CANONICAL** — superseded by `cianfhoghlaim/bonneagar/` per the `2026-06-29-bonneagar-iac-merge-komodo-pangolin-infisical` archived change + the recent `242c0e9c9 docs(openspec): record the bonneagar carveout as superseded by the mirror model` commit |

## 3-bucket categorization summary

### Bucket (a) — Stays in cianfhoghlaim (CANONICAL)
1. **BIEP — the British-Isles Education Pipeline** (6 LC subjects + gov.ie circulars + 7 CocoIndex flows + 42 Dagster assets + 6 marimo + 4 MotherDuck Dives + daily Flight).
2. **CIANCHEILTIS — the Celtic bilingual umbrella** (the `ciancheiltis/` sister marker + 6 CocoIndex flows + 6 marimo + 6 MotherDuck Dives + 6 daily Flights per `2026-09-06-ciancheiltis-v1`).
3. **TUATHA — BI Educational MMO + 8 NCCA subject agents** (the in-platform `agents/tuatha/` not the standalone `~/dev/tuatha/`).
4. **Bonneagar — IaC subdirectory** (`bonneagar/` — 95 stacks + Komodo + Pangolin + Infisical clients).
5. **Meaisínfhoghlaim — OCR/HTR/alignment/training** (`meaisinfhoghlaim/ocr/`, `meaisinfhoghlaim/alignment/`, etc.).
6. **14 web apps** under `web/apps/` (excluding ciafagent-*).
7. **The 102 openspec specs** (the canonical openspec surface).

### Bucket (b) — Owned by sister repos (DO NOT regress)
1. **Cianchosaint** owns: defence/policing/intelligence-oversight DLT (`dlt_sources/law_enforcement/*` + `dlt_sources/cianchosaint/*`), 4-tier BAML provider chain with Unsloth Studio primary, 9 ciafagent-* web apps, 33 openspec specs.
2. **Ciancheiltis** owns: Celtic-language DLT (`dlt_sources/cultural_heritage/`, `language/`, `lexicographic/`), Irish context (`context/gaeilge/`), `meaisinfhoghlaim/models/src/`, 1 openspec change + 2 specs.
3. **Ciandlithe** owns: visual/digital-art + coroner/health/legal DLT (`dlt_sources/ciandlithe/`), 7 ciandlithe-* web apps, 8 openspec specs.
4. **Gemini Hackathon** owns: Google Cloud deploy + BAML extracts + Gradio UI + FastAPI backend + the `baml_extracts/` symlink layout + `dlt_pipelines/` (different from cianfhoghlaim's `dlt_sources/`).
5. **Tuatha** (standalone) owns: phase-1 MMO experiment with its own `tuatha/` Python package + `sources/` Ireland-first rung-1 layer (27 commits, MIT-licensed).
6. **Bonneagar** (`~/repos/bonneagar/`) is **NOT canonical** — the standalone carveout is disabled (`.git_disabled`) and superseded by `cianfhoghlaim/bonneagar/` per the `2026-06-29-bonneagar-iac-merge` archive.

### Bucket (c) — Shared stack (must stay synchronized)
1. **4-tier ModelProviderRouter pattern** — every sister repo's `baml_src/clients.baml` MUST declare `Primary` / `Fallback` / `Emergency` clients routed through `_shared/provider_router.py`. (Verified: cianchosaint has it; **cianfhoghlaim lacks `_shared/provider_router.py`** — gap to close before archive.)
2. **`dlt_sources/_cross/jurisdiction_pipeline_base.py`** — wholesale-copy from cianfhoghlaim to every sister repo (cianchosaint has 60 lines vs cianfhoghlaim's 34; ciancheiltis has it).
3. **`cocoindex_flows/_shared/`** — the 7 canonical modules (`_lifespan.py`, `cli.py`, `cocoindex_query_api.py`, `languages.py`, `repo_embedding.py`, `repo_type_detector.py`, `reranker.py`) must be wholesale-copied. (Verified: cianfhoghlaim has 7 + Celtic extra `caighdean_standardize.py`; cianchosaint has 6.)
4. **OpenSpec 6-file change bundle** — every sister repo must have `openspec/AGENTS.md` + `openspec/changes/` + `openspec/specs/` matching the cianfhoghlaim convention.
5. **Bonneagar 6-file GOLD_STANDARD pattern** — every sister repo that ships IaC must carry `compose.yaml` + `sidecar.yaml` + `secrets.env` + `pangolin.yaml` + `blueprint.yaml` + `.env.example`.

## Refactor guidance for cianfhoghlaim

Per the user question, the **focus** for cianfhoghlaim refactor is:

1. **Wave 0–8 cascade** (per `openspec/plans/2026-08-24-dlt-deep-analysis-v2.md`) — repair the 5 inert layers per the trust-gap memory (`kcg-runtime-inert-layers`): local `cocoindex/` shadowing PyPI, `orchestration/defs/__init__.py` missing, `baml_client/` generation, `import dlt_sources` replacing `import dlt`, OCR ensemble wiring.
2. **Close the `_shared/provider_router.py` gap** (Shared-1) so cianfhoghlaim matches the cianchosaint 4-tier pattern.
3. **Defensive: do NOT delete the in-platform `agents/tuatha/`** — that is the canonical BI Educational MMO (Canonical-3), not the standalone `~/dev/tuatha/` (which is a phase-1 experiment).
4. **Defensive: do NOT delete `bonneagar/`** — it is the canonical IaC (Canonical-4), not the standalone `~/repos/bonneagar/` (which is disabled).
5. **Add `_shared/caighdean_standardize.py` to cianchosaint's `cocoindex_flows/_shared/` only if cianchosaint ever ingests Celtic-language content** — currently it does not, so the missing module is correct (Shared-3).
6. **Add `orchestration/defs/__init__.py` to cianchosaint** so its Dagster code-location can load (drift #2).

## Impact

- **Audience**: every agent + human working on cianfhoghlaim + every sister-repo maintainer.
- **Scope**: cianfhoghlaim only (this openspec change). Sister-repo deltas are tracked in their own repos.
- **Risk**: low — this change ONLY adds spec documentation. No existing code is touched.
- **Reversibility**: full — every file added is additive; deletion reverts cleanly.
- **Affected specs**: 2 NEW specs (`openspec/specs/cianfhoghlaim/spec.md` + `openspec/specs/sister-shared/spec.md`).
- **Affected skills**: openspec (per-sister-repo sync conventions).

## Dependencies

```yaml
Blocked by:        none
Blocked by (soft): 2026-08-24-wave-2-orchestration-vertical-pipelines-v1
                    2026-08-24-wave-4-ducklake-v1-hardening-v1
                    2026-08-24-wave-7-observability-drift-cleanup-v1
                    2026-09-06-ciancheiltis-v1
Affected repos:    cianfhoghlaim (single-repo change; sister-repo drifts are documented but not in scope)
Push target:       origin/restore-from-979b9b4ff5 (current branch)
```

## Acceptance gates

- `openspec validate cianchosaint-handoff-v1 --strict` passes (the new specs SHALL/MUST + ≥1 Scenario per Requirement).
- The 7 sister-repo drifts in §4 are catalogued with proposed follow-up openspec change IDs.
- The 3-bucket categorization table in the proposal maps every verified filesystem path to exactly one bucket.

## Out of scope (follow-up changes)

1. **`2026-09-XX-shared-provider-router-bridge-v1`** — add `baml_src/_shared/provider_router.py` to cianfhoghlaim (Shared-1 gap).
2. **`2026-09-XX-cianchosaint-orchestration-init-v1`** — add `__init__.py` to `cianchosaint/orchestration/defs/` + import the `licence_enforcement_sensor` (drift #2).
3. **`2026-09-XX-tuatha-supersession-v1`** — explicitly mark the standalone `~/dev/tuatha/` as superseded by the in-platform `agents/tuatha/` once Wave-2 lands.
4. **`2026-09-XX-bonneagar-disable-confirmation-v1`** — document the `~/repos/bonneagar/.git_disabled` state in an openspec change (the recent `242c0e9c9 docs(openspec): record the bonneagar carveout as superseded by the mirror model` commit added the prose; an openspec change makes it archivable).
6. **`2026-09-XX-ciandlithe-orchestration-init-v1`** — populate `ciandlithe/orchestration/` with a 5-layer defs scaffold mirroring cianfhoghlaim (drift #4 in ciandlithe's empty dirs).
7. **`2026-09-XX-gemini-hackathon-sister-umbrella-v1`** — codify that gemini_hackathon is a deploy-target sister (not a platform sister) and document the `baml_extracts/` symlink + `dlt_pipelines/` (NOT `dlt_sources/`) divergence.

## Cross-references

- [`openspec/plans/2026-08-24-dlt-deep-analysis-v2.md`](../../plans/2026-08-24-dlt-deep-analysis-v2.md) — the v2 plan §Phase 2.2 (sister-repo carveout)
- [`2026-08-24-wave-0-cocoindex-module-path-repair-v1`](../2026-08-24-wave-0-cocoindex-module-path-repair-v1/proposal.md) — Wave 0 (local `cocoindex/` shadowing PyPI)
- [`2026-08-24-wave-1-dlt-sources-domain-restructure-v1`](../2026-08-24-wave-1-dlt-sources-domain-restructure-v1/proposal.md) — Wave 1 (`import dlt_sources` vs `import dlt`)
- [`2026-08-24-wave-2-orchestration-vertical-pipelines-v1`](../2026-08-24-wave-2-orchestration-vertical-pipelines-v1/proposal.md) — Wave 2 (`orchestration/defs/__init__.py`)
- [`2026-09-06-ciancheiltis-v1`](../2026-09-06-ciancheiltis-v1/proposal.md) — the ciancheiltis sister carveout precedent
- [`cianchosaint/AGENTS.md`](../../../../cianchosaint/AGENTS.md) — the sister repo's scope + BUSL-1.1 licence
- [`openspec/specs/knowledge-sync-loop/spec.md`](../../specs/knowledge-sync-loop/spec.md) — the 14-layer sync loop
- [`openspec/specs/centralized-model-registry/spec.md`](../../specs/centralized-model-registry/spec.md) — the canonical model registry driving the 4-tier router
- [`openspec/specs/centralized-schema-registry/spec.md`](../../specs/centralized-schema-registry/spec.md) — BAML is the single source of truth
- [`openspec/specs/infrastructure-stacks/spec.md`](../../specs/infrastructure-stacks/spec.md) — the 6-file GOLD_STANDARD pattern
- [`openspec/specs/dagster-5-layer-component-architecture/spec.md`](../../specs/dagster-5-layer-component-architecture/spec.md) — the 5-layer defs shape
- [`openspec/specs/british-isles-education-pipeline/spec.md`](../../specs/british-isles-education-pipeline/spec.md) — the BIEP umbrella
- [`openspec/specs/ciancheiltis/spec.md`](../../specs/ciancheiltis/spec.md) — the Celtic bilingual umbrella
- [`openspec/specs/cianfhoghlaim-educational-mmo/spec.md`](../../specs/cianfhoghlaim-educational-mmo/spec.md) — the 8 NCCA subject × per-subject quest packs × 8 ADK agents
- `~/.claude/plans/do-an-extensive-deep-snoopy-marshmallow.md` — the 20-plan refactor roadmap (Wave boundaries)