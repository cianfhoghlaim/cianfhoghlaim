# 2026-08-22-concurrent-agent-write-safety-v1

## Why

The 2026-08-22 PR #5 (`2026-08-22-lakehouse-observability-stacks-modernization-v1`) lost 8 file modifications mid-session due to a concurrent-agent write race. Root cause:

1. The orchestrator agent was committing a 1058-file mega-commit (1055 unrelated changes from concurrent subagents + 8 intended files) via `git add -A` after the initial add+commit was rejected.
2. The orchestrator used `git reset --soft HEAD~1` followed by `git reset HEAD` to "clean up" — this unstaged everything (including the intended files) but did NOT delete the files from the working tree (they were untracked).
3. The intended files persisted on the filesystem but were now untracked + un-staged.
4. A subsequent commit (PR #5 openspec-only) shipped WITHOUT the 8 file modifications.
5. The bug was detected hours later when re-reading the files revealed the modernization was still on disk.

This change codifies the safety protocol so the same disaster cannot recur. The protocol is now in `AGENTS.md` § 5 (Concurrent-Write Safety Protocol) and is enforced as 3 new ADDED Requirements on `repo-hygiene-agent-routing`.

## User preferences (locked-in from prior turns)

| Decision | Choice |
|:--|:--|
| Enforcement level | **Documentation + spec only** (no git hook) — keep adoption low-friction |
| Scope | **Every agent session** (orchestrator, 5 subagents, IDE sessions, hooks) |
| Filing location | `AGENTS.md` § 5 (the consolidated protocols section) + `repo-hygiene-agent-routing` spec |
| Reference incident | The 2026-08-22 PR #5 file-loss event (this change was authored in response) |

## Dependencies

`Blocked by: none`
`Affected repos: cianfhoghlaim` (single-repo change)

## What changes

### 1. AGENTS.md § 5 (NEW — 90 lines)
Add the "Concurrent-Write Safety Protocol" section to the consolidated root AGENTS.md after the existing 4 protocols. The section includes:

- The 4-step file edit protocol (status before → edit → status after → add+commit)
- 7 forbidden patterns (with explanations)
- 5 safe patterns (with explanations)
- The "CLAIM A FILE" pattern (for multi-agent coordination via `/tmp/agent-claims.log`)
- A reference to the openspec contract (this change)
- A reference to the 2026-08-22 PR #5 incident

### 2. `repo-hygiene-agent-routing` spec delta (3 ADDED Requirements)

See `specs/repo-hygiene-agent-routing/spec.md` for the delta.

### 3. No tooling change

This change does NOT add a git pre-commit hook, a CI gate, or any other enforcement mechanism. The protocol is documentation + spec only. The spec delta is the constraint; agents are expected to follow the protocol.

## Out of scope (deferred)

- **Pre-commit hook**: a hook that runs `git status` to detect unstaged changes during a commit is NOT in this change. Hooks are too easy to skip with `--no-verify`.
- **Worktree isolation**: forcing every agent into a separate git worktree is NOT in this change. The protocol includes `git worktree add` as a recommended pattern but does not require it.
- **Agent coordination via `/tmp/agent-claims.log`**: the CLAIM A FILE pattern is documented but not implemented as a runtime lock. It's a soft coordination mechanism.

## Cross-references

- Spec delta: `openspec/changes/2026-08-22-concurrent-agent-write-safety-v1/specs/repo-hygiene-agent-routing/spec.md`
- Tasks: `openspec/changes/2026-08-22-concurrent-agent-write-safety-v1/tasks.md`
- AGENTS.md § 5: `AGENTS.md` (root, in the "Critical Agent Protocols & Habits" section)
- Reference incident: `openspec/changes/archive/2026-08-22-2026-08-22-lakehouse-observability-stacks-modernization-v1/proposal.md` (PR #5 — the openspec that lost 8 file modifications)
