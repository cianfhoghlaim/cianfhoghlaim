# Change: Celtic + Multilingual Education Pipeline Overhaul (the umbrella — 5 phases × 10 stages)

## Why

Cianfhoghlaim is the canonical British-Isles Education Pipeline (BIEP) hub. The sister repos (ciancheiltis + gemini_hackathon + cianchosaint + ciandlithe + tuatha + bonneagar) each carry Celtic-language and multilingual education content that has been developed independently but never fully integrated into the canonical hub.

This umbrella change is the **50-stage rollout** that re-integrates the Celtic + multilingual surface into cianfhoghlaim, broken into 5 sequential phases × 10 stages each:

1. **Phase 1 — Irish NLP Foundation** (Weeks 1-2): `2026-09-25-gaeilge-nlp-foundation-v1`
2. **Phase 2 — HuggingFace Dataset Integration** (Weeks 3-4): `2026-09-25-irish-hf-integration-v1`
3. **Phase 3 — CLARIN-UK + Institutional Sources** (Weeks 5-6): `2026-09-25-clarin-uk-institutional-v1`
4. **Phase 4 — Welsh + Manx + Celtic Siblings** (Weeks 7-8): `2026-09-25-celtic-hf-vernacular-v1`
5. **Phase 5 — Indexing + Verification** (Weeks 9-10): this change + per-phase wholesale-copy audit

Each phase is itself an openspec change (proposal + tasks + spec delta). This umbrella change:
- Defines the 5-phase × 10-stage plan
- Defines the canonical `celtic-language-pipeline` spec (codified at Phase 5.9)
- Defines the wholesale-copy contract (per `sister-shared` spec §Shared-1..5)
- Defines the verification gates (per-stage light + per-phase heavy)
- Tracks the 5 CLARIN / institutional data-access requests (filed at Action 0.3)
- Tracks the 6 sister-repo wholesale-copy integrations (verified at Phase 5.6)

## Sister-repo re-integration strategy (the intent)

| Sister intent | Where it lands | Phase |
|---|---|---|
| ciancheiltis `dlt_sources/language/clarin.py` (CLARIN VLO loader) | `dlt_sources/language/clarin.py` (wholesale) | Phase 1.7 + Phase 3.1 |
| ciancheiltis `dlt_sources/common/huggingface_factory.py` | `dlt_sources/common/huggingface_factory.py` (wholesale) | Phase 2.7 |
| ciancheiltis `meaisinfhoghlaim/models/teanga_registry.py` (12 models) | `meaisinfhoghlaim/models/teanga_registry.py` (wholesale) | Phase 1.7 |
| ciancheiltis 6 Celtic translation agents | `agents/meaisinfhoghlaim/educational/` (referenced from `agents/teanga/`) | Phase 4.5 + 4.6 (cross-Celtic context) |
| gemini_hackathon 29 BAML functions in `baml_extracts_education/` (post-dedupe) | referenced as the pattern for Phase 1.7 + Phase 4 | Phases 1-4 |
| gemini_hackathon 6 HF Spaces (editorial studios) | out of scope (per `sister-shared` spec) | n/a |
| gemini_hackathon `cloud_run_deep_research` (12th Terraform module) | out of scope (IaC sister) | n/a |

## Verification gates

### Per-stage (×50)
Light gate after each of the 50 stages:
- `ruff check . && ruff format --check .`
- `baml-cli generate` (if BAML touched)
- `uv run pytest tests/<surface> -v` (the surface's unit tests)
- ≈10 minutes per stage

### Per-phase (×5)
Heavy gate at each phase boundary:
- `bash scripts/verify.sh` (8/8 ticks)
- `mise run sync:all` (the 14-layer orchestrator — paths / CCC / Cognee / skills / MCP / Dagster / drift-docs / spec-agents / BAML / stacks / DLT / agents / notebooks / Firecrawl)
- `mise run lint:registry` (0 hardcoded model strings)
- `openspec validate --strict` (the phase change + the umbrella)
- `gcloud billing budgets list` (verify £300 alert still in place)
- Trigger Cloud Run redeploy if gemini_hackathon BAML changed
- Archive the phase change via `openspec archive`
- ≈2 hours per phase boundary

## Action 0 — Pre-flight (completed before any code work)

- [x] **Action 0.1**: Wholesale-copy infrastructure (`scripts/sister_lifts.py` + `stedding/sister-lifts/WHOLESALE_COPY_INDEX.md` + `LEDGER.md`)
- [x] **Action 0.2**: 5 openspec changes filed (proposals + tasks + spec deltas scaffolded)
- [ ] **Action 0.3**: 5 CLARIN / institutional data-access requests (filed via `scripts/access_requests.py`)
- [ ] **Action 0.4**: Per-phase smoke test (`tests/integration/test_full_celtic_pipeline.py`)

## The canonical `celtic-language-pipeline` spec (codified at Phase 5.9)

The umbrella change creates a new spec `openspec/specs/celtic-language-pipeline/spec.md` with 6 Requirements:

1. **CLP-1**: The 6 Celtic languages (ga, gd, cy, gv, br, kw) + EN must have unified BAML extraction surfaces
2. **CLP-2**: Each Celtic language must have at least 1 BAML extractor + 1 DLT source + 1 CocoIndex App + 1 Dagster asset + 1 MotherDuck Dive
3. **CLP-3**: Each Celtic language must have at least 1 HuggingFace dataset integrated (Phase 2 + 4)
4. **CLP-4**: CLARIN-UK VLO integration for each Celtic language (Phase 3)
5. **CLP-5**: Wholesale-copy invariants from the sister repos must pass the verification gates (Phase 5.6)
6. **CLP-6**: End-to-end Celtic pipeline smoke test (`tests/integration/test_full_celtic_pipeline.py`) must pass

## Impact

- **Affected code**: ~200+ files across 5 phases (the full Celtic + multilingual surface in cianfhoghlaim)
- **Affected specs**: NEW `celtic-language-pipeline` (added at Phase 5.9)
- **Affected sister repos**: ciancheiltis (read-only supplier), gemini_hackathon (read-only supplier), cianchosaint + ciandlithe (wholesale-copy verification)

## Sequenced timeline

```
Week  1- 2: Phase 1 — Irish NLP Foundation         10 stages × 1 stage/day = 10 working days
Week  3- 4: Phase 2 — HF Dataset Integration      10 stages × 1 stage/day
Week  5- 6: Phase 3 — CLARIN + Institutional      10 stages × 1 stage/day
Week  7- 8: Phase 4 — Welsh + Manx + Celtic         10 stages × 1 stage/day
Week  9-10: Phase 5 — Indexing + Verification     10 stages × 1 stage/day
                  TOTAL = 50 working days = 10 working weeks
```

## Out of scope (separate changes)

- **Tuatha sister-repo carry-over** (Celtic mythology, NPC dialogue, MMO agents)
- **Bonneagar IaC sister carry-over** (89 stacks)
- **GCP-first IaC refactor** (the `2026-08-30-gcp-first-iac-refactor-v1` change in gemini_hackathon — depends on `terraform apply` decision)
- **The 8 LC subject BAML dedupe** (`2026-09-13-baml-extracts-education-dedupe`) — separate change, executed in parallel
- **Tuatha BI Educational MMO** (the 14-subject extension)

## Budget estimate

- HF dataset downloads: ~50 GB → free
- CocoIndex LanceDB tables: ~10 GB → free (local)
- Cloud Run redeploys: ~£5 × 5 redeploys = £25
- Vertex AI eval: ~£30 (gemma-4-26b-a4b evaluations on 4 eval datasets × ~50 prompts)
- **Total: ~£55** of the £350 budget — comfortable
