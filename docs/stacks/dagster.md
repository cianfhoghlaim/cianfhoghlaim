# dagster

## Purpose for the Cianfhoghlaim project

![Dagster Documentation](https://storage.googleapis.com/firecrawl-scrape-media/screenshot-1a114b7d-86ea-487c-abc0-7588bca67989.png)

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the lakehouse data plane (Dagster + DuckLake + Lance). State persists to Garage S3; embeddings to LanceDB; code lives in cianfhoghlaim/ as Python modules. Reproducible via the IaC bootstrap.

## Cross-references

- **Ops**: `bonneagar/stacks/dagster/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:data-engineering`
- - **Pangolin**: `https://dagster.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:bunchloch`
- `tier:data-engineering`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
