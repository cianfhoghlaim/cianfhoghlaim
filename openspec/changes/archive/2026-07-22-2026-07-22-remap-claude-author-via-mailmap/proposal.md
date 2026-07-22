# 2026-07-22 · Remap `Claude <claude@anthropic.com>` author via `.mailmap`

## Why

The 2026-07-21-purge-claude-coauthor-trailer change stripped the
`Co-Authored-By:` trailer from commit messages but left the **author
field** of every commit untouched. GitHub's **Contributors** graph
(as well as blame, shortlog, and PR commit lists) is rendered from the
author field, not from trailers — so 3 commits on `main` whose primary
author was `Claude <claude@anthropic.com>` (from the
`feat(lc-2026): end-to-end Leaving Cert pipeline working` series that
landed on 2026-06-09 via the now-retired `scripts/claude-with-secrets.sh`
wrapper) were still attributed to Claude on github.com/cianfhoghlaim.

This change adds a `.mailmap` at the repo root that remaps
`Claude <claude@anthropic.com>` to `cianfhoghlaim <cianmacliathain@gmail.com>`.
GitHub honours `.mailmap` for display purposes without rewriting commit
SHAs, so:

- The 3 commits remain bit-identical (no SHA churn, no force-push needed)
- Their raw authors in `git cat-file` are unchanged
- Their DISPLAYED authors on the GitHub Contributors graph, in blame, in
  shortlog, and in PR commit lists are now correctly attributed to
  `cianfhoghlaim`

## What changes

### `.mailmap` at repo root

A single mapping line:

```
cianfhoghlaim <cianmacliathain@gmail.com> <claude@anthropic.com>
```

…remaps every commit author with the email `claude@anthropic.com` to the
display name `cianfhoghlaim` and the canonical email
`cianmacliathain@gmail.com`. The user's primary human identity is the
right target because:

1. The user was the one operating the agent runtime (the work was done
   on the user's behalf)
2. `claude@anthropic.com` is a non-deliverable / fictional email of the
   Claude Code CLI — the user has no account at that address
3. The 3 commits appear in a series the user authored (Dagster / LC
   pipeline work) under their broader BIEP dashboard effort

### Spec delta

The `agent-runtime-and-attribution` spec gets **two new requirements**:

- A `MAILMAP REMAPS CLAUDE/ANTHROPIC AUTHORS` requirement that codifies
  the `.mailmap` presence and contents
- A `HISTORY HAS NO CLAUDE/ANTHROPIC PRIMARY AUTHORS IN DISPLAYED
  GRAPHS` requirement that codifies the post-deploy audit
  (`git shortlog -sn`)

## Dependencies

None — extends the archived 2026-07-21 change.

## Cross-repo sync

None — single-repo change.

## Risk + rollback

- **Risk**: Zero. `.mailmap` only affects display, never the bytes of
  any commit. To rollback, `git rm .mailmap` and force-push the
  removal commit.
- **Rollback**: Drop the file, push the removal. Reverts on the next
  GitHub sync (~minutes).

## Out of scope

- Other repos (`bonneagar`, `leabharlann`) — separate audit; not
  touched here.
- The 33 `feat/*` branches that still carry pre-rewrite SHAs on origin
  — those will pick up the same `.mailmap` automatically as soon as
  GitHub picks up the `main` HEAD.
