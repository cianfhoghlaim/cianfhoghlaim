# 2026-07-21 · Purge `Co-Authored-By: Claude (builder mode)` trailer and lock down commit attribution

## Why

Git history on `origin` (github.com/cianfhoghlaim/cianfhoghlaim) carries a false co-author trailer on **26+ commits** between 2026-06-06 and 2026-07-20:

```
Co-Authored-By: Claude (builder mode) <noreply@anthropic.com>
```

The trailer appears on **user-authored** commits (`cianfhoghlaim <cianmacliathain@gmail.com>`) **and** on agent commits (`Cianfhoghlaim Builder`, `frontend-apps subagent (T6)`). It is rendered on every commit page on GitHub and misleads anyone reading the history.

**Root cause** — not the model the user is invoking, but the **runtime**:

1. `scripts/claude-with-secrets.sh` launches the `claude` binary (Claude Code, the Anthropic CLI) with `op run --env-file=.env.local -- claude "$@"`.
2. Claude Code appends `Co-Authored-By: Claude (builder mode) <noreply@anthropic.com>` **client-side, in the binary**, on every commit it makes — regardless of which model is served at the configured API endpoint. The `(builder mode)` suffix is the giveaway: it is a Claude Code session-mode tag.
3. The user's actual model is `minimax/MiniMax-M3` served via an Anthropic-compatible endpoint; that endpoint only sees API traffic, not commit attribution.
4. The user's current runtime is **OpenCode 1.17.9** (`~/.local/share/mise/installs/opencode/1.17.9/opencode`). OpenCode does **not** add any co-author trailer (verified by `strings` over the binary).

Therefore the trailer is a false attribution and must be removed from history, and the runtime that produced it (Claude Code) must be retired from this repo so it can never recur.

## What changes

### History rewrite
- Run `git filter-repo --message-callback <strips trailer>` across **all** local refs.
- Force-push with `--force-with-lease --all --tags` to `origin`.
- All commit SHAs change; collaborators (incl. CI) must `git fetch --prune` and reset/rebase.

### Hook layer (prevents recurrence)
- Add `.githooks/prepare-commit-msg` — strips any trailer line that mentions `Claude` or `anthropic.com` from the commit message before the editor even opens.
- Add `.githooks/pre-push` — re-reads the messages of commits about to be pushed; refuses the push with a non-zero exit if a Claude/Anthropic trailer is still present.
- Set `git config core.hooksPath .githooks` (committed in `.git/config` via the bootstrap script `scripts/install-hooks.sh`).
- Add `mise run hooks:install` task.

### Runtime swap
- **Delete** `scripts/claude-with-secrets.sh` — the only entry point that launches Claude Code.
- **Add** `scripts/opencode-with-secrets.sh` — replaces it with `exec mise run locket:exec -- opencode "$@"`, so future sessions keep getting Infisical/Locket secret injection but on OpenCode, never Claude Code.

### Spec
- New spec `openspec/specs/agent-runtime-and-attribution/spec.md` (broad scope: covers agent identity, runtime choice, attribution truthfulness).
- Capture rationale + REQUIREMENT(S) + Scenario(s) so future commits cannot drift back to false attribution.

## Dependencies

None — this is a leaf change. It does not block or get blocked.

## Cross-repo sync

None. The rewrite is local to the `cianfhoghlaim` repo. `archive-bonneagar` and `leabharlann` remotes are untouched. The `git filter-repo` invocation restricts `--remotes` to `origin` only (not `archive-bonneagar` or `leabharlann`).

## Risk + rollback

- **Risk**: Force-push invalidates every SHA. Any open PR's base branch needs to be re-pointed at the rewritten `main`; CI caches keyed on old SHAs must be invalidated.
- **Rollback**: Before force-push, every local branch is mirrored to a backup remote refspace `backup/pre-claude-trailer-purge-*` so an emergency rollback is just `git push origin backup/pre-claude-trailer-purge-main:main --force-with-lease`.
- **Coordination**: Done in-session; the GitHub commit page on a sample commit becomes the public verification surface.

## Out of scope

- Other repos (`bonneagar`, `leabharlann`) — separate audit; not touched here.
- `.claude/` project-local dir (12 rules + 33 skills) — kept as-is per user decision; even if Claude Code is ever reinstalled, the deleted wrapper script + the prepare-commit-msg hook close the practical attack surface.
