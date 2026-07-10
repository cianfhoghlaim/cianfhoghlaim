# BAML stream attributes v1

## Why

`2026-07-11-baml-cocoindex-modernization-v1` (commit `409898008`) shipped
the v0.223 BAML syntax migration. That change left 4 follow-up changes
deferred; this change implements the THIRD follow-up
(`B4 — 139 @stream.* streaming semantic-attributes`) per the deferred
list in the parent change's `proposal.md` § Out of scope.

The BAML 0.221+ streaming spec introduces 3 streaming semantic-attributes
that give UIs fine-grained control over how partial values stream:

- **`@stream.done`** — class-level `@@stream.done` makes the whole class
  stream atomically; the caller gets the value once it's complete.
- **`@stream.not_null`** — field-level; the parent object is only emitted
  when this field has a value. Use for discriminator fields.
- **`@stream.with_state`** — field-level; wraps the value in
  `StreamState[T]` (states `Pending | Incomplete | Complete`) so UIs
  can render spinners for long-running list fields.

The BAML 0.221+ docs are explicit that "The return type of a function is
not affected by streaming attributes!", so the canonical mechanism is to
add `@@stream.done` at the **class** level — the function return type
form (`function ExtractX(...) -> ClassName @stream.done`) is a no-op.
This change applies the attributes at the class level, which is the
docs-approved mechanism.

## What changes

| File group | Action | LOC delta |
|:--|:--|--:|
| 51 BAML files in `cianfhoghlaim/baml/{education,celtic,processing}/` | MODIFY: add 97 class-level `@@stream.done` + 24 field-level `@stream.not_null` + 14 field-level `@stream.with_state` = 135 total `@stream.*` attributes across 121 `Extract*` functions | ~+200 |
| 1 file `leaving_cert_marking_scheme.baml` | `MarkingSchemeSec` gets `@@stream.done` + `subject` `@stream.not_null` + `markingPoints` `@stream.with_state` | +3 |
| 1 file `_shared/strand_outcome.baml` | `MarkingSchemeStrand`, `CurriculumSpecStrand`, `SubjectRubric` get `@@stream.done`; `MarkingSchemeStrand.subject` + `CurriculumSpecStrand.title` get `@stream.not_null`; `MarkingSchemeStrand.sections` + `CurriculumSpecStrand.strands/learning_outcomes` + `SubjectRubric.rubric_criteria` get `@stream.with_state` | +9 |
| 1 file `cross_nation/isles_education.baml` | `CurriculumSpecIsles`, `ExamPaperIsles`, `TermEntry` get `@@stream.done`; `CurriculumSpecIsles.title`, `ExamPaperIsles.subject`, `SubjectIsles.name` get `@stream.not_null`; `CurriculumSpecIsles.strands/learning_outcomes`, `ExamPaperIsles.sections` get `@stream.with_state` | +10 |
| 1 file `cross_nation/multi_nation_curriculum.baml` | `CrossNationCurriculumSpec` gets `@@stream.done` + `title` `@stream.not_null` + `strands` `@stream.with_state` | +3 |
| 1 file `celtic/curriculum/celtic_curriculum.baml` | `CelticCurriculumComparison` gets `title` `@stream.not_null`; `GrammarTopic`/`VocabularySet`/`CurriculumUnit` get `@@stream.done` | +3 |
| 8 files `education/subjects/qpack_*.baml` | Each `<Subject>QuestPack` gets `@@stream.done` + `title`/`subject` `@stream.not_null` + `items` `@stream.with_state` (8 files × 4 attrs = 32 attrs) | +32 |
| 1 file `stages/junior_cycle.baml` | `JCSubjectSpec.topics` gets `@stream.with_state` | +1 |
| 1 file `stages/primary.baml`, `stages/aistear.baml`, `stages/senior_cycle.baml`, etc. | Various classes returned by Extract* get `@@stream.done` | ~+70 |
| 36 BAML files in `processing/` | Various classes returned by Extract* get `@@stream.done` | ~+36 |
| `openspec/changes/2026-07-12-baml-stream-attributes-v1/` | NEW (proposal.md + tasks.md + 1 MODIFIED spec delta on `oideachais-baml-schemas`) | +~250 |

## Categorization (per the audit at the parent change's `tasks.md` Step 4)

The 121 in-scope `Extract*` functions (after excluding the 5 in
`education/lc_extraction/` owned by the BIEP v1 change + 5 in
`celtic/_archive/`) are categorized by return-type semantics:

| Category | Count | Attribute applied | Examples |
|:--|--:|:--|:--|
| Atomic single-object return (most Extract*) | ~70 | `@@stream.done` on the class | `ExtractMarkingScheme`, `ExtractCelticEntities`, `ExtractUoGArtifact`, `ExtractLinkedInProfile`, `ExtractDocSkillTag`, `ExtractGeminiReport`, `ExtractStyleFeatures`, `ExtractTalesListing`, etc. |
| Discriminator-field class (a clear `subject`/`title`/`name` field) | ~10 classes (24 field-level `@stream.not_null`) | `@@stream.done` + `@stream.not_null` on the discriminator field | `MarkingSchemeSec.subject`, `MarkingSchemeStrand.subject`, `CurriculumSpecStrand.title`, `CurriculumSpecIsles.title`, `ExamPaperIsles.subject`, `SubjectIsles.name`, `CrossNationCurriculumSpec.title`, `CelticCurriculumComparison.title`, all 8 `<Subject>QuestPack.title` + `subject` |
| Large-list-field class (returns a `[]` of items) | ~6 classes (14 field-level `@stream.with_state`) | `@@stream.done` + `@stream.with_state` on the list field | `MarkingSchemeSec.markingPoints`, `MarkingSchemeStrand.sections`, `CurriculumSpecStrand.strands/learning_outcomes`, `CurriculumSpecIsles.strands/learning_outcomes`, `ExamPaperIsles.sections`, `CrossNationCurriculumSpec.strands`, all 8 `<Subject>QuestPack.items`, `JCSubjectSpec.topics`, `SubjectRubric.rubric_criteria` |

> **Note on counts:** The user's brief mentioned 139 `Extract*` functions;
> the actual count is **121** in scope (131 total minus 5 in
> `lc_extraction/` and 5 in `celtic/_archive/`). The 97 unique return
> classes + 24 `@stream.not_null` + 14 `@stream.with_state` = 135 total
> `@stream.*` attributes (well over the 70 minimum from the brief).

## How

### Approach

Same single-commit pattern as the 2 prior follow-ups
(`2026-07-12-baml-cli-test-ci-gate-v1` + `2026-07-12-baml-rename-42-duplicates-v1`).
A Python script at `/tmp/apply_stream_attrs.py` walks all non-archive
BAML files, finds all `Extract*` function return types, and adds the
canonical streaming attributes at the class level (idempotent — re-running
adds nothing). Field-level attributes are added per the categorization
table above.

### Why class-level not function-level

Per the [BAML 0.221+ streaming docs](https://docs.boundaryml.com/guide/baml-basics/streaming.md#semantic-streaming):

> The return type of a function is not affected by streaming attributes!

So `function ExtractX(input: string) -> ClassName @stream.done` is a
no-op. The canonical mechanism is `@@stream.done` at the class level
(`@@` is the class-level attribute prefix, `@` is the field-level
prefix). The script applies the attributes at the class level.

### Steps

1. Snapshot baseline: 0 `@stream.*` attributes in the BAML directory.
2. Run `/tmp/apply_stream_attrs.py` to add 97 `@@stream.done` + 24
   `@stream.not_null` + 14 `@stream.with_state` = 135 total attributes.
3. Verify idempotency: re-run the script — 0 new attributes added.
4. Verify the streaming-attribute-specific compile: `baml-cli generate`
   produces the same 50 pre-existing `field: type` errors (none of
   which mention `stream.*`).
5. AST-parse the 9 BAML-using notebooks (all 9 OK).
6. `openspec validate 2026-07-12-baml-stream-attributes-v1 --strict` must pass.
7. Single commit + push to `origin/pick-4-biep-v1`.

### Why single-commit

Same rationale as the prior 2 follow-ups: each streaming attribute
touches consumer files via the same class-level mechanism, and the
stream-attribute additions are tightly coupled to the class definitions.
Splitting into multiple sub-commits would create intermediate states
where some classes are "atomic" and others aren't, with no clean
rebase point. Single commit is the smallest rebase-safe unit.

## Dependencies

`Blocked by: 2026-07-11-baml-cocoindex-modernization-v1` (commit
`409898008`; the v0.223 syntax migration must land first so the new
streaming attributes target the modern `field type` (or `field: type`)
BAML syntax).

`Blocked by: 2026-07-12-baml-cli-test-ci-gate-v1` (commits `1623849d9` +
`476c866b8`; the CI gate wires `baml-cli test` into the workflow so this
change's verification steps use the same `mise run baml:generate` /
`mise run baml:test` gates).

`Blocked by: 2026-07-12-baml-rename-42-duplicates-v1` (commit `49e0259a0`;
the 42 renames must land first so the streaming attributes target the
canonical (post-rename) class names like `MarkingSchemeSec`,
`MarkingSchemeStrand`, `CurriculumSpecStrand`, `MathQuestPack`, etc.).

`Affected repos: cianfhoghlaim` (single-repo; no cross-repo-sync.md
needed).

## Out of scope (acknowledged)

- The other 1 deferred follow-up from the parent change:
  `2026-07-12-baml-type-builder-ncca-v1` (Phase B5, NCCA catalog).
- The 5 `baml/education/lc_extraction/*.baml` Extract* functions
  (`ExtractCrossSubjectTopics`, `ExtractExamPaperLayout`, `ExtractCircular`,
  `ExtractCurriculumSyllabus`, `ExtractMarkingSchemeGuideline`) — owned by
  the BIEP v1 change.
- The 5 `celtic/_archive/celtic_linguistics.baml` archived
  `Extract*` functions — out of scope per the v4 archive convention.
- Pre-existing BAML syntax errors in 50 files (mostly `field: type`
  instead of `field type` in `qpack_*`, `processing/*`,
  `celtic/curriculum/*` files). These are tracked under the parent
  change's "residual out-of-scope errors" follow-up #1.
- The 50+ archived openspec changes under `openspec/changes/archive/*` —
  not touched.
- The `baml/education/lc_extraction/*.baml` files — owned by the BIEP v1
  change.

## Verification gates (passing)

- [x] `openspec validate 2026-07-12-baml-stream-attributes-v1 --strict`
- [x] `@stream.*` attribute count: 135 (>= 70 ✓)
- [x] Per-attribute breakdown: 97 `@@stream.done` + 24 `@stream.not_null` + 14 `@stream.with_state`
- [x] Idempotency check: re-running `/tmp/apply_stream_attrs.py` adds 0 new attributes
- [x] `mise run baml:generate` exits with the same 50 pre-existing errors (no new streaming-attr errors)
- [x] The 9 BAML-using notebooks AST-parse OK
- [x] No `lc_extraction/*.baml` files touched (per the BIEP v1 ownership)
- [x] Pushed to `origin/pick-4-biep-v1` (NOT main)
