# Spec Delta: meaisinfhoghlaim-ocr-htr

This change modifies the `meaisinfhoghlaim-ocr-htr` capability
(`openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md`) by adding 2
new requirements. The full modified spec lives at
`openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md`.

## ADDED Requirements

### Requirement: 4 OCRAdapter concretes wired to the eval harness

The system SHALL provide the 4 concrete implementations —
`PaddleOCRAdapter`, `DoclingAdapter`, `DotsOCRAdapter`,
`UnstractAdapter` — under the `OCRAdapter` ABC at
`cianfhoghlaim/meaisinfhoghlaim/backends/adapters.py`. All 4
SHALL be wired through `OCRAdapterRegistry.get()` so the canonical
call `compare_ocr_models(image_bytes, models=[...])` returns
`OCRResult` rows for any subset of the 4 backends.

#### Scenario: compare_ocr_models fans out to all 4 adapters

- **GIVEN** an image at `/tmp/lc_chemistry_syllabus_p1.png`
- **WHEN** `compare_ocr_models(image_bytes, models=["paddleocr", "docling", "dots_ocr", "unstract"])`
- **THEN** the result is a `dict[str, OCRResult]` with all 4
  keys present
- **AND** the `OCRResult.backend` value matches the corresponding
  `OCRBackend.PADDLEOCR/DOCLING/DOTS_OCR/UNSTRACT` enum

#### Scenario: Adapter error produces graceful empty result

- **WHEN** an adapter raises a network error
- **THEN** the corresponding `OCRResult` has `status="error"`
  and `error=str(exc)`
- **AND** the other adapters continue to run (parallel
  fan-out is best-effort)

### Requirement: Classical OCR evaluation uses the OCRAdapter registry

The system SHALL route every `ClassicalOCRStack.stack_name` to
one of the 4 `OCRAdapter` concretes via
`_CLASSICAL_ADAPTER_FOR_STACK` from
`meaisinfhoghlaim/evaluation/compare.py:_run_classical_eval()`.
The `_run_classical_eval()` function MUST be the canonical
entry point for any classical OCR evaluation — Plan 1 (~220
evals across 16 corpora) and any future corpus evaluation.

#### Scenario: Classical OCR plan 1 eval uses the wired adapters

- **GIVEN** the Plan 1 corpora (6 leabharlann subdirs + 10 IE
  education stages × 2 languages)
- **WHEN** `run_plan1_eval(output_path)` runs
- **THEN** each `_run_classical_eval(stack, corpus, document)`
  invocation returns a well-formed `EvalSample`
- **AND** at least 1 of the 4 adapters is exercised per
  stack name

## Cross-references

- [`cianfhoghlaim/meaisinfhoghlaim/backends/adapters.py`](../../../cianfhoghlaim/meaisinfhoghlaim/backends/adapters.py)
- [`cianfhoghlaim/meaisinfhoghlaim/evaluation/compare.py`](../../../cianfhoghlaim/meaisinfhoghlaim/evaluation/compare.py)
- [`openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md`](../meaisinfhoghlaim-agent-frameworks/spec.md) (the eval harness consumer)
