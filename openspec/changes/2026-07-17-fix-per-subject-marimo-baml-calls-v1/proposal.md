# Change: Fix per-subject marimo BAML calls

## Summary

The six per-subject study-tool notebooks in `notebooks/12_subject_study_tools/` displayed BAML-looking state dictionaries instead of invoking the generated BAML client. Their `_per_subject_baml` cells recorded `{"function": "Generate<Subject>FormativeItem", "status": "invoked"}` and a deferred quest-pack placeholder, so the UI shipped as theatre.

The six `notebooks/leaving_cert/<subject>.py` dashboards also used stale quest-pack calls: several referenced non-existent long-form BAML functions such as `GenerateComputerScienceQuestPack`, `GenerateEnglishQuestPack`, `GenerateGaeilgeQuestPack`, and `GenerateGeographyQuestPack`; all six passed the old `(topic, level, language, n_items)` shape instead of the canonical `(syllabus, past_papers, marking_schemes, level)` signature.

This change replaces the dead-code dictionaries with real synchronous BAML client calls and aligns the leaving_cert dashboards with the generated `qpack_<subject>.baml` signatures.

## Dependencies

Blocked by: none
Blocked by (soft): `2026-07-16-biiep-v1-lc-per-subject-marimo-study-tools-v1`, `2026-07-16-biiep-v1-lc-per-subject-agent-workflows-v1`
Affected repos: cianfhoghlaim

## Scope

- Update 6 study-tool notebooks:
  - `12_subject_study_tools/mathematics.py`
  - `12_subject_study_tools/chemistry.py`
  - `12_subject_study_tools/computer_science.py`
  - `12_subject_study_tools/english.py`
  - `12_subject_study_tools/gaeilge.py`
  - `12_subject_study_tools/geography.py`
- Update 6 leaving_cert dashboards:
  - `leaving_cert/mathematics.py`
  - `leaving_cert/chemistry.py`
  - `leaving_cert/computer_science.py`
  - `leaving_cert/english.py`
  - `leaving_cert/gaeilge.py`
  - `leaving_cert/geography.py`
- Add one spec delta under `end-to-end-llm-zoomcamp-style-tutorial` requiring real per-subject BAML invocations.

## Non-goals

- Do not edit the canonical `qpack_<subject>.baml` files.
- Do not edit archived OpenSpec changes.
- Do not modify the `lc_extraction/*.baml` schemas owned by the BIEP v1 change.
- Do not require live LLM credentials for AST validation; notebook cells remain try/except-wrapped so they render when BAML credentials are absent.
