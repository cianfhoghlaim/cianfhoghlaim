# Delta: oideachais-leabharlann

## ADDED Requirements

### Requirement: Leabharlann worktree for personal archive history

The `leabharlann/` directory history SHALL live in the sibling `leabharlann` worktree (at `./leabharlann/`) per the worktree approach adopted 2026-06-29. The cianfhoghlaim monorepo SHALL NOT re-import the leabharlann history as a subtree because the 3.4 GB PDF corpus made every `git push` upload 3 GB of binary data. The cianfhoghlaim monorepo SHALL retain a thin `leabharlann/` reference (a README pointer) for navigation; the canonical leabharlann corpus lives in https://github.com/cianfhoghlaim/leabharlann.

#### Scenario: a developer looks for the canonical leabharlann corpus

- **GIVEN** the developer wants to find the canonical 225-document leabharlann corpus
- **WHEN** the developer runs `cd ./leabharlann && git log --oneline`
- **THEN** the developer sees the canonical history
- **AND** the monorepo's `git log -- leabharlann/` shows only the 2026-06-29 reset marker
