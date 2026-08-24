# `dlt_sources/filesystem/`

> `filesystem/`: the file system sources (leaving_cert + zotero + takeout + UoG) — 17 .py files, 8 @dlt.source.

## Quick start

- `leaving_cert_source.py` — the 80+ Leaving Cert PDFs at `/leaving_certificate/`
- `zotero.py` — Zotero research library exports
- `google_takeout.py` + `takeout_v1.py` — Google Takeout exports
- `university_of_galway.py` — UoG research library + lectures (the leabharlann personal archive)
- `gemini_deep_research.py` + `gemini_corpus_source.py` + `email_inbox.py` — Gemini exports + research corpus + email
- `leabharlann_books.py` + `lc6_cross_check.py` + `previews.py` + `pdf_download_source.py` — leabharlann utilities

## Status

The UoG source (`university_of_galway.py`) and the leabharlann personal archive sources are wired into the BIEP v3 5-phase pattern (1_ingestion + 2_materials + 4_asset_generation). The UoG exam_papers source is wired via `orchestration/defs/uog_exam.py`.

The `university_of_galway_deep.py` DLT source file (at `dlt_sources/british_isles/ireland/education/`) is currently orphaned (not referenced by `ireland_jurisdiction_pipeline.py`). Phase A3 will wire it into the BIEP v3 5-phase pattern (Decision 2 of the audit).
