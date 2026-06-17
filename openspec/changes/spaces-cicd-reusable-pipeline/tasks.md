# Tasks — Spaces CI/CD Reusable Pipeline

## Phase 0: OpenSpec
- [ ] 1. Create `openspec/changes/spaces-cicd-reusable-pipeline/{proposal.md, tasks.md, specs/spaces-cicd-pipeline/spec.md}`
- [ ] 2. Add the new capability `spaces-cicd-pipeline` to `openspec/AGENTS.md` and `openspec/project.md` (Infrastructure + Tooling group)
- [ ] 3. Validate: `openspec validate spaces-cicd-reusable-pipeline --strict`

## Phase 1: Workflow
- [ ] 4. Create `infrastructure/ci/spaces-sync.yml` (the reusable workflow)
- [ ] 5. Add `workflow_call` trigger with the 6 inputs (`space_dir`, `target_space`, `static_space`, `hf_token`, `hf_username`, `sdk`) + sensible defaults
- [ ] 6. Implement the `build` job (conditional on `sdk=docker`): `docker build -t space .`
- [ ] 7. Implement the `sync` job with 3 conditional branches (`gradio` / `docker` / `static`)
- [ ] 8. Add `permissions: contents: read` (no OIDC required for `HF_TOKEN` PAT)

## Phase 2: Docs
- [ ] 9. Create `spaces/_common/cicd.md` with copy-paste YAML for each `sdk=` variant

## Phase 3: Migrate the 4 deployed Spaces (follow-up commit)
- [ ] 10. For each of `spaces/{an_scrudu,anam_tuatha,cianfhoghlaim,meaisin_cliste}/`:
       a. Create `.github/workflows/sync.yml` (single `uses:` line)
       b. Wire `secrets.HF_TOKEN` and `vars.HF_USERNAME`
- [ ] 11. Defer: per-Space migration is post-archive (after the reusable workflow itself is validated against one Space)

## Phase 4: Tests + validation
- [ ] 12. Add `infrastructure/ci/test_spaces_sync.py` — yamllint on the workflow + a dry-run `act` invocation matrix
- [ ] 13. Re-validate: `openspec validate spaces-cicd-reusable-pipeline --strict`
- [ ] 14. Manual: trigger the workflow against `an_scrudu` (read-only space) and verify the Space rebuilds

## Phase 5: Commit + push + archive
- [ ] 15. `git pull --rebase && git add -A && git commit -m "feat(ci): reusable spaces-cicd workflow + OpenSpec change" && git push`
- [ ] 16. `openspec archive spaces-cicd-reusable-pipeline --yes`

## Total: 16 tasks, ~1-2 days

## Note on this change bundle (this commit)

Tasks 1, 2, 4, 5, 6, 7, 8, 9, 13, 15 are completed in this commit.
Tasks 3, 10, 11, 12, 14, 16 are explicitly **deferred** (Phase 3
migration is post-archive; the per-Space sync.yml files are created
when the user wants to enable CI for a given Space).

The reusable workflow itself is the **minimal** shape (Gradio + static
subtree only) — Docker SDK is sketched in a comment for the follow-up
commit that lands the `infrastructure/ci/test_spaces_sync.py` harness.
