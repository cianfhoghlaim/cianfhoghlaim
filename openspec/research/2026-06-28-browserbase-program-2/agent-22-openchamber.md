# Agent 22 — OpenChamber (Agent IDE)

**Date:** 2026-06-28
**Phase:** 2 (recheck, agent-platform)
**Budget used:** ~10 credits (Firecrawl)
**Subagent:** agent-platform

## TL;DR

**OpenChamber is REAL upstream** (5.9k★, 620 forks, MIT, `v1.11.7` June 2026) — a
Bun + React + Electron + VS Code **agent IDE** for the `sst/opencode` AI coding
agent. Cianfhoghlaim wires it as the human-operator surface at
`openchamber.cianfhoghlaim.ie` via the Pangolin mesh, bundled-mode (no
`OPENCODE_HOST`), Locket-injected Infisical secrets. **Critical drift**: the
P2-20 research file (`phase-2/P2-20-openchamber.md`) is **inconsistent with
the deployed stack** — it says `image: openchamber/openchamber:latest`,
`port 3030:8080`, `openchamber-postgres`, and `LITELLM_BASE_URL`, none of
which match `infrastructure/stacks/openchamber/compose.yaml`.

## Code

| Path | Purpose |
|:--|:--|
| `infrastructure/stacks/openchamber/compose.yaml` | Single service, port 3000, no Postgres, no LiteLLM wiring |
| `infrastructure/stacks/openchamber/sidecar.yaml` | Locket sidecar (`ghcr.io/bpbradley/locket:infisical`) |
| `infrastructure/stacks/openchamber/secrets.env` | 4 Infisical refs (ui_password, openai/anthropic/minimax keys) |
| `infrastructure/stacks/openchamber/pangolin.yaml` | Traefik router with `tinyauth` + `secure-headers` middlewares |
| `infrastructure/stacks/openchamber/blueprint.yaml` | Pangolin private resource `openchamber` (Member role, port 3000) |
| `infrastructure/stacks/openchamber/.env.example` | Non-secret defaults + commented future-mode hints |
| `openspec/changes/add-openchamber-stack-and-opencode-ui/proposal.md` | The ADDED spec, **bundled-mode + no-tunnel v1** |
| `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-20-openchamber.md` | **DRIFTED** — claims Postgres+LiteLLM wiring that doesn't exist |

**Canonical deployed compose** (`infrastructure/stacks/openchamber/compose.yaml:28-64`):
```yaml
openchamber:
  image: ghcr.io/openchamber/openchamber:1.0.0@sha256:00000000…0000
  container_name: openchamber
  restart: unless-stopped
  read_only: true
  tmpfs: [/tmp:64m]
  cap_drop: [ALL]
  security_opt: [no-new-privileges:true]
  ports: ["127.0.0.1:3000:3000"]            # not :latest, not 3030:8080
  environment:
    OPENCHAMBER_PORT: "3000"
    OPENCHAMBER_THEME: ${OPENCHAMBER_THEME:-cianfhoghlaim-dark}
    OPENCHAMBER_LOG_LEVEL: ${OPENCHAMBER_LOG_LEVEL:-info}
    # OPENCODE_HOST intentionally NOT set (bundled mode)
  volumes: [openchamber-state:/home/bun/.openchamber]
  healthcheck:
    test: ["CMD-SHELL", "curl -fs http://localhost:3000/api/health || exit 1"]
  deploy:
    resources:
      limits: {cpus: '1', memory: 1G}
```

**Upstream `openchamber/openchamber` architecture** (from `AGENTS.md` at HEAD `v1.11.7`):
- **Stack:** Bun runtime, Node ≥22, React + TypeScript + Vite + Tailwind v4,
  Zustand state, **Base UI** (`@base-ui/react` — primary; Radix is legacy,
  HeroUI is also a dep), Remixicon (sprite-only, never direct import).
- **Server:** Express at `packages/web/server/index.js`, exposed via
  `startWebUiServer({...})` returning `{getPort(), stop()}`.
- **Desktop shell:** Electron 41, `packages/electron/main.mjs` boots the
  **web server in the same Node process** (no sidecar subprocess); preload
  `packages/electron/preload.mjs` exposes the IPC bridge.
- **VS Code:** `packages/vscode/` provides webview + extension-host parity.
- **OpenCode integration:** UI wrapper `packages/ui/src/lib/opencode/client.ts`
  imports `@opencode-ai/sdk/v2`; sync/event pipeline is `SyncProvider` from
  `packages/ui/src/sync/sync-context.tsx`; SSE/WS events in
  `packages/ui/src/sync/event-pipeline.ts`; server embeds OpenCode via
  `createOpencodeServer` in `packages/web/server/index.js`. **External mode:**
  set `OPENCODE_HOST` (e.g. `http://hostname:4096`) + `OPENCODE_SKIP_START=true`.
- **Workspaces:** `packages/{ui, web, electron, vscode}`.
- **Critical runtime rule:** "Electron imports the server via
  `@openchamber/web/server/index.js` (workspace dep) and calls
  `startWebUiServer({...})`" — bundled, not networked.

## Env

| Env var | Deployed value | Source | P2-20 says | Drift? |
|:--|:--|:--|:--|:--|
| `OPENCHAMBER_PORT` | `3000` | compose | `3030:8080` (compose port) | YES |
| Image | `ghcr.io/openchamber/openchamber:1.0.0@sha256:0…0` | compose | `openchamber/openchamber:latest` | YES |
| `OPENCODE_HOST` | NOT set (bundled) | compose | n/a (not mentioned) | OK |
| `OPENCHAMBER_TUNNEL_TOKEN` | NOT set (Pangolin) | compose | n/a | OK |
| `OPENCHAMBER_UI_PASSWORD` | Infisical ref | secrets.env | n/a | OK |
| `OPENAI_API_KEY` | Infisical ref | secrets.env | n/a (not LiteLLM) | OK |
| `ANTHROPIC_API_KEY` | Infisical ref | secrets.env | n/a | OK |
| `MINIMAX_API_KEY` | Infisical ref | secrets.env | `LITELLM_BASE_URL=http://litellm:4000/v1` (not used) | YES |
| `LITELLM_BASE_URL` | **NOT used** | — | `http://litellm:4000/v1` (P2-20:31) | YES |
| `LANGFUSE_HOST` | **NOT used** | — | `${LANGFUSE_HOST}` (P2-20:33) | YES |
| `OPENCHAMBER_DATABASE_URL` | **NOT used** (no Postgres) | — | `infisical://dev-baile/openchamber/database_url` (P2-20:50) | YES |
| `POSTGRES_PASSWORD` | **NOT used** | — | `${POSTGRES_PASSWORD}` (P2-20:43) | YES |
| `DATABASE_URL` | **NOT used** | — | `postgres://openchamber-postgres:5432/openchamber` (P2-20:30) | YES |

## CCC anchors

- `infrastructure/stacks/openchamber/` (6 files + README = 7, all GOLD_STANDARD)
- `openspec/changes/add-openchamber-stack-and-opencode-ui/{proposal.md, tasks.md, specs/{infrastructure-stacks,agentic-frontend-frameworks}/spec.md}`
- `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-20-openchamber.md` (drifted, see §6)
- Upstream: `github.com/openchamber/openchamber` (5.9k★, 620 forks, MIT, `v1.11.7`)
- Search terms: `"openchamber"`, `"OPENCHAMBER_UI_PASSWORD"`, `"OPENCODE_HOST"`,
  `"startWebUiServer"`, `"@opencode-ai/sdk/v2"`, `"createOpencodeServer"`.

## Drift log

| Date | Event | Source |
|:--|:--|:--|
| 2025-12 | Initial OpenChamber "deploy" claim (P2-20:63) — never actually deployed in this shape | P2-20 drift log |
| 2026-03 | "Embedded in TanStack Start (oideachais-web)" — **no such embed in `oideachais-web/src/routes/agents.tsx` today** | P2-20 drift log |
| 2026-05 | "Wired to LiteLLM `minimax` alias" — actual stack uses direct `MINIMAX_API_KEY`, **not** LiteLLM | P2-20 drift log |
| 2026-06-28 | Real stack landed at `infrastructure/stacks/openchamber/` via `add-openchamber-stack-and-opencode-ui` change | proposal.md |
| 2026-06-28 | P2-20 research file **never updated** to reflect deployed reality (image tag, port, no Postgres, no LiteLLM) | P2-20 |

**Confirmed by upstream `AGENTS.md` (v1.11.7, 2026-06-26):**
- Bundled-mode is the supported default; `OPENCODE_HOST` only set for external daemon.
- Image: `oven/bun:1.3.5` base; upstream monthly release cadence; semver + SHA256 pin
  pattern is canonical (matches our `1.0.0@sha256:0…0` placeholder convention).

## Anti-patterns

1. **Don't use `:latest`** — upstream `AGENTS.md` mandates semver + SHA256 pin;
   current `compose.yaml:29` uses placeholder digest `0000…0000` (still a pin,
   but a zero placeholder — replace before deploy).
2. **Don't set `OPENCODE_HOST` in v1** — README:32-33, proposal:56-67, and
   upstream docs all say bundled is the default; setting `OPENCODE_HOST` would
   break the build-phase user-survey decision.
3. **Don't bypass Pocket ID OIDC** — `pangolin.yaml:23` requires the
   `tinyauth` middleware; the `OPENCHAMBER_UI_PASSWORD` is a 2nd factor, not
   the only auth (proposal:166-167).
4. **Don't run OpenChamber without a host-volume session store** —
   `compose.yaml:50` mounts `openchamber-state` to `/home/bun/.openchamber`;
   losing this loses session history.
5. **Don't put BAML inside the openchamber image** — the upstream is an
   OpenCode UI shell; BAML extraction lives in the `oideachais-baml-schemas`
   spec (`sruth/oideachais/baml_src/`).
6. **Don't port-forward `:3000` directly to the public internet** —
   `compose.yaml:41` binds to `127.0.0.1:3000`; Pangolin/Traefik is the only
   public path.
7. **Don't use `with_state` cross-runtime paths in shared UI** — upstream
   rule: "Do not ship a web-only assumption into shared UI" (Electron +
   webview + VS Code webview parity is required).

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Runtime mode | **Bundled** (no `OPENCODE_HOST`) | User-survey result; avoids 2-process ops |
| Auth | **Pocket ID OIDC** (Pangolin) + UI password 2FA | proposal:166-167; matches all other stacks |
| DB | **None** (named volume only) | P2-20's Postgres was never wired; sessions are local file state |
| LLM gateway | **Direct provider keys** (not LiteLLM) | UI ships its own provider picker; LiteLLM is for app backends |
| Tunnel | **None** (Pangolin only) | proposal:69-77; v1 doesn't need Cloudflare tunnel |
| Hosting | `arm1-oci` (control plane) | proposal:152-158; same tier as `oideachais`, `openclaw` |
| Resources | `1 CPU / 1 GB` | compose.yaml:58-62; matches `openclaw` (256 MB idle / 1 GB load) |
| Image pin | semver + SHA256 | matches all 90 stacks; renovate monthly |
| OpenCode wire | `@opencode-ai/sdk/v2` | upstream-canonical (v1.11.7) |
| State store | Zustand + Express server-side + SSE | upstream-canonical; not Redux/Jotai |

## §8 Refactor (4 items)

**R1 (HIGH) — P2-20 research file drift:** Rewrite
`openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-20-openchamber.md`
to match the **actually-deployed** stack. Replace:
- ❌ `image: openchamber/openchamber:latest` → ✅ `ghcr.io/openchamber/openchamber:1.0.0@sha256:0…0`
- ❌ `ports: ["3030:8080"]` → ✅ `ports: ["127.0.0.1:3000:3000"]`
- ❌ `openchamber-postgres` service → ❌ **delete entirely** (no DB)
- ❌ `LITELLM_BASE_URL=http://litellm:4000/v1` → ❌ **delete** (direct provider keys)
- ❌ `LANGFUSE_HOST` env → ❌ **delete** (not wired)
- ❌ Embed claim in `oideachais-web/src/routes/agents.tsx` → ❌ **delete** (no embed today)
- ✅ Update drift-log dates to 2026-06-28 with the new "P2-20 never updated" event.
- ✅ Add a §3 row in decision matrix: "State store = named volume, not DB".

**R2 (MED) — Replace placeholder SHA256 digest:** `compose.yaml:29` has
`sha256:0000000000000000000000000000000000000000000000000000000000000000`
— a zero-digest placeholder. Before first deploy, resolve the real digest
via `docker pull ghcr.io/openchamber/openchamber:1.0.0` and pin it. Until
then, `docker compose config` will pass but no image will actually pull.

**R3 (MED) — Add Litestream-style backup hint for `openchamber-state`:**
The `openchamber-state` named volume holds session history and skill catalog
metadata (per upstream `skills-catalog/DOCUMENTATION.md`). Add a 1-line note
in `README.md` recommending `restic` to a Garage S3 bucket on the
`backup` schedule. No code change required; just a README paragraph.

**R4 (LOW) — Cross-link `openclaw` stack:** The proposal.md:154 explicitly
says openchamber's resource budget matches `openclaw`. Add a 1-line
cross-reference in `infrastructure/stacks/openclaw/README.md` (and vice
versa) so operators can see the 2 agent-UI surfaces side-by-side. The
`openclaw` stack is the chat assistant surface; `openchamber` is the
coding-agent IDE surface — complementary, not redundant.

---

**Cross-references:**
- Agent 06 (litellm): confirmed `OPENAI_BASE_URL` for `minimax` is `http://litellm:4000/v1`
  but the openchamber stack **bypasses** LiteLLM and uses direct provider keys. Do
  **not** add `LITELLM_BASE_URL` to `secrets.env` — it would break the upstream
  provider-picker UX.
- Agent 17 (komodo): the `komodo run procedure deploy-openchamber-arm1-oci` and
  `infrastructure/komodo/stacks/openchamber-arm1-oci.toml` files are referenced
  in proposal.md:82-87 but **do not yet exist on disk** — openspec change is
  partially-merged (the 6-file compose set is in place; the Komodo glue is not).
