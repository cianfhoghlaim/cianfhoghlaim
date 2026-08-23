## ADDED Requirements

### Requirement: skill-refresh-batch-2026-09

The `.agents/skills/` tree SHALL be refreshed in batch 2026-09: 8
skills gain a "What's new in 2026-08/09" section + the 4
`dignified-python-310/311/312/313` variants fold into DEPRECATED
redirects pointing to the canonical `dignified-python` skill.

#### Scenario: 8 skills are refreshed with new sections

- **WHEN** the skill refresh batch runs
- **THEN** 8 skills (apple-photos-ingestion, huggingface, mlflow,
  langfuse, cognee, graphiti, dagster, dlt) MUST each include a
  "What's new in 2026-08/09" section

#### Scenario: 4 dignified-python variants are redirects

- **WHEN** the 4 `dignified-python-310/311/312/313` variants are folded
- **THEN** each variant MUST be ≤ 10 lines
- **AND** each MUST contain a `Use the canonical replacement:` line
  pointing to `dignified-python`

#### Scenario: lint gates still pass

- **WHEN** the skill refresh + fold is complete
- **THEN** `mise run lint:skills` MUST exit 0 (no frontmatter drift)
- **AND** `mise run lint-skill:deprecated-cleanup` MUST exit 0
  (all DEPRECATED files are ≤ 50 lines)