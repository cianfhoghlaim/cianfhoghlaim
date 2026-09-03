# `dlt_sources/` — DLT ingestion layer

> **The canonical post-v7 Python sub-package for DLT sources + destinations + cross-jurisdiction registry + common helpers.**

## Quick start

```bash
# The 6 CLI subcommands
uv run python -m dlt_sources.cli list-sources

# Run the Ireland BIEP v3 generic pipeline (no MotherDuck auth required for the object to load)
python -c "from dlt_sources.british_isles.ireland.education.ireland_jurisdiction_pipeline import ireland_jurisdiction_pipeline; print(ireland_jurisdiction_pipeline.jurisdiction)"
# -> ireland

# Run with the curated local scrape cache (no API credits consumed)
USE_LOCAL_SCRAPES=true uv run python -c "from dlt_sources.british_isles.ireland.education.ireland_jurisdiction_pipeline import ireland_jurisdiction_pipeline; ireland_jurisdiction_pipeline.run()"

# Run with full MotherDuck destination (requires MOTHERDUCK_TOKEN)
MOTHERDUCK_TOKEN=$MOTHERDUCK_TOKEN uv run python -c "from dlt_sources.british_isles.ireland.education.ireland_jurisdiction_pipeline import ireland_jurisdiction_pipeline; ireland_jurisdiction_pipeline.run()"
```

## Layout — 13 sub-trees

| Sub-tree | Files | Purpose |
|:--|--:|:--|
| `british_isles/` | many | The BIEP focus: ireland + england + scotland + wales + ni + isle_of_man + jersey + guernsey + sct_wls_ni + crown_dependencies + `_cross/` |
| `european_nations/` | many | 40 nations × {education, government, law, medicine, statistics} |
| `european_union/` | many | EUR-Lex + CEDEFOP + ECDC + EMA + Eurostat + Eurydice + Commission press + ... |
| `commonwealth/` | many | australia + canada (12 provinces + quebec/montreal) + india + new_zealand + nigeria (federal + 36 states) + south_africa |
| `american_nations/` | many | brazil + mexico + united_states (CA) + venezuela |
| `common/` | 25 | destinations + endpoint_recovery + observability + http_client + motherduck_options + ... |
| `language/` | many | Logainm + Téarma + Ainm + Gaois + Dúchas + Canúint (Celtic-language sources) |
| `official_media/` | many | British Crown + Channel Islands government official-media feeds |
| `api_sources/` | 9 | Spotify + SoundCloud + YouTube + GitHub + LinkedIn + ResearchGate (generic non-jurisdictional) |
| `filesystem/` | 10 | DLT filesystem pipeline utilities |
| `jobs/` | 2 | Long-running scheduled jobs (only `government_circulars_job.py`) |
| `portfolio/` | 6 | CV + teaching + artwork + labels (personal portfolio data) |
| `apple_photos/` | 1 | Stub (the 5th leabharlann corpus via osxphotos — deferred per the `apple-photos-ingestion` openspec change) |

## The BIEP v3 jurisdiction pipeline pattern

The canonical reference is `dlt_sources/british_isles/ireland/education/ireland_jurisdiction_pipeline.py`. Subclass `JurisdictionPipelineBase` (at `british_isles/_cross/jurisdiction_pipeline_base.py:33`) to add a new jurisdiction:

```python
from dlt_sources.british_isles._cross.jurisdiction_pipeline_base import JurisdictionPipelineBase

class MyJurisdictionPipeline(JurisdictionPipelineBase):
    STAGE = "leaving_certificate"

    def build_pipeline_resource(self, pipeline):
        @dlt.resource(name="documents", write_disposition="merge", primary_key=["content_hash"])
        def documents():
            for subject in self.subjects():
                yield {"subject": subject, "content_hash": ..., "url": ..., "text": ...}
        return documents

my_pipeline = MyJurisdictionPipeline("my_jurisdiction")
my_pipeline.run()  # writes to md:cianfhoghlaim.education.my_jurisdiction.*
```

## The 3 critical conventions

1. **Always use relative imports** within `dlt_sources/`
2. **Respect the ingestion cache** — `USE_LOCAL_SCRAPES=true` routes all extractions through the curated `stedding/ingest_queue/` snapshot
3. **Zero absolute namespaces** — never `from cianfhoghlaim.dlt.* import ...` from within the data platform

## Environment variables

| Variable | Default | Notes |
|:--|:--|:--|
| `USE_LOCAL_SCRAPES` | `false` | Set `true` for the curated `stedding/ingest_queue/` snapshot fallback |
| `MOTHERDUCK_TOKEN` | _required for MD_ | Read from Infisical `dev-baile` via mise |
| `MOTHERDUCK_ENABLED` | `false` | Set `true` to opt-in to `md:cianfhoghlaim` |
| `CIANFHOGHLAIM_ROOT` | `~/dev/kings_college_galway` | Repo root (overridden by `nb_utils.REPO_ROOT`) |
| `BIEP_REGISTRY_URI` | local DuckDB | Override for the cross-jurisdiction registry location |

## Cross-references

- [`AGENTS.md`](AGENTS.md) — the canonical quadrant overview (the agent-facing entry point)
- [`LEGACY_ALIASES.md`](LEGACY_ALIASES.md) — the v7 ISO-3 → snake_case rename map (historical)
- [`../.agents/skills/dlt/SKILL.md`](../.agents/skills/dlt/SKILL.md) — the DLT master routing skill
- [`../.agents/skills/motherduck/SKILL.md`](../.agents/skills/motherduck/SKILL.md) — MotherDuck connection options
- [`../openspec/specs/british-isles-education-pipeline/spec.md`](../openspec/specs/british-isles-education-pipeline/spec.md) — flagship BIEP spec