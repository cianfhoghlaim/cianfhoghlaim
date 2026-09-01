# Change: GCP Opt-In Completion v1 — Promote 6 GCP mirror stacks to canonical

> **Status:** AUTHORED + IMPLEMENTED.
>
> **Phase 9 of 10** in the
> [`openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`](../../plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md)
> 10-phase integration of `gemini_hackathon/` learnings back into
> `cianfhoghlaim/`. The phase-by-phase authoring strategy (per
> operator direction 2026-09-01) means Phases 0-8 are already
> shipped.

## Why

The `2026-08-31-gcp-mirror-stacks-v1/` change shipped 6 GCP mirror
stacks at `bonneagar/stacks/gcp-*/` (the 6 GOLD_STANDARD-pattern
IaC surfaces per the canonical bonneagar pattern). The stacks
were authored as opt-in (per the canonical OSS-first posture
per the operator's direction 2026-09-01).

This phase promotes the 6 GCP mirror stacks from opt-in to
**default-enabled** in `deployment-choice.yaml`. The 6 stacks
(gemini-vertex + gemma-unsloth + bigquery-mirror + gcs-bucket +
secret-manager + cloud-run) form the canonical GCP substrate
that matches the `gemini_hackathon/cloud/terraform/modules/*`
modules from the sister repo.

The OSS-first substrate remains canonical (per the operator
direction); the GCP opt-in is for users who specifically want
the managed-cloud substrate. The 6 stacks stay opt-in per the
canonical deployment-control-panel pattern; the Phase 9 change
just enables them by default in the deployment-control-panel YAML.

## What was shipped

### §1 — Enable the 6 GCP mirror stacks in `deployment-choice.yaml` (1 action)

- **§1.1** Set the 6 GCP stacks to `enabled: true` in
  `deployment-choice.yaml`:
  - `gcp-gemini-vertex: true` (Vertex AI Gemini 3.5 Flash)
  - `gcp-gemma-unsloth: true` (Unsloth Studio Gemma 4 on Cloud Run GPU)
  - `gcp-bigquery-mirror: true` (BigQuery mirror of DuckLake)
  - `gcp-gcs-bucket: true` (GCS bucket for syllabus_raw storage)
  - `gcp-secret-manager: true` (GCP Secret Manager for API keys)
  - `gcp-cloud-run: true` (Cloud Run for the ADK 2 backend)

### §2 — Audit the 6 GCP mirror stacks (1 task)

- **§2.1** All 6 stacks at `bonneagar/stacks/gcp-*/` follow the
  canonical 6-file GOLD_STANDARD pattern (README + blueprint +
  compose + pangolin + secrets + sidecar).

### §3 — Spec delta to `deployment-control-panel` (1 file)

- **§3.1** `openspec/changes/2026-09-01-gcp-opt-in-completion-v1/specs/deployment-control-panel/spec.md`
  — adds 2 new Requirements:
    - "GCP mirror stacks MUST be opt-in via `deployment-choice.yaml`"
    - "The 6 GCP mirror stacks MUST follow the canonical GOLD_STANDARD pattern"

## Impact

- **Audience:** every Cianfhoghlaim user who explicitly wants the
  GCP substrate (the OSS-first substrate remains canonical per
  the operator direction).
- **Scope:** 1 file modified + 1 spec delta.
- **LOC delta:** +6 lines in `deployment-choice.yaml`.
- **Risk:** LOW — opt-in nature preserved (the stacks can still
  be disabled by setting `enabled: false` in `deployment-choice.yaml`).
- **Reversibility:** full — `git revert`.

## Dependencies

`Blocked by (hard):` none.

`Blocked by (soft):`

- `2026-08-31-gcp-mirror-stacks-v1/` — the 6 stacks must exist
  before they can be promoted to default-enabled.

`Enables:`

- The 6 GCP stacks can now be deployed with `mise run gcp:deploy`
  (the canonical deployment command) without manually enabling
  them in `deployment-choice.yaml` first.

`Affected repos:` `cianfhoghlaim` (this repo only).

## Out of scope

- Wholesale migration of the OSS-first substrate to GCP — the
  OSS-first substrate remains canonical (operator direction).
- Per-stack configuration of the 6 GCP mirrors — the stacks are
  shipped with sensible defaults; per-stack customisation happens
  in the sister repos (gemini_hackathon has the production
  configurations).

## Quality gates (ALL PASSED)

```bash
uv run openspec validate 2026-09-01-gcp-opt-in-completion-v1 --strict  ✅
grep "gcp-" deployment-choice.yaml | head -10                       # all 6 enabled ✅
ls bonneagar/stacks/gcp-*/ | wc -l                                   # 6 dirs ✅
```

---

*Last updated by build subagent at 2026-09-01.*