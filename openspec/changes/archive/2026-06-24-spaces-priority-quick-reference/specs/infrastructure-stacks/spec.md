## ADDED Requirements

### Requirement: Priority quick reference section in every Spaces AGENTS.md

Every AGENTS.md file under the `spaces/` tree (`spaces/AGENTS.md`, `spaces/_common/AGENTS.md`, `spaces/{an_scrudu,meaisin_cliste,cianfhoghlaim,anam_tuatha,data-engineering}/AGENTS.md`) MUST start with a "Priority quick reference" section that prominently surfaces the canonical skills, the ccc code-search command, the openspec commands, and the openspec specs most relevant to that Space. The section MUST be at most 60 lines and MUST be a structured table (not prose).

#### Scenario: Spaces AGENTS.md leads with priority quick reference

- **WHEN** an agent reads any `spaces/*/AGENTS.md` file
- **THEN** the first section after the title is "Priority quick reference"
- **AND** it lists the 3-5 skills most relevant to that Space + the ccc command + the 4 openspec commands

#### Scenario: Parent spaces AGENTS.md links to all 4 active Spaces

- **WHEN** an agent reads `spaces/AGENTS.md`
- **THEN** it lists the 4 active Spaces + the 1 archived Space + the 5 priority skills + the 4 priority openspec specs
- **AND** it links to each per-Space AGENTS.md for the developer-quick-reference routing table
