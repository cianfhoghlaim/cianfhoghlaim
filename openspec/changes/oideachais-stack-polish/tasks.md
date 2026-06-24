# Tasks: oideachais-stack-polish

## Phase 1: Bump FRONTEND_PORT default 3000 → 3080

- [ ] In `infrastructure/stacks/oideachais/compose.yaml`:
  - Change `"${FRONTEND_PORT:-3000}:3000"` to `"${FRONTEND_PORT:-3080}:3000"`
  - Update the comment above the frontend service to document the new default

## Phase 2: Move depends_on: locket into compose.yaml

- [ ] In `infrastructure/stacks/oideachais/compose.yaml`:
  - Add `depends_on: locket: condition: service_healthy` to the `dagster` service
  - Add `depends_on: locket: condition: service_healthy` to the `api` service
  - Add `depends_on: locket: condition: service_healthy` to the `frontend` service
- [ ] In `infrastructure/stacks/oideachais/sidecar.yaml`:
  - Remove the `depends_on` references from the `dagster` / `api` / `frontend` service definitions (they're now in compose.yaml)
  - Keep the `locket` service definition in sidecar.yaml

## Phase 3: Pin locket image to a specific SHA

- [ ] In `infrastructure/stacks/oideachais/sidecar.yaml`:
  - Replace `image: ghcr.io/cianfhoghlaim/locket:latest` with `image: ghcr.io/cianfhoghlaim/locket:1.2.3`
  - Add a comment explaining the pin rationale

## Phase 4: Add stack README.md

- [ ] Create `infrastructure/stacks/oideachais/README.md` with:
  - Purpose
  - Architecture (3 services + 1 sidecar)
  - Ports
  - Networks
  - Dependencies
  - Commands (local dev + production)
  - References to sibling files

## Phase 5: Validation

- [ ] `bun run validate-stacks` passes
- [ ] `docker compose -f compose.yaml config` parses
- [ ] `docker compose -f compose.yaml -f sidecar.yaml config` parses
- [ ] The README documents all 3 services + the locket sidecar
- [ ] `openspec validate oideachais-stack-polish --strict` passes

## Phase 6: Land the plane

- [ ] Stage the changes
- [ ] Commit: `git commit -m "oideachais-stack-polish: bump frontend port + pin locket + add README"`
- [ ] `git pull --rebase`
- [ ] `git push origin q3-2026-oideachais-consolidation`
