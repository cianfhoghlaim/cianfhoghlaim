# Cross-repo-sync: 2026-08-07-biep-v3-hardening-v1

## Affected repos

- `cianfhoghlaim` (this repo) — DLT + BAML + CocoIndex + Dagster code
- `bonnegar` (separate repo) — IaC stack catalogue + canonical 3 clients

## Commit plan

### Commit 1 (cianfhoghlaim repo)

```
1. Add baml_src/clients_biep_v3.py
2. Update 67+ active BAML functions to use the 3 canonical clients
3. Add dlt/british_isles/_cross/jurisdiction_pipeline_base.py
4. Refactor 4 jurisdiction pipeline files to use the base class
5. Add dlt/common/ducklake_pool.py + dlt/common/iceberg_options.py
6. Update dlt/common/destinations_cianfhoghlaim.py (mode/tenant/iceberg)
7. Add dlt/common/motherduck_snapshots.py
8. Create 3 new sensors + 1 S3 sensor
9. Rewrite .github/workflows/baml-test.yaml (full CI gate)
```

### Commit 2 (bonneagar repo)

```
1. Update stacks/lakehouse/compose.yaml (use BIEPV3Extract client config)
2. Update komodo/procedures/deploy-{lakehouse,cognee,motherduck}.toml
```

## Push targets

- `origin/openspec/2026-07-25-refactor-batch-v1`
