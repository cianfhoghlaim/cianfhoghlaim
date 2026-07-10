## ADDED Requirements

### Requirement: All procedures have `server_id` by 2026-07-13

The system SHALL require every Komodo procedure TOML under `komodo/procedures/` to declare a top-level `server_id` field with one of the values:
- `"bunchloch"` — for procedures that deploy + verify resources on the `bunchloch` host
- `"arm1-oci"` — for procedures that deploy + verify resources on the `arm1-oci` host

Procedures added or modified after **2026-07-13** MUST include `server_id = "bunchloch"` or `server_id = "arm1-oci"`. The legacy back-compat path (procedures without `server_id` showing in both hosts' UIs) is **deprecated and SHALL be removed by 2026-08-15**: at that date, any procedure without `server_id` SHALL emit a hard error from `openspec validate` (not just a warning) and SHALL be removed from both UIs.

The convention is documented in `komodo/procedures/server_id_legend.md` (the legend doc added by the `2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow` change).

#### Scenario: New procedure has `server_id`

- **WHEN** a new procedure is added to `komodo/procedures/` after 2026-07-13
- **THEN** the procedure SHALL include `server_id = "bunchloch"` or `server_id = "arm1-oci"` at the top of the `[[procedure.config]]` (or `[[procedure]]`) block
- **AND** `openspec validate <change-id> --strict` SHALL emit an error if the field is missing
- **AND** the procedure SHALL appear in only the matching host's `km` UI

#### Scenario: Backfill of legacy procedures

- **WHEN** a procedure is added to `komodo/procedures/` without a `server_id` field between **2026-07-13** and **2026-08-15**
- **THEN** the procedure SHALL appear in BOTH hosts' UIs (back-compat path)
- **AND** Komodo Core SHALL log a deprecation warning: `WARN: procedure '<name>' has no server_id field; defaulting to both hosts. Add server_id = 'bunchloch' or 'arm1-oci'.`

#### Scenario: 2026-08-15 hard cutover

- **WHEN** the 2026-08-15 cutover date passes
- **THEN** any procedure without a `server_id` field SHALL be hard-rejected by `openspec validate` (not just a warning)
- **AND** the back-compat path SHALL be removed from Komodo Core (procedures without `server_id` are invisible in both UIs)
- **AND** the only valid procedure files are ones with `server_id = "bunchloch"` or `server_id = "arm1-oci"`
