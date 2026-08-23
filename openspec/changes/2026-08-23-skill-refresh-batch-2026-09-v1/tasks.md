## Implementation Tasks

- [x] 1. Add "What's new in 2026-08/09" section to 8 skills (apple-photos-ingestion, huggingface, mlflow, langfuse, cognee, graphiti, dagster, dlt). (verification-id: skills-refreshed) (verification: inspection)

- [x] 2. Fold `dignified-python-310`, `-311`, `-312`, `-313` into DEPRECATED redirect stubs pointing to canonical `dignified-python`. (verification-id: python-variants-folded) (verification: inspection — `wc -l .agents/skills/dignified-python-*/SKILL.md` returns ≤ 10 lines each)

- [x] 3. Run `mise run lint:skills` + `mise run lint-skill:deprecated-cleanup` to confirm no regressions. (verification-id: lint-passes) (verification: integration — both tasks exit 0)

- [x] 4. Run canonical CI gates: `mise run core:typecheck` (exit 0), `openspec validate --all --strict` (exit 0). (verification-id: no-regressions) (verification: integration)

## Final Validation

- [x] `openspec validate 2026-08-23-skill-refresh-batch-2026-09-v1 --strict` passes
- [x] 8 skills refreshed
- [x] 4 python variants folded
- [x] All lint gates pass
- [x] Canonical CI gates pass