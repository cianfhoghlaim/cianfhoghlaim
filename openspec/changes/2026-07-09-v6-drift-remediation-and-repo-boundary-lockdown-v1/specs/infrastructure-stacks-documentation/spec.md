## ADDED Requirements

### Requirement: Repo boundary documented in root AGENTS.md

The root `AGENTS.md` SHALL contain a `## Repo Boundary` section
that explicitly lists which directories / files belong to
which of the 3 repos (cianfhoghlaim + bonneagar + leabharlann).

#### Scenario: A new agent reads root AGENTS.md

- **WHEN** an agent reads `AGENTS.md` to understand where to
  add a new component
- **THEN** the agent SHALL be able to identify the canonical
  repo for any of the 3 ownership domains from the
  `## Repo Boundary` section
- **AND** SHALL NOT need to read any other file to make the
  routing decision

#### Scenario: The repo boundary is queried

- **WHEN** an agent searches for `sruth/`, `stacks/`,
  `infrastructure/`, or `leabharlann/` in `AGENTS.md`
- **THEN** the result SHALL reference the correct repo for
  each path (post-v4 consolidation: `sruth/` is gone;
  `stacks/` lives in bonneagar; `leabharlann/` is a worktree)