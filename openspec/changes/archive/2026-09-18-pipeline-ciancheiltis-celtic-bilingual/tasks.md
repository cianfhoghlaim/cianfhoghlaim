# Tasks: pipeline-ciancheiltis-celtic-bilingual

## 1. Phase 1 — Local sources for 5 Celtic pairs + EU dimension

- [ ] **C1.1** `dlt_sources/ciancheiltis/__init__.py` — wholesale copy of `dlt_sources/british_isles/__init__.py`
- [ ] **C1.2** `dlt_sources/ciancheiltis/_base.py` — `CelticBilingualPipelineBase` contract
- [ ] **C1.3** `dlt_sources/ciancheiltis/cy/` (Welsh) — gov.wales + Senedd + Welsh Tribunals
- [ ] **C1.4** `dlt_sources/ciancheiltis/gd/` (Scottish Gaelic) — gov.scot + Scottish Parliament + Bòrd na Gàidhlig
- [ ] **C1.5** `dlt_sources/ciancheiltis/ga-ni/` (Irish in NI) — nidirect + NI Assembly + Foras na Gaeilge
- [ ] **C1.6** `dlt_sources/ciancheiltis/gv/` (Manx) — gov.im + Tynwald + Culture Vannin
- [ ] **C1.7** `dlt_sources/ciancheiltis/ga-eu/` (Irish at EU) — europarl.ie + Oireachtas + EU institutions

## 2. Phase 2 — 10-theme classification taxonomy

- [ ] **C2.1–C2.10** 10-theme taxonomy (education + governance + media +
  culture + sport + business + legal + health + welfare + diaspora)
- [ ] **C2.11** Theme detection prompt (`baml_src/ciancheiltis/processing/theme_classification.baml`)
- [ ] **C2.12** Confidence threshold + analyst-review queue for low-confidence classifications

## 3. Phase 3 — BAML extraction

- [ ] **C3.1** `baml_src/ciancheiltis/processing/celtic_pair_extraction.baml` (canonical shared prompt)
- [ ] **C3.2–C3.6** Per-jurisdiction overrides (Welsh nuances + Scottish Gaelic nuances + etc.)
- [ ] **C3.7** Content-based language detection (opaque URLs + bilingual mixed content)
- [ ] **C3.8** gov.wales WAF bypass (HTTP headers + cookie + rate-limit handling)

## 4. Phase 4 — CocoIndex embedding (R1–R4)

- [ ] **C4.1** `cocoindex_flows/ciancheiltis/cy_flow.py` (Welsh)
- [ ] **C4.2** `cocoindex_flows/ciancheiltis/gd_flow.py` (Scottish Gaelic)
- [ ] **C4.3** `cocoindex_flows/ciancheiltis/ga_ni_flow.py` (Irish in NI)
- [ ] **C4.4** `cocoindex_flows/ciancheiltis/gv_flow.py` (Manx)
- [ ] **C4.5** `cocoindex_flows/ciancheiltis/ga_eu_flow.py` (Irish at EU)
- [ ] **C4.6** `cocoindex_flows/ciancheiltis/bre_flow.py` (Breton — extra pair beyond the initial 5)
- [ ] **C4.7** CLARIN-UK integration (alignment corpora from
  https://www.clarin.ac.uk — ud_irish + ud_welsh + ud_scots +
  ud_breton + ud_manx + ud_cornish)
- [ ] **C4.8** Apply R1 (typed Pydantic row schema) + R2 (BAMLFunctionTool
  wire) + R3 (marimo surface) + R4 (cross-pipeline join)

## 5. Phase 5 — Marimo + A2UI surface

- [ ] **C5.1** `notebooks/ciancheiltis/bilingual_corpus.py` — 8-tab marimo notebook
- [ ] **C5.2** Per-pair filtering tabs (6 tabs)
- [ ] **C5.3** Theme distribution chart
- [ ] **C5.4** Pair confidence histogram
- [ ] **C5.5** A2UI surface for inline queries
- [ ] **C5.6** MotherDuck Dive card `ciancheiltis.celtic_pair_count`

## 6. Phase 6 — Cross-pipeline integration

- [ ] **C6.1** Wire to BIEP pipeline (Celtic-language sources feed the
  LC + JC syllabi when relevant)
- [ ] **C6.2** Wire to ciancheiltis sister repo (`~/dev/ciancheiltis/`)
- [ ] **C6.3** Wire to cianchosaint's BIIP pipeline (intelligence
  oversight covers Celtic-language Celtic-language press)

## 7. Verification

- [ ] Run `openspec validate pipeline-ciancheiltis-celtic-bilingual --strict` — pass
- [ ] Run `openspec validate --all --strict` — pass
- [ ] Run `mise run ciancheiltis:dlt:sync-all` — pass
- [ ] Verify ≥100 rows per Celtic pair in the MotherDuck Dive

## Verification

```bash
cd ~/dev/cianchosaint-laim 2>/dev/null || cd ~/dev/cianfhoghlaim
openspec validate pipeline-ciancheiltis-celtic-bilingual --strict
```
