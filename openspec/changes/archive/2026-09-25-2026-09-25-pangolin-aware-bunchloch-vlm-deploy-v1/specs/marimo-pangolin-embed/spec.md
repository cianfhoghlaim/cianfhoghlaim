# marimo-pangolin-embed Specification

## Purpose
The authentication + embedding pattern for serving the 15 Stage-F marimo dashboards (and
the new VLM benchmark notebook) behind the Pangolin + Pocket ID OIDC tunnel, so they are
reachable from any device with Pangolin.app connected, but only after the operator has
authenticated via Pocket ID SSO.

## ADDED Requirements

### Requirement: All 15 Stage-F dashboards served via marimo server behind Pocket ID OIDC
The marimo server (`:2718`) SHALL be exposed as a Pangolin private resource
`marimo.cianfhoghlaim.ie`. Pocket ID OIDC (via the Pangolin + Tinyauth middleware stack) SHALL
gate access; only authenticated members of the `Member` role may reach the dashboard
iframe surface. The 15 Stage-F dashboards (5 tertiary ADK 2 deep-research + 5 K-12 teacher +
5 K-12 student) SHALL all be reachable from this entrypoint.

#### Scenario: Dashboard loads after Pocket ID SSO
- **GIVEN** the user has Pangolin.app connected and is signed into `auth.cianfhoghlaim.ie`
- **WHEN** the user opens `https://marimo.cianfhoghlaim.ie/notebooks/<stage>/<name>.py`
- **THEN** the iframe loads within 5 seconds
- **AND** all cells render
- **AND** the user can click the **Run Pillar-3 ...** button and observe real-time cell updates

#### Scenario: Unauthenticated access is denied
- **WHEN** an unauthenticated caller opens `https://marimo.cianfhoghlaim.ie/notebooks/...`
- **THEN** the user is redirected to the Pocket ID login flow
- **AND** the notebook is not visible until the login flow completes

### Requirement: VLM benchmark notebook at `/en/dashboards/vlm-benchmark`
The TanStack Start route `/en/dashboards/vlm-benchmark` SHALL be added (per
`web/apps/cianfhoghlaim-web/apps/web/src/routes/en/dashboards/$stage.tsx` pattern) and
SHALL render the new `notebooks/_shared/evaluation/vlm_registry_benchmark.py` notebook in a
sandboxed iframe.

#### Scenario: VLM benchmark renders the 12-model side-by-side table
- **WHEN** the user opens `http://localhost:3000/en/dashboards/vlm-benchmark`
- **THEN** the page renders a comparison table with 12 rows (one per unsloth model) and
  3 columns (one per standard prompt)
- **AND** each cell shows: latency_ms, prompt_tokens, completion_tokens, cost_usd,
  ragas_faithfulness
- **AND** the radar chart visualises the per-model trade-off

### Requirement: Iframe sandbox per marimo embedding best practices
The iframe element SHALL use the recommended sandbox attribute set per the Marimo embedding
docs (`https://docs.marimo.io/guides/publishing/embedding/`):

```html
<iframe
  src="https://marimo.cianfhoghlaim.ie/notebooks/<path>"
  sandbox="allow-scripts allow-same-origin allow-downloads allow-popups allow-forms"
  allow="microphone"
  allowfullscreen
  width="100%"
  height="600"
/>
```

#### Scenario: Sandbox blocks popups + clipboard in basic mode
- **WHEN** the iframe is loaded with only `allow-scripts` (basic mode)
- **THEN** the notebook runs in-memory state only (resets on reload)
- **AND** clipboard access uses browser prompts instead of the clipboard API

#### Scenario: Recommended mode enables downloads + forms
- **WHEN** the iframe is loaded with the recommended sandbox set
- **THEN** the user can download CSV exports from notebook outputs
- **AND** the user can submit interactive form cells (`mo.ui.form`)
- **AND** persistent state is available via `localStorage` (since the iframe + the
  upstream share the `marimo.cianfhoghlaim.ie` origin)

### Requirement: Marimo server proxied through Pangolin Traefik
The marimo container's `:2718` SHALL be reachable on `marimo.cianfhoghlaim.ie` via the
Pangolin Traefik reverse proxy. The marimo stack already runs on `bunchloch`; the
new requirement is the Pangolin Traefik route + the Pocket ID OIDC middleware.

#### Scenario: Traefik route serves the notebook
- **WHEN** the user opens `https://marimo.cianfhoghlaim.ie/`
- **THEN** the marimo landing page renders (the file picker)
- **AND** the 15 Stage-F dashboards are listed (under `notebooks/_shared/<stage>/walkthroughs/`)
- **AND** the VLM benchmark is listed (under `notebooks/_shared/evaluation/`)
