# Change: 2026-10-30-openspec-backlog-triage-v1

> **Status (added 2026-10-30, per Umbrella 4 of the platform-reset saga):**
> This change is **KEEP** in the backlog triage. This is the triage
> umbrella itself — it documents the classification of the 57
> zero-progress changes (5 KEEP, 24 ARCHIVE-AS-RESEARCH, 28
> ARCHIVE-AS-OUTDATED), executes the 52 archive moves, writes 1-paragraph
> "what this is for" stubs in the 5 KEEP changes' `proposal.md`,
> fixes the `openspec/project.md` STALE PATHS WARNING, registers the
> new `media-intel-and-curriculum-hydration` spec, and runs the skill
> conformance check. The 5 KEEP changes are: lakehouse-bridge-bring-up
> (Umbrella 3), spacetimedb-babylonjs-adr-clean-break, cocoindex-retro-gameplay,
> adk-asset-generation-pillar3, and this change (meta).

## Why

The repo has 126 active openspec changes (~80 with 0% progress, per the
live `openspec list --changes` count). The Stage 8 fresh-slate handoff
(`openspec/plans/2026-10-26-stage-8-fresh-slate-spec-handoff-v1.md`)
Gap 2 documents this as the 79-stalled-change backlog. Of those 80,
the handoff estimates: 30 are genuinely needed, 20 are research
artifacts that should be archived, 29 are outdated superfluous work
that should be archived, 1 should be merged into another change.

This umbrella is the triage itself: classify all 80, write 1-paragraph
"what this is for" stubs in each KEEP change's `proposal.md`,
`openspec archive <change> --yes` the ARCHIVE moves, fix the
`openspec/project.md` STALE PATHS WARNING, register the new
`media-intel-and-curriculum-hydration` spec, and run the skill
conformance check.

This is Umbrella 4 of 4 in
`openspec/plans/2026-10-30-platform-reset-saga-v1.md`.
