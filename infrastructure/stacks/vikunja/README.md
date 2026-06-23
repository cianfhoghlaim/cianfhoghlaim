# Vikunja — Team Task Management

Kanban + Gantt + list task management at `https://vikunja.cianfhoghlaim.ie`.

Login via PocketID SSO (passkey). Tasks flow in from:
- n8n email triage → auto-creates classified tasks
- cal-diy appointments → Gantt-viewable tasks with start/end
- Paperless documents → categorised + summarised tasks

The n8n seed creates 6 projects on first boot: `_briefings`, `_drafts`, `_reports`, `client-work`, `internal`, `support`.

Backed by PlanetScale "bunchloch" (schema: `vikunja`), fallback to arm1-oci Postgres.
