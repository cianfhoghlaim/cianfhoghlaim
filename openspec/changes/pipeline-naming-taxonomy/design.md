## Context

Three data-platform trees (`dlt_sources/`, `orchestration/`,
`cocoindex_flows/`) grew independently across recent waves of work,
each accumulating its own naming choices. The 2026-09-02 pipeline
audit catalogued the resulting drift with exact file counts; this
design covers how to sequence fixing it without a single risky
mass-rename commit. See
`openspec/plans/2026-09-02-pipeline-rename-and-refactor-audit-v1.md`
for the full evidence base.

## Goals / Non-Goals

**Goals:**
- Establish the naming law once, in one spec, so every subsequent
  rename task cites the same authority instead of re-deriving
  conventions per-change.
- Sequence execution by risk and leverage.

**Non-Goals:**
- This change does NOT execute the renames — no code, `defs.yaml`,
  or `dlt_sources/` file is touched by this change itself.
  Execution is explicitly deferred to follow-up tasks/changes.
- This change does NOT resolve the `orchestration/defs/` vs
  `pipelines/` end-state itself (fully-merged-into-pipelines vs
  permanent-division).

## Decisions

**Adopt in-flight rename work as the execution vehicle.** Any existing
or future rename change (the `kcg-rename`-style work, the `biiep→bep`
typo fix, the `official_media/` directory split) already specifies the
naming convention implicitly; this change makes that convention
explicit so future renames have one authority to cite.

**Sequence: data-loss bug → in-flight rename resumption → directory
cleanup → BIEP spelling → sibling nesting → pipeline_name normalisation
→ shim expiry → scripts/ triage → test renaming.** This matches the
audit's priority order, chosen by (file-count leverage) × (risk of
doing nothing) rather than alphabetical or chronological order. The
1-line `SOURCE_DIR` bug is silent data loss right now — it goes first
regardless of everything else's batching.

**Nesting threshold is "3 or more flat siblings," not "any sibling
grab-bag."** Two related directories may legitimately stay flat if
they're genuinely distinct enough; the audit found real grab-bags
only once the sibling count reached 3+ per domain. Codifying "3+" as
the threshold gives a concrete trigger instead of relying on repeated
manual re-audits.

## Risks / Trade-offs

- [Risk] Large-blast-radius renames (one that touches hundreds of
  `defs.yaml` files) carry high per-commit risk → Mitigation: execute
  via a script with a dry-run diff review step, not a blind sed
  across hundreds of files.
- [Trade-off] Documenting the `defs/`-vs-`pipelines/` division of
  labour without resolving which end-state is correct means the
  ambiguity persists one layer up (documented-but-undecided rather
  than undocumented) → Accepted: forcing that architectural decision
  inside a naming-taxonomy change would conflate two different-sized
  decisions.

## Open Questions

- Should `orchestration/pipelines/` fully absorb `orchestration/defs/`,
  or should the two trees have a permanent division of labour?