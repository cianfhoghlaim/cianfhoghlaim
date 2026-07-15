## ADDED Requirements

### Requirement: ChangeDetection.io for England awarding bodies

The system SHALL provide 3 ChangeDetection.io monitors in
`bonneagar/stacks/changedetection/monitors/`:

- `aqa_monitor.yaml` — AQA spec pages
  (`https://www.aqa.org.uk/subjects/<subject>/specifications`)
- `ocr_monitor.yaml` — OCR spec pages
  (`https://www.ocr.org.uk/qualifications/<subject>/`)
- `edexcel_monitor.yaml` — Edexcel spec pages
  (`https://qualifications.pearson.com/en/qualifications/edexcel-<subject>.html`)

Each monitor MUST:

- Use `web_scraping` mode + CSS selector for the spec version + PDF link
- Trigger a webhook to
  `http://dagster-webhook:8080/webhooks/england_change_detection`
- Be uploaded to the dev ChangeDetection.io vault via the ChangeDetection.io
  REST API

The system SHALL also provide 1 DuckLake audit table
`oideachais.education.british_isles.england.changes` with the 11 columns
declared in the proposal.

#### Scenario: AQA maths GCSE spec change detected

- **GIVEN** AQA publishes a new version of the GCSE Mathematics specification
- **WHEN** the ChangeDetection.io `aqa_monitor.yaml` detects the change
- **THEN** the monitor posts a webhook payload to
  `http://dagster-webhook:8080/webhooks/england_change_detection`
- **AND** the Dagster sensor `england_change_detection_sensor` fires
- **AND** the sensor triggers the `england_england_re_extraction_job`
  for `(board=aqa, subject=mathematics, qualification_level=gcse)`
- **AND** a new row lands in
  `oideachais.education.british_isles.england.changes` with
  `board='aqa'`, `subject='mathematics'`, `qualification_level='gcse'`
- **AND** a Slack alert posts to `#kcg-biep-v2`
- **AND** an email alert posts to `kcg-curriculum@cianfhoghlaim.ie`
- **AND** the re-extraction runs the full Change 3 ensemble (BAML +
  Unstract + qwen3-vl-8b + gemma-4-26B-A4B + RAGAS vote)
