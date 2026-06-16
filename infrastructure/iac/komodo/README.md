# Komodo + Pangolin IaC

TypeScript Infrastructure-as-Code for managing Komodo Core + the Pangolin
Integrations API as the source of truth for stack and resource state.

## Layout

| File | Purpose |
|:--|:--|
| `config.ts` | Reads env vars + .env; exports `CONFIG` |
| `komodo-rpc.ts` | Bare-metal fetch wrapper for Komodo Core API (`/read`, `/write`, `/execute`) |
| `deploy-stacks.ts` | Idempotent upsert of all Komodo servers, stacks, resource-syncs |
| `read-state.ts` | Dumps current Komodo state to stdout (for verification) |
| `create-resources.ts` | Idempotent upsert of all Pangolin private resources |
| `package.json` | Uses `komodo_client` SDK (when available) — also hand-rolled RPC fallback |

## Usage

```bash
# 1. Install deps
cd infrastructure/iac/komodo
bun install

# 2. Set Komodo credentials (either a JWT or a password)
export KOMODO_JWT="<jwt from /auth/login>"
# OR
export KOMODO_PASSWORD="changeme-not-for-production"

# 3. Read state
bun run read-state.ts

# 4. Deploy stacks
bun run deploy-stacks.ts

# 5. Set Pangolin API key (one-time, from Pangolin UI)
export PANGOLIN_API_KEY="<key>"

# 6. Create Pangolin private resources
bun run create-resources.ts
```

## Why a custom `komodo-rpc.ts` instead of `komodo_client`?

The official `komodo_client` npm package (v2.1.1) imports `mogh_auth_client`
which uses `localStorage` — a browser-only API. It crashes in Node/Bun
unless we polyfill. Our `komodo-rpc.ts` calls the Komodo HTTP API directly
with `fetch()`, which works in both browser and Bun/Node.

Once `mogh_auth_client` becomes SSR-friendly, switch to:

```ts
import { KomodoClient } from "komodo_client";
const komodo = KomodoClient(url, { type: "jwt", params: { jwt } });
```

## Why `create-resources.ts` calls Pangolin via raw fetch?

Pangolin doesn't publish an official TypeScript client yet. The
Integrations API is documented at https://docs.pangolin.net/manage/integration-api
and lives at `https://pangolin.cianfhoghlaim.ie/api/v1/...` (Bearer auth).

We hit the raw endpoints in `create-resources.ts` to create/update site
resources without round-tripping through the UI.

## See also

- `infrastructure/docs/pangolin-komodo/PANGOLIN_KOMODO_SETUP.md` — the
  full end-to-end runbook (Phase 1-9, idempotency, gotchas)
- `infrastructure/scripts/setup-pangolin-komodo.sh` — the bash
  orchestrator that runs the same 9 phases
