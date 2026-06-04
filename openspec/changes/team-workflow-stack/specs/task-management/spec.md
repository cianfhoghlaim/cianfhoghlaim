# `task-management` capability spec (NEW)

Self-hosted team task management built on Vikunja. Combines kanban boards, Gantt charts, hierarchical task lists, and team sharing. Workflows from `workflow-automation` (n8n) write into Vikunja via REST; cal-diy booking events land in Vikunja as time-bound tasks that surface on the Gantt view.

## ADDED Requirements

### Requirement: Vikunja Deployment
The system SHALL deploy Vikunja as a private Pangolin resource with team kanban, Gantt, and list views enabled.

#### Scenario: First-boot seeding
- **WHEN** the vikunja stack is deployed for the first time and the `vikunja-seed` one-shot container runs
- **THEN** the `team` group is created (idempotent), the `team-lead` admin user is created, and 6 starter projects are seeded: `_briefings`, `_drafts`, `_reports`, `client-work`, `internal`, `support`

#### Scenario: Multiple views per project
- **WHEN** a team member opens any seeded project in the Vikunja UI
- **THEN** the project SHALL be viewable as a kanban board, a list, and a Gantt chart

#### Scenario: Team sharing
- **WHEN** the `team` group is granted Write access to the `client-work`, `internal`, and `support` projects
- **THEN** every member of the `team` group SHALL have read+write access without per-user setup

### Requirement: Gantt Chart Integration
The system SHALL populate the Gantt chart automatically from inbound cal-diy booking events.

#### Scenario: cal-diy booking creates Gantt-visible task
- **WHEN** a cal-diy `booking.created` webhook fires for a new appointment and the n8n `team-booking-to-vikunja` workflow runs
- **THEN** a new Vikunja task SHALL be created with `start_date` and `end_date` set to the meeting time, and the task SHALL appear on the team's Gantt chart

### Requirement: n8n-driven task creation
The system SHALL allow n8n workflows to create Vikunja tasks with team-level assignment.

#### Scenario: Email triage task assignment
- **WHEN** the `team-email-triage` workflow categorises an inbound message and creates a new Vikunja task
- **THEN** the task's `assignees` field SHALL include the `team` group, allowing any team member to claim

### Requirement: Backup
The system SHALL back up the Vikunja Postgres database nightly to Garage S3.

#### Scenario: Nightly backup
- **WHEN** the `team-backup.toml` Komodo procedure runs at 02:00
- **THEN** `pg_dump` of the Vikunja database SHALL be compressed and uploaded to `s3://team-backups/vikunja/vikunja-<timestamp>.sql.gz`

### Requirement: Private Routing
The system SHALL route Vikunja only through the Pangolin private resource pattern.

#### Scenario: No public exposure
- **WHEN** an unauthenticated client attempts to reach `vikunja.cianfhoghlaim.ie` over the public internet
- **THEN** the request SHALL be rejected at Traefik (no DNS, no TLS for the public hostname)
- **AND WHEN** an authenticated team member connects via the Olm VPN client
- **THEN** the request SHALL succeed
