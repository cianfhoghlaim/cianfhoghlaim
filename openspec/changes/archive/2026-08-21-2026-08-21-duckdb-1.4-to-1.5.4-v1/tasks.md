# Tasks — 2026-08-21-duckdb-1.4-to-1.5.4-v1

## 1. Bump

- [ ] 1.1 Edit `pyproject.toml`: `duckdb>=1.4` → `duckdb>=1.5.4,<1.5.5`. Run `uv sync`. Verify `uv pip show duckdb | grep Version` prints `1.5.4`.

## 2. Verify

- [ ] 2.1 Re-run the BIEP v3 Ireland LC pipeline (now on DLT 1.30 + DuckDB 1.5.4) against the 80 PDFs. Assert 80 rows + sub-second extraction.
- [ ] 2.2 Run `mise run data:status` and verify all sections OK.
- [ ] 2.3 Run a local DuckDB query (e.g. `duckdb -c "SELECT 1.5.4 AS duckdb_version;"`) and verify the binary accepts queries.

## 3. openspec

- [ ] 3.1 `openspec validate 2026-08-21-duckdb-1.4-to-1.5.4-v1 --strict`.
- [ ] 3.2 `openspec archive 2026-08-21-duckdb-1.4-to-1.5.4-v1 --yes`.

## 4. Documentation

- [ ] 4.1 Update `.agents/skills/duckdb/SKILL.md` with the 1.5.4 pin note.
