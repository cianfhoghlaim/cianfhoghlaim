# Tasks — 2026-08-22-litellm-1.91-to-1.97-image-bump-v1

## 1. Bump

- [ ] 1.1 Edit `pyproject.toml`: `litellm>=1.91,<1.98` → `litellm>=1.97,<1.98`. Run `uv sync`. Verify `uv pip show litellm | grep Version` prints `1.97.x`.
- [ ] 1.2 Edit `bonnegar/stacks/litellm/compose.yaml`: image `ghcr.io/berriai/litellm-database:v1.91.0` → `:v1.97.0`.
- [ ] 1.3 Run `docker compose -f bonnegar/stacks/litellm/compose.yaml -f bonnegar/stacks/litellm/sidecar.yaml --env-file .env pull` to download the new image.

## 2. Pangolin path addition

- [ ] 2.1 Edit `bonnegar/stacks/litellm/pangolin.yaml`: add `/v1/messages` (Rust v1.95.0 endpoint) under the LITELLM private resource.

## 3. Regenerate config

- [ ] 3.1 Run `mise run ml:litellm:regenerate` to refresh `bonnegar/stacks/litellm/config/config.yaml` from the centralized MODEL_REGISTRY.

## 4. Verify

- [ ] 4.1 Restart litellm: `docker compose -f bonnegar/stacks/litellm/compose.yaml -f bonnegar/stacks/litellm/sidecar.yaml --env-file .env up -d`.
- [ ] 4.2 `curl -s http://localhost:4000/v1/models` returns the regenerated model list.
- [ ] 4.3 `mise run data:status` reports litellm ONLINE.

## 5. openspec

- [ ] 5.1 `openspec validate 2026-08-22-litellm-1.91-to-1.97-image-bump-v1 --strict` exits 0.
- [ ] 5.2 `openspec archive 2026-08-22-litellm-1.91-to-1.97-image-bump-v1 --yes`.

## 6. Commit + push

- [ ] 6.1 Stage the modified files + commit with the openspec change-id in the body.
- [ ] 6.2 `git push origin HEAD`.

## 7. Documentation

- [ ] 7.1 Update `.agents/skills/litellm/SKILL.md` with the v1.97 features (MCP Gateway, OAuth 2.0 v2, Rust /v1/messages).
- [ ] 7.2 Update `AGENTS.md` priority commands table — `mise run ml:litellm:regenerate` is now auto-run in CI.
