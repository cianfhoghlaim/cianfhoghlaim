# Tasks: GCP Mirror Stacks v1

> 5 phases, ~24 tasks. All tasks MUST pass before `openspec archive`.

## Phase A — OpenSpec scaffolding (5 min)

- [ ] **A.1** Author `proposal.md` + `tasks.md` + `specs/infrastructure-stacks/spec.md`

## Phase B — 6 GCP mirror stacks (60 min)

- [ ] **B.1** `bonneagar/stacks/gcp-gemini-vertex/` — 6-file GOLD_STANDARD pattern (Vertex AI Express mode for Gemini 3.5 Flash)
- [ ] **B.2** `bonneagar/stacks/gcp-gemma-unsloth/` — 6-file pattern (Unsloth Studio on GCE)
- [ ] **B.3** `bonneagar/stacks/gcp-bigquery-mirror/` — 6-file pattern (BigLake Iceberg REST)
- [ ] **B.4** `bonneagar/stacks/gcp-gcs-bucket/` — 6-file pattern (Cloud Storage bucket)
- [ ] **B.5** `bonneagar/stacks/gcp-secret-manager/` — 6-file pattern (Secret Manager + Workload Identity Federation)
- [ ] **B.6** `bonneagar/stacks/gcp-cloud-run/` — 6-file pattern (Cloud Run service)

## Phase C — `deployment-choice.yaml` (5 min)

- [ ] **C.1** Add `enabled_stacks: gcp-gemini-vertex: false` + 5 more (opt-in default)
- [ ] **C.2** Add `enabled_models: gemini-3.5-flash: false` + `gemini-3.5-flash-lite: false` (opt-in via MODEL_PROFILE=hackathon)
- [ ] **C.3** Add `enabled_models: gemma-4-26b-a4b: true` + `gemma-4-e4b: true` (already-on via Unsloth Studio)

## Phase D — `mise.toml` (5 min)

- [ ] **D.1** Add 6 `stack:gcp-*` tasks (one per new stack)

## Phase E — Validation (5 min)

- [ ] **E.1** `mise run openspec:validate 2026-08-31-gcp-mirror-stacks-v1 --strict`
- [ ] **E.2** `mise run stacks:gold-standard-audit` — verify the 6 GCP stacks pass the GOLD_STANDARD check
- [ ] **E.3** `mise run sync:all`

---

*Last updated by build subagent at 2026-08-31.*