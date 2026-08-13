## ADDED Requirements

### Requirement: Phase 7 of deploy-full.sh runs the memory-stack doctor

The system SHALL extend `scripts/deploy-full.sh` Phase 7
(`data-stacks-up`) to invoke `bun run scripts/lakehouse-memory-doctor.ts`
after the 8 supporting stacks (litellm + langfuse + mlflow + logfire +
cognee + graphiti + lancedb + falkordb) come up. The probe SHALL fail
the phase if any of the 5 memory backends reports a `not_healthy`
status.

#### Scenario: All 5 memory backends return healthy

- **WHEN** `mise run deploy:full --phase=7` runs
- **THEN** the doctor SHALL probe all 5 memory backends
- **AND** the JSON health report SHALL be emitted at `stedding/memory-health/<utc-ts>.json`
- **AND** the phase SHALL exit 0
- **AND** the deploy-state.json checkpoint SHALL record `phase_7_memory_doctor: success`

#### Scenario: One memory backend reports unhealthy

- **WHEN** the doctor reports `falkordb: not_healthy`
- **THEN** the phase SHALL exit non-zero
- **AND** the deploy-state.json checkpoint SHALL record `phase_7_memory_doctor: failed: falkordb_unhealthy`
- **AND** the operator SHALL see the actionable error in the deploy log

#### Scenario: Re-running deploy:full resumes from the failed Phase 7

- **WHEN** `mise run deploy:full` runs after a Phase 7 failure
- **THEN** Phases 1-6 SHALL be skipped (already `success`)
- **AND** Phase 7 SHALL re-run the doctor
- **AND** if the underlying issue has been resolved, the doctor SHALL report `healthy: 5/5` and the checkpoint SHALL be updated