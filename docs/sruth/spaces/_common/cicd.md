# Spaces CI/CD — How to use the reusable workflow

This doc lives at `spaces/_common/cicd.md` so every Space can import it
or link to it from its own README.

The reusable workflow lives at [`infrastructure/ci/spaces-sync.yml`](../../infrastructure/ci/spaces-sync.yml).
It publishes a directory under `spaces/*/` to a Hugging Face Space.

## Quick start

1. **Create a per-Space workflow file** at
   `spaces/<my_space>/.github/workflows/sync.yml`:

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
       uses: ./.github/workflows/spaces-sync.yml
       with:
         space_dir: spaces/<my_space>
         target_space: cianfhoghlaim/<my_space>
         hf_token: ${{ secrets.HF_TOKEN }}
         hf_username: ${{ vars.HF_USERNAME }}
         sdk: gradio
   ```

2. **Configure secrets** in the GitHub repo:
   - `secrets.HF_TOKEN` — Hugging Face PAT with `write` scope on Spaces
   - `vars.HF_USERNAME` — your HF org/username (default: `cianfhoghlaim`)

3. **Push to `main`** — the workflow triggers on any change to
   `spaces/<my_space>/**`.

## Per-SDK recipes

### `sdk: gradio` (the common case)

For a Gradio app with `app.py` and `requirements.txt` at the root of the
Space dir:

```yaml
with:
  space_dir: spaces/my_space
  target_space: cianfhoghlaim/my-space
  sdk: gradio
```

### `sdk: docker` (for Spaces with a `Dockerfile`)

> **Status:** Docker SDK support is documented but the implementation is
> deferred to a follow-up commit. See the open scenarios in
> `openspec/specs/spaces-cicd-pipeline/spec.md`.

For a Space with a `Dockerfile`:

```yaml
with:
  space_dir: spaces/my_space
  target_space: cianfhoghlaim/my-space
  sdk: docker
```

### `sdk: static` (for Evidence-style static dashboards)

For a Space where the built dashboard lives in a subdir (the Evidence
pattern, the `git subtree split` flow):

```yaml
with:
  space_dir: spaces/my_space
  target_space: cianfhoghlaim/my-space-code   # the "code" space (builds)
  static_space: cianfhoghlaim/my-space-site   # the "static" space (serves)
  sdk: static
```

This is the pattern used by `spaces/data-engineering/` (see its prior-art
`.github/workflows/main.yml:1-27`).

## Troubleshooting

- **"HF_TOKEN not set"** — add the secret under
  `Settings → Secrets and variables → Actions → New repository secret`.
- **"Space already exists"** — the workflow is idempotent; a re-run
  rebuilds the existing Space.
- **"Path filter not matching"** — double-check the `paths:` glob in your
  per-Space workflow file matches the actual file path.

## See also

- [`spaces/_common/README.md`](./README.md) — the shared bundle used by
  every deployed Space
- [`openspec/specs/spaces-cicd-pipeline/spec.md`](../../openspec/specs/spaces-cicd-pipeline/spec.md)
  — the canonical capability spec for this workflow
