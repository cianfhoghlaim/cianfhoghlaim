## ADDED Requirements

### Requirement: 12 Python OCR/VLM/memory packages in the dagster-local image

The `dagster-local` Docker image SHALL install 12 Python packages so
the 6 TRANSFORMERS-backend models in the v4 OCR/VLM registry are
loadable from Python: `surya-ocr`, `rapidocr`, `pytesseract`,
`easyocr`, `docling[mlx-vlm]`, `paddleocr-vl`, `marker-pdf`, `mineru`,
`llama-cpp-python`, `graphiti-core[falkordb]`, `cognee-sdk`, `letta`.

These are added to `bonneagar/stacks/dagster/Dockerfile.dagster` per
Change A of 2026-07-03.

#### Scenario: The dagster image imports all 12 packages

- **WHEN** `docker run --rm dagster-local:latest python -c "import surya, rapidocr, easyocr, docling, paddleocr_vl, marker_pdf, mineru, llama_cpp, graphiti_core, cognee, letta, huggingface_hub"`
- **THEN** the command SHALL exit 0

### Requirement: dev-with-vision extra in pyproject.toml

The `cianfhoghlaim/pyproject.toml` SHALL have a
`[project.optional-dependencies.dev-with-vision]` composite extra
combining `dev + memory + ocr-vision-full` for the 25 new dev
notebooks under `notebooks/dashboards/{leaving_cert,law,...}`.

#### Scenario: dev-with-vision includes all 25-notebook deps

- **WHEN** `uv pip install -e '.[dev-with-vision]'`
- **THEN** the venv SHALL contain: surya-ocr, rapidocr, easyocr,
  docling, paddleocr-vl, marker-pdf, mineru, llama-cpp-python,
  graphiti-core[falkordb], cognee-sdk, letta, huggingface-hub,
  marimo, altair, pytest, ruff, mypy, pre-commit

### Requirement: 25 dev marimo notebooks under notebooks/dashboards/

The system SHALL have 25 working dev marimo notebooks:
- 16 LC: `notebooks/dashboards/leaving_cert/{01..16}_*.py`
- 9 Gemini: `notebooks/dashboards/{law,medical,politics,culture,technology,other}/0?_*.py`

Each SHALL have working `@app.cell` code (not skeletons), use the
`mo.sql(engine=duckdb)` pattern, and display altair/plotly
visualisations.

#### Scenario: All 25 notebooks AST-parse

- **WHEN** `for f in $(find notebooks/dashboards/{leaving_cert,law,medical,politics,culture,technology,other} -name '0?_*.py'); do python -c "import ast; ast.parse(open('\$f').read())"; done`
- **THEN** all 25 files SHALL parse without syntax errors
