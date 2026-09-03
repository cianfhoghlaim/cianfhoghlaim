# Spec delta: `knowledge-sync-loop`

This change adds the 5-layer pull-based sync architecture plus the 3
feedback loops to the cianfhoghlaim knowledge surface. The 10 base
requirements (Layer 1-5 sync + orchestrator + 3 feedback loops) were
already added to the canonical spec at `openspec/specs/knowledge-sync-loop/spec.md`
during the parallel-session commit. This delta adds the one new requirement
that the parallel work did not cover — the operator-egress notification.

## ADDED Requirements

### Requirement: sync:all operator egress notification

The system SHALL emit a single Slack notification (or local desktop
notification when no Slack is configured) after every successful
`mise run sync:all` invocation. The notification SHALL include:
- The total sync duration (seconds)
- The 5 layer pass/fail summary
- A link to the latest `stedding/sync-reports/all-{date}.md` report
- A one-line "all 5 layers healthy" or "N layers failed" verdict

#### Scenario: sync:all succeeds with all 5 layers healthy

- **GIVEN** the operator runs `mise run sync:all`
- **WHEN** all 5 layer scripts exit 0
- **THEN** the system SHALL emit a notification with verdict
  "all 5 layers healthy" + the report link
- **AND** the notification SHALL arrive within 60 seconds of the
  last layer completing

#### Scenario: sync:all fails on 1+ layer

- **GIVEN** the operator runs `mise run sync:all`
- **WHEN** at least 1 layer script exits non-zero
- **THEN** the system SHALL emit a notification with verdict
  "N layers failed (see report)" + the report link
- **AND** the notification SHALL highlight the failed layer names
