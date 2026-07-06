# Tasks: 2026-07-06-wire-biep-notebooks-to-lakehouse

## 1. Update lakehouse_pipeline.py (ibis-first)

- [ ] 1.1 Read the full 362-line file
- [ ] 1.2 Replace `import duckdb` with `import ibis` (the canonical
      KCG entrypoint per `.agents/skills/ibis/SKILL.md`)
- [ ] 1.3 In the `environment == "local"` branch: replace
      `CONFIG["ducklake_conn"]` / raw queries with
      `conn = ibis.duckdb.connect("ducklake:postgres:host=lakehouse-postgres port=5432 user=lakekeeper password=… dbname=ducklake_oideachais")`
- [ ] 1.4 In the `environment == "remote"` branch: replace PlanetScale
      rows with `conn = ibis.duckdb.connect("md:oideachais")` (per the
      motherduck skill — required because MotherDuck federates via
      DuckDB)
- [ ] 1.5 Replace the Lance section with
      `lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")`
      per `.agents/skills/lancedb/SKILL.md`; replace raw `lance_scan()`
      calls with `lance.table("oideachais_litellm_models").head(5).execute()`
      style ibis expressions
- [ ] 1.6 Regenerate the marimo `__generated_with` if a local `marimo`
      CLI is available
- [ ] 1.7 Add a smoke cell that asserts:
      `ibis.duckdb.connect("md:oideachais").raw_sql("SELECT 1").fetchone() == (1,)`
      AND
      `ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182").list_tables()`
      returns the expected 6 BIEP subject tables

## 2. Wire the 6 BIEP notebooks (ibis-first)

- [ ] 2.1 Verify `2026-07-06-british-isles-education-pipeline-v1`
      has archived (else defer this PR until it does)
- [ ] 2.2 For each subject (mathematics, chemistry, geography, gaeilge,
      english, computer-science): confirm the marimo notebook exists
      at `cianfhoghlaim/notebooks/biep/<subject>.py`
- [ ] 2.3 For each notebook, replace ANY raw `duckdb.connect(...)`
      with `conn = ibis.duckdb.connect(...)` — local OR `md:oideachais`
- [ ] 2.4 For each notebook, replace ANY raw `lancedb.connect(...)`
      with
      `lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")`
- [ ] 2.5 For each notebook, set the default session state to:
      - `LANCEDB_URI=rest://lakehouse-lance-namespace:8182`
      - `DUCKLAKE_DB=ducklake_<subject>`
      - `IBIS_BACKEND=duckdb` (the canonical KCG choice per the
        `ibis` skill frontmatter)
- [ ] 2.6 Add a top-of-notebook import block:
      ```python
      import ibis
      import marimo as mo
      @app.setup
      def _setup():
          conn  = ibis.duckdb.connect(os.environ["DUCKDB_CONNECTION_STRING"])
          lance = ibis.lancedb.connect(os.environ["LANCEDB_URI"])
          return conn, lance
      ```
- [ ] 2.7 Each cell SHALL prefer ibis expressions over raw SQL
      (e.g.
      `conn.table("ducklake_oideachais").filter(_.subject == "mathematics").count().execute()`)

## 3. Verify per-notebook

For each `marimo run cianfhoghlaim/notebooks/biep/<subject>.py`:
- [ ] First data cell: `conn.raw_sql("SELECT 1").fetchone()` returns
      `(1,)` within 2 seconds
- [ ] First Lance cell: `lance.list_tables()` lists
      `oideachais.lc.<subject>.<level>_<lang>` tables
- [ ] The marimo reactive graph resolves without "Pending" cells after
      5 seconds

## 4. Run lakehouse_pipeline.py end-to-end

- [ ] 4.1 `marimo run bonneagar/stacks/lakehouse/notebooks/lakehouse_pipeline.py`
- [ ] 4.2 Capture the cell-by-cell output to
      `.scratch/lakehouse-pipeline-2026-07-06.txt`
- [ ] 4.3 Verify the local-mode DuckDB query
      (`SELECT 1 FROM lakehouse.litellm.users LIMIT 1`) returns a table
      (even if 0 rows)
- [ ] 4.4 Verify the LANCEDB_URI lance_search() returns the
      `oideachais_litellm_models` table (0 rows is OK)

## 5. Cross-stack verification

- [ ] 5.1 `grep -r "duckdb.connect(" cianfhoghlaim/notebooks/biep/
      bonneagar/stacks/lakehouse/notebooks/` — zero matches
- [ ] 5.2 `grep -r "import ibis" cianfhoghlaim/notebooks/biep/
      bonneagar/stacks/lakehouse/notebooks/` — ≥ 7 matches (1 + 6)
- [ ] 5.3 `openspec validate 2026-07-06-wire-biep-notebooks-to-lakehouse --strict`
- [ ] 5.4 `mise run lint:skills` — confirm no regression