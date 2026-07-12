# Modal GPU Compute

The `dagster-modal` integration lets you run Dagster assets on
Modal (the serverless GPU platform). Useful for HTR training, OCR
ensemble, and any GPU-bound work.

## When to use this

- The asset needs a **GPU** (HTR, OCR ensemble, fine-tuning)
- The workload is **spiky** (e.g. nightly HTR retraining, not
  24/7 inference)
- The on-prem `bunchloch` / `arm1-oci` hardware is busy

## Reference

- The `docs/dagster/integrations/dagster-modal/` example
  (26-line README + `dagster_modal/resources.py`) was in
  `docs/dagster/integrations/` (deleted with the
  `sync-skills-from-docs` change). The same content is in the
  upstream [dagster-modal](https://github.com/dagster-io/dagster/tree/master/python_modules/libraries/dagster-modal)
  package
- The Modal docs: <https://modal.com/docs>
- The KCG stack uses Modal for `agents/meaisinfhoghlaim/ocr/` HTR
  fine-tuning and OCR ensemble inference
- The `meaisinfhoghlaim-ocr-htr` openspec spec
