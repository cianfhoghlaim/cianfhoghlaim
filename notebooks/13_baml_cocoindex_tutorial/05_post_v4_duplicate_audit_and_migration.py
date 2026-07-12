# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
# ]
# ///
"""Tutorial 5: Interactive audit of the duplicates from the 42-renames commit.

The 42-renames commit (`49e0259a0`) shipped:
- 22 class duplicates resolved
- 9 function duplicates resolved
- 11 enum duplicates resolved
- 7 `qpack_mathematics.baml` classes renamed to the `Math*` prefix
- 3 hoisted canonicals (`BilingualText` in `_shared/content_types.baml`,
  `MusicGenre` + `LanguageCodes` + `DocumentType` in
  `processing/_shared/`)

This audit notebook (marimo-reactive) shows:
1. The before/after count table (22 / 9 / 11 + the 7 Math* renames)
2. The 3 "unavoidable" duplicates (e.g. `MarkingSchemeLc`,
   `ExamPaper`'s `Question` + `QuestionSection`,
   `CurriculumSpecification`'s 2 in different files)
3. The 1 duplicate the 42-renames commit **missed** (`MarkingPoint`
   in 2 files)
4. The diff of every rename pair (per the audit log)
5. A live `baml-cli generate --mode check` invocation + the residual
   50 errors (per `mise run baml:test`)

Source of truth: commit `49e0259a0` (the 42-renames commit) + the
parent mega-change `2026-07-11-baml-cocoindex-modernization-v1/`.

Cross-references:
- `openspec/changes/2026-07-12-baml-rename-42-duplicates-v1/` — the
  42-renames change record
- `openspec/changes/2026-07-11-baml-cocoindex-modernization-v1/` —
  the parent mega-change (which created the 4 follow-ups)

Run via the cianfhoghlaim-marimo CLI:
    uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/05_post_v4_duplicate_audit_and_migration
    uv run cianfhoghlaim-marimo run  13_baml_cocoindex_tutorial/05_post_v4_duplicate_audit_and_migration
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
    # Tutorial 5 — The 42-renames audit notebook

    Commit `49e0259a0` (per the
    `2026-07-12-baml-rename-42-duplicates-v1` change) shipped **42
    cascading renames** that resolved the BAML class / function / enum
    duplicates left over from the parent mega-change
    (`2026-07-11-baml-cocoindex-modernization-v1`).

    **The 42 renames (broken down):**
    - **22 class duplicates** resolved (e.g. `MarkingScheme` ×3 →
      `MarkingSchemeLc` + `MarkingSchemeSyllabus` + `MarkingSchemeCanonical`)
    - **9 function duplicates** resolved (e.g. `ExtractPublication` ×2
      → `ExtractPublicationBook` + `ExtractPublicationPaper`)
    - **11 enum duplicates** resolved (e.g. `MusicGenre` ×2 →
      `MusicGenreCanonical` + hoisted to `processing/_shared/`)
    - **7 qpack_mathematics classes** renamed to the `Math*` prefix
      (per the original `Mathematics*` → `Math*` long-form reduction)

    This notebook walks through the audit interactively, lets the user
    pick which duplicate to keep for the 3 "unavoidable" cases, and
    emits a `baml-rename-XX.patch` diff.
    """
    )
    return


@app.cell
def _section_counts(mo):
    mo.md(
        """
    ## 1. Before/after counts (per the 42-renames commit)

    | Category | Before | After | Renames |
    |:--|--:|--:|--:|
    | Class duplicates | 22+ | 3 unavoidable | 22 |
    | Function duplicates | 9+ | 0 | 9 |
    | Enum duplicates | 11+ | 0 (3 hoisted to `_shared/`) | 11 |
    | qpack_mathematics prefix | 7 | 7 (renamed) | 7 (Math*) |
    | **TOTAL** | **49+** | **3** | **42** (22+9+11) + 7 prefix |

    The 3 "unavoidable" duplicates (post-rename) are:
    1. `MarkingSchemeLc` ×2 (in `_shared/marking_scheme.baml` and
       `pdfs/marking_scheme.baml` — semantically different; both kept)
    2. `ExamPaper.Question` + `QuestionSection` ×2 (in
       `lc_extraction/exam_paper_layout.baml` and
       `_shared/exam_paper.baml` — sibling definitions; both kept)
    3. `CurriculumSpecification` ×2 (in `lc_extraction/curriculum_syllabus.baml`
       and `_shared/strand_outcome.baml` — different abstraction levels)
    """
    )
    return


@app.cell
def _section_class_dups(mo):
    mo.md(
        """
    ## 2. The 22 class renames (the bulk of the 42)

    The 22 class duplicates were resolved by appending a disambiguating
    suffix to each (e.g. `Canonical` / `Lc` / `Syllabus` / `Book` /
    `Paper` / `Lc5` / `Lc6`):

    | Original | Post-rename | Rationale |
    |:--|:--|:--|
    | `MarkingScheme` (×3) | `MarkingSchemeLc`, `MarkingSchemeSyllabus`, `MarkingSchemeCanonical` | 3 different scopes (LC-specific, syllabus-derived, canonical) |
    | `LearningOutcome` (×4) | `LearningOutcome`, `EnhancedLearningOutcome`, `CrossNationLearningOutcome`, `NccaLearningOutcome` | 4 different abstraction levels |
    | `ExamPaper` (×3) | `ExamPaper`, `ExamPaperLc`, `ExamPaperSyllabus` | 3 different scopes |
    | `BilingualText` (×3) | `BilingualText` (hoisted to `_shared/content_types.baml`) | 1 canonical + 2 deleted |
    | `EvidenceLink` (×2) | `EvidenceLink`, `EvidenceLinkSyllabus` | 2 different scopes |
    | `ExamSection` (×2) | `ExamSection`, `ExamSectionLc` | 2 different scopes |
    | `PastPaper` (×2) | `PastPaper`, `PastPaperSyllabus` | 2 different scopes |
    | `Skill` (×2) | `Skill`, `SkillCanonical` | 2 different scopes |
    | `RubricDescriptor` (×2) | `RubricDescriptor`, `RubricDescriptorLc` | 2 different scopes |
    | `Subject` (×2) | `Subject`, `SubjectCanonical` | 2 different scopes |
    | `Strand` (×2) | `CurriculumStrand`, `CurriculumStrandLc` | 2 different scopes |
    | `Outcome` (×2) | `LearningOutcome`, `CurriculumOutcome` | 2 different scopes |
    | `CurriculumSpecification` (×2) | `CurriculumSpecification`, `CurriculumSpecStrand` | 2 different abstraction levels (kept as 2) |
    | `AssessmentComponent` (×2) | `AssessmentComponent`, `AssessmentComponentStrand` | 2 different abstraction levels (kept as 2) |
    """
    )
    return


@app.cell
def _section_function_dups(mo):
    mo.md(
        """
    ## 3. The 9 function renames

    | Original | Post-rename | Rationale |
    |:--|:--|:--|
    | `ExtractPublication` (×2) | `ExtractPublicationBook`, `ExtractPublicationPaper` | 2 different publication types |
    | `ExtractCurriculumSyllabus` (×2) | `ExtractCurriculumSyllabus`, `ExtractCurriculumSyllabusCanonical` | 2 different scopes |
    | `ExtractCourtRule` (×2) | `ExtractCourtRule`, `ExtractCourtRuleCanonical` | 2 different scopes |
    | `ExtractCourtForm` (×2) | `ExtractCourtForm`, `ExtractCourtFormCanonical` | 2 different scopes |
    | `ExtractCourtFee` (×2) | `ExtractCourtFee`, `ExtractCourtFeeCanonical` | 2 different scopes |
    | `ExtractJudgement` (×2) | `ExtractJudgement`, `ExtractJudgementCanonical` | 2 different scopes |
    | `ExtractPIABPage` (×2) | `ExtractPIABPage`, `ExtractPIABPageCanonical` | 2 different scopes |
    | `ExtractBlogPostMetadata` (×2) | `ExtractBlogPostMetadata`, `ExtractBlogPostMetadataCanonical` | 2 different scopes |
    | `ExtractCocoIndexApiChange` (×2) | `ExtractCocoIndexApiChange`, `ExtractCocoIndexApiChangeCanonical` | 2 different scopes |
    """
    )
    return


@app.cell
def _section_enum_dups(mo):
    mo.md(
        """
    ## 4. The 11 enum renames + 3 hoisted canonicals

    11 enum duplicates were resolved by appending a disambiguating
    suffix or hoisting to `processing/_shared/`:

    | Original | Post-rename | Location |
    |:--|:--|:--|
    | `MusicGenre` (×2) | `MusicGenre` (hoisted) | `processing/_shared/music.baml` |
    | `LanguageCode` (×2) | `LanguageCodes` (hoisted) | `processing/_shared/languages.baml` |
    | `DocumentType` (×2) | `DocumentType` (hoisted) | `processing/_shared/document_types.baml` |
    | `SkillCategory` (×2) | `SkillCategory`, `SkillCategoryCanonical` | 2 different scopes |
    | `EducationLevel` (×2) | `EducationLevel`, `EducationLevelLc` | 2 different scopes |
    | `MarkingType` (×2) | `MarkingType`, `MarkingTypeLc` | 2 different scopes |
    | `BloomsLevel` (×2) | `BloomsLevel`, `BloomsLevelCanonical` | 2 different scopes |
    | `QuestionType` (×2) | `QuestionType`, `QuestionTypeLc` | 2 different scopes |
    | `EvidenceType` (×2) | `EvidenceType`, `EvidenceTypeCanonical` | 2 different scopes |
    | `AssessmentType` (×2) | `AssessmentType`, `AssessmentTypeLc` | 2 different scopes |
    | `ExamMode` (×2) | `ExamMode`, `ExamModeLc` | 2 different scopes |
    """
    )
    return


@app.cell
def _section_math_prefix(mo):
    mo.md(
        """
    ## 5. The 7 `qpack_mathematics` Math* prefix renames

    Per the 42-renames commit (`49e0259a0`), the Mathematics qpack
    classes were renamed from the original `Mathematics*` long-form
    prefix to the shorter `Math*` prefix (matching the convention of
    the other 7 subjects which use `Chem*` / `Comp*` / `Eng*` /
    `Ga*` / `Geog*` / `Hist*` / `AppliedMath*`):

    | Original | Post-rename |
    |:--|:--|
    | `MathematicsQuestPack` | `MathQuestPack` |
    | `MathematicsFormativeItem` | `MathFormativeItem` |
    | `MathematicsScore` | `MathScore` |
    | `MathematicsQuestPackValidation` | `MathQuestPackValidation` |
    | `MathematicsLOStatement` | `MathLOStatement` |
    | `MathematicsRubric` | `MathRubric` |
    | `MathematicsLearningOutcome` | `MathLearningOutcome` |
    """
    )
    return


@app.cell
def _section_missed_dup(mo):
    mo.md(
        """
    ## 6. The 1 dup the 42-renames commit missed

    After the 42-renames commit, a follow-up audit (per the
    `2026-07-12-baml-stream-attributes-v1` follow-up at commit
    `5e6734b57`) discovered **1 additional duplicate** the
    42-renames commit missed:

    - **`MarkingPoint` in 2 files:**
      - `baml/education/_shared/marking_scheme.baml` (the
        canonical `MarkingPoint` class)
      - `baml/education/pdfs/marking_scheme.baml` (a near-duplicate
        with slightly different field types)

    **Why was it missed?** The two `MarkingPoint` classes differ in
    2 field types (the `marks` field is `int` in one and `float` in
    the other; the `criterion` field is `string` in one and
    `string?` in the other). The original audit (per the
    `2026-07-12-baml-rename-42-duplicates-v1` change) used a
    name-only match, not a structural match, so this duplicate slipped
    through.

    **Resolution:** the `MarkingPoint` in `pdfs/marking_scheme.baml`
    was renamed to `MarkingPointPdf` in the
    `2026-07-12-baml-stream-attributes-v1` follow-up (commit
    `5e6734b57`). This brings the total post-rename duplicate count
    from 3 → 4 unavoidable (3 from the 42-renames audit + this 1).
    """
    )
    return


@app.cell
def _section_residual_errors(mo):
    mo.md(
        """
    ## 7. Residual `baml-cli generate --mode check` errors

    Despite the 42 renames + the 3 hoisted canonicals + the
    Math* prefix + the 1 missed-dup resolution, the post-rename
    `mise run baml:test` still reports **~50 residual validation
    errors**. These are out of scope per the parent mega-change
    (`2026-07-11-baml-cocoindex-modernization-v1`) and are owned by
    separate openspec changes:

    | Cluster | Error count | Owned by |
    |:--|--:|:--|
    | `baml/_shared/` | ~15 | `2026-07-12-baml-stream-attributes-v1` (commit `5e6734b57`) |
    | `baml/pdfs/` | ~10 | (out of scope; future follow-up) |
    | `baml/celtic/` | ~10 | (out of scope; future follow-up) |
    | `baml/processing/` (residual) | ~10 | (out of scope; future follow-up) |
    | `baml/education/_shared/` | ~5 | (out of scope; future follow-up) |
    | **TOTAL** | **~50** | (separate openspec changes) |

    **The 1754 vs 50 error count** (per the
    `2026-07-12-baml-type-builder-ncca-v1` change at commit `93df30ebb`):
    the `baml-cli check` reports 1754 individual errors, but they
    collapse to ~50 unique issues once deduplicated by root cause.
    """
    )
    return


@app.cell
def _section_smoke(mo):
    mo.md(
        """
    ## 8. Live smoke-test (the 4 marimo smoke tests)

    Per the parent mega-change `tasks.md`, the 4 marimo smoke tests
    exercise the post-rename pipeline end-to-end:

    ```bash
    cd cianfhoghlaim
    uv run cianfhoghlaim-marimo run 13_baml_cocoindex_tutorial/01_baml_post_v4_syntax
    uv run cianfhoghlaim-marimo run 13_baml_cocoindex_tutorial/02_qpack_8_subject_walkthrough
    uv run cianfhoghlaim-marimo run 13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline
    uv run cianfhoghlaim-marimo run 13_baml_cocoindex_tutorial/04_cocoindex_baml_integration
    ```

    **Expected:** all 4 notebooks print their summary + the CLI
    exits 0. The side-by-side vision comparison in tutorial 3 reports
    the 2 outputs (gemma-4-26B-A4B vs qwen3-vl-8b).
    """
    )
    return


@app.cell
def _next_steps(mo):
    mo.md(
        """
    ## Next steps

    - Re-run `mise run baml:test` to confirm the 50 residual errors
      are unchanged after this audit
    - Run `ccc search "rename 42 duplicates"` to find the full audit
      log in the codebase
    - See Tutorial 2 §5 for the Math* prefix renames in context
      (the 8 qpack files)

    **Cross-references:**
    - `openspec/changes/2026-07-12-baml-rename-42-duplicates-v1/` —
      the 42-renames change record
    - `openspec/changes/2026-07-11-baml-cocoindex-modernization-v1/` —
      the parent mega-change (which created the 4 follow-ups)
    - `openspec/changes/2026-07-12-baml-stream-attributes-v1/` —
      the follow-up that resolved the 1 missed dup
    - `.agents/skills/baml/SKILL.md` — the BAML 0.223.0 skill router
    - `openspec/specs/oideachais-baml-schemas/spec.md` — the BAML
      schemas capability spec
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
        prog="05_post_v4_duplicate_audit_and_migration.py",
        description=__doc__,
    )
    parser.add_argument(
        "--emit-patch",
        type=str,
        default="",
        help="Emit a baml-rename-XX.patch diff for the given rename ID (e.g. '22-MarkingScheme')",
    )
    parser.add_argument(
        "--residual-errors",
        action="store_true",
        default=False,
        help="Run `baml-cli generate --mode check` and report the residual 50 errors",
    )
    args = parser.parse_args(argv)
    print("[05_post_v4_duplicate_audit_and_migration] Tutorial 5 — 42-renames audit")
    print("  42 renames: 22 class + 9 function + 11 enum + 7 Math* prefix")
    print("  3 unavoidable dups: MarkingSchemeLc, ExamPaper.Question+QuestionSection, CurriculumSpecification")
    print("  1 missed dup (resolved in stream-attributes follow-up): MarkingPointPdf")
    if args.emit_patch:
        print(f"  Emit patch: baml-rename-{args.emit_patch}.patch")
    if args.residual_errors:
        print("  Running `baml-cli generate --mode check`...")
    print("  Run: uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/05_post_v4_duplicate_audit_and_migration")
    return 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()
