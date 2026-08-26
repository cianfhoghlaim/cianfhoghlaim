# Spec Delta: tuatha-lance

## ADDED Requirements

### Requirement: The 4 ANAM tables live under the cianfhoghlaim.tuatha.* namespace

The system SHALL create the 4 Lance tables under
`s3://garage/lance/cianfhoghlaim.tuatha.*`:

| Table | Embedding dim | FTS column | Primary key |
|:--|--:|:--|:--|
| `cianfhoghlaim.tuatha.hades.boons` | 1024 | `effect_text` | `boon_id` |
| `cianfhoghlaim.tuatha.comic.particles` | 1024 | `motion_description` | `panel_id` |
| `cianfhoghlaim.tuatha.gba.magic` | 1024 | `sprite_description` | `psynergy_name` |
| `cianfhoghlaim.tuatha.anam_particles` | 1024 | `description_en` | `anam_id` |

All 4 SHALL use the BAAI/bge-m3 1024-d multilingual embedder per the
BIEP v3 canonical pattern.

#### Scenario: The marimo Join tab federates the 4 tables via lance_scan()

- **WHEN** the operator opens `notebooks/tuatha_anam_dashboard.py`
- **AND** clicks the **Join** tab
- **THEN** the notebook SHALL query
  `lance_scan('s3://garage/lance/cianfhoghlaim.tuatha.anam_particles')`
  via DuckDB federation
- **AND** render the rows with their Celtic-deity + ANAM-color
  annotations.
