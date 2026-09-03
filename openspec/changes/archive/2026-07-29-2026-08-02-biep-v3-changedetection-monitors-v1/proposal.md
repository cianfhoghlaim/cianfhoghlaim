## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

# 2026-08-02-biep-v3-changedetection-monitors-v1

## Why

The BIEP v3 batch shipped 5 generic jurisdiction pipelines (Ireland,
England, SCT/WLS/NI, Crown Dependencies) covering ~1,560 cohorts across
8 British Isles jurisdictions. But the ChangeDetection.io monitors
that drive the freshness guarantee (per the 2026-07-22 BIEP v2
spec) are MISSING for 7 of the 8 jurisdictions.

Today only 3 monitors exist: `aqa_monitor.yaml` (England — AQA only),
`edexcel_monitor.yaml` (England — Edexcel), `ocr_monitor.yaml`
(generic OCR). None cover:
- Ireland (NCCA + SEC)
- Scotland (SQA)
- Wales (WJEC)
- Northern Ireland (CCEA)
- Jersey
- Guernsey
- Isle of Man

This is the B2 change. It lives in the **bonneagar repo** (the
ChangeDetection.io stack is at
`bonnegar/stacks/changedetection/monitors/`).

## What changes

7 new ChangeDetection.io monitor YAML files:

- `ncca_monitor.yaml` — Ireland NCCA + SEC
- `sqa_monitor.yaml` — Scotland SQA (National 5 + Higher + Adv Higher)
- `wjec_monitor.yaml` — Wales WJEC (GCSE + A-Level + Welsh Baccalaureate)
- `ccea_monitor.yaml` — Northern Ireland CCEA (GCSE + A-Level)
- `jersey_monitor.yaml` — States of Jersey Education Department
- `guernsey_monitor.yaml` — States of Guernsey Education Services
- `iom_monitor.yaml` — Isle of Man Department of Education

Each mirrors the 3 existing England monitors' 6-label GOLD_STANDARD fields.
Webhook target = `http://dagster-webhook:8080/webhooks/biep_change_detection`
(the BIEP umbrella webhook).

## Dependencies

```yaml
Blocked by: 2026-07-31-biep-v3-crown-dependencies-v1
Blocked by (soft): 2026-08-01-bonneagar-iac-namespace-alignment-v1
Affected repos: bonneagar (single-repo change)
```

## Acceptance gates

- `bun run changedetection:list` returns 10 monitors (3 existing + 7 new)
- All 7 new monitors point at the BIEP umbrella webhook
- `openspec validate 2026-08-02-biep-v3-changedetection-monitors-v1 --strict` passes

## Cross-references

- `bonnegar/stacks/changedetection/monitors/{aqa,edexcel,ocr}_monitor.yaml` (existing)
- `bonnegar/stacks/changedetection/stacks/changedetection.compose.yaml` (the stack)
- `.agents/skills/change-detection/SKILL.md` — the 4-layer change-detection pattern