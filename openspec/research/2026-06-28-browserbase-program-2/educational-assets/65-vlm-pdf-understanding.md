# 65 — VLM PDF Page Understanding (Design Spec)

**Agent 65 of 65 — vlm-pdf-understanding** · 2026-06-28 · Wave 3 design
**Inputs:** `synthesis/27-feature-backlog.md` (F-10 multimodal search hook), `agent-15-baml.md` (BAML `baml_py.Pdf.from_base64()`), `agent-19-unsloth.md` (Gemma 4 / Qwen3.6 vision), `stacks/docling-serve/` (port 5001), `ocr/document_factory/` (5 converters including `docling_converter.py`)
**Output budget:** ≤ 350 lines · 1 PR

---

## 1. TL;DR

Current PDF processing is **text-extraction only** (Docling → markdown, then BAML extracts text-derived fields). We need **page-understanding** — figures, diagrams, tables, math equations, and layout structure (bounding boxes, reading order) — so the curriculum pipeline can answer "what is the diagram in Question 2(b)?" not just "what does Question 2(b) say?". Pick **Docling** as the primary VLM (already in `docling-serve` stack on port 5001, already imported in `document_factory/converters/docling_converter.py:55`); keep **OlmOCR** as the cloud-burst fallback for >100-page documents; reject **Unstract** (it is a workflow orchestrator, not a VLM — wrong category). Output as DocTags XML (Docling native) → BAML `Pdf` multimodal input → 5-stage Dagster pipeline. Cost: $0 locally vs ~$0.0004/call if we had picked a cloud VLM — we didn't.

---

## 2. What VLM PDF understanding is (beyond text extraction)

| Capability | Text extraction (today) | VLM page understanding (proposed) |
|:--|:--|:--|
| **Reading order** | Implicit in `export_to_markdown()` (Docling's `document_converter.py:55`) | Explicit per-block with bounding boxes (`doc.pages[].blocks[].bbox`) |
| **Figures / diagrams** | Dropped to `[Image: ...]` placeholder | Cropped image bytes + caption + `figure_id` + cross-reference to the question that contains it |
| **Tables** | Markdown table (lossy) | Structured `Table.export_to_dataframe()` with cell-level bbox and header detection |
| **Math equations** | LaTeX lost; rendered as Unicode | LaTeX preserved (`equations[i].latex`) + `equation_id` linked to surrounding prose |
| **Reading-order across columns** | Heuristic (often wrong for newspaper-style) | Layout-aware with `reading_order` graph |
| **Section hierarchy** | Flat markdown headings | Nested `doc.sections[]` tree with `level`, `parent_id`, `children_ids` |
| **Confidence per block** | None | Per-block `confidence: float` (Docling's `predictions`) |
| **Multi-language** | Joined text only | Per-block `lang` detection (Irish vs English on bilingual papers) |

The KCG use case: Leaving Cert exam papers (`examinations.ie` PDF → `DocumentSource.SEC` in `base.py:23`) contain a question, a diagram, and a marking-scheme table interleaved. **Without VLM page understanding, the BAML extractor sees a flat text blob and cannot associate the diagram with the question.** With DocTags XML, BAML can consume `<figure id="fig-2b-1" attached_to="q2b">` directly.

---

## 3. Docling vs OlmOCR vs Unstract

| Dimension | **Docling** (IBM, Apache-2.0) | **OlmOCR** (Allen AI, Apache-2.0) | **Unstract** (AGPL-3, paid cloud) |
|:--|:--|:--|:--|
| **Architecture** | Local-first, 258M param Granite-Docling model + MLX backend; also PyTorch | Local-first, 7B Qwen2-VL fine-tune; CLI + Python SDK | Hosted API only; workflow-orchestrator wrapper around multiple VLMs (no model of its own) |
| **Output** | DocTags XML (richest), Markdown, JSON, DoclingDocument | Plain markdown + page-level JSON bbox | Plain text + JSON via LLM-prompt |
| **Layout / bbox** | ✅ Per-block, per-cell, per-figure | ✅ Per-block | ❌ Text only |
| **Tables** | ✅ `export_to_dataframe()`, header detection | ⚠️ Markdown only | ❌ |
| **Math (LaTeX)** | ✅ `equations[i].latex` | ❌ | ❌ |
| **Figures / crops** | ✅ `figure.crop_image()` returns PIL.Image | ❌ | ❌ |
| **Reading order** | ✅ Graph-based | Heuristic | Heuristic |
| **KCG install footprint** | ✅ `stacks/docling-serve/` already running on port 5001; `document_factory/converters/docling_converter.py:55` already imports it | ❌ New dep, ~13 GB Qwen2-VL weights | ❌ SaaS-only, requires `UNSTRACT_API_KEY` |
| **Cost** | $0 (local, mlx-omni on M4) | $0 (local) but 7B model = 14 GB RAM | $0.0004/call cloud (per task brief) |
| **License** | Apache-2.0 ✅ KCG-compatible | Apache-2.0 ✅ | AGPL-3 ⚠️ viral; not KCG-compatible |
| **License whitelisted upstream** | ✅ `infrastructure-stacks/AGENTS.md` | ❌ Not in stack registry | ❌ Not in stack registry |
| **KCG 5-stage pipeline fit** | ✅ Already at stage 1 (PDF → DocTags) | ⚠️ Would need a new wrapper | ❌ Wrong category |
| **Mature / actively maintained** | ✅ v2.x mid-2026, MLX backend | ⚠️ Early 2026 release, 1.5k★ | ✅ Mature but commercial-led |

**The 5 stages of the KCG PDF pipeline (already partial):**
1. **Ingest** — dlt `@dlt.incremental` on S3/Leabharlann/curriculumonline (`dlt/SKILL.md`).
2. **Convert** — `docling-serve:5001/v1/convert/source` → DocTags XML. ← **Docling excels here**.
3. **Extract** — BAML `ExtractEnStrong` with `Pdf.from_base64()` input consuming the DocTags (`_oideachais_src/curriculum_extraction.baml:775` `LazyExtractExamPaper`).
4. **Embed** — `oideachais-semantic-search` (CocoIndex v1, `bge-m3`) over the structured output.
5. **Evaluate** — RAGAS `asset_check` (every 5th doc) with VLM-derived figure/equation ground truth.

**Why not Unstract:** Unstract is a no-code LLM-extraction workflow product. It does not have its own VLM — it wraps other vendors (Anthropic, OpenAI, Mistral). The task brief explicitly excludes anthropic/openai. Unstract's only KCG-acceptable mode would be wrapping our local Docling, which is two layers of indirection for zero benefit. **Reject.**

**Why OlmOCR is the cloud-burst fallback, not primary:** OlmOCR (Allen AI, June 2026) is a strong 7B Qwen2-VL fine-tune for academic PDFs, but it lacks (a) figure cropping, (b) table-to-DataFrame, (c) LaTeX equation export, (d) MLX backend for M4. Useful only when we have a >100-page dense academic PDF (e.g. `leabharlann` arXiv papers) where Docling's 258M model is too weak. Wire as **fallback chain**: Docling first, OlmOCR if `len(pdf.pages) > 100 and not has_structured_tables`.

---

## 4. Recommended choice — **Docling as primary**

**Docling is the primary VLM for 5 reasons:**

1. **Already deployed.** `cianfhoghlaim/stacks/docling-serve/compose.yaml:16` runs `ghcr.io/ds4sd/docling-serve:latest` on port 5001, with `DOCLING_SERVE_ARTIFACTS_PATH=/home/docling/models` and the `stedding/huggingface` volume mounted. The `document_factory/converters/docling_converter.py:55` Python wrapper already imports `docling.document_converter`. The cutover is *wrapping*, not deploying.
2. **Output format (DocTags XML) is the right substrate for BAML.** Docling's `export_to_doctags()` produces `<figure>`, `<equation>`, `<table>`, `<section_header>` with explicit IDs and bounding boxes — BAML can `@check` that every question has an `attached_figure_id` if the layout is known. Pure markdown loses this.
3. **MLX backend on M4.** Granite-Docling 258M runs on Apple Silicon via `mlx-omni` (Agent 20 stack). $0 marginal cost; no API rate limits; deterministic latency.
4. **Apache-2.0 license, KCG whitelisted.** Listed in `stacks/` registry; not a new vendor onboarding.
5. **Fits the existing `DocumentConverter` ABC** (`base.py:86`). Adding `VLMConverter` mixin (a) calls Docling serve via HTTP, (b) parses DocTags XML, (c) populates the new `page_understanding: dict` field on `ExtractionResult` (`base.py:48`).

**Cutover design:** Add a new `VlmDoclingConverter` class alongside `DoclingConverter` in `document_factory/converters/vlm_docling_converter.py`. The existing `DoclingConverter` (text-only markdown path) becomes the *fast path* for dlt incremental loads where we only need text. The new `VlmDoclingConverter` is the *rich path* for the 5-stage VLM pipeline.

---

## 5. Integration with BAML

The DocTags XML output is the **multimodal input** to BAML extraction. BAML's `baml_py.Pdf.from_base64()` (per Agent 15 env table) accepts raw PDF, but a richer path is to send DocTags XML as a `string` to a new BAML function that has been trained on the tag structure.

```baml
// New file: _oideachais_src/vlm_pdf_extraction.baml
class FigureExtraction {
  figure_id     string  @description("DocTags <figure id='...'> attribute")
  caption       string? @description("DocTags <caption> child, may be null for unlabeled figures")
  attached_to   string? @description("DocTags <attached_to> ref, e.g. 'q2b' — question ID this figure illustrates")
  bbox          BoundingBox? @description("DocTags <figure bbox='x0,y0,x1,y1'>")
  crop_b64      string? @description("Base64-encoded PNG of the cropped figure region, for downstream embedding")
}

class EquationExtraction {
  equation_id   string
  latex         string  @description("Preserved LaTeX from DocTags <equation>")
  attached_to   string?
}

class TableExtraction {
  table_id      string
  headers       string[]
  rows          string[][]
  bbox          BoundingBox?
}

class BoundingBox {
  x0 float
  y0 float
  x1 float
  y1 float
}

class VlmExtractionResult {
  figures       FigureExtraction[]   @assert(has_unique_ids, {{ this|map(attribute='figure_id')|unique|length == this|length }})
  equations     EquationExtraction[] @assert(has_unique_ids, {{ this|map(attribute='equation_id')|unique|length == this|length }})
  tables        TableExtraction[]
  page_count    int
  doctags_xml   string               @description("Original DocTags XML, retained for audit + RAGAS ground truth")
}

function ExtractVlmPage(
  doctags_xml: string,
  page_number: int,
  subject_context: string
) -> VlmExtractionResult {
  client ExtractEnStrong
  prompt #"
    You are an expert curriculum analyst. Parse the DocTags XML for page {{ page_number }}
    of a {{ subject_context }} document. Extract every figure, equation, and table with
    its associated question/paragraph ID (the `attached_to` attribute, if present).
    Preserve LaTeX verbatim for equations. Preserve all header cells for tables.
    {{ ctx.output_format }}
    DocTags:
    --- {{ doctags_xml }} ---
  "#
}

test ExtractVlmPageIrishHistory {
  functions [ExtractVlmPage]
  args {
    doctags_xml #" <page number='3'> <section_header>...</section_header> <figure id='fig-2b-1' attached_to='q2b' bbox='120,400,500,800'>...</figure> <equation id='eq-2b-1' attached_to='q2b'>\\sin(\\theta) = \\frac{opp}{hyp}</equation> </page> "#
    page_number 3
    subject_context "Leaving Cert Irish History — document analysis question"
  }
}
```

**Why DocTags XML → BAML `string` rather than `Pdf.from_base64()`:**
- BAML's `Pdf` type re-OCR's the page internally — double work if Docling already parsed it.
- DocTags carries the structure BAML needs to ground extractions in figure/equation IDs.
- The `doctags_xml` field is retained on the result for **RAGAS ground truth** — when a figure-caption extraction is wrong, the auditor can diff against the XML.

**The 5-stage pipeline becomes:**
1. dlt ingests PDF (unchanged)
2. `VlmDoclingConverter` → `ExtractionResult` with `metadata["doctags_xml"]`
3. BAML `ExtractVlmPage` consumes DocTags → structured `VlmExtractionResult`
4. CocoIndex v1 `vlm_pdf_embedding` App embeds `figure.caption + figure.crop_b64` (ColPali) + `equation.latex` into LanceDB (links to F-10 multimodal search)
5. RAGAS `asset_check` compares BAML `attached_to` against DocTags `<attached_to>` ground truth

---

## 6. Cost analysis

| Option | Per-page cost | 1,000 pages | 10,000 pages | Comments |
|:--|--:|--:|--:|:--|
| **Docling (local, M4 MLX)** | **$0** | $0 | $0 | Granite-Docling 258M, mlx-omni backend. ~3 sec/page. Marginal electricity only. |
| **Docling (CPU fallback)** | $0 | $0 | $0 | PyTorch backend, ~12 sec/page. No GPU required. |
| **OlmOCR (local)** | $0 | $0 | $0 | 7B Qwen2-VL. ~14 GB RAM. Only if Docling's 258M is too weak. |
| **Anthropic Claude Sonnet 4 (cloud, REJECTED per task brief)** | $0.003/page (PDF input) | $3.00 | $30.00 | Best quality; rejected for vendor lock-in. |
| **OpenAI GPT-4o (cloud, REJECTED per task brief)** | $0.0025/page | $2.50 | $25.00 | Rejected for vendor lock-in. |
| **Unstract (cloud, REJECTED)** | $0.0004/call (task brief estimate) | $0.40 | $4.00 | Cheapest *but* wraps cloud VLMs internally (so its real cost is the wrapped VLM + Unstract's margin). Wrong category. |

**The 5-year TCO argument:** A Leaving Cert cycle has ~150 papers (50 subjects × 3 years). A curriculum online corpus is ~5,000 PDFs. A leabharlann arXiv corpus is ~10,000 PDFs. Total ~15,000 PDFs in steady state. At cloud-VLM pricing: $30–$50/year. At local Docling: $0 + 1 day/week of `bunchloch` M4 idle time that we'd burn anyway. **The local path wins by 1 order of magnitude on cost and 2 orders of magnitude on data-residency grounds** (Irish education PDFs do not leave the EU).

**The 0.0004-per-call figure in the task brief is for Unstract. We reject Unstract anyway (wrong category, AGPL-3).**

---

## 7. Cutover — 1 PR

**PR title:** `feat(ocr+core/baml): VLM page understanding via Docling DocTags → BAML ExtractVlmPage (F-10 prerequisite)`

**Files changed (5 files, ~280 lines net):**

| File | Change | Lines |
|:--|:--|--:|
| `cianfhoghlaim/ocr/document_factory/document_factory/converters/vlm_docling_converter.py` | **NEW** — calls `docling-serve:5001/v1/convert/source`, parses DocTags XML, returns `ExtractionResult` with `metadata["doctags_xml"]` + `metadata["figures"]` + `metadata["equations"]` + `metadata["tables"]` | +180 |
| `cianfhoghlaim/ocr/document_factory/document_factory/base.py` | Add `doctags_xml: str = ""` and `page_understanding: dict = field(default_factory=dict)` to `ExtractionResult` | +3 |
| `cianfhoghlaim/ocr/document_factory/document_factory/pdf_factory.py` | Register `VlmDoclingConverter` in the converter list; `get_best_converter()` prefers it when `metadata.requires_vlm == True` | +15 |
| `cianfhoghlaim/core/baml/_oideachais_src/vlm_pdf_extraction.baml` | **NEW** — `FigureExtraction` / `EquationExtraction` / `TableExtraction` / `BoundingBox` / `VlmExtractionResult` classes + `ExtractVlmPage` function (see §5) + 2 test blocks (Irish History + Maths) | +90 |
| `openspec/changes/2026-06-28-vlm-pdf-understanding/proposal.md` | **NEW** change: spec delta adding the VLM page understanding capability to `meaisinfoglaim-ocr-htr` + `oideachais-baml-schemas` | +60 |

**Validation:**
- `openspec validate 2026-06-28-vlm-pdf-understanding --strict` (required per `openspec/AGENTS.md`)
- `mise run turbo test` — BAML `baml-cli test` runs the 2 new `ExtractVlmPage` tests; OCR tests run the new converter on `stedding/ingest_queue/sample_lc_higher_maths_2024.pdf` and assert `len(metadata["figures"]) > 0`.
- `mise run ccc:index` — re-index the codebase.
- 1 RAGAS eval run (5 sample exam papers) — verify `ExtractVlmPage` matches DocTags ground truth on `attached_to` joins.

**Effort:** 1 day (1 agent, 1 PR). This is the F-10 multimodal search *prerequisite*; F-10 itself stays separate and rides on the CocoIndex App that consumes `figure.crop_b64` + `figure.caption`.

**Anti-patterns to avoid:**
1. ❌ Don't re-OCR via `baml_py.Pdf.from_base64()` — pass the DocTags XML as a `string` instead.
2. ❌ Don't pick Anthropic/OpenAI cloud VLMs for PDF understanding — the task brief excluded them and the cost + data-residency argument is decisive.
3. ❌ Don't pick Unstract — wrong category (workflow orchestrator, not VLM) and AGPL-3 is viral.
4. ❌ Don't pick OlmOCR as primary — only as fallback for >100-page dense academic PDFs.
5. ❌ Don't use the new `VlmDoclingConverter` for dlt incremental loads — keep `DoclingConverter` (text-only) for those; the VLM path is for the explicit page-understanding stage.
6. ❌ Don't re-export DocTags as plain markdown — the XML is the substrate; markdown loses the IDs and bbox.
7. ❌ Don't inline `client "anthropic/..."` in the new BAML file — use `client ExtractEnStrong` (per Agent 15 anti-pattern #1).
8. ❌ Don't add the VLM converter to `get_best_converter()`'s default selection — it must be opt-in via `metadata.requires_vlm=True` to avoid 3× cost on every dlt incremental run.

---

## 1-paragraph summary

The current pipeline extracts PDF text only via `DoclingConverter`; we need **VLM page understanding** so figures, diagrams, tables, and LaTeX equations are associated with the questions that contain them, not lost as `[Image: ...]` placeholders. We pick **Docling** as the primary VLM (already in `stacks/docling-serve` on port 5001, already imported in `document_factory/converters/docling_converter.py:55`, Apache-2.0 whitelisted, $0 marginal cost via MLX on M4), keep **OlmOCR** as the cloud-burst fallback for >100-page dense academic PDFs, and reject **Unstract** (workflow orchestrator, not VLM; AGPL-3 viral). Docling's native **DocTags XML** output — with explicit `<figure>`, `<equation>`, `<table>` IDs and bounding boxes — feeds a new BAML function `ExtractVlmPage` (using `client ExtractEnStrong`, not inline `anthropic/...`) that produces structured `FigureExtraction[]`, `EquationExtraction[]`, and `TableExtraction[]` for CocoIndex v1 embedding (F-10 multimodal search prerequisite) and RAGAS ground truth. Cost: $0 local vs $25–$50/yr for cloud VLMs (rejected per task brief); 5-year TCO favours local by 1 order of magnitude on cost and 2 orders of magnitude on data residency. Cutover is **1 PR, 5 files, ~280 net lines**: new `VlmDoclingConverter` + new BAML `vlm_pdf_extraction.baml` + small `ExtractionResult` extension + `pdf_factory.py` opt-in registration + `openspec` change proposal. Effort: 1 day.
