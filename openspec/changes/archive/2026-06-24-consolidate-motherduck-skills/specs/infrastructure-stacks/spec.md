## ADDED Requirements

### Requirement: Skill consolidation ratio

KCG-authored umbrella skill trees (e.g. MotherDuck, browser, code search) MUST be reorganised so that no more than 5 task-specific sub-skills exist per tree, with a single routing skill that dispatches to the right one.

#### Scenario: MotherDuck skill tree is consolidated

- **WHEN** an agent triggers a phrase that should load a MotherDuck skill
- **THEN** the loader matches one of: `motherduck` (router), `motherduck-architecture`, `motherduck-data-modeling`, `motherduck-analytics`, `motherduck-connections` (4 task-specific)
- **AND** the 18 prior `motherduck-*` sub-skills are removed

#### Scenario: Router points to the 4 consolidated skills

- **WHEN** `motherduck/SKILL.md` is read
- **THEN** it contains a router table that points to exactly `motherduck-architecture`, `motherduck-data-modeling`, `motherduck-analytics`, `motherduck-connections` (no orphan references to deleted skills)
