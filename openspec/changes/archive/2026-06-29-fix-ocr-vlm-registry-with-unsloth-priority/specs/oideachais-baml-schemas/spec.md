# Spec Delta: oideachais-baml-schemas

## ADDED Requirements

### Requirement: 2 new BAML files for PDF processing

The system SHALL provide 2 new BAML files for the 6-stage PDF processing pipeline:

1. **`leaving_cert_marking_scheme_extraction.baml`** (NEW, at `cianfhoghlaim/core/baml/_oideachais_src/`) — extracts `MarkingPoint` records from SEC marking-scheme PDFs. Classes: `MarkingPoint`, `MarkingScheme`, `MarkingType` enum. Function: `ExtractMarkingScheme(pdf_text: string) -> MarkingScheme`.

2. **`clients_llama_swap.baml`** (NEW, at `cianfhoghlaim/core/baml/_oideachais_src/`) — defines the `LlamaSwapClient` for routing BAML extraction calls through the local llama-swap server (which serves Unsloth GGUFs at `http://llama-swap:8080/v1/chat/completions`). Default model: `qwen3-vl-8b` (for figure captioning), `gemma-4-12B` (for general extraction), `deepseek-ocr-2` (for formula OCR).

The 2 new files augment the existing 9 BAML files in `cianfhoghlaim/core/baml/_oideachais_src/` (the 9 existing files include `leaving_cert_syllabus_extraction.baml`, `leaving_cert_past_paper_extraction.baml`, `clients.baml`, etc.).

#### Scenario: A marking scheme is extracted via the new BAML schema

- **GIVEN** a 2024 LC Maths marking scheme PDF text
- **WHEN** `b.ExtractMarkingScheme(pdf_text)` is called
- **THEN** the response is a `MarkingScheme` Pydantic object with 18 `MarkingPoint` records
- **AND** the BAML client is `LitellmClient` (routed via `litellm.cianfhoghlaim.ie:4000`)

#### Scenario: A BAML extraction routes through llama-swap for VL tasks

- **GIVEN** Stage 2 needs to caption a detected figure region
- **WHEN** `b.ExtractFigureCaption(image_bytes)` is called
- **THEN** the `LlamaSwapClient` routes to `qwen3-vl-8b` via `http://llama-swap:8080/v1/chat/completions`
- **AND** the response is parsed into a `FigureCaption` Pydantic record
