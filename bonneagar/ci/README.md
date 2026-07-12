# Reusable Spaces CI/CD workflow

This workflow is a **single source of truth** for publishing any directory
under `spaces/*/` to a Hugging Face Space. It is invoked from a per-Space
`.github/workflows/sync.yml` via a `uses:` reference.

## Inputs

| Input | Required | Default | Description |
|:--|:-:|:-:|:--|
| `space_dir` | yes | — | Subdir to push (e.g. `spaces/an_scrudu`) |
| `target_space` | yes | — | HF Space slug (e.g. `cianfhoghlaim/an-scrudu`) |
| `static_space` | no | `""` | If set, also push `dashboard/` subdir to this static space via `git subtree split` |
| `hf_token` | yes | — | PAT from `secrets.HF_TOKEN` |
| `hf_username` | yes | — | HF org/user from `vars.HF_USERNAME` |
| `sdk` | no | `gradio` | `gradio` \| `docker` \| `static` (the `static` mode is the Evidence-subtree pattern) |

## Usage from a per-Space workflow

Drop this into `spaces/<my_space>/.github/workflows/sync.yml`:

```yaml
name: Sync <my_space> to HF
on:
  push:
    branches: [main]
    paths:
      - 'spaces/<my_space>/**'
  workflow_dispatch:

jobs:
  sync:
    uses: ./.github/workflows/spaces-sync.yml    # see infrastructure/ci/spaces-sync.yml
    with:
      space_dir: spaces/<my_space>
      target_space: cianfhoghlaim/<my_space>
      hf_token: ${{ secrets.HF_TOKEN }}
      hf_username: ${{ vars.HF_USERNAME }}
      sdk: gradio
```

## Patterns

This workflow absorbs two prior-art patterns:

1. **Static subtree sync** (from `spaces/data-engineering/.github/workflows/main.yml:1-27`):
   `git subtree split --prefix dashboard main:main` + `git push -f
   https://$TOKEN@huggingface.co/spaces/$USERNAME/$STATIC_SPACE`. Used when
   `sdk: static` and `static_space` is set.
2. **Hugging Face `huggingface_hub` API upload** (modern equivalent of
   `huggingface-cli upload`). Used for `sdk: gradio` and `sdk: docker`.

## When to use which `sdk`

- `sdk: gradio` — your Space is a Gradio app (the default for `spaces/an_scrudu`,
  `spaces/anam_tuatha`, `spaces/cianfhoghlaim`, `spaces/meaisin_cliste`)
- `sdk: docker` — your Space has a `Dockerfile` (the `spaces/data-engineering/dashboard/Dockerfile`
  pattern; Docker SDK is deferred to follow-up commit)
- `sdk: static` — your Space is a static dashboard (Evidence pattern, the
  `git subtree split` flow)

## Why this is reusable

Before this workflow, every Space needed its own copy of the
`git push -f https://...` logic. Bugs had to be fixed in 4+ places. New
security hardening (e.g. switching from `git push` to `huggingface_hub`
API) required touching all 4 workflows. This single file is now the
canonical implementation.
