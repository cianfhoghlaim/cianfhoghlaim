# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
# ]
# ///
"""Tutorial 3 (Gaeilge): The vision+PDF extraction pipeline on GA PDFs.

Companion to `03_education_pdf_vision_pipeline.py`. Demonstrates the
Gaeilge (Irish) language path through the same vision+PDF pipeline:

1. `ExtractCurriculumSyllabus` (text; lc_extraction/curriculum_syllabus.baml)
2. `ExtractExamPaperLayout` (text+image refs; lc_extraction/exam_paper_layout.baml)
3. `ExtractSyllabusDiagram` (vision, gemma-4-26B-A4B OR qwen3-vl-8b;
   lc_extraction/exam_paper_layout.baml)
4. `ExtractMarkingSchemeGuideline` (text+grading;
   lc_extraction/marking_scheme.baml)

The GA counterpart focuses on the **Gaeilge NCCA syllabus PDFs** (the
Gaeilge PDFs are the most fully bilingual NCCA document — every page
has both Irish and English text). The side-by-side cell runs the
**same Gaeilge diagram page** through both vision models and emits a
comparison row.

**Gaeilge-specific considerations:**
- Irish text uses the síneadh fada (the acute accent over vowels:
  á, é, í, ó, ú). The vision model must render this correctly.
- The GA page often has the Irish text on the left column and the
  English translation on the right column. Both models need to
  preserve the column structure.
- Gaeilge-specific diagram types: "Léamhthuiscint" (reading
  comprehension) tables, "Filíocht" (poetry) form diagrams,
  "Gramadach" (grammar) parse trees.

Cross-references:
- `.agents/skills/baml/SKILL.md`
- `openspec/changes/2026-07-13-baml-cocoindex-tutorials-ga-v1/` —
  this openspec change

Run via the cianfhoghlaim-marimo CLI:
    uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline_ga
    uv run cianfhoghlaim-marimo run  13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline_ga
"""

from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo

    return (mo,)


@app.cell
def _intro(mo):
    mo.md(
        """
    # Tutorial 3 (GA) — The vision+PDF extraction pipeline on GA PDFs

    The GA counterpart of Tutorial 3. Exercises the same 4
    vision+PDF extraction functions on the **Gaeilge NCCA syllabus
    PDFs**.

    The Gaeilge PDFs are the **most fully bilingual** NCCA documents:
    every page has Irish text (typically the left column) and English
    text (typically the right column). The vision model must preserve
    both columns.

    **What you'll learn:**
    1. How `ExtractCurriculumSyllabus` runs on the Gaeilge NCCA PDF
    2. How `ExtractExamPaperLayout` returns bilingual section metadata
    3. The side-by-side `gemma-4-26B-A4B` vs `qwen3-vl-8b` comparison
       on a Gaeilge diagram page (the síneadh fada + the dual-column
       layout are the key GA-specific challenges)
    4. How `ExtractMarkingSchemeGuideline` extracts bilingual marking
       criteria
    """
    )
    return


@app.cell
def _section_curriculum_ga(mo):
    mo.md(
        """
    ## 1. `ExtractCurriculumSyllabus` on the Gaeilge PDF

    Same function as the English tutorial (`lc_extraction/curriculum_syllabus.baml`),
    but the input PDF is the **Gaeilge NCCA Leaving Certificate Gaeilge
    syllabus** (`leaving-cert-gaeilge-syllabus.pdf`). The function
    returns a `CurriculumSyllabus` object with the strand/outcome
    structure in both Irish (canonical) and English (helper
    translation).

    **GA-specific input:**

    The Gaeilge NCCA syllabus has 8 strands (Léamhthuiscint,
    Litríocht, Gramadach, Filíocht, Prós, Béaloideas,
    Scríbhneoireacht, Cluastuiscint) × 3 levels (FL / OL / HL) =
    24 strand-level combinations. Each carries 8-12 LOs with
    bilingual EN+GA competency text.

    ```baml
    function ExtractCurriculumSyllabus(
      pdf_text: string,
      subject: string?
    ) -> CurriculumSyllabus {
      client default
      prompt #"Extract the NCCA Leaving Certificate syllabus structure from this {{ subject }} PDF: {{ pdf_text }}"#
    }
    ```

    **Cost:** ~4K-8K input + 1K-2K output per syllabus. For the Gaeilge
    PDF specifically, the bilingual structure pushes input tokens
    ~30% higher than the English-only subjects.
    """
    )
    return


@app.cell
def _section_exam_paper_ga(mo):
    mo.md(
        """
    ## 2. `ExtractExamPaperLayout` on the Gaeilge exam paper

    The Gaeilge exam paper PDF has a **2-column layout** (Irish on
    the left, English on the right). The function returns an
    `ExamPaperLayout` with `image_refs: string[]` that point to the
    bilingual question pages.

    ```baml
    function ExtractExamPaperLayout(
      pdf_text: string,
      subject: string?
    ) -> ExamPaperLayout {
      client default
      prompt #"Extract the exam paper structure (sections, questions, marks) from this {{ subject }} PDF: {{ pdf_text }}"#
    }
    ```

    **GA-specific image_refs:**
    - `figure_léamhthuiscint_p12` (reading-comprehension figure)
    - `diagram_filíocht_p15` (poetry form diagram)
    - `table_gramadach_p18` (grammar parse table)

    These are the diagram pages that `ExtractSyllabusDiagram` (next
    section) processes.
    """
    )
    return


@app.cell
def _section_syllabus_diagram_ga(mo):
    mo.md(
        """
    ## 3. `ExtractSyllabusDiagram` on Gaeilge diagram pages

    The signature GA feature: the **same diagram page** (typically a
    poetry-form or grammar-parse diagram) is run through **both**
    vision models, side-by-side.

    ```baml
    function ExtractSyllabusDiagram(
      page_image: image,
      diagram_type: string,
      pointing_model: string        // "gemma-4-26B-A4B" | "qwen3-vl-8b"
    ) -> ExtractedDiagram {
      client <pointing_model>
      prompt #"Extract the diagram structure from this {{ diagram_type }} image: {{ page_image }}"#
    }
    ```

    **GA-specific challenges:**
    - **Síneadh fada:** Irish vowels carry an acute accent (á, é, í, ó, ú).
      The vision model must render these accurately. qwen3-vl-8b
      typically wins on this (favours OCR fidelity).
    - **Dual-column layout:** Irish on the left, English on the right.
      gemma-4-26B-A4B typically wins on this (favours structure).
    - **Gaeilge-specific diagram types:** "Léamhthuiscint" tables,
      "Filíocht" form diagrams, "Gramadach" parse trees.
    """
    )
    return


@app.cell
def _side_by_side_ga_code():
    side_by_side_ga_code = """\
# Side-by-side GA vision comparison
import asyncio
from baml_client.sync_client import b as baml_sync

async def run_ga_side_by_side(page_image: bytes, diagram_type: str) -> dict:
    \"\"\"Run both vision models on the same Gaeilge diagram page.\"\"\"
    gemma4_result = await asyncio.to_thread(
        baml_sync.ExtractSyllabusDiagram,
        page_image=page_image,
        diagram_type=diagram_type,
        pointing_model="gemma-4-26B-A4B",
    )
    qwen3vl_result = await asyncio.to_thread(
        baml_sync.ExtractSyllabusDiagram,
        page_image=page_image,
        diagram_type=diagram_type,
        pointing_model="qwen3-vl-8b",
    )
    return {
        "diagram_type": diagram_type,
        "language": "ga",
        "gemma4": gemma4_result,
        "qwen3vl": qwen3vl_result,
        "gemma4_strength": "structure (dual-column Irish+English layout)",
        "qwen3vl_strength": "OCR (síneadh fada fidelity)",
    }\
"""
    return (side_by_side_ga_code,)


@app.cell
def _render_side_by_side_ga(side_by_side_ga_code, mo):
    mo.md(
        f"""
    ### Side-by-side GA vision comparison code

    ```python
    {side_by_side_ga_code}
    ```

    The cell returns a dict with:
    - `diagram_type` — "Léamhthuiscint" / "Filíocht" / "Gramadach" /
      "Cluastuiscint" / etc.
    - `language` — always `"ga"` for the GA path
    - `gemma4` — the `gemma-4-26B-A4B` extraction result
    - `qwen3vl` — the `qwen3-vl-8b` extraction result
    - `gemma4_strength` — "structure (dual-column Irish+English layout)"
    - `qwen3vl_strength` — "OCR (síneadh fada fidelity)"

    ### Marimo table cell

    ```python
    @app.cell
    def _render_ga_comparison(run_result):
        rows = [
            {
                "diagram_type": run_result["diagram_type"],
                "language": run_result["language"],
                "gemma-4 (structure)": str(run_result["gemma4"]),
                "qwen3-vl (OCR)": str(run_result["qwen3vl"]),
                "match_confidence": compute_jaccard(
                    run_result["gemma4"], run_result["qwen3vl"]
                ),
            }
        ]
        return mo.ui.table(rows, label="GA side-by-side vision comparison")
    ```
    """
    )
    return


@app.cell
def _section_marking_ga(mo):
    mo.md(
        """
    ## 4. `ExtractMarkingSchemeGuideline` on the Gaeilge marking scheme

    The Gaeilge marking scheme PDF carries bilingual marking
    criteria (Irish canonical + English helper). The function returns
    a `MarkingSchemeGuideline` with the per-criterion marks + the
    examiner notes.

    ```baml
    function ExtractMarkingSchemeGuideline(
      pdf_text: string,
      subject: string?
    ) -> MarkingSchemeGuideline {
      client default
      prompt #"Extract the marking scheme criteria + marks + examiner notes from this {{ subject }} PDF: {{ pdf_text }}"#
    }
    ```

    **GA-specific cost:** ~3K-5K input + 0.5K-1K output per marking
    scheme (slightly higher than English-only subjects due to the
    bilingual content).
    """
    )
    return


@app.cell
def _section_outro(mo):
    mo.md(
        """
    ## Next steps

    - **Tutorial 4 (GA)** — `04_cocoindex_baml_integration_ga.py`
      demonstrates the 3 CocoIndex+BAML integration patterns on
      Gaeilge content
    - **Tutorial 5 (GA)** — `05_post_v4_duplicate_audit_and_migration_ga.py`
      audits the bilingual BAML additions

    For the canonical English-language walkthrough of the same
    vision+PDF pipeline, see `03_education_pdf_vision_pipeline.py`.
    """
    )
    return


if __name__ == "__main__":
    app.run()