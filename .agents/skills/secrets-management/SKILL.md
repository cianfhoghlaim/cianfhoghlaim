---
name: secrets-management
description: Secrets management for the Cianfhoghlaim platform — Infisical + Locket + mise three-way contract. Add/rotate secrets, Locket sidecar pattern, security model (tmpfs, file modes, no-root). Use when adding a new secret, rotating a secret, debugging missing secrets, or wiring a new Locket-enabled stack. **Infisical is the only canonical provider** (1Password migration completed 2026-06).
---

# Secrets Management — Infisical + Locket + mise

## When to use this skill

Use when you need to:

- "Add a new secret (API key, DB password, etc.)"
- "Rotate a secret across all environments"
- "Debug why secrets are missing in a stack"
- "Wire a Locket sidecar for a new stack"
- "Set up a new Infisical project / environment"
- "Migrate from .env to Infisical"

## Overview

The KCG secrets stack has **3 layers**:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Source of truth (Infisical vault)                │
│  → dev-baile environment, /oideachais, /tuatha, /meaisi,   │
│    /croilar projects                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Template (committed to git)                        │
│  → .infisical.env (URI refs only, e.g.                        │
│    infisical://dev-baile/oideachais/OPENAI_API_KEY)          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Runtime (gitignored)                                │
│  → .env (hydrated by mise hook or Locket sidecar)             │
└─────────────────────────────────────────────────────────────┘
```

**Never hand-edit `.env`.** The contract is enforced via
tooling (mise hook + Locket), not discipline.

## The three-way contract

| Layer | Path | Committed? | Editable? |
|:--|:--|:--|:--|
| **Source** | Infisical vault (`dev-baile`) | n/a (remote) | only via Infisical UI / CLI |
| **Template** | `.infisical.env` | YES | YES (URI refs only) |
| **Runtime** | `.env` | NO (gitignored) | NO (auto-hydrated) |

If you need to change a secret:
1. Update the Infisical vault (UI or CLI)
2. Re-run `mise run secrets:init` (or Locket picks it up)
3. Done — `.env` is regenerated, `.infisical.env` is unchanged

If you need to add a NEW secret:
1. Add to Infisical vault
2. Add the URI ref to `.infisical.env`
3. Run `mise run secrets:init` (or restart Locket)

## Two hydration paths

### Path 1: mise hook (developer machines)

```toml
# mise.toml
[hooks]
post-install = "mise run secrets:init"
```

The `mise run secrets:init` task runs `bun run scripts/init-vault.ts`,
which calls `infisical export` to hydrate `.env`.

### Path 2: Locket sidecar (production containers)

```yaml
# infrastructure/stacks/<surface>/sidecar.yaml
services:
  locket:
    image: ghcr.io/cianfhoghlaim/locket:latest
    command: locket --mode=watch
    volumes:
      - secrets:/run/secrets/locket
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9999/health"]

  app:
    depends_on:
      locket: { condition: service_healthy }
    volumes:
      - secrets:/run/secrets/locket
volumes:
  secrets:
    driver: local
    driver_opts:
      type: tmpfs
      device_mode: "0700"
```

The Locket sidecar injects secrets via the tmpfs volume at
`/run/secrets/locket`. The app reads them at boot.

## Locket modes

| Mode | Use case | Persistence |
|:--|:--|:--|
| `exec` | Dev (one-shot) | No |
| `sidecar` | Production (default) | Yes (tmpfs) |
| `watch` | Production (continuous) | Yes (tmpfs, auto-rehydrate on vault change) |
| `park` | Dev (paused) | No |
| `one-shot` | CI (one-time) | No |

## Standard sidecar.yaml template

```yaml
# 6-file GOLD_STANDARD stack with Locket
services:
  locket:
    image: ghcr.io/cianfhoghlaim/locket:latest
    command: locket --mode=watch --project=oideachais
    environment:
      INFISICAL_TOKEN: ${INFISICAL_TOKEN}
    volumes:
      - secrets:/run/secrets/locket
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9999/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  app:
    image: your-app:latest
    depends_on:
      locket: { condition: service_healthy }
    volumes:
      - secrets:/run/secrets/locket
    environment:
      ENV_FILE: /run/secrets/locket/secrets.env
```

## Provider reference (Infisical-only)

**Infisical is the only canonical KCG provider** (as of
2026-06-23, the 1Password + 1Password Connect + Bitwarden
options have been removed; KCG has moved entirely to
Infisical). The rationale:

- **Infisical** = cloud + on-prem, OIDC SSO, free tier,
  native Docker + Kubernetes + sidecar patterns
- 1Password / Bitwarden = no native Locket sidecar
  integration, no Infisical-style URI references, no OIDC
  SSO across the cluster

| Provider | Status | Setup |
|:--|:--|:--|
| **Infisical** (canonical) | ✅ All KCG projects | `bun run scripts/init-vault.ts` |

**Migration history (one-time)**: in June 2026 KCG
migrated from 1Password → Infisical. The
`docs/06-infrastructure/integrating-1password-cli-*.md`
and `where-to-install-1password-cli-op.md` files are
archived; if you find a 1Password reference in any old doc
or stack, treat it as stale and replace with
`infisical://...` URI.

## Security model

| Layer | Protection | Trade-off |
|:--|:--|:--|
| Source (Infisical) | Encrypted at rest, RBAC, audit log | Cloud dependency |
| Template (`.infisical.env`) | URI refs only (no secrets) | None — must be in git |
| Runtime (`.env`) | tmpfs (no disk), file mode 0700 | Single-host only |
| Locket sidecar | tmpfs, no-root, exec-only | Sidecar overhead |

**Threat model**: a compromised dev machine can read all
secrets (Infisical client holds them). A compromised
container can read its own secrets (tmpfs mounted in), but
not other containers' secrets. A compromised CI runner can
read all secrets (no Infisical RBAC by default).

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| `KeyError: 'OPENAI_API_KEY'` | Locket not running | `mise run stack:up <name>` (auto-starts locket) |
| `.env` is empty | Infisical token expired | `mise run secrets:init` (re-auths) |
| `infisical: command not found` | mise toolchain not installed | `mise install` |
| Locket unhealthy in CI | Missing `INFISICAL_TOKEN` secret | Add to GitHub Actions secrets |
| `permission denied` on tmpfs | File mode not 0700 | Fix in sidecar.yaml |

## Adding a new secret (5-step workflow)

```bash
# 1. Add the secret to Infisical
infisical secrets set OPENAI_API_KEY=sk-...

# 2. Add the URI ref to .infisical.env
echo 'OPENAI_API_KEY=infisical://dev-baile/oideachais/OPENAI_API_KEY' \
  >> .infisical.env

# 3. Re-hydrate locally
mise run secrets:init

# 4. Verify
grep OPENAI_API_KEY .env
# → OPENAI_API_KEY=sk-...

# 5. (Production) Restart Locket
docker compose -f infrastructure/stacks/<surface>/compose.yaml restart locket
```

## Rotating a secret

```bash
# 1. Rotate in Infisical (old + new overlap for 24h)
infisical secrets set --rotate OPENAI_API_KEY=sk-new-...

# 2. Wait for Locket to re-hydrate (auto, within 60s)

# 3. Verify the new value is loaded
docker compose exec locket locket dump | grep OPENAI_API_KEY

# 4. Remove the old value
infisical secrets delete OPENAI_API_KEY_OLD
```

## Cross-references

- `.agents/skills/stack-ops/SKILL.md` — the 6-file GOLD_STANDARD
  stack pattern (includes `secrets.env` + `sidecar.yaml`)
- `.agents/skills/dagger/SKILL.md` — Dagger call for CI parity
- `.agents/skills/monorepo/SKILL.md` — bun + uv + turbo
- `.agents/skills/komodo/SKILL.md` — Komodo deploys the
  Locket sidecar
- `.agents/skills/pulumi/SKILL.md` — Pulumi provisions the
  Infisical organisation

## Resources

- Infisical: <https://infisical.com/docs>
- Locket: <https://github.com/cianfhoghlaim/locket> (KCG)
- mise: <https://mise.jdx.dev/
