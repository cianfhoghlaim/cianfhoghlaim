# BIEP v3 — BAML Client (how to invoke the 6 new Extract* functions from Python)

> Per the `2026-08-13-biep-v3-systematic-download-ireland-england-v1`
> openspec change. How to invoke the 6 new BAML `Extract*` functions from
> Python code.

## Overview

The BIEP v3 systematic download plan introduced 6 new BAML
`Extract*` functions (one per deferred jurisdiction) + the existing
`ExtractCurriculumSyllabus` (Ireland LC) + `ExtractUKQualSpec` (England
AQA/OCR/Edexcel). The 6 new functions are:

| Function | Jurisdiction | File | Return type |
|:--|:--|:--|:--|
| `ExtractScotlandSyllabus` | Scotland | `baml_src/british_isles/scotland/education/subject_taxonomy.baml` | `ScotlandSyllabusSpec` |
| `ExtractWalesSyllabus` | Wales | `baml_src/british_isles/wales/education/subject_taxonomy.baml` | `WalesSyllabusSpec` |
| `ExtractNIExamPaper` | Northern Ireland | `baml_src/british_isles/northern_ireland/education/subject_taxonomy.baml` | `NorthernIrelandExamPaper` |
| `ExtractJerseySyllabus` | Jersey | `baml_src/british_isles/jersey/education/subject_taxonomy.baml` | `JerseySyllabusSpec` |
| `ExtractGuernseySyllabus` | Guernsey | `baml_src/british_isles/guernsey/education/subject_taxonomy.baml` | `GuernseySyllabusSpec` |
| `ExtractIsleOfManSyllabus` | Isle of Man | `baml_src/british_isles/isle_of_man/education/subject_taxonomy.baml` | `IsleOfManSyllabusSpec` |

All 6 functions route via the canonical `BIEPV3Extract` client
(post-v3 hardening per the 2026-08-07 change).

## Basic usage (from Python)

```python
from baml_client import b
from baml_client.types import ScotlandSyllabusSpec

# 1. The canonical invocation (from a Dagster asset or a notebook)
result: ScotlandSyllabusSpec = b.ExtractScotlandSyllabus(
    pdf_text=pdf_text,           # The PDF text (extracted via pymupdf)
    subject="MATHEMATICS",     # The SCQFSubject enum
    level="HIGHER",             # The SCQFLevel enum
)
print(result.title)             # "Mathematics Higher"
print(result.total_marks)       # 100
print(result.topics)            # [ScotlandTopic, ...]
```

## Advanced usage (with the 4-path OCR ensemble + RAGAS voting)

The 6 new `Extract*` functions are called by the BIEP v3 4-path OCR
ensemble via `EnsembledExtractor.extract()`. The canonical call pattern
(from the BIEP v3 systematic download plan):

```python
from meaisinfhoghlaim.ocr.ensemble.ensembled_extractor import (
    EnsembledExtractor,
    EnsembleResult,
)

# 1. The 4-path ensemble (per the 2026-07-22 change)
extractor = EnsembledExtractor()
result: EnsembleResult = extractor.extract(
    pdf_path="s3://garage/cianfhoghlaim/scotland/higher/mathematics/2024/a1b2c3d4.pdf",
    baml_function="b.ExtractScotlandSyllabus",  # The per-jurisdiction function
    jurisdiction="scotland",
    scope="education",
    subject="mathematics",
    board="sqa",                  # or "na" for non-board jurisdictions
    qualification_level="higher", # or "untiered"
    language="en",
)

# 2. The result contains per-path rows + the RAGAS-voted_canonical row
print(result.baml_canonical_row)   # Path 1 (Docling → BAML)
print(result.unstract_json_row)    # Path 2 (Docling → Unstract)
print(result.qwen3_vl_row)          # Path 3 (qwen3-vl-8b)
print(result.gemma4_row)           # Path 4 (gemma-4-26B-A4B)
print(result.voted_canonical_row)   # The RAGAS-voted_canonical row
print(result.ragas_score)          # 0.0-1.0 (must be >= 0.70 for the asset check to pass)
```

## Error handling

The 6 new BAML functions return a typed Pydantic model (e.g.
`ScotlandSyllabusSpec`). If the LLM fails to extract a field, the
function raises a `BamlValidationError` with details. The canonical
error handling pattern:

```python
try:
    result = b.ExtractScotlandSyllabus(pdf_text=pdf_text, subject="MATHEMATICS", level="HIGHER")
except Exception as exc:
    # Fall back to the heuristic extractor
    result = heuristic_extract_scotland_syllabus(pdf_text)
    log_warning(f"LLM extraction failed: {exc}; using heuristic fallback")
```

## Testing the 6 new functions

Per the BAML v1 spec, every BAML function MUST have a `Test {function_name} { ... }`
block. The 6 new BAML files have the canonical test blocks (Phase 4 of
this change). To run the tests:

```bash
cd baml_src
uv run baml-cli test
```

## See also

- `docs/agents/biiep-v3-systematic-download.md` — the canonical newcomer guide
- `docs/agents/biiep-v3-quickstart.md` — the "first 30 minutes" guide
- `docs/agents/biiep-v3-faq.md` — the canonical FAQ
- `docs/agents/biiep-v3-storage-layout.md` — the DuckLake + Lance + MotherDuck layout
- `docs/agents/biiep-v3-cron-schedule.md` — the 4-cadence scheduling policy in detail
- `docs/agents/biiep-v3-bie-8-jurisdictions.md` — the 8-jurisdiction rollout + the 2 scanner domains
