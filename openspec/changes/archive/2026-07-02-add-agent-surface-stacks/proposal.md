# Change: 2026-07-02-add-agent-surface-stacks

## Why

The `agent-platform-cluster` spec describes the canonical
3-vertex agent-platform group on `bunchloch`:

- **hermes** (NousResearch/hermes-agent v0.17.0, MIT) — the
  autonomous long-running agent runtime as the **3rd vertex**
- **openclaw** — the channel-fanout gateway (8 channels:
  Telegram + Slack + Discord + WhatsApp + WebChat + MS Teams
  + Signal/iMessage/Matrix scaffolded but disabled)
- **openchamber** — the OpenCode web/desktop UI (Bun + React,
  18+ themes, bundled opencode-ai runtime)

The 3 stacks already exist at `bonneagar/stacks/{hermes,
openclaw,openchamber}/` and are fully GOLD_STANDARD-compliant
(all 6 files + extras like `init-allowlist.sh`,
`skills-curated/`, `pangolin.yaml`). Each routes its LLM
traffic through the **canonical `litellm` gateway** at
`http://litellm:4000/v1` (per the M3 chokepoint design
described in the `2026-06-30-agent-platform-cluster-hermes-cocoindex`
proposal §1).

Change 1 (19-stack bootstrap) + Change 2 (lancedb + logfire
+ 5 image pins) + Change 3 (marimo) brought up the
data + observability + dashboard layers. This change ships
the **3 agent UI surfaces** as the final Wave 4.

## What changes

### 3 compose.yaml edits (image pin + placeholder-digest removal)

The 3 compose files all referenced images with a
**placeholder SHA256 digest**
(`@sha256:0000000000000000000000000000000000000000000000000000000000000000`)
that would fail `docker compose pull`. The semver tags
themselves are also problematic for 2 of the 3 stacks:

| Stack | Old | New | Notes |
|:--|:--|:--|:--|
| `hermes` | `ghcr.io/nousresearch/hermes-agent:0.17.0@sha256:0000...` | `ghcr.io/nousresearch/hermes-agent:0.17.0` | Semver `0.17.0` per `agent-platform-cluster` spec; placeholder digest removed (would fail pull); upstream image is **private** (401 on GHCR HEAD) — requires `docker login ghcr.io` with NousResearch credentials |
| `openclaw` | `ghcr.io/openclaw/openclaw:1.0.0@sha256:0000...` | `ghcr.io/openclaw/openclaw:2026.2.6` | **Tag was wrong** — `1.0.0` does NOT exist on GHCR; upstream uses date-based tags; latest verified is `2026.2.6` (200 on GHCR HEAD); placeholder digest removed |
| `openchamber` | `ghcr.io/openchamber/openchamber:1.0.0@sha256:0000...` | `ghcr.io/openchamber/openchamber:1.0.0` | Semver `1.0.0` kept (per compose header); placeholder digest removed; upstream image is **private** (401 on GHCR HEAD) — requires `docker login ghcr.io` with openchamber credentials |

The 3 image edits are **independent of container lifecycle**
— they take effect on the next `docker compose pull` (which
happens automatically on `up -d` if the image is not
locally cached).

### 5 new openspec change files

The change adds:
- **1 ADDED Requirement** to `infrastructure-stacks` (the
  Wave 4 bring-up + image pinning)
- **1 new capability spec** `agent-platform-cluster` (the
  3-vertex bundle + litellm chokepoint + 3-layer auth) with
  **3 ADDED Requirements** and 8 Scenarios
- **1 ADDED Requirement** to `agentic-frontend-frameworks`
  (the 3 agent surfaces wired into the canonical web/UI
  framework)

## Impact

- **Affected specs:** `agent-platform-cluster` (new),
  `infrastructure-stacks` (shared),
  `agentic-frontend-frameworks` (shared)
- **Affected code:** 3 `compose.yaml` files (image line
  edits) + 5 new openspec change files
- **Affected hosts:** `bunchloch` only (the workload host);
  the 3 stacks are workload-tier per the 3-tier host
  convergence model in `infrastructure-stacks` §"Three-Tier
  Host Convergence"
- **Risk:** medium-high
  - **Image access:** `hermes` + `openchamber` are private
    at GHCR; without proper credentials, `docker compose
    pull` will fail with 401. The operator must add the
    NousResearch + openchamber PATs to `~/.docker/config.json`
    before Wave 4 bring-up.
  - **Network dependency:** all 3 stacks join the
    `cianfhoghlaim` external network and require the
    `litellm` service on `:4000` to be reachable. Wave 2's
    `litellm` bring-up (Change 1) is a hard prerequisite.
  - **Pangolin:** each stack has a `pangolin.yaml` that
    declares public-private resource routes. If Pangolin
    is not running on `arm1-oci`, the WebChat / Telegram
    / etc. ingress flows are degraded but the agent runtimes
    still start locally.
- **Audit gates:** `bun run validate-stacks` + `mise run
  lint:skills` + `openspec validate --strict`

## Non-goals

- **Not pinning the 3 images to full SHA256 digests.** The
  semver tag satisfies the `infrastructure-stacks` §"Image
  Pinning Policy" requirement (no `:latest`); full digest
  pinning is a renovate-cycle follow-up. Once Renovate is
  configured to run on `bonneagar/stacks/`, the
  `@sha256:<digest>` suffixes can be re-introduced.
- **Not providing NousResearch + openchamber credentials.**
  Those are secrets the operator must add to
  `dev-baile/hermes/*` and `dev-baile/openchamber/*` in
  Infisical BEFORE the first deploy. Adding those secrets
  is a separate ops change.
- **Not deploying the 3 stacks in Locket/Infisical production
  mode.** They use dev-mode defaults (per `./scripts/stack.sh`
  with no LOCKET_ENABLED). Full Locket integration is a
  follow-up change.
- **Not addressing the in-flight v5-drift change's
  unrelated edits** (the user has separately uncommitted
  edits to other files in the bonneagar worktree; those are
  not in this change's scope).
- **Not bringing up mailcow-dockerized / mlx-omni / letta /
  browser.** All 4 remain deferred (per the Change 1 plan's
  defer list).

## Spec delta

- `infrastructure-stacks/spec.md` — 1 ADDED Requirement
- `agent-platform-cluster/spec.md` — **NEW capability spec**
  with 3 ADDED Requirements
- `agentic-frontend-frameworks/spec.md` — 1 ADDED Requirement

See `specs/<capability>/spec.md` for the full delta.

## Open follow-up issues

| Issue | Tracking change |
|:--|:--|
| Full SHA256 digest pinning for the 3 images (renovate cycle) | `2026-07-XX-stack-doctor-image-digest-pinning` (deferred) |
| NousResearch + openchamber PATs added to dev-baile Infisical | `2026-07-XX-wire-hermes-openchamber-infisical-secrets` (deferred) |
| Build dots-ocr image locally from upstream Dockerfile | `2026-07-XX-bring-dots-ocr-up-to-spec` (deferred) |
| Bring browser stack to GOLD_STANDARD | `2026-07-XX-bring-browser-stack-to-gold-standard` (deferred) |
| Multi-notebook marimo dashboard (11 tabs) | `2026-07-XX-marimo-multi-notebook-dashboard` (deferred) |