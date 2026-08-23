# 2026-08-23 — Locket shim v0.3 + sidecar pattern (2 new tasks)

## Why

Locket shim v0.2.1 is current (per `a8d9b7b2 fix(infra): complete Locket migration + INFISICAL_URL flip`). The Locket upstream has shipped v0.3 features in beta:

- **Secret rotation tracking** (v0.3.0-beta): the shim now logs each secret fetch to a `locket_audit.scrapes` table for auditability
- **Sidecar health endpoint** (`/healthz`): enables Komodo health checks to verify the sidecar is alive
- **Cross-stack INFISICAL_FALLBACK_FILE** (v0.3.0-beta): allows stacks in the same docker network to share a single secret without re-fetching

The previous Locket migration work handled the v0.2.1 baseline. This change adds the **task surface** for v0.3 features.

## What changes

### 2 new mise tasks in `mise.toml`

| Task | What it does |
|:--|:--|
| `devops:locket:rotate` | Triggers a secret rotation via the Locket API (calls `POST /rotate` on the sidecar) — useful for monthly key rotations |
| `devops:locket:audit` | Queries the `locket_audit.scrapes` table (DuckLake) and emits the last 100 secret fetches per service |

### 1 doc update

`docs/research/infrastructure/locket/locket.md`: add a "Locket v0.3+ new features" section documenting the rotation endpoint + audit table + cross-stack fallback.

## Dependencies

- **Blocked by:** none
- **Soft-blocked by:** the `a8d9b7b2` commit (the v0.2.1 baseline)
- **Affected repos:** cianfhoghlaim only
- **Out of scope:**
  - The actual v0.3 upgrade (deferred; needs careful testing of the rotation endpoint)
  - The `locket_audit.scrapes` table schema (separate change)

## Acceptance criteria

1. Both new tasks exist in `mise.toml`
2. `devops:locket:rotate` calls the Locket rotation endpoint
3. `devops:locket:audit` queries the audit table
4. `docs/research/infrastructure/locket/locket.md` includes the new section
5. `openspec validate 2026-08-23-infra-locket-shim-v0-3-and-sidecar-pattern-v1 --strict` exits 0

## Rollback plan

- Remove the 2 tasks from `mise.toml`
- Revert the doc update
- No code changes; no API changes; no migration