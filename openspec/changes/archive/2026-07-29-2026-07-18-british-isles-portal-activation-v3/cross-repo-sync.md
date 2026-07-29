# cross-repo-sync — british-isles-portal-activation-v3

This change touches 2 repos per the
`2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1` convention.

## Repo 1: cianfhoghlaim (this repo)

Branch: `feat/2026-07-18-british-isles-portal-activation-v3`
Push target: `origin`

| Commit # | Phase | Message |
|--:|---|---|
| 1 | Phase 0 | `openspec(changes): british-isles-portal-activation-v3 skeleton + 8 spec deltas (R11-R25)` |
| 2 | Phase 1 | `web(leaving-cert): A2UI catalog (11 entries) + central portal entry + British Isles map routes` |
| 3 | Phase 2 | `web(leaving-cert) + notebooks: marimo-on-Cloudflare + R2 bucket + MotherDuck Dive + daily Flight` |
| 4 | Phase 3 | `web(leaving-cert): Storybook 18 stories + Langfuse + MLflow + RAGAS` |
| 5 | Phase 4 | `web(leaving-cert): PDF-REF items R21-R25 (machine-readable + design-tokens + MCP server + Pocket ID SSO + feature flags)` |

## Repo 2: bonneagar (separate worktree)

Branch: `feat/2026-07-18-portal-cloudflare-r2-stack-v3`
Push target: `origin`

| Commit # | Message |
|--:|---|
| 1 | `iac(stacks): portal-cloudflare-r2 stack (6-file GOLD_STANDARD) + Komodo sync + Pangolin route` |

## Order of operations

1. **First** push the cianfhoghlaim commit series (commits 1–5).
2. **Then** push the bonneagar commit (commit 1).
3. **Then** open the PRs in the order: cianfhoghlaim PR → bonneagar PR.
4. **Then** deploy via `bun run iac:deploy --stack portal-cloudflare-r2` from the bonneagar worktree.
5. **Then** archive the openspec change: `bun run spec:archive 2026-07-18-british-isles-portal-activation-v3 --yes`.

## Why two repos

- **`cianfhoghlaim`** owns the web app surfaces + BAML/CocoIndex/notebooks
  (where the 5 Requirements R11–R13 + R15–R25 land).
- **`bonneagar`** owns the IaC subtree (stacks + Komodo + Pangolin
  resource-syncs) where the `portal-cloudflare-r2` stack + the
  `portal.cianfhoghlaim.ie` route + the Komodo sync land (R14 — R2 +
  Pages + Pangolin, **no Worker** since signed URLs come from Hono).

## Hard blockers

| Blocker | Owner change | Resolution path |
|---|---|---|
| `conic-leaving-cert` Convex deployment | `2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow` | Must archive BEFORE Phase 5 (`iac:deploy`) of this change can run |
| Pocket ID OIDC audiences `leaving_cert_portal` + `portal` | `bonneagar/iac/pocketid/audiences.yaml` | Adds the 2 new audiences before Phase 5 (`iac:deploy`) |
