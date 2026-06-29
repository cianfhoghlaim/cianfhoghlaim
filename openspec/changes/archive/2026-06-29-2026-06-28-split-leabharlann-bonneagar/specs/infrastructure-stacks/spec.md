# Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: Bonneagar worktree for infrastructure history

The `infrastructure/` directory history SHALL live in the sibling `bonneagar` worktree (at `./bonneagar/`) per the worktree approach adopted 2026-06-29. The cianfhoghlaim monorepo SHALL NOT re-import the bonneagar history as a subtree because the 6.9 MB subtree size made every `git push` upload the full content. The cianfhoghlaim monorepo SHALL retain a thin `infrastructure/` reference (a README pointer) for navigation; the canonical `infrastructure/` lives in https://github.com/cianfhoghlaim/bonneagar.

#### Scenario: a developer looks for the canonical infrastructure history

- **GIVEN** the developer wants to find the canonical 70+ Docker Compose stack history
- **WHEN** the developer runs `cd ./bonneagar && git log --oneline`
- **THEN** the developer sees the canonical history
- **AND** the monorepo's `git log -- infrastructure/` shows only the 2026-06-29 reset marker
