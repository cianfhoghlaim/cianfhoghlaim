# Tasks: wire-6-stage-pdf-pipeline-to-production

- [ ] 1. Replace Stage 1 stub with litellm + llama-swap call (already
  done in the parent change; verify with
  `grep "_call_vlm_for_page" cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_processing/pipeline.py`)
- [ ] 2. Replace Stage 2 stub with Granite-Docling + Molmo2-8B
  (already done; verify with
  `grep "classify_layout" cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_processing/diagram_detector.py`)
- [ ] 3. Replace Stage 3 stub with baml_client import (already done;
  verify with `grep "ExtractMarkingScheme" pipeline.py`)
- [ ] 4. Replace Stage 4 stub with DuckDB-backed NCCA taxonomy load
  (already done; verify with `grep "duckdb" topic_validator.py`)
- [ ] 5. Replace Stage 5 stub with CocoIndex v1 + BGE-M3 + LanceDB
  (already done; verify with `grep "lancedb" semantic_chunker.py`)
- [ ] 6. Add the 3 Dagster assets at `pdf_processing_assets.py`
  (already done; verify with `grep "@asset" pdf_processing_assets.py`)
- [ ] 7. Wire the observability layer (Langfuse + MLflow + RAGAS +
  Logfire) via `observability.py` (already done)
- [ ] 8. Run the 6-stage pipeline on 5 sample NCCA syllabi (to
  validate end-to-end)
- [ ] 9. Run `openspec validate wire-6-stage-pdf-pipeline-to-production --strict`
- [ ] 10. Commit + push to origin/main
