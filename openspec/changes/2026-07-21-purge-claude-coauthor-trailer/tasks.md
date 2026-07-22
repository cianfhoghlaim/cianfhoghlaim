# Tasks

## 1. Draft + validate openspec change
- [ ] Create `openspec/changes/2026-07-21-purge-claude-coauthor-trailer/{proposal.md,tasks.md}`
- [ ] Create `openspec/changes/2026-07-21-purge-claude-coauthor-trailer/specs/agent-runtime-and-attribution/spec.md` with ADDED Requirements using SHALL/MUST + ≥1 Scenario block each
- [ ] Run `openspec validate 2026-07-21-purge-claude-coauthor-trailer --strict` and resolve any errors

## 2. Pre-rewrite audit
- [ ] Verify a clean working tree (`git status` reports nothing)
- [ ] List branches that will be rewritten (`git branch -a`)
- [ ] Capture pre-rewrite SHAs of `main`, `HEAD`, and any checked-out branch (`git rev-parse HEAD^{} main`)
- [ ] Confirm `git-filter-repo` is available (`uv tool install git-filter-repo` if not)

## 3. Author the rewrite
- [ ] Write `.scratch/strip-claude-trailer.py` (Python callback passed to `--message-callback`; strips `Co-Authored-By: Claude … <noreply@anthropic.com>` line AND the preceding blank line; idempotent)
- [ ] Run `git filter-repo --force --message-callback …` against `--branches --tags` (NOT pushing yet)
- [ ] Verify zero commits still carry the trailer (`git log --all --grep='Co-Authored-By: Claude' --grep='noreply@anthropic.com' -i` returns empty)
- [ ] Verify commit authors/committers were preserved
- [ ] Note the new SHAs of `main` and `HEAD`

## 4. Force-push
- [ ] Push backup branch first: `git push origin 'refs/heads/*:refs/heads/backup/pre-claude-trailer-purge-*'`
- [ ] `git push --force-with-lease --all --tags origin`
- [ ] `git fetch --prune origin` and reconcile any local working branches
- [ ] Confirm GitHub UI on a sample commit no longer shows the trailer

## 5. Hook layer
- [ ] Create `.githooks/prepare-commit-msg` (executable; sed-strips any line matching `^[Cc]o-[Aa]uthored-[Bb]y:.*([Cc]laude|anthropic\.com)` from the message file)
- [ ] Create `.githooks/pre-push` (executable; iterates commits being pushed, refuses if any still has the trailer)
- [ ] Create `scripts/install-hooks.sh` (executable; runs `git config core.hooksPath .githooks` and chmods the hooks +x)
- [ ] Add `hooks:install` task in `mise.toml` (calls `scripts/install-hooks.sh`)
- [ ] Run `mise run hooks:install` on this worktree
- [ ] Smoke-test: `git commit --allow-empty -m "Co-Authored-By: Claude (builder mode) <noreply@anthropic.com>"` — the trailer must be gone from `git log -1`
- [ ] Smoke-test: try `git push --dry-run` after authoring a commit with the trailer — must refuse

## 6. Runtime swap
- [ ] `git rm scripts/claude-with-secrets.sh`
- [ ] Author `scripts/opencode-with-secrets.sh` (executable; `exec mise run locket:exec -- opencode "$@"`)
- [ ] Run `shellcheck scripts/opencode-with-secrets.sh` if available
- [ ] Run `mise run lint:skills` to ensure skill metadata stays valid

## 7. Wrap-up
- [ ] Commit everything (hooks + scripts + spec + deletion of claude-with-secrets.sh) on the feature branch
- [ ] Direct merge into `main` (no PR — local-only coordination per decision)
- [ ] `openspec archive 2026-07-21-purge-claude-coauthor-trailer --yes`
- [ ] Update AGENTS.md sections that referenced Claude Code (search for `claude-with-secrets` and `Claude Code`)

## 8. Post-deploy verification
- [ ] Open the GitHub commit page for one old-SHA-equivalent commit (compare tree-hash, since SHA changed) — confirm no `Co-Authored-By:` trailer mentioning Claude/Anthropic
- [ ] Confirm `git push` from any subdir rejects future trailer attempts
- [ ] Confirm `scripts/opencode-with-secrets.sh` launches OpenCode (does NOT require `claude` binary)
