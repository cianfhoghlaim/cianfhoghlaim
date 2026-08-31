# Tasks — Extend Educational MMO to 14 Subjects v1

## Phase 1 — Mirror (parallel)

- [x] T1.1: Mirror the standalone `tuatha/` openspec change
  `2026-08-26-tuatha-subject-expansion-to-14-v1` to
  `openspec/changes/from-tuatha/` in the main repo
  (4 files: proposal.md + tasks.md + 2 spec deltas)

## Phase 2 — Author (parallel)

- [x] T2.1: Author `openspec/specs/tuatha-british-isles-mmo/spec.md`
  (mirror of the standalone tuatha's new spec)

## Phase 3 — Modify (parallel)

- [ ] T3.1: MODIFY `openspec/specs/cianfhoghlaim-educational-mmo/spec.md`
  to extend the `8 NCCA Subjects` requirement to
  `14 NCCA + NCCA-adjacent subjects`

## Quality gates

- [ ] G1: `openspec validate 2026-08-26-extend-educational-mmo-to-14-subjects-v1 --strict` PASS
- [ ] G2: `openspec validate --all --strict` 103+ specs PASS (was 101)

## Final

- [ ] Final: `git commit -m "feat(openspec): extend educational-mmo spec to 14 subjects"`
- [ ] Final: `git push origin token-plan-lc-pipeline-2026-08`
- [ ] Final: `openspec archive 2026-08-26-extend-educational-mmo-to-14-subjects-v1 --yes`
