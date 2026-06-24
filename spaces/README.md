# `spaces/` — Cianfhoghlaim Hugging Face Spaces

This directory is the canonical home for every Hugging Face Space published
by the Cianfhoghlaim monorepo. It contains 4 sub-trees:

| Sub-tree | What it is | Source-of-truth |
|:--|:--|:--|
| `spaces/_common/` | The cross-cutting bundle (theme, BAML client, i18n, demo recorder, Anam Bonneagar footer, soulbound SVG, social card, **CICD docs**) | [`_common/README.md`](./_common/README.md), [`_common/cicd.md`](./_common/cicd.md) |
| `spaces/{an_scrudu,anam_tuatha,cianfhoghlaim,meaisin_cliste}/` | The 4 deployed Build Small 2026 hackathon Spaces (1 per quadrant + 1 integration) | Each Space's own `README.md` |
| `spaces/data-engineering/` | **Prior-art** repo (BigQuery → Delta Lake → DuckDB → dbt → Evidence pipeline). Lives in `spaces/` for reference; not part of the monorepo git history (it is a separate git repo with its own `.git/`). | [§1.1 below](#1-prior-art-repositories-patterns) |
| `spaces/anti-phish/` | **Prior-art** repo (6-stage ML progression + Gradio front-end). Same: separate git repo, lives here for reference. | [§1.2 below](#2-prior-art-repository-anti-phish) |
| `spaces/{STATUS.md,build-small-2026-*.md,*.md}` | The 5 hackathon planning artefacts and the status doc. | [`STATUS.md`](./STATUS.md) |
| `spaces/croilar-demo-quadrant-indexes.md`, `spaces/infisical-recovery-2026-06-09.md` | Supporting docs from the Build Small 2026 prep. | (their own frontmatter) |

## How to use this README

- **Just landed here?** Start with [§1 Prior-art patterns](#1-prior-art-patterns) — the catalogue of 20 reusable patterns from the two prior-art repos.
- **Adding a new Space?** Read [§3 Per-Space quickstart](#3-per-space-quickstart) and follow the recipe in `spaces/_common/cicd.md`.
- **Migrating a Space to the new reusable CI?** Read [`spaces/_common/cicd.md`](./_common/cicd.md) §"Quick start".
- **Looking for the "what patterns do we adopt, adapt, defer, skip" decision?** [§2 Adopt / Adapt / Defer / Skip decision matrix](#2-adopt--adapt--defer--skip-decision-matrix).

---

## 1. Prior-art patterns

The two prior-art repos (`spaces/data-engineering/`, `spaces/anti-phish/`)
each demonstrate ~10 reusable patterns. We do not care about their themes
(PyPI download analytics, phishing email detection) — we care about the
**software and architecture patterns** they embody.

### 1.1 Prior-art repository: `spaces/data-engineering/`

**Stack:** BigQuery → Delta Lake → DuckDB (or MotherDuck) → dbt-duckdb →
Evidence.dev dashboard, orchestrated by Dagster.

| # | Pattern | Source | Reusable for us? | Where it lands |
|--:|:--|:--|:--|:--|
| **A1** | **Multi-stage data pipeline** with `@asset` + `@dbt_assets` + `group_name` partitioning. | `package_analytics/assets.py:16-125` | ✅ Adopt | `oideachais/dagster_defs/` (already have Dagster; missing dbt). Marimo is our preferred dashboard. |
| **A2** | **Pydantic typed ingestion models** (`FileDownloads`, `Details`, `PypiJobParameters`) + pyarrow validation. | `package_analytics/dlt_sources/models.py:1-108` | ✅ Adopt | `oideachais/dlt_sources/<area>/models.py` (reuse; some already exist) |
| **A3** | **dlt `@source` / `@resource`** pattern returning pyarrow tables with explicit `name=` per project. | `package_analytics/dlt_sources/bigquery_pipeline.py:140-173` | ✅ Adopt | Already used in `oideachais/dlt_sources/ireland/*`; promote the "yield pa.Table" idiom |
| **A4** | **`CustomDagsterDbtTranslator`** that flattens `dbt_resource_props["name"]` to an `AssetKey` and pins `group_name`. | `package_analytics/resources.py:9-15` | ✅ Adopt | New `oideachais/dagster_defs/dbt_translator.py` (Phase 4 of the `celtic-data-engineering-patterns` change) |
| **A5** | **dbt-duckdb multi-target** with `{{ 'incremental' if target.name == 'prod' else 'table' }}` and `+unique_key`. | `dbt_project/{dbt_project.yml,models/pypi_daily_stats.sql}` | ✅ Adopt | New `oideachais/dbt_project/` mirroring this exact shape |
| **A6** | **DuckDB ⇄ MotherDuck** swap via `DUCKDB_DATABASE` env (`md:db?motherduck_token=...` vs local path). | `.env.template:9-15` + `dbt_project/profiles.yml` | ✅ Adopt | Drop-in for our existing MotherDuck wiring |
| **A7** | **HF Space deploy via `git subtree split`** + `git push -f` to a "static space" + `sdk: docker` build that uploads to a separate space. | `.github/workflows/main.yml:1-27` + `dashboard/Dockerfile:1-45` | ✅ Adopt | Promoted to reusable workflow at `infrastructure/ci/spaces-sync.yml` (sister change `spaces-cicd-reusable-pipeline`) |
| **A8** | **Evidence `sources/<name>/connection.yaml` + `*.sql`** layout for typed SQL queries referenced from `pages/*.md` via `` ```sql name ``. | `dashboard/sources/pypi_analytics/*` + `pages/index.md:62-156` | ⚠️ Adapt | Not Evidence (we use marimo) but the **SQL-by-fenced-block** pattern translates to marimo's `mo.sql()` cells or a `queries/<name>.sql` dir |
| **A9** | **Custom `+layout.svelte`** + `.evidence/customization/.profile.json` for theming Evidence. | `dashboard/{pages/+layout.svelte, .evidence/customization/*}` | ✅ Adapt | Map directly to marimo custom CSS + theme overrides in `oideachais/marimo/theme.py` |
| **C1** | **`from .resources import dbt_manifest_path, CustomDagsterDbtTranslator`** + module-name-as-Dagster-code-location (`tool.dagster module_name = "package_analytics"`). | `pyproject.toml:5` + `package_analytics/__init__.py` | ✅ Adopt | Apply to our existing `oideachais/dagster_defs/` |
| **C2** | **`.env.template` with commented MotherDuck branch** (single source of truth, dev-vs-prod). | `.env.template` | ✅ Already done | We have `.infisical.env` template; one extra comment line per dev-baile secret |
| **C3** | **Evidence devcontainer** with `evidence.evidence-vscode` + Codespaces `postCreateCommand` cleanup. | `dashboard/.devcontainer/devcontainer.json` + `.vscode/extensions.json` | ⚠️ Defer | Add `oideachais/.devcontainer/` for marimo + dbt + dagster parity — Phase 5+ |

### 1.2 Prior-art repository: `spaces/anti-phish/`

**Stack:** 6-stage ML progression: data extraction → classical sklearn →
PyTorch → HF Transformers → Flower FL → Gradio ensemble UI.

| # | Pattern | Source | Reusable for us? | Where it lands |
|--:|:--|:--|:--|:--|
| **B1** | **6-stage ML progression** (extract → classical sklearn → PyTorch → HF Transformers → Flower FL → Gradio) with one model per stage and comparative UI. | `{1..6}_*.ipynb` | ✅ Adopt | Adopt as **canonical ML workflow** in `meaisinfhoghlaim/pipelines/` |
| **B2** | **sklearn pickle models served from S3** loaded with `urllib.request.urlopen` at app boot. | `6_Gradio_Front_End.ipynb:cell-6` | ⚠️ Adapt | Replace S3 with HF Hub `huggingface_hub.hf_hub_download` (cheaper, no egress) |
| **B3** | **HuggingFace `pipeline("sentiment-analysis", model=…)`** wrapper for fine-tuned model. | `6_Gradio_Front_End.ipynb:cell-6` | ✅ Adopt | Reuse for any of our 10 OCR / classification models (`meaisinfhoghlaim/ocr/model_registry.py`) |
| **B4** | **Gradio `Interface` with multiple parallel `outputs`** (one per model) + `examples=[…]` + `allow_flagging="never"`. | `6_Gradio_Front_End.ipynb:cell-8` | ✅ Adopt | Adopt as the **ensemble UI pattern** in `meaisinfhoghlaim/pipelines/ensemble_gradio.py` |
| **B5** | **`Dataset.from_pandas` + `train_test_split` + `Trainer`** with `transformers.set_seed(N)` and `device = "cuda" if available else "mps" else "cpu"`. | `4_Huggingface_Transformers.ipynb:cell-1..7` | ✅ Adopt | Template for fine-tuning Celtic-language classifiers (BGE-M3, mms-tts-ga) |
| **B6** | **Pushing fine-tuned model to HF Hub** (`foghlaimeoir/phishing-DistilBERT`). | `README.md:25` | ✅ Adopt | Already used in `meaisinfhoghlaim/`; codify as `spaces/_common/hf_hub_push.py` |
| **B7** | **Federated learning with Flower** for distributed fine-tuning. | `5_Flower_Federated_Learning.ipynb` | ⚠️ Defer | Reuse for privacy-preserving Gaelscoil NLP training (not hackathon scope) |

---

## 2. Adopt / Adapt / Defer / Skip decision matrix

| Decision | Count | Examples |
|:--|:-:|:--|
| ✅ **Adopt** as-is | 10 | A1, A2, A3, A4, A5, A6, B1, B3, B4, B5, B6, C1, C2 |
| ⚠️ **Adapt** (use the pattern but rewrite for our stack) | 3 | A8 (Evidence → marimo `mo.sql`), A9 (svelte layout → marimo theme), B2 (S3 → HF Hub) |
| ⏸️ **Defer** (good idea, not in scope) | 2 | A7 (HF Space deploy — done as separate OpenSpec change), B7 (Flower FL), C3 (devcontainer) |
| ❌ **Skip** | 0 | — |

**Anti-patterns observed in the prior-art (do NOT copy):**

- `spaces/data-engineering/package_analytics/dlt_sources/bigquery_pipeline.py:80-97` — the `bigquery_to_gcs()` branch is half-written (writes to GCS but the GCS data is never read downstream). Dead code.
- `spaces/data-engineering/package_analytics/dlt_sources/bigquery_pipeline.py:196-197` — `fire.Fire(lambda **kwargs: main(PypiJobParameters(**kwargs)))` is a fragile CLI pattern. Use `pydantic` `argparse` binding or `typer` instead.
- `spaces/data-engineering/dashboard/.github/workflows/release.yml` — a 14-matrix GitHub Release workflow that builds zips for every Node/OS/arch combination and never consumes the artifacts. Idempotent busywork.
- `spaces/anti-phish/4_Huggingface_Transformers.ipynb` — the fine-tuning notebooks save checkpoints to local disk (no Hub push) and have no reproducibility metadata. The HF Hub push helper (B6) fixes this.
- `spaces/anti-phish/1_Data_Extraction.ipynb` — 5,563 lines of unstructured extraction code with no library boundary. Don't repeat at this scale; use the BAML `ExtractEn` / `ExtractEnStrong` clients we already have.

---

## 3. Per-Space quickstart

The 4 deployed Spaces (`an_scrudu`, `anam_tuatha`, `cianfhoghlaim`,
`meaisin_cliste`) all share the same shape:

```
spaces/<my_space>/
├── app.py            # Gradio app: blocks + i18n + theme
├── requirements.txt  # minimal: gradio>=4.44, huggingface_hub>=0.24
├── README.md         # HF frontmatter (sdk, app_file, emoji, color)
├── social_card.png   # 1200x630 PNG (rendered at build time)
├── voiceover_script.txt   # human narration for the demo video
├── storyboard.png         # visual storyboard
├── demo_sequence.json     # programmatic demo sequence
└── record_demo.py         # wraps _common/demo_recorder.py
```

The shared bundle lives in `spaces/_common/`. Every Space imports from it:

```python
from spaces._common import (
    apply_celtic_theme, GRADIO_CSS,
    render_anam_bonneagar_footer, render_social_card,
    I18N_STRINGS, translate, set_lang,
    chat_complete, get_hackathon_client_config,
)
```

For the canonical Space + 5-element story see
[`spaces/build-small-2026-plan.md`](./build-small-2026-plan.md).

## 4. CI/CD migration

See [`spaces/_common/cicd.md`](./_common/cicd.md) for the recipe. The
sister OpenSpec change `spaces-cicd-reusable-pipeline` (in
`openspec/changes/spaces-cicd-reusable-pipeline/`) lands the reusable
workflow at `infrastructure/ci/spaces-sync.yml`. Per-Space
`.github/workflows/sync.yml` files are added in a follow-up commit.

## 5. Pattern-to-file map (the absorption plan)

The full work breakdown is in the OpenSpec change
`openspec/changes/celtic-data-engineering-patterns/`. Quick map:

| Pattern | OpenSpec change | File(s) |
|:--|:--|:--|
| A1, A4, A5 | `celtic-data-engineering-patterns` | `oideachais/dbt_project/*`, `oideachais/dagster_defs/dbt_translator.py` |
| A6 | (no new file — drop-in) | The MotherDuck wiring in `oideachais/dagster_defs/` already supports it |
| A7 | `spaces-cicd-reusable-pipeline` (sister) | `infrastructure/ci/spaces-sync.yml` |
| A8, A9 | (marimo equivalents) | `meaisinfhoghlaim/marimo/01_*.py`, `02_*.py` |
| B1, B3, B4 | `celtic-data-engineering-patterns` | `meaisinfhoghlaim/pipelines/ensemble_gradio.py` |
| B5, B6 | `celtic-data-engineering-patterns` | `spaces/_common/hf_hub_push.py` (and existing `meaisinfhoghlaim/ocr/`) |
| B7 | (deferred) | — |

## 6. Related monorepo docs

- [`openspec/AGENTS.md`](../openspec/AGENTS.md) — change-management workflow
- [`openspec/project.md`](../openspec/project.md) — 26 capability specs
- [`oideachais/AGENTS.md`](../oideachais/AGENTS.md) — lakehouse quadrant
- [`meaisinfhoghlaim/AGENTS.md`](../meaisinfhoghlaim/AGENTS.md) — AI/ML quadrant (now includes the new `marimo/` row)
- [`tuatha/AGENTS.md`](../tuatha/AGENTS.md) — MMO + crypto
- [`croilar/AGENTS.md`](../croilar/AGENTS.md) — multi-persona portfolio
- [`AGENTS.md`](../AGENTS.md) — root agent instructions

## 7. Change history

| Date | Change | OpenSpec |
|:--|:--|:--|
| 2026-06-08 | Build Small 2026 hackathon: 4 Spaces + `_common` bundle | `croilar-hf-build-small-2026-demo` (archived 2026-06-08) |
| 2026-06-17 | Reusable HF Spaces CI/CD workflow | `spaces-cicd-reusable-pipeline` (this branch) |
| 2026-06-17 | Celtic data-engineering + Gradio ensemble patterns + 2 marimo notebooks | `celtic-data-engineering-patterns` (this branch) |
| 2026-06-24 | 8 active + 1 archived + 1 canonical exception documented | `spaces-bundle-decomposition-v1` (round 12) |

---

## How to deploy

The 4 active Spaces (an_scrudu / meaisin_cliste / cianfhoghlaim / anam_tuatha) deploy via GitHub Actions:

```bash
# Trigger the per-Space sync workflow (uses the canonical reusable workflow at
# .github/workflows/spaces-sync.yml)
gh workflow run "Sync <space> to HF" --repo cianfhoghlaim/kings_college_galway --ref main

# Verify
gh run list --workflow="Sync *_to HF" --limit=4
# All 4 should show "completed" within 5 minutes
```

The 4 new demo Spaces (croilar_portfolio_demo / oideachais_mission_control /
crypteolas_defi_monitor / tuatha_mmo_demo) deploy the same way.

The 1 non-gradio Space (data-engineering) is built locally and pushed via
`python -m build && twine upload dist/*` to PyPI.

The full 8-phase playbook is in [`DEPLOY.md`](../DEPLOY.md).

## How to debug

| Symptom | Cause | Fix |
|:--|:--|:--|
| The Gradio app fails to import | The `_common/` bundle is missing | Add `from spaces._common import ...` |
| The 5-element palette is missing | The `theme.py` import is missing | Use `gr.Blocks(theme=theme)` |
| The LLM call returns 502 | The LiteLLM gateway is unreachable | The `chat_complete_json` helper auto-falls back |
| The HF sync workflow times out | HF API rate limit | Add `retry: 3` to the reusable workflow |
| The bilingual toggle doesn't work | The `i18n.t("key")` calls are missing | Use `i18n.t("key", lang=lang)` |

## Common workflows

1. **Add a new Space** — `mkdir -p spaces/<space>/` + create the 4 required files (app.py + requirements.txt + README.md + AGENTS.md) + add the per-Space sync.yml wrapper
2. **Add a new Space theme** — extend the `tabs` list in `app.py` (see `.agents/skills/gradio-ensemble-pattern/`)
3. **Add a new 5-element palette** — `spaces/_common/theme.py`
4. **Add a new i18n string** — `spaces/_common/i18n.py` (the EN/GA bilingual toggle)
5. **Push a model to HF Hub** — `spaces/_common/hf_hub_push.py`
