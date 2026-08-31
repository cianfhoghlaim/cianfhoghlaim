# Locket — Secrets Management Agent for the bons IaC

> **Status**: Ported from `/stedding/locket` (the upstream local repo) for bons IaC reference.
> The bons IaC uses Locket as the canonical secrets-injection pattern for the bundled `stacks/control-plane/` stack.
> For the full Locket docs, see `https://github.com/bpbradley/locket`.

## What is Locket?

Locket is a small CLI tool (also packaged as a tiny rootless and distroless Docker image) designed to orchestrate secrets for dependent applications and services. Locket works with most secrets providers and coordinates the retrieval of secrets + injection into dependent services.

## Supported Providers (in priority order for the bons IaC)

1. **Infisical** (the bons IaC default) — see `/stedding/locket/docs/providers/infisical.md`
2. 1Password Connect — `/stedding/locket/docs/providers/connect.md`
3. 1Password Service Accounts — `/stedding/locket/docs/providers/op.md`
4. Bitwarden Secrets Manager — `/stedding/locket/docs/providers/bws.md`
5. OpenBao / HashiCorp Vault — `/stedding/locket/docs/providers/bao.md`

> **TIP**: Each provider has its own docker image tag for sidecar mode if a slim version is preferred. `ghcr.io/bpbradley/locket:latest` bundles all providers (~150MB), `ghcr.io/bpbradley/locket:infisical` is just the Infisical provider (~4MB).

## The Infisical Provider (bons IaC default)

### Reference syntax

Infisical does not have a native secret reference syntax. We define a custom URI scheme:

```
infisical:///<secret-key>?env=<env-slug>&path=</path/to/folder>&project_id=<project-uuid>&type=<secret-type[shared|personal]>
```

- The URI prefix disambiguates from other providers
- The secret key is required (encoded in the path component)
- The environment slug, path, project ID, and secret type are optional query parameters overriding defaults

### Setup (one-time)

> **TIP**: Create a Machine Identity on your Infisical Organization — makes it simpler to manage access for Locket if it needs access to multiple projects.

1. Create an Infisical Account
2. Create a project, and add secrets to it
3. Create a Machine Identity for Locket:
   - Navigate to Organization > Access Control > Machine Identities
   - Select **Create Organization Machine Identity**
   - Give it a name, and assign permissions (e.g. `No Access` if you only need client_credentials)
4. In the Universal Auth tab, select **Add Client Secret**. Give it a name, and any TTL or usage limits. Select **Create**
5. Take note of the `Client Secret` and keep it in a safe location (it will not be shown again)
6. Make sure to associate this `Client Secret` with the `Client ID` of the Universal Auth instance
7. Add any projects that you want Locket to have access to

### Example: Sidecar Configuration (the bons IaC pattern)

The bons IaC's `stacks/control-plane/secrets.env` uses the Infisial provider via Locket sidecar:

```sh
locket inject --provider infisical \
  --infisical-client-secret=file:/run/secrets/infisical_secret \
  --infisical-client-id=c74d3ea3-d189-43f0-96bb-649fa27bee30 \
  --infisical-default-environment=dev \
  --infisical-default-project-id=f3cff583-b74b-4804-b9d3-db8b68885236 \
  --map /templates:/run/secrets/locket
```

The corresponding `docker-compose.yml` (the bons IaC's standard locket sidecar):

```yaml
services:
  app:
    image: my-app:latest
    depends_on:
      locket:
        condition: service_healthy
    volumes:
      - /run/secrets/locket:/run/secrets/locket:ro

  locket:
    image: ghcr.io/bpbradley/locket:infisical
    user: "1000:1000"
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    container_name: locket-app
    secrets:
      - infisical_secret
    volumes:
      - ./templates:/templates:ro
      - out-app:/run/secrets/locket
    command:
      - "--provider=infisical"
      - "--infisical-client-secret=file:/run/secrets/infisical_secret"
      - "--infisical-client-id=c74d3ea3-d189-43f0-96bb-649fa27bee30"
      - "--infisical-default-environment=dev"
      - "--infisical-default-project-id=f3cff583-b74b-4804-b9d3-db8b68885236"
      - "--map=/templates:/run/secrets/locket"

secrets:
  infisical_secret:
    file: /etc/tokens/infisical

volumes:
  out-app:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
      o: "uid=1000,gid=1000,mode=0700"
```

## Sidecar Modes

| Mode | Description | Use case |
|:--|:--|:--|
| `watch` | Materialize all secrets once, then watch for changes on templates + reinject. Long-running. | **Docker Default**. Use in `docker-compose.yml`. |
| `one-shot` | Materialize all secrets once and exit. | CLI tool mode. |
| `park` | Inject once then park (stay alive for healthcheck). | Use in `docker-compose.yml` when the app needs a healthcheck target. |
| `exec` | (Provider mode) Inject secrets directly into a dependent process's env, then exec it. | Docker CLI plugin mode. |
| Volume Driver | Inject secrets as tmpfs volumes managed by the Docker daemon. | (Optional) Docker Engine plugin mode. |

## Bons IaC Integration

The bons IaC uses Locket in 2 ways:

1. **IaC's own use** — `iac:bootstrap-locket-binary` downloads the binary to `~/.local/bin/locket` for the bons IaC's own secret materialization (e.g. for dev)
2. **Sidecar in `stacks/control-plane/`** — every service in the bundled control-plane stack has a Locket sidecar that materializes the service's secrets from Infisical

The canonical env-var names (validated by `bun run validate-stacks`):
- `INFISICAL_URL` — Infisical server URL (default: `https://infisical.cianfhoghlaim.ie`)
- `INFISICAL_CLIENT_ID` — bons-iac machine identity client_id
- `INFISICAL_CLIENT_SECRET` — bons-iac machine identity client_secret
- `INFISICAL_PROJECT_ID` — `f3cff583-b74b-4804-b9d3-db8b68885236` (the dev-baile project)
- `INFISICAL_DEFAULT_ENVIRONMENT` — `dev`
- `INFISICAL_DEFAULT_PATH` — `/`

## How the bons IaC uses the Infisical provider

The bons IaC's `iac/clients/infisical-rest.ts` is a direct-REST replacement for the buggy `@infisical/sdk@5.0.2`. The bons IaC uses this for:

- The Pulumi IaC scripts (`iac/pulumi/oci/{setup,deploy}.ts`) that save Cloudflare creds + server info to Infisical
- The `iac:rotate-auth` 3-way credential rotation (Pangolin API key + Komodo password + Infisical self-bootstrap)
- The `iac:bootstrap-infisical` first-admin + 8 machine identity seeding

The bons IaC always uses **form-encoded body** for the `/api/v1/auth/universal-auth/login` endpoint (NOT JSON — the SDK was sending JSON which the server rejects).

## Validation

`bun run validate-stacks` (the stack-doctor turbo task) checks every stack under `bonneagar/stacks/<name>/` for:
- The presence of a 6-file GOLD_STANDARD contract
- The use of `--provider=infisical` in `sidecar.yaml`
- The use of the canonical `INFISICAL_*` env-var names

A stack that diverges fails the build.

## Cross-references

- `/stedding/locket` — the upstream local repo (development source of truth)
- `/stedding/locket/README.md` — the upstream README
- `/stedding/locket/docs/CONFIGURATION.md` — full configuration reference
- `/stedding/locket/docs/inject.md` — inject command reference (the bons IaC's mode of use)
- `/stedding/locket/docs/providers/infisical.md` — full Infisical provider reference
- `iac/clients/infisical-rest.ts` — the bons IaC's direct-REST Infisical client
- `iac/commands/bootstrap-infisical.ts` — uses Locket indirectly via Infisical

## Operator handoff

```bash
# 1. Download locket binary locally (1-time, for IaC use)
cd ${CIANFHOGHLAIM_ROOT:-/Users/cianmacandeisigh/dev/cianfhoghlaim}/bonneagar
bun run iac:bootstrap-locket-binary

# 2. Verify
locket --version
# Expected: locket 0.4.0

# 3. Test against the production Infisical
INFISICAL_URL=https://infisical.cianfhoghlaim.ie \
INFISICAL_CLIENT_ID=$POCKETID_BONS_IAC_CLIENT_ID \
INFISICAL_CLIENT_SECRET=$POCKETID_BONS_IAC_CLIENT_SECRET \
INFISICAL_PROJECT_ID=f3cff583-b74b-4804-b9d3-db8b68885236 \
INFISICAL_DEFAULT_ENVIRONMENT=dev \
locket inject --provider=infisical --map=/tmp/templates:/tmp/out --mode=one-shot
```
