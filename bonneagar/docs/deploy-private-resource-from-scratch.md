# Deploying a private resource from scratch

> Reproduce the `openchamber.cianfhoghlaim.ie` setup on your own hardware,
> VPS provider and domain: a service on a machine you own, reachable from your
> phone over a private tunnel, with a valid TLS certificate and no inbound
> ports opened at home.

Read [private-resources-architecture.md](private-resources-architecture.md)
first if you want to know *why* any of this works. This document is the build.

---

## 0. Substitutions

Everything below is written with our values. Replace them with yours:

| Placeholder | Ours | Yours |
|---|---|---|
| `example.com` | `cianfhoghlaim.ie` | your domain |
| `<org>` | `cianfhoghlaim` | your Pangolin org id |
| `<control-plane>` | `oci.arm1` (Oracle ARM, London) | your VPS |
| `<workload-host>` | MacBook (site `macbook`) | your always-on machine |
| `<service>` | OpenChamber on `127.0.0.1:57123` | whatever you're exposing |
| `<fqdn>` | `openchamber.cianfhoghlaim.ie` | your resource hostname |

---

## 1. What you actually need

**None of this is specific to Oracle Cloud, Apple Silicon, or Cloudflare.**
The requirements are narrow:

### Control plane host

| Requirement | Why | Notes |
|---|---|---|
| Public IPv4 | Clients and sites dial in | A single VPS. Oracle free tier, Hetzner CX/CAX, GCP e2-micro, Vultr, a Pi on a static IP — all fine. |
| 2 vCPU / 2 GB RAM | Pangolin + Gerbil + Traefik + Postgres/SQLite | Our 4-core/24 GB ARM box is heavily over-provisioned for this. 2 GB is comfortable. |
| Inbound `443/tcp`, `80/tcp` | Public path + ACME | |
| Inbound `51820/udp`, `21820/udp` | WireGuard + hole punching | **The most commonly missed step.** |
| Docker + Compose | | |

Provider-specific firewalling is the usual trip hazard, because most providers
have *two* layers and you must open both:

| Provider | Layer 1 | Layer 2 |
|---|---|---|
| Oracle Cloud | VCN Security List / NSG | `iptables` on the instance — Oracle images ship with a restrictive default |
| Hetzner | Cloud Firewall | `ufw` if enabled |
| GCP | VPC firewall rules | usually none |
| AWS | Security Group | NACL if customised |

### Workload host

| Requirement | Why |
|---|---|
| Outbound internet | newt dials out; **no inbound ports, no public IP, CGNAT is fine** |
| Runs continuously | A sleeping laptop is an offline site |
| Docker *or* a place to run one binary | newt ships as both |

Architecture is irrelevant — Apple Silicon, x86, ARM SBC all work.

### Domain and DNS

Any registrar and any DNS host. You need to create records and, for wildcard
certificates, an API token for DNS-01. Cloudflare is what we use because
Traefik's DNS-01 provider support is good, but Route53, DigitalOcean, deSEC and
others are equally supported by Traefik/Lego.

### Licensing

`mode: http` and `mode: ssh` private resources require a **licensed Pangolin
tier**. Unlicensed, you get:

```
HTTP private resources are not included in your current plan. Please upgrade.
```

Without a licence, use `mode: host` or `mode: cidr` and reach the service at
`http://<alias-ip>:<port>` — same privacy and tunnelling, no per-resource
hostname or TLS. **Decide this before designing your naming scheme.**

---

## 2. Phase 0 — DNS

Two records, both pointing at the control plane:

```
pangolin.example.com    A    <vps-ip>     # dashboard
<fqdn>                  A    <vps-ip>     # the private resource
```

A private resource **does** need a public A record, even though private traffic
never uses it. It exists so the public path can serve the "connect via client"
page, and so ACME can validate the name. A wildcard `*.example.com` works too.

Verify before continuing — ACME failures cascade confusingly:

```bash
dig +short pangolin.example.com A
dig +short <fqdn> A
```

---

## 3. Phase 1 — Control plane

Use the stack in [`../stacks/pangolin/`](../stacks/pangolin/) or upstream's
compose. Bring-up detail lives in [../PANGOLIN-SETUP.md](../PANGOLIN-SETUP.md).
Three things matter more than the rest:

### Pin the image, and pick the right family

Pangolin's EE image ships in two families that are **not interchangeable**:

| Tag | Database |
|---|---|
| `fosrl/pangolin:ee-1.21.1` | SQLite |
| `fosrl/pangolin:ee-postgresql-1.21.1` | PostgreSQL |

Switching families points Pangolin at an empty database. Everything appears
lost, though nothing is. Confirm which you are on before any upgrade:

```bash
# authoritative: does the app actually receive a connection string?
docker exec pangolin sh -c 'tr "\0" "\n" < /proc/1/environ' | grep -i postgres
ls -la /opt/pangolin/config/db/db.sqlite   # non-trivial size ⇒ SQLite is live
```

A compose file that *declares* a Postgres service proves nothing — if the
connection string never reaches the container, Pangolin silently uses SQLite.

Never track a floating tag. `ee-latest` is how an install sits three minor
versions behind without anyone noticing.

### Back up before upgrading

```bash
sqlite3 /opt/pangolin/config/db/db.sqlite ".backup /opt/backup/db.sqlite"
sqlite3 /opt/backup/db.sqlite "pragma integrity_check;"
tar czf /opt/backup/config.tar.gz -C /opt/pangolin config   # certs + keys too
```

Migrations run automatically on boot and are one-way.

### Verify

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://pangolin.example.com/
docker logs pangolin 2>&1 | grep -iE 'migration|listening'
```

---

## 4. Phase 2 — Secrets

Every stack here reads the *same variable names* regardless of where the values
come from, so the provider is swappable. See
[../SECRETS-MANAGEMENT.md](../SECRETS-MANAGEMENT.md) for the parity table
covering Infisical, 1Password and plain `.env`.

One deliberate exception, worth copying: **newt's own credentials are stored as
a plain file**, not fetched from a secrets manager. A tunnel agent that cannot
start until a remote vault answers has coupled your connectivity to that
vault's uptime — and if the vault is itself behind the tunnel, that is a
deadlock. Bootstrap credentials belong on disk.

---

## 5. Phase 3 — Register the workload host as a site

In the Pangolin dashboard: **Sites → Add Site → Newt**. Copy the generated
`newtId` and `secret`.

> **Name the site after the machine, and never reuse the name.** Sites are
> addressed by `niceId` in automation but shown by `name` in the UI, and a
> stale site with a plausible name is the single most effective way to lose an
> afternoon. If you retire a site, delete it.

### Option A — Docker (what we run)

`newt.env`, mode `600`:

```bash
PANGOLIN_ENDPOINT=https://pangolin.example.com
NEWT_ID=<newtId>
NEWT_SECRET=<secret>
LOG_LEVEL=INFO
```

`newt.yaml`:

```yaml
name: newt
services:
  newt:
    image: fosrl/newt:1.16.0
    container_name: newt
    restart: unless-stopped
    env_file: [newt.env]
    cap_add: [NET_ADMIN, NET_RAW]
    extra_hosts:
      - host.docker.internal:host-gateway
```

Do not copy `SYS_MODULE` or custom networks from older examples unless you need
them; `SYS_MODULE` is meaningless on macOS runtimes, and referencing an
external network that doesn't exist prevents the container from starting at all.

### Option B — native binary

Better when the target is bound to host loopback and your container runtime
can't reach it. `newt --id <id> --secret <secret> --endpoint https://pangolin.example.com`,
supervised by systemd or launchd.

### The reachability question that decides A vs B

**Can newt reach your service?** If newt is containerised and the service is
bound to `127.0.0.1` on the host, this is runtime-dependent:

| Runtime | Container → host loopback | Use |
|---|---|---|
| OrbStack (macOS) | Yes, via `host.docker.internal` | `host.docker.internal` |
| Docker Desktop (macOS/Windows) | Usually, via `host.docker.internal` | test it |
| Docker CE (Linux) | No by default | `--network host`, native newt, or bind the service to the bridge |
| Service is a sibling container | n/a | use the container name |

Test it explicitly rather than assuming — one command settles it:

```bash
docker exec newt wget -qO- --timeout=5 http://host.docker.internal:<port>/ | head -c 100
```

If that fails, no amount of Pangolin configuration will help. Fix it here.

### Confirm the site is online

```bash
docker logs newt | grep -iE 'Tunnel connection|Server version'
```

Expect `Tunnel connection to server established successfully!`, and the site
showing **online** in the dashboard. A site that never comes online is almost
always wrong credentials or blocked outbound UDP.

### Persistence

`restart: unless-stopped` only helps if the container runtime itself starts at
boot. On macOS with OrbStack:

```bash
orb config set app.start_at_login true
```

Otherwise the tunnel silently disappears on every reboot.

---

## 6. Phase 4 — Declare the resource

Use a blueprint. It is Pangolin's own declarative interface, it reconciles
rather than appends, and it rebuilds the derived grant caches that hand-editing
the database does not.

Look up the site's `niceId` — **not its display name**:

```bash
sqlite3 /opt/pangolin/config/db/db.sqlite 'select siteId, name, niceId, online from sites;'
```

Then, in [`../pangolin/private-resources.blueprint.yaml`](../pangolin/private-resources.blueprint.yaml):

```yaml
private-resources:
  my-service:                      # ← the niceId AND the upsert key
    name: My Service
    mode: http
    scheme: http
    ssl: true
    sites:
      - <site-niceId>
    destination: host.docker.internal
    destination-port: 57123
    full-domain: my-service.example.com
    enabled: true
    users:
      - you@example.com            # your account email
    roles: []                      # never "Admin"
    machines: []
```

Apply:

```bash
export PANGOLIN_API_KEY='<apiKeyId>.<apiKeySecret>'
./apply-blueprint.sh
```

Expect `Blueprint applied successfully`.

### Getting an API key

Set `PANGOLIN_ROOT_API_KEY={apiKeyId}.{apiKeySecret}` in the Pangolin
container's environment (id must be 15 lowercase alphanumeric characters) and
restart. Pangolin creates or promotes the key at boot and logs
`ROOT API KEY CREATED FROM ENVIRONMENT`. The hash persists in the database, so
the environment variable can then be removed. Keys created this way may need
their action grants populated before the API will authorise them.

### Four rules

1. **The YAML key is the `niceId` and the upsert key.** Renaming it creates a
   second resource rather than renaming the first.
2. **`sites:` matches `niceId`, not name.** Wrong value gives
   `No valid sites found for private private resource <name> in org <org>`.
3. **`users:` is an email, `machines:` is a client `niceId`.** Unresolvable
   entries are ignored silently, producing a resource nobody can reach.
4. **Never `roles: [Admin]`.** Rejected outright; admin access is implicit.

### Gotcha: the endpoint takes JSON

Blueprints are authored and displayed as YAML, but the API takes base64-encoded
**JSON**. Posting base64 YAML fails with
`SyntaxError: Unexpected token '#'`. `apply-blueprint.sh` converts for you.

---

## 7. Phase 5 — Connect a client and verify

Install the Pangolin app (iOS, Android, macOS, Linux), sign in, connect.

Then verify **in order**. Each stage isolates one hop, so the first failure
tells you where the problem is:

```bash
# 1. DNS — must return the private alias, NOT your VPS IP
nslookup my-service.example.com
#    → 100.96.x.x   good
#    → <vps-ip>     the client isn't overriding DNS; you'd get the block page

# 2 + 3. TLS validates against the real hostname, and HTTP answers
curl -sS -o /dev/null -w 'HTTP %{http_code}\n' https://my-service.example.com/

# 4. protocol-specific: WebSockets, streaming, auth flows
```

Do not skip stage 1. "It shows the block page" and "it times out" are different
faults and stage 1 distinguishes them instantly.

### Verifying without a phone

You can drive the whole path from a container, which makes this scriptable and
means you can test before enrolling a real device. Create a throwaway client,
grant it the resource, run `fosrl/olm`, and query through it:

```bash
docker run -d --name olm-verify --cap-add NET_ADMIN --device /dev/net/tun \
  -e PANGOLIN_ENDPOINT=https://pangolin.example.com \
  -e OLM_ID=<olmId> -e OLM_SECRET=<secret> fosrl/olm:latest

docker exec olm-verify sh -c 'nslookup my-service.example.com'
docker exec olm-verify sh -c 'wget -qO- -S https://my-service.example.com/ 2>&1 | head -20'
```

`wget` validates certificates by default, so a clean fetch proves DNS, tunnel,
TLS and the backend in one shot. Delete the client afterwards.

---

## 7a. Validate continuously — `pangolin-doctor`

Every check in [`../pangolin/pangolin-doctor.sh`](../pangolin/pangolin-doctor.sh)
corresponds to a failure that actually happened here. Run it after any change:

```bash
cd bonneagar/pangolin && ./pangolin-doctor.sh      # or: ./pangolin-doctor.sh 1 2 7
```

| # | Check | The failure it catches |
|---|---|---|
| 1 | Resource bound to an **online** site | A resource pinned to a dead site — looks correct everywhere, never loads |
| 2 | Destination reachable **from newt** | Wrong port, or `localhost` (which is the newt container, not the host) |
| 3 | Association cache populated | A hand-edited database, which never rebuilds the cache |
| 4 | Grants resolve | Grants to accounts/clients that do not exist — silently ignored |
| 5 | Blueprint matches live state | Drift, and resources nobody is managing declaratively |
| 6 | Image tags pinned | `ee-latest` quietly drifting three minor versions |
| 7 | Locket healthy **and** `/run/secrets/locket` populated | A stack started without its sidecar — see below |

`apply-blueprint.sh` also pre-flights every apply: it resolves site niceIds
against the live org (printing the valid ones when you get it wrong), rejects
`Admin` in `roles`, and warns on unresolvable users/machines and on
`destination: localhost`.

## 7b. Bring stacks up WITH their sidecar overlay

If a stack uses Locket for secrets, it must be started with both files:

```bash
docker compose -f compose.yaml -f sidecar.yaml up -d     # correct
docker compose up -d                                     # starts unconfigured
```

`sidecar.yaml` is what mounts the `stack-secrets` volume at
`/run/secrets/locket`. Started from `compose.yaml` alone, the app comes up with
no secrets and fails in whatever way that particular app fails — openclaw
crash-looped on "no token is configured"; hermes started its supervisor tree
and then exited with no logs at all.

Two traps found on 2026-08-23:

- **Duplicate `environment:` keys.** 17 `sidecar.yaml` files in this repo
  declared `environment:` twice in the same service. Duplicate mapping keys are
  a YAML error, so `docker compose -f compose.yaml -f sidecar.yaml` refused to
  parse and the overlay could never be used at all. PyYAML silently accepts
  duplicates (last wins) while Go's parser errors, so a Python-based lint will
  *not* catch this — check with a duplicate-key-aware loader or just run
  `docker compose config --quiet`.
- **Placeholder secrets.** Infisical held the literal
  `sk-placeholder-replace-me` for `/hermes/openai_api_key`. Locket resolved it
  perfectly and reported healthy — a placeholder is a valid value. Check
  resolved *values*, not just that resolution succeeded.

## 7c. Bind inside the container, not just on the host

A service that binds **container loopback** cannot be reached through Docker
port publishing: the port appears published on the host and every connection is
refused. The service must bind `0.0.0.0` *inside* the container; the host-side
publish (`127.0.0.1:PORT:PORT`) is what keeps it off your LAN.

openclaw needed `gateway --bind lan`; its default bound loopback and the
resource would have 502'd. Symptom to recognise:

```bash
docker ps            # shows 127.0.0.1:18789->18789/tcp   (looks fine)
curl 127.0.0.1:18789 # 000, connection refused            (is not fine)
```

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Block page while connected | DNS not overridden | Confirm client connected; check it resolves via the tunnel resolver |
| `No valid sites found` | `sites:` used a display name | Use the `niceId` |
| Site never comes online | Bad credentials, or outbound UDP blocked | Check newt logs; open `51820`/`21820` outbound |
| Times out, DNS correct | Site offline | Check `sites.online`; is the host awake? |
| `502` from the alias | newt can't reach the destination | `docker exec newt wget -qO- http://<dest>:<port>/` |
| Cert warning | Cert not issued/distributed | Check the `certificates` table |
| Resource invisible to a device | Missing grant or stale cache | Re-apply the blueprint; never hand-edit the DB |
| Worked yesterday, not today | Runtime didn't start at boot | `orb config set app.start_at_login true` or equivalent |
| App up, port published, connection refused | Service bound container loopback | Bind `0.0.0.0` inside the container (§7c) |
| App starts then exits, no/empty logs | Started without `-f sidecar.yaml`, so no secrets | Bring up with both files (§7b) |
| `docker compose -f a -f b` won't parse | Duplicate `environment:` key in the overlay | Merge into one block (§7b) |
| Locket healthy but auth still fails | Secret resolved to a *placeholder* value | Inspect the resolved value, not just health (§7b) |
| Port changed under you | App picked a new port | Re-check the service's port; update `destination-port` |

### Diagnosing in the right order

Work outward from the target — most faults are at the ends, not the middle:

```bash
# 1. is the service up locally?
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:<port>/

# 2. can newt reach it?
docker exec newt wget -qO- --timeout=5 http://<destination>:<port>/ | head -c 100

# 3. is the site online and the resource bound to it?
sqlite3 db.sqlite 'select siteId,name,online from sites;'
sqlite3 db.sqlite 'select sr.niceId, s.name, s.online from siteResources sr
  join siteNetworks sn on sn.networkId=sr.networkId
  join sites s on s.siteId=sn.siteId;'

# 4. may the client see it?
sqlite3 db.sqlite 'select * from clientSiteResourcesAssociationsCache;'
```

If step 4 is empty but the grants look right, the cache is stale from a direct
database write. Re-apply the blueprint.

---

## 9. Adapting this

| If you have | Change |
|---|---|
| Hetzner / GCP / AWS instead of Oracle | Nothing but firewall syntax |
| A Linux workload host | Prefer native newt or `--network host`; `host.docker.internal` isn't automatic |
| Several workload hosts | One newt per host; list multiple `sites:` for failover |
| No licence | `mode: host` / `cidr`; reach services by alias IP and port |
| A non-Cloudflare DNS host | Any Traefik/Lego DNS-01 provider; only credentials change |
| Only a laptop, no VPS | You still need a public IP somewhere for Gerbil. A cheap VPS is the minimum. |

---

## See also

- [private-resources-architecture.md](private-resources-architecture.md)
- [ai-provider-tiers.md](ai-provider-tiers.md) — sizing model serving to your hardware
- [../SECRETS-MANAGEMENT.md](../SECRETS-MANAGEMENT.md)
- [../pangolin/private-resources.blueprint.yaml](../pangolin/private-resources.blueprint.yaml)
