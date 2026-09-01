# cocoindex_flows/uk_ncce — UK NCCE Learning Graph Pipeline

Phase 4 of the 2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1 change
(Phase 4 of the cianfhoghlaim-nua v6 era plan).

The NCCE learning-graph pipeline walks 5 NCCE PDF artefacts
(`data/bi_ep/syllabi_raw/uk_ncce/curriculum/`) and converts them
to grid-aware Markdown output via Docling + the row × column
detector at `cocoindex_flows/_shared/_docling_grid_segmenter.py`.

## Files

- `learning_graphs_app.py` — the canonical grid-aware PDF converter
  (lifted + OSS-ified from `gemini_hackathon/cocoindex_flows/uk_ncce/`)

## Usage

```bash
# Run the conversion
python -m cocoindex_flows.uk_ncce.learning_graphs_app
```

## See also

- `baml_src/british_isles/uk_ncce/learning_graph.baml` — the 6
  per-subject NCCE learning-graph extractors
- `baml_src/british_isles/uk_ncce/equivalencies.baml` — the 48
  cell-level cross-jurisdiction equivalencies
- `data/bi_ep/learning_graphs/` — the 11 NCCE learning-graph JSONs
- `openspec/changes/2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1/`