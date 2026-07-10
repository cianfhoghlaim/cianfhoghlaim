# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
# ]
# ///
"""Tutorial 1 (Gaeilge): Bilingual EN+GA post-v4 BAML 0.223.0 syntax.

Companion to `01_baml_post_v4_syntax.py` (the canonical English-language
walkthrough). Demonstrates the bilingual EN+GA extraction path through
the same BAML 0.223.0 + CocoIndex v1 stack.

Covers the bilingual additions shipped in this openspec change
(`2026-07-13-baml-cocoindex-tutorials-ga-v1`):
1. `enum GaeilgeLanguage` — the 2-language discriminant (`ga` / `en`)
2. `class BilingualText` — the canonical 6-language EN/GA/GD/CY/GV/KW
   shape (text_en required; the other 5 nullable)
3. `function ExtractBilingualText(content) -> BilingualText`
4. `function ExtractStrandGaStatement(paragraph) -> string[]`
5. The `Extract<Subject>GaStatement` GA-language variant on each of the
   6 GA-LC-subject qpacks (gaeilge / mathematics / history / geography /
   chemistry / applied_mathematics)
6. The `bilingual(en, ga)` helper for rendering EN + GA side-by-side

Cross-references:
- `.agents/skills/baml/SKILL.md`
- `openspec/changes/2026-07-13-baml-cocoindex-tutorials-ga-v1/` —
  this openspec change
- `openspec/changes/2026-07-12-baml-cocoindex-tutorials-v1/` — the
  English-language predecessor

Run via the cianfhoghlaim-marimo CLI:
    uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/01_baml_post_v4_syntax_ga
    uv run cianfhoghlaim-marimo run  13_baml_cocoindex_tutorial/01_baml_post_v4_syntax_ga
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
    # Tutorial 1 (GA) — Bilingual EN+GA post-v4 BAML syntax

    This is the **Gaeilge counterpart** of Tutorial 1. It demonstrates the
    bilingual EN+GA extraction path through the same BAML 0.223.0 +
    CocoIndex v1 stack that the English tutorial documents.

    The bilingual EN+GA mandate is project-wide: the agent fleet + marimo
    notebooks + BAML extraction functions all carry both languages.

    **What you'll learn:**
    1. The `enum GaeilgeLanguage` (`ga` / `en`) discriminant
    2. The `class BilingualText` shape (6 languages, EN required)
    3. `function ExtractBilingualText(content) -> BilingualText`
    4. `function ExtractStrandGaStatement(paragraph) -> string[]`
    5. The `Extract<Subject>GaStatement` variants on the 6 GA-LC-subject qpacks
    6. A `bilingual(en, ga)` rendering helper for EN + GA side-by-side cells
    """
    )
    return


@app.cell
def _section1_gaeilge_language(mo):
    mo.md(
        """
    ## 1. `enum GaeilgeLanguage` (the 2-language discriminant)

    The 2-language enum that the bilingual EN+GA extraction functions use
    to declare "this row is bilingual EN+GA" without dragging in the full
    6-language `BilingualText` shape.

    Source of truth: `cianfhoghlaim/baml/education/_shared/content_types.baml`

    ```baml
    enum GaeilgeLanguage {
      "ga"   @description("Gaeilge (Irish) — the canonical first-language form for Gaeilge-medium content")
      "en"   @description("Béarla (English) — the canonical first-language form for English-medium content")
    }
    ```

    **Why a 2-language enum (not just the 6-language `BilingualText`)?**
    The 2-language discriminant is a thin tag the pipeline can switch on
    without having to carry 4 nullable fields it never reads. The full
    `BilingualText` shape is reserved for the rows that actually carry
    the 6 Celtic-language form.
    """
    )
    return


@app.cell
def _section2_bilingual_text(mo):
    mo.md(
        """
    ## 2. `class BilingualText` (the canonical 6-language shape)

    The canonical hoisted BilingualText class (per the 42-renames commit
    `49e0259a0`). `text_en` is required; the other 5 Celtic languages are
    nullable. This is the shape `ExtractBilingualText` returns.

    Source of truth: `cianfhoghlaim/baml/education/_shared/content_types.baml`

    ```baml
    class BilingualText {
      text_en: string @description("English text")
      text_ga: string? @description("Irish (Gaeilge) translation; null if EN-only")
      text_gd: string? @description("Scottish Gaelic (Gàidhlig) translation")
      text_cy: string? @description("Welsh (Cymraeg) translation")
      text_gv: string? @description("Manx (Gaelg) translation")
      text_kw: string? @description("Cornish (Kernewek) translation")
    }
    ```

    **2 prior duplicates resolved** by the 42-renames commit:
    - `root_pdf_extraction.baml` BilingualText (kept as canonical EN/GA-only)
    - `isles_education.baml` BilingualText (renamed to BilingualTextIsles)
    """
    )
    return


@app.cell
def _section3_extract_bilingual_text(mo):
    mo.md(
        """
    ## 3. `function ExtractBilingualText(content) -> BilingualText`

    The bilingual EN+GA extraction primitive. Same `client default` as the
    121 canonical `Extract*` functions from the v0.223.0 bump.

    ```baml
    function ExtractBilingualText(content: string) -> BilingualText {
      client default
      prompt #"Extract the structured bilingual text from: {{ content }}.
        Return the English text (text_en) and the Irish (Gaeilge) text
        (text_ga) where present. If only one language is present in the
        source, leave the other field as null. The 6-language form
        (text_gd / text_cy / text_gv / text_kw) stays null unless the
        source explicitly carries Scottish Gaelic / Welsh / Manx / Cornish
        text."#
      @@description("Bilingual EN+GA text extractor; returns the canonical BilingualText shape.")
    }
    ```

    **Why this is a separate function (not just `client "openai/gpt-4o"` inline):**
    The 121 canonical `Extract*` functions all share the `client default`
    config (the LiteLLM gateway → `minimax-m3` per commit `667635dfd`).
    Putting `ExtractBilingualText` on the same `client default` keeps the
    bilingual EN+GA path on the same cost + retry curve as the rest of the
    pipeline.
    """
    )
    return


@app.cell
def _section4_extract_strand_ga(mo):
    mo.md(
        """
    ## 4. `function ExtractStrandGaStatement(paragraph) -> string[]`

    The NCCA strand/outcome extractor that returns the GA-canonical
    statement list. Routes via `client default`.

    ```baml
    function ExtractStrandGaStatement(paragraph: string) -> string[] {
      client default
      prompt #"Extract the NCCA strand/outcome statements in Irish (Gaeilge)
        from: {{ paragraph }}. Return them as a list of full Irish
        statements, verbatim from the source, with the LO code if present
        (e.g. 'LC-GAEL-LO-2.4: ...'). Use the same wording and punctuation
        as the NCCA source PDF."#
      @@description("NCCA strand/outcome extractor; returns the GA-canonical statement list.")
    }
    ```
    """
    )
    return


@app.cell
def _section5_per_subject_ga(mo):
    mo.md(
        """
    ## 5. `Extract<Subject>GaStatement` on the 6 GA-LC-subject qpacks

    Each of the 6 GA-LC-subject qpack files exposes a
    `Extract<Subject>GaStatement(paragraph: string) -> string[]` function
    alongside the existing `Extract<Subject>LOStatement`. The GA variant
    uses `client default` (not `client ExtractEn`) so it can be
    benchmarked against the EN variant.

    | Subject | qpack file | GA function |
    |:--|:--|:--|
    | Gaeilge | `qpack_gaeilge.baml` | `ExtractGaelGaStatement` |
    | Mathematics | `qpack_mathematics.baml` | `ExtractMathGaStatement` |
    | History | `qpack_history.baml` | `ExtractHistGaStatement` |
    | Geography | `qpack_geography.baml` | `ExtractGeogGaStatement` |
    | Chemistry | `qpack_chemistry.baml` | `ExtractChemGaStatement` |
    | Applied Mathematics | `qpack_applied_mathematics.baml` | `ExtractAppmGaStatement` |

    All 6 share the same `string[]` return shape so the qpack pipeline can
    run either the EN path (`Extract<Subject>LOStatement` →
    `client ExtractEn`) or the GA path (`Extract<Subject>GaStatement` →
    `client default`) without code changes.

    **Fallback:** For LOs the NCCA did not translate, the GA function
    returns the English statements verbatim with a leading `[EN-only]`
    marker (LC Mathematics + Chemistry + Applied Mathematics are mostly
    EN-only at NCCA level; the marker makes the fallback auditable).
    """
    )
    return


@app.cell
def _section6_bilingual_helper(mo):
    mo.md(
        """
    ## 6. The `bilingual(en, ga)` rendering helper

    A small `bilingual(en, ga)` helper that the 5 _ga companion tutorials
    use to render EN + GA side-by-side in a single `mo.md` cell. The
    helper accepts a tuple of `(english_text, irish_text)` and emits the
    2-column markdown. If `ga` is `None`, it falls back to showing only
    the EN text with a `[EN-only]` tag.

    ```python
    def bilingual(en: str, ga: str | None = None) -> str:
        if ga is None:
            return f"| EN | {en} |\\n| GA | _(níor aistríodh)_ [EN-only] |"
        return f"| EN | {en} |\\n| GA | {ga} |"
    ```

    The helper is a regular Python function (not a marimo cell) — it
    just returns a markdown string. Subsequent cells pass the string to
    `mo.md(bilingual(...))` for rendering.
    """
    )
    return


@app.cell
def _bilingual_helper_impl():
    def bilingual(en, ga=None):
        """Render EN + GA side-by-side as a 2-column markdown table."""
        if ga is None:
            return f"| EN | {en} |\n| GA | _(níor aistríodh)_ [EN-only] |"
        return f"| EN | {en} |\n| GA | {ga} |"
    return (bilingual,)


@app.cell
def _section7_demo(mo, bilingual):
    # Demo cell — the bilingual helper rendering a sample row.
    demo_text = bilingual(
        en="Students should be able to solve quadratic equations by factoring.",
        ga="Ba chóir do dhaltaí a bheith in ann cothromóidí cearnacha a réiteach trí fhachtóiríocht.",
    )
    mo.md(
        f"""
    ### Demo: `bilingual(en, ga)` in action

    | | |
    |:--|:--|
    {demo_text}

    The above table is rendered via `mo.md(bilingual(en, ga))` — the EN
    and GA rows are formatted as a 2-column markdown table so the reader
    can scan both languages at a glance.
    """
    )
    return


@app.cell
def _section_outro(mo):
    mo.md(
        """
    ## Next steps

    - **Tutorial 2 (GA)** — `02_qpack_8_subject_walkthrough_ga.py` walks
      through the 6 GA-LC-subject qpack files end-to-end
    - **Tutorial 3 (GA)** — `03_education_pdf_vision_pipeline_ga.py`
      adds the side-by-side `gemma-4` vs `qwen3-vl` vision comparison on
      the Gaeilge NCCA PDFs
    - **Tutorial 4 (GA)** — `04_cocoindex_baml_integration_ga.py`
      demonstrates the 3 CocoIndex+BAML integration patterns on GA content
    - **Tutorial 5 (GA)** — `05_post_v4_duplicate_audit_and_migration_ga.py`
      audits the bilingual BAML additions in the same way as the English
      audit notebook

    For the canonical English-language walkthrough, see
    `01_baml_post_v4_syntax.py`.
    """
    )
    return


if __name__ == "__main__":
    app.run()