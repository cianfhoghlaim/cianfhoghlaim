## ADDED Requirements

### Requirement: All 25 dev marimo notebooks wire to live DLT data

The 25 dev marimo notebooks (16 LC5 + 9 Gemini) SHALL each have at
least one `@app.cell` that runs the actual DLT source
(`lc5_documents` for LC5, `gemini_documents` for Gemini) on the
appropriate root_path and shows real data (not stub data).

The 16 LC5 notebooks (under `leaving_cert/`):
- 02-05: per-subject (computer_science, gaeilge, geography,
  mathematics) — filter by subject
- 06-10: cross-subject — all 72 rows
- 11-15: model benchmark — uses `model_key` column from the 72 rows
- 16: runtime_comparison_llama_swap_vs_cpp — status @app.cell
  explaining the 13 GGUF models are queued for download (~95 GB
  via `mise run llama-swap:download-models`)

The 9 Gemini notebooks:
- 01_{medical,politics,culture,technology,other}_corpus_overview:
  per-corpus (filter by corpus) — 5 notebooks
- 02_cross_corpus_timeline, 03_jurisdictional_map,
  04_pattern_detection: cross-corpus (all 224 rows) — 3 notebooks
- 01_law_corpus_overview: already wired (Session 9)

#### Scenario: LC5 notebook shows real chemistry data

- **WHEN** `cd cianfhoghlaim && uv run python -c "from dlt.filesystem.leaving_cert_source import lc5_documents; print(len(list(lc5_documents())))"`
- **THEN** the output SHALL be `72`
- **AND** when filtered by `subject == 'chemistry'`, the result SHALL
  be 16 rows

#### Scenario: Gemini notebook shows real law data

- **WHEN** `cd cianfhoghlaim && uv run python -c "from dlt.filesystem.gemini_corpus_source import gemini_documents; print(len(list(gemini_documents())))"`
- **THEN** the output SHALL be `224`
- **AND** when filtered by `corpus == 'law'`, the result SHALL be 57 rows

#### Scenario: All 27 notebooks parse

- **WHEN** `python3 -c "import ast; from pathlib import Path; notebooks = [f for d in ['leaving_cert', 'medical', 'politics', 'culture', 'technology', 'other', 'law'] for f in Path(f'cianfhoghlaim/notebooks/dashboards/{d}').glob('*.py')]; [ast.parse(n.read_text()) for n in notebooks]; print(f'{len(notebooks)} OK')"`
- **THEN** the output SHALL be `27 OK` (25 wired + 2 pre-existing)
