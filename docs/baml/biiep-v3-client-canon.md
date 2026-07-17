# BIEP v3 canonical BAML clients

Per the **2026-08-07-biep-v3-hardening-v1** change.

The fragmented client setup (`ExtractEn`, `ExtractEnStrong`,
`LlamaSwapClient`, `LocalVision`, etc.) is consolidated into **3
canonical clients** that all active BIEP v3 jurisdiction functions route
through.

## The 3 canonical clients

### 1. `BIEPV3Extract` — light-weight

- **Model:** Gemma 3 4B IT
- **Use case:** Single-shot extraction where latency matters
  (registry queries, primary curriculum)
- **Retries:** 3
- **Timeout:** 60s
- **Max tokens:** 2,048

### 2. `BIEPV3ExtractStrong` — detail-rich

- **Model:** Qwen 3-VL 8B IT
- **Use case:** Multi-shot extraction where fidelity matters
  (curriculum syllabus extraction, marking scheme analysis)
- **Retries:** 3
- **Timeout:** 120s
- **Max tokens:** 4,096

### 3. `BIEPV3Vision` — OCR/VLM ensemble

- **Model:** qwen3-vl-8b via llama-swap
- **Use case:** The 4-path OCR/VLM ensemble (Docling + Unstract + qwen3-vl + gemma4)
- **Retries:** 5
- **Timeout:** 180s
- **Max tokens:** 8,192

## Migration

For each `client ExtractEn` / `client ExtractEnStrong` reference in
BAML function signatures:

- Single-subject quick extraction → `client BIEPV3Extract`
- Multi-step syllabus extraction → `client BIEPV3ExtractStrong`
- OCR/VLM pipeline integration → `client BIEPV3Vision`

## Code example

```baml
// Before:
function ExtractCurriculumSyllabus(pdf_text: string, subject: string?) -> SyllabusDocument {
  client ExtractEn
  ...
}

// After:
function ExtractCurriculumSyllabus(pdf_text: string, subject: string?) -> SyllabusDocument {
  client BIEPV3Extract
  ...
}
```

## Cross-references

- `baml_src/clients_biep_v3.py` (the canonical file)
- `.github/workflows/baml-test.yaml` (the CI gate that enforces this)
- `openspec/changes/2026-08-07-biep-v3-hardening-v1/`
