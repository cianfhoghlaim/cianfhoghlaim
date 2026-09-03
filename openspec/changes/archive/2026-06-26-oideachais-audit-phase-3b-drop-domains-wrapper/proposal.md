# Drop `dlt_sources/domains/` wrapper — country-first layout

## Why

The current canonical layout `dlt_sources/domains/{domain}/{nation}/{entity}.py` has the domain first when only `education/` is populated. This adds an extra nesting level with no value when 99% of sources are education. The legacy `dlt_sources/{ireland,uk,crown_dependencies}/` paths are already country-first.

Per Round 11 design (2026-06-26, user-confirmed): the country-first layout `dlt_sources/{nation}/{domain}/{entity}.py` is the canonical target. This change drops the `domains/` wrapper for the canonical DLT source tree only.

## Scope

**In scope (this change):**
- The 53 files under `sruth/oideachais/dlt_sources/domains/` move to `sruth/oideachais/dlt_sources/{nation}/{domain}/{entity}.py`
- Shims at the new locations continue to re-export from the LEGACY `oideachais.dlt_sources.{ireland,uk,crown_dependencies}.*` paths
- All 30+ importers that reference `dlt_sources.domains.*` get updated to `dlt_sources.{nation}.{domain}.*`
- The empty `domains/` tree is deleted

**Out of scope (deferred to follow-up changes):**
- Migrating legacy `dlt_sources/{ireland,uk,crown_dependencies,celtic,bunchloch,geospatial,official_media}/` source files to canonical paths (Phase 3C)
- Splitting multi-source files per source (Phase 3D)
- Deleting the legacy `dlt_sources/{ireland,uk,crown_dependencies,celtic,bunchloch,geospatial,official_media}/` trees (Phase 3E)
- Restructuring the parallel `dagster_defs/assets/{domain}/{nation}/` tree (separate change)

## What changes

### Canonical dlt_sources tree (53 files)

Move:
- `dlt_sources/domains/__init__.py` → `dlt_sources/__init__.py` (re-export surface)
- `dlt_sources/domains/cross/upstream/blog_post.py` → `dlt_sources/cross/upstream/blog_post.py`
- `dlt_sources/domains/culture/ie/heritage_source.py` → `dlt_sources/ie/culture/heritage.py`
- `dlt_sources/domains/education/{en,ggy,ie,iom,jey,ni,sct,wls}/__init__.py` → `dlt_sources/{nation}/education/__init__.py`
- `dlt_sources/domains/law/_legislation_helper.py` → `dlt_sources/law/_legislation_helper.py`
- `dlt_sources/domains/law/{en,ggy,ie,iom,jey,ni,sct,wls}/__init__.py` → `dlt_sources/{nation}/law/__init__.py`
- `dlt_sources/domains/law/{en,ggy,iom,jey,ni,sct,wls}/legislation.py` → `dlt_sources/{nation}/law/legislation.py`
- `dlt_sources/domains/law/ie/doj.py` → `dlt_sources/ie/law/doj.py`
- `dlt_sources/domains/law/ie/irish_statute_book.py` → `dlt_sources/ie/law/irish_statute_book.py`
- `dlt_sources/domains/law/ie/lawreform.py` → `dlt_sources/ie/law/lawreform.py`
- `dlt_sources/domains/medicine/{en,ggy,ie,iom,jey,ni,sct,wls}/__init__.py` → `dlt_sources/{nation}/medicine/__init__.py`
- `dlt_sources/domains/medicine/en/{gmc,nhs_england,nice}.py` → `dlt_sources/en/medicine/{gmc,nhs_england,nice}.py`
- `dlt_sources/domains/medicine/ggy/health_social_care.py` → `dlt_sources/ggy/medicine/health_social_care.py`
- `dlt_sources/domains/medicine/ie/{doh,hpsc,hse,medical_council}.py` → `dlt_sources/ie/medicine/{doh,hpsc,hse,medical_council}.py`
- `dlt_sources/domains/medicine/iom/health_social_care.py` → `dlt_sources/iom/medicine/health_social_care.py`
- `dlt_sources/domains/medicine/jey/health_community_services.py` → `dlt_sources/jey/medicine/health_community_services.py`
- `dlt_sources/domains/medicine/ni/nidirect.py` → `dlt_sources/ni/medicine/nidirect.py`
- `dlt_sources/domains/medicine/sct/nhs_scotland.py` → `dlt_sources/sct/medicine/nhs_scotland.py`
- `dlt_sources/domains/medicine/wls/nhs_wales.py` → `dlt_sources/wls/medicine/nhs_wales.py`
- `dlt_sources/domains/site_analysis.py` → `dlt_sources/site_analysis/site_analysis.py`

### Importers updated (~30 files)

- `sruth/oideachais/cognee_integration/culture_cognify.py` — `dlt_sources.domains.culture.ie.heritage_source` → `dlt_sources.ie.culture.heritage`
- `sruth/oideachais/dagster_defs/assets/ie/law/__init__.py` — `dlt_sources.domains.law.ie.*` → `dlt_sources.ie.law.*`
- `sruth/oideachais/dagster_defs/assets/ie/medicine/__init__.py` — same
- `sruth/oideachais/dagster_defs/assets/law/{nation}/__init__.py` (8 files) — `dlt_sources.domains.law.{nation}.*` → `dlt_sources.{nation}.law.*`
- `sruth/oideachais/dagster_defs/assets/medicine/{nation}/__init__.py` (8 files) — `dlt_sources.domains.medicine.{nation}.*` → `dlt_sources.{nation}.medicine.*`
- `sruth/oideachais/dagster_defs/assets/site_analysis/extract.py` — `dlt_sources.domains.site_analysis` → `dlt_sources.site_analysis.site_analysis`
- `sruth/oideachais/dagster_defs/assets/upstream_monitoring_assets.py` — same
- `sruth/oideachais/dlt_sources/uk/{england,northern_ireland,scotland,wales}/__init__.py` (4 files) — `dlt_sources.domains.{education,law,medicine}.{nation}.*` → `dlt_sources.{nation}.{education,law,medicine}.*`
- `sruth/oideachais/tests/dlt_sources/domains/ie/test_ie_medicine_and_law.py` — same
- `sruth/oideachais/tests/dlt_sources/domains/uk/test_crown_deps.py` — same
- `sruth/oideachais/tests/dlt_sources/domains/uk/test_uk_medicine_and_law.py` — same
