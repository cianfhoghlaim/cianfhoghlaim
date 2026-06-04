---
name: stack-ops
description: "This skill should be used when adding, fixing, or auditing a Docker Compose stack under infrastructure/stacks/. Trigger phrases: 'add a new stack', 'fix stack', 'audit stacks', 'add Locket sidecar', 'add Infisical secret', 'check stack health', 'stack-doctor', 'why is stack X broken'."
---

# stack-ops — Adding, fixing, and auditing Docker Compose stacks

The cianfhoghlaim monorepo manages 70+ Docker Compose stacks under `infrastructure/stacks/{engineering,tools,storage,machine_learning,infrastructure}/<name>/`. Every stack must follow the **6-file GOLD_STANDARD** pattern. This skill teaches you how to add new stacks, fix incomplete ones, and audit them in bulk.

## The 6-file GOLD_STANDARD

Every deployable stack has these files:

| File | Required? | Purpose |
|:--|:--|:--|
| `compose.yaml` | **Yes** | Service definitions. NO `env_file: .env` (Locket injects instead). NO Locket references. |
| `sidecar.yaml` | **Yes** if compose exists | Defines the Locket sidecar + service overrides that mount `/run/secrets/locket/secrets.env` |
| `secrets.env` | **Yes** | Locket template. Every value is `{{ infisical:///<key> }}`. The `--provider=infisical` flag on Locket short form. |
| `pangolin.yaml` | **Yes** if web-facing | 6-label pattern: `pangolin.private-resources.<name>.{name,mode,full-domain,destination-port,protocol,roles[0]}` |
| `blueprint.yaml` | **Yes** | Pangolin routing blueprint — mirror of `pangolin.yaml` |
| `.env.example` | **Yes** | Non-secret defaults for local dev. Copy to `.env.local`. Never commit `.env.local`. |

For non-web stacks (e.g. databases, message brokers) `pangolin.yaml` + `blueprint.yaml` may use `mode: tcp` instead of `mode: http`.

## Adding a new stack

```bash
mkdir -p infrastructure/stacks/<category>/<name>

# 1. Start from an existing stack in the same category
cp -r infrastructure/stacks/tools/linkwarden/* infrastructure/stacks/<category>/<name>/

# 2. Edit compose.yaml
#    - Remove `env_file: .env` lines
#    - Add healthcheck: blocks for every service
#    - Add deploy.resources.limits
#    - Pin image versions (no :latest)
#    - Use the shared `cianfhoghlaim` Docker network

# 3. Edit sidecar.yaml — usually no change unless you have new services

# 4. Edit secrets.env — replace any direct values with {{ infisical:///<key> }}

# 5. Add a .env.example with dev defaults

# 6. Add a Komodo procedure at infrastructure/komodo/procedures/<name>-*.toml
#    (copy from team-stack-up.toml as a template)
```

## Wiring the Pangolin private resource

The 6-label pattern is exact. Use it without exception:

```yaml
# pangolin.yaml
services:
  <service>:
    labels:
      - "pangolin.private-resources.<repo>.name=<Human Name>"
      - "pangolin.private-resources.<repo>.mode=http"   # or "tcp" for non-HTTP
      - "pangolin.private-resources.<repo>.full-domain=<repo>.cianfhoghlaim.ie"
      - "pangolin.private-resources.<repo>.destination-port=<internal_port>"
      - "pangolin.private-resources.<repo>.protocol=http"  # or "tcp"
      - "pangolin.private-resources.<repo>.roles[0]=Member"
```

```yaml
# blueprint.yaml
private-resources:
  <repo>:
    name: "<Human Name>"
    mode: http
    full-domain: "<repo>.cianfhoghlaim.ie"
    destination-port: <internal_port>
    protocol: http
    sites: [arm1-oci]      # only site is arm1-oci
    roles: [Member]
```

## Locket + Infisical pattern

Locket reads `secrets.env` and resolves `{{ infisical:///<key> }}` at container boot. The runtime secret never hits disk.

**Before editing a secrets.env**: confirm the secret exists in Infisical under `dev-baile/<category>/<key>`. If it doesn't, seed it first:

```bash
PROJECT_ID="d18560c0-75d5-436f-a411-0bb758567196"
JWT=$(curl -fsS -X POST "http://localhost:8081/api/v1/auth/universal-auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"clientId\":\"$INFISICAL_CLIENT_ID\",\"clientSecret\":\"$INFISICAL_CLIENT_SECRET\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['accessToken'])")

curl -fsS -X POST "http://localhost:8081/api/v3/secrets/raw/<key>" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d "{\"workspaceId\":\"$PROJECT_ID\",\"environment\":\"dev-baile\",\"secretPath\":\"/<category>\",\"secretValue\":\"<value>\"}"
```

## Auditing existing stacks

The root `scripts/stack-doctor.sh` script audits every stack in the repo. Run it before and after any stack change.

```bash
bun run turbo doctor           # via turbo (fast)
bash scripts/stack-doctor.sh   # direct
bash scripts/stack-doctor.sh --json | jq  # CI / structured output
```

Severity:
- **CRITICAL** — stack cannot deploy (no compose.yaml, no blueprint.yaml, or compose fails to parse)
- **WARNING** — stack deploys but doesn't follow the 5-file pattern
- **INFO** — best-practices polish (`:latest` tags, missing healthchecks, no resource limits)

## Common fixes

### Adding a sidecar to a stack that's missing it

```bash
# 1. Copy the Locket sidecar template
cp infrastructure/stacks/tools/linkwarden/sidecar.yaml infrastructure/stacks/<category>/<name>/sidecar.yaml

# 2. Edit the `services:` block at the bottom to override your main service
# 3. Add the secrets.env with infisical:// references
# 4. Append new infisical env vars to root .infisical.env
```

### Fixing `latest` image tags

Look up the latest stable version on Docker Hub / GitHub Container Registry. Replace `image: foo:latest` with `image: foo:1.2.3`. Document the policy in the stack README.

### Adding healthchecks

For every service with a health endpoint:
```yaml
healthcheck:
  test: ["CMD", "wget", "-q", "-O-", "http://localhost:<port>/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

For services that depend on it, add `depends_on:` with `condition: service_healthy`.

## Cross-references

- `infrastructure/stacks/GOLD_STANDARD.md` — full 5-file pattern with examples
- `infrastructure/SECRETS-MANAGEMENT.md` — Locket + Infisical + mise bootstrap
- `infrastructure/PANGOLIN-SETUP.md` — Pangolin private resource topology
- `infrastructure/stacks/engineering/n8n/sidecar.yaml` — canonical sidecar reference
- `scripts/stack-doctor.sh` — the auditor this skill complements
- `.agents/skills/dagster/SKILL.md` — for the data platform orchestration layer
- `.agents/skills/dlt/SKILL.md` — for the data ingestion layer
- `.agents/skills/docker-compose/SKILL.md` — for compose syntax reference
