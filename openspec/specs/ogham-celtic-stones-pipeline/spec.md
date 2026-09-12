# Ogham Celtic Stones Pipeline Capability

## Purpose

`ogham-celtic-stones-pipeline` ingests the CISP (Cornish Inscribed
Stones Project) + Megalithic Portal corpora and emits Anam Particles
that map each stone to its inscription reading + landscape context.

This capability is referenced by:
- `openspec/changes/2026-09-08-ogham-celtic-stones-pipeline-v1`
- `openspec/changes/2026-09-29-familiar-dynamic-nft-system-v1`

## Requirements

### Requirement: CISP ingestion

The pipeline SHALL ingest every CISP stone record (bilingual
Cornish-English metadata + the stone's IIIF image + the Ogham
transcription) and emit one DLT source row per stone.

#### Scenario: CISP record parsed

- **WHEN** the pipeline receives a CISP record with `id`, `name`,
  `parish`, `inscription_text`, `iiif_image_uri`
- **THEN** it SHALL emit a DLT row to `cisp_records` with all
  fields populated and `inscription_text` non-empty

### Requirement: Megalithic Portal ingestion

The pipeline SHALL ingest every Megalithic Portal stone record
(landscape context + grid reference) and emit one DLT source row
per stone.

#### Scenario: Megalithic Portal record parsed

- **WHEN** the pipeline receives a Megalithic Portal record with
  `stone_id`, `lat`, `lon`, `site_type`, `description`
- **THEN** it SHALL emit a DLT row to `megalithic_records` with
  all fields populated

### Requirement: Anam Particle emission

The pipeline SHALL emit an Anam Particle per (stone, visitor)
event so the Familiar NFT system can mint a unique card per visit.

#### Scenario: Stone visit recorded

- **WHEN** a player visits a stone location in the tuatha-ui map
- **THEN** the pipeline SHALL emit an Anam Particle with
  `stone_id`, `player_id`, `timestamp`, `anam_color_hex`
