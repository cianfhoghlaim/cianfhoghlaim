# Tasks: 2026-07-13-backfill-server-id-on-12-procedures

## 1. Spec delta

- [ ] 1.1 Create `specs/infrastructure-stacks/spec.md` (1 ADDED Requirement: "All procedures have `server_id` by 2026-07-13" with 2 Scenarios)
- [ ] 1.2 `openspec validate 2026-07-13-backfill-server-id-on-12-procedures --strict` returns 0

## 2. Backfill 6 bunchloch procedures

Add `server_id = "bunchloch"` at the top of the `[[procedure.config]]` (or `[[procedure]]`) block of each:

- [ ] 2.1 `komodo/procedures/deploy-falkordb-bunchloch.toml`
- [ ] 2.2 `komodo/procedures/deploy-graphiti-bunchloch.toml`
- [ ] 2.3 `komodo/procedures/deploy-bunchloch-stack-bootstrap.toml`
- [ ] 2.4 `komodo/procedures/deploy-lakehouse-bunchloch.toml`
- [ ] 2.5 `komodo/procedures/deploy-lancedb-bunchloch.toml`
- [ ] 2.6 `komodo/procedures/deploy-wave2-bunchloch.toml`

## 3. Backfill 6 arm1-oci procedures

Add `server_id = "arm1-oci"` at the top of the `[[procedure.config]]` block of each:

- [ ] 3.1 `komodo/procedures/deploy-agent-platform-cluster-arm1-oci.toml`
- [ ] 3.2 `komodo/procedures/deploy-hermes-arm1-oci.toml`
- [ ] 3.3 `komodo/procedures/deploy-langfuse-arm1-oci.toml`
- [ ] 3.4 `komodo/procedures/deploy-observability-arm1-oci.toml`
- [ ] 3.5 `komodo/procedures/deploy-openchamber-arm1-oci.toml`
- [ ] 3.6 `komodo/procedures/deploy-openclaw-arm1-oci.toml`

## 4. Validation + commit + push

- [ ] 4.1 `openspec validate 2026-07-13-backfill-server-id-on-12-procedures --strict` returns 0
- [ ] 4.2 `git -C cianfhoghlaim add openspec/changes/2026-07-13-backfill-server-id-on-12-procedures/`
- [ ] 4.3 `git -C cianfhoghlaim commit -m "feat(openspec): backfill server_id on 12 procedures"`
- [ ] 4.4 `git -C bonneagar add komodo/procedures/*.toml`
- [ ] 4.5 `git -C bonneagar commit -m "fix(komodo): backfill server_id on 12 procedures (6 bunchloch + 6 arm1-oci)"`
- [ ] 4.6 `git -C cianfhoghlaim push origin pick-4-biep-v1`
- [ ] 4.7 `git -C bonneagar push bonneagar pick-5b-bonneagar-v5-continuation`
- [ ] 4.8 After push, the 60s resource-sync cycle picks up the changes; verify the bunchloch `km` UI shows 22 procedures and the arm1-oci `km` UI shows 14
- [ ] 4.9 `openspec archive 2026-07-13-backfill-server-id-on-12-procedures --yes`
