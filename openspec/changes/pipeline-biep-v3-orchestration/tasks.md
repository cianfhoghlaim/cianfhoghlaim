# Tasks: pipeline-biep-v3-orchestration

> Cross-batch BIEP v3 orchestration contract.
> Absorbs `2026-08-13-biep-v3-orchestration-activation-v1` (0/17) +
> `2026-08-10-england-biiep-pipeline-v1` (0/17).

## 1. BIEP v3 orchestration activation (from biep-v3-orchestration-activation-v1)

- [ ] **O1.1** Add `scripts/download_gguf_weights.py` (downloads 17 GGUF models into `stedding/huggingface/gguf/`)
- [ ] **O1.2** Add `scripts/verify_litellm_redeploy.sh` (`km deploy stack litellm --force` + health assertion)
- [ ] **O1.3** Fix the litellm `router_settings.fallbacks` (the malformed config causing the crash-loop)
- [ ] **O1.4** Fix the llama-swap image tag (currently wrong)
- [ ] **O1.5** Update `infrastructure-stacks/spec.md` — new requirement: litellm + llama-swap MUST be redeployed + GGUF-loaded before any BIEP v2 OCR asset can run

## 2. England BIEP pipeline (from england-biiep-pipeline-v1)

- [ ] **E2.1** `dlt_sources/gcse_aqa_source.py`
- [ ] **E2.2** `dlt_sources/gcse_ocr_source.py`
- [ ] **E2.3** `dlt_sources/gcse_edexcel_source.py`
- [ ] **E2.4** `dlt_sources/a_level_aqa_source.py`
- [ ] **E2.5** `dlt_sources/a_level_ocr_source.py`
- [ ] **E2.6** `dlt_sources/a_level_edexcel_source.py`
- [ ] **E2.7** Real BAML prompt `ExtractAQAQualSpec` (baml_src/british_isles/england/education/aqa_qual_spec.baml)
- [ ] **E2.8** Dagster asset group for England BIEP (3 boards × 92 subjects)
- [ ] **E2.9** Misconfig-check + seeds for the 92 subjects
- [ ] **E2.10** Update `openspec/specs/bie-8-jurisdictions/spec.md` +3 ADDED Requirements (DLT sources + Dagster assets + BAML extraction for England)

## 3. Verification

- [ ] Run `openssl validate pipeline-biep-v3-orchestration --strict` — pass
- [ ] Run `mise run cianfhoghlaim:biep:v3:smoke` — pass

## Verification

```bash
cd ~/dev/cianchosaint-laim 2>/dev/null || cd ~/dev/cianfhoghlaim
openspec validate pipeline-biep-v3-orchestration --strict
```
