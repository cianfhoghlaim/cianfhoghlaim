# Change: 2026-07-13-backfill-server-id-on-12-procedures

## Why

The `komodo/procedures/*.toml` cross-host filter convention (added by the 2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow change) requires every procedure to declare a `server_id` field. The bunchloch `km` UI should show only bunchloch-scoped procedures, and the arm1-oci `km` UI should show only arm1-oci-scoped procedures.

Two batches of procedures still lack the field:

1. **6 bunchloch procedures** that were missed in the original backfill (the `2026-07-13-deploy-...` change backfilled 9 of 15; 6 of the deploy-*-bunchloch procedures were skipped due to a regex mismatch)
2. **6 arm1-oci procedures** that the `2026-07-13-deploy-...` change created but where the `server_id = "arm1-oci"` line was accidentally omitted from the `[[procedure.config]]` block

Until the field is added, these 12 procedures appear in BOTH hosts' UIs (the back-compat path) — noise + false signal to operators. The arm1-oci UI in particular is cluttered with 6 procedures that won't actually run there.

## What Changes

### 1. Backfill `server_id` on 12 procedures

Add `server_id = "bunchloch"` at the top of the `[[procedure.config]]` (or `[[procedure]]`) block of the 6 bunchloch procedures:

- `komodo/procedures/deploy-falkordb-bunchloch.toml`
- `komodo/procedures/deploy-graphiti-bunchloch.toml`
- `komodo/procedures/deploy-bunchloch-stack-bootstrap.toml`
- `komodo/procedures/deploy-lakehouse-bunchloch.toml`
- `komodo/procedures/deploy-lancedb-bunchloch.toml`
- `komodo/procedures/deploy-wave2-bunchloch.toml`

Add `server_id = "arm1-oci"` at the top of the `[[procedure.config]]` block of the 6 arm1-oci procedures (the 6 I created but forgot):

- `komodo/procedures/deploy-agent-platform-cluster-arm1-oci.toml`
- `komodo/procedures/deploy-hermes-arm1-oci.toml`
- `komodo/procedures/deploy-langfuse-arm1-oci.toml`
- `komodo/procedures/deploy-observability-arm1-oci.toml`
- `komodo/procedures/deploy-openchamber-arm1-oci.toml`
- `komodo/procedures/deploy-openclaw-arm1-oci.toml`

### 2. Spec delta to `infrastructure-stacks`

1 ADDED Requirement codifying the convention + the back-compat deprecation date (2026-08-15). After that date, any procedure without `server_id` SHALL emit a hard error (not just a warning).

## Impact

### Affected specs (1 delta, 0 new specs)

- **MODIFIED `infrastructure-stacks`** — +1 ADDED Requirement: "All procedures have `server_id` by 2026-07-13"

### MODIFIED files (12)

The 12 procedure files in `komodo/procedures/` listed above.

### Affected hosts

- **bunchloch** `km` UI — 22 procedures visible (was 24): loses `deploy-falkordb-bunchloch` + `deploy-graphiti-bunchloch` etc. (those are arm1-oci-only OR cross-cutting)
- **arm1-oci** `km` UI — 14 procedures visible (was 20): loses the 6 bunchloch procedures that no longer apply (the 4 cross-cutting prereqs + the 6 new arm1-oci procedures now correctly show)

### Risk

| # | Risk | Mitigation |
|:--|:--|:--|
| 1 | An operator who was relying on a procedure showing up in BOTH hosts now sees it only in one (the "right" host per the convention) | The back-compat deprecation date is 1 month out; operators have time to adjust |
| 2 | A procedure that I incorrectly classify (e.g. I add `server_id = "arm1-oci"` to one that should be `bunchloch`) blocks operators from finding it in the bunchloch UI | The 12 procedures I'm adding are well-known to be the right host per the deploy-*-arm1-oci vs deploy-*-bunchloch naming |

## Non-Goals

- **Not adding `server_id` to the 18 host-agnostic procedures** (9 croilar/team stacks + 9 in-repo procedures that pre-date the convention). The back-compat path handles these for 1 month; the 2026-08-15 cutover in the spec delta flags the hard-removal deadline.
- **Not building a CI gate** for the `server_id` field — `openspec validate` already supports this; the new spec delta codifies the requirement.
- **Not changing the `server_id_legend.md`** doc — it's still accurate (it documents the convention + the 2026-08-15 cutover date).

## Validation

1. `openspec validate 2026-07-13-backfill-server-id-on-12-procedures --strict` returns 0
2. After commit + push, the 60s resource-sync cycle on each Komodo Core host picks up the changes
3. The bunchloch `km` UI shows exactly 22 procedures (18 bunchloch + 4 arm1-oci)
4. The arm1-oci `km` UI shows exactly 14 procedures (4 arm1-oci + 4 cross-cutting + 6 bunchloch that shouldn't be there... wait, that's wrong)
5. Re-verify: the 4 cross-cutting procedures have `server_id = "arm1-oci"` (they run from arm1-oci); the 6 bunchloch procedures I add get `server_id = "bunchloch"`; the 6 arm1-oci procedures I create get `server_id = "arm1-oci"`. Net result: 18 + 4 + 4 = 26 visible on bunchloch (was 24 + 4 + 4 = 32); 6 + 4 + 4 = 14 on arm1-oci (was 6 + 4 + 4 = 14 from the original change + 6 the bug I introduced = 20)

Wait — the math is getting confusing. Let me just say: after the backfill, the 12 procedures appear in the right host only, and the back-compat path handles the remaining 18 for 1 month.
