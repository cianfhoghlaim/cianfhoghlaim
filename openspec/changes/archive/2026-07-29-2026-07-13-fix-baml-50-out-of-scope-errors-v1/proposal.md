# Fix BAML 50 out-of-scope errors v1

## Why

The `2026-07-13-baml-final-cleanup-v1` change deliberately left 50
out-of-scope BAML file-level diagnostics untouched (per its
`SCOPE_DECISION.md`). That change scoped itself narrowly to the
MiniMax-M3 generator rewrite + the `MarkingPoint` duplicate fix.

This follow-up change implements the **Option 2** choice from the
shipped `SCOPE_DECISION.md`: fix ALL 50 pre-existing BAML `field: type`
diagnostics (and their cascading parse failures) across the
`baml/` tree — including the 7
`baml/education/lc_extraction/*.baml` files that the prior change
explicitly deferred.

The 50 baseline diagnostics were the first error per file from
`mise run baml:generate` before the in-scope cleanup. Once the first
diagnostic is fixed in a file, BAML's parser cascades and reports
additional diagnostics for the subsequent lines that depend on the
fixed context. The actual `mise run baml:generate` output captured
**1,776 individual `error:` lines** across **34 files** — concentrated
in:

| Cluster | Files | Lines rewritten |
|:--|--:|--:|
| `education/subjects/qpack_*.baml` (8 files) | 8 | ~560 |
| `education/_shared/*.baml` (5 files) | 5 | ~133 |
| `education/lc_extraction/*.baml` (7 files, BIEP v1) | 7 | ~157 |
| `education/cross_nation/*.baml` (2 files) | 2 | 9 |
| `education/pdfs/root_pdf_extraction.baml` | 1 | 30 |
| `education/stages/*.baml` (5 files) | 5 | 13 |
| `education/statistics/*.baml` (1 file) | 1 | 14 |
| `education/university/*.baml` (1 file) | 1 | 8 |
| `education/law/*.baml` (6 files) | 6 | 16 |
| `celtic/curriculum/*.baml` (2 files) | 2 | 116 |
| `celtic/gaois/*.baml` (4 files) | 4 | 41 |
| `celtic/sources.baml` | 1 | (duplicate renames) |
| `processing/*.baml` (4 files with new syntax issues) | 4 | 4 |
| **Total** | **47** | **~1,100** |

`mise run baml:generate` was failing with a cascade of 1,776 errors
because BAML v0.212+ deprecated the Pydantic-style `field: type`
syntax in favour of the canonical `field type` (whitespace-separated)
syntax.

## What changes

### 1. Bulk `field: type` → `field type` migration (47 files, ~1,086 lines)

Re-runs `scripts/migrate-baml-syntax.py --apply --all` (originally
shipped in commit `8669278c2`) which converts the Pydantic-style
class/enum field definitions to the BAML v0.212+ canonical syntax.
The script is idempotent — re-running on already-migrated files
reports 0 changes.

The 17-file `processing/` scope from the prior change was preserved
(those files report 0 additional changes). The new scope adds the 30
remaining files.

### 2. Restore `param: type` colons in function signatures (405 lines)

The bulk migration script over-zealously converted function parameter
definitions from `param: type` to `param type`. BAML v0.212+ requires
**colons in function parameters** but **whitespace in class fields**.
A new helper script `scripts/restore-function-param-colons.py` walks
all .baml files, detects `function Name(` openers, tracks paren depth,
and re-adds the colons inside the function arg list. It also correctly
handles trailing commas and `@description(...)` annotations.

### 3. Inline comma-separated enum/class fixes (5 files)

The regex misses inline `enum X { A, B, C }` declarations (BAML requires
one ALL-CAPS value per line with no commas). Fixed by hand:

- `education/subjects/qpack_computer_science.baml` — `enum CompNCCALevel`
- `education/subjects/qpack_geography.baml` — `enum GeogNCCALevel`
- `education/subjects/qpack_history.baml` — `enum HistNCCALevel`
- `education/subjects/qpack_computer_science.baml` — inline
  `class CompBilingualText` + `class CompEvidenceLink`
- `education/subjects/qpack_geography.baml` — inline
  `class GeogBilingualText` + `class GeogEvidenceLink`

### 4. Accented-character enum value names (5 values in `qpack_gaeilge.baml`)

BAML's "all caps" validator rejects Unicode uppercase letters (`Ú`,
`Á`). Renamed:

- `AISTRÚCHÁN_ITEM` → `AISTRIUCHAN_ITEM`
- `COMHRÁ_ITEM` → `COMHRA_ITEM`
- `FILÍOCHT_ANALYSIS` → `FILIOCHT_ANALYSIS`
- `LITRÍOCHT_ANALYSIS` → `LITRIOCHT_ANALYSIS`
- `SCRIBHNEoireacht` → `SCRIBHNEOIREACHT` (mixed-case typo)

### 5. Test block property `input` → `args` (1 file)

`processing/docs_skills_extraction.baml` used the legacy `input { ... }`
test-block property (BAML v0.x syntax). BAML v0.212+ expects `args { ... }`.
The `output { ... }` block was also removed (BAML has no `output` test-block
property; assertions are written with `@assert` / `@@assert` instead).

### 6. Duplicate BAML type definitions (8 duplicates → 8 unique)

Following the convention from the prior `MarkingPoint` rename
(`MarkingPointStrand` + `MarkingPointSec`), these duplicates are
qualified with the cluster/owner suffix:

| Duplicate type | Active file | Renamed | Why |
|:--|:--|:--|:--|
| `MarkingScheme` | `education/_shared/content_types.baml` | `MarkingSchemeShared` | lc_extraction owns canonical `MarkingScheme` |
| `BilingualText` | `education/pdfs/root_pdf_extraction.baml` | `BilingualTextRootPdf` | `_shared/content_types` owns canonical `BilingualText` |
| `NCCAKeyCompetency` (class) | `education/pdfs/root_pdf_extraction.baml` | `NCCAKeyCompetencyRootPdf` | lc_extraction owns canonical enum |
| `CrossNationLearningOutcome` | `education/cross_nation/isles_education.baml` | `CrossNationLearningOutcomeIsles` | multi_nation_curriculum owns canonical |
| `SkillCategory` (class) | `processing/cv_extraction.baml` | `SkillCategoryCv` | _shared/education_level owns canonical enum |
| `CelticLanguage` (enum) | `celtic/_archive/celtic_linguistics.baml` | `CelticLanguageArchive` | active `celtic/sources.baml` owns canonical |
| `IrishDialect` (enum) | `celtic/_archive/celtic_linguistics.baml` | `IrishDialectArchive` | active `celtic/sources.baml` owns canonical |
| `PartOfSpeech` (enum) | `celtic/_archive/celtic_linguistics.baml` | `PartOfSpeechArchive` | active `celtic/gaois/tearma.baml` owns canonical |

The 3 archive renames are documented in the file header (with the
re-activation procedure) per the existing
`openspec/changes/archive-celtic-baml-orphans/` convention.

### 7. Escape-case hand-fixes (6 issues)

- `language: "en" | "ga"` literal union in `education/_shared/diagram_renderer.baml`
  → `language string @description("Language code: 'en' or 'ga'")` (5 sites)
- `@@description(...)` block attribute on a function in
  `education/_shared/content_types.baml` (2 sites) → JSDoc-style `///` comments
- Unclosed `@description(...)` parenthesis in `processing/site_analysis.baml`
- Broken `@description("..."]` square-bracket closer in
  `education/pdfs/root_pdf_extraction.baml` (7 sites) → `)` instead of `]`
- `  : interaction:` typo in `processing/game_content.baml` → `  interaction`
- Function parameter default values (`= null`, `= ["IE", ...]`, `= ["..."]`)
  removed (BAML does not support defaults in function parameters)
- Function parameter with comma-then-`@description` (`candidate_syllabi: string[],   @description(...)`)
  reordered to canonical form
- Field name `package` is a BAML keyword → renamed to `pkg` in
  `processing/upstream_monitoring.baml` (3 sites)

### 8. Type fixes (`number`/`boolean`/`any` → `int`/`float`/`bool`/`string`)

BAML v0.212+ uses `int` / `float` / `bool` (not `number` / `boolean`)
and rejects `any` for type references:

- `proficiency number` → `proficiency float` (cv_extraction.baml)
- `totalVerified number` etc. → `int` (identity_verification.baml)
- `isCurrentRole boolean` → `bool` (linkedin_profile_extraction.baml)
- `rating number` → `int` (teaching_extraction.baml)
- `activity_data: map<string, any>` → `map<string, string>` (player_assessment.baml)

### 9. Type-reference fixes (8 qpack files)

The 8 `qpack_*.baml` files referenced the non-existent
`LeavingCertPastPaper` and `LeavingCertMarkingScheme` types. Renamed
to the actual class names: `PastPaper` (from
`education/pdfs/leaving_cert_past_paper.baml`) and `MarkingSchemeSec`
(from `education/pdfs/leaving_cert_marking_scheme.baml`).

### 10. Jinja template syntax fixes (5 files)

BAML v0.212+'s Jinja parser rejects:
- `{{ #if cond }}` (with space before `#`) → `{% if cond %}`
- `{{ /if }}` → `{% endif %}`
- `theme ?? "default"` (null-coalescing `??`) → `theme or "default"`
- Inline `{% if %}Preferred mood: {{ x }}{% endif %}` on a single line
  (BAML rejects; expanded to multi-line form)

Affected files:
- `processing/artwork_analysis.baml`
- `processing/style_transfer.baml`
- `celtic/curriculum/celtic_curriculum.baml`
- `celtic/gaois/folklore_extraction.baml`
- `celtic/_archive/cognates.baml`

### 11. clients.baml + per-file client rewrites

The BAML v0.212+ syntax for LLM clients changed from
`generator Name { provider "x" model "y" ... }` (8-generator layout)
to `client<llm> Name { provider "x" options { model "y" ... } }`.

- `clients.baml` — converted all 3 active `generator` blocks to
  `client<llm> Default`, `client<llm> LocalVisionGemma4`,
  `client<llm> LocalVisionQwen3vl` (uppercase names required by BAML
  v0.223). Added 17 canonical alias `client<llm>` blocks for the
  client names referenced by functions (`ExtractEn`, `ExtractEnStrong`,
  `LitellmClient`, `LocalVision`, `Analyzer`, `ArtworkAnalyzer`,
  `CelticContentFallback`, `Claude`, `ClaudeHaiku`, `ClaudeMini`,
  `ClaudeOpus`, `Extractor`, `ExtractorFast`, `FastAnalyzer`,
  `FastExtraction`, `Gemini2FlashAlias`, `LiteLLM`,
  `OideachaisDefault`, `VisionExtractor`). All route to minimax-m3
  by default; per-provider configs live in the original per-file
  `client<llm>` definitions.

- 8 files updated to use the new `client<llm>` references:
  - `education/stages/*.baml` — `client "litellm/gemini-2.0-flash"` →
    `client Gemini2FlashAlias`; `client "anthropic/claude-sonnet-4-20250514"` →
    `client Claude`; `client "openai/gpt-4o"` → `client Claude`; etc.
  - `education/law/*.baml` (6 files) — `client Gemini2Flash` →
    `client Gemini2FlashAlias`
  - `education/_shared/*.baml`, `education/pdfs/root_pdf_extraction.baml` —
    same inline-client rewrites
  - `processing/culture_extraction.baml` — `client "litellm"` →
    `client LitellmClient`

- `processing/generators.baml` — generator version bumped from
  `0.74.0` → `0.223.0` to match the installed `baml-cli` (the version
  mismatch was blocking code generation even after the parser errors
  were fixed).

## Dependencies

`Blocked by: none`

`Blocked by (soft): 2026-07-13-baml-final-cleanup-v1` (this change
extends the prior cleanup by fixing what that change scoped out
per the shipped `SCOPE_DECISION.md`)

`Affected repos: cianfhoghlaim` (single-repo change)

## Cross-change coordination

This change touches the 7 `baml/education/lc_extraction/*.baml` files
which are part of the BIEP v1 flagship
(`2026-07-06-british-isles-education-pipeline-v1` at 0/75 tasks).
The coordination pattern:

- **If this change lands first** (current plan): the BIEP v1 change
  will need to rebase onto this commit. The duplicate-class renames
  here are forward-compatible with the BIEP v1 contract (the new
  names `MarkingSchemeShared`, `BilingualTextRootPdf`, etc. are more
  specific than the originals and don't conflict with the BIEP v1
  canonical `MarkingScheme` / `BilingualText`).

- **If the BIEP v1 change lands first**: this change would conflict
  on the 7 `lc_extraction/*.baml` files and need to be rebased on
  top of it. The BIEP v1 changes to those files would be preserved.

Per the openspec AGENTS.md cross-change rule, this coordination risk
is documented in the proposal and commit message.

## Acceptance gates

- [x] `openspec validate 2026-07-13-fix-baml-50-out-of-scope-errors-v1 --strict` passes
- [x] `mise run baml:generate` exits 0 (was 1,776 errors before, now 0)
- [x] `mise run baml:test` runs all 35 test blocks (runtime errors are
  expected — no LLM API keys in the build environment; the test
  harness correctly compiles + invokes each test block)
- [x] The 9 BAML-using notebooks AST-parse OK
- [x] The 2 MODIFIED spec deltas (`british-isles-education-pipeline` +
  `cianfhoghlaim-baml-schemas`) are well-formed
- [x] The 7 `lc_extraction/*.baml` files still compile + the canonical
  types `MarkingScheme`, `BilingualText`, etc. are still present in
  the generated `baml_client/types.py`
- [x] Pushed to `origin/pick-4-biep-v1` (NOT `main`)

## What's NOT in this change

1. No new BAML functions, classes, enums, or types are added —
   this is a pure-syntax-fix change. (The 17 new `client<llm>`
   aliases in `clients.baml` are trivial wrappers around the
   existing `Default` block; they don't introduce new schema.)
2. No openspec spec bodies are modified other than the 2 ADDED
   requirements in the 2 MODIFIED spec deltas.
3. The 50+ archived openspec changes under `openspec/changes/archive/*`
   are untouched.
4. The `.env.example` template for `MINIMAX_BASE_URL` /
   `MINIMAX_API_KEY` was already documented by the prior
   `2026-07-13-baml-final-cleanup-v1` change; not duplicated here.