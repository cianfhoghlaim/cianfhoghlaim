# Sister-Repo Lift: `bonneagar-iac-gcp-mirror-lift-v1`

> **One-line summary:** Lift the canonical study-plan BAML + the
> Convex schema (slimmed to the 6 IaC tables) + the 7-stage
> certificate pipeline (retooled for Terraform plan JSON) from
> cianfhoghlaim into bonneagar. The 6 GCP mirror stacks already
> live in bonneagar — no lift needed. The 11-component A2UI
> catalog stays behind (bonneagar uses Pangolin UI).

## Source files (cianfhoghlaim)

| # | Source path | Bytes | Description |
|--:|---|--:|---|
| B.1 | `baml_src/british_isles/_shared/study_plan.baml` | ~14 KB | The canonical StudyPlan + ExtractStudyPlan + GenerateStudyPlanAssets BAML surface. |
| B.2 | `bonneagar/stacks/gcp-{bigquery-mirror,cloud-run,gcs-bucket,gemini-vertex,gemma-unsloth,secret-manager}/README.md` | ~30 KB | The 6 GCP mirror stack READMEs. **No lift needed** — already in bonneagar. |
| B.3 | `web/packages/db/convex/schema.ts` | ~5 KB | The canonical 13-table Convex schema. **Slimmed to 6 IaC tables** for bonneagar (no 16 LC tables). |
| B.4 | `meaisinfhoghlaim/certificate/` | ~50 KB | The 7-stage certificate pipeline (pipeline.py + rubric.py + types.py + backends/). **Stage3 retargeted to Terraform plan JSON; Stage4 dropped** (no rubric for IaC artefacts). |
| B.5 | `web/packages/a2ui/` (11 components) | ~25 KB | The A2UI v0.9 catalog. **Stays behind** — bonneagar uses Pangolin UI, not A2UI. |

## Destination files (bonneagar)

| # | Destination path | Bytes | Source |
|--:|---|--:|---|
| B.1.dest | `~/dev/bonneagar/baml_src/_study_plan.baml` | ~10 KB | B.1 (rewritten — drop `british_isles._shared` namespace; strip per-jurisdiction SubjectSpec refs; keep canonical StudyPlan + ExtractStudyPlan + GenerateStudyPlanAssets shape) |
| B.3.dest | `~/dev/bonneagar/web/packages/db/convex/schema.ts` | ~3 KB | B.3 (slimmed to 6 IaC tables: `users + workspaces + stacks + pipelines + runs + audit_log`) |
| B.4.dest | `~/dev/bonneagar/meaisinfhoghlaim/certificate/` (5 files) | ~45 KB | B.4 (retooled: `Stage3_ArtifactBuilder` emits Terraform plan JSON, `Stage4_RubricValidator` dropped, `Stage5_QualityGate` rewired) |

## Transformation rules

### B.1 — study_plan.baml

| Rule | Before (cianfhoghlaim) | After (bonneagar) |
|---|---|---|
| **Namespace** | `baml_src/british_isles/_shared/study_plan.baml` | `baml_src/_study_plan.baml` (drop `_shared`; bonneagar is the substrate, not the BIEP) |
| **Class names** | `class StudyPlan { ... }` | `class IaCStudyPlan { ... }` (rename to disambiguate from BIEP) |
| **Per-jurisdiction refs** | The 5 `class {en,wl,ni,sc,im}SubjectSpec` imports | **Drop** — bonneagar doesn't need jurisdiction-specific SubjectSpecs |
| **Function names** | `function GenerateStudyPlanAssets(...)` | `function GenerateIaCStudyPlanAssets(...)` (rename) |

### B.3 — schema.ts (slimmed)

| Rule | Before | After |
|---|---|---|
| **16 LC tables** | `accounting + business + french + history + art + music + applied_mathematics + physics + chemistry + mathematics + gaeilge + english + geography + biology + computer_science + ...` | **Drop all 16** — IaC substrate doesn't need BIEP tables |
| **5 jurisdiction tables** | `england_subject_specs + wales_subject_specs + ...` | **Drop all 5** — IaC substrate is jurisdiction-agnostic |
| **6 IaC tables** | n/a | `users + workspaces + stacks + pipelines + runs + audit_log` (the canonical IaC substrate) |
| **Index strategy** | `by_jurisdiction + by_subject` | `by_stack + by_pipeline + by_run_status` (per-stack health queries) |

### B.4 — certificate/ (retooled for Terraform plan JSON)

| Rule | Before | After |
|---|---|---|
| **Stage3_ArtifactBuilder** | emits PDF certificate | emits Terraform plan JSON |
| **Stage4_RubricValidator** | validates NCCA marking rubric | **Dropped** — no rubric for IaC artefacts |
| **Stage5_QualityGate** | validates NCCA certificate quality | **Rewired** — validates Terraform plan idempotency + drift detection |
| **Backend** | `comfyui + getimg + stability` | **Drop** — IaC cert uses no ML backends; just hash the plan JSON |

## Per-PR step-by-step checklist

### PR #1 — Lift the canonical study-plan BAML (3 items)

- [ ] **1.1** Copy `baml_src/british_isles/_shared/study_plan.baml` → `~/dev/bonneagar/baml_src/_study_plan.baml`
- [ ] **1.2** Apply the 4 transformation rules above (namespace + class names + jurisdiction refs + function names)
- [ ] **1.3** Regenerate the bonneagar baml_client: `cd ~/dev/bonneagar && uv run baml-cli generate`

### PR #2 — Slim the Convex schema to the 6 IaC tables (4 items)

- [ ] **2.1** Copy `web/packages/db/convex/schema.ts` → `~/dev/bonneagar/web/packages/db/convex/schema.ts`
- [ ] **2.2** Apply the 4 transformation rules above (drop 16 LC tables + drop 5 jurisdiction tables + add 6 IaC tables + rewire indexes)
- [ ] **2.3** Author `~/dev/bonneagar/web/packages/db/convex/_migrations/iac_substrate.ts` with the migration plan from the BIEP schema to the IaC schema
- [ ] **2.4** Run `cd ~/dev/bonneagar/web/packages/db && npx convex dev` to verify the schema deploys cleanly

### PR #3 — Lift the 7-stage certificate pipeline (retooled for Terraform plan JSON) (5 items)

- [ ] **3.1** Copy `meaisinfhoghlaim/certificate/{pipeline.py,rubric.py,types.py,__init__.py}` → `~/dev/bonneagar/meaisinfhoghlaim/certificate/`
- [ ] **3.2** Apply the 4 transformation rules above (Stage3 retarget + Stage4 drop + Stage5 rewire + backends drop)
- [ ] **3.3** Copy `meaisinfhoghlaim/certificate/backends/__init__.py` → `~/dev/bonneagar/meaisinfhoghlaim/certificate/backends/__init__.py` (empty backends package)
- [ ] **3.4** Author `~/dev/bonneagar/meaisinfhoghlaim/certificate/tests/test_terraform_plan.py` with the canonical Terraform plan idempotency + drift tests
- [ ] **3.5** Run `cd ~/dev/bonneagar && uv run pytest meaisinfhoghlaim/certificate/tests/ -v`

## What stays behind (explicit)

- **B.2** — The 6 GCP mirror stack READMEs are already in
  `bonneagar/stacks/gcp-*/README.md` (the home repo); ciandlithe +
  cianchosaint + gemini_hackathon reference these stacks via
  Pangolin resources, NOT by copying the stack files.
- **B.5** — The 11-component A2UI catalog stays behind entirely;
  bonneagar uses Pangolin resource pages, not A2UI chat surfaces.

## Sister-repo hand-off

- Bonneagar maintainer receives this lift patch + openspec change
  `2026-09-XX-bonneagar-lift-v1.md` (authored in `~/dev/bonneagar/openspec/changes/`).
- Approximate LOC delta: 580 LOC (~14 KB BAML + ~3 KB schema +
  ~45 KB certificate + ~30 KB of CI/test scaffolding).
