# Tasks for kcg-monorepo-readme-expansion

## 1. Root README + 6 quadrant READMEs

- [x] 1.1 `README.md` — add the 6 sections + the 8-phase
  end-to-end deploy playbook (preserves the 655 lines)
- [x] 1.2 `infrastructure/README.md` — add the 6 sections
  (preserves the 386 lines)
- [x] 1.3 `sruth/oideachais/README.md` — add the 6 sections
  (preserves the 674 lines)
- [x] 1.4 `sruth/meaisinfhoghlaim/README.md` — add the 6 sections
  (preserves the 525 lines)
- [x] 1.5 `sruth/tuatha/README.md` — add the 6 sections
  (preserves the 834 lines)
- [x] 1.6 `sruth/croilar/README.md` — add the 6 sections
  (preserves the 819 lines)
- [x] 1.7 `spaces/README.md` — add the 6 sections
  (preserves the 157 lines)

## 2. Standalone DEPLOY.md

- [x] 2.1 Create `DEPLOY.md` — the standalone end-to-end
  deploy playbook (~800 lines, the canonical rollback
  procedure)

## 3. Spec delta

- [x] 3.1 MODIFIED Requirement "Canonical Directory Layout"
  (the 6-section README pattern + the standalone DEPLOY.md)
- [x] 3.2 ADDED Requirement "End-to-end deploy playbook"
  (the 8-phase playbook + the 9th phase rollback)

## 4. Validation + commit + push + archive

- [ ] 4.1 Run `openspec validate kcg-monorepo-readme-expansion --strict`
- [ ] 4.2 Run `mise run lint:skills` (no new skills; just
  verify the existing 123 still pass)
- [ ] 4.3 Commit + push (single Round 13 commit per the
  user's instruction)
- [ ] 4.4 Run `openspec archive kcg-monorepo-readme-expansion --yes`
