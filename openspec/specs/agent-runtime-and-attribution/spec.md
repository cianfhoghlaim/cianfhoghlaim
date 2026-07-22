# agent-runtime-and-attribution Specification

## Purpose

Governs which agent runtimes are permitted in this repo, what attribution
they may apply to commits (both trailer + author field), and how false
attributions are remapped for display. The canonical runtime is OpenCode;
Claude Code is **not** an approved runtime because it appends a hardcoded
`Co-Authored-By: Claude <noreply@anthropic.com>` trailer AND sets the
author field to `Claude <claude@anthropic.com>` on every commit —
both of which are false attribution when the user's actual model backend
(MiniMax-M3 via an Anthropic-compatible endpoint) is in use.

## Requirements
### Requirement: COMMIT ATTRIBUTION MUST ONLY NAME THE ACTUAL AUTHOR
The system MUST ensure that every commit recorded in git history attributes
the work only to the human or agent that **actually produced** the change.
A commit MUST NOT carry a `Co-Authored-By:` trailer that names an entity
(individual or organization) that did not author the change.

#### Scenario: Bare commit with no trailer
- WHEN a developer commits `fix(api): handle null token` with no trailer
- THEN the commit SHALL be accepted and recorded with only the author's identity
- AND the GitHub commit page SHALL display only the author, no co-author.

#### Scenario: Trailer naming a non-participant is rejected
- WHEN a developer attempts `git commit -m "fix: thing

Co-Authored-By: Claude (builder mode) <noreply@anthropic.com>"`
- THEN the `prepare-commit-msg` hook SHALL strip the `Co-Authored-By:` line
- AND the recorded commit message SHALL NOT contain `Claude` or `anthropic.com`

### Requirement: APPROVED RUNTIMES LIST
The system SHALL ship an explicit allow-list of agent runtimes permitted to
produce commits in this repo. The default allow-list for this repo is:

| Runtime | Status | Reason |
|:--|:--|:--|
| `opencode` (via `scripts/opencode-with-secrets.sh` or direct) | **approved** | Does not inject commit trailers AND does not set a Claude/Anthropic author |
| `git` invoked directly by a human | **approved** | Author is the human |
| `claude` (Claude Code CLI) | **forbidden** | Hardcodes both `Co-Authored-By: Claude` trailer AND author `Claude <claude@anthropic.com>` in every commit |

A change to the allow-list SHALL be made by an openspec change to this spec.

#### Scenario: Wrapper script for the approved runtime is provided
- GIVEN the repo's secrets layer is Locket + mise
- WHEN a developer wants to launch the approved runtime with secrets injected
- THEN `scripts/opencode-with-secrets.sh` SHALL exist and be executable
- AND it SHALL launch `opencode` via `mise run locket:exec --`
- AND it SHALL NOT depend on, mention, or launch `claude`

#### Scenario: Wrapper script for a forbidden runtime does not exist
- GIVEN the allow-list forbids `claude` (Claude Code CLI)
- WHEN the repo is checked out at any branch
- THEN `scripts/claude-with-secrets.sh` SHALL NOT exist
- AND no `scripts/*with-secrets*.sh` SHALL target the forbidden runtime

### Requirement: TRAILER-STRIPPING HOOKS PREVENT REGRESSION
The repo MUST ship a layered hook defence so a Claude Code trailer cannot
land in a future commit even if Claude Code is temporarily installed again.

#### Scenario: prepare-commit-msg strips Claude/Anthropic trailers
- GIVEN `.githooks/prepare-commit-msg` is installed via `core.hooksPath`
- WHEN a commit message file is created by `git commit`
- THEN any line matching `/^[Cc]o-[Aa]uthored-[Bb]y:.*(Claude|anthropic\.com)/`
  SHALL be removed before the editor launches
- AND the original message file SHALL NOT be rewritten with the trailer

#### Scenario: pre-push refuses a push that still has the trailer
- GIVEN `.githooks/pre-push` is installed
- WHEN `git push` is run
- THEN the hook SHALL inspect every commit message in the pushed range
- AND if any message contains `Co-Authored-By: … Claude …` or `…anthropic.com`
  the push SHALL be refused with non-zero exit status
- AND the refusal output SHALL name the offending SHAs

### Requirement: HISTORY HAS NO CLAUDE/ANTHROPIC CO-AUTHOR TRAILERS
The system MUST ensure that after this change is archived, the git history of
the default branch does NOT contain any commit whose message includes a
`Co-Authored-By:` trailer naming `Claude` or `anthropic.com`. The system MUST
fail this requirement if any such commit is detected by the post-deploy audit.

#### Scenario: Post-deploy audit
- WHEN `git log --all --grep='Co-Authored-By: .*[Cc]laude' --grep='noreply@anthropic.com' -i --pretty=oneline` runs after this change is archived
- THEN the output SHALL be empty

### Requirement: PRIMARY AUTHORS MUST BE THE ACTUAL AGENT OR HUMAN
The system MUST ensure that the **author** field of every commit (not just the
`Co-Authored-By:` trailer) reflects the actual agent runtime or human that
produced the change. A commit MUST NOT carry an author field that names an
entity (individual or organization) that did not author the change.

#### Scenario: Bare commit with no trailer AND no Claude author
- WHEN a developer commits `fix(api): handle null token`
- THEN the recorded author SHALL be the developer's identity
- AND the commit message SHALL NOT contain a `Co-Authored-By:` trailer
- AND GitHub's Contributors graph SHALL display the commit under the developer's identity

### Requirement: MAILMAP REMAPS CLAUDE/ANTHROPIC AUTHORS
The repo MUST ship a `.mailmap` at the repo root that rewrites any commit
author whose email is `claude@anthropic.com` (the Claude Code CLI's
hardcoded identity) to display as `cianfhoghlaim <cianmacliathain@gmail.com>`
(the user's primary human identity). The purpose is to correct the
displayed author on GitHub's Contributors graph and blame views
without rewriting commit bytes (zero SHA churn, zero force-push).

#### Scenario: Mailmap entry exists and matches the canonical false identity
- GIVEN `.mailmap` exists at the repo root and is tracked in HEAD
- WHEN `grep -E '^cianfhoghlaim <[^>]+> \.?[Cc]laude@anthropic\.com' .mailmap` runs
- THEN the output SHALL contain at least one matching line

### Requirement: HISTORY HAS NO CLAUDE/ANTHROPIC PRIMARY AUTHORS IN DISPLAYED GRAPHS
The system MUST ensure that, after the change implementing this spec is
archived, the git history SHALL NOT contain any commit whose
**mailmap-displayed** author (not just raw author) is
`Claude <claude@anthropic.com>`. This is the property GitHub's
Contributors graph renders; the raw author field is permitted to retain
the historical identifier for forensic purposes.

#### Scenario: Post-deploy audit (mailmap-aware)
- WHEN `git shortlog -sn --all | grep -E '^\s*[0-9]+\s+Claude <claude@anthropic\.com>'` runs after this change is archived
- THEN the output SHALL be empty

#### Scenario: Contributing-graph reconciliation is implied
- WHEN the GitHub Contributors graph re-renders after this change is on `main`
- THEN the 3 commits previously attributed to `Claude` SHALL appear under `cianfhoghlaim`
- AND the total commit count under `cianfhoghlaim` SHALL be 1701 + 3 = 1704
- AND the `Claude` contributor entry SHALL be removed from the graph

