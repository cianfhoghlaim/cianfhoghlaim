## ADDED Requirements

### Requirement: Dev venv ships 574 packages at the latest available versions

The Cianfhoghlaim dev `.venv` (at `.venv/` of the repo root) SHALL
contain 574+ packages (vs. the prior 195) installed via
`uv pip install ".[all]"` from `cianfhoghlaim/`. The 14 critical
packages — `dagster`, `dlt`, `cognee`, `falkordb`, `mlflow`, `easyocr`,
`docling`, `llama_cpp`, `graphiti_core`, `letta`, `huggingface_hub`,
`marimo`, `baml_py`, `paddleocr` (requires `paddlepaddle` installed
separately) — SHALL be importable in the dev venv.

The `pyproject.toml` SHALL bump all 91 pinned packages to >=X.Y.Z
where X.Y.Z is the latest available on PyPI (as of 2026-07-05).
The "Drop both lower bounds" conflict resolution policy SHALL apply
when transitive constraints conflict: the lower bound on the more
flexible package is dropped.

The 5 KCG Components SHALL import from
`cianfhoghlaim.orchestration.components` (post-Session-10 rename).
The 22 v4 `VISION_MODELS` SHALL be importable from
`cianfhoghlaim.meaisinfhoghlaim.models.registry`.

#### Scenario: All 14 critical packages import in the dev venv

- **WHEN** `uv run python -c "import dagster, dlt, cognee, falkordb, mlflow, easyocr, docling, llama_cpp, graphiti_core, letta, huggingface_hub, marimo, baml_py; print('OK')"`
- **THEN** the command SHALL exit 0 with the message "OK"
- **AND** no `ModuleNotFoundError` SHALL be raised

#### Scenario: `dagster definitions validate` loads the code location

- **WHEN** `cd cianfhoghlaim && uv run dagster definitions validate -m cianfhoghlaim.orchestration.definitions`
- **THEN** the validation SHALL report "Validation successful for code
  location cianfhoghlaim.orchestration.definitions" (with the known
  pre-existing source_factory fallback to empty Definitions)
