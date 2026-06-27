# Tasks: Delete superseded `infrastructure/legacy/{ANALYSIS,LOCKET-MODES}.md`

## 1. Validate change

- [ ] 1.1 Run `openspec validate infrastructure-audit-phase-2-delete-superseded-legacy-docs --strict`

## 2. Delete superseded docs

- [ ] 2.1 `git rm infrastructure/legacy/ANALYSIS.md`
- [ ] 2.2 `git rm infrastructure/legacy/LOCKET-MODES.md`

## 3. Verify

- [ ] 3.1 Confirm `infrastructure/legacy/README.md` is unchanged (the archive index)
- [ ] 3.2 Confirm `infrastructure/legacy/` now contains only `README.md`
- [ ] 3.3 Run `mise run lint:skills` (must remain 123/123)

## 4. Spec delta + audit trail

- [ ] 4.1 Add 1 ADDED Requirement to `openspec/specs/indexing-and-cognition/spec.md`: no-dead-superseded-legacy-docs

## 5. Follow-up (NOT in this commit)

- [ ] 5.1 **User follow-up**: clean up the 2 dangling cross-references in skill docs:
  - `.agents/skills/kcg-pangolin-stack/SKILL.md:155` (refers to ANALYSIS.md)
  - `.agents/skills/kcg-locket-sidecar/SKILL.md:201` (refers to LOCKET-MODES.md)
  - These are pre-existing in-flight work per the user's exclusion list (`.agents/skills/*.md`). Out of Phase 16 scope.

## 6. Commit + push + archive

- [ ] 6.1 `git add` only the 2 deletions + the new change skeleton (NOT the skill docs)
- [ ] 6.2 Commit (refactor)
- [ ] 6.3 Push
- [ ] 6.4 `openspec archive infrastructure-audit-phase-2-delete-superseded-legacy-docs --yes`
- [ ] 6.5 Commit (spec delta + archive)
- [ ] 6.6 Push