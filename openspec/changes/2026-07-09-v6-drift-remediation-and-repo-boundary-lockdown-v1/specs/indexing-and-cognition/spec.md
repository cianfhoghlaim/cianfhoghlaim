## MODIFIED Requirements

### Requirement: CCC search excludes archived openspec

The CCC code search SHALL exclude `openspec/changes/archive/`
from all queries by default (the archived changes are
point-in-time artifacts per the `openspec/AGENTS.md` rule).

#### Scenario: A search query hits both active and archived changes

- **WHEN** a developer runs `bun run ccc:search "Brown Ajah"`
- **THEN** matches in `openspec/changes/2026-07-09-remove-brown-ajah-theming-v1/`
  (the active change) SHALL be returned
- **AND** matches in `openspec/changes/archive/2026-07-06-brown-ajah-v1/`
  (an archived ancestor) SHALL be excluded

#### Scenario: A search must explicitly include archive

- **WHEN** a developer runs
  `bun run ccc:search "Brown Ajah" --include-archive`
- **THEN** the archive SHALL be included in the result set