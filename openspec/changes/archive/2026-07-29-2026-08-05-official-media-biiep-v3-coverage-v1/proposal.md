## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

# 2026-08-05-official-media-biiep-v3-coverage-v1

## Why

The `official-media` pipeline at `dlt/official_media/` currently only
covers 3 of the 8 British Isles jurisdictions (England, Wales, Scotland).
With BIEP v3 shipping the canonical registry + generic jurisdiction
pipelines, the official-media pipeline can finally extend to all 5
UK + Crown Dependencies jurisdictions. This plan consolidates 6 issues
into one coordinated change.

This change lives in the **cianfhoghlaim repo**.

## What changes

### 1. PR 2: add SCT + WLS + IoM + JEY + GGY jurisdictions (closes #47)

- Extend `dlt/official_media/source_resolver.py` with the 5 missing
  jurisdiction resolvers
- Update `dlt/official_media/classifier.py` with the 5 new
  `official-media` feeds (Scottish Parliament, Senedd Cymru, Tynwald,
  States of Jersey, States of Guernsey)
- Add 5 new BAML classification targets
- Add 5 new Dagster assets (1 per jurisdiction)

### 2. side-loadable PWA / iOS / Android app (Phase 2) (closes #48)

- Add the `web/apps/official-media-pwa/` directory (TanStack Start + PWA manifest)
- Configure service worker for offline access
- Add iOS / Android wrappers via Tauri or Capacitor
- Wire the PWA to the `official-media` Hono API endpoint
- Add `mise run pwa:dev` + `mise run pwa:build` tasks

### 3. HMGCC co-creation sub-asset — 12-week rolling window (closes #49)

- Add the `dlt/official_media/hmgcc/` sub-asset
- 12-week rolling window of HMGCC (His Majesty's Government
  Communications Centre) publications
- Classify via the existing `classifier.py`
- Tag with `source: hmgcc` for provenance
- Add a Dagster asset `hmgcc_rolling_window`

### 4. Companies House re-identification (closes #50)

- Add the `dlt/official_media/companies_house_crown_filter.py`
  sub-asset
- Crown bodies are listed on Companies House but have `crown_body: true`
- Filter to distinguish Crown bodies (no personal officers) from
  registered companies (have directors)
- Add the canonical 6 Crown bodies registry (UK government + devolved
  + Crown Dependencies)

### 5. Deplatforming-thesis paper (closes #51)

- Add the `docs/theses/deplatforming_thesis.md` Markdown
- Cross-reference the existing `regulating_big_tech_in_british_isles.pdf`
- 1-page executive summary + 10-section outline
- Add to `docs/THESES.md` index

### 6. meaisinfhoghlaim web analyzer (closes #35)

- The web app is now shipped (B4 from the BIEP v3 followup wave)
- Add the `web/apps/cianfhoghlaim-web/src/routes/analyzer/` directory
- TanStack Start page that displays the meaisinfhoghlaim agent
  analysis output for any text input
- Wire to the meaisinfhoghlaim-web Hono endpoint

## Dependencies

```yaml
Blocked by: 2026-08-03-biep-v3-web-app-routes-hono-endpoints-v1
Blocked by (soft): 2026-07-31-biep-v3-crown-dependencies-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `dlt/official_media/source_resolver.py:resolve("tynwald", ...)` returns
  a valid Isle of Man media source
- The PWA loads at `localhost:3000/official-media-pwa/` with a valid
  service worker
- The HMGCC rolling window runs daily at 02:00 UTC
- The Companies House filter correctly identifies the 6 Crown bodies
- `openspec validate 2026-08-05-official-media-biiep-v3-coverage-v1 --strict` passes

## Cross-references

- `dlt/official_media/{source_resolver,classifier}.py` (the existing pipeline)
- `agents/meaisinfhoghlaim/agent_fleet/` (the agent orchestrator)
- `openspec/specs/official-media-pipeline/spec.md` (the umbrella spec)
- `.agents/skills/agent-fleet-orchestration/SKILL.md`
- GitHub issues #47, #48, #49, #50, #51, #35