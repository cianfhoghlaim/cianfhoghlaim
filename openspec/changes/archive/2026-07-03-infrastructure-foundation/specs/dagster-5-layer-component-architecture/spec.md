## ADDED Requirements

### Requirement: Dagster image ships with OCR/VLM/memory Python packages

The `dagster-local` Docker image built from `bonneagar/stacks/dagster/Dockerfile.dagster` SHALL install 12 Python packages to support the inline-Python backends for the v4 OCR/VLM/memory stack (the new `2026-07-03-infrastructure-foundation` change). These 12 packages are:

**OCR backends (4 packages):**
- `surya-ocr>=0.20.0` — sunbird text-line OCR (transformers backend)
- `rapidocr>=3.9.0` — fast onnx OCR with 3 backends (onnxruntime/paddle/torch)
- `pytesseract>=0.3.10` — Tesseract wrapper (transformers backend)
- `easyocr>=1.7.2` — 80+ language OCR with Celtic support

**VLM backends (2 packages):**
- `docling[mlx-vlm]>=2.0.0` — IBM Docling + MLX-VLM backend for Apple Silicon
- `paddleocr-vl>=1.0.0` — PaddleOCR-VL 1.6 Python wrapper (MLX backend)

**Document→Markdown (2 packages):**
- `marker-pdf>=1.10.2` — GPU-accelerated PDF→markdown (GPL-3.0 review required)
- `mineru>=3.4` — batch GPU PDF parsing

**In-process GGUF runtime (1 package):**
- `llama-cpp-python>=0.3.0` — Metal backend for Apple Silicon M-series

**Agent memory (3 packages):**
- `graphiti-core[falkordb]>=0.29.2` — temporal knowledge graph (FalkorDB Lite embedded)
- `cognee-sdk>=1.0.0` — knowledge graph for agents (complements the cognee/ Compose stack)
- `letta>=0.5` — 3rd memory backend per the agent-fleet-orchestration skill

**HF CLI (1 package):**
- `huggingface-hub>=0.27.0` — used by the v4 download scripts

In addition, the image SHALL install 4 system apt packages:
`tesseract-ocr`, `libtesseract-dev`, `poppler-utils`, `libgl1`,
`libglib2.0-0`.

#### Scenario: The dagster image imports all 12 packages

- **WHEN** `docker build -f bonneagar/stacks/dagster/Dockerfile.dagster -t dagster-local:latest bonneagar/stacks/dagster/ && docker run --rm dagster-local:latest python -c "import surya, rapidocr, easyocr, docling, paddleocr_vl, marker_pdf, mineru, llama_cpp, graphiti_core, cognee, letta, huggingface_hub"`
- **THEN** the command SHALL exit 0
- **AND** no ImportError SHALL be raised

#### Scenario: The image includes tesseract

- **WHEN** `docker run --rm dagster-local:latest which tesseract && docker run --rm dagster-local:latest tesseract --version`
- **THEN** the tesseract binary SHALL be at `/usr/bin/tesseract` (or similar) and `--version` SHALL print a version string ≥ 4.0

### Requirement: pyproject.toml optional-dependencies include ocr-vision-full

The `cianfhoghlaim/pyproject.toml` SHALL provide a
`[project.optional-dependencies.ocr-vision-full]` group containing the
9 production Python packages listed above (all OCR/VLM/doc→md packages
in the v4 stack). Installing this group SHALL make the
inline-Python OCR/VLM backends available for:

```bash
uv pip install -e '.[ocr-vision-full]'    # in dev
docker build ...                            # in the dagster image (Layer 2)
```

In addition, the `memory` extra SHALL be extended with `cognee-sdk` +
`letta` (alongside the existing `graphiti-core[falkordb]`).

A new composite extra `dev-with-vision` SHALL combine `dev + memory +
ocr-vision-full` for the 25 new dev notebooks under
`notebooks/dashboards/{leaving_cert,law,...}`.

#### Scenario: dev-with-vision installs all required deps

- **WHEN** `uv pip install -e '.[dev-with-vision]'` runs
- **THEN** the venv SHALL contain at least: pytest, ruff, mypy, marimo,
  altair, surya-ocr, rapidocr, easyocr, docling, paddleocr-vl,
  marker-pdf, mineru, llama-cpp-python, graphiti-core[falkordb],
  cognee-sdk, letta, huggingface-hub
- **AND** `mo run dashboards/leaving_cert/01_chemistry_analysis.py --headless` SHALL succeed (smoke test from Change B)
