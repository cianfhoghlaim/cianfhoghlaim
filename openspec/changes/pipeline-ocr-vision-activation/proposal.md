## Why

The 3 OCR/vision activation changes
(`2026-08-13-ocr-vision-activation-completion-v1`,
`2026-08-10-ocr-vision-activation-v1`,
`2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1`)
share the same vision-stack surface (Pylaia/TrOCR/PaddleOCR/Tesseract
+ dots-ocr + VLM ensemble) and depend on each other's activation
gates. Bundling them records that the vision ensemble is one
milestone, not three independent trackings.

## What Changes

- Adds a cross-batch vision activation contract: the 10 OCR models,
  the 24-model ensemble, and the unsloth-v5 vision LLM SHALL be
  testable as one stack.
- Records the dependency order in `design.md`.

## Capabilities

(none added; pure bundling)

## Impact

- **Affected changes**: 3 bundled
- **Affected code**: none — this change is metadata-only