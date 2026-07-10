# Scope decision: the 50 pre-existing BAML diagnostics

## Summary

The BAML runtime already failed before this follow-up. A baseline `uv run baml-cli generate` captured **50 file-level diagnostic groups** before the in-scope cleanup. This change deliberately fixed only the client-scope and `MarkingPoint` duplicate items it owns:

- `clients.baml` no longer contributes a parser diagnostic from invalid top-level test blocks.
- `education/_shared/strand_outcome.baml` no longer defines `class MarkingPoint`; it now defines `class MarkingPointStrand`.
- `education/pdfs/leaving_cert_marking_scheme.baml` no longer defines `class MarkingPoint`; it now defines `class MarkingPointSec`.

After those in-scope fixes, `mise run baml:generate` still fails on **47 remaining file-level diagnostic groups**. Those remaining diagnostics are intentionally **not fixed here**.

## The 50 baseline diagnostics

These are the first diagnostic per file from the baseline capture before this cleanup. Entries 1, 44, and 45 were addressed by this change's in-scope work; the rest remain out of scope.

| # | File:line | Error type |
|---:|:--|:--|
| 1 | `clients.baml:165` | Unexpected keyword `test` in type definition. Use `class` or `enum`. |
| 2 | `processing/email.baml:49` | Invalid line: does not start with a known BAML schema keyword. |
| 3 | `processing/circular_extraction.baml:44` | Invalid line: does not start with a known BAML schema keyword. |
| 4 | `processing/portfolio_extraction.baml:423` | Invalid line: does not start with a known BAML schema keyword. |
| 5 | `processing/audio_extraction.baml:111` | Invalid line: does not start with a known BAML schema keyword. |
| 6 | `processing/image_generation.baml:113` | Invalid line: does not start with a known BAML schema keyword. |
| 7 | `processing/site_analysis.baml:36` | Invalid field or attribute definition. |
| 8 | `education/_shared/diagram_renderer.baml:24` | Invalid field or attribute definition. |
| 9 | `education/lc_extraction/lc_topic_extraction.baml:55` | Invalid field or attribute definition. |
| 10 | `education/lc_extraction/exam_paper_layout.baml:23` | Invalid field or attribute definition. |
| 11 | `education/_shared/content_types.baml:29` | Invalid field or attribute definition. |
| 12 | `processing/ocr_extraction.baml:119` | Invalid line: does not start with a known BAML schema keyword. |
| 13 | `education/lc_extraction/curriculum_syllabus.baml:32` | Invalid field or attribute definition. |
| 14 | `processing/player_assessment.baml:94` | Invalid line: does not start with a known BAML schema keyword. |
| 15 | `processing/named_entities.baml:134` | Invalid line: does not start with a known BAML schema keyword. |
| 16 | `education/lc_extraction/circular_extraction.baml:47` | Invalid field or attribute definition. |
| 17 | `education/lc_extraction/marking_scheme.baml:18` | Invalid field or attribute definition. |
| 18 | `education/lc_extraction/cross_linguistic.baml:11` | Invalid field or attribute definition. |
| 19 | `processing/official_media.baml:29` | Invalid line: does not start with a known BAML schema keyword. |
| 20 | `education/lc_extraction/syllabus_diagram.baml:46` | Invalid field or attribute definition. |
| 21 | `processing/style_transfer.baml:68` | Invalid line: does not start with a known BAML schema keyword. |
| 22 | `education/subjects/qpack_mathematics.baml:71` | Invalid field or attribute definition. |
| 23 | `processing/ocr_validation.baml:272` | Invalid line: does not start with a known BAML schema keyword. |
| 24 | `education/subjects/qpack_computer_science.baml:7` | Inline comma-separated enum values; BAML requires one ALL-CAPS value per line. |
| 25 | `education/subjects/qpack_chemistry.baml:54` | Invalid field or attribute definition. |
| 26 | `processing/author_archive.baml:380` | Invalid line: does not start with a known BAML schema keyword. |
| 27 | `education/subjects/qpack_gaeilge.baml:45` | Inline comma-separated enum values; BAML requires one ALL-CAPS value per line. |
| 28 | `processing/ui_components.baml:52` | Invalid line: does not start with a known BAML schema keyword. |
| 29 | `education/subjects/qpack_geography.baml:7` | Inline comma-separated enum values; BAML requires one ALL-CAPS value per line. |
| 30 | `processing/culture_extraction.baml:35` | Invalid line: does not start with a known BAML schema keyword. |
| 31 | `education/subjects/qpack_applied_mathematics.baml:67` | Invalid field or attribute definition. |
| 32 | `education/subjects/qpack_history.baml:8` | Inline comma-separated enum values; BAML requires one ALL-CAPS value per line. |
| 33 | `celtic/_archive/cognates.baml:102` | Invalid line: does not start with a known BAML schema keyword. |
| 34 | `processing/game_content.baml:86` | Invalid line: does not start with a known BAML schema keyword. |
| 35 | `celtic/_archive/celtic_linguistics.baml:191` | Invalid line: does not start with a known BAML schema keyword. |
| 36 | `education/subjects/qpack_english.baml:48` | Invalid field or attribute definition. |
| 37 | `celtic/morphology.baml:154` | Invalid line: does not start with a known BAML schema keyword. |
| 38 | `celtic/curriculum/mythology_extraction.baml:39` | Invalid field or attribute definition. |
| 39 | `celtic/curriculum/celtic_curriculum.baml:30` | Invalid field or attribute definition. |
| 40 | `celtic/grammar_patterns.baml:123` | Invalid line: does not start with a known BAML schema keyword. |
| 41 | `education/pdfs/root_pdf_extraction.baml:22` | Invalid field or attribute definition. |
| 42 | `education/_shared/education_level.baml:210` | `SkillCategory` enum duplicate against an existing class. |
| 43 | `processing/cv_extraction.baml:49` | `SkillCategory` class duplicate against an existing enum. |
| 44 | `education/pdfs/leaving_cert_marking_scheme.baml:13` | `MarkingPoint` class duplicate. |
| 45 | `education/_shared/strand_outcome.baml:224` | `MarkingPoint` class duplicate. |
| 46 | `education/cross_nation/multi_nation_curriculum.baml:112` | `CrossNationLearningOutcome` class duplicate. |
| 47 | `education/cross_nation/isles_education.baml:102` | `CrossNationLearningOutcome` class duplicate. |
| 48 | `celtic/sources.baml:13` | `CelticLanguage` enum duplicate. |
| 49 | `celtic/gaois/tearma.baml:63` | `PartOfSpeech` enum duplicate. |
| 50 | `processing/docs_skills_extraction.baml:134` | Test-block property `input` is unknown; BAML expects `args`. |

## Options

### Option 1: Leave out of scope (CURRENT STATE — RECOMMENDED)

- **Pros:** Respects the BIEP v1 change's ownership of `lc_extraction/*.baml` and avoids broad BAML syntax churn in a cleanup change.
- **Cons:** `baml:generate` and `baml:test` still do not exit 0; the remaining parser diagnostics persist.
- **Cost:** 0 additional hours in this change.
- **Risk:** Downstream BAML client regeneration remains blocked until the owning BIEP/BAML syntax cleanup lands.

### Option 2: Fix here

- **Pros:** Would make the BAML pipeline cleaner and could unblock BAML client generation plus the BAML-using notebooks.
- **Cons:** Touches the 7 `lc_extraction/*.baml` files and a wider set of subject-pack / processing / Celtic files. This is code-review-required and exceeds the current cleanup scope.
- **Cost:** Estimated 6-8h minimum; likely more if every cascaded parser diagnostic must be reduced to zero.
- **Risk:** High conflict risk with the BIEP v1 change and the queued BAML syntax/duplicate follow-ups.

### Option 3: Hybrid (RECOMMENDED ALTERNATIVE)

- **Pros:** Fixes a smaller non-`lc_extraction` slice first, reducing parser noise while leaving the BIEP-owned 7 `lc_extraction/*.baml` files untouched.
- **Cons:** Still leaves `lc_extraction` diagnostics, so `baml:generate` likely remains non-zero until the BIEP v1 owner finishes those files.
- **Cost:** Estimated 2-3h for a carefully-reviewed subset; more if the current broad subject-pack and Celtic syntax drift is included.
- **Risk:** Medium; still needs dedicated review because parser errors can cascade.

## Recommendation

Option 1 is the right call for this change.

The current mega-change was scoped to a Minimax-M3 client cleanup, a single missed `MarkingPoint` duplicate, and a scope-decision artifact. Fixing the remaining diagnostics would cross into the BIEP v1 and broader BAML syntax-cleanup ownership surfaces.

If the user wants immediate progress without touching `lc_extraction/*.baml`, open a separate Option 3 change that targets only non-`lc_extraction` parser hygiene with explicit review gates and a fresh baseline.

## Validation notes

- `mise run baml:generate` was run after this cleanup and still fails on pre-existing diagnostics outside the files changed here.
- Baseline before this cleanup: 50 file-level diagnostic groups.
- After this cleanup: 47 file-level diagnostic groups remain; the removed groups are exactly the in-scope `clients.baml` parser issue plus the two `MarkingPoint` duplicate groups.
- Exact `^class MarkingPoint\b` count is 0.
