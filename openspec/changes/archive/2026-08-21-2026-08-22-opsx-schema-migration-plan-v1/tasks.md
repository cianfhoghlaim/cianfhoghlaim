# Tasks — 2026-08-22 OPSX schema migration plan (docs only)

## Phase 0 — Baseline

- [x] `mkdir -p openspec/changes/.../specs/dev-tooling-surfaces/`
- [x] Write `proposal.md` (the migration strategy)
- [x] Write `tasks.md` (this file — the meta-tasks)
- [ ] Write `specs/dev-tooling-surfaces/spec.md` delta (1 MODIFIED Requirement)
- [ ] `openspec validate ... --strict` → pass

## Phase 1 — Document the migration plan

- [x] Document why OPSX matters (3 benefits)
- [x] Document the 5 candidate pilot changes
- [x] Recommend 3 of them as the migration priority
- [x] Document the migration order
- [x] Document the rollback plan
- [x] Document the risks + mitigations

## Phase 2 — Archive (no implementation)

- [ ] `openspec validate ... --strict` → exits 0
- [ ] `openspec archive ... --yes` → archives the change
- [ ] Verify `openspec validate --all --strict` exits 0 with 146 items
- [ ] Commit + push (user-initiated)

## Out of scope (deferred to follow-up changes)

- **Follow-up change A**: Migrate `2026-08-22-lakehouse-observability-stacks-modernization-v1` (the most recent lakehouse change) to OPSX
- **Follow-up change B**: Migrate `2026-08-21-biiep-hackathon-agentic-educational-system-v1` (the new hackathon change) to OPSX
- **Follow-up change C**: Migrate `2026-08-13-knowledge-graph-population-activation-v1` (a smaller change) to OPSX
- **Follow-up change D**: Adopt OPSX as the default schema for all NEW changes
- **Follow-up change E**: Add the /opsx:* slash commands to `.opencode/commands/`
- **Follow-up change F**: Activate Stores Beta for multi-repo context

These can be sequenced as the user sees fit; this change is just the PLAN.
