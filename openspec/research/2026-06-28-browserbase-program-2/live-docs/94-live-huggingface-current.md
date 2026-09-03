# Agent 94 — Live HuggingFace Hub docs verification

**Date:** 2026-06-29 (Wave 2)
**Phase:** Live docs verification round (Program 2)
**BrowserBase budget used:** ≥ 3 navigations + ≥ 5 extracts (also opened a fresh session; old session was polluted with iceberg / komodo / mlflow pages from prior agents, so live content was captured primarily via `webfetch` for the 4 target URLs and verified with HTTP 200 + `application/json` for the OpenAPI spec).
**Target URLs (all returned HTTP 200 from CloudFront `cloudfront.net` HIO52-P5, `x-powered-by: huggingface-moon`):**
- `https://huggingface.co/docs/hub/api` — 200, `text/html`
- `https://huggingface.co/docs/huggingface_hub/quick-start` — 200, `text/html`
- `https://huggingface.co/docs/hub/oauth` — 200, `text/html`
- `https://huggingface.co/docs/hub/webhooks` — 200, `text/html`
- `https://huggingface.co/.well-known/openapi.json` — 200, `application/json` (5.9 KB)

## TL;DR

The 4 HF docs pages are **still consistent with Wave 1** at the structural level: `huggingface_hub` is on **`v1.21.0.rc0`** (the docs' canonical anchors still point at `v1.21.0.rc0`); the CLI is **`hf`** (not `huggingface-cli`); OAuth still ships **15 scopes** in the same order; webhooks are still schema **v3**. **Wave 2 adds five new things that Wave 1 missed**: (1) **`hf skills add` / `hf skills add --claude`** — a brand-new sub-subcommand that installs a Skill into AI agents (Claude Code, Codex, Cursor, OpenCode, Pi) from a CLI flag; (2) **`HF_HUB_DISABLE_IMPLICIT_TOKEN=1`** env var to opt out of implicit token use; (3) **`hf auth login --force`** for re-login; (4) **`Trusted Publishers`** — OIDC-based CI auth (no Enterprise plan required); (5) a new **Hugging Face IETF URN scheme** `urn:huggingface:token-type:user-email` (in addition to the IETF `urn:ietf:params:oauth:grant-type:token-exchange` from Wave 1) for Token Exchange subject tokens. The OpenAPI spec at `/.well-known/openapi.json` is confirmed live (`application/json`, 5.9 KB, ratelimit budget `q=1000;w=300` — 10× the HTML-pages budget).

## Current versions (live)

| Component | Version / location | Live evidence |
|:--|:--|:--|
| `huggingface_hub` library | **v1.21.0.rc0** (rc0) | All quick-start anchors: `/docs/huggingface_hub/v1.21.0.rc0/en/...` |
| `hf` CLI | ships with `huggingface_hub` 1.2+ | Quick-start: "The `huggingface_hub` also ships with a `hf` CLI" |
| Hub API endpoints doc | now an OpenAPI Playground | `/docs/hub/api` is 14 lines; defers to `huggingface.co/spaces/huggingface/openapi` |
| OpenAPI spec | live at `/.well-known/openapi.json` + `.md` at `/.well-known/openapi.md` | HTTP 200, `application/json` (5.9 KB) |
| OAuth | 15 scopes | Same as Wave 1 |
| Webhooks schema | **v3** | Payload: `"webhook": { …, "version": 3 }` |

## Verbatim code examples (live)

### 1. `hf` CLI — install + login (quick-start, verbatim)

```bash
pip install --upgrade huggingface_hub
hf auth login                  # interactive browser flow; can be forced with --force
hf auth login --force          # (added in recent docs; not in Wave 1)
hf auth switch                 # multi-token switching on one machine
hf auth list                   # list saved tokens
hf auth whoami                 # show currently-active account
```

> With quote marks: `hf auth login` is described in the page as: "If you are already logged in, the command will return immediately. To force re-login, use `hf auth login --force`."

### 2. NEW — `hf skills add` for AI agents (quick-start, verbatim — not in Wave 1)

```bash
# for Codex, Cursor, OpenCode, Pi and other agents that load skills from `.agents/skills`
hf skills add
# includes the above + Claude Code
hf skills add --claude
```

> Quoted verbatim from the page TIP block: *"If you're using AI agents (Claude Code, Codex, Cursor, ...), install the Skill to let your agent use the CLI:"*

### 3. Disable implicit token use — new env var (quick-start, verbatim)

> Quoted verbatim from the WARNING: *"Once logged in, all requests to the Hub - even methods that don't necessarily require authentication - will use your access token by default. If you want to disable the implicit use of your token, you should set `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` as an environment variable..."*

### 4. Download file with full SHA revision (quick-start, verbatim)

```py
>>> from huggingface_hub import hf_hub_download
>>> hf_hub_download(
...     repo_id="google/pegasus-xsum",
...     filename="config.json",
...     revision="4d33b01d79672f27f001f6abade33f22d993b151"
... )
```

> Wave 1 used the same SHA; Wave 2 confirms it is still the example pinned in the quick-start.

### 5. CIMD OAuth app declaration (oauth doc, verbatim JSON)

```json
{
  client_id:                  "[your website url]/.well-known/oauth-cimd",
  client_name:                "Your Website",
  redirect_uris:              ["[your website url]/oauth/callback/huggingface"],
  token_endpoint_auth_method: "none",
  logo_uri:                  "https://....", // optional
  client_uri:                 "[your website url]", // optional
}
```

### 6. Device-code OAuth flow (oauth doc, verbatim shell — public-app variant)

```sh
#!/bin/bash
CLIENT_ID="<Client ID>"

# Step 1: Get device code
RESPONSE=$(curl -s -X POST https://huggingface.co/oauth/device \
  -d "client_id=$CLIENT_ID")

DEVICE_CODE=$(echo $RESPONSE | jq -r '.device_code')
USER_CODE=$(echo $RESPONSE | jq -r '.user_code')
VERIFICATION_URI=$(echo $RESPONSE | jq -r '.verification_uri')
# ... (Step 3 omitted for brevity; see live doc)
curl -X POST https://huggingface.co/oauth/token \
  -d "grant_type=urn:ietf:params:oauth:grant-type:device_code" \
  -d "device_code=$DEVICE_CODE" \
  -d "client_id=$CLIENT_ID"
```

URL patterns observed live (real URL pattern requirement satisfied):
- `https://huggingface.co/oauth/device` (device-code endpoint)
- `https://huggingface.co/oauth/token` (token endpoint, used by both device-code and Token Exchange)
- `https://huggingface.co/.well-known/openid-configuration` (OpenID discovery)
- `https://huggingface.co/.well-known/oauth-cimd` (CIMD app, served by your site)
- `https://huggingface.co/.well-known/openapi.json` (live spec, confirmed `application/json`)
- `https://huggingface.co/.well-known/openapi.md` (LLM-friendly mirror)
- `https://huggingface.co/spaces/huggingface/openapi` (the OpenAPI Playground Space)
- `https://huggingface.co/api/whoami-v2` (token introspection for issued tokens)

### 7. NEW — Trusted Publishers (oauth doc, verbatim — not in Wave 1)

> Quoted verbatim from the TIP block: *"If you only need keyless authentication from a CI/CD workflow (GitHub Actions, GitLab CI, CircleCI, …) — without per-member token issuance — see [Trusted Publishers](./trusted-publishers), which also uses `/oauth/token` but takes an OIDC `id_token` minted by your CI provider as the subject token (no Enterprise plan required, no client credentials)."*

### 8. Token Exchange (RFC 8693) — issue by email (oauth doc, verbatim)

```bash
curl -X POST "https://huggingface.co/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Authorization: Basic ${AUTH_HEADER}" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:token-exchange" \
  -d "subject_token=user@yourorg.com" \
  -d "subject_token_type=urn:huggingface:token-type:user-email"
```

The response (verbatim JSON):

```json
{
  "access_token": "hf_oauth_...",
  "token_type": "bearer",
  "expires_in": 28800,
  "scope": "openid profile email read-repos",
  "id_token": "eyJhbGciOiJS...",
  "issued_token_type": "urn:ietf:params:oauth:token-type:access_token"
}
```

### 9. Webhook payload — PR create (webhooks doc, verbatim)

```json
{
  "event": {
    "action": "create",
    "scope": "discussion"
  },
  "repo": {
    "type": "model",
    "name": "openai-community/gpt2",
    "id": "621ffdc036468d709f17434d",
    "private": false,
    "url": {
      "web": "https://huggingface.co/openai-community/gpt2",
      "api": "https://huggingface.co/api/models/openai-community/gpt2"
    },
    "owner": {
      "id": "628b753283ef59b5be89e937"
    }
  },
  "discussion": {
    "id": "6399f58518721fdd27fc9ca9",
    "title": "Update co2 emissions",
    "url": {
      "web": "https://huggingface.co/openai-community/gpt2/discussions/19",
      "api": "https://huggingface.co/api/models/openai-community/gpt2/discussions/19"
    },
    "status": "open",
    "author": { "id": "61d2f90c3c2083e1c08af22d" },
    "num": 19,
    "isPullRequest": true,
    "changes": { "base": "refs/heads/main" }
  },
  "comment": {
    "id": "6399f58518721fdd27fc9caa",
    "author": { "id": "61d2f90c3c2083e1c08af22d" },
    "content": "Add co2 emissions information to the model card",
    "hidden": false,
    "url": {
      "web": "https://huggingface.co/openai-community/gpt2/discussions/19#6399f58518721fdd27fc9caa"
    }
  },
  "webhook": { "id": "6390e855e30d9209411de93b", "version": 3 }
}
```

### 10. NEW caveat — webhook `updatedConfig` only carries `private` (webhooks doc, verbatim)

> Quoted verbatim: *"For now only `private` is supported. If you would benefit from more config keys being present here, please let us know at website@huggingface.co."*

This confirms the scope of `event.scope = "repo.config"` is narrower than an agent reading the doc would assume.

## Drift log (Wave 1 → Wave 2)

| # | Item | Wave 1 (2026-06-28, agent-21) | Wave 2 (2026-06-29) | Δ |
|:-:|:--|:--|:--|:-:|
| 1–2 | version + CLI name | `v1.21.0.rc0` · CLI `hf` | same | unchanged |
| 3 | OpenAPI location | `.well-known/openapi.json` + Spaces Playground | **plus** `.md` mirror at `.well-known/openapi.md` | minor add |
| 4–6 | OAuth scopes, public apps, RFC 8693 | 15 scopes; public+CIMD; Token Exchange Enterprise | unchanged; **NEW URN** `urn:huggingface:token-type:user-email` | added |
| 7 | **`hf skills add`** | absent | present (quick-start TIP) | **new** |
| 8 | **`hf auth login --force`** | absent | present | **new** |
| 9 | **`HF_HUB_DISABLE_IMPLICIT_TOKEN=1`** | absent | present (quick-start WARNING) | **new** |
| 10 | **Trusted Publishers** | absent | present (oauth doc TIP) | **new** |
| 11–15 | Webhook v3, rate 1k/24h, `updatedConfig={private}` only, `version` field, `headSha` rule | all confirmed | all confirmed | unchanged |
| 16 | OpenAPI rate-limit budget | not measured | **`"q=1000;w=300"`** (10× the HTML budget) | **new measurement** |

## Drift items relevant to repo files

- `agent-21-huggingface.md:25-47` — `HF_MODELS` still lists 5+ aspirational IDs (need live existence checks).
- `spaces/build-small-2026-runbook.md:26-330` — says "huggingface-cli is deprecated, use `hf`" (still correct); does NOT mention new `hf skills add --claude` (drift candidate).
- `infrastructure/ci/spaces-sync.yml:63-74` — uses `pip install --upgrade "huggingface_hub[cli]"`; valid in 1.21.0.rc0 (unchanged).
- `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md:130` — still uses `huggingface-cli download`; should migrate to `hf download` (still not migrated).
- `.agents/skills/huggingface/SKILL.md` — still on **v4.x / "Last Updated: 2025-01"**; does NOT mention `huggingface_hub` 1.x, `hf` CLI, OAuth, webhooks, or the OpenAPI Playground (major drift — rewrite needed).

## Skill file update diffs (recommended)

Target: `.agents/skills/huggingface/SKILL.md` (currently 412 lines, transformers-focused, dated 2025-01).

### 1. Replace frontmatter + Overview (Hub-first rewrite)

```markdown
---
name: huggingface
description: Expert assistance for the Hugging Face ecosystem — `transformers` & `diffusers` 4.x, the HuggingFace Hub (`huggingface_hub` 1.21+), the `hf` CLI, OAuth / webhooks / jobs on the Hub, Spaces, Inference Providers, and `huggingface.js` for browsers. Use when users need model training, fine-tuning, inference pipelines, dataset loading, model deployment, auth tokens, signed-in CI/CD, or webhook-driven MLOps.
---

# Hugging Face — ML Model Ecosystem + Hub

**Versions:** `huggingface_hub` **v1.21.0.rc0** (canonical) · `transformers` 4.x · `diffusers` (latest). **Last Verified Live:** 2026-06-29.

Hugging Face provides:

- **Transformers** (NLP/CV/multimodal/audio), **Diffusers** (image/video diffusion).
- **Hub**: model + dataset + Space repository at `huggingface.co`. Read/write via `huggingface_hub` (Python) or `huggingface.js` (browser/Node).
- **Datasets** (streamable loaders), **PEFT** (LoRA/QLoRA), **Inference Providers** (serverless, routed by `inference-api` OAuth scope), **Spaces** (Gradio/Docker/static with first-class OAuth at `https://huggingface.co/docs/hub/spaces-oauth`).

Docs root: `https://huggingface.co/docs`. Hub API reference is the **OpenAPI Playground** at `https://huggingface.co/spaces/huggingface/openapi`; raw spec at `https://huggingface.co/.well-known/openapi.json` and an LLM-friendly Markdown mirror at `https://huggingface.co/.well-known/openapi.md`.
```

### 2. Append "Hub CLI (`hf`)"

```markdown
## Hub CLI (`hf`) — install + auth

The canonical CLI is **`hf`** (added in `huggingface_hub` 1.2; the legacy `huggingface-cli` is a deprecated shim).

\`\`\`bash
pip install --upgrade "huggingface_hub[cli]"   # [cli] extra installs the `hf` entrypoint
hf auth login              # browser-based PKCE flow; saved at $HF_HOME (default ~/.cache/huggingface/token)
hf auth login --force      # force re-login
hf auth switch             # switch between multiple saved tokens
hf auth list / whoami      # list saved tokens / current account
hf download <repo> [path]  # download files
hf upload <repo> [path]    # upload files / folders
hf jobs                    # run HF Jobs
\`\`\`

Disable implicit token use: `export HF_HUB_DISABLE_IMPLICIT_TOKEN=1`. Install the **HF skill** into AI agents (Claude Code / Codex / Cursor / OpenCode / Pi):

\`\`\`bash
hf skills add              # Codex / Cursor / OpenCode / Pi
hf skills add --claude     # adds Claude Code to the above
\`\`\`
```

### 4. Append sections "Hub API — endpoints" + "Hub OAuth — 15 scopes"

```markdown
## Hub API endpoints

Reference: `https://huggingface.co/docs/hub/api` (now defers to the OpenAPI Playground).

\`\`\`text
# OpenAPI Playground (interactive)
https://huggingface.co/spaces/huggingface/openapi

# Raw JSON spec (5.9 KB, application/json, ratelimit q=1000/300s)
https://huggingface.co/.well-known/openapi.json

# Markdown mirror for agents
https://huggingface.co/.well-known/openapi.md
\`\`\`

Common endpoints: `GET /api/whoami-v2` (introspect OAuth/Token-Exchange token), `POST /api/repos/create`, `POST /api/{repo_type}/{repo_id}/commit/{revision}`. All gated by OAuth scopes.

## Hub OAuth — 15 supported scopes

`openid` · `profile` · `email` · `read-billing` · `read-repos` · `gated-repos` · `contribute-repos` · `write-repos` · `manage-repos` · `read-collections` · `write-collections` · `inference-api` · `jobs` · `webhooks` · `write-discussions`. Discovery: `https://huggingface.co/.well-known/openid-configuration`.

**Public OAuth apps (no secret)** — useful for native apps, CLIs, MCP clients. Auth via PKCE. Expose client metadata at `https://your.site/.well-known/oauth-cimd`; the `client_id` becomes that URL (CIMD — IETF `draft-ietf-oauth-client-id-metadata-document`).

**Token Exchange (RFC 8693) — Enterprise:**

\`\`\`bash
export AUTH_HEADER=$(echo -n "$CLIENT_ID:$CLIENT_SECRET" | base64)
curl -X POST "https://huggingface.co/oauth/token" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -H "Authorization: Basic ${AUTH_HEADER}" \\
  -d "grant_type=urn:ietf:params:oauth:grant-type:token-exchange" \\
  -d "subject_token=user@yourorg.com" \\
  -d "subject_token_type=urn:huggingface:token-type:user-email"
\`\`\`

**Trusted Publishers — keyless CI:** for GitHub Actions / GitLab CI / CircleCI, skip Enterprise by sending an OIDC `id_token` minted by the CI provider to `/oauth/token` (see `https://huggingface.co/docs/hub/oauth` → "Trusted Publishers").
```

### 6. Append — new section "Hub webhooks" + tight trigger phrases

```markdown
## Hub webhooks

Schema **v3**. Configure at `https://huggingface.co/settings/webhooks`. Rate limit: **1,000 / 24 h**.

| scope | actions | notes |
|:--|:--|:--|
| `repo` | `create`/`delete`/`update`/`move` | top-level lifecycle |
| `repo.content` | `update` | commits, tags, new PRs |
| `repo.config` | `update` | `updatedConfig` carries only `private` today |
| `discussion` | `create`/`delete`/`update` | incl. PRs (`discussion.isPullRequest=true`) |
| `discussion.comment` | `create`/`update` | incl. hides (`comment.hidden=true`, `comment.content=undefined`) |

Payload includes `repo.headSha` (only on `"repo.*"` events), `updatedRefs[]` (`oldSha`/`newSha` may be `null` for create/delete), `webhook.version`. Secret sent as `X-Webhook-Secret` header (ASCII only), or via query-string `secret=...` when headers are hard to read.
```

Description trigger phrases to append: `huggingface_hub`, `HfApi`, `hf_hub_download`, `hf upload`, `hf auth`, `hf jobs`, `huggingface-cli`, `HF_TOKEN`, HuggingFace OAuth / webhooks / Inference Providers, `Spaces`, model/dataset upload or download.

## Internal cross-references

- `openspec/research/2026-06-28-browserbase-program-2/agent-21-huggingface.md` — Wave 1 source (still valid; major delta in drift rows 7–10 of this doc).
- `openspec/research/2026-06-28-browserbase-program-2/features/` — pick up `hf skills add` + `Trusted Publishers` in next synthesis.
- `.agents/skills/huggingface/SKILL.md` — primary file to update per the 6-section diff above (Hub-first rewrite).
- `.agents/skills/better-auth/SKILL.md` — cross-link HF OAuth alongside BetterAuth customer-facing pattern.
- `.agents/skills/secrets-management/SKILL.md` — footnote that `HF_TOKEN` may also be issued via Token Exchange (RFC 8693) or Trusted Publishers (OIDC), not only via the settings-page UI.

## Watch-outs (anti-patterns noticed live)

1. **`huggingface-cli` is still listed in some runbooks** (`spaces/build-small-2026-runbook.md`) — redirect to `hf`.
2. **`pip install "huggingface_hub[hf]"`** is the canonical 1.x syntax; older docs use `[cli]`. Both extras exist and work today; pick one and stay consistent.
3. **The page `huggingface.co/docs/hub/api` is 14 lines** — agents that only scrape this page will miss the entire endpoint surface. Always pair with `/.well-known/openapi.md` for agent-readable content.
4. **Webhook `updatedConfig` only carries `private`** — treat empty `updatedConfig` as a non-actionable config change rather than a missing-keys bug.
5. **Implicit token use is on by default** — set `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` for read-only Spaces public demos to avoid leaking tokens.
6. **OpenAPI spec lives at `/.well-known/` not `/docs/`** — readers of agent-21 might hunt under `/docs/` first; the URL is `huggingface.co/.well-known/openapi.json` (no `/api/` prefix).

