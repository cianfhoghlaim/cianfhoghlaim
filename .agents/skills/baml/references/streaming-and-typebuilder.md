# Streaming + TypeBuilder (combined pattern)

The most powerful BAML pattern: **stream partial results from a
runtime-built schema**. This is the heart of the `extract-anything`
example. You stream tokens from the LLM as they arrive, but the
schema is built at runtime via `TypeBuilder`.

## The BAML signatures

```baml
template_string BAMLBackground() #"
  You are a BAML schema designer. Output ONLY valid BAML source code
  that defines a class for the data you find in the content.
"#

class Schema {
  interface_code string
  return_type string
  other_code string?
}

function GenerateBAML(content: string | image | audio | image[]) -> Schema {
  client "openai/gpt-4o"
  prompt #"
    {{ BAMLBackground() }}
    Content: {{ content }}
    {{ ctx.output_format }}
  "#
}

class Response {
  @@dynamic
}

function ExecuteBAML(content: string | image | audio | pdf, dynamic_class_output: string) -> Response
  @stream.not_null
{
  client "openai/gpt-4o"
  prompt #"
    Use this BAML class:
    ```baml
    class Response { data { {{ dynamic_class_output }} } }
    ```
    Content: {{ content }}
    {{ ctx.output_format }}
  "#
}
```

## The Python glue (streaming + TypeBuilder)

```python
import asyncio
from baml_client import b
from baml_client.type_builder import TypeBuilder

async def extract_with_streaming(content):
    """Stream partial extractions while building the schema at runtime."""
    # 1. Ask the LLM to describe the schema (synchronous)
    schema = b.GenerateBAML(content)
    print(f"Generated return type: {schema.return_type}")

    # 2. Build the TypeBuilder
    tb = TypeBuilder()
    tb.add_baml(f"class Response {{ data {{ {schema.return_type} }} }}")

    # 3. Start streaming the extraction
    stream = b.stream.ExecuteBAML(
        content, schema.return_type, baml_options={"tb": tb}
    )

    # 4. Yield partial results as they arrive
    async for partial in stream:
        yield {"partial": partial, "final": False}

    # 5. Get the final typed result
    final = await stream.get_final_response()
    yield {"partial": None, "final": final}
```

## FastAPI server pattern (streaming + FastAPI)

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

@app.post("/extract")
async def extract(content: str):
    """Stream partial results via Server-Sent Events."""
    async def event_stream():
        async for event in extract_with_streaming(content):
            yield f"data: {json.dumps(event, default=str)}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

## React frontend (consuming the stream)

```typescript
async function extract(content: string) {
  const response = await fetch("/extract", {
    method: "POST",
    body: JSON.stringify({ content }),
    headers: { "Content-Type": "application/json" },
  });
  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value);
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const event = JSON.parse(line.slice(6));
        if (event.final) {
          console.log("Final result:", event.final);
        } else {
          console.log("Partial:", event.partial);
        }
      }
    }
  }
}
```

## Why combine streaming + TypeBuilder?

- **Streaming** gives the user partial results in real-time (better UX)
- **TypeBuilder** lets the system adapt to novel content (no manual
  schema writing)
- Together: a real-time, schema-adaptive extraction system that
  works for arbitrary content

## When to use this pattern

✅ **Use when**:
- The schema is genuinely novel (ad-hoc corpora, user-generated
  content, novel document types)
- UX requires partial results (live UIs, chatbots, real-time search)
- The extraction latency is dominated by the LLM (not the schema
  build)

❌ **Don't use when**:
- The schema is stable (use a static `.baml` instead)
- The LLM is fast enough that streaming is unnecessary
- The content is structured already (JSON / XML / CSV)

## Performance notes

- The Generate step adds ~1-2s of latency. Cache the schema for
  repeated content of the same type (e.g. by content hash or
  document kind)
- Streaming reduces **time to first byte** dramatically (~200ms vs
  ~3s for a full extraction) but not total latency
- For very long documents, consider streaming chunks of the
  document into the LLM rather than the whole thing at once

## Reference

- The `2025-09-30-dyanmic-schemas` and `extract-anything` examples
  (deleted with `docs/baml/`) are the canonical references. The same
  examples are in the upstream
  [BoundaryML/baml-examples](https://github.com/BoundaryML/baml-examples)
  repo.
- The `ai that works: Dynamic Schemas` video: <https://youtu.be/bak7-C--azc>
- BAML streaming docs: <https://docs.boundaryml.com/docs/streaming>
- BAML TypeBuilder docs: <https://docs.boundaryml.com/ref/dynamic>
