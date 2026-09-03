# Dagster group-name migration: slash → underscore

Per the **2026-08-06-biep-v3-critical-path-fixes-v1** change + the
pending correction at
`openspec/changes/2026-07-17-fix-dagster-group-name-bug-and-baml-blocker-v1/specs/dagster-5-layer-component-architecture/spec.md:5-31`.

Dagster 1.13.1 rejects `/` in `group_name=`. The canonical migration
is to replace `/` with `_`.

## Convention

| Old (invalid) | New (valid) |
|---|---|
| `1_ingestion/education/ireland/documents` | `1_ingestion_education_ireland_documents` |
| `2_materials/education/ireland/extractions` | `2_materials_education_ireland_extractions` |
| `3_model_lifecycle/education/ireland/embeddings` | `3_model_lifecycle_education_ireland_embeddings` |
| `official_media/jurisdictions` | `official_media_jurisdictions` |
| `official_media/hmgcc` | `official_media_hmgcc` |
| `official_media/companies_house` | `official_media_companies_house` |

## Migration script

```bash
cd /Users/cianmacandeisigh/dev/kings_college_galway

# Find all group_name= decorators with slashes
grep -rnE 'group_name="[^"]*/' orchestration/ --include="*.py"

# Replace slashes with underscores (per-file)
find orchestration/ -name "*.py" -exec sed -i '' 's|\(group_name="[^"]*\)/|\1_|g; s|\(group_name="[^"]*\)_/|\1_|g' {} \;
# (Run twice if a single name had 2+ slashes)

# Verify
grep -rnE 'group_name="[^"]*/' orchestration/ --include="*.py"
# Expected: 0 matches
```

## Validation

```bash
dg check yaml
# Expected: 0 validation errors
```

## Cross-references

- `openspec/changes/2026-07-17-fix-dagster-group-name-bug-and-baml-blocker-v1/specs/dagster-5-layer-component-architecture/spec.md`
- `openspec/specs/dagster-5-layer-component-architecture/spec.md:93-106`
- `.agents/skills/dagster/SKILL.md` (the canonical 5-layer group convention)
