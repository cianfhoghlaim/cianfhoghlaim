# reference/notebooks/ — upstream reference notebooks

Jupyter notebooks curated from Google ADK examples, data engineering tooling (LakeFS, GeoAI, Lance, DuckLake, DLT), and the **meaisínfhoghlaim** (ML/AI) research corpus.

> **Status (2026-06-25):** moved from `docs/notebooks/` to
> `reference/notebooks/` per the `docs/ → .agents/skills/` consolidation.
> These are **upstream reference material** — they are not imported
> by the codebase, not part of any test suite, and not part of the
> CI build. The directory exists for human reference and to support
> ad-hoc agent exploration.

343 notebooks organised by snakecase-filename category.

Last consolidated: 2026-06-14

---

## Subdirectory map

| Subdir | Topic | Notebooks | Size |
|---|---|---|---|
| [`data_engineering/lakefs/`](data_engineering/lakefs/) | Apache LakeFS data-versioning examples | 124 | 2.3M |
| [`data_engineering/geoai/`](data_engineering/geoai/) | GeoAI geospatial ML examples (raster, vector, segmentation, building detection, etc.) | 88 | 1.1M |
| [`data_engineering/lance/`](data_engineering/lance/) | LanceDB examples (incl. 14MB ColPali vision retriever) | 8 | 17M |
| [`data_engineering/ducklake/`](data_engineering/ducklake/) | DuckLake (DuckDB + Iceberg + lakehouse) | 6 | 516K |
| [`data_engineering/dlt/`](data_engineering/dlt/) | dlt workshops (Small Data SF 2025) | 1 | 12K |
| [`meaisínfhoghlaim/`](meaisínfhoghlaim/) | ML/AI research (Gemma3, Qwen3, HuggingFace, sam-audio, Deepseek, federated) | 82 | 52M |
| [`teanga/`](teanga/) | Irish-language processing (kscanne, historical document analysis) | 19 | 1.1M |
| [`agents_google-adk/`](agents_google-adk/) | Google ADK agent framework examples (Firecrawl, A2A, evaluation) | 3 | 3.1M |
| [`marimo_docs_marimo/`](marimo_docs_marimo/) | Marimo reactive-notebook examples (parallel to `docs/marimo/`) | 9 | 40K |
| [`_misc/`](_misc/) | One-off notebooks (boring-semantic-layer, bonneagar walkthrough) | 2 | 508K |
| [`_archives/`](_archives/) | Archived notebooks (18MB Gemma_3n audio understanding with embedded weights) | 1 | 18M |
| **Total** | | **343** | **95M** |

## Big-notebook notes

- **`meaisínfhoghlaim/[Gemma_3n]Audio_understanding_with_HF.ipynb` (18MB)** — moved to `_archives/`. The 18MB comes from embedded audio samples + HF model weights. Archived because (a) it's enormous, (b) the embedded weights are likely outdated. Re-run from upstream notebook if needed: <https://huggingface.co/docs/transformers>.
- **`data_engineering/lance/ColPali-vision-retriever_colpali.ipynb` (14MB)** — kept in `data_engineering/lance/` since ColPali is a current project. 14MB is embedded ColPali model weights.
- **`meaisínfhoghlaim/sam-audio_examples_visual_prompting.ipynb` (8.8MB)** and **`text_prompting` (8.0MB)** — kept; SAM-Audio is current.

## Topics-of-interest cross-refs

- **For pipeline architecture**: `data_engineering/ducklake/` + `data_engineering/lance/`
- **For curriculum knowledge graph (Cognee)**: `data_engineering/ducklake/` (DuckDB + Ibis examples)
- **For Celtic language processing**: `teanga/` + cross-ref `docs/marimo/`
- **For agent frameworks**: `agents_google-adk/` + cross-ref `docs/02-agents/`
- **For ML fine-tuning & inference**: `meaisínfhoghlaim/`
- **For geospatial (Tuath world map)**: `data_engineering/geoai/`
