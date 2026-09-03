# OpenAPI Source Generator (dlt-init-openapi)

`dlt-init-openapi` is a 3rd-party tool that **auto-generates a
verified dlt source from any OpenAPI spec**. It parses the spec,
inspects the example responses, and produces a typed Python module
with one `@dlt.resource` per endpoint.

## Install

```bash
pip install dlt-init-openapi
```

## Usage

```bash
# 1. Download the OpenAPI spec
curl -o spec.json https://api.example.com/openapi.json

# 2. Generate the source
dlt-init-openapi source spec.json --output ./generated_sources/example_api

# 3. Use the generated source
```

The generated module has:

- One `@dlt.source` per tag (e.g. `users`, `orders`, `products`)
- One `@dlt.resource` per endpoint
- Typed `pydantic` models for the response schema
- `incremental` cursor configuration for endpoints that support it
- A `Pipeline` class wired to the dlt destination

```python
# generated_sources/example_api/__init__.py
from .pipeline import example_api_source

source = example_api_source()
load_info = dlt.pipeline(
    pipeline_name="example_api",
    destination="duckdb",
    dataset_name="example",
).run(source)
```

## When to use this

- You're integrating with a **REST API that has an OpenAPI spec**
- The spec is **stable** (the API doesn't change frequently)
- You want a **verified, typed source** without hand-writing the
  `@dlt.resource` per endpoint

## When NOT to use this

- The API doesn't have an OpenAPI spec → use `create-rest-api-pipeline`
  instead (hand-write the resources)
- The spec is large (> 100 endpoints) → consider scoping to a
  subset
- The spec is unstable → you'll regenerate often, hand-writing is
  more stable

## KCG usage

- `dlt/british_isles/ireland/` (NCCA, SEC, DES) — most
  Irish sources are hand-written (no OpenAPI spec)
- `dlt/british_isles/northern_ireland/ccea_curriculum.py` —
  CCEA pages, hand-written
- `dlt/british_isles/medicine/ie/hse.py` — HSE OpenData
  portal (some endpoints have OpenAPI specs; could be migrated to
  `dlt-init-openapi` for auto-generation)

## Reference

- The `dlt_OpenAPI_Generator.py` reference (the full generator
  workflow) was in `docs/dlt/` (deleted with the
  `sync-skills-from-docs` change)
- The `dlt-init-openapi` docs: <https://github.com/dlt-hub/dlt-init-openapi>
- The `create-rest-api-pipeline` sub-skill for the hand-written
  approach
