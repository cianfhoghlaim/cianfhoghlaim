# Spec Delta: repo-hygiene-agent-routing

## ADDED Requirements

### Requirement: Every file edit MUST follow the 4-step file edit protocol

Every agent (orchestrator, subagent, IDE session, hook) MUST follow the 4-step protocol before making any file edit:

1. **Before edit**: Run `git status -- <path>` + `git diff -- <path>` + `sha256sum <path>` to record the current state. For tracked files, `git diff` should be empty.
2. **Make edit**: Use the Edit tool, Write tool, or shell sed/awk. Make ONE logical edit per call.
3. **After edit**: Run `git diff -- <path>` + `sha256sum <path>` again. The diff SHOULD show only the intended change. The hash SHOULD differ from step 1.
4. **Stage + commit immediately**: Run `git add <path>` (NOT `git add -A`), verify `git status -- <path>` shows the staged state, then `git commit -m "..."` + `git push origin <branch>` in the SAME shell context (don't batch).

If step 3 reveals unexpected changes (different line count, missing hunks, extra files), the agent MUST abort the edit and inspect `git status` + `git reflog` for concurrent-agent artifacts before retrying.

This protocol prevents the 2026-08-22 PR #5 file-loss incident from recurring.

Per the consolidated agent protocols documented in `AGENTS.md` § 5 (Concurrent-Write Safety Protocol).

#### Scenario: Single agent edits one file

- **GIVEN** a file at `path/to/file.txt` is in a clean state (no uncommitted changes)
- **WHEN** the agent runs the 4-step protocol
- **THEN** step 3 confirms the diff shows only the intended change
- **AND** the commit succeeds without touching other files
- **AND** `git push origin <branch>` succeeds

#### Scenario: Concurrent agent modifies the file mid-edit

- **GIVEN** the agent starts editing `path/to/file.txt`
- **AND** a concurrent agent writes to `path/to/file.txt` between step 1 and step 3
- **WHEN** the agent runs step 3 (verify diff)
- **THEN** the diff shows changes the agent did not make
- **AND** the agent ABORTS the edit
- **AND** inspects `git status` + `git reflog --date=iso | head -20`
- **AND** either re-applies their edit (if the concurrent change is benign) or escalates to the orchestrator

### Requirement: Git multi-file staging MUST use explicit paths, never `git add -A` or `git add .`

Agents MUST NOT use `git add -A` or `git add .` (or any other wildcard) for staging. Every `git add` MUST be an explicit path:

```bash
git add <path/to/file-1>
git add <path/to/file-2>
# NOT: git add -A    # ← FORBIDDEN
# NOT: git add .     # ← FORBIDDEN
# NOT: git add -u    # ← FORBIDDEN
```

This rule prevents concurrent agents' in-progress edits from being swept into a single commit. The 2026-08-22 PR #5 incident was triggered by `git add -A` which added 1058 files (1055 unrelated + 8 intended) before the agent realized the mistake.

#### Scenario: Agent needs to stage 3 intended files

- **GIVEN** the agent has edited 3 files: `a.txt`, `b.txt`, `c.txt`
- **AND** concurrent agents have edited `d.txt` (untracked) and modified `e.txt` (staged)
- **WHEN** the agent runs `git add a.txt b.txt c.txt`
- **THEN** ONLY the 3 intended files are staged
- **AND** `d.txt` and `e.txt` remain untouched
- **AND** the commit is safe

#### Scenario: Agent uses `git add -A` (forbidden pattern)

- **GIVEN** the agent should have staged only 3 files
- **WHEN** the agent runs `git add -A`
- **THEN** the staging area picks up CONCURRENT agents' in-progress edits
- **AND** the commit either (a) includes unintended changes (silent corruption) or (b) fails the safety check (visible disaster)

### Requirement: Multi-agent file claims MUST be coordinated via the CLAIM A FILE pattern

When multiple agents operate on the same git working tree concurrently, agents MUST coordinate via the CLAIM A FILE pattern (per `AGENTS.md` § 5):

```bash
# Agent A claims the dagster files
echo "$(date -Iseconds) agent A claims dagster/*" > /tmp/agent-claims.log

# Agent B waits or picks a different area
# Agent A finishes, commits, then releases the claim
echo "$(date -Iseconds) agent A releases dagster/*" >> /tmp/agent-claims.log
```

The `/tmp/agent-claims.log` file is a soft coordination mechanism (no runtime lock). It is informational only — agents SHOULD honor active claims but the protocol does not enforce a hard lock.

For zero-conflict scenarios, agents SHOULD use `git worktree add <path> <branch>` to isolate their work. Each worktree has its own working directory, so concurrent edits to the same file are impossible.

#### Scenario: Two agents want to edit the same stack

- **GIVEN** Agent A wants to edit `bonneagar/stacks/dagster/`
- **AND** Agent B wants to edit `bonneagar/stacks/dagster/dagster.yaml` (a sub-file)
- **WHEN** Agent A claims `dagster/*` via `/tmp/agent-claims.log`
- **THEN** Agent B reads the claim and waits
- **AND** Agent B picks a different area (e.g. `dagster/sidecar.yaml`)
- **AND** Agent A finishes, commits, releases the claim
- **AND** Agent B can now safely edit `dagster.yaml`

#### Scenario: Agents need hard isolation

- **GIVEN** Agents A and B MUST both edit files in the same directory concurrently
- **WHEN** Agent A uses `git worktree add ../a-worktree token-plan-lc-pipeline-2026-08`
- **AND** Agent B uses `git worktree add ../b-worktree token-plan-lc-pipeline-2026-08`
- **THEN** each agent has its own working directory
- **AND** edits to the same file are serialized at merge time
- **AND** neither agent's work is lost to the other's in-progress edits
