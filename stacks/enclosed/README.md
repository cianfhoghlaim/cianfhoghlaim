# Enclosed — Private, Encrypted Note Sharing

## Overview

Enclosed is a minimalist, open-source web application for creating encrypted, self-destructing notes. Notes are encrypted client-side before being stored on the server, and can be configured to expire after a set time or after being read. Built by Corentin (the same developer behind IT Tools).

## Why This Matters for Kings' College Galway

Sharing API keys, test credentials, configuration snippets, and temporary access tokens between team members requires a secure channel that isn't email or Slack. Enclosed provides one-time, encrypted note sharing — paste a secret, get a URL, share the URL, and the note self-destructs after reading. Client-side encryption means even the server cannot read the note contents. For a project that manages dozens of API keys and service credentials, this provides a zero-trust way to share sensitive information without it persisting in chat logs or email archives.

## Key Features

- **Client-side encryption** — Notes encrypted before leaving the browser
- **Self-destructing** — Notes expire after reading or after a time limit
- **No accounts** — No registration or login required
- **Minimalist** — Single-purpose tool with zero configuration
- **Open-source** — Self-hosted; no data sent to third parties

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/enclosed
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. No database or secrets required — data is stored in a local volume.

## Environment Variables

None required. Enclosed runs as a self-contained service storing encrypted notes in a local Docker volume.

## Access

- **Web UI**: `https://enclosed.cianfhoghlaim.ie` (private, Member role)
- **API**: `http://localhost:8787`
- **Auth**: None (anonymous note creation)

## Upstream

- **Repository**: <https://github.com/CorentinTh/enclosed>
- **Latest**: Active development — encryption improvements, expiry configuration, API support

## Screenshot

Enclosed's web UI is deliberately minimal: a single text area for entering a note, options for expiry (after reading, after 1 hour, after 1 day, after 1 week), and a "Create note" button. The note view shows the decrypted content with a warning that it will be deleted after reading.
