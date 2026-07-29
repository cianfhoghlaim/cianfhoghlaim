## ADDED Requirements

### Requirement: BIEP v3 2-axis scope/year partition

The Dagster 5-layer component architecture SHALL provide a BIEP v3
2-axis `MultiPartitionsDefinition` for the BIEP v3 jurisdiction pipeline
assets (defined in `orchestration/partitions_v2.py:39-64` as
`biiep_v3_scope_year_partition`):

```text
{
  "scope": DynamicPartitionsDefinition(name="cianhoghlaim_scope"),
  "year": StaticPartitionsDefinition(<2017-2027 + "undated">),
}
```

The `scope` axis uses a `DynamicPartitionsDefinition` because the 428+
cohort keys
(`<jurisdiction>__<stage>__<subject_slug>__<board>__<qualification_level>__<language>`)
are seeded at runtime by the British Isles Subject Registry. The `year`
axis is static (2017–2027 + "undated") because the curriculum refresh
cadence is on a known annual cycle.

The `CelticIngestionComponent` SHALL use this partition for all BIEP v3
jurisdiction pipeline assets (Ireland LC + JC + England A-Level + GCSE).
The `CelticMaterialsComponent` SHALL propagate the partition to all
downstream L2 extraction / embedding / audit assets.

The helper `scope_partition_key(jurisdiction, stage, subject_slug, board,
qualification_level, language)` SHALL build the canonical 6-token shape:

```text
<jurisdiction>__<stage>__<subject_slug>__<board>__<qualification_level>__<language>
```

(e.g. `ireland__leaving_cycle__mathematics__na__higher__en`).

#### Scenario: An Ireland LC Mathematics Higher English 2024 asset lands in the right partition

- **WHEN** the `ireland_lc_mathematics_higher_en_documents_ingested` asset
  materialises against the 2024 syllabus PDF
- **THEN** the partition key SHALL be
  `(scope="ireland__leaving_cycle__mathematics__na__higher__en", year="2024")`
- **AND** the asset_check SHALL enforce that every emitted row's
  `jurisdiction`, `stage`, `subject_slug`, `board`, `qualification_level`,
  and `language` columns match the `scope` partition

#### Scenario: An England AQA GCSE Mathematics 2025 asset lands in the right partition

- **WHEN** the `england_gcse_mathematics_aqa_documents_ingested` asset
  materialises against the 2025 spec
- **THEN** the partition key SHALL be
  `(scope="england__gcse__mathematics__aqa__gcse__en", year="2025")`
- **AND** the asset_check SHALL enforce that every emitted row's `board`
  matches `aqa` and `qualification_level` matches `gcse`

### Requirement: BIEP v3 daily Declarative Automation (per-milestone cron)

The `CelticAgentOpsComponent` SHALL provide daily Declarative Automation
(`AutomationCondition.cron(...)`) for each of the 4 BIEP v3 jurisdiction
pipelines, defined in `orchestration/automation/biiep_daily_automation.py`:

- `ireland_leaving_cycle_documents_ingested` — `AutomationCondition.cron("@daily")` at 02:00 UTC
- `ireland_junior_cycle_documents_ingested` — `AutomationCondition.cron("@daily")` at 02:30 UTC
- `england_a_level_documents_ingested` — `AutomationCondition.cron("@daily")` at 03:00 UTC
- `england_gcse_documents_ingested` — `AutomationCondition.cron("@daily")` at 03:30 UTC

The 6-hour `ScheduleDefinition` at
`orchestration/defs/2_materials/ocr_comparison/ensemble_comparison/biiep_ocr_ensemble.py:126-132`
SHALL be retired in favour of the per-milisdiction daily automation.

#### Scenario: Ireland LC daily automation fires at 02:00 UTC

- **WHEN** the daily cron fires at 02:00 UTC
- **THEN** the `ireland_leaving_cycle_documents_ingested` asset job fires
- **AND** the `ireland_lc_documents_ingested_check` asset_check resolves
  through the asset dependency chain
- **AND** the asset graph re-materialises the LC partition for the
  current year

#### Scenario: England AQA ChangeDetection sensor triggers

- **WHEN** the `england_aqa_a_level_jcq_monitor` ChangeDetection.io sensor
  fires (a new AQA A-Level spec is published)
- **THEN** the `england_a_level_documents_ingested` asset re-materialises
- **AND** the 4-path OCR ensemble runs against the new PDF
- **AND** the asset check `england_a_level_extractions_ragas_check` MUST
  pass with `ragas_score >= 0.70`
- **AND** an alert is posted to the `#kcg-biep-v3` Slack channel via the
  `biiep_daily_automation` post-hook
