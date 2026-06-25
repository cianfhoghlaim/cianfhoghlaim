# Tracking Issue — Unread PDFs in the `culture_heritage` Dataset

**Filed:** 2026-06-25
**Filed by:** build agent (extend-culture-heritage-to-8-articles)
**Status:** OPEN — awaiting follow-up agent with PDF input support

## Summary

2 PDFs in the `culture_heritage` corpus cannot be read by the current agent's PDF input pipeline. Their content is therefore absent from the `culture_heritage` Cognee dataset and from the `culture_heritage_chunks` LanceDB table. The README's "On the claim" subsection (lines 455–465) explicitly notes this gap.

## The 2 unread PDFs

### PDF 1 — Cooke's Corner / Galway Advertiser (August 1986)

- **Path:** `leabharlann/gemini_deep_research/culture/neil_deacy_cookes_corner-galway_advertiser.pdf`
- **Reason unreadable:** current agent's PDF parser returned an empty body
- **Why it matters:** the *Cooke's Corner* column in the *Galway Advertiser* covered the inaugural **Streets of Galway 8 km road race** in August 1986. Neil Deacy (the author's late grandfather) was a competitor in that inaugural race. The article is the primary source for Neil's appearance in the race and for the establishment of the Streets of Galway event.
- **Expected size on disk:** ~ 200-400 KB (single-page newspaper scan)
- **Expected content:** a 600-word *Cooke's Corner* column, likely with 1-3 references to Neil Deacy by name, possibly a finishing position in the 8 km race.
- **Action for follow-up agent:**
  1. Re-read with a PDF parser that supports OCR (Tesseract, PaddleOCR, or one of the `sruth/meaisinfhoghlaim/ocr/` models — olmocr-7b or qwen2.5-vl-7b are recommended).
  2. If the scan is image-only (no text layer), use a VLM to extract the text via the `baml:ExtractCultureClaims` function (the schema already accepts scanned-PDF input).
  3. Append the extracted claim(s) to `culture_heritage` Cognee dataset with `evidence_quality = PRIMARY` (newspaper source).
  4. Update the corresponding fixture `sruth/oideachais/dlt_sources/official_media/fixtures/identity_neil_deacy_cookes_corner.json` (does not yet exist — create with the SHA-256 of the clipped text).

### PDF 2 — Old passports (dual ROI/UK citizenship verification)

- **Path:** `cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf`
- **Reason unreadable:** current agent's PDF parser returned an empty body
- **Why it matters:** the dual ROI/UK citizenship scan is the primary documentary evidence for the author's claim of *Born a British citizen and obliged by oath of allegiance to King Charles the Third* (README line 596). The scan shows both passports side-by-side with the same photograph and signature, establishing the dual citizenship status.
- **Expected size on disk:** ~ 300-600 KB (two-page document scan)
- **Expected content:** page 1 = Republic of Ireland passport (current or expired); page 2 = United Kingdom passport (current or expired); both with same photograph, same signature, same name ("Cian Mac an Déisigh Uí Liatháin" or the anglicised form).
- **Action for follow-up agent:**
  1. **CAUTION — PII**: this PDF contains a passport scan with full name, photograph, signature, and passport number. **DO NOT** log the passport numbers in plain text; redact before any storage.
  2. Re-read with a privacy-preserving OCR pipeline that supports `redactPII: true` (Firecrawl MCP supports this flag).
  3. The Cognee cognify pass for `culture_heritage` should accept the redacted text and extract the `(person, citizenship, claim)` triple without storing the passport numbers.
  4. Append to `culture_heritage` Cognee dataset with `evidence_quality = PRIMARY` (government-issued identity document).

## Why these PDFs were unreadable

The current agent's PDF input pipeline (configured via the opencode tool configuration) returns empty bodies for image-only PDFs without a text layer. The fix is to either:

1. **Re-OCR the PDFs** with one of the 10 OCR models in `sruth/meaisinfhoghlaim/ocr/` (recommended: `olmocr-7b` for accuracy-critical Irish-language content, or `qwen2.5-vl-7b-mlx` for on-device M4 MacBook execution).
2. **Pipe through Firecrawl** with `parsers: ["pdf"]` and `redactPII: true` (for PDF 2).
3. **Hand-convert** the scans to text via `tesseract <pdf> <output>` with `--psm 6` (uniform block of text) for newspaper-column PDFs (PDF 1).

## Cross-references

- README lines 455–465: the "Note on 2 unreadable PDFs" section.
- `openspec/changes/extend-culture-heritage-to-8-articles/proposal.md`: the originating change.
- `sruth/oideachais/cognee_integration/culture_cognify.py`: the Cognee adapter that will accept the new claims on next run.
- `sruth/oideachais/baml_src/culture_extraction.baml`: the BAML extraction schema (`ExtractCultureClaims`).
- `.agents/skills/celtic-ocr-evaluation/SKILL.md`: the OCR evaluation harness for the 9 OCR models.