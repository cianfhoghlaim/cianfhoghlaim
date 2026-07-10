# Change: 2026-07-13-v6-drift-remediation-final-v1

## Why

The parent drift remediation change, `2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1`, was still at **0/52 tasks** while several parallel changes were landing on `pick-4-biep-v1`. The openspec-only drift subset landed in `2026-07-13-openspec-drift-cleanup-v1`; this standalone change finishes the remaining in-repo cleanup that does not require touching the separate `bonneagar` repository.

This change deliberately skips the `bonneagar/` infra-drift bucket because that tree is a separate repo/worktree boundary. It focuses on the Cianfhoghlaim repo surfaces: `.agents/skills/`, active openspec specs, and the OpenSpec validation defects that were already present on the branch.

## What changes

### Bucket 1 — Skill drift cleanup

- Baseline: **54 files** under `.agents/skills/` contained `sruth/` path references (**219 matches**).
- Cleanup: rewrote those path references to v4 `cianfhoghlaim/`, `cianfhoghlaim/agents/...`, `cianfhoghlaim/web/apps/...`, `cianfhoghlaim/dlt/...`, `cianfhoghlaim/cocoindex/...`, `cianfhoghlaim/orchestration/...`, `cianfhoghlaim/meaisinfhoghlaim/...`, and `bonneagar/stacks/browser` equivalents as appropriate.
- Post-check target: `.agents/skills/` has **0 `sruth/` matches** and **0 `sruth.` dotted matches**.
- Skill loader gate: `mise run lint:skills` reports `53 skills pass`.

### Bucket 2 — Active spec validation errors

- Baseline: **4 pre-existing strict validation errors**:
  - `oideachais-pipeline`: 1 Requirement outside the main `## Requirements` section.
  - `meaisinfhoghlaim-platform`: 3 Requirements outside the main `## Requirements` section.
- Cleanup:
  - Moved `LC5-subject + Gemini 6-corpus pipelines` back into `oideachais-pipeline`'s main `## Requirements` section.
  - Moved the 3 v4 extension Requirements back into `meaisinfhoghlaim-platform`'s main `## Requirements` section.
  - Repaired the comment-adjacent parser edge so the first moved requirement text begins with a SHALL statement.
- Post-check target: both specs validate with `openspec validate <spec> --strict`.

### Bucket 3 — Bare `oideachais.*` re-evaluation

- Baseline: **142** `from oideachais.` / `oideachais.<lowercase>` references in active `openspec/specs/*.md`.
- Decision:
  - Documentation shorthand such as MotherDuck schemas (`oideachais.education.ie...`), capability names, and logical quadrant names remains as-is.
  - Actual Python import examples are rewritten from `from oideachais...` to `from cianfhoghlaim...`.
- Post-check target:
  - `from oideachais.` import examples in active specs: **0**.
  - Remaining bare `oideachais.*` references: documentation shorthand only.

### Bucket 4 — Optional T1 follow-ups

- Baseline: `cianfhoghlaim/docs/stacks/` does not exist; `docs/stacks/` currently contains 89 markdown files including `README.md`.
- Decision: deferred. The user marked this bucket optional and the requested stack-doc generator is not present in this worktree (`scripts/generate-stack-env-example.ts` exists; no `generate-stack-docs.ts` equivalent was found). No `bonneagar/` files are touched.

## Affected specs

| Spec | Why |
|:--|:--|
| `infrastructure-stacks` | Adds a requirement that `.agents/skills/` must use the v4 namespace convention and must not reintroduce `sruth/` path drift. |
| `oideachais-pipeline` | Documents the strict-format fix for the LC5/Gemini requirement and the code-import rewrite to `from cianfhoghlaim...`. |
| `meaisinfhoghlaim-platform` | Documents the strict-format fix for the 3 v4 extension requirements and the code-import rewrite to `from cianfhoghlaim...`. |
| `agent-memory-systems` | Documents the strict-format fix for the LC5/Gemini memory-backend requirement and the code-import rewrite to `from cianfhoghlaim...`. |
| `documentation` | Adds the stack docs cross-reference requirement; implementation is deferred because this bucket is optional and the doc generator was not present. |
| `oideachais-cocoindex-v1-migration` | Documents the import-example rewrite from `from oideachais...` to `from cianfhoghlaim...` for actual code paths. |

## Acceptance gates

- [x] `openspec validate 2026-07-13-v6-drift-remediation-final-v1 --strict` passes.
- [x] Skill drift reduced from 54 files / 219 matches to 0 files / 0 matches for `sruth/` in `.agents/skills/`.
- [x] `mise run lint:skills` reports `53 skills pass`.
- [x] The 4 validation errors in `oideachais-pipeline` + `meaisinfhoghlaim-platform` are resolved.
- [x] Actual `from oideachais.` code-import examples in active specs are reduced to 0.
- [ ] Optional T1 docs/secrets follow-up is shipped. Deferred by design; see Bucket 4.

## Dependencies

`Blocked by: none`

`Blocked by (soft): 2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1` (parent change; this is the final in-repo cleanup subset)

`Blocked by (soft): 2026-07-13-openspec-drift-cleanup-v1` (parallel openspec drift subset already handled broad `sruth.<quadrant>` cleanup)

`Affected repos: cianfhoghlaim` (the `bonneagar/` repo is intentionally not modified)

## Deferred work

1. `bonneagar/` infra drift — separate repo/worktree, out of scope here.
2. Optional T1 stack-doc generation — defer until a `generate-stack-docs` script exists or until the stack-doc source of truth is clarified (`docs/stacks/` vs `cianfhoghlaim/docs/stacks/`).
3. Optional secrets.env normalization — defer with T1 because it belongs with stack generation and may touch the `bonneagar` repo boundary.
