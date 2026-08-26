# Pangolin private resources — architecture

> How `openchamber.cianfhoghlaim.ie` resolves to an app running on a laptop in
> a living room, with no port forwarding, no public exposure, and a valid
> public TLS certificate.

This document explains the mechanism. To build one, see
[deploy-private-resource-from-scratch.md](deploy-private-resource-from-scratch.md).

---

## 1. The single most important distinction

Pangolin serves two kinds of resource over completely different paths. They
share a dashboard and a domain, and almost nothing else. Conflating them is the
root of most confusion here, because a private resource that is *working
correctly* looks, from the public internet, exactly like a broken one.

```
        PUBLIC / PROXY RESOURCE                 PRIVATE / CLIENT RESOURCE
        (anyone on the internet)                (only your enrolled devices)

              Internet                             Olm client (phone/laptop)
                 │                                          │
                 │ DNS → VPS public IP                      │ DNS → alias 100.96.x.x
                 ▼                                          │   (resolved by the client,
        ┌──────────────────┐                                │    not by public DNS)
        │ Gerbil  :80/:443 │                                ▼
        └────────┬─────────┘                       ┌──────────────────┐
                 ▼                                 │ Gerbil :51820/udp│
        ┌──────────────────┐                       │  (WireGuard)     │
        │ Traefik          │                       └────────┬─────────┘
        │  + Badger plugin │                                │ encrypted tunnel
        │  terminates TLS  │                                ▼
        └────────┬─────────┘                       ┌──────────────────┐
                 ▼                                 │ Newt (site agent)│
        ┌──────────────────┐                       │ on workload host │
        │ Pocket ID /      │                       │ terminates TLS   │
        │ TinyAuth         │                       └────────┬─────────┘
        └────────┬─────────┘                                ▼
                 ▼                                     your service
             target                                (never publicly bound)

        table:  resources                        table:  siteResources
        TLS:    Traefik (Let's Encrypt)          TLS:    Newt (Pangolin-issued)
        auth:   OIDC / ForwardAuth               auth:   device enrolment + grants
```

**A private resource still has a public DNS record.** `openchamber.cianfhoghlaim.ie`
resolves publicly to the VPS. If you visit it *without* the client connected,
Traefik answers with Pangolin's "connect via the client" page. That page is not
an error — it is the public path working correctly and declining to serve a
resource that was never meant to be public. When the client *is* connected, the
client's own DNS resolver answers first and returns the private alias instead,
so the request never reaches the VPS at all.

---

## 2. Components

| Component | Runs on | Role |
|---|---|---|
| **Pangolin** | control plane VPS | Control plane. Owns the database, the dashboard, the API. Decides *who may reach what*. Carries no user traffic. |
| **Gerbil** | control plane VPS | WireGuard exit node. Every tunnel — sites and clients — terminates here. Owns `:51820/udp`, `:21820/udp` and, because Traefik shares its network namespace, `:80`/`:443`. |
| **Traefik** | control plane VPS | Public ingress only. Irrelevant to the private path except for serving the block page. |
| **Newt** | each workload host | Site agent. Dials out to Pangolin, joins the mesh, and proxies to local targets. **Outbound only — the workload host needs no inbound ports and no public IP.** |
| **Olm** | each user device | Client agent. The Pangolin iOS/Android/desktop app. Brings up WireGuard and overrides DNS for private domains. |
| **Pocket ID / TinyAuth** | control plane VPS | OIDC and ForwardAuth for the *public* path. Not in the private data path. |

The asymmetry worth internalising: **both newt and olm dial outward** to Gerbil.
Neither needs an open inbound port. That is why this works from behind CGNAT,
hotel Wi-Fi, or a mobile network.

---

## 3. The worked example

```
iPhone (Olm)                                MacBook (workload host)
100.90.128.5                                site "macbook", newt in Docker
     │                                              │
     │ 1. DNS: openchamber.cianfhoghlaim.ie         │
     │    → 100.96.128.11  (alias, via olm's        │
     │      resolver at 100.96.128.1:53)            │
     │                                              │
     │ 2. TCP 443 → 100.96.128.11                   │
     ├──── WireGuard ──► Gerbil ──── WireGuard ────►│
     │                   (VPS, exit node 1)         │
     │                                              │ 3. newt terminates TLS
     │                                              │    using the Pangolin
     │                                              │    cert for the FQDN
     │                                              │
     │                                              │ 4. plain HTTP →
     │                                              │    host.docker.internal:57123
     │                                              ▼
     │                                     OpenChamber (native macOS app,
     │                                     bound to 127.0.0.1 only)
```

Two details in step 4 carry most of the practical weight:

**The target never binds a public interface.** OpenChamber listens on
`127.0.0.1:57123`. Newt runs in Docker and reaches the host loopback via
`host.docker.internal`, which OrbStack maps to the macOS host. The app is
therefore reachable through the tunnel but not from the local Wi-Fi. Container
runtimes differ here — see the reachability matrix in the deployment guide.

**Newt terminates TLS, not Traefik.** Pangolin issues a certificate for the
FQDN and hands it to newt. The client validates it against the ordinary public
chain, so browsers show no warning despite the connection never touching the
public internet. This is why `ssl: true` and `mode: http` matter, and why
`mode: http` is a licensed feature — it is doing real certificate distribution.

---

## 4. Naming and addressing

Three distinct namespaces, easily confused:

| Namespace | Example | Assigned by | Used for |
|---|---|---|---|
| Site subnet | `100.89.128.12/30` | Pangolin | The WireGuard link to a site |
| Client subnet | `100.90.128.5/20` | Pangolin | A device's tunnel IP |
| Resource alias | `100.96.128.11` | Pangolin | The **virtual IP a private resource answers on** |

The alias is the key abstraction. It is not an address of any real machine; it
is a per-resource virtual IP that the client's routing table points down the
tunnel and that newt answers on behalf of. Multiple resources on one host each
get their own alias, which is how several HTTPS services on the same machine
can all listen on `:443` without colliding.

### niceIds

Every site, client and resource has both a display `name` and a `niceId`.
Pangolin generates niceIds as random animal names (`worried-upper-galilee-
mountains-blind-mole-rat`). **The API and blueprints address objects by
`niceId`; humans read the `name`.** These drift apart freely — a site named
`macbook` and a site named `bunchloch` are different objects regardless of
which machine you think of as which.

```bash
sqlite3 /opt/pangolin/config/db/db.sqlite \
  'select siteId, name, niceId, online from sites;'
```

---

## 5. Where state lives

| Table | Holds |
|---|---|
| `sites` | Registered workload hosts, `online` flag, last hole-punch |
| `newt` | Per-site agent credentials (secret is argon2-hashed) |
| `clients` | Enrolled devices (Olm) |
| `siteResources` | **Private resources** — destination, port, mode, alias, FQDN |
| `resources` | Public/proxy resources — a different feature |
| `networks` + `siteNetworks` | Which site(s) serve a given resource |
| `userSiteResources` / `clientSiteResources` | Explicit grants |
| `clientSiteResourcesAssociationsCache` | **Derived** — which client may reach which resource |

### The rule: never write to the database directly

`clientSiteResourcesAssociationsCache` is derived state that Pangolin rebuilds
only when a resource is mutated *through its own code paths*. A hand-written
`UPDATE` produces a resource that is correct in every table you inspect and
still invisible to every client, because the cache was never recomputed. There
is no periodic reconciler that will eventually fix it.

Mutate through the blueprint (preferred) or the API. Both rebuild site
bindings and grants transactionally.

---

## 6. Access control

Access is the union of:

- **Implicit admin** — org admins reach everything. Admin is *not* expressible
  as a grant; blueprints containing `roles: [Admin]` are rejected with
  `Admin role cannot be included in roles`.
- **`users:`** — by account email. Grants every device belonging to that user.
- **`roles:`** — by role name, e.g. `Member`.
- **`machines:`** — by client `niceId`. Grants one specific device.

Grant to `users:` for "my devices"; reserve `machines:` for pinning a resource
to a single device.

A grant is only half of it — the resource must also be bound to a site that is
**online**. A resource on an offline site is unreachable no matter how
generously it is shared, and Pangolin reports this only as a silent failure to
connect.

---

## 7. Failure modes, and what they actually mean

| Symptom | Meaning |
|---|---|
| Block page, client connected | Client DNS override isn't taking effect — you reached the public path. Check the client is actually connected and resolving via its own resolver. |
| Block page, client not connected | Correct behaviour. Connect the client. |
| DNS resolves to alias, connection times out | Site is offline, or newt has no route for this client. Check `sites.online`. |
| `502` from the alias | Tunnel is fine; newt cannot reach the destination. Test from inside newt. |
| TLS warning | Certificate not issued or not distributed — check the `certificates` table. |
| Resource invisible to a device | Missing grant, or a stale association cache from a direct DB write. |

---

## 8. Why this shape

- **Newt over `cloudflared`** — no dependency on a third party terminating
  your TLS, and no per-request egress through someone else's network.
- **Private resources over a VPN-wide tunnel** — access is per-resource and
  per-device. Enrolling a phone does not put it on a flat network with
  everything else.
- **Control plane on a cheap VPS, workloads at home** — the VPS needs only a
  public IP and a few open UDP ports. Compute-heavy work stays on hardware you
  already own, which is the whole point when that hardware is a workstation
  with a large GPU and the VPS is a free-tier ARM instance.

---

## See also

- [deploy-private-resource-from-scratch.md](deploy-private-resource-from-scratch.md) — build one
- [../pangolin/private-resources.blueprint.yaml](../pangolin/private-resources.blueprint.yaml) — the declarative source of truth
- [../PANGOLIN-SETUP.md](../PANGOLIN-SETUP.md) — control-plane bring-up
- [../SECRETS-MANAGEMENT.md](../SECRETS-MANAGEMENT.md) — credential hydration
