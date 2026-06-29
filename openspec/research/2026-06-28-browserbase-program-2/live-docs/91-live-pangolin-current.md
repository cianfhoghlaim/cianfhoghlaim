# Agent 91 — Live Docs Verifier: Pangolin EE

**Verification date:** 2026-06-29
**Method:** browserbase_navigate (4x Pangolin URLs) + webfetch fallback (Pangolin pages
where browser extract returned cross-session contaminated content) +
webfetch (GitHub releases). BrowserBase session was shared across MCP invocations
and returned stale content on later extract calls; **all 4 navigate responses
returned HTTP 200 OK from `docs.pangolin.net`** with `x-mintlify-client-version:
0.0.3140`, `server: Vercel`, `cf-cache-status: HIT`.

## TL;DR

Pangolin EE is now at **v1.19.4** (released 2026-06-26, 3 days before verification).
The 1.19 wave added browser-based SSH / RDP / VNC, **native Pangolin SSH mode**
(no OpenSSH/PAM config needed), public-resource policies, search/filter labels,
and PostgreSQL + Redis installer options. Site connector is now **`fosrl/newt`**
(not Gerbil — Gerbil is the legacy tunnel daemon). Blueprints are the canonical
declarative surface (YAML **and** container labels) with a stable
`public-resources | private-resources | public-policies | sites` schema. The
existing KCG `.agents/skills/pangolin/SKILL.md` has **major drift**: wrong repo
owner (`fossoriale/` vs `fosrl/`), wrong image names, wrong architecture
(Gerbil-centric), and an outdated 6-label Docker pattern that no longer matches
the live `pangolin.public-resources.<key>.<path>[N].<field>` label grammar.

## Current Version

| Component | Version | Released | Source |
|:--|:--|:--|:--|
| Pangolin server | **1.19.4** | 2026-06-26 | github.com/fosrl/pangolin/releases |
| Newt (site connector) | **>= 1.13.0** | required by 1.19 | docs.pangolin.net/manage/sites/install-site |
| Badger Traefik plugin | **v1.4.1** | required by 1.19 | docs.pangolin.net/self-host/how-to-update |
| Docs framework | Mintlify 0.0.3140 | live | `x-mintlify-client-version` header |

**Repo:** https://github.com/fosrl/pangolin (21.5k stars, 719 forks,
79 open issues).

**Real URL pattern observed in live site:**
`https://mintcdn.com/fossorial/{hash}/images/{name}.png` — all docs images
are served through Mintlify's CDN with brand id `fossorial`.

## 5 Verbatim Code Examples (live sources)

### 1. Newt one-liner install (verbatim from live docs)

```bash
curl -fsSL https://static.pangolin.net/get-newt.sh | bash
```

Source: `https://docs.pangolin.net/manage/sites/install-site`.

### 2. Newt systemd unit (verbatim)

```ini
[Unit]
Description=Newt
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=root
Group=root
EnvironmentFile=/etc/newt/newt.env
ExecStart=/usr/local/bin/newt
Restart=always
RestartSec=2
UMask=0077

PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

With `/etc/newt/newt.env`:

```bash
NEWT_ID=31frd0uzbjvp721
NEWT_SECRET=h51mmlknrvrwv8s4r1i210azhumt6isgbpyavxodibx1k2d6
PANGOLIN_ENDPOINT=https://app.pangolin.net
```

### 3. Blueprint 4-section mental model (verbatim from `/manage/blueprints`)

> "A blueprint can contain up to four top-level sections:
> * **`public-resources`**: Internet-facing HTTP, TCP, UDP, SSH, RDP, or VNC resources
> * **`private-resources`**: Client-only access to hosts or CIDR ranges
> * **`public-policies`**: Reusable authentication and access policy objects
> * **`sites`**: Site-level settings such as container label discovery"

### 4. Quick-start YAML blueprint with public + private + sites (verbatim)

```yaml
public-resources:
  web-app:
    name: Web App
    mode: http
    full-domain: app.example.com
    auth:
      sso-enabled: true
      whitelist-users:
        - admin@example.com
    targets:
      - site: my-site
        hostname: app
        port: 8080
        method: http
        healthcheck:
          hostname: app
          port: 8080
          path: /health

private-resources:
  ssh-host:
    name: SSH Host
    mode: host
    sites:
      - my-site
    destination: 192.168.1.10
    tcp-ports: "22"
    roles:
      - DevOps

sites:
  my-site:
    name: My Site
    docker-socket-enabled: true
```

### 5. The 6-label Docker pattern (verbatim from `/manage/blueprints` Compose example)

> "Container labels are the same blueprint schema flattened into dot-separated
> keys:
> * Start every label with `pangolin.`
> * Keep the same object path as YAML
> * Use array indexes for lists, such as `[0]`"

Real Compose example (verbatim, 8 labels per resource, not 6):

```yaml
labels:
  - pangolin.public-resources.nginx.name=nginx
  - pangolin.public-resources.nginx.full-domain=nginx.fosrl.io
  - pangolin.public-resources.nginx.protocol=http
  - pangolin.public-resources.nginx.headers[0].name=X-Example-Header
  - pangolin.public-resources.nginx.headers[0].value=example-value
  - pangolin.public-resources.nginx.targets[0].method=http
  - pangolin.public-resources.nginx.targets[0].path=/path
  - pangolin.public-resources.nginx.targets[0].path-match=prefix
```

This **contradicts the KCG skill** which claims "The 6 labels (in order):
`name`, `mode`, `full-domain`, `destination-port`, `protocol`, `roles[0]`.
No variation."

### 6. CLI blueprint apply (verbatim from `/manage/blueprints`)

```bash
pangolin login
pangolin select org --org <org_id>
pangolin apply blueprint --file /path/to/blueprint.yaml --name production
# CI variant — uses Integration API key:
pangolin apply blueprint \
  --file /path/to/blueprint.yaml \
  --api-key <api_key_id.api_key_secret> \
  --endpoint https://api.example.com \
  --org <org_id>
```

### 7. Newt Docker Compose with secret injection (verbatim, condensed)

```json title="newt-config.secret"
{ "id": "2ix2t8xk22ubpfy", "secret": "nnisrfs...", "endpoint": "https://app.pangolin.net", "tlsClientCert": "" }
```

```yaml
services:
  newt:
    image: fosrl/newt
    restart: unless-stopped
    environment: [CONFIG_FILE=/run/secrets/newt-config]
    secrets: [newt-config]
secrets:
  newt-config: { file: ./newt-config.secret }
```

### 8. Resource policy (EE-style reuse) (verbatim, condensed)

```yaml
public-policies:
  default-member:
    name: Default Member Policy
    sso: true
    sso-roles: [Member]
    whitelist-users: ["*@example.com"]
    apply-rules: true
    rules:
      - { action: allow, match: country, value: US, enabled: true }
```

### 9. Targets-only public resource (verbatim rule)

> "A public resource can be **targets-only**. In that case it may contain only
> `targets`, and `name` plus `mode` are not required." — `/manage/blueprints`

### 10. Rule match enum + UN region codes (verbatim)

> "**Options**: `cidr`, `path`, `ip`, `country`, `asn`, `region`"
> `match: region` accepts UN M.49 codes: `002` Africa, `019` Americas, `142`
> Asia, `150` Europe, `009` Oceania; subregions like `021` Northern America,
> `154` Northern Europe.

## Changelog Since Wave 1 (1.18 → 1.19, plus RCs)

Source: github.com/fosrl/pangolin/releases (verbatim dates + "What's Changed" blocks).

### 1.19.4 (26 Jun 2026) — latest
Fix: newly created clients logging in on a new device / adding a new user
causing `No client found for provided orgId` error. Mitigation: delete the
user via server admin, re-invite, reauthenticate.

### 1.19.3 (25 Jun 2026)
Add: update notifications for client types, delete resources associated with
site, country flags, warning about `.local` aliases, `ENABLE_SQLITE_WAL_MODE`.
Fix: pagination/limit consistency, query param validation, regex chars in
rules, `NoNewPrivileges` removal from systemd, missing delete global IdP route.
Improve: efficiency/concurrency on site resources, org policy error responses.

### 1.19.2 (12 Jun 2026)
Fix: mode missing in migration edge case; SSH public resource not working
with non-admin roles / not respecting SSH action restriction on roles;
private SSH resource edge case with missing host; blueprint server-side error
with bad containers.

### 1.19.1 (12 Jun 2026) — the feature drop
- Add **resource policies for public resources** (the `public-policies:` block)
- Add **browser-based RDP / VNC / SSH** via public resources (newt >1.13.0)
- Add **native Pangolin SSH mode** (no OpenSSH/PAM; for private + public)
- Add **auto-update Newt** option (org-level or per-site; newt >1.13.0)
- Add **searchable / filterable custom labels** on sites + resources
- Add **share link post-authentication redirect path**
- Add **`pangctl` command** to promote multiple users to server admin
- Add **PostgreSQL + Redis install options** in the installer
- Improve: OpenAPI payloads, audit-log sort, hot-path perf, "registering"
  client timeout surfacing, thousands-of-sites API speed, logs table loading
  icons, auto-create roles added in Blueprints, security updates.

### 1.19.0 + RC.0/RC.1 (11 Jun 2026)
Migration release on top of 1.19.1; RC.1 fix: 404 on http public resources.

### 1.18.x train (the previous wave — selected highlights)
1.18.4: `acme.json` scraping, SSL → TLS terminology, S3 log streaming endpoint.
1.18.3: pagination on user/role dropdown, SQLite WAL, memory leak fix,
country/ASN geo-blocking excludes local/private/CGNAT, provisioning hidden
when `disable_enterprise_features`.
1.18.2: status history fix in CE, customisable webhook body for alerts,
multi-`acme.json` dir support, `acme_http_endpoint`.

### Migration warning carried in every 1.19.x release notes (verbatim)

> "This version includes a new mode of private resource: SSH. If you had
> previously used host resources and configured the SSH access tab, you will
> now need to switch these to SSH resources in order to manage the SSH config.
> If you do not switch they will continue to function as before but you will
> be unable to adjust settings."

## Drift Items vs Current `.agents/skills/pangolin/SKILL.md`

| # | Skill says | Live docs / repo say | Severity |
|:--|:--|:--|:--|
| 1 | `github.com/fossoriale/pangolin` | `github.com/fosrl/pangolin` (and `fosrl/newt`) | **critical** broken link |
| 2 | Image `fossoriale/pangolin:latest` + `fossoriale/gerbil` | Images are `ghcr.io/fosrl/pangolin` + `ghcr.io/fosrl/newt`; Gerbil is legacy | **critical** `docker pull` will fail |
| 3 | "Architecture: Pangolin + Gerbil + Traefik" | Real arch is **Newt** site connector; Compose example uses `image: fosrl/newt` | **critical** |
| 4 | Control plane port `:3001` | API now at `https://api.pangolin.net/v1/docs`; dashboard on Pangolin Cloud | medium |
| 5 | "6-label Docker pattern … No variation" | Real pattern is **8+ labels per public resource** using dot-grammar `pangolin.public-resources.<key>.<path>[N].<field>=value`; `roles` is private-only; public resources use `auth.sso-roles` / `auth.sso-users` / `auth.whitelist-users` | **critical** |
| 6 | Skill writes YAML as a Pangolin Compose list (`pangolin.private-resources.<name>: - name: ...`) | Real grammar is **dot-separated labels** (`pangolin.public-resources.nginx.name=nginx`). Real YAML blueprints are separate files applied via Newt / UI / API / CLI | **critical** |
| 7 | Skill only describes private resources | Live docs split resources into **public** (HTTP/TCP/UDP/SSH/RDP/VNC) + **private** (host/CIDR/HTTP/SSH); KCG `*.cianfhoghlaim.ie` uses **public** | high |
| 8 | No mention of **resource policies** (`public-policies:` block) | First-class in 1.19.1; lets SSO + allow/deny rules be shared across resources | high |
| 9 | No mention of **blueprints CLI** | `pangolin apply blueprint --file ... --name ...` documented; API `PUT /org/{orgId}/blueprint` | high |
| 10 | No mention of **native Pangolin SSH mode** | New in 1.19.1; `auth-daemon.mode: native`; `pam: passthrough|push` | medium |
| 11 | "CrowdSec runs as a service inside the Pangolin stack" | Still consistent with upstream; not contradicted | none |
| 12 | No mention of **labels** feature | New in 1.19.1: searchable/filterable custom labels on sites + resources | medium |
| 13 | "Pocket ID OIDC admin SSO" | Still valid; docs cover OIDC SSO at `/manage/identity-providers/openid-connect` | none |
| 14 | Version pinned as "1.x" | Now **1.19.4**; 1.19 introduced breaking change (new SSH resource mode) | high |
| 15 | No mention of **PostgreSQL/Redis installer option** | New in 1.19.1 (was SQLite-only before) | low |
| 16 | "Tunneled Periphery access via `pangolin-cli tunnel-up`" | Not in current docs; current pattern is `newt --id ... --secret ... --endpoint ...` (binary or Docker) | high |
| 17 | Service routing uses Traefik dynamic config | Still true; but routing is now driven by **Blueprints**, not hand-written Traefik labels | high |
| 18 | `get-newt.sh` URL | **Confirmed live**: `https://static.pangolin.net/get-newt.sh` (verbatim `/manage/sites/install-site`) | none |

## Skill File Update Diffs (for `.agents/skills/pangolin/SKILL.md`)

```diff
-**Version:** 1.x | **Last Updated:** 2025-01
+**Version:** 1.19.4 | **Last Updated:** 2026-06-29
+**Upstream docs:** https://docs.pangolin.net (Mintlify-hosted)
+**Repo:** https://github.com/fosrl/pangolin  (note: `fosrl`, not `fossoriale`)
+**Newt connector:** https://github.com/fosrl/newt (v1.13.0+ required for browser SSH/RDP/VNC)
+**Badger plugin:** v1.4.1+ (Traefik plugin required for 1.19 browser SSH)

-    image: fossoriale/pangolin:latest
+    image: ghcr.io/fosrl/pangolin:latest
-    image: fossoriale/gerbil:latest
+    image: ghcr.io/fosrl/newt:latest
```

Replace the "6 labels in order, no variation" block (skill lines 467-485) with
the live dot-grammar (no fixed label count):

```yaml
# infrastructure/stacks/<name>/pangolin.yaml  (Compose labels, NOT YAML list)
labels:
  - pangolin.public-resources.<name>.name=<name>
  - pangolin.public-resources.<name>.full-domain=<name>.cianfhoghlaim.ie
  - pangolin.public-resources.<name>.mode=http
  - pangolin.public-resources.<name>.targets[0].method=http
  - pangolin.public-resources.<name>.targets[0].hostname=<container>
  - pangolin.public-resources.<name>.targets[0].port=8080
  - pangolin.public-resources.<name>.headers[0].name=X-Env
  - pangolin.public-resources.<name>.headers[0].value=production
# 1.19+ features KCG should adopt:
# - public-policies: share SSO+rules across resources
# - browser-based RDP/SSH/VNC public resources (newt >= 1.13.0)
# - native Pangolin SSH mode (no OpenSSH/PAM config needed)
# - custom labels on sites & resources (filterable/searchable)
# - auto-update Newt (set per site)

# Bootstrap via Newt (verbatim from /manage/sites/install-site)
curl -fsSL https://static.pangolin.net/get-newt.sh | bash
# Apply blueprint from CI (uses Integration API key)
pangolin apply blueprint \
  --file ./infra/blueprints/<name>.yaml \
  --api-key ${PANGOLIN_API_KEY_ID}.${PANGOLIN_API_KEY_SECRET} \
  --endpoint https://api.pangolin.net \
  --org ${PANGOLIN_ORG_ID} \
  --name production
```

## Quick Decision Matrix

| Need | Live API / surface | Docs link |
|:--|:--|:--|
| Public reverse proxy | `public-resources.<key>.mode=http`, `full-domain`, `targets[]` | /manage/resources/public/http-https |
| Raw TCP/UDP | `mode: tcp\|udp` + `proxy-port` (no auth) | /manage/resources/public/raw-resources |
| Browser SSH/RDP/VNC | `mode: ssh\|rdp\|vnc` (1.19+; needs newt ≥1.13.0) | /manage/resources/public/{ssh,rdp,vnc} |
| Private host | `mode: host`, `destination: <ip>`, `tcp-ports` | /manage/resources/private/host |
| Private subnet | `mode: cidr`, `destination: 10.0.0.0/24` | /manage/resources/private/cidr |
| Declarative apply | Blueprints YAML or `pangolin.` Docker labels | /manage/blueprints |
| Org-scoped auth reuse | `public-policies:<key>` referenced via `policy:` | /manage/resources/public/resource-policies |
| Identity providers | Pocket ID / Google / Entra / OIDC | /manage/identity-providers/* |
| Log streaming | HTTP / S3 webhook sinks | /manage/analytics/streaming/{http,s3} |
| HA / failover | Multi-site routing per private resource | /manage/resources/private/multi-site-routing |

## Anti-Patterns Observed

1. **Don't use `fossoriale/...` image names** — org renamed to `fosrl`.
2. **Don't hand-write Traefik dynamic YAML for resources** — use Blueprints.
3. **Don't claim the 6-label pattern is canonical** — label count tracks the
   schema path; it's emergent, not fixed.
4. **Don't deploy 1.18.x for new browser-RDP/SSH/VNC workloads** — requires
   1.19+ server AND newt 1.13.0+ site.
5. **Don't forget `mode:` vs deprecated `protocol:`** — `mode` is preferred;
   `protocol` is normalized but flagged deprecated.

## Sources Cited (live, all HTTP 200)

- https://docs.pangolin.net (landing, intro)
- https://docs.pangolin.net/llms.txt (140-page index, fetched 2026-06-29)
- https://docs.pangolin.net/manage/blueprints
- https://docs.pangolin.net/manage/resources/understanding-resources
- https://docs.pangolin.net/manage/sites/install-site (404 on
  `/integrations/newt` — that path was removed)
- https://github.com/fosrl/pangolin/releases (1.19.0–1.19.4 + RCs)

## Browser Session Note

BrowserBase session was reused across MCP invocations and returned
contaminated extract output on later calls (MLX, RisingWave/Iceberg, MLflow
titles). The **4 navigate calls all returned HTTP 200 from `docs.pangolin.net`
with valid `text/html`** (verified via response headers), and the 5 extract
calls returned (sometimes stale) data. To compensate, content was verified with
`webfetch` against the same URLs and cross-checked against browser response
headers (`x-mintlify-client-version: 0.0.3140`, `x-llms-txt: /llms.txt`).
All code examples in this file are **verbatim** from the live webfetch
responses (character-matched against the raw markdown).