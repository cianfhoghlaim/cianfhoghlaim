## Why

The lakehouse unified data plane
(`2026-08-15-lakehouse-unified-data-plane-v1`) and bonneagar infra
remediation v3 (`2026-08-13-bonneagar-infra-remediation-v3`) changes
share the IaC + storage dependency: the lakehouse landing zones
(Iceberg + Lakekeeper + Postgres + Garage S3) depend on the
remediation change having cleaned up the prior bad-state stacks.
Bundling them records the dependency.

## What Changes

- Cross-batch lakehouse + IaC remediation contract: remediation
  ships first, then lakehouse activation.
- Records the dependency order in `design.md`.

## Capabilities

(none added; pure bundling)

## Impact

- **Affected changes**: 2 bundled
- **Affected code**: none — this change is metadata-only