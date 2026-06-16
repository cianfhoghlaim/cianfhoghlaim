# Pangolin + Komodo Convergence Architecture — End-to-End Runbook

**Last verified:** 2026-06-16
**Stack version:** Pangolin 1.19.2 EE + Komodo Core 2 + Komodo Periphery 2-dev
**Convergence model:** MacBook (bunchloch) = control plane; arm1-oci = edge + worker

---

## 1. Topology

```
                                    ┌──────────────────────────┐
                                    │      Oracle Cloud        │
                                    │      arm1-oci (edge)     │
                                    │                          │
                  Public Internet  │  ┌────────────────────┐  │
                                    │  │ Pangolin EE        │  │  Pangolin + Gerbil
                                    │  │  (1.19.2 EE)       │  │  + Traefik + Pocket ID
                                    │  │ :3001 (API)        │  │  + TinyAuth + Komodo
                                    │  │ :80/:443 (L7)      │  │  Periphery (8120)
                                    │  └────────┬───────────┘  │
                                    │           │              │
                                    │  ┌────────▼───────────┐  │
                                    │  │ Gerbil (exit-node) │  │
                                    │  │ :51820/udp (WG)    │  │
                                    │  │ :3004 (hole punch) │  │
                                    │  └────────┬───────────┘  │
                                    └───────────┼──────────────┘
                                                │
                                                │  WireGuard tunnel
                                                │  (10.0.1.x/24)
                                                │
                                    ┌───────────▼──────────────┐
                                    │      MacBook (bunchloch) │
                                    │                          │
                                    │  ┌────────────────────┐  │
                                    │  │ Newt (tunnel)      │  │  Pangolin Newt
                                    │  │ wg0 → 10.0.1.2/24  │  │  + Locket sidecar
                                    │  └────────────────────┘  │
                                    │  ┌────────────────────┐  │
                                    │  │ Komodo Core        │  │  Orchestration
                                    │  │ :9120 (UI + API)   │  │  + FerretDB v2
                                    │  └────────┬───────────┘  │
                                    │           │              │
                                    │  ┌────────▼───────────┐  │
                                    │  │ Komodo Periphery   │  │  Periphery (8120)
                                    │  │ docker.sock        │  │  + Locket sidecar
                                    │  └────────────────────┘  │
                                    │                          │
                                    │  [Stacks managed by Komodo]
                                    │  ┌────────────────────┐  │
                                    │  │ oideachais-*       │  │
                                    │  │ litellm / dagster  │  │
                                    │  │ cognee / lancedb   │  │
                                    │  │ ...                │  │
                                    │  └────────────────────┘  │
                                    └──────────────────────────┘

                          Pangolin Integrations API
                          ┌─────────────────────────┐
                          │ Bearer token (org-scoped│
                          │ or root-scoped for EE)  │
                          │                         │
                          │ POST   /api/v1/...      │
                          │ GET    /api/v1/...      │
                          │ PATCH  /api/v1/...      │
                          │ DELETE /api/v1/...      │
                          └─────────────────────────┘
                          Swagger: https://pangolin.cianfhoghlaim.ie/v1/docs

                    Komodo TypeScript Client
                    ┌─────────────────────────┐
                    │ komodo_client SDK       │
                    │                         │
                    │ read / write / execute  │
                    │ stack / server / proc   │
                    └─────────────────────────┘
                    Docs: https://komo.do/docs/clients
```

## 2. Bootstrap Order

The 9 phases below must be executed in order — each phase depends on
artefacts created by the previous one.

| # | Phase | Host | Tool |
|:-:|:--|:--|:--|
| 1 | Pulumi: provision OCI + Cloudflare | mbp | `pulumi up` |
| 2 | Infisical: provision vault + secrets | mbp | `bun run scripts/init-vault.ts` |
| 3 | Pangolin + Gerbil + Traefik + Pocket ID + TinyAuth | arm1-oci | `docker compose` |
| 4 | Komodo Core + FerretDB + Postgres | mbp | `docker compose` |
| 5 | Komodo Periphery (mbp) | mbp | `docker compose` |
| 6 | Komodo Periphery (arm1-oci) | arm1-oci | `docker compose` |
| 7 | Pangolin Newt (mbp) | mbp | `docker compose` |
| 8 | Komodo stacks via TypeScript SDK | mbp | `bun run` |
| 9 | Pangolin resources via Integrations API | mbp | `bun run` |

## 3. Phase Details

### Phase 1 — Pulumi bootstrap

```bash
# 1.1 OCI: create arm1-oci instance, configure security lists
cd infrastructure/pulumi/oci
pulumi up

# 1.2 Cloudflare: create DNS-01 API token + WAF rules
cd ../cloudflare
# Set config: cloudflare:apiToken (account-level) + cloudflare:accountId
pulumi config set --secret cloudflare:apiToken "cfat_xxx"
pulumi config set cloudflare:accountId "08e219e57d3edac2b14da839892b2373"
pulumi up
# Outputs: cloudflareDnsApiToken, accountId, zoneId
```

**Required Cloudflare token permissions:**
- `Zone:DNS:Edit` (on cianfhoghlaim.ie zone)
- `Zone:Zone:Read`
- `Account:Account Settings:Read`

The Pulumi stack writes the token to a Pulumi secret. To retrieve:
```bash
pulumi stack output cloudflareDnsApiToken
```

### Phase 2 — Infisical vault provisioning

```bash
# 2.1 Get machine identity from Infisical UI:
#     Org Settings → Machine Identities → + New
#     Name: locket-bunchloch
#     Grant: Read+Write on dev-baile
#     Copy client_id + client_secret

# 2.2 Set env vars (or rely on mise hooks)
export INFISICAL_CLIENT_ID=<client_id>
export INFISICAL_CLIENT_SECRET=<client_secret>
export INFISICAL_PROJECT_ID=f3cff583-b74b-4804-b9d3-db8b68885236
export INFISICAL_URL=https://infisical.cianfhoghlaim.ie

# 2.3 Sync .env → vault
# The init-vault.ts script reads .env values and creates secrets at the
# paths specified in .infisical.env (e.g. infisical://dev-baile/pangolin/postgres_password
# becomes a secret at dev-baile/pangolin/postgres_password).
bun run scripts/init-vault.ts

# 2.4 Verify (should return 3 secrets)
curl -sS "https://infisical.cianfhoghlaim.ie/api/v1/secrets?env=dev-baile&path=/pangolin" \
  -H "Authorization: Bearer $INFISICAL_TOKEN"
```

**Infisical URI format** (locket `{{ infisical://... }}` template):

| Template | Resolves to |
|:--|:--|
| `{{ infisical://dev-baile/pangolin/server_secret }}` | secret `server_secret` at path `/pangolin` in env `dev-baile` |
| `{{ infisical://dev-baile/pangolin/postgres_password }}` | secret `postgres_password` at path `/pangolin` |
| `{{ infisical:///server_secret?path=/pangolin }}` | alt syntax: project_id from `--infisical-default-project-id`, env from `--infisical-default-environment` |
| `{{ infisical://dev-baile/pangolin/newt-arm1-oci/id }}` | per-host newt creds |

### Phase 3 — Pangolin stack on arm1-oci

```bash
# 3.1 Sync stack from mbp → arm1-oci
rsync -avz --delete \
  -e "ssh -i ~/.ssh/oci-arm1" \
  infrastructure/stacks/infrastructure/pangolin/ \
  ubuntu@140.238.96.148:/opt/pangolin/

# 3.2 SSH to arm1-oci, then:
ssh oci.arm1
cd /opt/pangolin

# 3.3 Verify .env has all required vars
#    (POSTGRES_PASSWORD, SERVER_SECRET, POCKETID_ENCRYPTION_KEY,
#     CLOUDFLARE_DNS_API_TOKEN, POCKETID_CLIENT_ID, POCKETID_CLIENT_SECRET)
cat .env

# 3.4 Bring up
docker compose up -d
docker compose ps

# 3.5 Verify traefik has the wildcard cert
docker exec traefik ls -la /letsencrypt/lego/certificates/
# Expect: _.cianfhoghlaim.ie.crt + _.cianfhoghlaim.ie.key

# 3.6 Test the public endpoint
curl -I https://pangolin.cianfhoghlaim.ie
# Expect: HTTP/2 200 or 302
```

**Wildcard cert note:**
The lego cert at `/opt/pangolin/config/letsencrypt/lego/` was issued via
Cloudflare DNS-01 in a previous session. If you need to re-issue:

```bash
docker run --rm \
  -v /opt/pangolin/config/letsencrypt/lego:/root/.lego \
  -e CLOUDFLARE_DNS_API_TOKEN=$CLOUDFLARE_DNS_API_TOKEN \
  goacme/lego:latest \
  --email ops@cianfhoghlaim.ie \
  --dns cloudflare \
  --accept-tos \
  --key-type ec256 \
  run \
  -d 'cianfhoghlaim.ie' \
  -d '*.cianfhoghlaim.ie'
```

### Phase 4 — Komodo Core on mbp

```bash
# 4.1 Sync stack
rsync -avz --delete \
  infrastructure/stacks/infrastructure/komodo/ \
  ~/.config/komodo/

# 4.2 Generate the JWT + passkey + DB password
KOMODO_JWT_SECRET=$(openssl rand -hex 32)
KOMODO_PASSKEY=$(openssl rand -hex 32)
KOMODO_INIT_ADMIN_PASSWORD=$(openssl rand -hex 16)
KOMODO_DATABASE_PASSWORD=$(openssl rand -hex 24)

# 4.3 Write .env (DO NOT COMMIT)
cat > ~/.config/komodo/.env <<EOF
KOMODO_DATABASE_USERNAME=komodo
KOMODO_DATABASE_PASSWORD=$KOMODO_DATABASE_PASSWORD
KOMODO_JWT_SECRET=$KOMODO_JWT_SECRET
KOMODO_PASSKEY=$KOMODO_PASSKEY
KOMODO_INIT_ADMIN_USERNAME=ciansedai
KOMODO_INIT_ADMIN_PASSWORD=$KOMODO_INIT_ADMIN_PASSWORD
KOMODO_HOST=https://komodo.cianfhoghlaim.ie
EOF

# 4.4 Place the locket machine-identity secret
mkdir -p ~/.config/komodo/secrets
cp /path/to/infisical_secret ~/.config/komodo/secrets/

# 4.5 Bring up Core + FerretDB + Postgres + Locket
cd ~/.config/komodo
docker compose -f compose.yaml -f sidecar.yaml up -d
docker compose ps

# 4.6 Test
curl -s http://localhost:9120/health
# Expect: {"status":"healthy"}
```

### Phase 5 — Komodo Periphery (mbp)

```bash
# 5.1 Periphery uses the same compose + sidecar
cd ~/.config/komodo
docker compose -f compose.yaml -f sidecar.yaml -f periphery.yaml up -d
# (the `periphery.yaml` override adds a `periphery` service)

# 5.2 In Komodo Core UI (http://localhost:9120):
#     Servers → + New
#     Name: bunchloch
#     Address: (leave blank = periphery connects outbound)
#     Passkey: $KOMODO_PASSKEY
#     Save

# 5.3 Verify: the server should appear as "online" in Komodo UI
```

### Phase 6 — Komodo Periphery (arm1-oci)

```bash
# 6.1 SSH to arm1-oci
ssh oci.arm1
mkdir -p /etc/komodo
cd /etc/komodo

# 6.2 Sync compose files
rsync -avz mbp:/Users/cianmacandeisigh/dev/kings_college_galway/infrastructure/stacks/infrastructure/komodo/ .

# 6.3 Write .env (same passkey as Core, different DB pw if desired)
# 6.4 Place infisical_secret at /opt/komodo/secrets/infisical_secret

# 6.5 Bring up Periphery only (no Core on arm1-oci)
docker compose -f periphery.yaml -f sidecar.yaml up -d

# 6.6 In Komodo Core UI:
#     Servers → + New
#     Name: arm1-oci
#     Passkey: $KOMODO_PASSKEY
#     Save
```

### Phase 7 — Pangolin Newt (mbp)

```bash
# 7.1 In Pangolin UI: https://pangolin.cianfhoghlaim.ie
#     Sites → + New
#     Name: bunchloch
#     Type: WireGuard (newt)
#     Click "Generate Newt Credentials"
#     Copy NEWT_ID + NEWT_SECRET
#     Save the Site, then click "Add" → "Create Exit Node Connection"
#     (The newt tunnel uses the global gerbil as exit node.)

# 7.2 Add the credentials to Infisical
#     Path: pangolin/newt-bunchloch/{id, secret}
#     (The locket sidecar on the newt will resolve them.)

# 7.3 Place the stack on mbp
mkdir -p ~/.config/pangolin-newt
cd ~/.config/pangolin-newt
rsync -avz .../infrastructure/stacks/infrastructure/pangolin/{newt.yaml,newt.sidecar.yaml,newt.secrets.env} .
# Remove the misplaced sidecar (we don't want locket unless Infisical KMS is healthy)
# Actually keep the locket pattern, it works.
# If KMS is broken, fall back to: export NEWT_ID + NEWT_SECRET in .env, skip sidecar

# 7.4 Place infisical_secret
mkdir -p ~/.config/pangolin-newt/secrets
cp /path/to/infisical_secret ~/.config/pangolin-newt/secrets/

# 7.5 Bring up
docker compose -f newt.yaml -f newt.sidecar.yaml up -d
docker compose ps
docker logs newt
# Expect: "Client connectivity setup. Ready to accept connections from clients!"
#         + an actual wg interface brought up (e.g. `ip link show newt` in container)

# 7.6 Verify tunnel
docker exec newt ip link show
# Expect: `newt` interface with state UP

# 7.7 Test from arm1-oci newt's perspective: ping mbp's docker network
#     (run in arm1-oci newt)
docker exec newt ping -c 1 10.0.1.2
# Expect: 64 bytes from 10.0.1.2
```

**Newt common gotchas:**

- **OrbStack TUN issue**: `/dev/net/tun` may not be available in the
  container's network namespace. Check with `docker exec newt ls -la /dev/net/tun`.
  If missing, add `--privileged` to the docker run.
- **Newt version pinning**: `fosrl/newt:latest` auto-updates. Pin to a
  specific version (e.g. `1.13.0`) for reproducibility.
- **Capability requirements**: newt needs `NET_ADMIN`, `NET_RAW`, and
  `SYS_MODULE` to bring up the wg interface. OrbStack's default
  capability stripping will silently fail.
- **Name resolution**: the newt uses `pangolin.cianfhoghlaim.ie` to reach
  Pangolin. If running on the same host as Pangolin, use
  `host.docker.internal`.

### Phase 8 — Deploy stacks via komodo_client TypeScript SDK

```typescript
// scripts/deploy-stacks.ts
import { KomodoClient } from "@komodo_client/sdk";

const core = new KomodoClient({
  url: "http://localhost:9120",
  // Use apiKey + apiSecret (from Komodo Core → User → API Keys)
  apiKey: process.env.KOMODO_API_KEY!,
  apiSecret: process.env.KOMODO_API_SECRET!,
});

// 1. Create or update a server (idempotent)
await core.execute("UpsertServer", {
  name: "arm1-oci",
  config: {
    address: "",
    enabled: true,
    // public_key from komodo-periphery container's first-boot log
    public_key: "MCowBQYDK2VuAyEAQbp8iLZRZQN+fpIU0hXWySQq+V4iCVixdDAR+zNCkhE=",
  },
});

// 2. Create or update a stack
await core.execute("UpsertStack", {
  name: "pangolin-core",
  server_id: "arm1-oci",
  run_directory: "/opt/pangolin",
  config: {
    file_paths: ["compose.yaml", "sidecar.yaml"],
    environment: "PANGOLIN_ENDPOINT=https://pangolin.cianfhoghlaim.ie\nLOCKET_MODE=watch",
  },
});

// 3. Deploy the stack
const deploy = await core.execute("DeployStack", {
  stack: "pangolin-core",
  server: "arm1-oci",
});
console.log("Deploy update_id:", deploy);

await new Promise<void>((resolve, reject) => {
  const interval = setInterval(async () => {
    const status = await core.read("GetStackDeployment", {
      stack: "pangolin-core",
      server: "arm1-oci",
    });
    if (status.status === "Complete") { clearInterval(interval); resolve(); }
    if (status.status === "Failed")    { clearInterval(interval); reject(); }
  }, 5000);
});
```

### Phase 9 — Pangolin private resources via Integrations API

```typescript
// scripts/create-pangolin-resources.ts
const PANGOLIN_URL = "https://pangolin.cianfhoghlaim.ie";
const API_KEY = process.env.PANGOLIN_API_KEY!;

async function createResource(opts: {
  orgId: string; siteId: string;
  name: string; subdomain: string;
  destination: string; destinationPort: number;
}) {
  const r = await fetch(`${PANGOLIN_URL}/api/v1/org/${opts.orgId}/site/${opts.siteId}/resource`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: opts.name,
      subdomain: opts.subdomain,
      domain_id: "<domain-id-for-cianfhoghlaim.ie>",
      protocol: "http",
      // For HTTP services, target the docker container by name + port.
      // The newt must be able to resolve the docker container hostname.
      // If newt is on mbp, the docker container must be on mbp.
      // If newt is on arm1-oci, the docker container must be on arm1-oci.
      //   The format is `<container-name>:<port>`.
      //   For services on the same host as newt, the newt can resolve
      //   the container by docker DNS.
      // For multi-host, you must use the newt's exit-node IP scheme.
      // The "destination" field is interpreted by the pangolin server
      // and the resulting URL is sent to the newt for connection.
      // Format: host:port or ip:port.
      http: true,
    }),
  });
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return await r.json();
}

// Example: komodo.cianfhoghlaim.ie → komodo-core:9120 (mbp)
await createResource({
  orgId: "cianfhoghlaim",
  siteId: "bunchloch",
  name: "Komodo Core",
  subdomain: "komodo",
  destination: "komodo-core:9120",
  destinationPort: 9120,
});
```

**Key gotchas:**

- **OrgId vs SiteId**: `siteId` is the Pangolin site that hosts the
  newt. The newt must be able to resolve the destination hostname.
- **Resource networking**: the destination is interpreted by the newt.
  If newt is on mbp and the service is on arm1-oci, the newt cannot
  reach it (without a second newt on arm1-oci).
- **Per-resource role**: each resource has a `role` that gates access
  via Pocket ID. Set `Member` for dev, `Admin` for management.

## 4. Known Gotchas (Reference)

| Symptom | Cause | Fix |
|:--|:--|:--|
| Locket says "invalid URI" | `{{ infisical://path/name }}` with extra `/` | Use `{{ infisical:///name?path=/folder }}` form |
| Locket says "401 Unauthorized" | KMS blind index broken | Wipe infisical-db, restore from backup, or re-init KMS |
| Pangolin 404 for `*.cianfhoghlaim.ie` | Traefik has no wildcard cert | Run lego DNS-01 with `CLOUDFLARE_DNS_API_TOKEN` |
| Newt stuck on "Tunnel connection established" | wg interface never comes up | Check `/dev/net/tun`, add `--privileged` + `cap_add: NET_ADMIN` |
| Komodo: "Address already in use: 8120" | Periphery already running | `docker compose -p komodo-periphery down` |
| OCI: "Out of host capacity" | Free tier limits hit | Destroy a 2nd instance or wait for upgrade |
| Pulumi: "Authentication error (10000)" | CF token lacks permission | Use `Account:Account Settings:Read` + `Zone:DNS:Edit` |

## 5. Disaster Recovery

| Disaster | Recovery | Time |
|:--|:--|:--|
| Infisical KMS broken | Re-initialize via DB wipe (KMS re-init) | 30 min |
| Pangolin DB corrupted | Restore from `pg_dump` cron | 15 min |
| arm1-oci unreachable | Pulumi-rebuild from snapshot | 1 hour |
| Lego cert expired | Re-run lego DNS-01 (3 commands) | 2 min |
| Komodo Core data loss | Restore from `komodo-backups` volume | 10 min |
| Newt stuck | `docker compose restart newt` | 30 sec |

## 6. Idempotency

All Phase 1-7 commands are idempotent (docker compose `up -d` is
idempotent, pulumi `up` is idempotent, init-vault.ts is idempotent).

Phase 8-9 (TypeScript SDK calls) are **not** idempotent at the API
level (POST /resource returns 409 on duplicate). Wrap them with a
`try { POST } catch (409) { PATCH }` pattern.

## 7. Where the Source of Truth Lives

| Concern | Source of Truth | Edit Mechanism |
|:--|:--|:--|
| OCI infra | Pulumi | `pulumi up` |
| Cloudflare DNS | Pulumi | `pulumi up` |
| Infisical secrets | Infisical UI + init-vault.ts | UI or `bun run scripts/init-vault.ts` |
| Stack compose files | Forgejo (this repo) | Git push → Komodo syncs |
| Stack deployment state | Komodo Core DB | Komodo UI / SDK |
| Pangolin resources | Pangolin DB | UI / Integrations API |
| Per-host data | Host filesystem | Backup cron |

---
*This document is the canonical reference for the cianfhoghlaim platform.
If a step fails, update this doc + the runbook in
`infrastructure/scripts/setup-pangolin-komodo.sh`.*
