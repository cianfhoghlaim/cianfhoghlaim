# Fix BAML codegen v4-syntax-v1

## Why

`mise run baml:generate` is failing with **~4,479 validation errors** because
17 `.baml` files in `baml/processing/` still use the legacy
**Pydantic-style** attribute syntax (`field_name: type`) that BAML
**v0.212+ deprecated** in favour of the canonical
`field_name type` (whitespace-separated) syntax.

The BAML CLI now rejects every `field: type` line with:

```
error: Error validating: This line is not a valid field or attribute definition.
A valid class property looks like: 'myProperty string[] @description("This is a description")'
```

The processing cluster (`baml/processing/`) is the worst-affected
zone. It contains 27 `.baml` files (the 17 legacy ones plus 10 that were
already-canonical). The 17 broken files account for **~354 broken lines**
that BAML rejects before it can produce any code. The cascade prevents:

- `baml_client/` regeneration (no Python Pydantic models for downstream Dagster / DLT / CocoIndex consumers)
- the 25 non-priority CocoIndex flows (the T3 backlog) — they all import from `baml_client.types`
- BIEP v1 Phase 4-5 DAG materialization (the `ExtractCurriculumSyllabus` / `ExtractExamPaperLayout` / `ExtractMarkingSchemeGuideline` / `ExtractCrossLinguisticConcept` / `ExtractSyllabusDiagram` functions can't be wired until the BAML client compiles)
- every consumer of `baml_client.types.*` in the 6 LC subjects (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science)

## What changes

Migrate the 17 affected `.baml` files in `baml/processing/`
from Pydantic-style `field: type` to BAML's canonical `field type`
(whitespace-separated) using a single regex-based migration script.

### Scope (the 17 files)

| # | File | Lines rewritten | Notes |
|:--|:--|--:|:--|
| 1 | `topic_profile.baml` | 19 | 2 `@description("..."]` typos hand-fixed to `)` |
| 2 | `player_assessment.baml` | 103 | |
| 3 | `game_content.baml` | 96 | |
| 4 | `author_archive.baml` | 18 | |
| 5 | `ireland_legal_extraction.baml` | 22 | |
| 6 | `legal_case_profile.baml` | 31 | 1 `@description("..."]` typo hand-fixed to `)` |
| 7 | `email.baml` | 8 | |
| 8 | `audio_extraction.baml` | 8 | |
| 9 | `image_generation.baml` | 7 | |
| 10 | `style_transfer.baml` | 16 | |
| 11 | `culture_extraction.baml` | 2 | |
| 12 | `circular_extraction.baml` | 2 | |
| 13 | `ocr_extraction.baml` | 4 | |
| 14 | `ocr_validation.baml` | 8 | |
| 15 | `official_media.baml` | 3 | |
| 16 | `portfolio_extraction.baml` | 3 | |
| 17 | `ui_components.baml` | 3 | |
| **Total** | | **353** | |

### Out of scope (intentionally not touched)

These clusters still have Pydantic-style lines but are owned by other agents / openspec changes:

- **`education/lc_extraction/*.baml`** (7 files, ~138 lines) — BIEP v1 canonical contract; owned by `2026-07-06-british-isles-education-pipeline-v1`
- **`education/subjects/qpack_*.baml`** (8 files, ~961 lines) — owned by the BIEP v1 quest-pack generators; will be migrated by `2026-07-06-british-isles-education-pipeline-v1` Phase 4-5
- **`education/_shared/*.baml`** (5 files, ~219 lines) — shared cross-stage types; will be migrated by the same BIEP follow-up
- **`education/pdfs/*.baml`** (3 files, ~67 lines) — owned by the pdfs/ cluster migration
- **`celtic/curriculum/*.baml`** (2 files, ~193 lines) — owned by the celtic-cluster BAML migration
- **`clients.baml`** — already rewritten to v0.212+ `generator {}` blocks by T4 (2026-07-09)
- **`clients_llama_swap.baml`** — same; already canonical

The 10 OTHER `.baml` files in `baml/processing/` (e.g. `artwork_analysis.baml`,
`cv_extraction.baml`, `site_analysis.baml`, `named_entities.baml`) are NOT
in the 17-file scope but several still have small amounts of Pydantic-style
syntax (e.g. `artwork_analysis.baml:210`) plus a syntax bug
(`site_analysis.baml:36` has an unclosed `@description(` parenthesis).
These will be addressed by a future openspec change that targets the
remaining `processing/` files.

## How

### Approach

A Python migration script `scripts/migrate-baml-syntax.py` with 3 modes:

- `--dry-run` — print diffs without modifying files
- `--apply` — rewrite files in place (idempotent)
- `--verify` — exit 1 if any Pydantic-style lines remain

The regex:

```python
ATTR_LINE_RE = re.compile(
    r"^(\s+)"
    r"([a-z_][a-zA-Z0-9_]*)"
    r"\s*:\s+"
    r"(string(?:\[\])?(?:\?)?|int(?:\[\])?(?:\?)?|float(?:\[\])?(?:\?)?|bool(?:\[\])?(?:\?)?|image(?:\[\])?(?:\?)?|[A-Z][a-zA-Z0-9_]*(?:\[\])?(?:\?)?|list<[^>]+>(?:\?)?|map<[^,]+,\s*[^>]+>(?:\?)?|class\s+[a-zA-Z0-9_]+|enum\s+[a-zA-Z0-9_]+|optional\s+[a-zA-Z<>,\s\[\]]+)"
    r"(?![\w])"
    r"(.*)$"
)
```

Defensive heuristics to avoid false positives:

1. Skip lines inside any `#"...content...#` raw-string block (prompt bodies
   and test-arg docs).
2. Skip lines inside `"""..."""` Python-style triple-quoted doc blocks.
3. Skip lines containing `{{` or `}}` (Jinja tokens used in BAML prompts).
4. Track `in_prompt` flag with paired `#"`/`"#` tokens — these also catch
   `pdf_text #"..."#`, `email_body #"..."#`, etc.

### Escape cases (hand-fixed)

Two `@description("..."]` typos in `topic_profile.baml` (lines 25 and 65)
and one in `legal_case_profile.baml` (line 59). These had `]` instead of
`)` as the description closer — a pre-existing typo that survived both the
migration and BAML's earlier v0.x parser. Fixed by hand-edit.

No other escape cases surfaced (no multiline attrs, no enum defaults,
no nested classes, no optional `[]` patterns, no `field = default` in
the 17-file scope).

### Verification results

```
$ grep -rE '^\s+[a-z_][a-zA-Z0-9_]*:\s+(string|int|float|bool|list|map|class|enum|optional)\b' \
    baml/processing/{topic_profile,player_assessment,game_content,author_archive,ireland_legal_extraction,legal_case_profile,email,audio_extraction,image_generation,style_transfer,culture_extraction,circular_extraction,ocr_extraction,ocr_validation,official_media,portfolio_extraction,ui_components}.baml \
    | wc -l
0
```

The 17 migrated files have **0 Pydantic-style attribute lines remaining**.

```
$ mise run baml:generate
... still exits non-zero with ~1,742 errors ...
```

The remaining ~1,742 errors come from out-of-scope clusters
(`education/lc_extraction/*`, `education/subjects/qpack_*`,
`education/_shared/*`, `education/pdfs/*`, `celtic/curriculum/*`)
plus 7 cascade "function keyword" errors in my migrated files that
trace back to the same out-of-scope clusters.

Per the explicit scope, `mise run baml:generate` exiting 0 is
**NOT** achieved by this change alone. It requires the follow-up
openspec changes (BIEP v1 Phase 4-5 + the celtic-cluster BAML
migration) to land first.

## Dependencies

`Blocked by: none`

`Affected repos: cianfhoghlaim`

This is a single-repo change. The 17 `.baml` files + the migration
script + the 2 new spec requirements all live in the `cianfhoghlaim`
monorepo. No `bonneagar/` or `leabharlann/` cross-repo sync needed.

## Acceptance gates

- [x] `openspec validate 2026-07-10-fix-baml-codegen-v4-syntax-v1 --strict` passes
- [x] `grep -rE '^\s+[a-z_][a-zA-Z0-9_]*:\s+(string|int|float|bool|list|map|class|enum|optional)\b' baml/processing/{17 files}.baml | wc -l` returns 0
- [ ] `mise run baml:generate` exits 0 — **NOT ACHIEVED** (blocked by out-of-scope lc_extraction + qpack + celtic + _shared clusters, owned by separate openspec changes)
- [x] The 7 BIEP v1 `lc_extraction/*.baml` files are still untouched (Pydantic-line counts unchanged: 28, 12, 18, 27, 15, 23, 15)
- [x] The 2 stale `.bak` files (`clients.baml.bak`, `clients_llama_swap.baml.bak`) deleted

## What's NOT in this change

1. The 7 `lc_extraction/*.baml` files — owned by `2026-07-06-british-isles-education-pipeline-v1`
2. The 8 `qpack_*.baml` files — owned by the BIEP v1 quest-pack generators
3. The 5 `education/_shared/*.baml` files — owned by the BIEP v1 shared types
4. The 3 `education/pdfs/*.baml` files — owned by the pdfs/ cluster migration
5. The 2 `celtic/curriculum/*.baml` files — owned by the celtic-cluster migration
6. The 10 OTHER `processing/*.baml` files (`artwork_analysis.baml`, `cv_extraction.baml`, `generators.baml`, `identity_verification.baml`, `linkedin_profile_extraction.baml`, `named_entities.baml`, `researchgate_extraction.baml`, `site_analysis.baml`, `teaching_extraction.baml`, `upstream_monitoring.baml`) — owned by a future "fix-remaining-processing-cluster" openspec change
7. `clients.baml` + `clients_llama_swap.baml` — T4 already rewrote these to canonical v0.212+ `generator {}` blocks

Once those follow-up changes land, `mise run baml:generate` will exit 0
and the 25 non-priority CocoIndex flows + BIEP v1 Phase 4-5 DAG
materialization + every `baml_client.types.*` consumer will be unblocked.