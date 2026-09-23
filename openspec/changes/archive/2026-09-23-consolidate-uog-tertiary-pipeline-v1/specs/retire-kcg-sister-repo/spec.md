# retire-kcg-sister-repo Specification

## Purpose

Codify the retirement of the `kings_college_galway` sister-repo
(publicly at `github.com/cianfhoghlaim/ollscoil-na-gaillimhe`). The
case-study-sister mission is fully replaced by the new
`dlt_sources/british_isles/ireland/tertiary/uog/` package in
cianfhoghlaim, which ships the same 5 UoG public-surface DLT
sources (academic_calendar + governance_minutes + press_releases +
programme_catalog + research_outputs) + 7 new per-tier deep
extractions + the authenticated regexam + Canvas pipelines.

Per the user's reverted-split directive ("our previous intent to
split the monorepo up into more usable case studies is reverted to
prefer the monorepo structure"), the KCG sister-repo has no
remaining reason to exist.

## Requirements

## ADDED Requirements

### Requirement: GitHub API deletion of the KCG repo

The system SHALL delete `github.com/cianfhoghlaim/ollscoil-na-gaillimhe`
via the GitHub API (`gh repo delete cianfhoghlaim/ollscoil-na-gaillimhe --yes`)
after the cianfhoghlaim umbrella change is archived.

#### Scenario: GitHub API deletion succeeds
- **WHEN** the operator runs `gh repo delete cianfhoghlaim/ollscoil-na-gaillimhe --yes`
- **THEN** the command exits 0
- **AND** `gh repo view cianfhoghlaim/ollscoil-na-gaillimhe` returns 404

### Requirement: Local mirror deletion

The system SHALL delete the local mirror at `~/dev/kings_college_galway/`
after the GitHub repo deletion.

#### Scenario: Local mirror deletion succeeds
- **WHEN** the operator runs `rm -rf ~/dev/kings_college_galway`
- **THEN** `ls ~/dev/kings_college_galway` returns "No such file or directory"

### Requirement: Naming artifacts purged from cianfhoghlaim

The system SHALL ensure no references to `kings_college_galway`,
`ollscoil-na-gaillimhe`, `uog_pipeline_base`, or the KCG README/LICENSE
remain anywhere in the cianfhoghlaim codebase.

#### Scenario: grep returns 0 matches for all retired naming artifacts
- **WHEN** the operator runs `git grep kings_college_galway && git grep ollscoil-na-gaillimhe && git grep "uog_pipeline_base"`
- **THEN** all 3 commands return 0 matches

### Requirement: Sister-shared umbrella updated

The system SHALL update `openspec/specs/pipeline-sister-repo-handoff/spec.md`
to remove the KCG sister from the inventory (KCG is no longer a
sister-repo; its content lives in cianfhoghlaim).

#### Scenario: sister-shared spec reflects the retirement
- **WHEN** the operator reads `openspec/specs/pipeline-sister-repo-handoff/spec.md`
- **THEN** the 4-sister-repo inventory reads "cianchosaint + ciandlithe + ciancheiltis + tuatha" (KCG removed)
- **AND** the KCG-related cross-repo consumer references are removed
