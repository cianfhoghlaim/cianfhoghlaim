# Author-Archive v1: Implementation Tasks

This is the implementation plan for `openspec/changes/author-archive-v1/`.
All work lands on the `feat/author-archive-v1` branch (which builds on
`feat/sruth-browser-refactor`).

## Stage 0 — Refactor prerequisite (already done on `feat/sruth-browser-refactor`)

- [x] Add `sruth_browser/credit_budget.py` (SQLite-backed persistent counter)
- [x] Add `sruth_browser/scrape_strategist.py` (typed wrapper)
- [x] Add `MAP_SITE` + `VISUAL_GROUNDING` to `BrowserOperation` enum
- [x] Extend `BackendRouter` with `pre_research`, `map_site`,
      `visual_ground`, `screenshot` methods
- [x] 47 new tests pass (`test_credit_budget.py` 23 + `test_scrape_strategist.py` 24)
- [x] Commit `c563b9680` on `feat/sruth-browser-refactor`

## Stage 1 — Pre-research + condensation + UI identification

### 1.0 BAML extension (DONE)

- [x] Add 6 new BAML functions to `baml_src/author_archive.baml`
      (PreResearchSite, CondenseToCriticalInfo, IdentifyUiPatterns,
      VisualGroundingFromScreenshot, SummarizeSite, ClassifySiteCivic)
- [x] Add 7 new classes (ResearchSiteMap, JsonSchema, ExtractedEntity,
      CondensedPage, UiType, UiIndicator, BoundingBox, GroundedElement,
      AuthorArchiveCivicCategory)
- [x] `baml-cli generate` succeeds (14 files written to `baml_client/`)
- [x] 6 new test cases in the BAML file (PreResearchSiteTest, etc.)

### 1.1 Dagster assets (DONE)

- [x] Create `sruth/oideachais/dagster_defs/assets/official_media/scraping_assets.py`
      with 4 assets: `pre_research`, `bulk_scrape`, `condense`, `identify_uis`
- [x] 17 sample sources covering all 10 official_media categories
- [x] Register in `sruth/oideachais/dagster_defs/assets/official_media/__init__.py`
- [x] Register in `sruth/oideachais/dagster_defs/assets/__init__.py` `all_assets`

### 1.2 Hero example script (DONE)

- [x] Create `sruth/oideachais/scripts/pre_research_cps_gov_uk.py` running all
      4 phases on CPS.gov.uk
- [x] Persist output to `/tmp/author_archive_cps_gov_uk.json` for marimo

### 1.3 OpenSpec change (DONE)

- [x] Create `openspec/changes/author-archive-v1/` with proposal + tasks
      + 4 spec deltas
- [ ] `openspec validate author-archive-v1 --strict` (next step)

### 1.4 OpenSpec specs (TODO — this commit)

- [ ] `author-archive-pipeline/spec.md` — Dagster + DLT + BAML matrix
- [ ] `author-archive-web-scraping/spec.md` — capability matrix + credit math
- [ ] `author-archive-ui-grounding/spec.md` — UI types + grounding shape
- [ ] `author-archive-credit-budget/spec.md` — ledger schema + marimo widget

## Stage 2 — UoG coursework (deferred to author-archive-v2)

5 new DLTs (`olscoil_mata.py`, `olscoil_software.py`, `olscoil_irish.py`,
`olscoil_education.py`, `personal_records.py`) + 20 new assets + 5 BAML
functions. Deferred to a follow-up change.

## Stage 3 — Cross-corpus knowledge graph (deferred)

Independent of the scraping layer. Will land in `author-archive-v3` after
the UoG and Gemini corpora are flowing.

## Stage 4 — Multi-target deployment (deferred)

`sruth/oideachais/dlt_utils/target_factory.py` + 3 targets (dev=DuckDB,
staging=MotherDuck, prod=Garage S3 + Lakekeeper) + `make_target.sh`.
Deferred to `author-archive-v4`.

## Validation

```bash
# 1. Validate OpenSpec change
openspec validate author-archive-v1 --strict

# 2. Run new browser tests
cd infrastructure/browser
python -m pytest tests/test_credit_budget.py tests/test_scrape_strategist.py -v

# 3. Run the hero example
cd oideachais
python scripts/pre_research_cps_gov_uk.py

# 4. Run existing oideachais tests
cd oideachais
pytest tests/test_official_media_assets.py -v
```

## Push status

This branch is **blocked by GitHub Push Protection** on a pre-existing
Cloudflare User API Token false positive in `92de91dd6` (the ancestor
of this branch). The user must click:
https://github.com/cianfhoghlaim/kings_college_galway/security/secret-scanning/unblock-secret/3FJCpFNzLDCfZJEGjxSjxtjI0vv
to unblock. Local commits on this branch are clean.
