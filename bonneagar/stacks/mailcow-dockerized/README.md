# Mailcow — Self-Hosted Email Server

## Overview

Mailcow is an open-source, Docker-based email server suite providing a complete self-hosted email infrastructure. It includes Postfix (SMTP), Dovecot (IMAP), SOGo (webmail/groupware), Rspamd (spam filtering), ClamAV (antivirus), and more — all managed through a single administrative web UI.

## Why This Matters for Kings' College Galway

Operating under the `cianfhoghlaim.ie` domain means email infrastructure is needed for team communication, automated notifications (Dagster pipeline failures, Langfuse alerts, model conversion completion), and official correspondence with educational institutions. Mailcow provides a fully self-hosted email stack, eliminating dependency on Google Workspace, Microsoft 365, or any third-party email provider. The SOGo groupware provides shared calendars and contacts for team coordination, and Rspamd + ClamAV provide enterprise-grade spam and malware filtering without sending email through cloud services.

## Key Features

- **Complete email stack** — SMTP, IMAP, webmail, calendar, contacts
- **SOGo groupware** — Shared calendars, address books, and task lists
- **Spam + antivirus** — Rspamd + ClamAV integrated filtering
- **Admin UI** — Web-based management for domains, mailboxes, aliases
- **Docker-native** — Entire stack in Docker Compose

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/mailcow-dockerized
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. Requires DNS configuration (MX, SPF, DKIM, DMARC records) for the `cianfhoghlaim.ie` domain.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `MAILCOW_HOSTNAME` | Yes | Mail server hostname | `mail.cianfhoghlaim.ie` |
| `MAILCOW_TZ` | No | Timezone | `Europe/Dublin` |
| `MAILCOW_DB_PASSWORD` | Yes | Database password | — |
| `MAILCOW_PASS` | Yes | Admin panel password | — |

## Access

- **Webmail (SOGo)**: `https://mail.cianfhoghlaim.ie/SOGo`
- **Admin Panel**: `https://mail.cianfhoghlaim.ie/admin`
- **SMTP**: Port 587 (submission), Port 25 (MTA)
- **IMAP**: Port 993 (SSL)
- **Auth**: Email/password per mailbox + Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/mailcow/mailcow-dockerized>
- **Documentation**: <https://docs.mailcow.email>
- **Latest**: Active development — SOGo updates, Rspamd improvements, Postfix 3.9, Dovecot upgrades

## Screenshot

Mailcow's admin UI shows a dashboard with domain statistics (mailbox count, disk usage, queue status), a mailbox management interface (add/edit/delete mailboxes, set quotas, configure aliases), and system status panels for each component (Postfix, Dovecot, SOGo, Rspamd, ClamAV). The SOGo webmail interface provides a full groupware experience with email, calendar, contacts, and tasks.
