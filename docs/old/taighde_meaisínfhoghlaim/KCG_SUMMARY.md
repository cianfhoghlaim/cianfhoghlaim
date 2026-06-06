# taighde_meaisínfhoghlaim — Consolidation Summary

**Consolidated**: 2026-06-06
**Original size**: 118MB (76 .md files, 653 total files)
**Action**: MIGRATED

## What was here

Machine learning research and training resources:
- `open-instruct/` — Allen AI open-instruct fork (593 files, ~115MB)
- `convert_hf_to_gguf.py` — GGUF conversion script
- 45 .md files covering: Unsloth fine-tuning guides, VLM/OCR research, iOS/Phone LLM deployment, GPU experiment guides, MLX/MPS workflows
- 5 research PDFs (bolmo, molmo2, and others)

## Where it went

| Content | Destination |
|---------|-------------|
| `open-instruct/` | `docs/meaisínfhoghlaim/training/open-instruct/` |
| `convert_hf_to_gguf.py` | `docs/meaisínfhoghlaim/training/utils/` |
| *Unsloth*.md files | `docs/meaisínfhoghlaim/notebooks/unsloth/docs/` |
| *VLM*.md, *OCR*.md files | `docs/meaisínfhoghlaim/notebooks/vlm/docs/` |
| *Phone*.md, *iPhone*.md, *iOS*.md | `docs/meaisínfhoghlaim/training/phone/docs/` |
| *.ipynb notebooks | `docs/meaisínfhoghlaim/notebooks/archive/` |
| PDFs | `docs/old/papers/` |
| ANALYSIS_SUMMARY.md, README_ANALYSIS.md, QUICK_REFERENCE.md | `docs/meaisínfhoghlaim/` |
| All other .md files | `docs/meaisínfhoghlaim/` |

## Notes

The `open-instruct/` directory is the largest component (~115MB) and was fully migrated.
This was the largest content-directory source for the ML research migration.
