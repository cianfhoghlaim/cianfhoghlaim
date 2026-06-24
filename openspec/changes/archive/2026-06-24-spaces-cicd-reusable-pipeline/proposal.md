# Reusable Hugging Face Spaces CI/CD Pipeline

## Why

We have 4 deployed HF Spaces under `spaces/{an_scrudu,anam_tuatha,cianfhoghlaim,meaisin_cliste}/`
plus 2 inherited prior-art repos (`spaces/data-engineering/`, `spaces/anti-phish/`)
and an active Build-Small-2026 submission pipeline. Each Space needs the same
pattern: build the Space, push to a HF Space, and for the Evidence-style static
dashboard, push only a subdir to a separate "static" space.

The prior-art `spaces/data-engineering/.github/workflows/main.yml:1-27` shows the
canonical pattern (`git subtree split --prefix dashboard main:main` + `git push -f
https://$TOKEN@huggingface.co/spaces/...`). It is hard-coded to one subdir and
one target space, and lives inside the prior-art repo (which is not a long-term
canonical home for our CI).

This change promotes that pattern to a **reusable workflow** under
`infrastructure/ci/` so every Space can call it the same way and we get a single
place to fix bugs, swap to the new `huggingface_hub` CLI upload, or add Slack
notifications.

## What Changes

### 1. New reusable workflow `infrastructure/ci/spaces-sync.yml`

Inputs (with defaults):

- `space_dir` (required) — the subdir to push (e.g. `spaces/an_scrudu`)
- `target_space` (required) — HF Space slug (e.g. `cianfhoghlaim/an-scrudu`)
- `static_space` (default `""`) — if set, push only the `dashboard/` subdir to
  this second "static" space using `git subtree split` (the Evidence pattern)
- `hf_token` (required) — from `secrets.HF_TOKEN`
- `hf_username` (required) — from `vars.HF_USERNAME`
- `sdk` (default `gradio`) — HF Space SDK (`gradio` | `docker` | `static`)

Two jobs: `build` (runs the Space's `Dockerfile` if `sdk=docker`, else
`pip install`) and `sync` (uses `huggingface-cli upload` for `sdk=docker`; uses
`git subtree split + push -f` for `sdk=static`; uses `huggingface_hub` API for
`sdk=gradio`).

### 2. New `spaces/_common/cicd.md`

Documents how to call the reusable workflow from any new Space, with
copy-paste YAML for each `sdk=` variant.

### 3. MODIFY the 4 deployed Spaces to call the new workflow

For each of `spaces/{an_scrudu,anam_tuatha,cianfhoghlaim,meaisin_cliste}/`,
create (if not already present) `.github/workflows/sync.yml` containing a
single `uses:` line pointing at `infrastructure/ci/spaces-sync.yml`. This
standardizes all 4 deploys on one workflow.

## Out of scope (deferred)

- Concrete `spaces/<x>/.github/workflows/sync.yml` per-Space files (Phase 4 of
  this change lives in a follow-up commit after this OpenSpec change is
  approved and the reusable workflow is validated end-to-end)
- Slack/Discord notifications
- Auto-versioning of the Space SDK version

## Spec Deltas

- ADDED `spaces-cicd-pipeline` capability
