# Spec: Agent Runtime and Attribution

## Purpose

Governs which agent runtimes are permitted in this repo and what attribution they
may apply to commits. The canonical runtime is OpenCode; Claude Code is **not** an
approved runtime for this repo because it appends a hardcoded, model-independent
`Co-Authored-By: Claude <noreply@anthropic.com>` trailer that produces false
attribution.

## ADDED Requirements

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
| `opencode` (via `scripts/opencode-with-secrets.sh` or direct) | **approved** | Does not inject commit trailers |
| `git` invoked directly by a human | **approved** | Author is the human |
| `claude` (Claude Code CLI) | **forbidden** | Hardcodes false `Co-Authored-By: Claude` trailer in every commit |

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
