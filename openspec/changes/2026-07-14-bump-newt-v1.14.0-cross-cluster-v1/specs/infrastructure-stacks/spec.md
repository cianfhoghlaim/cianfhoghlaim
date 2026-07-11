# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: newt image is pinned to v1.14.0 + SHA digest across all clusters

The system SHALL pin the fossorial `newt` Pangolin client image to **v1.14.0** with a **SHA256 digest** (not a mutable tag, not `:latest`) in every cluster that runs newt (bunchloch operator-laptop + arm1-oci control-plane).

The canonical image pin lives at `bonneagar/stacks/newt/IMAGE` (a single-file `NEWT_VERSION` + `NEWT_IMAGE` + `NEWT_SHA` constants). All other compose files reference these constants via the pinned image reference.

When upgrading newt:
1. Bump `NEWT_VERSION` + `NEWT_SHA` in `stacks/newt/IMAGE`
2. Update the 2 image references in `stacks/newt/docker-compose.yaml` + `stacks/pangolin/newt.yaml`
3. Open an openspec change documenting the bump (e.g. `2026-07-14-bump-newt-v1.14.0-cross-cluster-v1`)
4. Validate + commit + push + archive

#### Scenario: newt is pinned at v1.14.0

- **GIVEN** `stacks/newt/IMAGE` declares `NEWT_VERSION=1.14.0` + `NEWT_SHA=60c78391...`
- **AND** `stacks/newt/docker-compose.yaml` + `stacks/pangolin/newt.yaml` reference the same SHA
- **WHEN** `bun run stack-doctor` runs across the repo
- **THEN** no newt-related `:latest` warnings fire
- **AND** the newt image-pin check passes

#### Scenario: newt version mismatches across clusters

- **WHEN** `docker exec bunchloch-newt -- newt --version` returns `1.14.0`
- **AND** `docker exec pangolin-newt -- newt --version` returns `1.13.0`
- **THEN** the deploy-newt-bunchloch-v2 + deploy-pangolin-newt-arm1-oci procedures
  Stage 4 (health-checks) emit a MISMATCH error
- **AND** the operator is blocked from proceeding until both newt containers are on the same version

#### Scenario: IMAGE rotation is atomic

- **WHEN** the IMAGE file is updated to v1.15.0 (e.g. new SHA `abc...123`)
- **THEN** the 2 compose files SHALL reference the new SHA in the same commit
- **AND** the openspec change documents the upgrade
- **AND** the rotation is rolled out via the cross-cutting prereq order
  (pangolin-first → komodo-core → infisical-first → locket-deploy →
  deploy-pangolin-newt-arm1-oci → deploy-newt-bunchloch-v2)
