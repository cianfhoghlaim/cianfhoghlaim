# pangolin-integration-api — Agent Routing

> TBD - created by archiving change 2026-08-17-hygiene-drift-cleanup-v1. Update Purpose after archive.

## Routing

Load this AGENTS.md when you need to:
- Wire a PocketID OIDC client to a new Pangolin-routed service
- Diagnose `*.cianfhoghlaim.ie` cert errors (certResolver, HTTP-01 vs DNS-01)
- Add a Pangolin `siteResources` row via the integration API

For platform-wide context, load [`../../../AGENTS.md`](../../../AGENTS.md).

## Quick start

```bash
bun run scripts/check-edge-tls.sh --strict --all   # verify all 10 hostnames healthy
bun run scripts/wire-pocketid-pangolin-komoid.sh   # bootstrap OIDC + PocketID + Komodo
bun run scripts/wire-pocketid-resource-idp.sh --all  # bind PocketID to all Pangolin Resources
```

## Key sources

| Path | Why it matters |
|:--|:--|
| `docs/PANGOLIN_OIDC_CONFIG.md` | Canonical OIDC config doc (added by `2026-08-17-hygiene-drift-cleanup-v1`) |
| `bonneagar/pangolin/config/traefik/traefik_config.yml` | The 10 `*.cianfhoghlaim.ie` Traefik routers + certResolver declarations |
| `bonneagar/pangolin/agent-fleet.yaml` | The 12-agent fleet's Pangolin private-resource bindings |
| `bonneagar/pangolin/private-resources.blueprint.yaml` | The canonical blueprint for the private resources |

## Adjacent specs

- [`../infrastructure-stacks`](../infrastructure-stacks/spec.md) — the 94 Docker Compose stacks umbrella
- [`../bonneagar-iac-merge`](../bonneagar-iac-merge/spec.md) — the unified TypeScript IaC at `bonneagar/iac/`
- [`../agent-platform-cluster`](../agent-platform-cluster/spec.md) — the 8-stack cluster that uses Pangolin for SSO

## DO NOT

- **Never** use `certResolver: letsencrypt-dns` — our setup is HTTP-01 only.
- **Never** wire a PocketID OIDC client without `require_pkce: true` + `pkce_challenge_method: S256`.
- **Never** disable Auto Provision Users — operators manually approving every new user breaks the SSO flow.

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`infrastructure-stacks`](../../../.agents/skills/infrastructure-stacks/SKILL.md) | The 6-file GOLD_STANDARD pattern + stack-doctor CI gate |
| [`pangolin`](../../../.agents/skills/pangolin/SKILL.md) | Fossorial Pangolin reverse-proxy operations |
| [`komodo-gitops`](../../../.agents/skills/komodo-gitops/SKILL.md) | The 4 resource-syncs + 8-phase bootstrap state machine |
| [`secrets-management`](../../../.agents/skills/secrets-management/SKILL.md) | Infisical + Locket + mise three-way secrets contract |