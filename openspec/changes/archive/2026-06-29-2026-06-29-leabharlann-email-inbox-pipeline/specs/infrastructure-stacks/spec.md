# `infrastructure-stacks` capability spec — leabharlann-email-inbox-pipeline delta

The `infrastructure-stacks` capability spec governs the 94
Docker Compose stacks under `infrastructure/stacks/`, the
6-file GOLD_STANDARD pattern, the Locket sidecar contract, and
the Pangolin Traefik routing shape.

This delta adds the `mailcow-dockerized` stack (moved from
`bonneagar/stacks/` to `cianfhoghlaim/stacks/` per the v4
consolidation) with the full 6-file + README GOLD_STANDARD set.

## ADDED Requirements

### Requirement: `mailcow-dockerized` Stack Directory

The system SHALL provide a Docker Compose stack at
`cianfhoghlaim/stacks/mailcow-dockerized/` that runs the
upstream `mailcow/mailcow-dockerized` self-hosted email
server (Postfix + Dovecot + SOGo + Rspamd + ClamAV + the
built-in `dovecot_imapsync_runner` ofelia job) plus a Locket
sidecar for Infisical secret injection.

#### Scenario: 6 GOLD_STANDARD files present

- **WHEN** a developer lists
  `cianfhoghlaim/stacks/mailcow-dockerized/`
- **THEN** the directory SHALL contain all 6 GOLD_STANDARD
  files: `compose.yaml`, `sidecar.yaml`, `secrets.env`,
  `pangolin.yaml`, `blueprint.yaml`, `.env.example`
- **AND** a `README.md` describing the stack

#### Scenario: `pangolin.yaml` 6-label shape

- **WHEN** a developer reads
  `cianfhoghlaim/stacks/mailcow-dockerized/pangolin.yaml`
- **THEN** the file SHALL contain 3 routes:
  `mail.cianfhoghlaim.ie` (port 443, webmail/IMAPS,
  TinyAuth + Member role),
  `imap.cianfhoghlaim.ie` (port 993, internal,
  TinyAuth + SDP-MFA),
  `smtp.cianfhoghlaim.ie` (port 587, internal,
  TinyAuth + SDP-MFA)
- **AND** the internal-only routes SHALL be bound to
  `127.0.0.1` only

#### Scenario: `secrets.env` uses Infisical URI references

- **WHEN** a developer reads
  `cianfhoghlaim/stacks/mailcow-dockerized/secrets.env`
- **THEN** the file SHALL contain 12 `infisical://dev-baile/mailcow/...`
  references: 4 base (db_root, db_pass, hostname, admin_pass)
  + 8 IMAP credentials (4 accounts × {user, app_password})
- **AND** zero plaintext secrets

### Requirement: `mailcow-export` companion container

The system SHALL add a `mailcow-export` companion container to
the `mailcow-dockerized` stack that runs `doveadm export`
every 6 hours via ofelia, writing
`mailbox-<account>-<date>.mbox` to a shared volume.

#### Scenario: Companion container exports MBOX

- **GIVEN** the stack is up and the ofelia scheduler is running
- **WHEN** the 6-hour cron fires
- **THEN** `doveadm export` writes
  `/srv/mailcow-exports/mailbox-dkit_ie-2026-06-29.mbox`
- **AND** the file is readable from the Dagster container's
  `/srv/mailcow-exports/` mount

#### Scenario: Dagster container reads MBOX exports

- **GIVEN** the `mailcow-export` volume is mounted into the
  Dagster container at `/srv/mailcow-exports/`
- **WHEN** the `leabharlann_inbox_raw` Dagster asset
  materialises
- **THEN** it reads every `*.mbox` file in
  `/srv/mailcow-exports/` (recursive, excluding hidden files)

### Requirement: `dovecot_imapsync_runner` configuration

The system SHALL configure the Mailcow
`dovecot_imapsync_runner` ofelia job to poll 4 external
accounts (DKIT.ie Microsoft 365, 2 Gmail, Hotmail) and sync
into Mailcow mailboxes.

#### Scenario: 4 accounts sync into Mailcow

- **GIVEN** the 4 per-account IMAP credentials in Infisical
- **WHEN** the `dovecot_imapsync_runner` cron fires (every
  minute, with no-overlap guard)
- **THEN** the runner polls
  `imap.outlook.com:993` (dkit_ie),
  `imap.gmail.com:993` (gmail_personal),
  `imap.gmail.com:993` (gmail_academic),
  `outlook.office365.com:993` (hotmail_legacy)
- **AND** every new email is fetched into the corresponding
  Mailcow mailbox (`inbox-dkit_ie@cianfhoghlaim.ie` etc.)

## MODIFIED Requirements

*(None — the change only ADDS the `mailcow-dockerized` stack
to the v4 location; the 93 other stacks are unchanged.)*

## REMOVED Requirements

*(None.)*
