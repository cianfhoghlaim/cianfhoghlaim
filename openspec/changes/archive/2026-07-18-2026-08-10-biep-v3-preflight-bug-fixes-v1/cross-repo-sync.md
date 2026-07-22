# Cross-repo-sync: 2026-08-10-biep-v3-preflight-bug-fixes-v1

Per the openspec AGENTS.md convention, this change touches only the
`cianfhoghlaim` repo (no IaC or Leabharlann changes).

## Affected repos

- `cianfhoghlaim` (this repo) — DLT + BAML + MotherDuck + Dagster code

## Commit plan

### Commit 1 (cianfhoghlaim) — preflight fixes

```
1. Edit motherduck/flights/config.yaml (YAML indent fix L113-129)
2. Edit baml_src/clients_biep_v3.py (Strong model → gemma-3-27b-it)
3. Edit dlt/common/motherduck_snapshots.py (httpx impl)
4. Edit dlt/british_isles/_cross/registry_loader.py (docstring fix + assert)
5. Edit dlt/british_isles/_cross/jurisdiction_pipeline_base.py (add subject_to_row + build_pipeline)
6. Edit 4 dlt/british_isles/.../education/*_jurisdiction_pipeline.py (inherit base)
7. Add httpx + tenacity to pyproject.toml
8. Run uv sync + baml-cli generate
```

## Order of operations

1. Commit lands on `openspec/2026-07-25-refactor-batch-v1` branch.
2. `openspec validate 2026-08-10-biep-v3-preflight-bug-fixes-v1 --strict` passes.
3. Push to `origin/openspec/2026-07-25-refactor-batch-v1`.
4. Archive: `openspec archive 2026-08-10-biep-v3-preflight-bug-fixes-v1 --yes`.

## Push targets

- `origin/openspec/2026-07-25-refactor-batch-v1` (the wave branch)