"""Marimo dashboard for the 6-stage PDF processing pipeline.

Per `openspec/specs/oideachais-pdf-processing/spec.md` — Requirement:
"Marimo dashboard for processed PDFs".

Visualises the 6-stage pipeline state for any (subject, year, paper)
tuple from the `pdf_processing` DuckLake table.

Run with: `marimo edit 03_pdf_processing.py`
"""

import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return (mo,)


@app.cell
def __(mo):
    mo.md(
        """
        # Oideachais PDF Processing Dashboard

        Visualises the 6-stage PDF processing pipeline state for any
        (subject, year, paper) tuple from the `pdf_processing` DuckLake
        table.

        **Pipeline stages:**
        1. OCR (VLM dispatch) — `select_ocr_backend()` from the 24-entry VISION_MODELS registry
        2. Diagram detection — Granite-Docling + Molmo2-8B
        3. BAML extraction — `ExtractLeavingCertSyllabus` / `ExtractPastPaper` / `ExtractMarkingScheme`
        4. Topic validation — fuzzy-match against NCCA taxonomy
        5. Semantic chunking — CocoIndex v1 + BGE-M3
        6. Lakehouse + Cognee + Graphiti — DuckLake + KG + temporal
        """
    )
    return


@app.cell
def __(mo):
    # Sidebar selector for (subject, year, paper)
    subject_selector = mo.ui.dropdown(
        options=[
            "Mathematics",
            "Irish",
            "Biology",
            "French",
            "History",
            "Business",
            "Construction-Studies",
        ],
        value="Mathematics",
        label="Subject",
    )
    year_selector = mo.ui.slider(
        start=2010, stop=2026, step=1, value=2024, label="Year"
    )
    paper_selector = mo.ui.dropdown(
        options=["paper-1", "paper-2", "all"], value="paper-1", label="Paper"
    )
    mo.hstack([subject_selector, year_selector, paper_selector])
    return subject_selector, year_selector, paper_selector


@app.cell
def __(mo, subject_selector, year_selector, paper_selector):
    mo.md(f"## Selected: {subject_selector.value} / {year_selector.value} / {paper_selector.value}")
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Stage 1 — OCR (VLM dispatch)

        Per-page OCR confidence + image preview. The `select_ocr_backend()`
        heuristic dispatches to:

        - `gemma-4-E2B` for small text-first PDFs (<5 MB)
        - `gemma-4-26B-A4B` for dense syllabi (5–20 MB)
        - `qwen3-vl-8b` for SEC exam papers (image-heavy)
        - `glm-4.6v-flash` for pre-1922 scanned Gaelic texts
        - `molmo2-8b` for marking-scheme image-heavy

        *(Stub: the actual model dispatch + per-page preview is loaded
        from `motherduck://oideachais.pdf_processing.{subject}.{year}.{paper}.ocr_pages`)*
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Stage 2 — Diagram detection

        Per-page diagram detection with bounding-box overlay. Uses
        Granite-Docling 258M (DocTags) for layout classification and
        Molmo2-8B (transformers) for figure-region pointing.

        *(Stub: the actual diagram overlays are loaded from
        `motherduck://oideachais.pdf_processing.{subject}.{year}.{paper}.diagrams`)*
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Stage 3 — BAML extraction (typed records)

        BAML extraction preview (first 3 records per stage). Three BAML
        functions are used:

        - `ExtractLeavingCertSyllabus(page_text)` — existing BAML
        - `ExtractPastPaper(page_text)` — existing BAML
        - `ExtractMarkingScheme(page_text)` — new BAML
          (at `cianfhoghlaim/core/baml/_oideachais_src/leaving_cert_marking_scheme_extraction.baml`)

        All clients route through `litellm.cianfhoghlaim.ie:4000` with
        `MiniMaxClient` (vendor-de-risked) → `deepseek/deepseek-chat`
        fallback.
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Stage 4 — Topic validation (NCCA taxonomy)

        Topic validation pass/fail rate + mismatched records. The
        validator fuzzy-matches every BAML record's `topic` field
        against the NCCA syllabus topic list at the 95% threshold.
        Failed records are flagged for human review in the Gradio
        interface at `spaces/oideachais-pdf-review/`.

        *(Stub: actual pass/fail rate + mismatched records are loaded
        from `motherduck://oideachais.pdf_processing.{subject}.{year}.{paper}.validated`)*
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Stage 5 — Semantic chunking (CocoIndex v1 + BGE-M3)

        Chunk count per type + BGE-M3 embedding UMAP projection. The
        chunker respects:

        - **Syllabus:** chunk by topic (one per SyllabusTopic)
        - **Past paper:** chunk by question (one per PastExamQuestion)
        - **Marking scheme:** chunk by marking point (one per MarkingPoint)
        - **Diagrams:** one chunk per figure region (with caption as text)

        Chunk size: 256-1024 tokens (BGE-M3 sweet spot).
        Embedder: `BAAI/bge-m3` (1024-dim, batched 100+).

        *(Stub: actual chunk count + UMAP projection are loaded from
        `lancedb://oideachais.pdf_processing_chunks`)*
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        ## Stage 6 — Lakehouse + Cognee + Graphiti

        Lakehouse row count + Cognee KG node count + Graphiti episode
        count. The final stage writes to:

        - DuckLake: `oideachais.assets.official_documents.{syllabus|past_papers|marking_schemes}.{subject}.{year}.{paper}`
        - Cognee dataset: `oideachais.pdf_processing`
        - Graphiti episode: `{type, subject, year, paper, n_chunks, n_validated, n_mismatched}`

        *(Stub: actual counts are queried from DuckLake + Cognee + Graphiti.)*
        """
    )
    return


if __name__ == "__main__":
    app.run()
