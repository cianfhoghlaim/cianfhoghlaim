## ADDED Requirements

### Requirement: cocoindex-v1-0-14-tasks

The `data:cocoindex:*` task namespace SHALL expose CocoIndex v1.0.14+
features via 2 new tasks. Per the
`2026-08-23-data-cocoindex-v1-0-14-features-v1` change.

#### Scenario: data:cocoindex:apps:list returns ≥ 7 apps

- **WHEN** `mise run data:cocoindex:apps:list` runs
- **THEN** it MUST emit a list of all BIEP v1 Apps
- **AND** the list MUST contain ≥ 7 apps (6 LC subjects + government_circulars)

#### Scenario: data:cocoindex:flows:status exits 0 for a valid app

- **WHEN** `mise run data:cocoindex:flows:status -- <app_name>` runs
- **AND** the app exists
- **THEN** the command MUST exit 0
- **AND** the output MUST include the app's last-run timestamp + freshness status