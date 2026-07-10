# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
# ]
# ///
"""Tutorial 2: The 8 qpack_<subject>.baml files.

For each of the 8 LC subjects (Chemistry, Computer Science, English,
Gaeilge, Geography, History, Mathematics, Applied Mathematics), this
tutorial walks through:

1. The 5 canonical functions per subject:
   - `Generate<Subject>QuestPack(paragraph)`
   - `Extract<Subject>LOStatement(paragraph) -> string[]`
   - `Generate<Subject>FormativeItem(learning_outcome)`
   - `Score<Subject>FormativeResponse(item, student_response)`
   - `Validate<Subject>QuestPack(pack) -> <Subject>QuestPackValidation`
2. The canonical `paragraph → LO[] → FormativeItem → Score → Validate`
   flow across all 8 subjects
3. The 40+ BAML calls in aggregate (5 functions × 8 subjects)

Source of truth: `cianfhoghlaim/baml/education/subjects/qpack_*.baml`
(8 files, 5 functions each).

Cross-references:
- `.agents/skills/baml/SKILL.md`
- `openspec/changes/2026-07-12-baml-rename-42-duplicates-v1/` — the
  42-renames commit (`49e0259a0`) that renamed `qpack_mathematics.baml`
  classes to the Math* prefix
- `openspec/changes/2026-07-12-baml-stream-attributes-v1/` — the
  follow-up that added `@stream.*` to the 5 functions per subject

Run via the cianfhoghlaim-marimo CLI:
    uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/02_qpack_8_subject_walkthrough
    uv run cianfhoghlaim-marimo run  13_baml_cocoindex_tutorial/02_qpack_8_subject_walkthrough
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
    # Tutorial 2 — The 8 `qpack_<subject>.baml` files

    Each of the 8 LC subjects (Chemistry, Computer Science, English,
    Gaeilge, Geography, History, Mathematics, Applied Mathematics) has
    its own `.baml` file at
    `cianfhoghlaim/baml/education/subjects/qpack_<subject>.baml`. Each
    file ships **5 canonical functions** that together implement the
    `paragraph → LO[] → FormativeItem → Score → Validate` learning-
    outcome flow.

    **In aggregate:** 8 subjects × 5 functions = **40 BAML calls** per
    end-to-end NCCA strand/outcome processing pipeline run.
    """
    )
    return


@app.cell
def _inventory(mo):
    mo.md(
        """
    ## 1. The 8 `qpack_<subject>.baml` files (inventory)

    Per `ls cianfhoghlaim/baml/education/subjects/`:

    | Subject | File | Functions |
    |:--|:--|--:|
    | Chemistry | `qpack_chemistry.baml` | 5 |
    | Computer Science | `qpack_computer_science.baml` | 5 |
    | English | `qpack_english.baml` | 5 |
    | Gaeilge | `qpack_gaeilge.baml` | 5 |
    | Geography | `qpack_geography.baml` | 5 |
    | History | `qpack_history.baml` | 5 |
    | Mathematics | `qpack_mathematics.baml` | 5 |
    | Applied Mathematics | `qpack_applied_mathematics.baml` | 5 |
    | **TOTAL** | **8 files** | **40 functions** |
    """
    )
    return


@app.cell
def _section_canonical_pattern(mo):
    mo.md(
        """
    ## 2. The 5 canonical functions per subject

    Every `qpack_<subject>.baml` follows the same 5-function shape
    (with `<Subject>` = `Chem` / `Math` / `Eng` / `Ga` / `Geog` /
    `Hist` / `Comp` / `AppliedMath` etc.):

    1. **Generate<Subject>QuestPack** — generates a new question pack
       from a `paragraph` (the LC syllabus paragraph)
    2. **Extract<Subject>LOStatement** — extracts the learning
       outcome statements from a `paragraph`, returns `string[]`
    3. **Generate<Subject>FormativeItem** — generates a formative
       assessment item for one learning outcome
    4. **Score<Subject>FormativeResponse** — scores a student's
       response to a formative item (the canonical Bloom's-taxonomy
       rubric scoring)
    5. **Validate<Subject>QuestPack** — validates a generated quest
       pack against the canonical shape, returns
       `<Subject>QuestPackValidation`
    """
    )
    return


@app.cell
def _chemistry_functions():
    chem_functions = '''\
function GenerateChemQuestPack(paragraph: string) -> ChemQuestPack {
  client default
  prompt #"Generate a Chemistry Leaving Certificate quest pack for this NCCA paragraph: {{ paragraph }}"#
}

function ExtractChemLOStatement(paragraph: string) -> string[] {
  client default
  prompt #"Extract the learning outcome statements from this Chemistry paragraph: {{ paragraph }}"#
}

function GenerateChemFormativeItem(learning_outcome: string) -> ChemFormativeItem {
  client default
  prompt #"Generate a formative assessment item for this Chemistry LO: {{ learning_outcome }}"#
}

function ScoreChemFormativeResponse(item: ChemFormativeItem, student_response: string) -> ChemScore {
  client default
  prompt #"Score this student response against the rubric for: {{ item }} Response: {{ student_response }}"#
}

function ValidateChemQuestPack(pack: ChemQuestPack) -> ChemQuestPackValidation {
  client default
  prompt #"Validate this Chemistry quest pack: {{ pack }}"#
}\
'''
    return (chem_functions,)


@app.cell
def _render_chem_functions(chem_functions, mo):
    mo.md(
        f"""
    ### Example: Chemistry (`qpack_chemistry.baml`)

    ```baml
    {chem_functions}
    ```

    All 5 functions use the canonical `client default` (the LiteLLM
    OpenAI-compatible gateway). The 5-function shape is identical
    across all 8 subjects — only the type names differ
    (`ChemQuestPack` vs `MathQuestPack` vs `GaQuestPack` etc.).
    """
    )
    return


@app.cell
def _section_flow(mo):
    mo.md(
        """
    ## 3. The `paragraph → LO[] → FormativeItem → Score → Validate` flow

    The 5 functions compose into a single end-to-end pipeline:

    ```
    ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐
    │  NCCA       │    │  Extract*    │    │  Generate*       │
    │  paragraph  │ ─► │  LOStatement │ ─► │  FormativeItem   │
    │  (text)     │    │  (LO[])      │    │  (per LO)        │
    └─────────────┘    └──────────────┘    └──────────────────┘
                                                     │
                                                     ▼
    ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
    │  Generate*   │    │  Score*      │    │  (student        │
    │  QuestPack   │ ◄─ │  Formative   │ ◄─ │  response text)  │
    │  (validated) │    │  Response    │    │                  │
    └──────────────┘    └──────────────┘    └──────────────────┘
    ```
    """
    )
    return


@app.cell
def _flow_pseudocode():
    flow_pseudocode = '''\
# Python pseudo-code showing the end-to-end flow
async def process_ncca_paragraph(paragraph: str, subject: str) -> QuestPack:
    # 1. Extract the learning outcome statements
    los = await baml_sync.ExtractChemLOStatement(paragraph)  # or Math/Eng/Ga/...

    # 2. Generate a formative item per LO
    items = [
        await baml_sync.GenerateChemFormativeItem(lo)
        for lo in los
    ]

    # 3. Score a student response (per item, in production)
    # scores = [await baml_sync.ScoreChemFormativeResponse(item, response) ...]

    # 4. Generate the full quest pack
    pack = await baml_sync.GenerateChemQuestPack(paragraph)

    # 5. Validate the pack shape
    validation = await baml_sync.ValidateChemQuestPack(pack)

    if validation.valid:
        return pack
    else:
        raise ValueError(f"Pack validation failed: {validation.errors}")\
'''
    return (flow_pseudocode,)


@app.cell
def _render_flow_pseudocode(flow_pseudocode, mo):
    mo.md(
        f"""
    ```python
    {flow_pseudocode}
    ```

    **Note:** the Chemistry version (`ExtractChemLOStatement` etc.) is
    shown here. Replace with `Math` / `Eng` / `Ga` / `Geog` / `Hist`
    / `Comp` / `AppliedMath` for the other 7 subjects.
    """
    )
    return


@app.cell
def _section_subject_summary(mo):
    mo.md(
        """
    ## 4. Per-subject summary

    Below are the canonical class names per subject (the
    `<Subject>QuestPack`, `<Subject>FormativeItem`, etc. that the 5
    functions return). Note: the Mathematics classes are prefixed
    with `Math` (not `Mathematics`) per the 42-renames commit
    (`49e0259a0`).

    | Subject | QuestPack | LO type | FormativeItem | Score | Validation |
    |:--|:--|:--|:--|:--|:--|
    | Chemistry | `ChemQuestPack` | `string[]` | `ChemFormativeItem` | `ChemScore` | `ChemQuestPackValidation` |
    | Computer Science | `CompQuestPack` | `string[]` | `CompFormativeItem` | `CompScore` | `CompQuestPackValidation` |
    | English | `EngQuestPack` | `string[]` | `EngFormativeItem` | `EngScore` | `EngQuestPackValidation` |
    | Gaeilge | `GaQuestPack` | `string[]` | `GaFormativeItem` | `GaScore` | `GaQuestPackValidation` |
    | Geography | `GeogQuestPack` | `string[]` | `GeogFormativeItem` | `GeogScore` | `GeogQuestPackValidation` |
    | History | `HistQuestPack` | `string[]` | `HistFormativeItem` | `HistScore` | `HistQuestPackValidation` |
    | Mathematics | `MathQuestPack` | `string[]` | `MathFormativeItem` | `MathScore` | `MathQuestPackValidation` |
    | Applied Mathematics | `AppliedMathQuestPack` | `string[]` | `AppliedMathFormativeItem` | `AppliedMathScore` | `AppliedMathQuestPackValidation` |

    **40 BAML calls in aggregate:** 8 subjects × 5 functions each.
    The total cost per pipeline run is approximately 40 ×
    `gpt-5-mini` LiteLLM-token equivalent (≈ 60-80K tokens for a
    typical NCCA paragraph + 8 LOs + 8 formative items + 8 scores +
    1 pack generation + 1 validation).
    """
    )
    return


@app.cell
def _section_renames(mo):
    mo.md(
        """
    ## 5. The 42-renames commit (`49e0259a0`) — Math* prefix

    Per commit `49e0259a0`, the Mathematics classes were renamed from
    the original `MathematicsQuestPack` / `MathematicsFormativeItem` /
    etc. to the `Math*` prefix:

    | Pre-rename | Post-rename |
    |:--|:--|
    | `MathematicsQuestPack` | `MathQuestPack` |
    | `MathematicsFormativeItem` | `MathFormativeItem` |
    | `MathematicsScore` | `MathScore` |
    | `MathematicsQuestPackValidation` | `MathQuestPackValidation` |
    | `MathematicsLOStatement` | `MathLOStatement` |

    This was 1 of the 7 cascading renames in the `qpack_mathematics.baml`
    cluster. The other 6 subjects had no `Subject*` class-name collision
    (only Mathematics had the long-form prefix, since the module's
    original author used the long form).

    See Tutorial 5 for the full interactive audit of the 42 renames.
    """
    )
    return


@app.cell
def _section_streaming(mo):
    mo.md(
        """
    ## 6. The `@stream.*` annotations (per the stream-attributes follow-up)

    Per commit `5e6734b57`, the 5 functions per subject (40 in total)
    received `@stream.*` semantic-attributes:

    - `@stream.done` on the function-level (5 functions × 8 subjects = 40)
    - `@stream.not_null` on the `<Subject>` field of the QuestPack (8)
    - `@@stream.done` on the `FormativeItem[]` field (8)
    - `@@stream.with_state` on the `Score` class (8)

    **Total: 64 `@stream.*` annotations across the 8 qpack files.**
    See `openspec/changes/2026-07-12-baml-stream-attributes-v1/` for
    the full diff and Tutorial 1 §5 for the syntax reference.
    """
    )
    return


@app.cell
def _section_typebuilder(mo):
    mo.md(
        """
    ## 7. The `@@dynamic` markers (per the TypeBuilder follow-up)

    Per commit `93df30ebb`, the 4 canonical NCCA-related classes
    (`LearningOutcome`, `CurriculumStrand`, `CurriculumSpecStrand`,
    `AssessmentComponentStrand`) in
    `cianfhoghlaim/baml/education/_shared/strand_outcome.baml` received
    `@@dynamic` markers. These classes are referenced by every
    `<Subject>QuestPack` (via the `topics Topic[]` field), so the
    `@@dynamic` markers apply transitively to all 8 qpack files.

    See `openspec/changes/2026-07-12-baml-type-builder-ncca-v1/` for
    the full diff.
    """
    )
    return


@app.cell
def _section_smoke(mo):
    mo.md(
        """
    ## 8. Smoke-test the qpack pipeline end-to-end

    ```bash
    cd cianfhoghlaim
    uv run baml-cli test baml/education/subjects/qpack_chemistry.baml
    uv run baml-cli test baml/education/subjects/qpack_mathematics.baml
    mise run baml:test
    ```

    The 10 existing `@test` blocks (per the
    `2026-07-12-baml-cli-test-ci-gate-v1` follow-up at commit
    `1623849d9`) exercise 10 of the 40 qpack functions end-to-end.

    **Expected:** 0 new validation errors beyond the 50+ pre-existing
    out-of-scope errors in the `_shared/` / `pdfs/` / `celtic/`
    clusters (verified by the 5-tangent modernization + the 4
    follow-ups).
    """
    )
    return


@app.cell
def _next_steps(mo):
    mo.md(
        """
    ## Next steps

    - See `03_education_pdf_vision_pipeline.py` for the side-by-side
      `gemma-4-26B-A4B` vs `qwen3-vl-8b` comparison on the same
      NCCA syllabus PDFs (the 4 vision-extraction functions:
      `ExtractCurriculumSyllabus` / `ExtractExamPaperLayout` /
      `ExtractSyllabusDiagram` / `ExtractMarkingSchemeGuideline`)
    - See `04_cocoindex_baml_integration.py` for the 3 CocoIndex+BAML
      integration patterns
    - See `05_post_v4_duplicate_audit_and_migration.py` for the
      interactive 42-renames audit (the `Math*` prefix is one of the
      7 cascading renames)

    **Cross-references:**
    - `openspec/specs/oideachais-baml-schemas/spec.md`
    - `openspec/specs/british-isles-education-pipeline/spec.md` (the
      6 LC priority subjects + the gov.ie circulars pipeline)
    - `.agents/skills/baml/SKILL.md` — the BAML 0.223.0 skill router
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
        prog="02_qpack_8_subject_walkthrough.py",
        description=__doc__,
    )
    parser.add_argument(
        "--subject",
        type=str,
        choices=[
            "chemistry",
            "computer_science",
            "english",
            "gaeilge",
            "geography",
            "history",
            "mathematics",
            "applied_mathematics",
            "all",
        ],
        default="all",
        help="Which subject's qpack to walk through (default: all 8)",
    )
    args = parser.parse_args(argv)
    print("[02_qpack_8_subject_walkthrough] Tutorial 2 — qpack walkthrough")
    print(f"  Subject: {args.subject}")
    print("  8 subjects × 5 functions = 40 BAML calls total")
    print("  Source: cianfhoghlaim/baml/education/subjects/qpack_<subject>.baml")
    print("  Run: uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/02_qpack_8_subject_walkthrough")
    return 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()
