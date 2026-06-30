# Infrastructure GOLD STANDARD

The 6-file template that every Docker Compose stack under
`bonneagar/stacks/<name>/` SHALL follow. Use this as the
checklist when adding a new stack, and the audit reference when running
`bun run validate-stacks` (the `stack-doctor` turbo task).

## Why This Standard Exists

The 94 stacks in this monorepo were built by multiple agents over
~2 years. Without a uniform pattern:

- Komodo can't reliably sync them (different file layouts)
- Pangolin's Traefik labels drift (some stacks use 5, some use 6 labels)
- Locket sidecars are inconsistent (some stacks inject at boot, some
  don't)
- Secrets leak (some stacks have plaintext env in `compose.yaml`)

The 6-file GOLD_STANDARD eliminates all four failure modes. **All 6
files are required. Partial conformance is non-conformance.**

## The 6 Required Files

| File | Purpose | Committed? |
|:--|:--|:--|
| `compose.yaml` | Docker service definitions (health checks, restart policies, volumes, network) | Yes |
| `pangolin.yaml` | Traefik routing + TinyAuth SSO labels (6-label pattern) | Yes |
| `sidecar.yaml` | Locket container for Infisical secret injection at runtime | Yes |
| `secrets.env` | Infisical URI references (`infisical://dev-baile/...`) — NO plaintext | Yes |
| `blueprint.yaml` | Komodo Resource Sync definition for GitOps deployment | Yes |
| `.env.example` | Local-dev placeholder env vars (committed, no real secrets) | Yes |

Plus a `README.md` (recommended but not required) for human readers.

## 1. `compose.yaml` — Service Definitions

```yaml
# Exemplar: bonneagar/stacks/garage/compose.yaml
services:
  garage:
    image: dxflrs/garage:v1.0.1
    container_name: cianfhoghlaim-garage
    restart: unless-stopped
    ports:
      - "3900:3900"  # S3 API
      - "3901:3901"  # Admin
      - "3902:3902"  # Web UI
    volumes:
      - garage_meta:/var/lib/garage/meta
      - garage_data:/var/lib/garage/data
      - ./config/garage.toml:/etc/garage.toml:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3900/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    networks:
      - cianfhoghlaim
    depends_on:
      locket:
        condition: service_healthy

volumes:
  garage_meta:
  garage_data:

networks:
  cianfhoghlaim:
    external: true
```

**Mandatory fields:**
- `restart: unless-stopped` (or `always` for stateful critical services)
- `healthcheck:` with `test:`, `interval:`, `timeout:`, `retries:`
- `networks: - cianfhoghlaim` (or other shared network)
- `depends_on: locket: condition: service_healthy` (so secrets are ready)
- Named volumes (NOT bind mounts) for stateful data
- `container_name:` prefixed with `cianchoghlaim-` for docker ps grep

**Forbidden:**
- `image: :latest` — always pin to `<major>.<minor>.<patch>`
- Plaintext secrets in `environment:` — use Locket via `env_file: /run/secrets/locket/secrets.env`
- `network_mode: host` — defeats the shared-network pattern

## 2. `pangolin.yaml` — Traefik Routing

```yaml
# Exemplar: bonneagar/stacks/litellm/pangolin.yaml
http:
  routers:
    litellm:
      entryPoints: [https]
      rule: "Host(`litellm.cianfhoghlaim.ie`)"
      service: litellm
      tls: { certResolver: letsencrypt }
      middlewares: [tinyauth]
  services:
    litellm:
      loadBalancer:
        servers:
          - url: "http://litellm:4000"
```

**Mandatory fields:**
- `entryPoints: [https]` (never just `http`)
- `tls: { certResolver: letsencrypt }` for valid certs
- `middlewares: [tinyauth]` for SSO enforcement
- `Host(\`<service>.cianfhoghlaim.ie\`)` rule
- The 6-label `pangolin.private-resources.<name>.*` pattern
  (see `.agents/skills/stack-ops/SKILL.md` § "6-Label Pattern")

**Stacks that are NOT web-facing** (e.g. CLI tools, internal-only
services) can omit this file or have an empty stub.

## 3. `sidecar.yaml` — Locket Secret Injection

```yaml
# Exemplar: bonneagar/stacks/litellm/sidecar.yaml
services:
  locket:
    image: ghcr.io/cianfhoghlaim/locket:latest
    container_name: cianfhoghlaim-litellm-locket
    restart: unless-stopped
    env_file: /run/secrets/locket/secrets.env
    volumes:
      - locket_secrets:/run/secrets/locket:ro
    healthcheck:
      test: ["CMD-SHELL", "test -f /run/secrets/locket/secrets.env"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - cianfhoghlaim

volumes:
  locket_secrets:
    external: true
    name: cianfhoghlaim_locket_secrets

networks:
  cianfhoghlaim:
    external: true
```

**Mandatory fields:**
- Mounts the shared `cianchoghlaim_locket_secrets` external volume as read-only
- Health-check confirms the `secrets.env` file is present
- Uses the same shared network as the main service

## 4. `secrets.env` — Infisical References

```bash
# Exemplar: bonneagar/stacks/litellm/secrets.env
# COMMITTED: yes. PLAINTEXT: NEVER. Use Infisical URI references.

LITELLM_MASTER_KEY=infisical://dev-baile/litellm/master_key
LITELLM_SALT_KEY=infisical://dev-baile/litellm/salt_key
DATABASE_URL=infisical://dev-baile/litellm/postgres_url
```

**Mandatory:**
- Every line uses the `infisical://dev-baile/<service>/<key>` pattern
- NO plaintext secrets, NO `changeme`, NO `default`
- Variable names match what the service expects
- Comments at the top of the file remind contributors this is committed

**Forbidden:**
- `API_KEY=sk-12345...` — plaintext
- `PASSWORD=hunter2` — plaintext
- `*_KEY=changeme` — placeholder

## 5. `blueprint.yaml` — Komodo Resource Sync

```yaml
# Exemplar: bonneagar/stacks/litellm/blueprint.yaml
name: litellm
description: "LiteLLM gateway — LLM proxy with Postgres + Prometheus"
type: stack
run_directory: bonneagar/stacks/litellm
files:
  - compose.yaml
  - sidecar.yaml
schedule:
  enabled: false
metadata:
  ports: [4000, 9090, 5432]
  depends_on: [postgres]
```

**Mandatory fields:**
- `name:` matches the directory name (lowercase, kebab-case)
- `type: stack` (vs `type: procedure` or `type: action`)
- `run_directory:` is the relative path from the repo root
- `files:` lists the compose + sidecar YAML
- `metadata.ports:` lists exposed ports for documentation
- `metadata.depends_on:` lists other stacks (if any) for deployment ordering

## 6. `.env.example` — Local-Dev Placeholders

```bash
# Exemplar: bonneagar/stacks/litellm/.env.example
# COMMITTED: yes. This file is for local development only.
# For production, Locket resolves secrets via Infisical.

LITELLM_MASTER_KEY=sk-1234  # pragma: allowlist secret
LITELLM_SALT_KEY=sk-1234     # pragma: allowlist secret
DATABASE_URL=postgresql://litellm:litellm@postgres:5432/litellm
```

**Mandatory:**
- Every variable that `secrets.env` has should also appear here with a placeholder
- `# pragma: allowlist secret` after the placeholder so secret-scanners don't trip
- Comments explain the local-dev intent vs production Infisical resolution

## Adding a New Stack — Workflow

```bash
# 1. Use the stack-ops skill to scaffold the 6 files
#    (See .agents/skills/stack-ops/SKILL.md)
bun run stack:scaffold --name my-new-service

# 2. Edit compose.yaml to define your service
# 3. Edit pangolin.yaml to add the routing rule (if web-facing)
# 4. Edit secrets.env to reference your Infisical secrets
# 5. Edit .env.example to add local-dev placeholders
# 6. Add the secrets to the Infisical vault:
bun run scripts/init-vault.ts
# 7. Create the Komodo procedure:
#    bonneagar/komodo/procedures/<name>-<action>.toml
# 8. Validate:
bun run validate-stacks
# 9. Commit and let Komodo sync deploy
```

## Validation

```bash
# Full audit (all 94 stacks)
bun run validate-stacks

# Single stack
bun run stack-doctor.sh bonneagar/stacks/<name>/
```

The `stack-doctor` checks:
- All 6 GOLD_STANDARD files present
- `compose.yaml` has health checks + restart policy
- `pangolin.yaml` uses 6-label pattern (if web-facing)
- `secrets.env` has no plaintext (regex match against known-key patterns)
- `blueprint.yaml` has required fields
- `container_name:` is prefixed `cianchoghlaim-`
- `networks:` uses the shared `cianchoghlaim` network

Stacks that fail validation are listed in the audit report with the
specific file and line that needs fixing. **No stack may be deployed
via Komodo until it passes validation.**

## Exemplars (Reference Implementations)

The cleanest reference implementations in the repo, in order of
completeness:

| Stack | Why it's a good exemplar |
|:--|:--|
| `bonneagar/stacks/garage/` | Simplest possible stack (one service, S3 API, no web UI) |
| `bonneagar/stacks/litellm/` | 3-service stack (gateway + postgres + prometheus), web-facing |
| `bonneagar/stacks/cognee/` | 2-service stack (cognee + postgres) with complex env |
| `bonneagar/stacks/pangolin/` | The most complex stack — Traefik + WireGuard + Pocket ID + CrowdSec |

When in doubt, copy one of these and adapt.

## See Also

- `.agents/skills/stack-ops/SKILL.md` — operational skill for working with stacks
- `bonneagar/AGENTS.md` — agent instructions for the infrastructure layer
- `bonneagar/stacks/README.md` — the 94-stack flat directory
- `bonneagar/README.md` — 10-step quickstart bring-up
- `bonneagar/komodo/procedures/` — Komodo GitOps procedures
- `bonneagar/dagger/` — Dagger CI/CD modules
- `bonneagar/PANGOLIN-SETUP.md` — Pangolin installation walkthrough
- `bonneagar/SECRETS-MANAGEMENT.md` — Infisical + Locket deep-dive
- `bonneagar/DEPLOYMENT-STRATEGY.md` — the canonical 6-step deploy playbook

## CI gate — `stack-doctor`

A follow-up change will add a `stack-doctor` turbo task that
runs the 4 audit scripts under `bonneagar/audit/scripts/`
and the 6-file compliance check, posting the output as a
GitHub PR comment. The CI gate will be GREEN only when:

1. Every directory under `bonneagar/stacks/**/` that has a
   `compose.yaml` also has the other 5 GOLD_STANDARD files
   (`sidecar.yaml`, `secrets.env`, `blueprint.yaml`,
   `.env.example`, `README.md`).
2. Every `container_name:` declared in any compose is either
   present in the live `bonneagar/audit/inventory/<host>-<UTC>.json`
   snapshot OR explicitly documented as a "stacked-only, not
   running" service (e.g. the 3 control-plane stacks that
   only run on `arm1-oci`).
3. Every `secrets.env` line that contains an
   `infisical://dev-baile/...` reference points to a secret
   that exists in the vault.
4. Every Pangolin private-resource `blueprint.yaml` parses
   against the official `pangolin.cianfhoghlaim.io` schema.

The check is GREEN = 0 stack failures, RED = 1+ failures. The
exit code is bitwise-OR: 1 = missing files, 2 = orphaned
container, 4 = missing secret, 8 = malformed blueprint.

A future agent can invoke it as:

```bash
bun run validate-stacks
# or
bun run stack-doctor
```

For now, the audit scripts are run-on-demand only (see
`bonneagar/audit/README.md`).
