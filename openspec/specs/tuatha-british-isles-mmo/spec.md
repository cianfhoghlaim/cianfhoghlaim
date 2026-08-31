# tuatha-british-isles-mmo Specification

## Purpose

`tuatha-british-isles-mmo` is the standalone implementation
target for the British Isles Formative Assessment MMO. The
canonical GitHub repo is `github.com/cianfhoghlaim/tuatha`
(a sibling sub-app of the Cianfhoghlaim main repo). The
capability implements the canonical
`cianfhoghlaim-educational-mmo` spec for the standalone
deployment context.

## Background

The British Isles Formative Assessment MMO is the
educational platform for the NCCA Leaving Certificate
(Republic of Ireland) + the 7 sister jurisdictions (AQA,
OCR, Pearson, SQA, WJEC, CCEA, Isle of Man Education). The
canonical spec (`cianfhoghlaim-educational-mmo`) covers the
8 NCCA subjects; the standalone `tuatha/` repo implements
those 8 + the 6 NCCA-adjacent subjects (accounting, biology,
business, french, irish T2, physics) per the
`2026-08-26-tuatha-subject-expansion-to-14-v1` change.

The standalone deployment differs from the main
Cianfhoghlaim deployment in three ways:
1. It is independently deployable (no parent monorepo
   dependency at runtime — it consumes the TIER 1 packages
   via `depends_on_tier_1` in `subapp_manifest.yaml`)
2. It is paced per-openspec-change (the main Cianfhoghlaim
   platform is daily)
3. It uses a per-app `mise.toml` + `pyproject.toml` +
   `LICENSE` + `AGENTS.md` — no parent-monorepo coupling

## Requirements

### Requirement: 14-subject coverage (8 NCCA + 6 adjacent)

The standalone `tuatha/` SHALL cover exactly **14** subjects:
the 8 NCCA Leaving Certificate subjects (Mathematics +
Applied Mathematics + Chemistry + Geography + History +
English + Gaeilge + Computer Science) + the 6 NCCA-adjacent
subjects (Accounting + Biology + Business + French + Irish T2
+ Physics).

#### Scenario: Each subject has a complete per-subject stack

- **GIVEN** the post-expansion `tuatha/` repo
- **WHEN** the agent verifies the subject coverage
- **THEN** each of the 14 subjects SHALL have:
  - 1 `tuatha/subjects/<subject>.py` ADK LlmAgent
  - 5 `tuatha/tools/<subject>_<tool>.py` per-subject tools
  - 1 `tuatha/baml/qpack_<subject>.baml` BAML contract
  - 1 `tuatha/dlt/{syllabus,past_paper,marking_scheme,formative_item,response_score}/<subject>.py` DLT source
  - 1 `tuatha/web/apps/tuatha-ui/src/routes/realm/<subject>.tsx` PixiJS realm route
  - 1 `tuatha/web/packages/realm-canvas/src/subjects/<subject>.ts` sprite bank

### Requirement: Single MMO client

The standalone `tuatha/` SHALL ship a single MMO client
(PixiJS v8 2.5D Hades-orthographic renderer at
`tuatha/web/packages/realm-canvas/`) with the canonical
TanStack Start 2D surface at `tuatha/web/apps/tuatha-ui/`.

#### Scenario: The PixiJS canvas mounts on every /realm/<subject> route

- **GIVEN** the post-expansion `tuatha/` repo
- **WHEN** the agent navigates to `/realm/<subject>` for any
  of the 14 subjects
- **THEN** the page SHALL render the `RealmPage` component
  with the per-subject sprite bank + the Convex quest query
  + the CopilotKit AG-UI chat panel

### Requirement: Per-subject SUBJECT_WIRING_REGISTRY entries

Every subject SHALL be registered in
`tuatha/routing.py:SUBJECT_WIRING_REGISTRY` with the
canonical 8-field `SubjectAgentWiring` (ncca_subject /
module_slug / display_name / baml_prefix /
langfuse_trace_name / cognee_dataset / letta_agent_id /
litellm_routing_key).

#### Scenario: The 14-subject registry dispatches all 14 buckets

- **GIVEN** the post-expansion `tuatha/routing.py`
- **WHEN** the agent invokes `route_message()` with a
  keyword from any of the 14 `ROUTING_KEYWORDS` buckets
  (math / appm / chem / geog / hist / engl / gael / comp +
  acct / biol / bus / fren / iris / phys)
- **THEN** the dispatch SHALL return the correct module_slug
- **AND** `route_message_to_wire()` SHALL return the
  canonical `SubjectAgentWiring` for the matching subject

### Requirement: Independent deployable sibling subapp

The standalone `tuatha/` SHALL be deployable as an
independent TIER 3 subapp per the
`web-frontend-3-tier` architecture. The
`subapp_manifest.yaml` at the repo root declares the
`depends_on_tier_1` packages (model-registry, fleet,
theming, agui-bridge, observability, dlt-common, auth,
baml-helpers, ui-kit) + the pace_layer
(per_openspec_change) + the deployment_target (parent).

#### Scenario: The subapp_manifest.yaml is valid

- **GIVEN** the post-expansion `tuatha/` repo
- **WHEN** the parent's `sync_subapps.py` reads
  `tuatha/subapp_manifest.yaml`
- **THEN** the parser SHALL validate the manifest against
  the canonical `subapp_manifest.template.yaml` schema
- **AND** the manifest SHALL list all 9 TIER 1 packages
  in `depends_on_tier_1`

## Out of scope

- The 8 NCCA + 6 adjacent expansion is the ONLY spec
  extension this file owns. The 8 NCCA subjects continue
  to be governed by the canonical
  `cianfhoghlaim-educational-mmo` spec in the main repo.
- The on-chain AchievementToken credential is governed by
  the `learn-to-earn-token-credential` spec (cross-repo
  reference; mirrored in `tuatha/openspec/specs/`).
- The 2D + 2.5D asset pipeline is governed by the
  `celtic-asset-generation` spec (cross-repo reference).

## See also

- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` —
  the canonical spec the standalone tuatha implements
- `openspec/specs/celtic-asset-generation/spec.md` — the
  asset pipeline spec (FIBO + Unsloth Studio image gen)
- `openspec/specs/learn-to-earn-token-credential/spec.md`
  — the on-chain credential spec
- `openspec/changes/2026-08-26-tuatha-subject-expansion-to-14-v1/`
  — the openspec change that authored this spec
- `../../subapp_manifest.yaml` — the TIER 3 subapp
  declaration
