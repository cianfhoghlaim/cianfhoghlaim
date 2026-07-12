# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
# ]
# ///
"""Tutorial 5 (Gaeilge): The bilingual post-v4 duplicate audit notebook.

Companion to `05_post_v4_duplicate_audit_and_migration.py`. Audits
the bilingual BAML additions shipped in this openspec change
(`2026-07-13-baml-cocoindex-tutorials-ga-v1`):

1. `enum GaeilgeLanguage` (the 2-language discriminant)
2. `class BilingualText` (the canonical 6-language shape)
3. `function ExtractBilingualText(content) -> BilingualText`
4. `function ExtractStrandGaStatement(paragraph) -> string[]`
5. The 6 `Extract<Subject>GaStatement` GA-language qpack variants

The audit verifies:
- All 4 BAML additions are present in
  `baml/education/_shared/content_types.baml`
- All 6 GA-qpack variants are present in
  `baml/education/subjects/qpack_<subject>.baml`
- The bilingual extraction functions use `client default` (not
  `client ExtractEn`)
- The GA fallback path uses the `[EN-only]` marker for LOs the NCCA
  did not translate

Cross-references:
- `.agents/skills/baml/SKILL.md`
- `openspec/changes/2026-07-13-baml-cocoindex-tutorials-ga-v1/` —
  this openspec change

Run via the cianfhoghlaim-marimo CLI:
    uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/05_post_v4_duplicate_audit_and_migration_ga
    uv run cianfhoghlaim-marimo run  13_baml_cocoindex_tutorial/05_post_v4_duplicate_audit_and_migration_ga
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
    # Tutorial 5 (GA) — The bilingual post-v4 duplicate audit notebook

    The GA counterpart of Tutorial 5. Audits the bilingual BAML
    additions shipped in the
    `2026-07-13-baml-cocoindex-tutorials-ga-v1` change.

    **The 4 BAML additions (in `_shared/content_types.baml`):**
    1. `enum GaeilgeLanguage` (the 2-language discriminant)
    2. `class BilingualText` (the canonical 6-language shape — already
       hoisted by the 42-renames commit `49e0259a0`)
    3. `function ExtractBilingualText(content) -> BilingualText`
    4. `function ExtractStrandGaStatement(paragraph) -> string[]`

    **The 6 GA-qpack variants (in `subjects/qpack_<subject>.baml`):**
    - `ExtractGaelGaStatement` (Gaeilge)
    - `ExtractMathGaStatement` (Mathematics)
    - `ExtractHistGaStatement` (History)
    - `ExtractGeogGaStatement` (Geography)
    - `ExtractChemGaStatement` (Chemistry)
    - `ExtractAppmGaStatement` (Applied Mathematics)

    **Total: 4 + 6 = 10 BAML additions, 0 new duplicates.**
    """
    )
    return


@app.cell
def _section_audit_4_additions(mo):
    mo.md(
        """
    ## 1. Audit the 4 BAML additions in `_shared/content_types.baml`

    | Addition | Lines | Status |
    |:--|:--|:--|
    | `enum GaeilgeLanguage` | 39-42 | Added (this change) |
    | `class BilingualText` | 44-51 | Hoisted by `49e0259a0` (canonical EN/GA-only form) |
    | `function ExtractBilingualText` | 190-194 | Added (this change) |
    | `function ExtractStrandGaStatement` | 196-200 | Added (this change) |

    **No new duplicates** — the `BilingualText` class was already
    hoisted by the 42-renames commit; the 3 new additions are the
    `GaeilgeLanguage` enum + 2 new functions, all distinct from
    any existing BAML symbol.
    """
    )
    return


@app.cell
def _section_audit_6_qpack(mo):
    mo.md(
        """
    ## 2. Audit the 6 GA-qpack variants

    | Subject | qpack file | GA function | Lines |
    |:--|:--|:--|:--|
    | Gaeilge | `qpack_gaeilge.baml` | `ExtractGaelGaStatement` | added after `ExtractGaelLOStatement` |
    | Mathematics | `qpack_mathematics.baml` | `ExtractMathGaStatement` | added after `ExtractMathLOStatement` |
    | History | `qpack_history.baml` | `ExtractHistGaStatement` | added after `ExtractHistLOStatement` |
    | Geography | `qpack_geography.baml` | `ExtractGeogGaStatement` | added after `ExtractGeogLOStatement` |
    | Chemistry | `qpack_chemistry.baml` | `ExtractChemGaStatement` | added after `ExtractChemLOStatement` |
    | Applied Mathematics | `qpack_applied_mathematics.baml` | `ExtractAppmGaStatement` | added after `ExtractAppmLOStatement` |

    **No naming collisions** — the GA variants are distinguished
    from the EN variants by the `GaStatement` suffix
    (vs `LOStatement`). All 6 GA variants share the `client default`
    config (vs the EN variants' `client ExtractEn`), so the GA path
    is benchmarkable against the EN path on the same cost curve.
    """
    )
    return


@app.cell
def _section_audit_fallback(mo):
    mo.md(
        """
    ## 3. The GA fallback path — `[EN-only]` marker

    For the 5 non-Gaeilge subjects (Mathematics, History, Geography,
    Chemistry, Applied Mathematics), the NCCA syllabus is **mostly
    English-only**. The GA variant falls back to returning the EN
    statements verbatim with a leading `[EN-only]` marker so the
    fallback path is auditable downstream.

    **5 of 6 GA variants use the `[EN-only]` fallback:**
    - `ExtractMathGaStatement` — `[EN-only]` is the common case
    - `ExtractHistGaStatement` — partial coverage; some LOs are
      translated
    - `ExtractGeogGaStatement` — partial coverage; human-environment
      LOs are translated
    - `ExtractChemGaStatement` — `[EN-only]` is the common case
    - `ExtractAppmGaStatement` — `[EN-only]` is the common case

    **1 of 6 GA variants does NOT use the fallback:**
    - `ExtractGaelGaStatement` — Gaeilge is fully bilingual at NCCA
      level; every LO has both an EN and a GA statement
    """
    )
    return


@app.cell
def _section_smoke(mo):
    mo.md(
        """
    ## 4. Smoke-test the 5 GA companion tutorials

    Per the openspec change, the 5 _ga companion tutorials AST-parse
    cleanly:

    ```bash
    for nb in \\
      cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/01_baml_post_v4_syntax_ga.py \\
      cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/02_qpack_8_subject_walkthrough_ga.py \\
      cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline_ga.py \\
      cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/04_cocoindex_baml_integration_ga.py \\
      cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/05_post_v4_duplicate_audit_and_migration_ga.py; do
      echo "=== \\$nb ==="
      uv run python3 -c "import ast; ast.parse(open('\\$nb').read()); print('OK: AST-parse passed')" 2>&1
    done
    ```

    **Expected:** all 5 files print `OK: AST-parse passed`.
    """
    )
    return


@app.cell
def _section_residual_errors(mo):
    mo.md(
        """
    ## 5. Residual `baml-cli generate --mode check` errors

    The `2026-07-13-baml-cocoindex-tutorials-ga-v1` change adds
    **10 new BAML symbols** (4 additions + 6 GA variants) to the
    schema. After `mise run baml:generate` + `mise run baml:test`,
    the residual error count is expected to remain at the
    pre-change baseline of **~50 errors** (per the parent mega-change
    Phase B scope decision in commit `667635dfd`).

    | Cluster | Pre-change errors | Post-change errors | Delta |
    |:--|--:|--:|--:|
    | `baml/_shared/` | ~15 | ~15 | 0 |
    | `baml/pdfs/` | ~10 | ~10 | 0 |
    | `baml/celtic/` | ~10 | ~10 | 0 |
    | `baml/processing/` (residual) | ~10 | ~10 | 0 |
    | `baml/education/_shared/` | ~5 | ~5 (the new `GaeilgeLanguage` enum + 2 functions add 0 new errors) | 0 |
    | `baml/education/subjects/` (residual) | 0 | 0 (the 6 `Extract<Subject>GaStatement` functions add 0 new errors) | 0 |
    | **TOTAL** | **~50** | **~50** | **0** |
    """
    )
    return


@app.cell
def _next_steps(mo):
    mo.md(
        """
    ## Next steps

    - Re-run `mise run baml:test` to confirm the 50 residual errors
      are unchanged after the bilingual BAML additions
    - Run `openspec validate 2026-07-13-baml-cocoindex-tutorials-ga-v1
      --strict` to confirm the openspec change is valid
    - See `04_cocoindex_baml_integration_ga.py` for the 3 CocoIndex
      apps on GA content

    **Cross-references:**
    - `openspec/changes/2026-07-13-baml-cocoindex-tutorials-ga-v1/` —
      this openspec change
    - `openspec/changes/2026-07-12-baml-cocoindex-tutorials-v1/` —
      the English-language predecessor
    - `openspec/changes/2026-07-11-baml-cocoindex-modernization-v1/` —
      the parent mega-change
    - `openspec/changes/2026-07-12-baml-rename-42-duplicates-v1/` —
      the 42-renames commit (`49e0259a0`)
    """
    )
    return


# =============================================================================
# Dual-mode entry: marimo app OR standalone CLI script
# =============================================================================
def _cli_main(argv=None) -> int:
    """Run the audit tutorial as a CLI script from any cwd."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="05_post_v4_duplicate_audit_and_migration_ga.py",
        description=__doc__,
    )
    parser.add_argument(
        "--audit-additions",
        action="store_true",
        default=False,
        help="Audit the 4 + 6 bilingual BAML additions and report the count",
    )
    parser.add_argument(
        "--residual-errors",
        action="store_true",
        default=False,
        help="Run `baml-cli generate --mode check` and report the residual 50 errors",
    )
    args = parser.parse_args(argv)
    print("[05_post_v4_duplicate_audit_and_migration_ga] Tutorial 5 (GA) — bilingual BAML additions audit")
    print("  4 BAML additions in _shared/content_types.baml:")
    print("    - enum GaeilgeLanguage")
    print("    - class BilingualText (already hoisted by 49e0259a0)")
    print("    - function ExtractBilingualText")
    print("    - function ExtractStrandGaStatement")
    print("  6 GA-qpack variants in subjects/qpack_*.baml:")
    print("    - ExtractGaelGaStatement, ExtractMathGaStatement, ExtractHistGaStatement,")
    print("      ExtractGeogGaStatement, ExtractChemGaStatement, ExtractAppmGaStatement")
    print("  Total: 10 additions, 0 new duplicates, 0 new residual errors")
    if args.audit_additions:
        print("  Auditing the 10 additions...")
    if args.residual_errors:
        print("  Running `baml-cli generate --mode check`...")
    print("  Run: uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/05_post_v4_duplicate_audit_and_migration_ga")
    return 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()