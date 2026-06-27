# Tasks: Clean up dangling cross-references to deleted `infrastructure/legacy/{ANALYSIS,LOCKET-MODES}.md`

## 1. Validate change

- [ ] 1.1 Run `openspec validate infrastructure-audit-phase-3-clean-up-dangling-legacy-skill-refs --strict`

## 2. Surgically edit 2 skill docs

- [ ] 2.1 Edit `.agents/skills/kcg-pangolin-stack/SKILL.md`: delete line 155 (the dangling cross-ref to `infrastructure/legacy/ANALYSIS.md`)
- [ ] 2.2 Edit `.agents/skills/kcg-locket-sidecar/SKILL.md`: delete line 201 (the dangling cross-ref to `infrastructure/legacy/LOCKET-MODES.md`)

## 3. Verify

- [ ] 3.1 Confirm no active references to `infrastructure/legacy/ANALYSIS.md` or `infrastructure/legacy/LOCKET-MODES.md` remain in the repo (excluding `.git`/`.venv`/`__pycache__` and the archived openspec change)
- [ ] 3.2 Run `mise run lint:skills` (must remain 123/123)
- [ ] 3.3 Confirm `.agents/skills/kcg-pangolin-stack/SKILL.md` line count drops from 155 → 154
- [ ] 3.4 Confirm `.agents/skills/kcg-locket-sidecar/SKILL.md` line count drops from 201 → 200

## 4. Spec delta (extend existing Phase 16 requirement)

- [ ] 4.1 Add 1 NEW scenario to the existing `no-dead-superseded-legacy-docs` requirement in `openspec/specs/indexing-and-cognition/spec.md`: scenario = "No dangling cross-references"

## 5. Commit + push + archive

- [ ] 5.1 `git add` ONLY the 2 skill edits + the new change skeleton (NOT pre-existing in-flight work)
- [ ] 5.2 Commit (refactor)
- [ ] 5.3 Push
- [ ] 5.4 `openspec archive infrastructure-audit-phase-3-clean-up-dangling-legacy-skill-refs --yes`
- [ ] 5.5 Commit (spec delta + archive)
- [ ] 5.6 Push