# 2026-07-25-baml-archive-orphaned-and-superseded-v1

## Why

The audit identified 15 BAML files at
`baml_src/british_isles/ireland/education/` that are either orphaned
(zero callers in active code) or shadow-collide with the canonical
`lc_extraction/*.baml`:

- **6 `grading/<subject>_grading.baml`** (753 LOC) — zero callers in
  `dlt/`, `orchestration/`, `agents/`, `notebooks/`, `scripts/`,
  `cocoindex/`, or `baml_src/`
- **6 `web/<subject>_web.baml`** (1,298 LOC) — zero callers AND duplicate
  function names (`WebStudyPlan`, `WebExamPaperDiscussion`,
  `WebMarkingSchemeExplanation` declared in 6 files — would crash
  `baml-cli generate`)
- **3 `pdfs/leaving_cert_*.baml`** (254 LOC) — function names
  (`ExtractLeavingCertSyllabus`, `ExtractPastPaper`, `ExtractMarkingScheme`)
  shadow the canonical `lc_extraction/*.baml` versions — Dagster asset
  references pick up whichever loads last (pickup bug)

Per the user's choice, **move (not delete)** to
`baml_src/british_isles/ireland/education/_legacy/{grading,web,pdfs}/`.
Add `## REMOVED Requirements` to the BIEP v1 spec pointing at the
canonical homes (`lc_extraction/*.baml`).

## What changes

### 1. Move 15 BAML files to `_legacy/`

- MOVE 6 `grading/*.baml` → `baml_src/.../_legacy/grading/`
  - chemistry_grading.baml
  - computer_science_grading.baml
  - english_grading.baml
  - gaeilge_grading.baml
  - geography_grading.baml
  - mathematics_grading.baml

- MOVE 6 `web/*.baml` → `baml_src/.../_legacy/web/`
  - chemistry_web.baml
  - computer_science_web.baml
  - english_web.baml
  - gaeilge_web.baml
  - geography_web.baml
  - mathematics_web.baml

- MOVE 3 `pdfs/leaving_cert_*.baml` → `baml_src/.../_legacy/pdfs/`
  - leaving_cert_marking_scheme.baml
  - leaving_cert_past_paper.baml
  - leaving_cert_syllabus.baml

### 2. Create `_legacy/` package

- NEW `baml_src/.../_legacy/__init__.baml` (empty re-export)
- NEW `baml_src/.../_legacy/grading/README.md` (REMOVED notice)
- NEW `baml_src/.../_legacy/web/README.md` (REMOVED notice,
  explains the duplicate-function-name collision)
- NEW `baml_src/.../_legacy/pdfs/README.md` (REMOVED notice,
  explains the `lc_extraction/` shadow collision)

### 3. Spec delta

`openspec/specs/british-isles-education-pipeline/spec.md` — add 3
`## REMOVED Requirements` entries naming the 15 archived paths and
pointing at the canonical homes:
- `grading/<subject>_grading.baml` → superseded by `lc_extraction/marking_scheme.baml`
- `web/<subject>_web.baml` → superseded by web-side BAML (none active)
- `pdfs/leaving_cert_*.baml` → superseded by `lc_extraction/*.baml`

## Dependencies

```yaml
Blocked by: 2026-07-25-nb-utils-ibis-first-v1
            2026-07-25-cocoindex-per-subject-dedup-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-25-baml-archive-orphaned-and-superseded-v1 --strict` passes
- 15 BAML files moved (not deleted)
- 3 README.md REMOVED-notice files added
- `cd baml_src && uv run baml-cli generate` succeeds cleanly
- `mise run baml:cli-test` (the CI gate from `2026-07-12-baml-cli-test-ci-gate-v1`) passes
- The duplicate-function-name shadow bug is resolved (`baml-cli generate` no longer crashes)
- The `pdfs/` vs `lc_extraction/` shadow collision is resolved
- `mise run lint:skills` — must remain 53/53
- Push target: `origin/main`

## Cross-references

- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the parent BIEP v1 LC spec that gets 3 new `## REMOVED Requirements`
- [`oideachais-baml-schemas`](../../specs/oideachais-baml-schemas/spec.md) —
  the BAML extraction library this change cleans up
- `openspec/changes/2026-07-12-baml-cli-test-ci-gate-v1/` — the CI gate
  we run for codegen validation
- `.agents/skills/baml/SKILL.md` — the BAML schema patterns