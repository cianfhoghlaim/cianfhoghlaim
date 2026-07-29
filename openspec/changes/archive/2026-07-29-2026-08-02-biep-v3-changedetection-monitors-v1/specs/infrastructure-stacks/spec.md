## MODIFIED Requirements

### Requirement: 7 new ChangeDetection.io monitors for BIEP v3 jurisdictions

The system SHALL provide 7 new ChangeDetection.io monitor YAML files
under `bonnegar/stacks/changedetection/monitors/` covering the 7 BIEP v3
jurisdictions that don't currently have a monitor (Ireland / Scotland /
Wales / Northern Ireland / Jersey / Guernsey / Isle of Man).

#### Scenario: 10 ChangeDetection.io monitors exist

- **WHEN** `bun run changedetection:list` runs
- **THEN** exactly **10** monitors SHALL be listed
  (3 existing: aqa + edexcel + ocr + 7 new: ncca + sqa + wjec + ccea + jersey + guernsey + iom)
- **AND** every new monitor SHALL point at the BIEP umbrella webhook
  `http://dagster-webhook:8080/webhooks/biep_change_detection`

#### Scenario: 7 new monitors follow the 6-label GOLD_STANDARD contract

- **WHEN** any of the 7 new monitor YAMLs is read
- **THEN** the file SHALL contain the 6 GOLD_STANDARD fields:
  `name`, `url`, `css_selector`, `xpath`, `timeout`, `interval`,
  `fetch_backend`, `webhook_url`, `notification_format`, `watched_pages[]`,
  `alert`
- **AND** the `webhook_url` SHALL be the BIEP umbrella webhook
  `http://dagster-webhook:8080/webhooks/biep_change_detection`