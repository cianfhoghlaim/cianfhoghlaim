# 2026-08-02-biep-v3-changedetection-monitors-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify the BIEP v3 batch (Phases 0-5) merged
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Create the 7 new ChangeDetection.io monitors

- [ ] Create `bonnegar/stacks/changedetection/monitors/ncca_monitor.yaml`
  (Ireland NCCA + SEC) — 5 watched pages
- [ ] Create `bonnegar/stacks/changedetection/monitors/sqa_monitor.yaml`
  (Scotland SQA) — 5 watched pages
- [ ] Create `bonnegar/stacks/changedetection/monitors/wjec_monitor.yaml`
  (Wales WJEC) — 5 watched pages
- [ ] Create `bonnegar/stacks/changedetection/monitors/ccea_monitor.yaml`
  (Northern Ireland CCEA) — 5 watched pages
- [ ] Create `bonnegar/stacks/changedetection/monitors/jersey_monitor.yaml`
  (Jersey) — 3 watched pages
- [ ] Create `bonnegar/stacks/changedetection/monitors/guernsey_monitor.yaml`
  (Guernsey) — 3 watched pages
- [ ] Create `bonnegar/stacks/changedetection/monitors/iom_monitor.yaml`
  (Isle of Man) — 3 watched pages

## Stage 2 — Update the ChangeDetection.io config

- [ ] Edit `bonnegar/stacks/changedetection/stacks/changedetection.compose.yaml`
  to declare the 7 new webhook routes
- [ ] Update `mise.toml` to add 7 new `change-detection:monitor:<slug>` tasks

## Stage 3 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-08-02-biep-v3-changedetection-monitors-v1/specs/infrastructure-stacks/spec.md`
- [ ] Run `openspec validate 2026-08-02-biep-v3-changedetection-monitors-v1 --strict`
- [ ] Commit the change on a dedicated branch
- [ ] Open a PR on `origin/main` referencing this change
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-08-02-biep-v3-changedetection-monitors-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol