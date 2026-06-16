# `scheduling` capability spec (NEW)

Self-hosted team scheduling built on cal-diy (cal.com community build). Provides both a shared team booking page and per-member booking pages. Every booking event fires a webhook that the `workflow-automation` subsystem (n8n) consumes to populate the team's task management system (Vikunja) and the Gantt chart.

## ADDED Requirements

### Requirement: cal-diy Deployment
The system SHALL deploy cal-diy as a private Pangolin resource built from the local source checkout at `stedding/repos/cal.diy/`.

#### Scenario: Image built from source
- **WHEN** the cal-diy stack deploys and Docker builds the `calcom-web` service
- **THEN** the build context SHALL be `stedding/repos/cal.diy/` and the image SHALL be tagged `ghcr.io/cianfhoghlaim/cal-diy:local`

#### Scenario: License consent
- **WHEN** the image builds
- **THEN** `NEXT_PUBLIC_LICENSE_CONSENT=agree` SHALL be passed as a build argument
- **AND** `CALCOM_TELEMETRY_DISABLED=1` SHALL be set to disable telemetry

### Requirement: Shared Team Booking Page
The system SHALL expose a single team-level booking page in addition to per-member pages.

#### Scenario: Team booking page
- **WHEN** the `team` organisation is enabled (`ORGANIZATIONS_ENABLED=true`, `NEXT_PUBLIC_SINGLE_ORG_SLUG=team`) and a visitor navigates to `calcom.cianfhoghlaim.ie/team`
- **THEN** the shared team booking page SHALL render with the team's collective availability

#### Scenario: Per-member booking pages
- **WHEN** a visitor navigates to `calcom.cianfhoghlaim.ie/<member-slug>`
- **THEN** that specific member's individual booking page SHALL render with their personal availability

### Requirement: Outbound Webhook to n8n
The system SHALL fire a signed webhook on every booking event.

#### Scenario: booking.created webhook
- **WHEN** a visitor completes a booking and cal-diy records the event
- **THEN** an HMAC-signed POST SHALL be sent to `https://n8n.cianfhoghlaim.ie/webhook/team-booking-to-vikunja` with the full booking payload
- **AND** the signature SHALL be verified using `CALCOM_WEBHOOK_SECRET` from Infisical

#### Scenario: booking.rescheduled webhook
- **WHEN** an existing booking is rescheduled
- **THEN** a `booking.rescheduled` webhook SHALL fire with the updated `startTime` and `endTime`
- **AND** the n8n `team-booking-to-vikunja` workflow SHALL update the existing Vikunja task's start/end dates

#### Scenario: booking.cancelled webhook
- **WHEN** an existing booking is cancelled
- **THEN** a `booking.cancelled` webhook SHALL fire
- **AND** the n8n `team-booking-to-vikunja` workflow SHALL mark the corresponding Vikunja task as done

### Requirement: Cron Maintenance
The system SHALL enable cal-diy's built-in cron jobs via `CRON_API_KEY` + `CRON_ENABLE=true`.

#### Scenario: Cron scheduling
- **WHEN** the stack deploys with `CRON_API_KEY` from Infisical and cal-diy's internal scheduler runs
- **THEN** the cron endpoint SHALL authenticate via `Authorization: Bearer ${CRON_API_KEY}` and execute scheduled tasks (event reminders, calendar sync, etc.)

### Requirement: Backup
The system SHALL back up the cal-diy Postgres database nightly to Garage S3.

#### Scenario: Nightly backup
- **WHEN** the `team-backup.toml` Komodo procedure runs at 02:00
- **THEN** `pg_dump` of the cal-diy database SHALL be compressed and uploaded to `s3://team-backups/calcom/calcom-<timestamp>.sql.gz`

### Requirement: Private Routing
The system SHALL route cal-diy only through the Pangolin private resource pattern.

#### Scenario: No public exposure
- **WHEN** an unauthenticated client attempts to reach `calcom.cianfhoghlaim.ie` over the public internet
- **THEN** the request SHALL be rejected at Traefik
- **AND WHEN** an authenticated team member connects via the Olm VPN client
- **THEN** the request SHALL succeed
