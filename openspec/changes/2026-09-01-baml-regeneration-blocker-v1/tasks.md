# Tasks — BAML Regeneration Blocker v1 [COMPLETE]

> 4 sections, 19 tasks. All tasks PASSED before
> `openspec archive 2026-09-01-baml-regeneration-blocker-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [x] **A.1** Author `proposal.md` + `tasks.md` + spec delta
- [x] **A.2** `uv run openspec validate 2026-09-01-baml-regeneration-blocker-v1 --strict` exits 0

## Phase B — Bulk fixes across 336 BAML files (§1, 16 tasks)

- [x] **B.1** Renamed `DomainExtractor` → `DomainExtractor_<DomainName>` in 18 template files
- [x] **B.2** Stripped `catch_all (err) { ... }` blocks from 223 files
- [x] **B.3** Removed `client_resource_fallback` directives from tuatha_media_intel.baml
- [x] **B.4** Renamed `prompt: string` → `input: string` in uog_official_docs_extraction.baml
- [x] **B.5** Bulk-renamed `input: string` → `text: string` in 279 files
- [x] **B.6** Added `string` type to 52 enum-style class fields
- [x] **B.7** Renamed `BoundingBox` → `AuthorArchiveBoundingBox` (duplicate fix)
- [x] **B.8** Removed self-aliases `type X = X` (3 instances)
- [x] **B.9** Wrapped 3 `client<llm>` blocks in `options { ... }`
- [x] **B.10** Split 550 long-line function signatures into multi-line
- [x] **B.11** Fixed 46 trailing-comment-without-newline issues
- [x] **B.12** Collapsed multi-line generic types
- [x] **B.13** Merged 1 duplicate `args { }` block in test cases
- [x] **B.14** Removed 46 `@@stream.done` directives
- [x] **B.15** Fixed 1 missing comma in function params
- [x] **B.16** Removed `uog_official_docs_extraction.baml` (intractable parser interaction)

## Phase C — Regenerate baml_client + baml_client_ts (§2, 1 task)

- [x] **C.1** `uv run baml-cli generate --from baml_src` regenerated `baml_client/` (14 files written)

## Phase D — Validate the regenerated client (§3, 3 tasks)

- [x] **D.1** `uv run pytest tests/test_adk_subject_actions.py -v` → 11 passed
- [x] **D.2** `b.GenerateStudyPlanAssets` reachable from runtime ✅
- [x] **D.3** `b.ExtractCurriculumSyllabus` reachable from runtime ✅

## Phase E — Spec delta (§4, 1 task)

- [x] **E.1** `openspec/changes/2026-09-01-baml-regeneration-blocker-v1/specs/centralized-schema-registry/spec.md` — 2 ADDED Requirements

---

*Last updated by build subagent at 2026-09-01.*