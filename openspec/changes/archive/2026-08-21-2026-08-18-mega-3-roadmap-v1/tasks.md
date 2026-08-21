# Tasks — Mega-3 Roadmap

This is a narrative-only change that documents the 5-step Mega-3 rollout. No code changes in this step.

## Tasks

### TASK-1.1 — Document the 4-stage plane architecture
- **Status**: done (in `proposal.md`)
- **What**: Document the BAML + CocoIndex + Marimo + ADK parity across the 4 stages (LC + JC + A-Level + GCSE)
- **Reference**: `proposal.md` §"What — The 4-Stage Plane"

### TASK-1.2 — Document the -25,799 LOC dedup target
- **Status**: done (in `proposal.md`)
- **What**: Document the line-by-line dedup forecast across all 5 steps
- **Reference**: `proposal.md` §"Net Combined Forecast"

### TASK-1.3 — Document the spec deltas across 4 changes
- **Status**: done (in `proposal.md`)
- **What**: Document the ~90 ADDED spec requirements across 17 specs
- **Reference**: `proposal.md` §"Spec Deltas"

### TASK-1.4 — Document the dependency graph between the 4 changes
- **Status**: done (in `proposal.md`)
- **What**: Document the 2-4 week overlap between the 4 changes
- **Reference**: `proposal.md` §"Dependencies Between Steps"

### TASK-1.5 — Validate this change against openspec
- **Status**: pending
- **What**: Run `openspec validate 2026-08-18-mega-3-roadmap-v1 --strict` (should pass since there are no spec deltas)
- **Reference**: `openspec/AGENTS.md` §"Workflow"

## Acceptance Criteria

- [ ] This change validates with `openspec validate --strict`
- [ ] The 4 subsequent changes reference this roadmap in their `proposal.md`
- [ ] No code changes are made in this step