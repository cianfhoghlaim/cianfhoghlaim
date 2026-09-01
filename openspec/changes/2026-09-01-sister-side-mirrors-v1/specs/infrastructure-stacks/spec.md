## ADDED Requirements

### Requirement: Each sister repo MUST receive a deeply-per-sister-repo customisation (not a wholesale copy)

The Cianfhoghlaim infrastructure-stacks capability MUST distribute
the v6 era learnings (Phases 1-7) to the 6 sister repos via
per-sister-repo customisations, NOT via wholesale copies of the
cianfhoghlaim source tree.

Per the 2026-09-01-sister-side-mirrors-v1 change (Phase 8 of
the cianfhoghlaim-nua v6 era plan), each sister repo receives
a curated subset of the cianfhoghlaim substrate:

- **bonneagar** — the 6 GCP mirror stacks + Stackdriver AI Agent
  ADK instrumentation
- **tuatha** — the Primary + UnslothGemma4 + VertexGemini35Flash
  BAML clients + ADK 2-stage coordinators
- **ciancheiltis** — the 6 Celtic-language BAML extraction path
  + BGE-M3 embedder swap
- **ciandlithe** — Document AI OCR-ensemble path-1 + the OSINT
  legal-doc pipeline
- **cianchosaint** — the OSINT defence pipeline + Cloud Run ADK
  2-stage coordinators
- **gemini_hackathon** — the Phase 1-7 OSS-first substrate +
  per-PR reciprocal mirror + per-sister Langfuse project mapping

#### Scenario: The bonneagar sister repo receives the GCP mirror stacks

- **WHEN** `2026-09-01-bonneagar-sister-umbrella-mirror-v1/` archives
- **THEN** the 6 GCP mirror stacks (`gcp-gemini-vertex` +
  `gcp-gemma-unsloth` + `gcp-bigquery-mirror` + `gcp-gcs-bucket` +
  `gcp-secret-manager` + `gcp-cloud-run`) are promoted from
  Phase 3 to canonical in `bonneagar/stacks/`
- **AND** the Stackdriver AI Agent ADK instrumentation is documented
  in `bonneagar/AGENTS.md`

### Requirement: The 6 sister-side umbrella-mirror changes MUST be activated in Phase 8

The Cianfhoghlaim infrastructure-stacks capability MUST activate
the 6 sister-side umbrella-mirror changes (authored in Phase 0)
during Phase 8 of the v6 era plan:

1. `2026-09-01-bonneagar-sister-umbrella-mirror-v1/`
2. `2026-09-01-tuatha-sister-umbrella-mirror-v1/`
3. `2026-09-01-ciancheiltis-sister-umbrella-mirror-v1/`
4. `2026-09-01-ciandlithe-sister-umbrella-mirror-v1/`
5. `2026-09-01-cianchosaint-sister-umbrella-mirror-v1/`
6. `2026-09-01-gemini-hackathon-sister-umbrella-mirror-v1/`

Activation promotes each mirror from a passive awareness
document into a per-sister-repo transfer specification.

#### Scenario: The 6 sister-side mirrors are activated

- **WHEN** `2026-09-01-sister-side-mirrors-v1` archives
- **THEN** `openspec list` shows all 6 sister-side mirrors in the
  archived list
- **AND** the soft-cut feature flags from Phase 5 are removed
  (the sister repos now consume the canonical BAML functions
  directly)