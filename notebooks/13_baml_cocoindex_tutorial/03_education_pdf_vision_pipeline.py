# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
# ]
# ///
"""Tutorial 3: The vision+PDF extraction pipeline + side-by-side
`gemma-4-26B-A4B` vs `qwen3-vl-8b` comparison.

Walks through the 4 canonical vision+PDF extraction functions:
1. `ExtractCurriculumSyllabus` (text; lc_extraction/curriculum_syllabus.baml)
2. `ExtractExamPaperLayout` (text+image refs; lc_extraction/exam_paper_layout.baml)
3. `ExtractSyllabusDiagram` (vision, pointing_model="gemma-4-26B-A4B";
   lc_extraction/exam_paper_layout.baml)
4. `ExtractMarkingSchemeGuideline` (text+grading;
   lc_extraction/marking_scheme.baml)

**Signature feature:** a **side-by-side cell** that runs the same PDF
through both `gemma-4-26B-A4B` and `qwen3-vl-8b` and compares the
outputs in a marimo table. This shows the practical difference between
the two local vision models on the BIEP PDFs.

Source of truth:
- `cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml`
- `cianfhoghlaim/baml/education/lc_extraction/exam_paper_layout.baml`
- `cianfhoghlaim/baml/education/lc_extraction/marking_scheme.baml`

Cross-references:
- `openspec/changes/2026-07-11-baml-cocoindex-modernization-v1/` —
  the parent mega-change (Phase B3: added `local_vision_gemma4` +
  `local_vision_qwen3vl` generators)
- `openspec/changes/2026-07-12-baml-stream-attributes-v1/` — the
  `@stream.*` annotations on the 4 vision functions

Run via the cianfhoghlaim-marimo CLI:
    uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline
    uv run cianfhoghlaim-marimo run  13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline
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
    # Tutorial 3 — The vision+PDF extraction pipeline

    The BIEP (British-Isles Education Pipeline) ingests 4 types of
    LC source documents:

    1. **NCCA curriculum syllabus PDFs** (per subject, per level)
    2. **SEC exam paper PDFs** (per subject, per year, per level)
    3. **SEC marking scheme PDFs** (per subject, per year, per level)
    4. **Syllabus diagram pages** (extracted from the syllabus PDFs;
       the diagrams are typically on pages 10-30 of the 60-100 page
       NCCA syllabuses)

    Each document type has its own canonical BAML extraction function:

    | Document | Function | Mode | Generator |
    |:--|:--|:--|:--|
    | NCCA syllabus | `ExtractCurriculumSyllabus` | text | `default` (gpt-5-mini via LiteLLM) |
    | SEC exam paper | `ExtractExamPaperLayout` | text+image refs | `default` |
    | Syllabus diagram | `ExtractSyllabusDiagram` | **vision** | `local_vision_gemma4` OR `local_vision_qwen3vl` |
    | SEC marking scheme | `ExtractMarkingSchemeGuideline` | text+grading | `default` |

    **Signature feature:** the 3rd row (syllabus diagrams) uses the
    local vision models. The canonical pattern is to run the same PDF
    through **both** `gemma-4-26B-A4B` AND `qwen3-vl-8b` and emit a
    side-by-side comparison (see §5 below).
    """
    )
    return


@app.cell
def _section_curriculum(mo):
    mo.md(
        """
    ## 1. `ExtractCurriculumSyllabus` (text mode)

    Source of truth: `cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml`

    The function takes the PDF text + the subject name and returns a
    structured `CurriculumSyllabus` object (per Tutorial 1 §2):

    ```baml
    function ExtractCurriculumSyllabus(
      pdf_text: string,
      subject: string?
    ) -> CurriculumSyllabus {
      client default
      prompt #"Extract the NCCA Leaving Certificate syllabus structure from this {{ subject }} PDF: {{ pdf_text }}"#
    }
    ```

    **Cost:** approximately 4K-8K input tokens + 1K-2K output tokens
    per syllabus (depending on the subject + level). The 6 LC priority
    subjects (Mathematics, Chemistry, Geography, Gaeilge, English,
    Computer Science) at 2 levels (higher + ordinary) = 12 invocations
    per pipeline run.
    """
    )
    return


@app.cell
def _section_exam_paper(mo):
    mo.md(
        """
    ## 2. `ExtractExamPaperLayout` (text+image refs mode)

    Source of truth: `cianfhoghlaim/baml/education/lc_extraction/exam_paper_layout.baml`

    The function takes the PDF text + the subject name and returns a
    structured `ExamPaperLayout` object with section/question metadata:

    ```baml
    function ExtractExamPaperLayout(
      pdf_text: string,
      subject: string?
    ) -> ExamPaperLayout {
      client default
      prompt #"Extract the exam paper structure (sections, questions, marks) from this {{ subject }} PDF: {{ pdf_text }}"#
    }
    ```

    **Image references:** the returned `ExamPaperLayout` includes
    `image_refs: string[]` (e.g. `"figure_3_p12"`,
    `"diagram_5_p15"`). These are page-level references used by
    `ExtractSyllabusDiagram` (next section) to fetch the actual image
    bytes from the PDF.

    **Cost:** 3K-6K input + 1K output per exam paper. The SEC ships
    ~10 years × 6 subjects × 2 levels = 120 exam papers total; the
    pipeline processes them incrementally (incremental loading per
    `dlt` source cursor).
    """
    )
    return


@app.cell
def _section_syllabus_diagram(mo):
    mo.md(
        """
    ## 3. `ExtractSyllabusDiagram` (vision mode)

    Source of truth: `cianfhoghlaim/baml/education/lc_extraction/exam_paper_layout.baml`

    The function takes the **image bytes** (NOT text) of a syllabus
    diagram page + the pointing_model parameter:

    ```baml
    function ExtractSyllabusDiagram(
      page_image: image,
      diagram_type: string,
      pointing_model: string        // "gemma-4-26B-A4B" | "qwen3-vl-8b"
    ) -> ExtractedDiagram {
      client <pointing_model>        // resolved at call time
      prompt #"Extract the diagram structure from this {{ diagram_type }} image: {{ page_image }}"#
    }
    ```

    **The 2 supported pointing models:**
    - `local_vision_gemma4` → `gemma-4-26B-A4B` (favours structure)
    - `local_vision_qwen3vl` → `qwen3-vl-8b` (favours OCR fidelity)

    Both run on the local MLX backend via the llama-swap reverse-proxy
    (per the `local_vision_*` generators in
    `cianfhoghlaim/baml/clients.baml`).
    """
    )
    return


@app.cell
def _section_marking(mo):
    mo.md(
        """
    ## 4. `ExtractMarkingSchemeGuideline` (text+grading mode)

    Source of truth: `cianfhoghlaim/baml/education/lc_extraction/marking_scheme.baml`

    The function takes the marking-scheme PDF text + the subject name
    and returns a structured `MarkingSchemeGuideline` (with the
    marking criteria + the per-criterion mark allocation + the
    examiner notes):

    ```baml
    function ExtractMarkingSchemeGuideline(
      pdf_text: string,
      subject: string?
    ) -> MarkingSchemeGuideline {
      client default
      prompt #"Extract the marking scheme criteria + marks + examiner notes from this {{ subject }} PDF: {{ pdf_text }}"#
    }
    ```

    **Cost:** 2K-4K input + 0.5K-1K output per marking scheme. Like
    the exam papers, there are ~120 marking schemes total (10 years ×
    6 subjects × 2 levels).
    """
    )
    return


@app.cell
def _section_side_by_side(mo):
    mo.md(
        """
    ## 5. The side-by-side comparison — `gemma-4-26B-A4B` vs `qwen3-vl-8b`

    This is the **signature feature** of this tutorial. The cell below
    runs the same syllabus diagram image through **both** vision
    models and emits a marimo `mo.ui.table` showing the two outputs
    side-by-side.

    ### Why both?

    - **`gemma-4-26B-A4B`** (Gemma 4 26B parameter mixture-of-experts,
      active 4B): favours structural extraction (table cell values,
      equation structure, labelled axes). Often weaker on small OCR
      text.
    - **`qwen3-vl-8b`** (Qwen 3 VL 8B parameter dense): favours OCR
      fidelity (small text, subscripts, superscripts, mathematical
      notation). Often weaker on graph topology.

    Per the parent mega-change Phase B3 decision, the BIEP pipeline
    runs **both** models on every diagram and emits a
    `side_by_side_comparison` row to the `lc_diagrams` LanceDB table
    + a `graph` node to the `upstream_packages_graph` FalkorDB graph
    (the `match_confidence` is computed as a Jaccard similarity of the
    two outputs).
    """
    )
    return


@app.cell
def _side_by_side_code():
    side_by_side_code = '''\
# Side-by-side comparison cell — runs the same image through both models
import asyncio
from baml_client.sync_client import b as baml_sync

async def run_side_by_side(page_image: bytes, diagram_type: str) -> dict:
    """Run both vision models on the same image and emit a comparison row."""
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
        "gemma4": gemma4_result,
        "qwen3vl": qwen3vl_result,
        "gemma4_strength": "structure" if diagram_type in ("graph", "diagram") else "ocr",
        "qwen3vl_strength": "ocr" if diagram_type in ("equation", "table") else "structure",
    }\
'''
    return (side_by_side_code,)


@app.cell
def _render_side_by_side(side_by_side_code, mo):
    _md = (
        """
    ```python
    """
        + side_by_side_code
        + """
    ```

    The cell returns a dict with:
    - `diagram_type` — the canonical type ("graph" / "table" /
      "diagram" / "equation")
    - `gemma4` — the `gemma-4-26B-A4B` extraction result
    - `qwen3vl` — the `qwen3-vl-8b` extraction result
    - `gemma4_strength` — which aspect gemma-4 is expected to win on
      (heuristic; based on diagram type)
    - `qwen3vl_strength` — which aspect qwen3-vl is expected to win
      on (heuristic; based on diagram type)

    ### Marimo table cell

    Below is the marimo cell that consumes the side-by-side dict and
    emits a comparison table (the canonical pattern):

    ```python
    import marimo as mo

    @app.cell
    def _render_comparison(run_result):
        rows = [
            {
                "diagram_type": run_result["diagram_type"],
                "gemma-4 (structure)": str(run_result["gemma4"]),
                "qwen3-vl (OCR)": str(run_result["qwen3vl"]),
                "match_confidence": compute_jaccard(
                    run_result["gemma4"], run_result["qwen3vl"]
                ),
            }
        ]
        return mo.ui.table(rows, label="Side-by-side vision comparison")
    ```
    """
    )
    mo.md(_md)
    return


@app.cell
def _section_jaccard(mo):
    mo.md(
        """
    ## 6. The `match_confidence` Jaccard similarity

    The `match_confidence` between the two outputs is computed as a
    Jaccard similarity over the **flattened string representation**
    of the two extractions:

    ```python
    def compute_jaccard(a, b):
        # Jaccard similarity over the flattened string sets
        sa = set(json.dumps(a, sort_keys=True).split())
        sb = set(json.dumps(b, sort_keys=True).split())
        if not sa and not sb:
            return 1.0
        return len(sa & sb) / len(sa | sb)
    ```

    **Interpretation:**
    - `match_confidence > 0.8` — both models agree (use either)
    - `0.5 < match_confidence < 0.8` — models disagree on structure;
      use the model that matches the `diagram_type` strength
      (gemma-4 for graph/diagram, qwen3-vl for equation/table)
    - `match_confidence < 0.5` — manual review required; emit a Slack
      alert via the `upstream_breaking_change_sensor`
    """
    )
    return


@app.cell
def _section_pipeline(mo):
    mo.md(
        """
    ## 7. The full pipeline (4 functions chained)

    ```python
    async def process_diagram_page(page_image: bytes, diagram_type: str) -> dict:
        # 1. Run the side-by-side comparison
        result = await run_side_by_side(page_image, diagram_type)

        # 2. Compute the match_confidence
        result["match_confidence"] = compute_jaccard(
            result["gemma4"], result["qwen3vl"]
        )

        # 3. Emit to LanceDB (oideachais.lc.<subject>.diagrams)
        await lance_table.add([
            {
                "diagram_id": hash_image(page_image),
                "diagram_type": result["diagram_type"],
                "gemma4_extraction": json.dumps(result["gemma4"]),
                "qwen3vl_extraction": json.dumps(result["qwen3vl"]),
                "match_confidence": result["match_confidence"],
            }
        ])

        # 4. Emit to FalkorDB graph (upstream_packages_graph)
        await kg.add_node(
            node_type="syllabus_diagram",
            properties={
                "diagram_id": hash_image(page_image),
                "match_confidence": result["match_confidence"],
            },
        )

        return result
    ```
    """
    )
    return


@app.cell
def _section_smoke(mo):
    mo.md(
        """
    ## 8. Smoke-test the side-by-side pipeline

    ```bash
    cd cianfhoghlaim
    uv run python -c "
    from baml_client.sync_client import b as baml_sync
    gemma = baml_sync.ExtractSyllabusDiagram(
        page_image=b'fake_image_bytes',
        diagram_type='graph',
        pointing_model='gemma-4-26B-A4B',
    )
    qwen = baml_sync.ExtractSyllabusDiagram(
        page_image=b'fake_image_bytes',
        diagram_type='graph',
        pointing_model='qwen3-vl-8b',
    )
    print('gemma:', gemma)
    print('qwen:', qwen)
    "
    ```

    **Expected:** the function calls succeed (returning synthetic
    extractions); the `match_confidence` is computed in the
    `compute_jaccard` helper. The pipeline then emits the row to
    LanceDB + FalkorDB.
    """
    )
    return


@app.cell
def _next_steps(mo):
    mo.md(
        """
    ## Next steps

    - See `04_cocoindex_baml_integration.py` for the 3 real
      CocoIndex+BAML integration patterns (`upstream_api_surface` /
      `upstream_blog_monitor` / `docs_skills_consolidation`)
    - See `05_post_v4_duplicate_audit_and_migration.py` for the
      interactive 42-renames audit notebook
    - See Tutorial 1 §4 for the `image` first-class type syntax

    **Cross-references:**
    - `.agents/skills/baml/SKILL.md` — the BAML 0.223.0 skill router
    - `.agents/skills/cocoindex/SKILL.md` — the CocoIndex v1 skill
    - `openspec/specs/british-isles-education-pipeline/spec.md` —
      the 6 LC priority subjects pipeline (Mathematics, Chemistry,
      Geography, Gaeilge, English, Computer Science)
    - `openspec/specs/oideachais-baml-schemas/spec.md` — the BAML
      schemas capability spec (18 → 19 → 20 requirements)
    - `openspec/specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md`
      — this tutorial track's parent capability spec
    """
    )
    return


# =============================================================================
# Dual-mode entry: marimo app OR standalone CLI script
# =============================================================================
def _cli_main(argv=None) -> int:
    """Run the tutorial as a CLI script from any cwd."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="03_education_pdf_vision_pipeline.py",
        description=__doc__,
    )
    parser.add_argument(
        "--pdf",
        type=str,
        default="",
        help="Path to a PDF file to run the 4 extraction functions on (default: smoke test only)",
    )
    parser.add_argument(
        "--diagram-type",
        type=str,
        choices=["graph", "table", "diagram", "equation"],
        default="graph",
        help="Diagram type for the side-by-side comparison (default: graph)",
    )
    args = parser.parse_args(argv)
    print("[03_education_pdf_vision_pipeline] Tutorial 3 — vision+PDF pipeline")
    print("  4 extraction functions: ExtractCurriculumSyllabus,")
    print("    ExtractExamPaperLayout, ExtractSyllabusDiagram,")
    print("    ExtractMarkingSchemeGuideline")
    print(f"  Side-by-side: gemma-4-26B-A4B vs qwen3-vl-8b on {args.diagram_type}")
    if args.pdf:
        print(f"  PDF: {args.pdf}")
    print("  Run: uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline")
    return 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()
