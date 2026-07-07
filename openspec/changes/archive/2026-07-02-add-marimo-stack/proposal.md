# Change: 2026-07-02-add-marimo-stack

## Why

The `oideachais-marimo-dashboards` spec requires 11 marimo
notebooks (5 educational stages + Ireland curriculum analysis +
6 leabharlann subdir analyses + cross-domain) accessible via a
self-hosted marimo server. Until now, the marimo notebooks have
only been runnable via the local CLI
(`uv run marimo edit <name>.py`).

The `marimo` stack at `bonneagar/stacks/marimo/` exists but has
**4 latent bugs** that prevent it from starting:

1. **Wrong image registry path.** Line 4 reads
   `image: marimo/marimo:latest` — that image does **NOT** exist
   on Docker Hub. The upstream publishes to
   `ghcr.io/marimo-team/marimo` (verified live 2026-07-02; 67
   semver tags available, latest = `0.11.19`).

2. **Unpinned image tag.** Per `infrastructure-stacks` §"Image
   Pinning Policy", every `image:` line SHALL declare a
   specific semver tag (no `:latest`).

3. **Stale v3 volume path.** Line 10 reads
   `- ../../oideachais/notebooks:/notebooks:ro` — the
   `oideachais/` directory no longer exists after the
   2026-06-28 v4 consolidation; the canonical notebooks
   directory is now `../../cianfhoghlaim/notebooks/`.

4. **Stale notebook reference.** Line 8 reads
   `["edit", "/notebooks/mission_control.py", ...]` — the
   `mission_control.py` file lives at
   `/notebooks/dashboards/mmo/mission_control.py` (per the v4
   consolidation), not at the root.

This change ships the marimo stack with all 4 bugs fixed.

## What changes

### 1 compose.yaml edit (with 4 fixes)

The single file
`bonneagar/stacks/marimo/compose.yaml` is edited:

- **Line 4** image: `marimo/marimo:latest` →
  `ghcr.io/marimo-team/marimo:0.11.19`
- **Line 8** command notebook path:
  `mission_control.py` → `dashboards/mmo/mission_control.py`
- **Line 10** volume mount source:
  `../../oideachais/notebooks` → `../../cianfhoghlaim/notebooks`

The healthcheck, port mapping (`2718:2718`), networks
(`cianfhoghlaim`, `lakehouse_lakehouse` external), and resource
limits (2 CPUs, 2 GB RAM) are unchanged.

### 4 new openspec change files

The change adds **1 ADDED Requirement** to
`oideachais-marimo-dashboards` and **1 ADDED Requirement** to
`infrastructure-stacks`.

## Impact

- **Affected specs:** `oideachais-marimo-dashboards` (shared
  — wait, it's `oideachais` quadrant, not shared; corrected
  below), `infrastructure-stacks` (shared)
- **Affected code:** 1 `compose.yaml` file (3 line changes
  + comment block) + 4 new openspec change files
- **Affected hosts:** `bunchloch` only (the workload host)
- **Risk:** medium — the marimo server (when it starts) may
  require additional dependencies (BAML runtime, DuckDB
  access via lakehouse) that are not bundled in the
  `ghcr.io/marimo-team/marimo:0.11.19` image; if a notebook
  fails to load due to a missing Python module, the operator
  must either (a) add the module to a custom Dockerfile, or
  (b) use `marimo run --no-reload` with a specific
  requirements file
- **Audit gates:** `bun run validate-stacks` + `mise run
  lint:skills` + `openspec validate --strict`

## Non-goals

- **Not exposing all 11 marimo notebooks** as a multi-tab
  dashboard. The marimo CLI's `edit` command runs one
  notebook per process; the spec's "11 marimo notebooks
  across 5 stages + leabharlann" pattern would require
  either (a) multiple marimo processes behind a reverse
  proxy, or (b) a custom landing-page notebook that
  embeds the others. Both are deferred to a follow-up
  change. This change ships the **single-notebook
  mission-control variant** the original compose author
  intended.
- **Not pinning marimo to `0.23.12`** (the latest GitHub
  release). The GHCR max tag is `0.11.19`; marimo-team does
  not auto-publish every release to GHCR. Pinning to the
  latest GHCR tag is the safe compromise. A follow-up could
  build a custom image with `FROM ghcr.io/marimo-team/marimo
  + uv pip install marimo==0.23.12` if the upstream tag
  mismatch is a blocker.
- **Not producing Locket/Infisical integration.** The
  marimo stack uses its existing `secrets.env` defaults;
  no live Infisical round-trip is required.
- **Not migrating `marimo_data` volume contents** from any
  prior marimo install. The volume is freshly created.

## Spec delta

- `oideachais-marimo-dashboards/spec.md` — 1 ADDED Requirement
- `infrastructure-stacks/spec.md` — 1 ADDED Requirement

See `specs/<capability>/spec.md` for the full delta.

## Open follow-up issues

| Issue | Tracking change |
|:--|:--|
| Multi-notebook marimo dashboard (11 tabs, reverse-proxy) | `2026-07-XX-marimo-multi-notebook-dashboard` (deferred) |
| Custom marimo image with `marimo==0.23.12` (latest GitHub release) | `2026-07-XX-marimo-pin-latest-release` (deferred) |
| Build dots-ocr image locally from upstream Dockerfile | `2026-07-XX-bring-dots-ocr-up-to-spec` (deferred) |
| Bring browser stack to GOLD_STANDARD | `2026-07-XX-bring-browser-stack-to-gold-standard` (deferred) |