# Presenton — Self-Hosted Presentation Sharing

## Overview

Presenton is an open-source, self-hosted platform for creating, storing, and sharing presentations. It supports markdown-based slide creation with live preview, PDF export, and a clean presentation viewer. Designed as an alternative to Google Slides or SlideShare for teams that want to keep their presentation content private.

## Why This Matters for Kings' College Galway

The project produces a significant volume of presentation content: research presentations on curriculum extraction methodology, educational workshop slides for teacher training, project architecture overviews for collaborators, and student-facing study guides. Presenton provides a central repository for all presentations with version control, markdown-based authoring (the same format as the rest of the project's documentation), and private sharing through Pangolin. This keeps presentation content within the infrastructure rather than scattered across Google Drive, OneDrive, and SlideShare.

## Key Features

- **Markdown slides** — Write presentations in markdown with live preview
- **PDF export** — Export presentations for offline sharing
- **Private sharing** — Share links within the Pangolin private network
- **Version history** — Track changes to presentations over time
- **Clean viewer** — Presentation mode with slide navigation

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/tools/presenton
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `PRESENTON_PORT` | No | Web UI port | `3000` |
| `DATABASE_URL` | Yes | Database connection string | — |

## Access

- **Web UI**: `https://presenton.cianfhoghlaim.ie` (private, Member role)
- **Auth**: Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/presenton/presenton>
- **Latest**: Active development — markdown editor improvements, PDF export, sharing controls, theme support

## Screenshot

Presenton's web UI shows a split-pane editor: markdown on the left, rendered slide preview on the right. The presentation viewer shows a full-screen slide carousel with keyboard navigation. The dashboard lists all presentations with thumbnails, last-modified dates, and sharing status.
