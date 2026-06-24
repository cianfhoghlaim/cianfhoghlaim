## MODIFIED Requirements

### Requirement: The oideachais stack SHALL use port 3080 (not 3000) for the frontend
The oideachais stack MUST use port 3080 as the default host port
for the frontend service. Port 3000 is reserved per
`.agents/skills/kcg-convergence/SKILL.md` and MUST NOT be used as
the default. Existing deployments that set `FRONTEND_PORT=3000`
explicitly are still supported.

#### Scenario: A new deployment runs `docker compose up`
- **WHEN** a user runs `docker compose -f compose.yaml -f sidecar.yaml up -d`
  on a fresh checkout
- **THEN** the frontend container SHALL listen on host port 3080
  (not 3000)
- **AND** the user SHALL be able to reach the frontend at
  `http://localhost:3080`

#### Scenario: An existing deployment sets FRONTEND_PORT=3000
- **WHEN** a user runs `docker compose ... -e FRONTEND_PORT=3000 up -d`
  (or sets it in `.env`)
- **THEN** the frontend container SHALL listen on host port 3000
  (the env var overrides the default)

### Requirement: The canonical compose.yaml SHALL declare depends_on: locket
The canonical `infrastructure/stacks/oideachais/compose.yaml` MUST
declare `depends_on: locket: condition: service_healthy` for each
app service (`dagster`, `api`, `frontend`). The override
`sidecar.yaml` MUST NOT re-declare the `depends_on` (which would
shadow the canonical declaration).

#### Scenario: A new deployment runs `docker compose up`
- **WHEN** a user runs `docker compose -f compose.yaml -f sidecar.yaml up -d`
- **THEN** the 3 app services SHALL wait for the `locket` sidecar
  to be healthy before starting
- **AND** the `depends_on: locket: condition: service_healthy`
  line MUST be in the canonical `compose.yaml`, NOT in
  `sidecar.yaml`

### Requirement: Upstream container images SHALL be pinned to a specific SHA or version tag
The oideachais stack MUST NOT use `:latest` for any upstream
container image. Local build artifacts (e.g.
`oideachais-dev-dagster:latest`) are exempt (they have
`pull_policy: never`). Upstream images (e.g.
`ghcr.io/cianfhoghlaim/locket`) MUST be pinned to a specific
version tag (e.g. `1.2.3`).

#### Scenario: A new stack file declares an upstream image
- **WHEN** a contributor adds or modifies a service in the
  oideachais stack that uses an upstream image
- **THEN** the image tag MUST be a specific version (e.g. `1.2.3`,
  `1.2.3-sha256-deadbeef`) and NOT `:latest`
