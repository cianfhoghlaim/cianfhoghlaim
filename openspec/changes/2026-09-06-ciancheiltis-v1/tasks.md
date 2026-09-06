# Tasks — `ciancheiltis` v1

## 1. OpenSpec change skeleton (30 min)

- [ ] `openspec/changes/2026-09-06-ciancheiltis-v1/proposal.md` (this file)
- [ ] `tasks.md`
- [ ] `openspec/changes/2026-09-06-ciancheiltis-v1/specs/ciancheiltis/spec.md`
      (mirror of canonical `openspec/specs/ciancheiltis/spec.md`)
- [ ] `openspec/specs/ciancheiltis/spec.md` (canonical, 13 Requirements)
- [ ] `openspec/specs/ciancheiltis/AGENTS.md` (per-spec agent routing)

## 2. PR0.0 — Foundation directories + ciancheiltis README (30 min)

- [ ] `ciancheiltis/README.md` — user-facing orientation (the user
      asked for "a similar description as found explaining such in
      cianfhoghlaim")
- [ ] `dlt_sources/ciancheiltis/__init__.py`
- [ ] `dlt_sources/ciancheiltis/_shared/__init__.py`
- [ ] `dlt_sources/ciancheiltis/en_cy/__init__.py`
- [ ] `dlt_sources/ciancheiltis/en_ga_roi/__init__.py`
- [ ] `dlt_sources/ciancheiltis/en_ga_ni/__init__.py`
- [ ] `dlt_sources/ciancheiltis/en_gd/__init__.py`
- [ ] `dlt_sources/ciancheiltis/en_gv/__init__.py`
- [ ] `dlt_sources/ciancheiltis/en_ga_eu/__init__.py`
- [ ] `dlt_sources/ciancheiltis/clarin_uk/__init__.py`

## 3. PR0.1 — Cross-domain Celtic linguistic bridges (3 hours)

- [ ] `dlt_sources/ciancheiltis/clarin_uk/corpus_browser.py`
      (CLARIN-UK Celtic resource family catalogue)
- [ ] `dlt_sources/ciancheiltis/clarin_uk/cadhan_aonair.py`
      (UD Irish + UD Welsh + UD Scottish Gaelic + UD Breton + UD Manx)
- [ ] `dlt_sources/ciancheiltis/clarin_uk/focloir_gd_ga.py`
      (Foclóir Gàidhlig-Gaeilge cross-Celtic dictionary)
- [ ] `notebooks/_shared/firecrawl_corpus_loader.py`
      append key `clarin_uk_corpora` (weekly cadence)
- [ ] Seed `lancedb://md:cianfhoghlaim/clarin_uk_corpora` table
- [ ] `openspec validate 2026-09-06-ciancheiltis-v1 --strict` passes

## 4. PR0.2 — Shared `_shared/` helpers (4 hours)

- [ ] `dlt_sources/ciancheiltis/_shared/language_detector.py`
      (lingua-py content-based detection on first 5 KB)
- [ ] `dlt_sources/ciancheiltis/_shared/opaque_url_scanner.py`
      (numeric/slug-only URL discovery)
- [ ] `dlt_sources/ciancheiltis/_shared/gov_wales_waf_bypass.py`
      (gov.wales CloudFront + WAF + CAPTCHA fallback:
       `firecrawl_interact` profile + `hwb.gov.wales` mirror)
- [ ] `dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py`
      (¿same article, both languages? structural check)
- [ ] Smoke test that proves `legislation.gov.uk/uksi/2007/1484/made`
      is detected as `cy`-predominant despite `metadata["language"]
      = "eng"`
- [ ] `openspec validate 2026-09-06-ciancheiltis-v1 --strict` passes

## 5. PR0.3 — Phase 1 (en-cy / Wales) minimum-viable pipeline (8 hours)

For each of the 8 themes that ships bilingual content for en-cy:

- [ ] T1 `dlt_sources/ciancheiltis/en_cy/legislation.py`
      — legislation.gov.uk `uksi` + `wsi` dual crawl
- [ ] T2 `dlt_sources/ciancheiltis/en_cy/policy_consultations.py`
      — gov.wales consultations
- [ ] T3 `dlt_sources/ciancheiltis/en_cy/education.py`
      — Hwb + WJEC/CBAC
- [ ] T4 `dlt_sources/ciancheiltis/en_cy/healthcare.py`
      — NHS Wales patient info
- [ ] T5 `dlt_sources/ciancheiltis/en_cy/language_commissioner.py`
      — welshlanguagecommissioner.wales
- [ ] T6 `dlt_sources/ciancheiltis/en_cy/termau_cymru.py`
      — colegcymraeg.ac.uk/termau/
- [ ] T7 `dlt_sources/ciancheiltis/en_cy/court_service.py`
      — HMCTS Welsh
- [ ] T8 `dlt_sources/ciancheiltis/en_cy/local_government.py`
      — 22 Welsh LAs

## 6. PR0.4 — Phase 1 BAML + CocoIndex + Dagster integration (8 hours)

- [ ] `baml_src/british_isles/_shared/ciancheiltis.baml`
      declares `ExtractCiancheiltisBilingualPage(page, language_pair)`
- [ ] `baml_src/british_isles/wales/ciancheiltis_en_cy.baml`
      declares the per-phase BAML
- [ ] `baml_src/clients.baml` registers `ciancheiltisCyExtract`
      (uses `gemma-4-26B-A4B` for Welsh-aware routing)
- [ ] `cocoindex_flows/british_isles/uk/ciancheiltis_en_cy_embedding.py`
      — CocoIndex v1 R1-R4-conformant App
- [ ] `orchestration/defs/1_ingestion/ciancheiltis/en_cy/defs.yaml`
      (daily 04:00 UTC cron)
- [ ] `orchestration/defs/2_materials/baml_extraction/ciancheiltis/en_cy/_assets.py`
- [ ] `orchestration/defs/3_model_lifecycle/cocoindex_v1/ciancheiltis_en_cy/defs.yaml`
- [ ] `orchestration/defs/2_materials/ciancheiltis/en_cy/asset_checks.py`
      (RAGAS ≥ 0.70, ≥ 500 bilingual pairs gated)
- [ ] `mise run baml:generate` shows 0 errors

## 7. PR0.5 — Phase 1 MotherDuck Dive + marimo (4 hours)

- [ ] `motherduck/dives/ciancheiltis_en_cy_dive.py`
      showing per-theme coverage + metadata-language-mismatch rates
- [ ] `notebooks/ciancheiltis_en_cy.py` marimo notebook (dual-mode)
- [ ] `mise run locket:exec -- marimo edit notebooks/ciancheiltis_en_cy.py`
      opens without errors

## 8. PR 1 — Phase 1 acceptance gates (1 hour)

- [ ] `openspec validate 2026-09-06-ciancheiltis-v1 --strict` passes
- [ ] `mise run lint:skills` passes
- [ ] `mise run lint:drift-docs` passes (no number-claim drift
      in any new AGENTS.md)
- [ ] `dg check yaml` passes on all new Phase 1 defs.yaml
- [ ] `mise run sync:all` succeeds
- [ ] Phase 1 RAGAS ≥ 0.70 gate fires green
- [ ] Phase 1 metadata-language-mismatch log demonstrates at least
      one success on `legislation.gov.uk/uksi/2007/1484/made`

## 9. PRs 2–6 — Phase 2 (en-ga ROI), 3 (en-ga NI), 4 (en-gd),
              5 (en-gv), 6 (en-ga EU)

Each phase replicates PR0.3 + PR0.4 + PR0.5 template for the
next language pair. Gate: previous phase RAGAS ≥ 0.70 + ≥ 500
bilingual pairs seeded.

## 10. Commit + push (5 min)

- [ ] Single commit with message
  `feat(ciancheiltis): long-distance Celtic bilingual alignment umbrella (6-phase seed)`
- [ ] Push to `origin/main`
