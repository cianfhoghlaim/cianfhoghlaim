# meaisinfoghlaim-ocr-htr Specification

## Purpose
TBD - created by archiving change 2026-08-10-ocr-vision-activation-v1. Update Purpose after archive.
## Requirements
### Requirement: `_run_path_baml()` SHALL call the real BAML function

The `_run_path_baml()` method in `meaisinfoghlaim/ocr/ensemble/ensembled_extractor.py` SHALL:

1. Call `_call_docling(pdf_path, self.docling_url)` to get the raw text
2. Call `from baml_client.baml_client.sync_client import b` to import the BAML client
3. Invoke `getattr(b, baml_function)(text=_docling_text)` (e.g. `b.ExtractCurriculumSyllabus(text=...)`)
4. Serialise the typed result to JSON via `result.model_dump_json()`

**WHEN** a PDF is processed
**THEN** the BAML path SHALL emit a real `EnsemblePathOutput(raw_response=<baml_output_json>, confidence_score=0.85, schema_valid=True)`

#### Scenario: BAML path returns real Pydantic JSON

- **WHEN** the BIEP v2 ensemble processes a PDF
- **AND** the BAML function `ExtractCurriculumSyllabus(text=<docling_text>, subject="chemistry")` is invoked
- **THEN** the result is a Pydantic model with `.model_dump_json()` method
- **AND** `EnsemblePathOutput.raw_response` contains the JSON string

