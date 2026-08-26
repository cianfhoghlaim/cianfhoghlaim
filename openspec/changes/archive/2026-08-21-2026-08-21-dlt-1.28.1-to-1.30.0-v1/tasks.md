# Tasks — 2026-08-21-dlt-1.28.1-to-1.30.0-v1

## 1. Bump

- [ ] 1.1 Edit `pyproject.toml`: `dlt[duckdb,motherduck,filesystem]>=1.28.1` → `>=1.30.0,<2.0.0`. Run `uv sync`. Verify `uv pip show dlt | grep Version` prints `1.30.x`.

## 2. Migrate `replace` → `refresh`

- [ ] 2.1 List every `write_disposition="replace"` call site (already inventoried; 22 files). Migrate them to `refresh` only where the semantics fit (full-table refresh; not for incremental loads).
- [ ] 2.2 Skip the 6 jurisdiction pipelines (they're using `merge` already per DLT 1.25+ conventions).
- [ ] 2.3 Re-test the BIEP v3 Ireland LC pipeline end-to-end to assert no behavior regression.

## 3. Validate

- [ ] 3.1 Run `mise run data:status`.
- [ ] 3.2 `openspec validate 2026-08-21-dlt-1.28.1-to-1.30.0-v1 --strict`.
- [ ] 3.3 `openspec archive 2026-08-21-dlt-1.28.1-to-1.30.0-v1 --yes`.

## 4. Document

- [ ] 4.1 Update `meaisinfhoghlaim/README.md` (if any) with the new DLT version.
- [ ] 4.2 Update `.agents/skills/dlt/SKILL.md` if it mentions a specific version pin.
