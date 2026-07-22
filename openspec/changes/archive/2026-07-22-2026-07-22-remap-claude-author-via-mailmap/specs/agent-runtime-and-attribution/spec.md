# Spec: Agent Runtime and Attribution

## Purpose

Governs which agent runtimes are permitted in this repo and what attribution they
may apply to commits. The canonical runtime is OpenCode; Claude Code is **not** an
approved runtime for this repo because it appends a hardcoded, model-independent
`Co-Authored-By: Claude <noreply@anthropic.com>` trailer that produces false
attribution.

## ADDED Requirements

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

## MODIFIED Requirements

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
