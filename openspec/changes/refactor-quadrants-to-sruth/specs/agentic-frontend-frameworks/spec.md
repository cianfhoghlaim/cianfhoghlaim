## MODIFIED Requirements

### Requirement: File-based routing

The system SHALL use TanStack Start's file-based routing for the
oideachais web app and the croilar apps.

#### Scenario: Routes are auto-generated under sruth/

- **GIVEN** a file `sruth/oideachais/web/apps/web/src/routes/curriculum.tsx`
  (was `sruth/oideachais/web/apps/web/src/routes/curriculum.tsx` pre-refactor)
- **WHEN** the app is built
- **THEN** the route `/curriculum` is auto-generated and accessible
- **AND** the path uses the `sruth/oideachais/` prefix (not the legacy
  `sruth/oideachais/` prefix at the repo root)

### Requirement: Subagent roster matches opencode.json

The system SHALL document the 5 sruth-specialist subagents
(`oideachais`, `infrastructure`, `meaisinfhoghlaim`, `croilar`, `tuatha`)
in every place that lists the subagent roster, including the root
README's "Agent capabilities" table.

#### Scenario: Root README references 5 sruth specialists

- **GIVEN** the root `README.md`
- **WHEN** reading lines 55, 69, 137–138, and 287–303 (the agent roster
  tables)
- **THEN** the tables list the 5 real subagent names from `opencode.json`:
  `oideachais`, `infrastructure`, `meaisinfhoghlaim`, `croilar`, `tuatha`
- **AND** no reference exists to the 5 generic agent names
  (`explorer`, `data-engineer`, `ai-engineer`, `frontend-dev`,
  `devops-architect`) that previously appeared in the README but did
  not exist in `opencode.json`

#### Scenario: 7 agents total in opencode.json

- **GIVEN** `opencode.json`
- **WHEN** counting the subagents
- **THEN** the file contains exactly 7 agents: `build`, `plan`,
  `oideachais`, `infrastructure`, `meaisinfhoghlaim`, `croilar`, `tuatha`
- **AND** each sruth-specialist subagent has a `tools.allow` list that
  scopes it to its own sruth's filesystem paths (e.g.
  `oideachais` subagent is allowed `sruth/oideachais/**`)

### Requirement: Server functions

The system SHALL use TanStack Start server functions for all data fetching
and agent calls.

#### Scenario: Type-safe server function under sruth/

- **GIVEN** a server function defined at
  `sruth/oideachais/web/apps/web/src/server/curriculum.ts`
- **WHEN** called from the client with `subject="ga101"`
- **THEN** the function executes on the server with type safety
- **AND** the result is typed end-to-end
- **AND** the file lives under `sruth/oideachais/` (not under the
  legacy root `sruth/oideachais/`)

### Requirement: Croilar surfaces under sruth/croilar/

The system SHALL host the 2 Croilar front-end surfaces under
`sruth/croilar/apps/`.

#### Scenario: Croilar web and portal under sruth/

- **GIVEN** the Croilar public persona site and the Croilar self-hosted
  dashboard
- **WHEN** locating their filesystem paths
- **THEN** they live at `sruth/croilar/apps/web/` and
  `sruth/croilar/apps/portal/` respectively
- **AND** no top-level `sruth/croilar/apps/` directory exists at the repo root

### Requirement: Tuatha MMO front-end under sruth/tuatha/

The system SHALL host the Tuatha educational MMO front-end under
`sruth/tuatha/ui/`.

#### Scenario: Tuatha UI under sruth/

- **GIVEN** the Tuatha MMO Babylon.js client
- **WHEN** locating its filesystem path
- **THEN** it lives at `sruth/tuatha/ui/`
- **AND** no top-level `sruth/tuatha/ui/` directory exists at the repo root