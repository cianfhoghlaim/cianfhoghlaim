# Tasks — Fix BAML 50 out-of-scope errors v1

## 1. Capture baseline (15 min)

- [x] Run `mise run baml:generate` on the unchanged tree; capture the
  full output to `/tmp/baml-50-errors-before-full.txt` (1,776 `error:`
  lines across 34 files).
- [x] Categorise the per-file error count (top file is
  `education/_shared/content_types.baml` with 154 errors; the 8
  `qpack_*.baml` files collectively account for 1,041 errors).

## 2. Bulk migration (1.5 hours)

- [x] Run `uv run python scripts/migrate-baml-syntax.py --apply --all`
  (the script was originally shipped in commit `8669278c2` for the
  17-file processing scope; passing `--all` extends it to all 75
  `.baml` files).
- [x] Result: 1,086 lines rewritten across 47 files. The 17 prior
  `processing/` files report 0 changes (already migrated).

## 3. Restore function-parameter colons (15 min)

- [x] Write `scripts/restore-function-param-colons.py` — a new helper
  that walks every `.baml` file, detects `function Name(` openers,
  tracks paren depth, and re-adds the colons inside the function
  arg list.
- [x] Run with `--apply`: 405 parameter lines rewritten.

## 4. Hand-fix escape cases (30 min)

- [x] Inline comma-separated enums (3 sites in qpack_*.baml).
- [x] Inline class declarations with `;` (4 sites in
  qpack_*.baml).
- [x] Accented character enum value names (5 sites in
  qpack_gaeilge.baml).
- [x] Test block `input { ... }` → `args { ... }` + remove
  `output { ... }` (1 file).
- [x] Duplicate BAML class/enum definitions (8 duplicates renamed
  with cluster suffixes).
- [x] Type fixes (`number` → `int`/`float`, `boolean` → `bool`,
  `any` → `string`).
- [x] Type-reference fixes (`LeavingCertPastPaper` → `PastPaper`,
  `LeavingCertMarkingScheme` → `MarkingSchemeSec`).
- [x] Jinja template syntax fixes (`{{ #if }}` → `{% if %}`,
  `{{ /if }}` → `{% endif %}`, `??` → `or`, inline if/endif
  expanded to multi-line form).
- [x] Literal union type `language: "en" | "ga"` → `language string`.
- [x] Block-level `@@description(...)` on functions → JSDoc `///`.
- [x] Unclosed `@description("..."]` parenthesis in
  site_analysis.baml.
- [x] Square-bracket closer `@description("..."]` →
  `@description("...")` (7 sites in root_pdf_extraction.baml).
- [x] Field name `package` is a BAML keyword → renamed to `pkg`
  in upstream_monitoring.baml (3 sites).
- [x] Function parameter default values removed (BAML does not
  support them).

## 5. Rewrite clients.baml + per-file client references (20 min)

- [x] Convert the 3 active `generator` blocks in `clients.baml`
  to `client<llm>` blocks (uppercase names).
- [x] Add 17 canonical alias `client<llm>` blocks for the client
  names referenced by functions.
- [x] Rewrite inline `client "litellm/..."` and
  `client "anthropic/..."` references across 8 files
  (education/stages/*.baml, education/law/*.baml,
  education/_shared/*.baml, education/pdfs/root_pdf_extraction.baml,
  processing/culture_extraction.baml).
- [x] Bump `processing/generators.baml` `version` from `0.74.0` to
  `0.223.0` to match the installed `baml-cli`.

## 6. Write openspec change artifacts (15 min)

- [x] `proposal.md` — the full Why/What/Acceptance narrative.
- [x] `tasks.md` — this file.
- [x] `specs/oideachais-baml-schemas/spec.md` — 1 ADDED requirement
  capturing the "all 50 errors resolved; baml:generate exits 0" gate.
- [x] `specs/british-isles-education-pipeline/spec.md` — 1 ADDED
  requirement capturing the lc_extraction/*.baml syntax contract.

## 7. Run quality gates (10 min)

- [x] `mise run baml:generate` exits 0 (was 1,776 errors before).
- [x] `mise run baml:test` runs the 35 test blocks (the 35 runtime
  errors are network/env-related — no LLM API keys — not BAML syntax
  errors).
- [x] The 9 BAML-using notebooks AST-parse OK.
- [x] `openspec validate 2026-07-13-fix-baml-50-out-of-scope-errors-v1 --strict`
  passes.

## 8. Commit + push (10 min)

- [x] `git add -A` the 47 modified `.baml` files + the new
  `scripts/restore-function-param-colons.py` + the openspec change.
- [x] `git commit` with a descriptive message explaining the scope.
- [x] `git push --set-upstream origin pick-4-biep-v1` (NOT main).

## Final report (10 min)

- [x] Report back to the build agent with: commit hash, openspec
  validate result, 1,776 → 0 error transition (per-cluster
  breakdown), `mise run baml:generate` output, `mise run baml:test`
  output, 9-notebook import check result, 2 MODIFIED spec delta
  summaries, blockers / open questions.