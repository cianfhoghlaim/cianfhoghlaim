# Tasks: 2026-07-03-infrastructure-foundation

## Phase 1 — File authoring (15 min)

- [x] 1.1 Create `bonneagar/ocr/models/llama_swap_config.yaml` — 14 GGUF entries from `VISION_MODELS`
- [x] 1.2 Verify symlink: `file bonneagar/stacks/llama-swap/config.yaml` returns "UTF-8 text" (not "broken symbolic link")
- [x] 1.3 Create `stedding/huggingface/gguf/README.md` + `.gitkeep`
- [x] 1.4 Create `stedding/huggingface/unsloth/README.md` + `.gitkeep`
- [x] 1.5 Create `stedding/huggingface/mlx-community/README.md` + `.gitkeep`
- [x] 1.6 Create `scripts/download_mlx_models.py` — loops `VISION_MODELS.mlx_id`, defaults to host-path cache
- [x] 1.7 Edit `scripts/download_unsloth_models.py` — change `DEFAULT_CACHE_DIR` to host-path
- [x] 1.8 Edit `bonneagar/stacks/dagster/Dockerfile.dagster` — add 12 Python packages + 4 system deps
- [x] 1.9 Edit `cianfhoghlaim/pyproject.toml` — extend `memory` extra; add `ocr-vision-full` extra; add `dev-with-vision` extra; update `all`
- [x] 1.10 Edit `mise.toml` — fix 2 compose paths; update `download-models` description; add `download-mlx` + `download-models:dry-run` tasks
- [x] 1.11 Write `openspec/changes/2026-07-03-infrastructure-foundation/proposal.md` (this file)
- [x] 1.12 Write `openspec/changes/2026-07-03-infrastructure-foundation/tasks.md` (this file)
- [x] 1.13 Write `openspec/changes/.../specs/meaisinfhoghlaim-ocr-htr/spec.md` (delta)
- [x] 1.14 Write `openspec/changes/.../specs/dagster-5-layer-component-architecture/spec.md` (delta)

## Phase 2 — Validate (2 min)

- [ ] 2.1 `openspec validate 2026-07-03-infrastructure-foundation --strict` — must say "is valid"
- [ ] 2.2 `bun run validate-stacks` — must pass (no stack-image changes)
- [ ] 2.3 `mise run lint:skills` — must show 123/123

## Phase 3 — Smoke tests (5 min)

- [ ] 3.1 `file bonneagar/stacks/llama-swap/config.yaml` → "UTF-8 text" (not "broken symbolic link")
- [ ] 3.2 `ls stedding/huggingface/{gguf,unsloth,mlx-community}/` → 3 directories exist (each with `.gitkeep` and `README.md`)
- [ ] 3.3 `python -c "import yaml; yaml.safe_load(open('bonneagar/ocr/models/llama_swap_config.yaml'))"` — no YAML errors
- [ ] 3.4 `python scripts/download_unsloth_models.py --dry-run` — prints 14 model IDs from `VISION_MODELS`
- [ ] 3.5 `python scripts/download_mlx_models.py --dry-run` — prints 4 model IDs from `VISION_MODELS`
- [ ] 3.6 `mise run llama-swap:download-models:dry-run` — chained dry-run succeeds
- [ ] 3.7 `mise tasks | grep llama-swap` — shows the 6 llama-swap tasks (up, down, logs, download-models, download-mlx, download-models:dry-run, health)

## Phase 4 — Refresh HEALTH_REPORT (5 min)

- [ ] 4.1 Append Session 8 entry at the top of `bonneagar/stacks/HEALTH_REPORT.md`
  (technically a Session 8 here; Session 9 will be the post-Change-D entry)
- [ ] 4.2 Note the 4 file categories touched (create+edit counts)
- [ ] 4.3 Note the gate results from Phase 2 + Phase 3

## Phase 5 — Stage commits (5 min)

- [ ] 5.1 `git add bonneagar/ocr/ stedding/huggingface/gguf/README.md stedding/huggingface/unsloth/README.md stedding/huggingface/mlx-community/README.md scripts/download_mlx_models.py`
- [ ] 5.2 `git commit -m "feat(llama-swap): populate GGUF/MLX cache + write llama_swap_config.yaml (14 entries)"`
- [ ] 5.3 `git add scripts/download_unsloth_models.py mise.toml`
- [ ] 5.4 `git commit -m "fix(mise): correct llama-swap download paths; add download-mlx + dry-run tasks"`
- [ ] 5.5 `git add bonneagar/stacks/dagster/Dockerfile.dagster cianfhoghlaim/pyproject.toml`
- [ ] 5.6 `git commit -m "feat(dagster): extend Dockerfile + pyproject with 12 OCR/VLM/memory packages (LC5 + Gemini-6 ready)"`
- [ ] 5.7 `git add openspec/changes/2026-07-03-infrastructure-foundation/`
- [ ] 5.8 `git commit -m "docs(openspec): infrastructure-foundation change (proposal + tasks + 2 spec deltas)"`
- [ ] 5.9 `git push` (only after explicit user request)
