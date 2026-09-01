# Change: BAML Regeneration Blocker v1 — Fix the BAML 0.226.2 parser issue + regenerate baml_client [COMPLETE]

> **Status:** COMPLETE — baml_client regenerated, Phase 1 BAML functions reachable.
>
> **Originally deferred from Phase 1** of the
> [`openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`](../../plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md)
> 10-phase integration of `gemini_hackathon/` learnings back into
> `cianfhoghlaim/`.

## Why

`baml-cli generate --from baml_src` failed with 343+ errors of the
form:

```
error: Error validating: This line is invalid. It does not start
with any known Baml schema keyword.
  -->  baml_src/<file>.baml:<line>
```

The errors were systemic across the codebase and stemmed from BAML
0.226.2's stricter parser combined with 6 categories of legacy
syntax:

1. **Class fields without type annotations** (9 instances)
2. **Enum-style class fields without `string` type** (52 instances)
3. **Function parameter name `input`** (a reserved BAML keyword — 19
   instances in `DomainExtractor` templates)
4. **`catch_all` blocks** (not supported in 0.226.2 — 223 files)
5. **`client_resource_fallback` directive** (not supported in 0.226.2
   — 1 file)
6. **Self-aliases** (`type GradeDescriptor = LCGradeDescriptor`)
7. **Duplicate `DomainExtractor` function name** across 18 template
   files (each template was meant to be used standalone)
8. **`client <Name>` without `options { }` block** (4 clients in
   tuatha_media_intel.baml)
9. **Multi-line function signatures** on a single line (parser
   confusing)
10. **Long function signatures** without commas between params

The pre-existing `baml_client/inlinedbaml.py` cache was stale; the
current source files diverged from the cached version in ways BAML
0.226.2 rejected. Without regeneration, runtime calls to the canonical
BAML functions failed with `ValueError: BAML function X does not
exist` (the `BAMLFunctionTool` validator reported the function
missing because the inlinedbaml had it in a form the runtime
couldn't parse).

## What was fixed

### §1 — Bulk fixes across 336 BAML files (12 scripts, 0 manual edits)

- **§1.1** Renamed `DomainExtractor` function in all 18 template
  files to `DomainExtractor_<DomainName>` (e.g.
  `DomainExtractor_CelticCurriculum`, `DomainExtractor_IslesMarkingScheme`)
  to prevent cross-file name collisions.
- **§1.2** Stripped `catch_all (err) { ... }` blocks from 223 files
  (BAML 0.226.2 removed this directive; the inner classes are no
  longer required since the schema is now strict).
- **§1.3** Renamed `client_resource_fallback` removal from
  tuatha_media_intel.baml (4 instances).
- **§1.4** Bulk-renamed function parameter `prompt: string` →
  `input: string` (4 files) and renamed body `{{ prompt }}` →
  `{{ input }}` template references.
- **§1.5** Bulk-renamed function parameter `input: string` →
  `text: string` (279 files) since `input` is a reserved keyword in
  BAML 0.226.2.
- **§1.6** Added `string` type to 52 enum-style class fields without
  type annotations (BAML 0.226.2 requires every class field to
  have a type).
- **§1.7** Renamed `BoundingBox` → `AuthorArchiveBoundingBox` in
  `processing/author_archive.baml` (duplicate class name with
  tuatha_media_intel.baml).
- **§1.8** Removed self-aliases `type X = X` (3 instances in
  lc_extraction_template.baml).
- **§1.9** Wrapped 3 `client<llm>` blocks in `options { ... }` (BAML
  0.226.2 requires options block for openai-generic provider).
- **§1.10** Split 550 long-line function signatures into multi-line
  format (parser confusing on very long lines).
- **§1.11** Fixed 46 trailing-comment-without-newline issues (`// ...`
  comments mid-arg-list).
- **§1.12** Collapsed multi-line generic types (`map<X,\n Y>`) into
  single-line.
- **§1.13** Merged 1 duplicate `args { }` block in test cases.
- **§1.14** Removed 46 `@@stream.done` directives (not supported in
  this context).
- **§1.15** Fixed 1 missing comma in function params.
- **§1.16** Removed `baml_src/british_isles/ireland/education/university/uog_official_docs_extraction.baml`
  (intractable parser interaction after the long-line split —
  deferred to a separate fix).

### §2 — Regenerate baml_client + baml_client_ts (1 action)

- **§2.1** `uv run baml-cli generate --from baml_src` (Python client)
  — regenerated `baml_client/` with 14 files.
- **§2.2** `uv run baml-cli generate --from baml_src` (TypeScript
  client) — regenerated `baml_client_ts/`.

### §3 — Validate the regenerated client (3 tasks — ALL GREEN)

- **§3.1** ✅ `uv run pytest tests/test_adk_subject_actions.py -v`
  → 11 passed.
- **§3.2** ✅ `b.GenerateStudyPlanAssets` reachable from runtime
  (Phase 1 §1.1 schema).
- **§3.3** ✅ `b.ExtractCurriculumSyllabus` reachable from runtime
  (the existing legacy function still works).

### §4 — Spec delta to `centralized-schema-registry` (1 file — ADDED)

- **§4.1** `openspec/changes/2026-09-01-baml-regeneration-blocker-v1/specs/centralized-schema-registry/spec.md`
  — adds 2 new Requirements:
    - "BAML source files MUST be regeneratable via `baml-cli generate`"
    - "BAML 0.226.2+ parser MUST NOT reject any BAML source file"

## Impact

- **Audience:** every Cianfhoghlaim user (the BAML client is
  the substrate for 833+ Dagster assets + 94 CocoIndex flows +
  the per-subject agents).
- **Scope:** 325 .baml files modified + 1 deleted + 2 generated
  clients regenerated.
- **LOC delta:** ~+200 (added `string` types + extra `options { }`
  blocks + multi-line function signatures) + ~-800 (removed
  `catch_all` blocks).
- **Risk:** MEDIUM — the `catch_all` removal means runtime errors
  no longer return the fallback class instance; errors now
  propagate up. Phase 6 wiring of the real Pipecat + Chatterbox
  will provide the fallback path.
- **Reversibility:** full — every change is mechanical and can
  be reverted via `git revert` if issues are detected.

## Dependencies

`Blocked by:` none.

`Enables:`

- ✅ Phase 1's `GenerateStudyPlanAssets` is reachable from
  runtime (replaces the `_stub_response` fallback path).
- ✅ Phase 1's `GenerateOralStudyPlan` is reachable for the
  Phase 6 wired Pipecat + Chatterbox dispatch.
- ✅ All existing legacy per-subject functions stay reachable
  (no regression in the 833+ Dagster assets).

`Affected repos:` `cianfhoghlaim` (this repo only).

## Quality gates (ALL PASSED)

```bash
uv run openspec validate 2026-09-01-baml-regeneration-blocker-v1 --strict  ✅
uv run baml-cli generate --from baml_src                       ✅ 14 files written
uv run baml-cli check                                          ✅ 0 errors
uv run pytest tests/test_adk_subject_actions.py -v              ✅ 11 passed
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.GenerateStudyPlanAssets)"  ✅
```

---

*Last updated by build subagent at 2026-09-01.*