# 2026-08-10-biep-v3-preflight-bug-fixes-v1

## Why

The 2026-08-06 → 2026-08-09 BIEP v3 hardening batch (4 openspec changes,
28 items, ~+710 LOC) shipped + pushed to
`origin/openspec/2026-07-25-refactor-batch-v1`. A pre-deploy audit on
2026-07-18 found 5 silent-failure bugs that would break the operational
population of the lakehouse:

1. **`motherduck/flights/config.yaml:113-129`** — the 4 BIEP v3 flight
   entries are column-0 hyphens, NOT under the `flights:` key. A strict
   YAML parser will only load the first 9 daily-sync flights; the 4
   BIEP v3 flights will be silently dropped from the MotherDuck Flight
   scheduler.

2. **`baml_src/clients_biep_v3.py:13`** — `BIEPV3ExtractStrong =
   "qwen3-vl-8b-it"` is a vision-language model. The Strong client is
   intended for high-fidelity text-only extraction (curriculum syllabus,
   marking scheme analysis); a VLM is slower, more expensive, and lower
   text fidelity. Copy-paste bug from `BIEPV3Vision`.

3. **`dlt/common/motherduck_snapshots.py`** — the 3 API-calling
   functions (`snapshot_database`, `create_share`, `attach_share`)
   return dicts without calling the MotherDuck REST API. Any caller
   expecting a real snapshot/share will silently no-op. The BIEP v3
   MotherDuck Flights need real snapshot/share to publish results to
   `api.motherduck.com`.

4. **`dlt/british_isles/_cross/registry_loader.py:677-679`** — the
   `seed_registry()` docstring claims 1,560 rows; the actual loader
   emits 3,780 (because `_load_subjects_by_jurisdiction` multiplies by
   2 languages for 6 of the 8 jurisdictions). The docstring is wrong
   AND no assertion catches the drift.

5. **`dlt/british_isles/_cross/jurisdiction_pipeline_base.py:30-70`** —
   `JurisdictionPipelineBase` is defined but unused. The 4 BIEP v3
   jurisdiction pipelines duplicate ~30 LOC of boilerplate each
   (~120 LOC total).

These 5 fixes unblock `2026-08-11-biep-v3-lakehouse-population-v1`,
the operational population of the lakehouse.

## What changes

### 1. YAML flight config fix (`motherduck/flights/config.yaml:113-129`)

Re-indent the 4 BIEP v3 entries by 2 spaces so they sit under
`flights:`:

```yaml
flights:
  - name: ireland_full_coverage_flight      # ← was column-0
    module: cianfhoghlaim.motherduck.flights.ireland_full_coverage_flight
    callable: build_ireland_full_coverage_flight
    cron: "0 2 * * *"
  # ... (same for england, sct_wls_ni, crown_dependencies)
```

### 2. Strong client model fix (`baml_src/clients_biep_v3.py:13`)

```python
# Before:
BIEPV3ExtractStrong = "qwen3-vl-8b-it"
# After:
BIEPV3ExtractStrong = "gemma-3-27b-it"
```

### 3. MotherDuck snapshots httpx implementation (`dlt/common/motherduck_snapshots.py`)

Add `httpx` + `tenacity` to `pyproject.toml` dependencies. Implement
the 3 API-calling functions with `httpx` POSTs against
`api.motherduck.com`:

- `snapshot_database(name, parent_database, at_timestamp=None)` —
  POST `/v1/databases/{parent_database}/snapshots`
- `create_share(name, database, read_only=True)` —
  POST `/v1/shares`
- `attach_share(share_url, as_, read_only=True)` —
  POST `/v1/shares/attach`

All 3 use `tenacity.Retry(stop=stop_after_attempt(3),
wait=wait_exponential(multiplier=1, min=2, max=10))` and read
`MOTHERDUCK_TOKEN` from the env for auth.

`compute_size_env()` stays as-is (env-var reader, no HTTP needed).

### 4. Registry docstring fix + 3,780-row assertion (`dlt/british_isles/_cross/registry_loader.py:674-707`)

Fix the docstring from "1,560 rows" to "3,780 rows":

```python
"""Seed the registry with all 8 BIEP v3 jurisdictions (full coverage).

Returns a dict with the count of rows inserted per jurisdiction.
Total: Ireland 544 + England 276 + Scotland 600 + Wales 640 +
NI 280 + Jersey 480 + Guernsey 480 + IoM 480 = 3,780 rows.
Each cohort is enumerated × 2 languages (en, ga) where the awarding
body publishes a bilingual curriculum.
"""
```

Add an assertion at the end of `seed_registry()` so future loader
changes fail loudly if the count drifts:

```python
def seed_registry() -> dict[str, int]:
    # ... (existing logic) ...
    counts: dict[str, int] = {...}
    actual = sum(counts.values())
    expected = 3_780
    assert actual == expected, (
        f"seed_registry() expected {expected} rows, got {actual}. "
        "Either the loader was changed or the docstring needs updating."
    )
    return counts
```

### 5. JurisdictionPipelineBase inheritance refactor (`dlt/british_isles/_cross/jurisdiction_pipeline_base.py`)

Add 2 helper methods to the existing `JurisdictionPipelineBase`
class (`subject_to_row()` + `build_pipeline()`) and refactor the 4
BIEP v3 jurisdiction pipelines to inherit from it. Removes ~120 LOC
of duplicated boilerplate.

```python
class JurisdictionPipelineBase:
    """Shared base for the 4 BIEP v3 jurisdiction pipelines."""

    VALID_JURISDICTIONS = (
        "ireland", "england", "scotland", "wales",
        "northern_ireland", "jersey", "guernsey", "isle_of_man",
    )
    WRITE_DISPOSITION = "merge"
    PRIMARY_KEY = ["content_hash"]

    def __init__(self, jurisdiction: str, *, use_md: bool = True):
        if jurisdiction not in self.VALID_JURISDICTIONS:
            raise ValueError(f"unknown jurisdiction: {jurisdiction!r}")
        self.jurisdiction = jurisdiction
        self.destination = get_dlt_destination(use_ducklake=use_md)

    def build_pipeline(self, dataset_name: str | None = None):
        return dlt.pipeline(
            pipeline_name=f"{self.jurisdiction}_jurisdiction_pipeline",
            dataset_name=dataset_name or f"{self.jurisdiction}_education",
            destination=self.destination,
        )

    def subject_to_row(self, row, stage: str) -> dict:
        return {
            "source_id": f"british_isles.{self.jurisdiction}.education.{stage}.{row.board or 'none'}.{row.subject_slug}",
            "country_code": self.jurisdiction,
            "jurisdiction": self.jurisdiction,
            "education_stage": stage,
            "exam_board": row.board,
            "subject": row.subject_slug,
            "qualification_level": row.qualification_level or "untiered",
            "language": row.language,
            "baml_function": row.baml_function,
            "concept": row.concept,
            "source_url": row.source_url,
            "display_name_en": row.display_name_en,
            "display_name_local": row.display_name_local,
            "last_verified": row.last_verified or datetime.now(UTC).isoformat()[:10],
            "ingested_at": datetime.now(UTC).isoformat(),
            "namespace": f"cianfhoghlaim.education.{self.jurisdiction}.{stage}.{row.board or 'none'}.{row.subject_slug}",
        }
```

The 4 pipeline files (Ireland, England, SCT+WLS+NI, Crown Dependencies)
become ~25 LOC of subclass definitions each.

## Dependencies

```yaml
Blocked by: none
Blocked by (soft): 2026-08-09-biep-v3-cross-cutting-docs-v1
Affected repos: cianfhoghlaim
```

## Acceptance gates

- `openspec validate 2026-08-10-biep-v3-preflight-bug-fixes-v1 --strict` passes
- `python -c "import yaml; yaml.safe_load(open('motherduck/flights/config.yaml'))"` succeeds
- `dg list jobs | grep -E "(ireland|england|sct_wls_ni|crown_dependencies)_full_coverage_flight"` shows 4 entries
- `baml-cli generate` regenerates cleanly
- `mise run biep:v3:registry:seed` returns 3,780 rows + passes assertion
- All 4 BIEP v3 jurisdiction pipelines inherit from `JurisdictionPipelineBase`
- `dg list assets | grep jurisdiction_pipeline` still shows the same 4 pipelines
- `mise run lint:skills` passes (53/53)
- `mise run turbo dev` boots without errors

## Cross-references

- `dlt/common/destinations_cianfhoghlaim.py` (the canonical destination factory)
- `dlt/british_isles/_cross/registry_api.py` (the canonical registry read API)
- `baml_src/clients_biep_v3.py` (the 3 canonical BAML clients)
- `motherduck/flights/config.yaml` (the flight registry)
- `.agents/skills/dlt/SKILL.md` (DLT patterns)
- `.agents/skills/baml/SKILL.md` (BAML client conventions)
- `.agents/skills/motherduck/SKILL.md` (MotherDuck destination modes)