# Cianfhoghlaim Notebooks

The 70+ Marimo notebooks for the **British-Isles Education pipeline (BIEP)**.
Each notebook is a reactive dashboard AND a standalone CLI script (dual-mode).

## Quick start

```bash
# Interactive — pick a notebook from one of the groups below and open it
uv run marimo edit cianfhoghlaim/notebooks/01_dev_env/01_ccc_search.py

# CLI — invoke from any cwd (the notebook's @__main__ guard detects <flags>)
uv run cianfhoghlaim/notebooks/01_dev_env/01_ccc_search.py --query "Dagster asset"

# Discover + run via the CLI wrapper (auto-lists notebooks in each group)
uv run cianfhoghlaim/notebooks/cli.py list
uv run cianfhoghlaim/notebooks/cli.py run 06_mise_lint_skills -- --path .agents/skills/
```

## Layout — 11 functional groups

| Group | Files | Purpose |
|:--|--:|:--|
| `01_dev_env/` | 6 | The 6 dev-env ADK tools (ccc_search, drift_detect, firecrawl, hf_best_model, openspec_list, mise_lint_skills) |
| `02_vision_models/` | 6 | VLM dispatch explorer + 5 OCR/layout/table/diagram/benchmark notebooks |
| `03_leaving_cert/` | 17 | Per-subject + cross-subject BIEP LC5 analyses (10) + 5 PDF processing + 1 history + 1 root PDFs |
| `04_biep_motherduck/` | 11 | MotherDuck + DuckLake BIEP dashboards + parameterised 6-step subject pipeline |
| `05_lakehouse_inspect/` | 4 | DuckLake + Lance + CocoIndex + DLT pipeline inspection |
| `06_observability/` | 3 | BAML drift audit + Irish fada quality + Cognee KG visualiser |
| `07_educational_stages/` | 7 | 5 NCCA stages + cross-domain + analysis-plan viewer |
| `08_sources/` | 1 | sources.yaml federation (`01_sources_load.py`) |
| `09_official_media/` | 2 | Instagram → gov resolver + email triage |
| `10_mmo/` | 2 | Mission control + Tuatha MMO progress |
| `11_speedrun/` | 9 | SpeedRunEthereum challenges (Celtic-creature NFT theme) |
| `legacy/` | 25 | 1-cycle preservation window — deleted at archive time |
| `analysis_plan/` | 5 | Plan artifacts referenced by `07_educational_stages/07_analysis_plan_viewer.py` |

Total **70 active notebooks + 25 in legacy/**.

## Dual-mode (marimo + CLI)

Every refactored notebook under `01..11_*/` supports both execution modes:

| Mode | Command |
|:--|:--|
| **marimo edit** | `marimo edit notebooks/01_dev_env/01_ccc_search.py` |
| **marimo run**  | `marimo run  notebooks/01_dev_env/01_ccc_search.py` |
| **CLI script**  | `python notebooks/01_dev_env/01_ccc_search.py --query "..."` |
| **CLI via uv**  | `uv run notebooks/01_dev_env/01_ccc_search.py --query "..."` |

The CLI mode uses each notebook's `if __name__ == "__main__"` guard which
parses the BIEP canonical flags (`--subject`, `--level`, `--language`,
`--year`, `--limit`) via `nb_utils.cl_argument_parser()` and prints the
same data to stdout.

## Canonical helpers (`nb_utils.py`)

Re-exported via `from cianfhoghlaim.notebooks import ...`:

| Helper | Use |
|:--|:--|
| `connect_biep_lakehouse(use_md=True)` | MotherDuck + graceful local-DuckDB fallback |
| `connect_md_oideachais()` | Bare MotherDuck connect (raises on failure) |
| `lc_subject_query(subject, level, language)` | Per-subject topic query |
| `leabharlann_join_to_lc(book_id, topic)` | Cross-archive join |
| `cl_argument_parser(...)` | argparse factory with BIEP canonical flags |
| `run_as_script(main_fn, argv)` | Dual-mode CLI helper |
| `import_dev_env_tool()` | Convenience helper for the dev_env tool module |
| `BIEP_SUBJECTS` | The 6 LC priority subjects (math/biology/english/gaeilge/applied_math/chemistry) |
| `BIEP_LEVELS` | `higher / ordinary / foundation` |
| `BIEP_LANGUAGES` | `en / ga` |
| `REPO_ROOT` | The cianfhoghlaim monorepo root |

## Environment variables

| Variable | Default | Notes |
|:--|:--|:--|
| `MOTHERDUCK_TOKEN` | _required for MD_ | Read from Infisical `dev-baile` via mise |
| `MOTHERDUCK_ENABLED` | `false` | Set `true` to opt-in to `md:oideachais` |
| `USE_LOCAL_SCRAPES` | `false` | Set `true` for the curated `stedding/ingest_queue/` snapshot fallback |
| `CIANFHOGHLAIM_LEAVING_CERT_ROOT` | `~/dev/.../leaving_certificate` | Override for the BIEP corpus directory |
| `CIANFHOGHLAIM_LAKEHOUSE_DUCKDB` | `md:oideachais` | DuckDB attach string |
| `CIANFHOGHLAIM_ROOT` | `~/dev/kings_college_galway` | Repo root (overridden by `nb_utils.REPO_ROOT`) |

## Cross-references

- **openspec change**: [`2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep/`](../../openspec/changes/2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep/)
- **capability spec**: [`oideachais-marimo-dashboards`](../../openspec/specs/oideachais-marimo-dashboards/spec.md)
- **BIEP v1**: [`2026-07-06-british-isles-education-pipeline-v1/`](../../openspec/changes/2026-07-06-british-isles-education-pipeline-v1/)
- **dlt skill**: [`.agents/skills/dlt/SKILL.md`](../../../.agents/skills/dlt/SKILL.md)
- **baml skill**: [`.agents/skills/baml/SKILL.md`](../../../.agents/skills/baml/SKILL.md)
- **cocoindex skill**: [`.agents/skills/cocoindex/SKILL.md`](../../../.agents/skills/cocoindex/SKILL.md)
- **motherduck skill**: [`.agents/skills/motherduck/SKILL.md`](../../../.agents/skills/motherduck/SKILL.md)
- **marimo skill**: [`.agents/skills/marimo/SKILL.md`](../../../.agents/skills/marimo/SKILL.md)

## Status (post Phase 9 archive)

After the openspec archive step (Phase 9 of the change), the `legacy/`
directory is deleted. The final layout will be exactly the 70 active
notebooks across the 11 groups above.

## Common issues

**`ModuleNotFoundError: No module named 'cianfhoghlaim'` when running a notebook as a CLI script.**

The notebook's `_cli_main` adds `<repo>/` to `sys.path` via
`Path(__file__).parents[2]`. If you've moved the notebook, update that
reference. Or run via `uv run` from the repo root — the venv already
has the package on `sys.path`.

**`marimo edit` opens but the cell errors with `ImportError` for the `dev_env` tool module.**

The 6 `01_dev_env/*.py` notebooks compute the tool path via
`Path(__file__).resolve().parents[1] / 'agents' / 'adk' / 'tools' / 'dev_env.py'`.
If you move a notebook outside `01_dev_env/`, update that reference too.
