# Tasks: 2026-07-09-cross-nation-content-audit-v1

## 1. Create the openspec change directory + 5 DLT source dirs

- [x] 1.1 Create `openspec/changes/2026-07-09-cross-nation-content-audit-v1/`
- [x] 1.2 Create `openspec/changes/2026-07-09-cross-nation-content-audit-v1/specs/british-isles-education-pipeline/`
- [x] 1.3 Create `cianfhoghlaim/dlt/british_isles/scotland/education/sqa/`
- [x] 1.4 Create `cianfhoghlaim/dlt/british_isles/wales/education/wjec/`
- [x] 1.5 Create `cianfhoghlaim/dlt/british_isles/england/education/aqa/`
- [x] 1.6 Create `cianfhoghlaim/dlt/british_isles/england/education/pearson/`
- [x] 1.7 Create `cianfhoghlaim/dlt/british_isles/northern_ireland/education/ccea/`
- [x] 1.8 Create `stedding/site_scrape_samples/{sqa,wjec,aqa,pearson,ccea}/en/mathematics/`

## 2. Audit — write the 5-nation fact base

### 2.1 Scotland / SQA / Curriculum for Excellence

- [x] 2.1.1 Document canonical SQA URL: `https://www.sqa.org.uk/sqa/56983.html` (SQA National Qualifications finder)
- [x] 2.1.2 Document 3 qualification levels: National 5 (S4), Higher (S5), Advanced Higher (S6) — distinct from the English GCSE / A-Level scheme
- [x] 2.1.3 Document language convention: EN + Scots Gaelic (`gd`); CfE also has separate Gàidhlig-medium resources at `education.gov.scot/improvement/learning-resources/foghlam-tron-ghaidhlig/`
- [x] 2.1.4 Document partition pattern: `MultiPartitionsDefinition(cycle="scottish_senior_phase", subject, language)` — `cycle` values: `["national_5", "higher", "advanced_higher"]`, distinct from Ireland's `senior_cycle`
- [x] 2.1.5 Document topic overlap with Irish LC: mathematics / chemistry / physics / biology / english / history / geography / computing all share topics with the 6 Irish LC priority subjects

### 2.2 Wales / WJEC / Curriculum for Wales

- [x] 2.2.1 Document canonical WJEC URL: `https://www.wjec.co.uk/` (the WJEC qualification finder)
- [x] 2.2.2 Document 2 qualification levels: GCSE (key stage 4), A-Level (post-16) — same as England + NI
- [x] 2.2.3 Document language convention: EN + Welsh (`cy`); WJEC = English, CBAC (`cy`) = Welsh-language; both are the same body, branded differently per language
- [x] 2.2.4 Document partition pattern: `MultiPartitionsDefinition(cycle=["gcse", "a_level"], subject, language=["en", "cy"])`
- [x] 2.2.5 Document Curriculum for Wales (2022 reform) distinct from the older "National Curriculum for Wales" — 6 Areas of Learning and Experience (AoLE): Expressive Arts, Health & Well-being, Humanities, Languages, Literacy & Communication, Mathematics & Numeracy, Science & Technology

### 2.3 England / AQA / Pearson Edexcel / National Curriculum

- [x] 2.3.1 Document canonical AQA URL: `https://www.aqa.org.uk/subjects/gcse` + `https://www.aqa.org.uk/subjects/a-level`
- [x] 2.3.2 Document canonical Pearson Edexcel URL: `https://qualifications.pearson.com/en/qualifications/edexcel-gcses.html` + `https://qualifications.pearson.com/en/qualifications/edexcel-a-levels.html`
- [x] 2.3.3 Document 2 qualification levels: GCSE (key stage 4), A-Level (key stage 5) — England has 3 boards (AQA, OCR, Pearson Edexcel) + WJEC Eduqas
- [x] 2.3.4 Document language convention: EN only (no statutory second language at GCSE / A-Level)
- [x] 2.3.5 Document partition pattern: `MultiPartitionsDefinition(cycle=["gcse", "a_level"], subject, board=["aqa", "pearson", "ocr", "eduqas"], language=["en"])`
- [x] 2.3.6 Document Pearson = the international GCSE offer (Pearson Edexcel International GCSE) — distinct qualification from the UK GCSE, with ~70 subjects vs AQA's ~50

### 2.4 Northern Ireland / CCEA / NI Curriculum

- [x] 2.4.1 Document canonical CCEA URL: `https://ccea.org.uk/` (the CCEA qualification finder)
- [x] 2.4.2 Document 2 qualification levels: GCSE (years 11-12), A-Level (post-16) — same scheme as England + Wales
- [x] 2.4.3 Document language convention: EN + Irish (`ga`); Irish-medium schools (gaeltacht naíonraí + bunscoileanna) follow the same syllabus as the ROI Gaeltacht schools
- [x] 2.4.4 Document partition pattern: `MultiPartitionsDefinition(cycle=["gcse", "a_level"], subject, language=["en", "ga"])`
- [x] 2.4.5 Document CCEA = the sole Northern Ireland awarding body (since 1994) — distinct from the 3 England boards

### 2.5 Crown Dependencies (IoM / Jersey / Guernsey)

- [x] 2.5.1 Document that IoM follows the English National Curriculum + offers the same GCSE / A-Level suite (mostly via AQA + Pearson Edexcel); adds Manx Gaelic (`gv`) as a language subject
- [x] 2.5.2 Document that Jersey follows the English National Curriculum (GCSE + A-Level) + offers French + Jèrriais (`roa-jersey`) language options
- [x] 2.5.3 Document that Guernsey follows the English National Curriculum; offers English + French at GCSE (no distinct language of instruction)

## 3. Scaffold — write the 5 DLT source modules

- [x] 3.1 `cianfhoghlaim/dlt/british_isles/scotland/education/sqa/syllabus_source.py` — `sqa_syllabus_source(...)` with `@dlt.resource(name="mathematics_syllabus", write_disposition="merge", primary_key=["url"])`, reads from `stedding/site_scrape_samples/sqa/en/mathematics/sample.json`, returns 1 row when file exists, 0 rows otherwise
- [x] 3.2 `cianfhoghlaim/dlt/british_isles/wales/education/wjec/syllabus_source.py` — same pattern
- [x] 3.3 `cianfhoghlaim/dlt/british_isles/england/education/aqa/syllabus_source.py` — same pattern
- [x] 3.4 `cianfhoghlaim/dlt/british_isles/england/education/pearson/syllabus_source.py` — same pattern
- [x] 3.5 `cianfhoghlaim/dlt/british_isles/northern_ireland/education/ccea/syllabus_source.py` — same pattern
- [x] 3.6 Each source uses the existing `get_dlt_destination(namespace="<board>")` factory from `cianfhoghlaim/dlt/common/destinations_oideachais.py` (the v1 BIEP's `warehouse`-equivalent named destination)
- [x] 3.7 Each source honours `USE_LOCAL_SCRAPES=true` to skip any future live network calls

## 4. Cache files — write the 5 placeholder fixtures

- [x] 4.1 `stedding/site_scrape_samples/sqa/en/mathematics/sample.json` (Firecrawl-shaped: markdown + metadata)
- [x] 4.2 `stedding/site_scrape_samples/wjec/en/mathematics/sample.json`
- [x] 4.3 `stedding/site_scrape_samples/aqa/en/mathematics/sample.json`
- [x] 4.4 `stedding/site_scrape_samples/pearson/en/mathematics/sample.json`
- [x] 4.5 `stedding/site_scrape_samples/ccea/en/mathematics/sample.json`

## 5. Crosswalk + report — write `docs/agents/cross-nation-content-audit.md`

- [x] 5.1 Executive summary — the 5-nation exam-board matrix table
- [x] 5.2 Per-nation breakdown (5 nations + Crown Dependencies sub-section)
- [x] 5.3 Shared vs nation-specific topics table (5 columns: Ireland, Scotland, Wales, England, Northern Ireland)
- [x] 5.4 BAML function reuse — which of the 7 lc_extraction + 5 cross_nation functions apply to each nation, plus the 2 new functions v2 will need
- [x] 5.5 Hand-off to data-platform — the 5 scaffolded DLT sources are ready for v2 production-isation

## 6. Spec deltas

- [x] 6.1 Add 2 ADDED Requirements + 1 MODIFIED delta under `openspec/changes/2026-07-09-cross-nation-content-audit-v1/specs/british-isles-education-pipeline/spec.md`
- [x] 6.2 `Requirement: cross-nation audit produced for SQA / WJEC / CCEA / AQA / Pearson`
- [x] 6.3 `Requirement: 5 scaffolded DLT sources (one per nation) pass the smoke test`
- [x] 6.4 MODIFIED delta on the existing `Requirement: Cross-nation extension deferred to v2` — point at this change as the v2 precondition

## 7. Validate

- [x] 7.1 `openspec validate 2026-07-09-cross-nation-content-audit-v1 --strict` passes
- [x] 7.2 Word count of `docs/agents/cross-nation-content-audit.md` is between 2,000 and 3,000
- [x] 7.3 `dlt.pipeline(...).run(sqa_syllabus_source())` produces 1 row from the cache
- [x] 7.4 `ccc search "cross-nation scaffold"` returns the 5 new sources
- [x] 7.5 All 5 exam-board URLs in the audit doc are reachable

## 8. Commit + push

- [x] 8.1 Stage the 5 DLT sources, 5 cache files, 1 audit doc, openspec change (proposal + tasks + spec)
- [x] 8.2 Single commit with message `feat(biep): cross-nation content audit (T5) — 5 scaffolded sources + audit doc`
- [x] 8.3 `git push origin pick-4-biep-v1`
