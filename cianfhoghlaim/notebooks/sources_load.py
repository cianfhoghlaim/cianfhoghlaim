# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.10",
#     "ibis-framework[duckdb]>=9.0",
#     "pyyaml>=6.0",
#     "polars>=1.0",
#     "duckdb>=1.0",
# ]
# ///
"""
Sources Load — federate every source-registry YAML under sruth/
into a single DuckDB file. Read-only: the upstream YAMLs are
never modified.

Usage:
    cd sruth/oideachais
    uv run marimo edit notebooks/sources_load.py

The DuckDB file is written to <repo-root>/registry.duckdb by
default (gitignored). Re-running overwrites the `sources_raw`
table — your downstream pruning happens in OTHER tables you
create after this notebook has run.
"""
import marimo

__generated_with = "0.10.14"
app = marimo.App(width="medium")


# ─────────────────────────────────────────────────────────────────────────────
# Cell 1 — imports + intro
# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _():
    import hashlib
    import json
    import os
    from pathlib import Path

    import ibis
    import marimo as mo
    import polars as pl
    import yaml

    REPO_ROOT = Path(os.environ.get("CIANFHOGHLAIM_ROOT", Path.cwd())).resolve()
    # walk up to the repo root if we were launched from a subdir
    while not (REPO_ROOT / "sruth").exists() and REPO_ROOT != REPO_ROOT.parent:
        REPO_ROOT = REPO_ROOT.parent

    mo.md(
        f"""
        # Sources Load

        Federate the source-registry YAMLs under `sruth/` into one
        DuckDB at `registry.duckdb` (next to this notebook's quadrant root).

        **Repo root:** `{REPO_ROOT}`

        Each YAML list-of-dicts becomes rows in `sources_raw`:

        | column          | type    | meaning                                    |
        |-----------------|---------|--------------------------------------------|
        | `source_file`   | VARCHAR | path relative to repo root                 |
        | `family`        | VARCHAR | inferred registry family                   |
        | `top_key`       | VARCHAR | YAML top-level key (e.g. `sources`, `models`) |
        | `record_index`  | INT     | position in the list                       |
        | `record_json`   | VARCHAR | the full record, JSON-serialised           |
        | `record_sha256` | VARCHAR | SHA-256 of the JSON (for dedup)            |
        """
    )
    return REPO_ROOT, Path, hashlib, ibis, json, mo, pl, yaml


# ─────────────────────────────────────────────────────────────────────────────
# Cell 2 — path config (DuckDB output + which roots to scan)
# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(REPO_ROOT, mo):
    duckdb_path_text = mo.ui.text(
        value=str(REPO_ROOT / "registry.duckdb"),
        label="DuckDB output path",
        full_width=True,
    )

    roots_select = mo.ui.multiselect(
        options=[
            "sruth/oideachais",
            "sruth/meaisinfhoghlaim",
            "sruth/croilar",
            "sruth/crypteolas",
        ],
        value=[
            "sruth/oideachais",
            "sruth/meaisinfhoghlaim",
            "sruth/croilar",
            "sruth/crypteolas",
        ],
        label="Scan roots",
    )

    mo.vstack([duckdb_path_text, roots_select])
    return duckdb_path_text, roots_select


# ─────────────────────────────────────────────────────────────────────────────
# Cell 3 — discover YAMLs + infer family from path
# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(REPO_ROOT, Path, mo, pl, roots_select):
    # paths that are clearly NOT source registries — skip even if the user
    # toggles them on via the multiselect above
    DENY_PATTERNS = (
        # dependency / build caches
        ".venv/", "node_modules/", "__pycache__/", ".mypy_cache/",
        ".ruff_cache/", ".pytest_cache/", ".turbo/", "dist/", "build/",
        "site-packages/", ".pnpm-store/",
        # infra / compose / config
        "compose", "pangolin", "sidecar", "dagster.yaml", "workspace.yaml",
        "sqlmesh/", "config/pdf_extractors", "config/lightrag",
        "config/cache_config", "llama-swap-config", "ocr/config/",
        "game_showcase/project_data/", "apps/portal/", "agent_os/",
        "hono-api/", "dagster_assets/components/", "image-pipeline/",
        # app / framework internals
        "baml_src/", "baml_client/", ".baml/", "babel.config",
        "api/", "functions/", "convex/", "marimo/",
        "notebooks/", "dagster_defs/",
        # tests + generated fixtures
        "fixtures/", "tests/",
    )

    def infer_family(path: Path) -> str:
        s = str(path)
        if "oideachais/sources.yaml" in s:
            return "oideachais_yaml"
        if "oideachais/firecrawl_configs/" in s:
            return "oideachais_firecrawl"
        if "oideachais/dbt_project/" in s:
            return "oideachais_dbt"
        if "oideachais/samplaí/" in s:
            return "oideachais_samplai"
        if "meaisinfhoghlaim/catalog/models" in s:
            return "meaisinfhoghlaim_model"
        if "meaisinfhoghlaim/catalog/sources" in s:
            return "meaisinfhoghlaim_source"
        if "meaisinfhoghlaim/language/cognates" in s:
            return "cognates"
        if "meaisinfhoghlaim/language/" in s:
            return "celtic_sample"
        if "croilar/config/sources" in s:
            return "croilar_stream"
        if "crypteolas/apps/crypteolas_demo/foinse/sources" in s:
            return "crypteolas_source"
        if "crypteolas/apps/crypteolas_demo/foinse/databases" in s:
            return "crypteolas_database"
        if "crypteolas/config/" in s:
            return "crypteolas_config"
        if "crypteolas/repos.yaml" in s:
            return "crypteolas_repo"
        return "other"

    files: list[dict] = []
    for root_rel in roots_select.value:
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue
        for pattern in ("*.yaml", "*.yml"):
            for p in root.rglob(pattern):
                sp = str(p)
                if any(deny in sp for deny in DENY_PATTERNS):
                    continue
                files.append(
                    {
                        "path": str(p.relative_to(REPO_ROOT)),
                        "family": infer_family(p),
                        "size_kb": round(p.stat().st_size / 1024, 1),
                    }
                )

    if files:
        discovered = pl.DataFrame(files).sort("family", "path")
    else:
        discovered = pl.DataFrame(
            schema={"path": pl.Utf8, "family": pl.Utf8, "size_kb": pl.Float64}
        )

    mo.vstack(
        [
            mo.md(
                f"**{len(files)} YAML files** across **{discovered['family'].n_unique()} families**"
            ),
            mo.ui.table(discovered, page_size=20),
        ]
    )
    return DENY_PATTERNS, discovered, infer_family


# ─────────────────────────────────────────────────────────────────────────────
# Cell 4 — parse → explode into raw rows (recursive walk for nested YAML)
# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(REPO_ROOT, Path, discovered, hashlib, json, pl, yaml):
    discovered_records = discovered.to_dicts()
    parse_errors: list[dict] = []

    def parse_yaml_to_rows(path: Path) -> list[dict]:
        """Recursively walk a YAML file and emit one row per list-of-dicts
        at any depth. `top_key` becomes the dotted path of keys leading to
        the list (e.g. `streams.music.sources`). Surfaces YAML parse errors
        via the cell-level `parse_errors` list (not raised — other files
        should still load).
        """
        rel = str(path.relative_to(REPO_ROOT))
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            parse_errors.append({"path": rel, "error": str(exc).splitlines()[0]})
            return []
        if not isinstance(raw, dict):
            return []

        family = next(
            (f["family"] for f in discovered_records if f["path"] == rel),
            "other",
        )
        out: list[dict] = []

        def _emit(top_key: str, record_index: int, record: dict) -> None:
            rec_json = json.dumps(record, sort_keys=True, ensure_ascii=False)
            out.append(
                {
                    "source_file": rel,
                    "family": family,
                    "top_key": top_key,
                    "record_index": record_index,
                    "record_json": rec_json,
                    "record_sha256": hashlib.sha256(rec_json.encode()).hexdigest(),
                }
            )

        # closure factory — avoid recursive self-reference by name, since
        # marimo's AST transform renames `_walk` to `_cell_xxx_walk`.
        def _make_walk(emit):
            def walk(value, key_path, depth=0):
                if depth > 5:
                    return
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    for i, rec in enumerate(value):
                        emit(".".join(key_path), i, rec)
                    return
                if isinstance(value, dict):
                    for k, v in value.items():
                        walk(v, key_path + [str(k)], depth + 1)
            return walk

        walk = _make_walk(_emit)
        walk(raw, [], 0)
        return out

    rows: list[dict] = []
    for entry in discovered_records:
        rows.extend(parse_yaml_to_rows(REPO_ROOT / entry["path"]))

    # dedup by record_sha256 (the Celtic samples are duplicated between
    # sruth/meaisinfhoghlaim/language/ and sruth/oideachais/samplaí/)
    seen: set[str] = set()
    deduped: list[dict] = []
    for r in rows:
        if r["record_sha256"] in seen:
            continue
        seen.add(r["record_sha256"])
        deduped.append(r)

    df = pl.DataFrame(
        deduped,
        schema={
            "source_file": pl.Utf8,
            "family": pl.Utf8,
            "top_key": pl.Utf8,
            "record_index": pl.Int64,
            "record_json": pl.Utf8,
            "record_sha256": pl.Utf8,
        },
    )

    by_family = (
        df.group_by("family")
        .agg(pl.len().alias("rows"))
        .sort("rows", descending=True)
    )

    summary_md = f"**{len(df):,} unique records** (deduped from {len(rows):,} raw)"
    if parse_errors:
        summary_md += (
            f"\n\n⚠️ **{len(parse_errors)} YAML file(s) failed to parse** "
            "(skipped — see table below). Fix the upstream YAMLs and re-run."
        )

    summary_widgets = [mo.md(summary_md), mo.ui.table(by_family)]
    if parse_errors:
        summary_widgets.append(mo.md("### YAML parse errors"))
        summary_widgets.append(
            mo.ui.table(pl.DataFrame(parse_errors), page_size=10)
        )
    summary_widgets += [
        mo.md("### First 20 records"),
        mo.ui.table(df.head(20), page_size=20),
    ]
    mo.vstack(summary_widgets)
    return (
        by_family,
        deduped,
        df,
        parse_errors,
        parse_yaml_to_rows,
        rows,
        seen,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Cell 5 — connect to DuckDB via ibis
# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(duckdb_path_text, ibis, mo):
    duckdb_path = duckdb_path_text.value
    con = ibis.duckdb.connect(duckdb_path)
    existing = con.list_tables()
    mo.md(
        f"Connected to `{duckdb_path}`. "
        f"Existing tables: **{existing if existing else '(none — fresh)'}**."
    )
    return con, duckdb_path, existing


# ─────────────────────────────────────────────────────────────────────────────
# Cell 6 — overwrite sources_raw
# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(con, df, mo):
    con.create_table("sources_raw", df, overwrite=True)
    rows_in_db = con.table("sources_raw").count().execute()
    mo.md(
        f"✅ Wrote `sources_raw`: **{rows_in_db:,} rows**."
        " Prune / edit downstream — re-running this notebook will overwrite it."
    )
    return (rows_in_db,)


# ─────────────────────────────────────────────────────────────────────────────
# Cell 7 — three sanity queries
# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(con, mo, pl):
    # (a) rows per family
    by_family_q = (
        con.sql(
            """
            SELECT family, COUNT(*) AS rows
            FROM sources_raw
            GROUP BY family
            ORDER BY rows DESC
            """
        )
        .execute()
    )

    # (b) 10 largest records by JSON length
    largest_q = (
        con.sql(
            """
            SELECT source_file, family, top_key, record_index,
                   LENGTH(record_json) AS json_bytes
            FROM sources_raw
            ORDER BY json_bytes DESC
            LIMIT 10
            """
        )
        .execute()
    )

    # (c) records missing the common keys (id / name / urls)
    missing_keys_q = (
        con.sql(
            """
            SELECT family,
                   SUM(CASE WHEN json_extract_string(record_json, '$.id')    IS NULL THEN 1 ELSE 0 END) AS missing_id,
                   SUM(CASE WHEN json_extract_string(record_json, '$.name')  IS NULL THEN 1 ELSE 0 END) AS missing_name,
                   SUM(CASE WHEN json_extract(record_json, '$.urls')        IS NULL THEN 1 ELSE 0 END) AS missing_urls,
                   COUNT(*) AS total
            FROM sources_raw
            GROUP BY family
            ORDER BY family
            """
        )
        .execute()
    )

    mo.vstack(
        [
            mo.md("### (a) Rows per family"),
            mo.ui.table(pl.from_pandas(by_family_q)),
            mo.md("### (b) 10 largest records"),
            mo.ui.table(pl.from_pandas(largest_q)),
            mo.md("### (c) Missing-key report per family"),
            mo.ui.table(pl.from_pandas(missing_keys_q)),
        ]
    )
    return by_family_q, largest_q, missing_keys_q


if __name__ == "__main__":
    app.run()
