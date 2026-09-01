# Tasks — GCP Opt-In Completion v1

> 3 sections, 4 tasks. All tasks PASSED before
> `openspec archive 2026-09-01-gcp-opt-in-completion-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [x] **A.1** Author `proposal.md` + `tasks.md` + spec delta
- [x] **A.2** `uv run openspec validate 2026-09-01-gcp-opt-in-completion-v1 --strict` exits 0

## Phase B — Enable the 6 GCP mirror stacks in `deployment-choice.yaml` (§1, 1 task)

- [x] **B.1** Set the 6 GCP stacks to `enabled: true`:
  - `gcp-gemini-vertex: true`
  - `gcp-gemma-unsloth: true`
  - `gcp-bigquery-mirror: true`
  - `gcp-gcs-bucket: true`
  - `gcp-secret-manager: true`
  - `gcp-cloud-run: true`

## Phase C — Audit + spec delta (§2-§3, 2 tasks)

- [x] **C.1** Audit the 6 stacks — all follow the 6-file GOLD_STANDARD pattern
- [x] **C.2** Spec delta to `deployment-control-panel` — 2 ADDED Requirements

---

*Last updated by build subagent at 2026-09-01.*