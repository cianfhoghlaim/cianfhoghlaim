# Deploy: Modal (serverless)

Deploy a dlt pipeline as a **serverless** Modal app. Modal is the
canonical serverless platform for dlt pipelines (used in the
`docs/dlt/examples/dlt_modal/` example, deleted with the docs).

## 3 Modal patterns

### 1. Image + secrets + schedule (the simplest)

```python
# main.py
import modal
import dlt

app = modal.App("dlt-pipeline")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("dlt[bigquery]")
    .add_local_python_source("pipeline")
)

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("gcp-sa-key")],
    schedule=modal.Period(days=1),  # daily
)
def run_pipeline():
    import dlt
    pipeline = dlt.pipeline(
        pipeline_name="daily_ingest",
        destination="bigquery",
        dataset_name="events",
    )
    load_info = pipeline.run(my_source())
    print(f"Loaded {load_info.loads_id}")

@app.local_entrypoint()
def main():
    run_pipeline.remote()
```

```bash
# Deploy
modal deploy main.py
```

### 2. Backfill (one-shot, parallel)

```python
@app.function(image=image, secrets=[...])
def ingest_one(pdf_path: str):
    """Ingest a single PDF. Runs in its own container."""
    pipeline = dlt.pipeline(pipeline_name="backfill", destination="bigquery", dataset_name="events")
    pipeline.run(chunks(pdf_path))

@app.local_entrypoint()
def backfill():
    pdf_paths = list(Path("stedding/ingest_queue").glob("**/*.pdf"))
    # Parallel fan-out: 10 at a time
    for batch in [pdf_paths[i:i+10] for i in range(0, len(pdf_paths), 10)]:
        ingest_one.map(batch)
```

### 3. Parallel (one container per file, scheduled)

```python
@app.function(image=image, secrets=[...], schedule=modal.Period(hours=1))
def ingest_all():
    pdf_paths = list(Path("stedding/ingest_queue").glob("**/*.pdf"))
    ingest_one.map(pdf_paths)  # all parallel
```

## KCG usage

The KCG stack runs Modal for **GPU workloads** (HTR training, OCR
ensemble). For dlt pipelines, the KCG stack prefers **Dagster on
`bunchloch` (M4 Mac) + `arm1-oci` (ARM)** because:

- dlt pipelines are I/O-bound, not GPU-bound
- Dagster provides better observability + lineage + backfills
- The on-prem hardware is already paid for

Modal is a valid alternative for **bursty workloads** (e.g. a
one-time backfill of 10k PDFs).

## Reference

- The `dlt_modal/` example (3 variants: image + secrets + schedule,
  backfill, parallel) was in `docs/dlt/examples/` (deleted with the
  `sync-skills-from-docs` change). The same content is in the
  [dlt-hub/dlt](https://github.com/dlt-hub/dlt/tree/master/docs/examples/dlt_modal)
  repo
- The Modal docs: <https://modal.com/docs>
