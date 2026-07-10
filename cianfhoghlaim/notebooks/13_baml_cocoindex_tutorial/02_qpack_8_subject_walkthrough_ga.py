# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
# ]
# ///
"""Tutorial 2 (Gaeilge): The 6 GA-LC-subject qpack variants.

Companion to `02_qpack_8_subject_walkthrough.py`. Demonstrates the GA
language path through the 6 GA-LC-subject qpack files (Gaeilge +
Mathematics + History + Geography + Chemistry + Applied Mathematics).

Each of the 6 GA-LC-subject qpacks exposes a new
`Extract<Subject>GaStatement(paragraph) -> string[]` function alongside
the existing `Extract<Subject>LOStatement`. The GA variant uses
`client default` (not `client ExtractEn`) so it can be benchmarked
against the EN variant.

The full 8-subject walkthrough is in `02_qpack_8_subject_walkthrough.py`.
This GA companion focuses on the 6 subjects that ship GA statement
extraction; Computer Science + English are documented in the English
walkthrough only (their syllabi are predominantly EN-only at NCCA
level).

Cross-references:
- `.agents/skills/baml/SKILL.md`
- `openspec/changes/2026-07-13-baml-cocoindex-tutorials-ga-v1/` —
  this openspec change

Run via the cianfhoghlaim-marimo CLI:
    uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/02_qpack_8_subject_walkthrough_ga
    uv run cianfhoghlaim-marimo run  13_baml_cocoindex_tutorial/02_qpack_8_subject_walkthrough_ga
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
    # Tutorial 2 (GA) — The 6 GA-LC-subject qpack variants

    The GA counterpart of Tutorial 2. While the English walkthrough
    covers all 8 LC subjects (40 BAML calls = 8 subjects × 5 functions),
    this GA companion focuses on the **6 subjects that ship GA statement
    extraction**:

    | # | Subject | qpack file | GA function |
    |:--|:--|:--|:--|
    | 1 | Gaeilge | `qpack_gaeilge.baml` | `ExtractGaelGaStatement` |
    | 2 | Mathematics | `qpack_mathematics.baml` | `ExtractMathGaStatement` |
    | 3 | History | `qpack_history.baml` | `ExtractHistGaStatement` |
    | 4 | Geography | `qpack_geography.baml` | `ExtractGeogGaStatement` |
    | 5 | Chemistry | `qpack_chemistry.baml` | `ExtractChemGaStatement` |
    | 6 | Applied Mathematics | `qpack_applied_mathematics.baml` | `ExtractAppmGaStatement` |

    **In aggregate:** 6 GA functions × 1 LO-extraction shape per
    subject = **6 GA statement-extraction BAML calls** for the GA path,
    alongside the 6 EN statement-extraction calls for the bilingual
    run.

    **Computer Science + English** are deliberately omitted — their
    NCCA syllabi are predominantly EN-only; the GA path returns the
    EN statements verbatim with a `[EN-only]` marker.
    """
    )
    return


@app.cell
def _section_gaeilge_functions():
    gael_functions = """\
function ExtractGaelGaStatement(paragraph: string) -> string[] {
  client default
  prompt #"
    Extract all NCCA Gaeilge strand/outcome statements in Irish
    (Gaeilge) from the following NCCA syllabus paragraph. Return
    them as a list of full Irish statements, verbatim from the
    source, with the LO code if present (e.g. 'LC-GAEL-LO-2.4: ...').

    Paragraph: {{ paragraph }}

    {{ ctx.output_format }}
  "#
}\
"""
    return (gael_functions,)


@app.cell
def _render_gael_functions(gael_functions, mo):
    mo.md(
        f"""
    ## 1. Gaeilge — `ExtractGaelGaStatement`

    ```baml
    {gael_functions}
    ```

    **Gaeilge is the only LC subject taught primarily in Irish.** The
    GA function returns the Irish statements verbatim from the source.
    There is no `[EN-only]` fallback path because the NCCA Gaeilge
    syllabus is fully bilingual — every LO has both an EN and a GA
    statement.
    """
    )
    return


@app.cell
def _section_math_functions():
    math_functions = """\
function ExtractMathGaStatement(paragraph: string) -> string[] {
  client default
  prompt #"
    Extract all NCCA Mathematics strand/outcome statements in Irish
    (Gaeilge) from the following NCCA syllabus paragraph. Return
    them as a list of full Irish statements, verbatim from the
    source, with the LO code if present (e.g. 'LC-MATHS-LO-2.4: ...').
    For Mathematics, the source language is typically English; if
    no Irish translation is available in the paragraph, return the
    English statements verbatim and tag them with a leading
    '[EN-only]' marker.

    Paragraph: {{ paragraph }}

    {{ ctx.output_format }}
  "#
}\
"""
    return (math_functions,)


@app.cell
def _render_math_functions(math_functions, mo):
    mo.md(
        f"""
    ## 2. Mathematics — `ExtractMathGaStatement`

    ```baml
    {math_functions}
    ```

    **Mathematics is mostly EN-only at NCCA level.** The `[EN-only]`
    fallback path is the common case; the GA function still runs
    end-to-end so the bilingual pipeline shape is identical across
    all 6 subjects.
    """
    )
    return


@app.cell
def _section_history_functions():
    hist_functions = """\
function ExtractHistGaStatement(paragraph: string) -> string[] {
  client default
  prompt #"
    Extract all NCCA History strand/outcome statements in Irish
    (Gaeilge) from the following NCCA syllabus paragraph. Return
    them as a list of full Irish statements, verbatim from the
    source, with the LO code if present (e.g. 'LC-HIST-LO-3.1: ...').
    If no Irish translation is available in the paragraph, return
    the English statements verbatim with a leading '[EN-only]' marker.

    Paragraph: {{ paragraph }}

    {{ ctx.output_format }}
  "#
}\
"""
    return (hist_functions,)


@app.cell
def _render_hist_functions(hist_functions, mo):
    mo.md(
        f"""
    ## 3. History — `ExtractHistGaStatement`

    ```baml
    {hist_functions}
    ```

    **History has more Irish-language coverage than Mathematics.** Some
    LC History LOs carry Irish-language strands on the cultural-context
    dimension (e.g. "an Gorta Mór", "Réabhlóid na Poblachta"); the GA
    function returns these verbatim and falls back to `[EN-only]` for
    the LOs the NCCA did not translate.
    """
    )
    return


@app.cell
def _section_geography_functions():
    geog_functions = """\
function ExtractGeogGaStatement(paragraph: string) -> string[] {
  client default
  prompt #"
    Extract all NCCA Geography strand/outcome statements in Irish
    (Gaeilge) from the following NCCA syllabus paragraph. Return
    them as a list of full Irish statements, verbatim from the
    source, with the LO code if present (e.g. 'LC-GEOG-LO-2.5: ...').
    If no Irish translation is available in the paragraph, return
    the English statements verbatim with a leading '[EN-only]' marker.

    Paragraph: {{ paragraph }}

    {{ ctx.output_format }}
  "#
}\
"""
    return (geog_functions,)


@app.cell
def _render_geog_functions(geog_functions, mo):
    mo.md(
        f"""
    ## 4. Geography — `ExtractGeogGaStatement`

    ```baml
    {geog_functions}
    ```

    **Geography has Irish-language coverage on the human-environment
    interaction dimension** (e.g. "síneadh an daonra", "inimirce"). The
    `[EN-only]` fallback covers the physical-geography LOs the NCCA
    left English-only.
    """
    )
    return


@app.cell
def _section_chemistry_functions():
    chem_functions = """\
function ExtractChemGaStatement(paragraph: string) -> string[] {
  client default
  prompt #"
    Extract all NCCA Chemistry strand/outcome statements in Irish
    (Gaeilge) from the following NCCA syllabus paragraph. Return
    them as a list of full Irish statements, verbatim from the
    source, with the LO code if present (e.g. 'LC-CHEM-LO-2.4: ...').
    If no Irish translation is available in the paragraph, return
    the English statements verbatim with a leading '[EN-only]' marker.

    Paragraph: {{ paragraph }}

    {{ ctx.output_format }}
  "#
}\
"""
    return (chem_functions,)


@app.cell
def _render_chem_functions(chem_functions, mo):
    mo.md(
        f"""
    ## 5. Chemistry — `ExtractChemGaStatement`

    ```baml
    {chem_functions}
    ```

    **Chemistry is mostly EN-only at NCCA level.** Same fallback pattern
    as Mathematics: the GA function returns the EN statements verbatim
    with a `[EN-only]` marker. The bilingual pipeline shape stays
    identical.
    """
    )
    return


@app.cell
def _section_appm_functions():
    appm_functions = """\
function ExtractAppmGaStatement(paragraph: string) -> string[] {
  client default
  prompt #"
    Extract all NCCA Applied Mathematics strand/outcome statements
    in Irish (Gaeilge) from the following NCCA syllabus paragraph.
    Return them as a list of full Irish statements, verbatim from
    the source, with the LO code if present (e.g. 'LC-APPM-LO-2.4: ...').
    If no Irish translation is available in the paragraph, return
    the English statements verbatim with a leading '[EN-only]' marker.

    Paragraph: {{ paragraph }}

    {{ ctx.output_format }}
  "#
}\
"""
    return (appm_functions,)


@app.cell
def _render_appm_functions(appm_functions, mo):
    mo.md(
        f"""
    ## 6. Applied Mathematics — `ExtractAppmGaStatement`

    ```baml
    {appm_functions}
    ```

    **Applied Mathematics is almost entirely English-language at NCCA
    level.** The `[EN-only]` fallback path is the common case. The
    bilingual pipeline shape stays identical regardless.
    """
    )
    return


@app.cell
def _section_flow(mo):
    mo.md(
        """
    ## 7. The bilingual `paragraph → LO[]` flow (EN + GA side-by-side)

    The bilingual EN+GA pipeline runs **both** paths in parallel — the
    EN path (`Extract<Subject>LOStatement`) for the EN-canonical output
    and the GA path (`Extract<Subject>GaStatement`) for the GA-canonical
    output. Both paths share the same `string[]` return shape so the
    downstream pipeline can `zip(en_los, ga_los)` per LO.

    ```
    ┌─────────────┐
    │   NCCA      │  ─┬─►  Extract<Subject>LOStatement  (client ExtractEn)  ──►  string[] (EN)
    │  paragraph  │   │
    │  (text)     │  ─┴─►  Extract<Subject>GaStatement  (client default)    ──►  string[] (GA)
    └─────────────┘
    ```

    Both lists are emitted to the same `oideachais.leaving_cert.<subject>_<lang>`
    DuckLake table (one row per `(subject, language, lo_code)`), which
    the per-subject marimo notebooks query via
    `mo.sql(engine=md:oideachais, ...)`.
    """
    )
    return


@app.cell
def _section_outro(mo):
    mo.md(
        """
    ## Next steps

    - **Tutorial 3 (GA)** — `03_education_pdf_vision_pipeline_ga.py`
      exercises the side-by-side `gemma-4` vs `qwen3-vl` vision
      comparison on the Gaeilge NCCA PDFs
    - **Tutorial 4 (GA)** — `04_cocoindex_baml_integration_ga.py`
      demonstrates the 3 CocoIndex+BAML integration patterns on GA
      content
    - **Tutorial 5 (GA)** — `05_post_v4_duplicate_audit_and_migration_ga.py`
      audits the bilingual BAML additions

    For the canonical English-language walkthrough of all 8 subjects
    (40 BAML calls), see `02_qpack_8_subject_walkthrough.py`.
    """
    )
    return


if __name__ == "__main__":
    app.run()