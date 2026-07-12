# Komodo Infrastructure

GitOps-managed infrastructure using Komodo for container orchestration.

## Architecture

This environment implements a decoupled control plane architecture using **Komodo v2.2** and **Pangolin 1.18**:

1. **MacBook (Control Plane):** Runs **Komodo Core**, managing the database, states, and the web UI.
2. **Oracle Cloud Free Tier (Workloads):** Runs **Komodo Periphery**, an execution agent that reports back to Core.
3. **Pangolin Tunnels:** The Oracle instance runs **Newt** (Pangolin client) to securely tunnel out to the MacBook. Oracle Periphery connects back to the Core's private HTTPS endpoint via Pangolin multi-site HA and Private Resources.

## Secrets Management

Secrets are managed via **Infisical** and injected using **Locket** (`ghcr.io/bpbradley/locket:infisical`). 
Locket acts as a sidecar that mounts ephemeral memory (`tmpfs`) to provide runtime secrets strictly to the Docker containers without writing to disk. Development scripts wrap `docker compose` with `locket exec` for CLI injection.

*No legacy passkeys or Infisical API tokens are stored in the git repository or host variables.*

## Requirements

- Komodo Core 2.x
- Periphery v2 pinned docker tags (`ghcr.io/moghtech/komodo-periphery:2`)
- Infisical Secret Manager with Universal Auth Client Secret.
- Pangolin 1.18+ (HTTPS Private Resources)

## Directory Consolidation

*   `stacks/`: All stack definitions in canonical TOML format (17 files, ~20 stack entries)
*   `procedures/`: All procedure TOML files (56 files)
*   `servers/`: Server definitions (2 hosts: arm1-oci + bunchloch)
*   `sites/`: Per-host bootstrap (OCI + MacBook)

**Note (2026-06-24):** The 5 legacy `.ts` scripts in
`infrastructure/legacy/` (`ansible.ts`, `cloudflare-dns.ts`,
`pangolin-setup.ts`, `servers.ts`, `taisce-deploy.ts`) have
been **deleted** in round 7 of the multi-quadrant refactor
plan. They were already replaced by `infrastructure/iac/komodo/*.ts`
+ the 56 procedures in `infrastructure/komodo/procedures/`. See
`openspec/changes/archive/2026-06-24-infrastructure-stack-doctor-v1/`.
*   `resource-syncs/`: GitOps resource sync from Forgejo to Komodo Core
*   `../ansible/`: Main infrastructure provisioning automation

## Deploy the 6 Team-Workflow Stacks

```bash
# 1. Ensure Infisical is up at infisical.cianfhoghlaim.ie
cd infrastructure/infisical
docker compose -f docker-compose.yaml -f sidecar.yaml up -d

# 2. Verify PlanetScale "bunchloch" DB is reachable
PGPASSWORD="$PLANETSCALE_PASSWORD" psql -h eu-west-3.pg.psdb.cloud -p 5432 \
  -U "$PLANETSCALE_USERNAME" -d bunchloch -c "SELECT schema_name FROM information_schema.schemata;"

# 3. Run schema bootstrap (idempotent)
bash scripts/setup-planetscale.sh

# 4. Deploy via Komodo (in dependency order)
komodo-cli deploy vikunja --server arm1-oci
komodo-cli deploy cal-diy --server arm1-oci
komodo-cli deploy n8n --server arm1-oci
komodo-cli deploy paperless-ngx --server arm1-oci
komodo-cli deploy glance --server arm1-oci
komodo-cli deploy changedetection --server arm1-oci
komodo-cli deploy bytebase --server arm1-oci

# 5. Seed n8n workflows + Vikunja projects
docker run --rm --network host ghcr.io/cianfhoghlaim/vikunja-seed:latest
docker run --rm --network host ghcr.io/cianfhoghlaim/n8n-init:latest

# 6. Verify
curl https://vikunja.cianfhoghlaim.ie/api/v1/info
curl https://n8n.cianfhoghlaim.ie/healthz
curl https://calcom.cianfhoghlaim.ie/api/v2/ping
curl https://glance.cianfhoghlaim.ie/
```

### CI/CD (GitHub Actions)
On push to main, Dagger CI/CD runs `test-all` → `build-images` → pushes to `ghcr.io/cianfhoghlaim`.
On manual approval, deploys to production via `dagger call deploy --approved=true`.

### CI/CD (Forgejo Actions)
Mirrored at `.forgejo/workflows/`. GitHub Actions added per Phase F to give dual-runtime coverage.
