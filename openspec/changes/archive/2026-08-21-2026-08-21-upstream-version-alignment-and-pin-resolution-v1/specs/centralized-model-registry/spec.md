## ADDED Requirements

### Requirement: Post-v1 OCR ensemble additions (dots.mocr + OlmOCR-2 + PaddleOCR-VL-1.6)

The system SHALL add 3 new OCR/VLM model entries to `MODEL_REGISTRY` per the upstream-version audit (Stedding 2026-08-21):

1. `dots.mocr` (`rednote-hilab/dots.mocr`) — successor to `dots.ocr-1.5`; new SOTA on OmniDocBench v1.5 (1124.7 score). Provider: HF Hub (model pulled at runtime, not in 6-file compose).
2. `olmocr-2` (`allenai/olmocr-2`) — successor to `olmocr`; 8B multimodal with 82.3 olmOCR-bench overall score. Provider: HF Hub.
3. `paddleocr-vl-1.6` (PaddlePaddle) — successor to `paddleocr-vl-1.5`; ships with `paddleocr>=3.0.1` plugin support. Provider: PaddleOCR Python package.

Each entry SHALL retain the canonical 9-attribute shape (key, family, role, unsloth_id, mlx_id, upstream_id, backend, available, notes).

#### Scenario: dots.mocr is queryable and marked available

- **GIVEN** the audit added `dots.mocr` to the OCR ensemble
- **WHEN** the operator runs `python3 -c "from meaisinfhoghlaim.models.registry import MODEL_REGISTRY; e = MODEL_REGISTRY.resolve('ocr_vision', 'primary'); print(e.key)"`
- **THEN** the output is `"dots.mocr"`
- **AND** `e.available is True`
- **AND** the previous primary `dots.ocr-1.5` is marked `available: False` with `notes: 'superseded by dots.mocr — see 2026-08-21-dotsocr-to-dotsmocr-v1'`

#### Scenario: OlmOCR-2 is queryable as alternative

- **WHEN** the operator runs `python3 -c "print(MODEL_REGISTRY.resolve('ocr_vision', 'alternative').key)"`
- **THEN** the output is `"olmocr-2"`
- **AND** the previous alternative `olmocr` is marked `available: False`

#### Scenario: PaddleOCR-VL-1.6 is queryable as supplementary

- **WHEN** the operator runs `python3 -c "print(MODEL_REGISTRY.resolve('ocr_vision', 'supplementary').key)"`
- **THEN** the output is `"paddleocr-vl-1.6"`
- **AND** `e.backend == "paddleocr"`
- **AND** `e.notes` references the `paddleocr>=3.0.1` plugin dependency
