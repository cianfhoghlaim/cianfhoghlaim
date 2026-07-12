# Locket / Pangolin / Komodo - Deployment Gold Standard

When converting a repository to our standard deployment format, generate the following 5 files in `infrastructure/stacks/<repo_name>/`:

## 1. compose.yaml

Base compose file containing the application services.

**Rules:**
- MUST NOT contain any Locket references natively
- MUST NOT contain `env_file: .env` (secrets come from Locket via `sidecar.yaml`)
- Use `${VAR:-default}` for non-secret env vars with sensible defaults
- Use `depends_on: locket: condition: service_healthy` only in `sidecar.yaml`, NOT here
- Define all non-secret environment variables inline in `environment:` blocks

**Local dev workflow:** Create a `.env.example` with defaults. Developers copy to `.env.local`:
```bash
cp .env.example .env.local
# Edit .env.local with dev values
docker compose up -d
```

**Production workflow (via Komodo or CLI):** No `.env` file needed. Locket + sidecar.yaml inject secrets:
```bash
docker compose -f compose.yaml -f sidecar.yaml up -d
```

## 2. sidecar.yaml

The Locket sidecar definition and service override. Uses the **Infisical provider** (not 1Password Connect):

```yaml
services:
  locket:
    image: ghcr.io/bpbradley/locket:infisical
    container_name: ${COMPOSE_PROJECT_NAME:-stack}-locket
    restart: unless-stopped
    user: "65532:65532"
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    command:
      - "--provider=infisical"
      - "--infisical-client-id=$${INFISICAL_CLIENT_ID}"
      - "--infisical-client-secret=file:/run/secrets/infisical_secret"
      - "--map=/templates:/run/secrets/locket"
      - "--mode=${LOCKET_MODE:-watch}"
    secrets:
      - infisical_secret
    volumes:
      - ./secrets.env:/templates/secrets.env:ro
      - stack-secrets:/run/secrets/locket
    healthcheck:
      test: ["CMD", "/locket", "healthcheck"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 5s
    networks:
      - stack

  # Override each service that needs secrets
  main-service:
    depends_on:
      locket:
        condition: service_healthy
    volumes:
      - stack-secrets:/run/secrets/locket:ro
    env_file:
      - /run/secrets/locket/secrets.env

secrets:
  infisical_secret:
    file: $${INFISICAL_SECRET_FILE:-../../infisical_secret}

volumes:
  stack-secrets:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
      o: uid=65532,gid=65532,mode=700
```

**Important for self-hosted Infisical:** You MUST include `--infisical-url`, `--infisical-default-environment`, and `--infisical-default-project-id` flags. Without these, Locket defaults to `https://app.infisical.com` (Infisical Cloud) which will fail against a self-hosted instance.

**Template format**: Use `{{ infisical:///<key> }}` (triple-slash) for secrets stored at the root level, or `{{ infisical:///<key>?path=/folder }}` to specify a folder path. Environment and project ID should come from the CLI flags, not from individual template references.

**Locket v0.17.3 caveat**: Template substitution for `?path=` query parameters may not resolve correctly. If Locket's `policy=passthrough` fallback copies raw templates to the output, use the `render-secrets.py` helper script at `scripts/render-secrets.py` to generate resolved `.env` files directly from the Infisical API. See `scripts/render-secrets.py` for usage.

## 3. secrets.env

Locket template file using Infisical URI references. The reference syntax is:

```
{{ infisical:///<secret-key>?env=<env-slug>&project_id=<project-uuid> }}
```

The simplest form (uses defaults from the Locket configuration):
```env
# =============================================================================
# <STACK_NAME> - Locket Secrets Template
# =============================================================================
# These infisical:// references are resolved by Locket at runtime.
# Vault: dev-baile

DATABASE_URL={{ infisical:///database_url }}
POSTGRES_PASSWORD={{ infisical:///postgres_password }}
API_KEY={{ infisical:///api_key }}
```

With explicit project and environment:
```env
DATABASE_URL={{ infisical:///database_url?env=prod&project_id=abc123-def456 }}
```

## 4. pangolin.yaml

Pangolin labels for service discovery. **Private resources are the default** — use zero-trust access via Pangolin client (WireGuard tunnel).

### Private resource (default for internal services):

```yaml
services:
  main-service:
    labels:
      - "pangolin.private-resources.<repo_name>.name=<Repo Name>"
      - "pangolin.private-resources.<repo_name>.mode=http"
      - "pangolin.private-resources.<repo_name>.full-domain=<repo>.cianfhoghlaim.ie"
      - "pangolin.private-resources.<repo_name>.destination-port=<Internal Port>"
      - "pangolin.private-resources.<repo_name>.protocol=http"
      - "pangolin.private-resources.<repo_name>.roles[0]=Member"
```

### Public resource (only for services that need internet exposure):

```yaml
services:
  main-service:
    labels:
      - "pangolin.public-resources.<repo_name>.name=<Repo Name>"
      - "pangolin.public-resources.<repo_name>.full-domain=<repo>.cianfhoghlaim.ie"
      - "pangolin.public-resources.<repo_name>.protocol=http"
      - "pangolin.public-resources.<repo_name>.targets[0].method=http"
      - "pangolin.public-resources.<repo_name>.targets[0].port=<Internal Port>"
```

**Guidelines:**
- Most services should be **private** (databases, ML tools, admin panels, internal APIs)
- Only make services public if they need internet exposure (git servers, auth providers, admin dashboards accessed without VPN)
- Public services should add SSO auth via `auth:` section
- Private resources require users to connect via Pangolin client (Olm) and are granted access via roles

### Services that should stay PUBLIC:
- Forgejo (`git.cianfhoghlaim.ie`) — public git access
- Pocket ID (`auth.cianfhoghlaim.ie`) — SSO authentication provider
- Pangolin admin — network management
- Dozzle — container log viewer (debugging)
- S3 APIs (Garage, Lakehouse S3) — programmatic access needs public endpoint

## 5. blueprint.yaml

Pangolin routing blueprint. **Private resources are the default.**

### Private resource blueprint (default):

```yaml
private-resources:
  <repo_name>:
    name: "<Repo Name>"
    full-domain: "<repo>.cianfhoghlaim.ie"
    mode: http
    destination-port: <Internal Port>
    protocol: http
    sites:
      - arm1-oci
    roles:
      - Member
```

### Public resource blueprint (only for internet-facing services):

```yaml
public-resources:
  <repo_name>:
    name: "<Repo Name>"
    full-domain: "<repo>.cianfhoghlaim.ie"
    protocol: "http"
    auth:
      sso-enabled: true
      sso-roles:
        - Member
    targets:
      - site: "arm1-oci"
        hostname: "<repo_name>-main"
        method: "http"
        port: <Internal Port>
```

### TCP resource blueprint (for databases, brokers):

```yaml
private-resources:
  kafka-broker:
    name: "Kafka Broker"
    mode: host
    destination: "127.0.0.1"
    tcp-ports: "9094"
    sites:
      - arm1-oci
    roles:
      - Member
```

## Deployment Workflows

### Local Development

```bash
cp .env.example .env.local
# Edit .env.local with dev values (no real secrets needed)
docker compose up -d
```

### Production via CLI (with Locket)

```bash
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Production via Komodo

Komodo deploys using `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from Infisical at runtime. Pangolin labels are applied via `pangolin.yaml`.

Key points for Komodo:
- **Don't add `.env` file in Komodo UI** — secrets come from Locket via `sidecar.yaml`
- **Don't configure secrets in Komodo** — Locket + Infisical handles this
- Komodo just needs `compose.yaml` + `sidecar.yaml` as compose files
- Environment variables with `${VAR:-default}` get defaults from the compose file

## Checklist

When processing a repo:
1. Identify its services, ports, and required environment variables from its original `docker-compose.yml`
2. Map required secrets into `secrets.env` using `{{ infisical:///<key> }}` references
3. Create the 5 standard files: `compose.yaml`, `sidecar.yaml`, `secrets.env`, `pangolin.yaml`, `blueprint.yaml`
4. Create `.env.example` with non-secret defaults for local development
5. Make services **private by default** in `pangolin.yaml` and `blueprint.yaml`
6. Only mark services public if they genuinely need internet exposure
7. NEVER commit `.env` files, real secrets, or the `infisical_secret` token file