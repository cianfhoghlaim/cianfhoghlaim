# Dynamic Schema Extraction (TypeBuilder + `@@dynamic`)

The **dynamic schema** pattern lets you extract records whose schema
is not known at `.baml` authoring time. It uses two BAML functions
in sequence:

1. **Generate** — ask the LLM to describe the schema in BAML source
2. **Execute** — use `TypeBuilder.add_baml()` to inject the schema,
   then extract against the runtime-built class

This is the canonical pattern from the BAML `ai that works` episode
"Dynamic Schemas" (Sep 2025) and the `extract-anything` example.

## The two BAML functions

```baml
// baml_src/generate_baml.baml
template_string BAMLBackground() #"
  You are a BAML schema designer. Output ONLY valid BAML source code
  that defines a class for the data you find in the content.

  Example:
  class Response {
    data {
      name string
      age int
    }
  }
"#

class Schema {
  interface_code string
  return_type string  // the class definition
  other_code string?  // any helper classes
}

function GenerateBAML(
  content: string | image | audio | image[]
) -> Schema {
  client "openai/gpt-4o"
  prompt #"
    {{ BAMLBackground() }}

    Content to summarise:
    ```
    {{ content }}
    ```

    {{ ctx.output_format }}
  "#
}
```

```baml
// baml_src/execute_baml.baml
class Response {
  @@dynamic  // allow runtime-injected fields
}

function ExecuteBAML(
  content: string | image | audio | pdf,
  dynamic_class_output: string
) -> Response {
  client "openai/gpt-4o"
  prompt #"
    Extract the data from the following content using this BAML class:

    ```baml
    class Response { data { {{ dynamic_class_output }} } }
    ```

    Content:
    ```
    {{ content }}
    ```

    {{ ctx.output_format }}
  "#
}
```

## The Python glue

```python
from baml_client import b
from baml_client.type_builder import TypeBuilder

def extract_anything(content: str | bytes, content_type: str = "text"):
    """Extract any data from any content. Schema is LLM-generated."""
    # 1. Build the input based on content type
    if content_type == "image":
        import baml_py, base64
        image = baml_py.Image.from_base64("image/png", base64.b64encode(content).decode())
        content = image
    elif content_type == "pdf":
        import baml_py
        content = baml_py.Pdf.from_base64(content)

    # 2. Step 1: ask the LLM to describe the schema
    schema = b.GenerateBAML(content)
    # schema.return_type is something like "name string, age int"

    # 3. Step 2: build a TypeBuilder and inject the runtime class
    tb = TypeBuilder()
    tb.add_baml(f"class Response {{ data {{ {schema.return_type} }} }}")

    # 4. Step 3: execute the extraction
    response = b.ExecuteBAML(content, schema.return_type, baml_options={"tb": tb})
    return response
```

## Use cases in KCG

- **Ad-hoc corpus ingestion** — user dumps a folder of obscure PDFs
  (e.g. an old Irish-medium exam paper) and the system extracts
  whatever it can without writing a new `.baml` first
- **Site analysis** — `baml/site_analysis.baml`
  extracts site properties (CMS, captcha, robots.txt) where the
  exact set of properties varies by site
- **UI component extraction** — `baml/ui_components.baml`
  can adapt to novel UI patterns (e.g. a new dashboard layout)
- **Portfolio extraction** — `baml/portfolio_extraction.baml`
  for the croilar personal-archive CV / achievements PDFs

## Limitations

- **Type safety is weakened** — the runtime-injected class is not
  validated at compile time. Use deterministic runtime evals
  (see `runtime-evals.md`) to validate the extraction.
- **Two LLM calls per extraction** — the Generate step adds latency
  and cost. Cache the schema for repeated content of the same type.
- **The LLM may hallucinate a bad schema** — the `interface_code` /
  `other_code` fields let you inspect the generated schema before
  executing.

## Debugging

```python
schema = b.GenerateBAML(content)
print("Generated schema:")
print(schema.interface_code)
print("---")
print("Return type:")
print(schema.return_type)
print("---")
print("Other code:")
print(schema.other_code or "(none)")

# Manually inspect the TypeBuilder
tb = TypeBuilder()
tb.add_baml(f"class Response {{ data {{ {schema.return_type} }} }}")
print("TypeBuilder:", tb)
```

## Reference

- The `extract-anything` and `2025-09-30-dyanmic-schemas` example
  projects (deleted with `docs/baml/`) are the canonical references.
  The same examples are in the upstream
  [BoundaryML/baml-examples](https://github.com/BoundaryML/baml-examples) repo.
- The `ai that works: Dynamic Schemas` video: <https://youtu.be/bak7-C--azc>
- The BAML `@@dynamic` docs: <https://docs.boundaryml.com/ref/dynamic>
