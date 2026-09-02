"""OCR/VLM ensemble pipeline (BIEP v2).

Per the 2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1 change.

The 4-path ensemble:
  Path 1 (BAML):    Docling-serve -> text -> b.Extract<Jurisdiction>Document()
  Path 2 (Unstract): Docling-serve -> Unstract workflow -> JSON
  Path 3 (gemma4):  gemma-4-26B-A4B-vision page-level image -> JSON
                    (was qwen3-vl-8b before 2026-08-31 v5 model priority change)
  Path 4 (gemma4):  gemma-4-26B-A4B page-level image -> JSON

Per-path DuckLake landing:
  oideachais.education.british_isles.<jurisdiction>.<scope>.<subject>.{baml_canonical,unstract_json,gemma4,gemma4}
  oideachais.education.british_isles.<jurisdiction>.<scope>.<subject>.voted_canonical

RAGAS vote: `biiep_extraction_consensus` ranks the 4 outputs by 3 sub-metrics
(faithfulness, answer_relevance, context_precision) and returns the highest-scoring
output as the canonical BAML object.
"""
