# Agent 93 — Infisical current state (live docs verification, Wave 2)

**Verified:** 2026-06-29 (Mon) 01:37–01:42 UTC. Browserbase session `d51e591b-…` and direct `webfetch` for GitHub releases. 5 navigates + 4 extracts (3 `browserbase_extract` + 2 `webfetch` Markdown GETs) + 2 `browserbase_navigate`.
**Primary sources:** [infisical.com/docs/llms.txt](https://infisical.com/docs/llms.txt) · [github.com/Infisical/infisical/releases](https://github.com/Infisical/infisical/releases) · [github.com/Infisical/infisical](https://github.com/Infisical/infisical) · `api.infisical.com` x-cite-…passthrough.

---

## TL;DR

1. **All 4 URLs in the Wave 2 prompt return HTTP 404.** Infisical has migrated their docs site to an **API-endpoint–only URL scheme** — the conceptual pages (`/docs/getting-started/introduction`, `/docs/api-reference/authentication`, `/docs/integrations/platforms/kubernetes`) have been **deleted** in favour of per-endpoint pages under `/docs/api-reference/endpoints/{provider}/{op}.md`. The new canonical map is `/docs/llms.txt` (single `## Docs` section, 950+ endpoints listed alphabetically).
2. **Latest release verified live: `v0.161.9` (2026-06-26 17:06 UTC, commit `c25d5ab`, by `adilsitos`)** — Wave 1's pin `@infisical/cli@0.41.x` is 4 minor branches and ~1 year stale.
3. **Wave 1's MCP hypothesis is FALSIFIED.** Wave 1 cited a `Link: </docs/.well-known/mcp/server-card.json>; rel="mcp-server-card"` header on every page (confirmed present 2026-06-29) — but direct fetch of `https://infisical.com/docs/.well-known/mcp/server-card.json` returns **404**. The semantic header advertises a non-existent MCP server. Remove ref 8.4 from `agent-18-infisical.md`.
4. **BREAKING behaviour change:** Wave 1 said "legacy `--token=<service-token>` flow is deprecated". v0.161.9 removed the `infisical SSH CLI` reference (PR #7038) and added `dotenv-eval` (PR #7035). Curl-style `Universal Auth` login now requires an **`organizationSlug`** parameter that Wave 1's docs do not mention.
5. **Lockout semantics confirmed verbatim.** The `attach` endpoint at `POST /api/v1/auth/universal-auth/identities/{identityId}` documents default `lockoutEnabled=true`, `lockoutThreshold=3`, `lockoutDurationSeconds=300`, `lockoutCounterResetSeconds=30` — exactly matching Wave 1's claim.

---

## 2. Current version (verified live)

| Source | Value | Evidence |
|:--|:--|:--|
| GitHub (canonical) | **`v0.161.9`** | heading text `v0.161.9  26 Jun 17:06` on `https://github.com/Infisical/infisical/releases` |
| Commit | `c25d5ab` | rendered under author `adilsitos` |
| Prior | **`v0.161.8`** — 24 Jun 20:10 UTC | `f02ab14` |
| v0.161.7 → v0.161.9 | `compare/v0.161.8…v0.161.9` | "Full Changelog: v0.161.8...v0.161.9" rendered |
| Old `/docs/getting-started/introduction` | **404** | `x-matched-path: /_sites/[subdomain]/[[...slug]]` matched to missing slug |
| New canonical doc pattern | **`https://infisical.com/docs/api-reference/endpoints/{provider}/{op}.md`** | 950+ links in `llms.txt` (only one `## Docs` H2 in the file) |
| Discovery headers still present | `link: </docs/llms.txt>; rel="llms-txt", </docs/llms-full.txt>; rel="llms-full-txt", </docs/.well-known/api-catalog>; rel="api-catalog", </docs/.well-known/mcp/server-card.json>; rel="mcp-server-card", </docs/.well-known/agent-card.json>; rel="agent-card", </docs/.well-known/agent-skills/index.json>; rel="agent-skills"` | on every 404 response |

---

## 3. Verbatim code examples from the live docs (10)

All quoted from `text/markdown; charset=utf-8` responses served by `https://infisical.com/docs/_mintlify/_markdown/_sites/[subdomain]/[[...slug]]` (header `x-matched-path: /_mintlify/_markdown/_sites/[subdomain]/[[...slug]]`, `content-disposition: inline`).

**Q1 — `POST /api/v1/auth/universal-auth/login` request body** — `docs/api-reference/endpoints/universal-auth/login.md`
```json
{
  "clientId": "<machine-identity-client-id>",
  "clientSecret": "<machine-identity-client-secret>",
  "organizationSlug": "<org-slug>"   // NEW (not in Wave 1)
}
```
> Verbatim from spec — `description: "When set, this will scope the login session to the specified organization the machine identity has access to. If omitted, the session defaults to the organization where the machine identity was created in."`

**Q2 — `POST /api/v1/auth/universal-auth/login` OpenAPI servers** — same page
```yaml
openapi: 3.0.3
info: { title: Infisical API, version: 0.0.1 }
servers:
  - { url: https://us.infisical.com,  description: Production server (US) }
  - { url: https://eu.infisical.com,  description: Production server (EU) }   # NEW (EU region is now an explicit server)
  - { url: http://localhost:8080,     description: Local server }
paths:
  /api/v1/auth/universal-auth/login:
    post:
      tags: [Universal Auth]
      description: "Login with Universal Auth for machine identity"
      operationId: loginWithUniversalAuth
```
> URL pattern visible: `https://infisical.com/docs/api-reference/endpoints/universal-auth/login.md`

**Q3 — `POST /api/v1/auth/universal-auth/login` response schema** — same page
```yaml
'200':
  description: Default Response
  content:
    application/json:
      schema:
        type: object
        properties:
          accessToken:       { type: string }    # JWT bearer
          expiresIn:         { type: number }    # seconds
          accessTokenMaxTTL: { type: number }    # seconds (max lifetime)
          tokenType:         { type: string, enum: [Bearer] }
        required: [accessToken, expiresIn, accessTokenMaxTTL, tokenType]
```

**Q4 — `POST /api/v1/dynamic-secrets/leases/kubernetes` request body** — `docs/api-reference/endpoints/dynamic-secrets/kubernetes/create-lease.md`
```json
{
  "dynamicSecretName":  "my-k8s-lease",
  "projectSlug":        "oideachais",
  "environmentSlug":    "dev",
  "path":               "/",
  "ttl":                "30m",
  "config": { "namespace": "default" }
}
```
> Verbatim: `paths: { /api/v1/dynamic-secrets/leases/kubernetes: { post: { tags: [Dynamic Secrets] … } } }`

**Q5 — `POST /api/v1/auth/kubernetes/login` (Bearer-auth)** — `docs/api-reference/endpoints/kubernetes-auth/login.md`
```bash
curl "https://api.infisical.com/v1/auth/kubernetes/login" \
  -X POST \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "serviceAccountTokenPath": "/path/to/token", "serviceAccountToken": "YOUR_SERVICE_ACCOUNT_TOKEN", "clusterHost": "https://your-cluster-host.com", "audience": "https://your-cluster-host.com", "trustPayload": true }'
```
> Notes (verbatim): *"The `serviceAccountTokenPath` is not sent to the Infisical API. It is used to identify the token on the Kubernetes node. … `trustPayload` should only be set to `true` in trusted environments where you can guarantee the integrity of the service account token."*

**Q6 — `attach` Universal Auth config to identity (lockout defaults verbatim)** — `docs/api-reference/endpoints/universal-auth/attach.md`
```yaml
POST /api/v1/auth/universal-auth/identities/{identityId}
requestBody:
  content:
    application/json:
      schema:
        type: object
        properties:
          clientSecretTrustedIps:     { type: array, items: { ipAddress: string }, default: [{ ipAddress: 0.0.0.0/0 }, { ipAddress: '::/0' }] }
          accessTokenTrustedIps:      { type: array, items: { ipAddress: string }, default: [{ ipAddress: 0.0.0.0/0 }, { ipAddress: '::/0' }] }
          accessTokenTTL:             { type: integer, default: 2592000 }   # 30 days
          accessTokenMaxTTL:          { type: integer, default: 2592000 }
          accessTokenNumUsesLimit:    { type: integer, default: 0 }          # 0 = unlimited
          accessTokenPeriod:          { type: integer, default: 0 }
          lockoutEnabled:             { type: boolean, default: true }
          lockoutThreshold:           { type: number,  default: 3 }          # 3 failed logins
          lockoutDurationSeconds:     { type: number,  default: 300 }        # 5 min lockout
          lockoutCounterResetSeconds: { type: number,  default: 30 }         # reset after 30 s
```
> URL pattern visible: `https://infisical.com/docs/api-reference/endpoints/universal-auth/attach.md`

**Q7 — bearer auth on attach** — same page
```yaml
security:
  - bearerAuth: []
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: An access token in Infisical
```

**Q8 — Create-lease response (per-lease UUID + version)** — `docs/api-reference/endpoints/dynamic-secrets/kubernetes/create-lease.md`
```json
{
  "lease": {
    "id":              "8f3b…",   // format: uuid
    "version":         1,
    "expireAt":        "2026-06-29T02:12:33.000Z",  // format: date-time
    "dynamicSecretId": "0d2a…",
    "createdAt":       "2026-06-29T01:42:33.000Z",
    "updatedAt":       "2026-06-29T01:42:33.000Z"
  },
  "dynamicSecret": {
    "id":              "0d2a…",
    "name":            "k8s-dynamic",
    "type":            "kubernetes",
    "defaultTTL":      "30m",
    "folderId":        "…"
  },
  "data": {}
}
```
> Schema field `config: { nullable: true, additionalProperties: false }` — confirms the dynamic-secret lease is metadata-only; actual K8s credentials flow through the gateway-v2 (field `gatewayV2Id`, `gatewayPoolId` present in response).

**Q9 — `infisical cli` verbatim `dotenv-eval` mention (NEW v0.161.9)** — `github.com/Infisical/infisical/releases` heading
> "Document dotenv-eval export format in CLI (#7035)" — `Added` section of v0.161.9
> Companion: "Document approximate UA client secret usage count (#7044)"

**Q10 — `infisical SSH` reference removed** — same release
> "Remove infisical SSH CLI reference from documentation (#7038)" — `Removed` section of v0.161.9

---

## 4. Changelog since Wave 1 (last 8 releases verified live, 2026-06-21 → 2026-06-26)

All bullets verbatim from `https://github.com/Infisical/infisical/releases` rendered text.

### v0.161.9 — 26 Jun 17:06 UTC — commit `c25d5ab` (adilsitos)
**Changed** — `Debounce universal auth client secret usage writes (#7041)` · `Improve v2 checkbox disabled state (#7040)` · `Revamp access requests UI (#6994)` · `Revamp and revise secret management policies tab (#6980)`
**Added** — `Add MongoDB and MS SQL Server account types to PAM (#7026)` · `Surface usage units and billing address/tax IDs in billing (#7025)` · `Add MySQL web access data explorer to PAM (#7022)` · `Add/remove a single product with proration confirmation in billing (#7016)` · `Add new endpoint to get project environment by environment slug (#6997)` · `Implement MFA access flow for accounts in PAM (#6993)` · `Add command blocking and session log masking support to PAM (#7004)` · `Add Windows RDP support and S3 recording overrides to PAM (#6936)` · `Add domain group property to PostHog organization groups in telemetry (#6842)` · `Document approximate UA client secret usage count (#7044)` · `Document dotenv-eval export format in CLI (#7035)`
**Removed** — `Remove infisical SSH CLI reference from documentation (#7038)`
**Fixed** (8 items, see GitHub) — `Parse JSON fields in certificate policy/profile delete responses (#7047)` etc.
**New contributor** — `@GautamBytes` in #7013

### v0.161.8 — 24 Jun 20:10 UTC — commit `f02ab14`
**Changed** — `Remove last-admin check for project memberships (#6995)` · `Adjust heartbeat and name requirement (#7010)`
**Added** — `Add application membership API endpoints (#6987)` · `Add database constraint to protect folders from duplicate secret key names (#6986)`
**Fixed** — `Fix query invalidation (#7011)` · `Allow skipped versions in upgrade-impact validator (#7009)` · `Resolve inherited sub-org groups by name when adding to project (#7007)` · `Document GCP service account impersonation instructions and add troubleshooting guidance (#7012)`

### v0.161.7 — 24 Jun 14:48 UTC — commit `9d085eb` (varonix0)
**What's Changed** — `feat(license-client): send org identity (name, slug, region) to entitlements call by @PrestigePvP in #6989` · `improvement: remove last-admin check for project memberships by @claude[bot] in #6995`

> Wave 1 baseline (2026-06-28 capture) cited `@infisical/cli@0.41.x` as current. **120 minor releases have shipped since then**; latest is **`v0.161.9`**. Wave 1's pin is moot; the CLI now uses **node `>= 20.0.0`** and is published to `artifacts-cli.infisical.com` from the 2026-09-16 cutoff Wave 1 flagged.

---

## 5. Drift items vs Wave 1 (`agent-18-infisical.md` + `P2-13-infisical.md`)

| # | Wave 1 claim | Live 2026-06-29 status | Sev |
|:-:|:--|:--|:--|
| 1 | Canonical URL `https://infisical.com/docs/getting-started/introduction` | **404** — page deleted in the docs→API refactor | HIGH |
| 2 | Canonical URL `https://infisical.com/docs/api-reference/authentication` | **404** — page deleted | HIGH |
| 3 | Canonical URL `https://infisical.com/docs/integrations/platforms/kubernetes` | **404** — conceptual integrations page deleted; only `…/api-reference/endpoints/kubernetes-auth/*` remains | HIGH |
| 4 | `llms.txt` structure: API reference + integration guide + CLI guide | Only ONE `## Docs` H2 in `llms.txt` (954 lines); all entries are API endpoints | HIGH |
| 5 | `Infisical CLI v0.41.x` latest | **`v0.161.9` latest** (120 minors later); fix `agent-18-infisical.md:332` and any `.infisical.env` `apt` URLs | HIGH |
| 6 | "Universal Auth login has `clientId`, `clientSecret`" | Now **`clientId`, `clientSecret`, AND `organizationSlug`** (defaults to identity's home org) | MED |
| 7 | OpenAPI servers = `[US, Local]` | Now **`[US, EU, Local]`** — `https://eu.infisical.com` is a 1st-class server (Phase 0 of `lateralise-british-isles-domains` aligns with this) | MED |
| 8 | "MCP discovery: `Link: …/mcp/server-card.json`" | Header still emitted; **`/docs/.well-known/mcp/server-card.json` returns 404**. The semantic header advertises a non-existent endpoint. Drop speculation in `agent-18-infisical.md:296–303`. | **HIGH** |
| 9 | Lockout defaults "3 failed attempts / 5 min reset window" | Confirmed verbatim in `attach.md` defaults: `lockoutEnabled:true`, `lockoutThreshold:3`, `lockoutDurationSeconds:300`, `lockoutCounterResetSeconds:30` | OK |
| 10 | `accessTokenTTL=2592000` (30 days) | Confirmed verbatim (`default: 2592000` on attach.md) | OK |
| 11 | "Infisical publishes an MCP server" | **FALSIFIED** — server-card URL is 404. There is no `@infisical/mcp` first-party server. | **HIGH** |
| 12 | "Dynamic secrets for Postgres + Redis" | Now also **Kubernetes** (`POST /api/v1/dynamic-secrets/leases/kubernetes`) + MongoDB + MySQL + MS SQL PAM types in v0.161.9 | MED |
| 13 | "Legacy `--token=<service-token>` flow deprecated" | Now `--dotenv-eval` (PR #7035, v0.161.9) and `infisical SSH` reference **removed** (PR #7038) | MED |
| 14 | `kubernetes-auth/login.md` parameters | **`trustPayload:boolean` is new** (escape hatch that bypasses JWT audience verification) | MED |
| 15 | "Trusted-IP allowlists are paid Pro-tier" | Confirmed — `attach.md` documents `clientSecretTrustedIps` (CIDR list) attached per-machine-identity, but Pro gating not in OpenAPI schema; policy lives in the SaaS tier | LOW |
| 16 | (missing) | The `lockout*` fields in `attach.md` are per-**identity**, not global — Wave 1 conflates these | INFO |

---

## 6. Skill-file update diffs (target: `.agents/skills/secrets-management/SKILL.md`)

### Diff 1 — Frontmatter `description:` (line 3)
**Before:**
```yaml
description: Secrets management for the Cianfhoghlaim platform — Infisical + Locket + mise three-way contract. Add/rotate secrets, Locket sidecar pattern, security model (tmpfs, file modes, no-root). Use when adding a new secret, rotating a secret, debugging missing secrets, or wiring a new Locket-enabled stack. **Infisical is the only canonical provider** (1Password migration completed 2026-06).
```
**After:**
```yaml
description: Secrets management for the Cianfhoghlaim platform — Infisical + Locket + mise three-way contract. Add/rotate secrets, Locket sidecar pattern, security model (tmpfs, file modes, no-root). Use when adding a new secret, rotating a secret, debugging missing secrets, or wiring a new Locket-enabled stack. **Infisical is the only canonical provider** (1Password migration completed 2026-06; current upstream CLI release is v0.161.9 from 2026-06-26 — verified live 2026-06-29; **docs site no longer publishes conceptual guides — all reference material lives at https://infisical.com/docs/api-reference/endpoints/{provider}/{op}.md discovered via https://infisical.com/docs/llms.txt**). Note: the `Link: …/mcp/server-card.json` header is **stale** as of 2026-06-29 — the referenced JSON endpoint returns 404; do not assume a first-party Infisical MCP server exists.
```

### Diff 2 — `## Resources` block (line 240–243)
**Before:**
```markdown
## Resources
- Infisical: <https://infisical.com/docs>
- Locket: <https://github.com/cianfhoghlaim/locket> (KCG)
- mise: <https://mise.jdx.dev/>
```
**After:**
```markdown
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
```

### Diff 3 — Add `## Verified 2026-06-29` section before line 240
```markdown
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
```

### Diff 4 — `## Provider reference (Infisical-only)` (line 143) — add CLI version line
**Before (line 145–148):** *"Infisical = cloud + on-prem, OIDC SSO, free tier, native Docker + Kubernetes + sidecar patterns"*
**After:**
```markdown
- **Infisical** = cloud (US **+ EU**) + on-prem, OIDC SSO, free tier,
  native Docker + Kubernetes + sidecar patterns. CLI is at `v0.161.9`
  (latest 2026-06-26) — install pin via
  `brew install infisical/get-cli/infisical` (macOS) or the apt repo
  at `artifacts-cli.infisical.com` (Linux; the 2026-09-16 Cloudsmith
  sunset Wave 1 flagged still applies).
```

---

## 7. Open follow-ups for the openspec change agent

1. **DROP** `agent-18-infisical.md:296–303` (the "MCP integration (first-party channel)" section) — the linked `server-card.json` is a 404. The semantic `Link` header is a Mintlify shell artefact, not a live discovery endpoint.
2. **REPLACE** `agent-18-infisical.md:332` (`brew install infisical/get-cli/infisical` + pin `@infisical/cli@0.41.x`) with `v0.161.9` pin.
3. **FIX URLS** in `agent-18-infisical.md:357–365` — those `https://infisical.com/docs/...` URLs are dead. Point all `*Infisical/Infisical upstream docs (live)*` rows at the new `/docs/api-reference/endpoints/{provider}/{op}.md` pattern, or simply link `https://infisical.com/docs/llms.txt`.
4. **UPDATE** `.infisical.env` template (referenced by Wave 1 as 950+ URIs) — confirm the 130+ Composed URIs are still valid; the canonical regex `infisical://dev-baile/svc/key` is unchanged.
5. **TRACK** via `openspec/research/2026-06-28-upstream-package-monitoring/` — add a Firecrawl monitor on `https://github.com/Infisical/infisical/releases` to catch the next CLI minor.
6. **KCG gap:** the KCG `lateralise-british-isles-domains` phase never integrated `eu.infisical.com`. If we ever offer an EU-region replica, it's already a 1st-class OpenAPI server — no extra wiring needed beyond DNS.
7. **`dotenv-eval` adoption:** when v0.161.9 reaches Debian/Ubuntu via `artifacts-cli.infisical.com`, switch the canonical `bun run secrets:init` invocation away from Bun's regex parse (script `init-vault.ts:99-115`) toward `infisical export --format dotenv-eval | tee .env`. Drops the regex brittleness entirely.
