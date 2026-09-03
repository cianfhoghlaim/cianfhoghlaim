## ADDED Requirements

### Requirement: Priority quick reference section in every AGENTS.md

Every AGENTS.md file under the Cianfhoghlaim monorepo (`/AGENTS.md`, the 4 quadrant `AGENTS.md` files, `/infrastructure/AGENTS.md`, `/openspec/AGENTS.md`) MUST start with a "Priority quick reference" section (immediately after the title heading) that prominently surfaces the canonical skills, the ccc code-search command, the openspec commands, and the priority tools for that file's audience. The section MUST be at most 50 lines and MUST be a structured table (not prose).

#### Scenario: Root AGENTS.md leads with priority quick reference

- **WHEN** an agent reads `/AGENTS.md` from the repo root
- **THEN** the first section after the title is "Priority quick reference"
- **AND** it contains 4 tables: Priority skills (5 entries), ccc + openspec commands, Priority mise tasks (4 entries), Priority compose stacks (4 entries)

#### Scenario: Quadrant AGENTS.md leads with priority quick reference

- **WHEN** an agent reads `/sruth/oideachais/AGENTS.md` (or any of the 4 quadrant `AGENTS.md` files)
- **THEN** the first section after the title is "Priority quick reference"
- **AND** it lists the 5-8 skills most relevant to that quadrant + the ccc command + the 4 openspec commands

#### Scenario: infrastructure/AGENTS.md leads with priority quick reference

- **WHEN** an agent reads `/infrastructure/AGENTS.md`
- **THEN** the first section after the title is "Priority quick reference"
- **AND** it contains the stack-doctor command + the stack-ops skill + the 4 priority compose stacks (oideachais, litellm, langfuse, lakehouse)

#### Scenario: openspec/AGENTS.md leads with priority quick reference

- **WHEN** an agent reads `/openspec/AGENTS.md`
- **THEN** the first section after the title is "Priority quick reference"
- **AND** it contains the 4 priority specs (oideachais-pipeline, infrastructure-stacks, agent-memory-systems, dagger-pipelines) + the ccc command + the lint:skills task
