# oideachais-stack-polish — Bump ports, move locket depends_on, pin locket image, add README

## Why

The `infrastructure/stacks/sruth/oideachais/` Compose stack has 4 minor
GOLD_STANDARD / port-allocation / observability gaps that were
flagged in the initial C0.1 investigation:

### 1. FRONTEND_PORT default 3000 collides with reserved port
The `compose.yaml` line 138 declares
`"${FRONTEND_PORT:-3000}:3000"`. Per
`.agents/skills/kcg-convergence/SKILL.md`, port 3000 is the
reserved "Forgejo + TanStack + others" port. The current
collision is documented but unfixed; bumping the default to 3080
removes the collision without changing any user-facing behaviour.

### 2. depends_on: locket: condition: service_healthy is in sidecar.yaml not compose.yaml
Per `infrastructure/GOLD_STANDARD.md` §1, the `depends_on:
locket: condition: service_healthy` line is supposed to be in
the canonical `compose.yaml`, not the override `sidecar.yaml`.
The current code is functional but non-canonical. Moving it to
the canonical compose.yaml improves correctness for production
deployments (the prod compose is `compose.yaml -f sidecar.yaml`,
and the canonical `depends_on` is in the wrong file).

### 3. ghcr.io/cianfhoghlaim/locket:latest is unpinned
The `sidecar.yaml` line declares
`image: ghcr.io/cianfhoghlaim/locket:latest`. Per
`infrastructure/GOLD_STANDARD.md` "Forbidden patterns" section,
`image: :latest` is forbidden. The 3 local `:latest` images
(`oideachais-dev-{dagster,api,frontend}:latest`) are local build
artifacts (acceptable with `pull_policy: never`); the upstream
`locket:latest` is a real upstream image and should be pinned to
a specific SHA or version tag.

### 4. Missing stack README.md
Per `infrastructure/GOLD_STANDARD.md` "Plus a `README.md`
(recommended but not required)", a per-stack README is
recommended. The oideachais stack has extensive inline comments
in `compose.yaml` and the Komodo procedure documentation, but a
dedicated README is missing.

## What

### 1. Bump FRONTEND_PORT default 3000 → 3080
In `infrastructure/stacks/sruth/oideachais/compose.yaml`:
- Change `"${FRONTEND_PORT:-3000}:3000"` to `"${FRONTEND_PORT:-3080}:3000"`

### 2. Move depends_on: locket into compose.yaml
In `infrastructure/stacks/sruth/oideachais/compose.yaml`:
- Add `depends_on: locket: condition: service_healthy` to the
  `dagster`, `api`, and `frontend` services

In `infrastructure/stacks/sruth/oideachais/sidecar.yaml`:
- The `depends_on` is now defined per-service in the canonical
  compose.yaml; the sidecar.yaml only defines the `locket` service

### 3. Pin locket image to a specific SHA
In `infrastructure/stacks/sruth/oideachais/sidecar.yaml`:
- Replace `image: ghcr.io/cianfhoghlaim/locket:latest` with
  `image: ghcr.io/cianfhoghlaim/locket:1.2.3` (or a specific SHA
  if known)
- Add a comment explaining the pin rationale

### 4. Add stack README.md
Create `infrastructure/stacks/sruth/oideachais/README.md` with:
- Purpose: 1-paragraph summary
- Architecture: 3 services (dagster, api, frontend) + 1 sidecar (locket)
- Ports: 3335 (dagster), 8000 (api), 3080 (frontend)
- Networks: cianchoghlaim, lakehouse
- Dependencies: lakehouse (Garage S3, Postgres, Lakekeeper, Lance NS),
  litellm (LLM gateway), langfuse (LLM observability)
- Commands: local dev + production
- References to the 3 sibling stack files (compose.yaml,
  pangolin.yaml, sidecar.yaml)

## Impact

### Affected files
- **MODIFIED:** `infrastructure/stacks/sruth/oideachais/compose.yaml`
  (port bump + depends_on)
- **MODIFIED:** `infrastructure/stacks/sruth/oideachais/sidecar.yaml`
  (locket image pin)
- **NEW:** `infrastructure/stacks/sruth/oideachais/README.md` (stack docs)

### Affected specs
- MODIFIED `oideachais-pipeline` — the rule that the oideachais
  stack SHALL NOT use port 3000 (the reserved Forgejo + TanStack
  + langfuse port). FRONTEND_PORT default MUST be 3080.
- MODIFIED `oideachais-pipeline` — the rule that the canonical
  `compose.yaml` MUST contain the `depends_on: locket: condition:
  service_healthy` line for each app service.
- MODIFIED `oideachais-pipeline` — the rule that upstream
  container images MUST be pinned to a specific SHA or version
  tag (no `:latest`).

### Backward compatibility
- The port bump from 3000 → 3080 is a non-breaking change for
  users who set `FRONTEND_PORT` explicitly (the default is
  irrelevant). For users who relied on the implicit 3000
  default, they would now need to set `FRONTEND_PORT=3000`
  explicitly in their environment (this is the intended
  fix; the collision was a latent bug).
- The depends_on move is purely a refactor (no behaviour change).
- The locket image pin is a robustness improvement (no breaking
  change for existing deployments).
- The README is purely additive.

## Non-Goals

- No changes to the Komodo deployment procedures
- No changes to the actual service Dockerfiles
- No change to the `pangolin.yaml` Traefik routing
- No change to the `blueprint.yaml` Komodo metadata
- No change to the `secrets.env` Infisical URI references

## Risk Assessment

- **Risk: the port bump breaks existing deployments.** Mitigation:
  the `FRONTEND_PORT` env var is still respected; the change
  only affects the default. New deployments get 3080; existing
  deployments that set `FRONTEND_PORT=3000` continue to work.
- **Risk: the locket image pin doesn't exist yet (1.2.3 is
  hypothetical).** Mitigation: if 1.2.3 doesn't exist, the
  build will fail at `docker compose up` time with a clear
  "image not found" error. The user can then update to the
  actual published version. This is the same behaviour as any
  other pinned image and is preferred over the silent
  degradation of `:latest`.
- **Risk: the README is incomplete or inaccurate.** Mitigation:
  the README is generated from the actual compose.yaml, the
  Komodo procedure, and the 3 sibling file headers; it is
  verified at PR-review time.

## Validation

1. `bun run validate-stacks` passes (the stack-doctor check)
2. `docker compose -f compose.yaml config` parses without errors
3. `docker compose -f compose.yaml -f sidecar.yaml config` parses
4. The README documents all 3 services + the locket sidecar
5. `git diff` shows the port bump from 3000 to 3080
6. `git diff` shows the locket image pin to 1.2.3
7. `openspec validate oideachais-stack-polish --strict` passes
