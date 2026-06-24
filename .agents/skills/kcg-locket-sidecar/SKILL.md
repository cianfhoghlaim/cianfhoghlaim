---
name: kcg-locket-sidecar
description: Wire a Locket sidecar into a Docker Compose stack that needs Infisical secret injection at runtime in the Cianfhoghlaim monorepo. Covers the canonical `sidecar.yaml` template (the 3 observed variants across 86+ stacks: linkwarden-style with tmpfs driver_opts, cognee-style with `type: tmpfs` block, pocket-id-style with Komodo env block), the `secrets.env` URI syntax (`infisical://dev-baile/<svc>/<key>`), the 3 Locket modes (`watch` / `exec` / `oneshot`), the `user: 65532:65532` + `no-new-privileges:true` + `cap_drop: [ALL]` security baseline, the `cianchoghlaim_locket_secrets` shared tmpfs volume contract, and the relationship between `secrets.env` (the consumer) and `sidecar.yaml` (the Locket injection). Use when adding a new stack that needs secrets at runtime, debugging a missing env var, or migrating a stack from the v0 secret-injection pattern to Locket.
---

# KCG Locket Sidecar

## Purpose

Locket is the KCG secret-injection sidecar. Every Docker Compose
stack that needs **runtime** secrets (not just build-time) has a
`sidecar.yaml` that runs a Locket container alongside the main
service. Locket reads the `secrets.env` file (a list of
`infisical://dev-baile/<svc>/<key>` URIs), fetches the values from the
Infisical vault, and writes them to a shared tmpfs volume at
`/run/secrets/locket/secrets.env`. The main service then
`env_file: /run/secrets/locket/secrets.env`.

This skill captures the canonical template + the 3 observed
variants + the security baseline + the tmpfs volume contract.

## When to use this skill

Use when you need to:

- "Add a new Locket-protected stack"
- "Debug a `secret not found` from a running container"
- "Migrate a stack from the v0 Infisical `op run` pattern to Locket"
- "Add a new secret to a stack's `secrets.env`"
- "Understand the difference between `watch` / `exec` / `oneshot` modes"
- "Understand the `user: 65532:65532` security baseline"

## The canonical `sidecar.yaml` template (the 6-field shape)

```yaml
# infrastructure/stacks/<name>/sidecar.yaml
services:
  locket:
    image: ghcr.io/cianfhoghlaim/locket:1.0.0   # SHA-pinned per stack-doctor rule
    user: "65532:65532"                          # nobody:nogroup (the security baseline)
    security_opt:
      - "no-new-privileges:true"
    cap_drop:
      - "ALL"
    read_only: true
    tmpfs:
      - /run/secrets/locket:size=1m,mode=0700,uid=65532,gid=65532
    environment:
      LOCKET_MODE: watch                          # "watch" | "exec" | "oneshot"
      LOCKET_SECRETS_FILE: /run/secrets/locket/secrets.env
    volumes:
      - cianchoghlaim_locket_secrets:/run/secrets/locket:ro
    restart: unless-stopped
    depends_on:
      <main-service>:
        condition: service_healthy

volumes:
  cianchoghlaim_locket_secrets:
    external: true   # defined in infrastructure/locket/compose.yaml
```

## The 3 observed variants (the drift to unify)

| Variant | Where | Difference from canonical |
|:--|:--|:--|
| `linkwarden-style` | `stacks/linkwarden/sidecar.yaml` | Uses `driver_opts: { device: "tmpfs", o: "size=1m,mode=0700" }` instead of `tmpfs:` block |
| `cognee-style` | `stacks/cognee/sidecar.yaml` | Uses `tmpfs: { type: tmpfs, target: /run/secrets/locket, ... }` (the v3 Compose spec) |
| `pocket-id-style` | `stacks/pocket-id/sidecar.yaml` | Has an extra `env_file: secrets.env` block at the top of the `locket` service (so Locket reads the URI list from the volume, not from a literal `environment:`) |

**`bun run stack-doctor` enforces the canonical template**; the
3 variants above are scheduled for migration in round 7 of the
multi-quadrant refactor plan.

## The `secrets.env` URI syntax

```bash
# infrastructure/stacks/<name>/secrets.env
INFI_DATABASE_URL=infisical://dev-baile/oideachais/database_url
INFI_LANCEDB_URI=infisical://dev-baile/oideachais/lancedb_uri
INFI_HF_TOKEN=infisical://dev-baile/cross-cutting/hf_token
INFI_PANGOLIN_API_KEY=infisical://dev-baile/control-plane/pangolin_api_key
```

The URI has 3 parts:
1. **scheme**: always `infisical://`
2. **environment**: always `dev-baile` (the only dev environment; prod uses `prod-` prefix)
3. **path**: `<service>/<key>` — must match the vault structure (see `.agents/skills/secrets-management/SKILL.md` for the full path table)

Locket resolves the URI at runtime by calling the Infisical API with
the machine identity token (stored in `infrastructure/infisical_secret`).

## The 3 Locket modes (the runtime contract)

| Mode | Behaviour | When to use |
|:--|:--|:--|
| `watch` | Locket polls the vault every 60s and rewrites the tmpfs file if any secret changed | Long-running services (Dagster, the FastAPI agents) |
| `exec` | Locket runs as a one-shot and the main service `depends_on: locket: condition: service_completed_successfully` | Init containers + batch jobs |
| `oneshot` | Locket writes the secrets and exits; the tmpfs file persists for the lifetime of the compose project | CI/CD pipelines + ephemeral tasks |

The default is `watch`; use `exec` for batch jobs and `oneshot` for CI.

## The security baseline (the 4 hard rules)

1. **`user: "65532:65532"`** (nobody:nogroup) — Locket must NOT run as root
2. **`security_opt: ["no-new-privileges:true"]`** — no setuid escalation
3. **`cap_drop: ["ALL"]`** — drop all Linux capabilities
4. **`read_only: true`** + **`tmpfs:` block at `/run/secrets/locket`** — the only writable path is the tmpfs

The 4 rules are enforced by `bun run stack-doctor` (a violation is
**CRITICAL** and fails the build).

## The shared tmpfs volume (the contract)

`cianchoghlaim_locket_secrets` is an **external** volume defined in
`infrastructure/locket/compose.yaml`. Every stack that uses Locket
mounts the same external volume — the secrets are NOT per-stack.

```yaml
# infrastructure/locket/compose.yaml
volumes:
  cianchoghlaim_locket_secrets:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
      o: size=10m,mode=0700
```

The volume is **shared** (10MB cap) so Locket can re-use the same
volume across all 86+ stacks without exhausting memory.

## Worked example: add a new Locket-protected stack

1. Add `infrastructure/stacks/oideachais-dagster/secrets.env`:

   ```bash
   INFI_DAGSTER_HOME=infisical://dev-baile/oideachais/dagster_home
   INFI_DAGSTER_DB=infisical://dev-baile/oideachais/dagster_db_url
   ```

2. Add `infrastructure/stacks/oideachais-dagster/sidecar.yaml`:

   ```yaml
   services:
     locket:
       image: ghcr.io/cianfhoghlaim/locket:1.0.0
       user: "65532:65532"
       security_opt: ["no-new-privileges:true"]
       cap_drop: ["ALL"]
       read_only: true
       tmpfs: [/run/secrets/locket:size=1m,mode=0700,uid=65532,gid=65532]
       environment:
         LOCKET_MODE: watch
         LOCKET_SECRETS_FILE: /run/secrets/locket/secrets.env
       volumes: [cianchoghlaim_locket_secrets:/run/secrets/locket:ro]
       restart: unless-stopped
   volumes:
     cianchoghlaim_locket_secrets: { external: true }
   ```

3. Add `infrastructure/stacks/oideachais-dagster/compose.yaml`:

   ```yaml
   services:
     dagster:
       image: ghcr.io/cianfhoghlaim/oideachais-dagster:latest
       env_file: /run/secrets/locket/secrets.env   # the Locket tmpfs
       volumes: [cianchoghlaim_locket_secrets:/run/secrets/locket:ro]
   ```

4. Wire the 2 files together:

   ```bash
   cd infrastructure/komodo
   docker compose -f compose.yaml -f ../stacks/oideachais-dagster/compose.yaml -f ../stacks/oideachais-dagster/sidecar.yaml up -d
   ```

5. Verify:

   ```bash
   docker compose exec dagster env | grep INFI_DAGSTER_HOME
   # Returns: INFI_DAGSTER_HOME=postgresql://...
   ```

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| `env_file: /run/secrets/locket/secrets.env: No such file or directory` | Locket didn't run | Check `docker compose ps locket`; the Locket container must be `Up` |
| `Locket: infisical URI not found: infisical://dev-baile/oideachais/foo` | The URI path doesn't match the vault | Run `bun run scripts/init-vault.ts` to create the secret |
| `Locket: 401 Unauthorized` | The machine identity token expired | Re-run `mise run locket:init` |
| `Locket: tmpfs volume not mounted` | The `cianchoghlaim_locket_secrets` external volume is missing | Run `docker compose -f infrastructure/locket/compose.yaml up -d` |

## Cross-references

- `.agents/skills/secrets-management/SKILL.md` — the 3-layer Infisical + Locket + mise contract
- `.agents/skills/stack-ops/SKILL.md` — the 6-file GOLD_STANDARD pattern
- `.agents/skills/kcg-convergence/SKILL.md` — the Locket category in the 94-stack layout
- `infrastructure/SECRETS-MANAGEMENT.md` — the 245-line Infisical + Locket + mise contract
- `infrastructure/legacy/LOCKET-MODES.md` — the v0 predecessor analysis (now superseded)
