# Pre-Teardown Snapshot — Phase 0

Captured before the clean-slate re-architecture of Pangolin + Komodo + Newt + Periphery.

## mbp (bunchloch / OrbStack)

### Pangolin / Komodo / Periphery (TO BE REMOVED)
| Container | Status | Ports |
|:--|:--|:--|
| `newt` | Up 11 hours | 2112/tcp |
| `newt-locket` | Restarting (loop) | — |
| `komodo-core` | Up 3 days (healthy) | 0.0.0.0:9120→9120 |
| `komodo-ferretdb` | Up 3 days (healthy) | 8088/tcp, 27017-27018/tcp |
| `komodo-postgres` | Up 3 days (healthy) | 5432/tcp |
| `komodo-periphery` | Up 3 days | 8120/tcp |

### Unrelated stacks (PRESERVE)
- oideachais: frontend/api/dagster, litellm, cognee, lakehouse (garage/lakekeeper/lance/ferretdb-postgres), langfuse, lancedb, llama-swap, browser (stagehand-proxy/litellm/grid), convex, aleyum (postgres/dragonfly), croilar-postgres, dagger-engine

## arm1-oci (Ubuntu 24.04 / docker compose)

### Pangolin stack (TO BE REMOVED)
| Container | Status | Ports |
|:--|:--|:--|
| `pangolin` | Up 3 days (healthy) | 3000/3001 internal |
| `pangolin-postgres` | Up 3 days (healthy) | 5432/tcp |
| `pangolin-locket` | Up 3 days (healthy) | — |
| `gerbil` | Up 27 hours | :80, :443, :51820/udp, :3004 metrics |
| `traefik` | Up 27 hours | (shares gerbil net ns) |
| `pocket-id` | Up 9 days (healthy) | 1411/tcp |
| `tinyauth` | Up 10 days (healthy) | 3000/tcp |
| `newt-arm1-oci` | Up 9 hours | 2112/tcp (WireGuard broken) |
| `arm1.oci-periphery` | Up 2 weeks | 8120/tcp |
| `arm1.oci-locket` | Up 2 weeks (healthy) | — |

### PRESERVE
- **infisical** (backend+db+redis) — KMS partly broken but core auth works
- **calcom** (web+db+redis) — calendar stack
- **vikunja** (web+db) — task management
- **n8n** (worker+db+redis) — workflows (unhealthy but keep data)
- **glance** — dashboard
- **changedetection** — web monitor
- **bytebase-pg** — DB
- **arm1.oci-beszel-agent** — monitoring

## Pangolin DB state (4 newts, 3 siteResources, 2 networks)

### newts
| id | siteId | version | comment |
|:--|:--|:--|:--|
| `j945b5441fhi7kg` | 4 (bunchloch) | — | orphan from old Pangolin DB |
| `uhk487mkf6hafya` | 4 (bunchloch) | 1.12.5 | stale |
| `pmbv6gh6rzpqi5e` | 1 (mbp) | 1.12.5 | re-registered after 1.19.2 upgrade |
| `h1r2rblq0cwstg1` | 2 (arm1-oci) | 1.12.5 | re-registered after 1.19.2 upgrade |

### siteResources
| name | networkId | defaultNetworkId | fullDomain | orgId |
|:--|:--|:--|:--|:--|
| Komodo | 2 | 2 | komodo.cianfhoghlaim.ie | cianfhoghlaim |
| Infisical Vault | 1 | 1 | infisical.cianfhoghlaim.ie | cianfhoghlaim |
| cal-diy Scheduling | 1 | 1 | calcom.cianfhoghlaim.ie | cianfhoghlaim |

### networks
| networkId | orgId | sites on it |
|:--|:--|:--|
| 1 | kings-college-galway | siteId=2 (arm1-oci), siteId=4 (bunchloch) |
| 2 | cianfhoghlaim | siteId=1 (mbp) |

## Why newts can't bring up WireGuard
- All 4 newts (1.12.5) report "Tunnel connection to server established successfully" but no wg interface comes up
- The `--native` flag (1.13.0) fails with `CreateTUN("newt") failed; /dev/net/tun does not exist`
- OrbStack strips /dev/net/tun from the container's mount namespace by default
- The `test_wg` interface in 1.12.5 logs is just a placeholder, not the real wg

## Wildcard cert (PRESERVE)
- Path: `/opt/pangolin/config/letsencrypt/lego/certificates/_.cianfhoghlaim.ie.crt` + `.key`
- Issuer: Let's Encrypt YR1
- Not Before: Jun 15 10:53:29 2026 GMT
- Not After: Sep 13 10:53:28 2026 GMT (90 days, valid ~88 more days)
- Token: `REDACTED` (manual dashboard-issued; in .env as `CLOUDFLARE_API_TOKEN` / `PANGOLIN_CF_DNS_API_TOKEN`)
