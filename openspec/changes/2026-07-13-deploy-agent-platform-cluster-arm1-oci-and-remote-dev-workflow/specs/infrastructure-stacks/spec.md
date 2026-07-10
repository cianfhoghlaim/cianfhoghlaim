## ADDED Requirements

### Requirement: Procedure `server_id` field for cross-host dispatch

The system SHALL include a top-level `server_id` field in every Komodo procedure TOML under `komodo/procedures/`. The `server_id` value SHALL be one of:
- `"bunchloch"` — for procedures that deploy + verify resources on the `bunchloch` host (this Mac, the workload + dev host)
- `"arm1-oci"` — for procedures that deploy + verify resources on the `arm1-oci` host (Oracle Cloud Free Tier, Frankfurt, the control-plane host)

Each Komodo Core host (bunchloch + arm1-oci) SHALL filter the procedures it shows in its UI + REST API to those whose `server_id` matches that host (or to procedures with no `server_id` field, for back-compat). The `arm1-oci.toml` + `bunchloch.toml` + `cross-cutting.toml` resource-syncs SHALL all include the `procedures/*.toml` glob; the per-host filtering happens at the Komodo Core level based on the `server_id` field.

Procedures with no `server_id` field SHALL appear in BOTH hosts (back-compat for v1 deploys that pre-date this change) and SHALL emit a deprecation warning in the Komodo logs.

The convention is documented in `komodo/procedures/server_id_legend.md`.

#### Scenario: Bunchloch UI shows only bunchloch procedures

- **WHEN** the operator visits `https://komodo.cianfhoghlaim.ie/procedures` on bunchloch
- **THEN** the procedures list SHALL include only procedures with `server_id = "bunchloch"` (plus a small back-compat section for procedures without the field)
- **AND** arm1-oci-specific procedures (e.g. `deploy-openclaw-arm1-oci`) SHALL NOT appear in this list

#### Scenario: arm1-oci UI shows only arm1-oci procedures

- **WHEN** the operator visits `https://komodo.cianfhoghlaim.ie/procedures` on arm1-oci
- **THEN** the procedures list SHALL include only procedures with `server_id = "arm1-oci"` (plus the back-compat section)
- **AND** bunchloch-specific procedures (e.g. `deploy-lakehouse-bunchloch`) SHALL NOT appear in this list

#### Scenario: Back-compat — missing server_id

- **WHEN** a procedure TOML under `komodo/procedures/` has no `server_id` field
- **THEN** the procedure SHALL appear in BOTH bunchloch and arm1-oci UIs
- **AND** Komodo Core SHALL log a deprecation warning: `WARN: procedure '<name>' has no server_id field; defaulting to both hosts. Add server_id = 'bunchloch' or 'arm1-oci'.`

#### Scenario: New procedure must declare server_id

- **WHEN** a new procedure TOML is added under `komodo/procedures/`
- **THEN** the procedure SHALL include a `server_id` field at the top
- **AND** `openspec validate` SHALL emit an error if the field is absent (per the validation gate)

### Requirement: Komodo `Build` resource for code-owned images

The system SHALL provide a Komodo `[[build]]` resource for every code-owned image (an image the repo builds from a local Dockerfile, as opposed to pulling from an upstream registry). Every `komodo/builds/<name>.toml` file SHALL declare:
- `repo` + `branch` — the source repo + branch to pull from
- `build_path` — the path to the Dockerfile relative to the repo root
- `image_name` + `image_tag` — the canonical output image + tag (e.g. `ghcr.io/cianfhoghlaim/openchamber:1.14.1-arm1`)
- The `komodo/resource-syncs/*.toml` files SHALL include the `komodo/builds/*.toml` glob so the builds are registered on each host's Komodo Core

Code-owned images SHIP with full Dockerfile provenance (the Dockerfile is committed in the repo under `bonneagar/stacks/<name>/Dockerfile.<name>`) and are tagged with the `<arch>-arm` suffix to distinguish them from the upstream private images.

#### Scenario: Build resource is registered on arm1-oci

- **WHEN** the `arm1-oci` resource-sync's 60s pull cycle runs
- **THEN** the 3 new `komodo/builds/{openchamber-arm1-oci, openclaw-arm1-oci, hermes-arm1-oci}.toml` files SHALL be registered on arm1-oci's Komodo Core
- **AND** `km run build <name>` on arm1-oci SHALL build the corresponding image and push it to the `ghcr.io/cianfhoghlaim/*` registry

#### Scenario: Build replaces the private upstream image

- **WHEN** the openchamber-arm1-oci build completes
- **THEN** the locally-built `ghcr.io/cianfhoghlaim/openchamber:1.14.1-arm1` image SHALL be available on arm1-oci
- **AND** the `komodo/stacks/openchamber-arm1-oci.toml` stack SHALL reference this local image (not the private upstream `ghcr.io/openchamber/openchamber:1.0.0`)
- **AND** `bun run validate-stacks` SHALL hard-fail if the stack still references the private upstream image tag
