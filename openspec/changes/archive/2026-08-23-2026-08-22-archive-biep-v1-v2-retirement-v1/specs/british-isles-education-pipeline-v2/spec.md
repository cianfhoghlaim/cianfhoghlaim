# Spec Delta: british-isles-education-pipeline-v2

## REMOVED Requirements

### Requirement: 4-jurisdiction BIEP coverage

**Reason**: Pre-v3 transitional spec. The canonical 8-jurisdiction plan is documented in `british-isles-education-pipeline-v3` (Requirement "BIEP v3 6-deferred-jurisdiction plan (M5-M10)").
**Migration**: Load `british-isles-education-pipeline-v3` for the canonical jurisdiction coverage.

### Requirement: 4-path OCR/VLM ensemble with RAGAS voting

**Reason**: Pre-v3 transitional spec. The canonical OCR ensemble is documented in `meaisinfhoghlaim-ocr-htr` (Requirements on the 24-model 4-backend v4 registry + BAML Collector API integration) and the 4-path ensemble is implemented in `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`.
**Migration**: Load `meaisinfhoghlaim-ocr-htr` for the canonical OCR ensemble spec.

### Requirement: Cross-jurisdiction marimo portal

**Reason**: Pre-v3 transitional spec. The canonical marimo dashboards are documented in `cianfhoghlaim-marimo-dashboards` (10 requirements) and the cross-jurisdiction portal is one of the dashboards.
**Migration**: Load `cianfhoghlaim-marimo-dashboards` for the canonical marimo portal.

### Requirement: England ChangeDetection freshness guarantee

**Reason**: Pre-v3 transitional spec. The ChangeDetection.io monitoring + Firecrawl monitor + Dagster sitemap-hash sensor pattern is documented in the `upstream-package-monitoring` spec.
**Migration**: Load `upstream-package-monitoring` for the canonical change-detection pattern.

## ADDED Requirements

### Requirement: v2 retirement — see british-isles-education-pipeline-v3

The system SHALL recognize that `british-isles-education-pipeline-v2` is a transitional retirement marker. The canonical capability is `british-isles-education-pipeline-v3` (25 requirements) which covers the 5-milestone sequential plan + the 6-deferred-jurisdiction plan (M5-M10) + the 2-scanner-domain plan + the 4-cadence scheduling policy + the 5-phase pattern (Ingestion → Extraction → Embedding → ibis logging → Analytics).

The original v1 spec `british-isles-education-pipeline` (41 requirements) covers the original LC subjects + gov.ie circulars; the v3 spec layers on top of v1 with the milestone plan + 8-jurisdiction expansion.

Per the 2026-08-22-openspec-audit-and-merge-v1 audit + the 2026-08-22-archive-biep-v1-v2-retirement-v1 retirement change.

#### Scenario: Agent looks up the canonical BIEP v3 spec

- **WHEN** an agent reads `openspec/list --specs` to find the 5-milestone BIEP plan
- **THEN** the agent SHOULD load `british-isles-education-pipeline-v3` (the canonical)
- **AND** the transitional v2 spec is preserved as a retirement marker