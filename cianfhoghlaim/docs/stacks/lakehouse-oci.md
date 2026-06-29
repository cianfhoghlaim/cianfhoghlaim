# lakehouse-oci

## Purpose for the Cianfhoghlaim project

The OCI variant of the lakehouse stack, designed for the production deployment on `arm1-oci` (Oracle Cloud Ampere A1). Unlike the standard lakehouse which uses PlanetScale, this stack runs a standalone PostgreSQL instance alongside Lakekeeper, providing fully self-contained catalog metadata on the ARM64 control plane node.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the personal/utility fleet. Reproducible via the IaC bootstrap; no cianfhoghlaim project dependencies.

## Cross-references

- **Ops**: `bonneagar/stacks/lakehouse-oci/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:personal-utility`
- - **Pangolin**: not exposed (internal-only service)

## Tags

- `host:bunchloch`
- `tier:personal-utility`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
