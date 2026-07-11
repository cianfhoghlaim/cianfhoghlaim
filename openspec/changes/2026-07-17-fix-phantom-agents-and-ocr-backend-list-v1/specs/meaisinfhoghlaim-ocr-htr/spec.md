# Spec Delta — meaisinfhoghlaim-ocr-htr

This delta adds one new requirement to the existing
`meaisinfhoghlaim-ocr-htr` capability. Existing requirements are
preserved unchanged.

## ADDED Requirements

### Requirement: Canonical 6 OCR backends registered in `CLASSICAL_OCR`

The system SHALL register the canonical 6 OCR backends in
`cianfhoghlaim.meaisinfhoghlaim.ocr.models.registry:CLASSICAL_OCR`
(the v4 platform-spec source of truth for classical OCR Docker
stacks).

The 6 canonical backends (the user-cited source of truth) are:

1. **`docling-serve`** — IBM Docling (258M params, DocTags layout,
   the "safety net" when VLM extraction fails; port 5001)
2. **`paddleocr`** — PaddlePaddle OCR (multilingual, first-party
   GGUF; port 8888)
3. **`dots-ocr`** — rednote-hilab Dots-OCR (3.0B layout specialist;
   port 8001)
4. **`unstract`** — Unstract (no-code LLM-powered document
   extraction; port 8002)
5. **`tesseract`** — Tesseract 4 (clean printed-text baseline;
   port 8889)
6. **`tesseract-shadow`** — Tesseract 4 shadow variant (A/B
   comparison + drift detection; port 8890)

The legacy 6 backends (`docling-serve`, `paddleocr`, `olmocr`,
`tesseract`, `pylaia`, `dots-ocr`) are superseded. Pylaia remains
available as a Dúchas HTR specialist via `tuatha_root_agent` for
the historical Irish-manuscript corpus (see
`openspec/specs/cianfhoghlaim-educational-mmo/spec.md`); olmocr
is no longer a canonical OCR backend (its 7B math-OCR capability
is covered by the `gemma-4-26B-A4B` VLM via llama-swap, per the
`meaisinfhoghlaim-ocr-htr` "24-model 4-backend v4 registry"
requirement).

Each `CLASSICAL_OCR` entry SHALL be a `dict[str, Any]` with the
canonical 4-key schema (`stack`, `image`, `port`, `notes`).

#### Scenario: CLASSICAL_OCR contains exactly the 6 canonical backends

- **WHEN** `from cianfhoghlaim.meaisinfhoghlaim.ocr.models.registry import CLASSICAL_OCR`
- **THEN** `len(CLASSICAL_OCR) == 6`
- **AND** `set(CLASSICAL_OCR.keys()) == {"docling-serve", "paddleocr", "dots-ocr", "unstract", "tesseract", "tesseract-shadow"}`

#### Scenario: unstract is registered with the canonical port + image

- **GIVEN** `CLASSICAL_OCR["unstract"]`
- **THEN** `CLASSICAL_OCR["unstract"]["port"] == 8002`
- **AND** `CLASSICAL_OCR["unstract"]["stack"] == "infrastructure/stacks/ocr-classical/unstract/"`
- **AND** `CLASSICAL_OCR["unstract"]["image"] == "docker.io/unstract/api:latest"`

#### Scenario: tesseract-shadow is registered with the canonical port + image

- **GIVEN** `CLASSICAL_OCR["tesseract-shadow"]`
- **THEN** `CLASSICAL_OCR["tesseract-shadow"]["port"] == 8890`
- **AND** `CLASSICAL_OCR["tesseract-shadow"]["stack"] == "infrastructure/stacks/ocr-classical/tesseract-shadow/"`

#### Scenario: legacy olmocr + pylaia are removed from CLASSICAL_OCR

- **WHEN** `"olmocr" in CLASSICAL_OCR` is evaluated
- **THEN** it returns `False`
- **AND** `"pylaia" in CLASSICAL_OCR` returns `False`

#### Scenario: each canonical backend has the 4-key schema

- **WHEN** each `CLASSICAL_OCR[k]` is inspected
- **THEN** `set(CLASSICAL_OCR[k].keys()) == {"stack", "image", "port", "notes"}`
- **AND** `isinstance(CLASSICAL_OCR[k]["port"], int)`
- **AND** `isinstance(CLASSICAL_OCR[k]["stack"], str)`
- **AND** `isinstance(CLASSICAL_OCR[k]["image"], str)`
- **AND** `isinstance(CLASSICAL_OCR[k]["notes"], str)`