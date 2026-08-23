# Spec Delta: dev-tooling-surfaces

## ADDED Requirements

### Requirement: Stale openspec changes MUST have a documented triage decision

The system SHALL ensure that any pending openspec change that has been at `0/N tasks` for more than 7 days has a documented triage decision (KEEP / CLOSE / SPLIT / TRIAGE) in either:
- The change's own `proposal.md` (a "Triage" section)
- A separate triage change (e.g. `2026-08-22-stale-changes-triage-v1`)

The triage decision MAY be reversed later (a KEEP can become a CLOSE). The decision MUST cite the per-change rationale (e.g. "superseded by archived change X", "real work, in-flight", "oversized, needs split").

Per the 2026-08-22-openspec-audit-and-merge-v1 audit + the 2026-08-22-stale-changes-triage-v1 triage change.

#### Scenario: A change is 0/N tasks for 14 days

- **GIVEN** a pending openspec change has been at `0/N tasks` for 14+ days
- **WHEN** the openspec CI gate runs (or a developer inspects the change list)
- **THEN** the change MUST have a documented triage decision
- **AND** the decision MUST be either KEEP / CLOSE / SPLIT / TRIAGE
- **AND** the rationale MUST cite at least 1 specific reason

#### Scenario: A change is added to the triage change

- **GIVEN** a pending openspec change is added to `2026-08-22-stale-changes-triage-v1/proposal.md` Group B (CLOSE) or Group C (SPLIT) or Group D (TRIAGE)
- **THEN** the triage change is the authoritative source for the decision
- **AND** the original change does NOT need a separate "Triage" section in its own `proposal.md`