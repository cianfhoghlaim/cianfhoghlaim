# olake

## Purpose for the Cianfhoghlaim project

Olake is an open-source Change Data Capture (CDC) tool that replicates data from databases (MongoDB, PostgreSQL, MySQL) to data lake formats (Iceberg, Parquet) at high throughput. It is designed as a cost-effective alternative to Fivetran and Airbyte for database-to-lake replication, achieving 300K+ rows per second.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the personal/utility fleet. Reproducible via the IaC bootstrap; no cianfhoghlaim project dependencies.

## Cross-references

- **Ops**: `bonneagar/stacks/olake/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:personal-utility`
- - **Pangolin**: `https://olake.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:bunchloch`
- `tier:personal-utility`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
