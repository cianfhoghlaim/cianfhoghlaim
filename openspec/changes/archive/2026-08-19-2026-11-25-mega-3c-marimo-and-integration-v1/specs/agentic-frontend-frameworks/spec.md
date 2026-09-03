## ADDED Requirements

### Requirement: marimo_to_fastapi integration helper

The system SHALL provide `notebooks/_shared/marimo_to_fastapi.py`
that mounts the 6 BIEP v3 stage dashboards + the canonical
`00_marimo_patterns_tour.py` as FastAPI endpoints.

The helper exposes each notebook's public functions via
`@app.get("/<stage>/<function>")` (per the
`frameworks/fastapi/` pattern).

#### Scenario: The 6 BIEP notebooks are exposed as FastAPI endpoints

- **WHEN** the operator runs `curl http://localhost:8000/ireland_lc/curriculum_educator`
- **THEN** the endpoint returns the canonical `curriculum_educator`
  output from the LC stage dashboard

### Requirement: FastAPI Auth for the 6 BIEP notebooks

The system SHALL lock down the 6 BIEP v3 stage dashboards with the
canonical `frameworks/fastapi-auth/` pattern.

The auth includes:
- Token-based authentication
- Rate limiting
- CORS configuration

#### Scenario: Unauthenticated requests are rejected

- **WHEN** the operator sends `curl http://localhost:8000/ireland_lc/curriculum_educator` (without auth)
- **THEN** the server returns 401 Unauthorized