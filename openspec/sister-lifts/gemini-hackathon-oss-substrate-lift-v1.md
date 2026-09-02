# Sister-Repo Lift: `gemini-hackathon-oss-substrate-lift-v1`

> **One-line summary:** Lift the OSS-first substrate (NCCE
> learning_graph + equivalencies + certification.baml + the
> 7-stage certificate pipeline + the CocoIndex learning_graphs
> app) from cianfhoghlaim into gemini_hackathon (the GCP-first
> hackathon sister repo). The CocoIndex LanceDB target is swapped
> for the BigQuery + GCS path; the NCCE learning_graph is slimmed
> to the 5-subject OSS-first subset.

## Source files (cianfhoghlaim)

| # | Source path | Bytes | Description |
|--:|---|--:|---|
| G.1 | `baml_src/british_isles/uk_ncce/learning_graph.baml` | ~14 KB | The NCCE learning_graph BAML — 5 NCCE subjects (Computing + Maths + Science + English + Geography) with the canonical learning_graph schema. |
| G.2 | `baml_src/british_isles/uk_ncce/equivalencies.baml` | ~6 KB | The equivalencies BAML — maps the 5 British Isles jurisdictions (ENG + WAL + NIR + SCO + IoM) to NCCE. |
| G.3 | `baml_src/british_isles/ireland/education/certification.baml` | ~8 KB | The LC + JC certificate schema — the canonical certification shape. |
| G.4 | `meaisinfhoghlaim/certificate/` (7-stage pipeline) | ~50 KB | The 7-stage certificate pipeline (pipeline.py + rubric.py + types.py + backends/). |
| G.5 | `cocoindex_flows/uk_ncce/learning_graphs_app.py` | ~10 KB | The CocoIndex v1 NCCE learning_graphs App — the canonical reference implementation. |

## Destination files (gemini_hackathon)

| # | Destination path | Bytes | Source |
|--:|---|--:|---|
| G.1.dest | `~/dev/gemini_hackathon/baml_src/education/learning_graph.baml` | ~10 KB | G.1 (drop 14 LC subject extensions; keep 5 NCCE subjects; rename package to `_education_`) |
| G.2.dest | `~/dev/gemini_hackathon/baml_src/education/equivalencies.baml` | ~5 KB | G.2 (drop jurisdiction-specific equivalencies; keep canonical 5-jurisdiction equivalence) |
| G.3.dest | `~/dev/gemini_hackathon/baml_src/education/certification.baml` | ~8 KB | G.3 (lift as-is — canonical LC + JC certification shape) |
| G.4.dest | `~/dev/gemini_hackathon/meaisinfhoghlaim/certificate/` (5 files) | ~45 KB | G.4 (lift with a `GEMINI_HACKATHON_PROFILE` flag that drops the NCCA-specific stages for the GCP-first path) |
| G.5.dest | `~/dev/gemini_hackathon/cocoindex_flows/education/learning_graphs_app.py` | ~10 KB | G.5 (drop CocoIndex LanceDB target; switch to BigQuery + GCS path) |

## Transformation rules

### G.1 — learning_graph.baml

| Rule | Before | After |
|---|---|---|
| **Package namespace** | `package british_isles_uk_ncce` | `package education` (canonical gemini_hackathon namespace) |
| **14 LC subject extensions** | The 14 LC subjects (Mathematics + Chemistry + Geography + Gaeilge + English + Computer Science + ...) are referenced | **Drop all 14** — gemini_hackathon is the 5-subject OSS-first subset |
| **5 NCCE subjects** | Computing + Maths + Science + English + Geography | **Keep all 5** as-is |
| **Function names** | `function ExtractLearningGraph(subject: NcceSubject, text: string) -> LearningGraph` | `function ExtractNCCEGraph(subject: NcceSubject, text: string) -> LearningGraph` (no rename — the function shape is identical) |

### G.2 — equivalencies.baml

| Rule | Before | After |
|---|---|---|
| **Jurisdiction-specific equivalencies** | The schema references the en/wl/ni/sc/im jurisdiction pairs (the 20 jurisdiction pairs from the cianfhoghlaim 5-jurisdiction completion) | **Drop** — gemini_hackathon uses the canonical 5-jurisdiction equivalence (ENG + WAL + NIR + SCO + IoM → NCCE) |
| **5-jurisdiction equivalence** | `enum Jurisdiction { EN, WL, NI, SC, IM }` | **Keep as-is** — the canonical 5-jurisdiction equivalence |

### G.3 — certification.baml

| Rule | Before | After |
|---|---|---|
| **Package namespace** | `package ireland_education` | `package education` |
| **LC + JC schema** | The 2-tier certification schema (LC + JC) | **Lift as-is** — both repos use the same certification shape |
| **Function names** | `function GenerateLCertificate(...)` + `function GenerateJCertificate(...)` | **Keep as-is** |

### G.4 — certificate/ (retooled with GEMINI_HACKATHON_PROFILE)

| Rule | Before | After |
|---|---|---|
| **Profile flag** | n/a | `GEMINI_HACKATHON_PROFILE = true` — drops `Stage4_RubricValidator` (no NCCA rubric for the GCP-first path) + drops the NCCA-specific backends (comfyui + getimg + stability) |
| **Stage3_ArtifactBuilder** | emits PDF certificate | emits BigQuery row + GCS PDF + GCS JSON receipt (the GCP-first triple-store) |
| **Stage5_QualityGate** | validates NCCA certificate quality | validates BigQuery row idempotency + GCS object versioning + receipt JSON signature |

### G.5 — learning_graphs_app.py

| Rule | Before | After |
|---|---|---|
| **CocoIndex target** | LanceDB (`mount_table_target=LanceDBTarget(table_name="ncce_learning_graphs")`) | **Drop**; switch to BigQuery (`mount_table_target=BigQueryTarget(project="gemini-hackathon-dev", dataset="ncce", table="learning_graphs")`) + GCS object storage |
| **Embedder** | `BAAI/bge-m3` (1024-d) | **Keep as-is** — the canonical embedder per the centralized-model-registry |
| **Function names** | `class NcceLearningGraphsApp(coco.App)` | `class EducationLearningGraphsApp(coco.App)` (rename to disambiguate from the cianfhoghlaim NCCE app) |

## Per-PR step-by-step checklist

### PR #1 — Lift the NCCE learning_graph + equivalencies BAML (3 items)

- [ ] **1.1** Copy `baml_src/british_isles/uk_ncce/learning_graph.baml` → `~/dev/gemini_hackathon/baml_src/education/learning_graph.baml`; apply the 4 transformation rules
- [ ] **1.2** Copy `baml_src/british_isles/uk_ncce/equivalencies.baml` → `~/dev/gemini_hackathon/baml_src/education/equivalencies.baml`; apply the 2 transformation rules
- [ ] **1.3** Regenerate the gemini_hackathon baml_client: `cd ~/dev/gemini_hackathon && uv run baml-cli generate`

### PR #2 — Lift the certification BAML + the retooled 7-stage certificate pipeline (4 items)

- [ ] **2.1** Copy `baml_src/british_isles/ireland/education/certification.baml` → `~/dev/gemini_hackathon/baml_src/education/certification.baml` (no transformation; rename package to `education`)
- [ ] **2.2** Copy `meaisinfhoghlaim/certificate/{pipeline.py,rubric.py,types.py,__init__.py}` → `~/dev/gemini_hackathon/meaisinfhoghlaim/certificate/`; apply the 3 transformation rules (PROFILE flag + Stage3 retarget + Stage5 rewire)
- [ ] **2.3** Wire the certification BAML + the retooled pipeline into the gemini_hackathon GCP-first path (`~/dev/gemini_hackathon/meaisinfhoghlaim/certificate/gemini_hackathon_main.py`)
- [ ] **2.4** Run `cd ~/dev/gemini_hackathon && uv run pytest meaisinfhoghlaim/certificate/tests/ -v`

### PR #3 — Lift the CocoIndex learning_graphs app (retargeted to BigQuery + GCS) (5 items)

- [ ] **3.1** Copy `cocoindex_flows/uk_ncce/learning_graphs_app.py` → `~/dev/gemini_hackathon/cocoindex_flows/education/learning_graphs_app.py`; apply the 3 transformation rules (drop LanceDB + switch to BigQuery + GCS + rename class)
- [ ] **3.2** Author `~/dev/gemini_hackathon/cocoindex_flows/education/_bigquery_target.py` with the canonical BigQuery target shim (per the 6 GCP mirror stacks)
- [ ] **3.3** Author `~/dev/gemini_hackathon/cocoindex_flows/education/_gcs_target.py` with the canonical GCS target shim
- [ ] **3.4** Author `~/dev/gemini_hackathon/cocoindex_flows/education/test_learning_graphs_app.py` with the canonical BigQuery + GCS regression tests
- [ ] **3.5** Run `cd ~/dev/gemini_hackathon && uv run pytest cocoindex_flows/education/test_learning_graphs_app.py -v`

## What stays behind (explicit)

- **The 14 LC subject extensions to the NCCE learning_graph** —
  these are BIEP-specific and stay in cianfhoghlaim.
  gemini_hackathon is the 5-subject OSS-first subset.
- **The CocoIndex LanceDB target** — gemini_hackathon uses
  BigQuery + GCS (per the 6 GCP mirror stacks already consumed
  via Pangolin).
- **The NCCA-specific backends (comfyui + getimg + stability)** —
  gemini_hackathon uses the GCP-first path, not the OSS-first
  ML backends.

## Sister-repo hand-off

- gemini_hackathon maintainer receives this lift patch + openspec
  change `2026-09-XX-gemini-hackathon-lift-v1.md` (authored in
  `~/dev/gemini_hackathon/openspec/changes/`).
- Approximate LOC delta: 620 LOC (~10 KB learning_graph + ~5 KB
  equivalencies + ~8 KB certification + ~45 KB certificate + ~10
  KB learning_graphs_app + ~30 KB of BigQuery/GCS/test
  scaffolding).
