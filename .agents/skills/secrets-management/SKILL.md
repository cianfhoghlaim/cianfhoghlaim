---
name: secrets-management
description: Secrets management for the Cianfhoghlaim platform — Infisical + Locket + mise three-way contract. Add/rotate secrets, Locket sidecar pattern, security model (tmpfs, file modes, no-root). Use when adding a new secret, rotating a secret, debugging missing secrets, or wiring a new Locket-enabled stack. **Infisical is the only canonical provider** (1Password migration completed 2026-06; current upstream CLI release is v0.161.9 from 2026-06-26 — verified live 2026-06-29; **docs site no longer publishes conceptual guides — all reference material lives at https://infisical.com/docs/api-reference/endpoints/{provider}/{op}.md discovered via https://infisical.com/docs/llms.txt**). Note: the `Link: …/mcp/server-card.json` header is **stale** as of 2026-06-29 — the referenced JSON endpoint returns 404; do not assume a first-party Infisical MCP server exists. Powers the BIEP secret contract: `infisical://dev-baile/cianfhoghlaim/...` (no `cianfhoghlaim/` prefix).
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
│    infisical://dev-baile/cianfhoghlaim/OPENAI_API_KEY)          │
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
# bonneagar/stacks/<surface>/sidecar.yaml
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
echo 'OPENAI_API_KEY=infisical://dev-baile/cianfhoghlaim/OPENAI_API_KEY' \
  >> .infisical.env

# 3. Re-hydrate locally
mise run secrets:init

# 4. Verify
grep OPENAI_API_KEY .env
# → OPENAI_API_KEY=sk-...

# 5. (Production) Restart Locket
docker compose -f bonneagar/stacks/<surface>/compose.yaml restart locket
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

- `.agents/skills/infrastructure-stacks/SKILL.md` — the 6-file
  GOLD_STANDARD stack pattern (includes `secrets.env` + `sidecar.yaml`)
- `.agents/skills/dagger-pipelines/SKILL.md` — Dagger call for CI parity
- `.agents/skills/komodo/SKILL.md` — Komodo deploys the
  Locket sidecar
- `.agents/skills/pulumi/SKILL.md` — Pulumi provisions the
  Infisical organisation
- Root `AGENTS.md` — the bun + uv + turbo monorepo layout

## Verified 2026-06-29 (Wave 2 Agent 93)

- **CLI latest release: `v0.161.9`** (2026-06-26 17:06 UTC, commit `c25d5ab`, by `adilsitos`). Wave 1's `@infisical/cli@0.41.x` pin is stale (≈120 minor versions behind).
- **OpenAPI Universal Auth login** (v0.161+) accepts `clientId` + `clientSecret` + `organizationSlug` (optional; defaults to identity home org).
- **OpenAPI Universal Auth attach** defaults: `accessTokenTTL = 2592000` (30 d), `accessTokenMaxTTL = 2592000`, `accessTokenNumUsesLimit = 0` (unlimited), `lockoutEnabled = true`, `lockoutThreshold = 3`, `lockoutDurationSeconds = 300`, `lockoutCounterResetSeconds = 30`, `clientSecretTrustedIps = [0.0.0.0/0, ::/0]`, `accessTokenTrustedIps = [0.0.0.0/0, ::/0]`.
- **NEW** infisical CLI command: **`infisical export --format dotenv-eval`** (PR #7035, v0.161.9) — switch `bun run secrets:init` consumers to this when available.
- **NEW** `POST /api/v1/dynamic-secrets/leases/kubernetes` — ephemeral K8s lease per `dynamicSecretName`/`projectSlug`/`environmentSlug`/`namespace`/`ttl`. Pair with `gatewayV2Id` for in-cluster gateways.
- **REMOVED** documentation reference: `infisical SSH` CLI (#7038). Migrate any `SSH` auth flows to `universal-auth` + a dynamic-secret `ssh` type if available.
- **NO** first-party Infisical MCP server as of 2026-06-29 — `Link` header advertises `/docs/.well-known/mcp/server-card.json` but the URL returns 404. Wave 1's ref 8.4 in `agent-18-infisical.md` (MCP integration) should be **deleted** until/unless a server card is published.
- **EU region** is now a 1st-class OpenAPI server: `https://eu.infisical.com`. KCG's `arm1-oci` self-host does not need to migrate; the EU server is for multi-region SaaS customers only.
- **`trustPayload: boolean`** is new on `kubernetes-auth/login.md` — only `true` in strictly trusted environments (bypasses audience claim validation).

## Resources

- Infisical docs index: <https://infisical.com/docs/llms.txt> (machine-readable, 950+ endpoints, single `## Docs` section)
- Infisical canonical doc URL pattern: `https://infisical.com/docs/api-reference/endpoints/{provider}/{op}.md` (verified 2026-06-29)
  - Universal Auth login: <https://infisical.com/docs/api-reference/endpoints/universal-auth/login.md> (now requires `organizationSlug`)
  - Universal Auth attach: <https://infisical.com/docs/api-reference/endpoints/universal-auth/attach.md> (lockout + TTL + IP defaults)
  - Kubernetes auth login: <https://infisical.com/docs/api-reference/endpoints/kubernetes-auth/login.md>
  - K8s dynamic-secret lease: <https://infisical.com/docs/api-reference/endpoints/dynamic-secrets/kubernetes/create-lease.md>
- Infisical releases: <https://github.com/Infisical/infisical/releases> (latest `v0.161.9` 2026-06-26)
- Locket: <https://github.com/cianfhoghlaim/locket> (KCG)
- mise: <https://mise.jdx.dev/>

---

## Hermes + Apple Photos secret contracts (added 2026-06-30)

### Hermes secret contract

The `hermes` stack adds 9 `infisical://dev-baile/hermes/<key>` references:
- `api_server_key` — admin API token
- `openai_api_key` — LITELLM_MASTER_KEY (re-keyed at the Infisical layer)
- `openai_base_url` — http://litellm:4000/v1
- `langfuse_public_key` + `langfuse_secret_key` + `langfuse_base_url`
- `telegram_bot_token` + `discord_bot_token` (separate from openclaw's)
- `operator_pocket_id_subject` — the operator's Pocket ID subject for day-one allowlist population

### Apple Photos secret contract

The `apple_photos` dlt source uses 1 Infisical reference:
- `paperless_consumer_token` — for POSTing document scans to paperless-ngx

GPS coordinates are NOT a secret; they're gated by the
`LEABHARLANN_PHOTOS_INCLUDE_GPS` env var (default `false`).

### OpenClaw + OpenChamber LLM rewire

Both stacks now route LLM through LiteLLM:
- `openai_api_key` = `infisical://dev-baile/<stack>/openai_api_key` (resolves to `LITELLM_MASTER_KEY`)
- `openai_base_url` = `infisical://dev-baile/<stack>/openai_base_url` (resolves to `http://litellm:4000/v1`)

The previous `opencode-go` + `minimax-coding-plan` fallback chain is removed from `openclaw.json`.

## British-Isles Education pipeline (post-v4 secret contract)

The BIEP (`openspec/changes/lc6-biep/`) consumes 12 secrets
under the canonical `infisical://dev-baile/cianfhoghlaim/<key>`
prefix (no `cianfhoghlaim/` segment — the v4 consolidation moved the
project path to `cianfhoghlaim/`):

| Secret | Purpose |
|:--|:--|
| `MOTHERDUCK_TOKEN` | Business-tier PAT for the `md:oideachais` DB |
| `BAML_LLM_API_KEY` | BAML client for `ExtractCurriculumSyllabus` + 4 sibling functions |
| `BGE_M3_MODEL_PATH` | Optional override; defaults to `BAAI/bge-m3` HF cache |
| `LANCEDB_GARAGE_KEY_ID` | S3 access for the 24+1 LanceDB companion tables |
| `LANCEDB_GARAGE_SECRET` | S3 secret for the same |
| `LANCEDB_GARAGE_ENDPOINT` | `https://garage.cianfhoghlaim.ie` |
| `NCCA_SCRAPER_TOKEN` | Optional — DLT source for NCCA PDFs (cached via `stedding/ingest_queue/`) |
| `SEC_PAST_PAPER_TOKEN` | Optional — DLT source for SEC past papers |
| `GOV_IE_SCRAPER_TOKEN` | Optional — DLT source for `gov.ie` circulars |
| `FIRECRAWL_API_KEY` | Fallback scraper for the BAML extraction pipeline |
| `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY` | BIEP trace routing via `baml_client.tracing` |
| `LITELLM_MASTER_KEY` | The unified LLM gateway (proxies BAML + Langfuse) |

**Canonical URI form (post-v4):**

```bash
infisical://dev-baile/cianfhoghlaim/MOTHERDUCK_TOKEN
infisical://dev-baile/cianfhoghlaim/BAML_LLM_API_KEY
infisical://dev-baile/cianfhoghlaim/LANCEDB_GARAGE_KEY_ID
# etc.
```

The pre-v4 form (`infisical://dev-baile/cianfhoghlaim/...`)
**does not resolve** post-v4 — Infisical returns a 404 on the
old prefix because the project was renamed during the v4
consolidation (2026-06-28). If a stack's `.infisical.env` still
references the old prefix, run `bun run scripts/init-vault.ts`
after the rename to migrate the URI references.

**British-Isles Education pipeline use case:**

- **6 LC subjects × 2 languages** — Mathematics, Chemistry,
  Geography, Gaeilge, English, Computer Science, each with
  `en`/`ga` BAML extraction runs under the same
  `BAML_LLM_API_KEY`.
- **`gov.ie` circulars** — `GOV_IE_SCRAPER_TOKEN` powers the
  7th v1 CocoIndex App (`government_circulars`); the
  `FIRECRAWL_API_KEY` is the fallback when the gov.ie HTML
  changes break the BAML extraction.
- **Secret rotation cadence** — `MOTHERDUCK_TOKEN` rotates
  every 90 days; `BAML_LLM_API_KEY` rotates every 30 days;
  `LANCEDB_GARAGE_*` rotates on demand (no fixed cadence).
  All three are managed via the Locket sidecar in
  `bonneagar/stacks/<surface>/sidecar.yaml` (note: the
  `infrastructure/stacks/` prefix is the pre-v4 path).

Cross-references:
- Root `AGENTS.md` — the canonical
  `infisical://dev-baile/cianfhoghlaim/...` contract
- [`.agents/skills/dlt/SKILL.md`](../dlt/SKILL.md) — the DLT
  pipelines that consume `NCCA_SCRAPER_TOKEN` and
  `SEC_PAST_PAPER_TOKEN`
- [`.agents/skills/motherduck/SKILL.md`](../motherduck/SKILL.md) —
  the 4 Dives that consume `MOTHERDUCK_TOKEN`
- [`.agents/skills/lancedb/SKILL.md`](../lancedb/SKILL.md) —
  the 24+1 LanceDB tables that consume `LANCEDB_GARAGE_*`
- [`.agents/skills/baml/SKILL.md`](../baml/SKILL.md) — the 5
  BIEP extraction functions that consume `BAML_LLM_API_KEY`
- [`.agents/skills/change-detection/SKILL.md`](../change-detection/SKILL.md) —
  the sensors that use `GOV_IE_SCRAPER_TOKEN` + `FIRECRAWL_API_KEY`
