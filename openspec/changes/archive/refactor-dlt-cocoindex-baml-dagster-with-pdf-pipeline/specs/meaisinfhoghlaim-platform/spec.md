## MODIFIED Requirements

### Requirement: All dagster assets live under by_domain/

Per the v3 consolidation plan, the 65+ dagster asset files SHALL be
organised under `dagster/assets/by_domain/` by domain. The legacy
top-level paths (`dagster/assets/{subject}_assets.py`) SHALL be
preserved as backward-compat shim files for one release.

#### Scenario: A developer accesses a legacy asset path

- **WHEN** `from cianfhoghlaim.dagster.assets.english_assets import english_syllabus_raw` is used
- **THEN** the import resolves via the shim at
  `dagster/assets/english_assets.py` which re-exports from
  `dagster/assets/by_domain/education/english_assets.py`