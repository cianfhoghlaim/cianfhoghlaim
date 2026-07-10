# Tasks: 2026-07-13-v6-drift-remediation-final-v1

## 1. Pre-flight and baseline

- [x] Checkout `pick-4-biep-v1`.
- [x] Attempt `git pull --rebase`.
  - Result: skipped because the working tree already had unstaged changes from parallel work; no rebase was in progress.
- [x] Capture bucket baselines:
  - Skill drift: 54 files / 219 `sruth/` matches in `.agents/skills/`.
  - Validation errors: 4 strict OpenSpec errors across `oideachais-pipeline` (1) and `meaisinfhoghlaim-platform` (3).
  - Bare `oideachais.*`: 142 active-spec matches.
  - Stack docs: `cianfhoghlaim/docs/stacks` = 0; `docs/stacks` = 89 markdown files including README.

## 2. Skill drift cleanup

- [x] Rewrite `.agents/skills/` path references from pre-v4 `sruth/<quadrant>/...` to v4 paths.
- [x] Rewrite dotted skill examples from `sruth.<quadrant>...` to v4 package/import forms.
- [x] Verify `.agents/skills/` has 0 `sruth/` matches.
- [x] Verify `.agents/skills/` has 0 `sruth.` dotted matches.
- [x] Run `mise run lint:skills`.
  - Result: `lint-skills: 53 skills pass`.

## 3. Validation errors

- [x] Move `oideachais-pipeline`'s `LC5-subject + Gemini 6-corpus pipelines` Requirement into the main `## Requirements` section.
- [x] Move `meaisinfhoghlaim-platform`'s 3 v4 extension Requirements into the main `## Requirements` section.
- [x] Re-run strict validation for both specs.
  - Result: both specs valid.

## 4. Bare `oideachais.*` re-evaluation

- [x] Inspect active-spec `from oideachais.` import examples.
- [x] Rewrite actual code-import examples to `from cianfhoghlaim...`.
- [x] Preserve documentation shorthand (`oideachais.*` DB schemas, logical quadrant shorthand, capability names).
- [x] Verify active-spec `from oideachais.` examples are 0.
- [x] Validate every spec touched by this pass:
  - `oideachais-pipeline`
  - `meaisinfhoghlaim-platform`
  - `agent-memory-systems`
  - `oideachais-cocoindex-v1-migration`

## 5. Optional T1 follow-ups

- [ ] Generate 94 missing `docs/stacks/<name>.md` files.
  - Deferred: current worktree has `scripts/generate-stack-env-example.ts` and `scripts/generate-stack-pangolin-yaml.ts`, but no `generate-stack-docs.ts` equivalent.
- [ ] Normalize 18 `secrets.env` files to `infisical://` references.
  - Deferred with stack-doc generation because stack secrets likely cross the `bonneagar` repo boundary.
- [ ] Run `bun run stack-doctor --strict`.
  - Deferred because no stack docs/secrets changes were shipped.

## 6. OpenSpec change files

- [x] Write `proposal.md`.
- [x] Write this `tasks.md`.
- [x] Write spec deltas:
  - [x] `specs/infrastructure-stacks/spec.md`
  - [x] `specs/oideachais-pipeline/spec.md`
  - [x] `specs/meaisinfhoghlaim-platform/spec.md`
  - [x] `specs/agent-memory-systems/spec.md`
  - [x] `specs/documentation/spec.md`
  - [x] `specs/oideachais-cocoindex-v1-migration/spec.md`

## 7. Validate, commit, push

- [x] Run `openspec validate 2026-07-13-v6-drift-remediation-final-v1 --strict`.
- [x] Re-run affected spec validation.
- [x] Re-run bucket post-counts.
- [x] Commit only intended files (leave pre-existing parallel-agent dirty state unstaged).
- [x] Push to `origin/pick-4-biep-v1`.
