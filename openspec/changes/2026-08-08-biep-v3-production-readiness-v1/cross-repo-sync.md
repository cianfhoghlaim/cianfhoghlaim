# Cross-repo-sync: 2026-08-08-biep-v3-production-readiness-v1

## Affected repos

- `cianfhoghlaim` (this repo) — OCR ensemble + RAGAS + automation code

## Commit plan

### Commit 1 (cianfhoghlaim repo)

```
1. Update meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py
   - real httpx calls for Docling + Unstract + qwen3-vl + gemma4
2. Update meaisinfhoghlaim/evaluation/ragas_biiep_ensemble.py
   - biiep_v2 → biiep_v3 rename
3. Create cocoindex/subjects/education_subject_embedding.py
4. Create orchestration/automation/{subject_backfill,biiep_daily_automation}.py
```

## Push targets

- `origin/openspec/2026-07-25-refactor-batch-v1`
