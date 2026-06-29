# lakehouse

## Purpose for the Cianfhoghlaim project

The lakehouse stack integrates Garage S3-compatible storage, Lakekeeper Iceberg REST Catalog, a Lance Namespace sidecar, the Nimtable Iceberg catalog UI, the Olake CDC engine, and the LanceDB table viewer into a single deployable unit. It is the primary data plane for the Kings' College Galway project — every curriculum Parquet file, every vector index, and every generated study asset passes through this stack.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the lakehouse data plane (Dagster + DuckLake + Lance). State persists to Garage S3; embeddings to LanceDB; code lives in cianfhoghlaim/ as Python modules. Reproducible via the IaC bootstrap.

## Cross-references

- **Ops**: `bonneagar/stacks/lakehouse/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:data-engineering`
- - **Pangolin**: `https://s3.lakehouse.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:bunchloch`
- `tier:data-engineering`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
