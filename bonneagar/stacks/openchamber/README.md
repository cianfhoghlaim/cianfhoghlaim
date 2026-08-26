# OpenChamber — OpenCode web/desktop UI

> **Current deployment: the native macOS desktop app on the workload host,
> exposed as a Pangolin private resource at `openchamber.cianfhoghlaim.ie`.**
>
> The containerised stack in this directory is **superseded** — see
> [§5](#5-the-superseded-container-stack). It is retained for reference and for
> anyone deploying OpenChamber to a Linux host, where containerising it is
> still the right answer.

---

## 1. What is actually running

| | |
|---|---|
| **Form** | Native macOS app (`/Applications/OpenChamber.app`), not a container |
| **Listens on** | `127.0.0.1:57123` — loopback only, never bound to the LAN |
| **Reached at** | `https://openchamber.cianfhoghlaim.ie` |
| **Exposed by** | Pangolin private (client) resource, niceId `openchamber` |
| **Served by** | Pangolin site `macbook` (siteId 6) via newt in Docker |
| **Declared in** | [`../../pangolin/private-resources.blueprint.yaml`](../../pangolin/private-resources.blueprint.yaml) |

```
iPhone / laptop (Pangolin Olm client)
        │  DNS → 100.96.128.11 (private alias)
        ▼
   Gerbil (WireGuard exit node, control-plane VPS)
        │
        ▼
   newt (Docker, on the MacBook) ── terminates TLS
        │  plain HTTP
        ▼
   host.docker.internal:57123 → OpenChamber.app
```

The full mechanism is documented in
[`../../docs/private-resources-architecture.md`](../../docs/private-resources-architecture.md).

### Two properties worth understanding

**The app stays bound to loopback.** newt runs in Docker and reaches the host's
loopback through `host.docker.internal`, which OrbStack maps to the macOS host.
So OpenChamber is reachable through the tunnel *without* being exposed on the
local network. Enabling OpenChamber's own LAN-access mode is unnecessary here —
and that mode is gated behind setting a UI password anyway.

**The port is stable but not contractual.** `57123` is OpenChamber's
`desktopLocalPort`, persisted in `~/.config/openchamber/settings.json`. It
survives restarts, but nothing guarantees it. If it ever changes, the private
resource 502s until `destination-port` in the blueprint is updated to match.

---

## 2. Access

Connect the Pangolin client, then open `https://openchamber.cianfhoghlaim.ie`.

Without the client connected you get Pangolin's "connect via the client" page.
That is correct behaviour, not a fault — see the architecture doc.

Granted to `cian.deacy@icloud.com`, which covers every enrolled device for that
account.

---

## 3. Security posture

**OpenChamber's HTTP API is unauthenticated.** `GET /api/config` returns the
full configuration, including permission settings that allow shell execution.
Anything that can reach `127.0.0.1:57123` — or the private resource — has
effective shell access on the workload host.

Current controls: the resource is reachable only from an enrolled, granted
Pangolin client. There is no second factor.

If you want defence in depth, OpenChamber supports a UI password
(`desktopUiPassword` in settings, or `OPENCHAMBER_UI_PASSWORD`). Setting it is
also a prerequisite for OpenChamber's LAN-access mode, which this deployment
deliberately does not use.

---

## 4. Operations

```bash
# Is the app serving locally?
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:57123/

# Can newt reach it? (the hop that actually breaks)
docker exec newt wget -qO- --timeout=5 http://host.docker.internal:57123/ | head -c 100

# Is the site online?
docker logs newt | grep -iE 'Tunnel connection|Synced targets'

# Re-assert the declared state (idempotent)
cd bonneagar/pangolin && PANGOLIN_API_KEY=... ./apply-blueprint.sh
```

**Persistence.** newt is `restart: unless-stopped`, but that only helps if the
container runtime starts at login. On macOS: `orb config set app.start_at_login true`.
Otherwise the tunnel disappears on reboot and the resource goes dark with no
error anywhere.

Troubleshooting table: [`../../docs/deploy-private-resource-from-scratch.md`](../../docs/deploy-private-resource-from-scratch.md#8-troubleshooting).

---

## 5. The superseded container stack

`compose.yaml`, `compose.dev.yaml` and `sidecar.yaml` describe an earlier
design (`pangolin.yaml` was deleted on 2026-08-23 — see below): OpenChamber running as a container on the control-plane VPS
(bundled `opencode-ai` runtime) or on the MacBook against an external OpenCode
server on `:4096`, published through Traefik with TinyAuth/Pocket ID.

It is kept because it is a valid pattern for a **Linux** workload host. It is
not what runs today, and two parts of it will not work as written:

- **`compose.yaml` pins a fabricated image digest.** Its own comments record
  that `MOCK_MODE=1` generated
  `sha256:21fda9fc9b0eb7ade140fb763d72779b039ba185be3beafad207a3f88978eae3`
  because GHCR was unreachable from the build sandbox. That digest does not
  exist and the image cannot pull. Re-resolve a real digest before use.
- **`pangolin.yaml` was deleted.** It defined a Traefik file-provider router
  for the *public* path with TinyAuth ForwardAuth. A private client resource
  does not use Traefik at all; it is declared in the blueprint. Applying both
  would have published the service publicly — the opposite of the intent.
  Nothing was lost: Traefik reads its config from Pangolin's database via the
  HTTP provider, and the control plane's `config/traefik/rules/` directory is
  empty, so no per-stack `pangolin.yaml` in this repo was ever deployed.

To revive the container form on Linux: resolve a real digest, keep
`compose.yaml` + `sidecar.yaml`, and add a blueprint entry whose `destination`
is the container name on newt's Docker network.

**Bring it up with both files** — `docker compose -f compose.yaml -f
sidecar.yaml up -d`. `compose.yaml` alone omits the Locket secrets mount, and
the stack then starts silently unconfigured. That single mistake is what had
openclaw and hermes down; see `bonneagar/docs/deploy-private-resource-from-scratch.md`.

---

## See also

- [`../../docs/private-resources-architecture.md`](../../docs/private-resources-architecture.md) — how the private path works
- [`../../docs/deploy-private-resource-from-scratch.md`](../../docs/deploy-private-resource-from-scratch.md) — reproduce it
- [`../../docs/ai-provider-tiers.md`](../../docs/ai-provider-tiers.md) — the model backends OpenChamber talks to
- [`../../pangolin/private-resources.blueprint.yaml`](../../pangolin/private-resources.blueprint.yaml) — the declaration
