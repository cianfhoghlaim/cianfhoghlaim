## ADDED Requirements

### Requirement: Lance Namespace 0.9 Contract Conformance

The `bonneagar/stacks/lakehouse/lance-sidecar/` custom Python sidecar SHALL
implement the lance-namespace 0.9 REST contract, including the
context-header rename from `x-lance-ctx-*` to `header.<name>` (introduced in
PR #358, released with lance-namespace 0.9.0 on 2026-07-01).

#### Scenario: Lance sidecar uses the v0.9 context-header prefix

- **WHEN** `bonneagar/stacks/lakehouse/lance-sidecar/main.py` is read
- **THEN** every outgoing REST request SHALL set context headers with
  the `header.<name>` prefix (NOT `x-lance-ctx-<name>`)
- **AND** `requirements.txt` SHALL pin
  `pylance>=8.0.0` (was `>=0.26.0`; the 0.x → 8.0 jump shipped 2026-07-01)
  and `lance-namespace-urllib3-client>=0.0.30` (was `>=0.0.21`; the 0.9
  release added 9 months of contract changes)

#### Scenario: Lakehouse lance-sidecar passes the v0.9 health probe

- **WHEN** `curl -sf http://localhost:8182/v1/info` returns HTTP 200
- **THEN** the response body SHALL contain `{"version": "0.9.x", ...}`
  per the upstream contract
- **AND** zero requests in the access log SHALL carry
  `x-lance-ctx-*` headers (those would indicate a stale client)