# BAML+CocoIndex tutorial track (5 notebooks)

This directory is the **BAML+CocoIndex tutorial track** — 5 marimo
notebooks covering the full stack from post-v4 BAML 0.223.0 syntax to
the CocoIndex v1 + vision model integration. It is the canonical
follow-up to the parent mega-change
`2026-07-11-baml-cocoindex-modernization-v1/` (commit `409898008`).

| # | File | What it teaches | BAML/CocoIndex | Vision model |
|:--|:--|:--|:--|:--|
| 1 | `01_baml_post_v4_syntax.py` | Canonical post-v4 BAML 0.223.0 syntax (`generator` block + `field Type` whitespace + `@@description` + `image` + `@stream.*` + `?` optionality) | BAML syntax | none |
| 2 | `02_qpack_8_subject_walkthrough.py` | The 8 `qpack_<subject>.baml` files (the `paragraph → LO[] → FormativeItem → Score → Validate` pattern; 40+ BAML calls) | BAML | none |
| 3 | `03_education_pdf_vision_pipeline.py` | The vision+PDF pipeline (`ExtractCurriculumSyllabus` → `ExtractExamPaperLayout` → `ExtractSyllabusDiagram` → `ExtractMarkingSchemeGuideline`) with **side-by-side `gemma-4-26B-A4B` vs `qwen3-vl-8b`** | BAML + vision | `gemma-4-26B-A4B` + `qwen3-vl-8b` |
| 4 | `04_cocoindex_baml_integration.py` | The 3 real CocoIndex+BAML integration patterns (`upstream_api_surface`, `upstream_blog_monitor`, `docs_skills_consolidation`) | BAML + CocoIndex | none |
| 5 | `05_post_v4_duplicate_audit_and_migration.py` | Interactive audit of the duplicates from the 42-renames commit (`49e0259a0`) | BAML audit | none |

Each tutorial is dual-mode (marimo + `uv run` via PEP 723 inline
deps). The marimo app entrypoint is `app.run()`; the CLI entrypoint
is `_cli_main()`.

## Cross-references

- `openspec/specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md` —
  the parent capability spec (8 requirements, including the
  "5-notebook BAML+CocoIndex tutorial track" requirement)
- `openspec/changes/2026-07-12-baml-cocoindex-tutorials-v1/` —
  the openspec change record for this tutorial track
- `openspec/changes/2026-07-11-baml-cocoindex-modernization-v1/` —
  the parent mega-change (Phase C)
- `openspec/changes/2026-07-08-five-tangent-modernization/` — the
  5-tangent change that introduced the 8-step tutorial pattern +
  the `end-to-end-llm-zoomcamp-style-tutorial` spec
- `docs/agents/five-tangent-modernization.md` — the 5-tangent
  companion doc

## Run via the `cianfhoghlaim-marimo` CLI

```bash
# List all 5 tutorial notebooks (CLI discovers them under the
# `13_baml_cocoindex_tutorial/` group)
uv run cianfhoghlaim-marimo list 13_baml_cocoindex_tutorial

# Open the BAML post-v4 syntax walkthrough in marimo edit
uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/01_baml_post_v4_syntax

# Run the vision+PDF pipeline (with the side-by-side gemma-4 vs qwen3-vl comparison)
uv run cianfhoghlaim-marimo run 13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline

# Serve the vision+PDF pipeline as a marimo dashboard
uv run cianfhoghlaim-marimo dashboard 13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline
```

## The `01_overview_setup.py` Step 0.5 pointer

The notebook `cianfhoghlaim/notebooks/01_overview_setup.py` has a
"Step 0.5: the BAML+CocoIndex tutorial track" Markdown cell that links
to this directory + lists the 5 tutorials with their 1-line summaries.
Per the parent mega-change spec delta on `oideachais-marimo-dashboards`,
the pointer is wired to this directory by reference (no hard dependency
on the 5 tutorial files existing).