---
name: baml
description: Expert assistance for building type-safe LLM applications with BAML (Basically A Made-up Language). Use when users need structured LLM outputs, prompt engineering, schema definitions, or multi-model orchestration with automatic retries and validation.
---

# BAML - Type-Safe LLM Development

**Version:** 0.76.x | **Last Updated:** 2025-01

## Overview

BAML (Basically A Made-up Language) is a domain-specific language for building type-safe, production-ready LLM applications. It provides:

- **Type-Safe Outputs**: Define structured schemas that LLMs must follow
- **Multi-Provider Support**: Works with OpenAI, Anthropic, Google, Azure, Ollama, and more
- **Automatic Retries**: Built-in retry logic with fallback models
- **Code Generation**: Generates native Python/TypeScript clients from schemas
- **Streaming Support**: Type-safe streaming with partial object parsing
- **Testing/Validation**: Built-in playground for prompt iteration

**Documentation**: https://docs.boundaryml.com

## When to Use This Skill

Activate when users need:

- "Extract structured data from text using an LLM"
- "Create type-safe prompts with validation"
- "Build multi-model pipelines with fallbacks"
- "Generate code from LLM responses"
- "Stream partial LLM responses with types"
- "Test and iterate on prompts"

## Core Concepts

### 1. BAML Files (.baml)

BAML uses `.baml` files to define:
- **Classes/Enums**: Output schemas
- **Functions**: LLM operations
- **Clients**: Model configurations
- **Tests**: Validation cases

```baml
// schema.baml

// Define output structure
class ExtractedEntity {
  name string
  type EntityType
  confidence float @description("0.0 to 1.0")
}

enum EntityType {
  PERSON
  ORGANIZATION
  LOCATION
  DATE
}

// Define LLM function
function ExtractEntities(text: string) -> ExtractedEntity[] {
  client GPT4oMini
  prompt #"
    Extract all named entities from the following text.

    Text: {{ text }}

    {{ ctx.output_format }}
  "#
}

// Configure model
client<llm> GPT4oMini {
  provider openai
  options {
    model "gpt-4o-mini"
    temperature 0.1
  }
}

// Test case
test ExtractEntitiesTest {
  functions [ExtractEntities]
  args {
    text "Apple Inc. was founded by Steve Jobs in Cupertino, California on April 1, 1976."
  }
}
```

### 2. Type System

**Primitive Types:**
- `string` - Text
- `int` - Integer
- `float` - Decimal number
- `bool` - Boolean
- `null` - Null value

**Complex Types:**
- `ClassName` - Custom class
- `EnumName` - Enumeration
- `Type[]` - Array
- `Type?` - Optional (nullable)
- `map<K, V>` - Key-value map
- `Type | Type` - Union type

**Type Annotations:**
```baml
class Product {
  name string
  price float
  tags string[]
  metadata map<string, string>
  category Category?
  status Active | Inactive | Pending
}
```

### 3. Prompt Engineering

**Template Syntax:**
```baml
prompt #"
  {{ variable }}              // Insert variable
  {{ ctx.output_format }}     // Insert expected output schema
  {{ _.role("system") }}      // Set message role
  {{ _.chat([...]) }}         // Multi-turn chat
"#
```

**Multi-Turn Chat:**
```baml
function ChatWithHistory(messages: Message[], query: string) -> string {
  client GPT4oMini
  prompt #"
    {{ _.role("system") }}
    You are a helpful assistant.

    {{ _.chat(messages) }}

    {{ _.role("user") }}
    {{ query }}
  "#
}

class Message {
  role "user" | "assistant"
  content string
}
```

**Output Format Injection:**
```baml
function Analyze(text: string) -> Analysis {
  client Claude
  prompt #"
    Analyze the following text and provide structured output.

    Text: {{ text }}

    Respond in this exact format:
    {{ ctx.output_format }}
  "#
}
```

### 4. Client Configuration

**OpenAI:**
```baml
client<llm> GPT4 {
  provider openai
  options {
    model "gpt-4o"
    temperature 0.7
    max_tokens 4096
    api_key env.OPENAI_API_KEY
  }
}
```

**Anthropic:**
```baml
client<llm> Claude {
  provider anthropic
  options {
    model "claude-sonnet-4-20250514"
    max_tokens 4096
    api_key env.ANTHROPIC_API_KEY
  }
}
```

**Google (Gemini):**
```baml
client<llm> Gemini {
  provider google-ai
  options {
    model "gemini-1.5-pro"
    api_key env.GOOGLE_API_KEY
  }
}
```

**Ollama (Local):**
```baml
client<llm> LocalLlama {
  provider ollama
  options {
    model "llama3.2"
    base_url "http://localhost:11434/v1"
  }
}
```

**Azure OpenAI:**
```baml
client<llm> AzureGPT {
  provider azure-openai
  options {
    resource_name "my-resource"
    deployment_id "gpt-4-deployment"
    api_key env.AZURE_OPENAI_KEY
  }
}
```

### 5. Retry and Fallback Strategies

**Simple Retry:**
```baml
client<llm> ReliableGPT {
  provider openai
  retry_policy Exponential
  options {
    model "gpt-4o-mini"
  }
}

retry_policy Exponential {
  max_retries 3
  strategy {
    type exponential_backoff
    delay_ms 1000
    multiplier 2
  }
}
```

**Fallback Chain:**
```baml
client<llm> ResilientLLM {
  provider fallback
  options {
    strategy [GPT4, Claude, Gemini]
  }
}
```

**Round-Robin Load Balancing:**
```baml
client<llm> LoadBalanced {
  provider round-robin
  options {
    strategy [GPT4Instance1, GPT4Instance2, GPT4Instance3]
  }
}
```

### 6. Streaming

**Define Streamable Function:**
```baml
function GenerateStory(topic: string) -> Story {
  client GPT4
  prompt #"
    Write a short story about {{ topic }}.
    {{ ctx.output_format }}
  "#
}

class Story {
  title string
  chapters Chapter[]
}

class Chapter {
  title string
  content string
}
```

**Python Streaming Usage:**
```python
from baml_client import b
from baml_client.types import Story

async def stream_story():
    async with b.stream.GenerateStory("space exploration") as stream:
        async for partial in stream:
            # partial is Partial[Story] with available fields
            if partial.title:
                print(f"Title: {partial.title}")
            if partial.chapters:
                for ch in partial.chapters:
                    if ch.content:
                        print(ch.content, end="", flush=True)

        # Get final complete result
        final: Story = await stream.get_final_response()
```

## Project Setup

### Installation

```bash
# Install BAML CLI
pip install baml-py

# Or with uv
uv add baml-py

# Initialize project
baml init

# Generate client code
baml generate
```

### Project Structure

```
project/
├── baml_src/           # BAML source files
│   ├── main.baml       # Main definitions
│   ├── clients.baml    # Client configurations
│   └── generators.baml # Code generation config
├── baml_client/        # Generated code (don't edit)
│   ├── __init__.py
│   ├── sync_client.py
│   └── async_client.py
└── main.py             # Your application
```

### Generator Configuration

```baml
// baml_src/generators.baml

generator python {
  output_type python/pydantic
  output_dir ../baml_client
  version "0.76.0"
}

generator typescript {
  output_type typescript
  output_dir ../baml_client_ts
  version "0.76.0"
}
```

## Python Usage

### Basic Usage

```python
from baml_client import b
from baml_client.types import ExtractedEntity

# Synchronous call
entities: list[ExtractedEntity] = b.ExtractEntities(
    text="Apple Inc. was founded by Steve Jobs in Cupertino."
)

for entity in entities:
    print(f"{entity.name} ({entity.type}): {entity.confidence}")
```

### Async Usage

```python
import asyncio
from baml_client import b

async def main():
    result = await b.ExtractEntities(
        text="Microsoft was founded by Bill Gates in Albuquerque."
    )
    return result

entities = asyncio.run(main())
```

### Context and Tracing

```python
from baml_client import b
from baml_client.tracing import trace, set_tags

@trace
async def process_document(doc_id: str, content: str):
    set_tags(document_id=doc_id)

    # All BAML calls within are traced
    entities = await b.ExtractEntities(text=content)
    summary = await b.Summarize(text=content)

    return {"entities": entities, "summary": summary}
```

### Dynamic Client Selection

```python
from baml_client import b
from baml_client.types import ClientRegistry

# Override client at runtime
registry = ClientRegistry()
registry.add_llm_client("GPT4oMini", "openai", {
    "model": "gpt-4o-mini",
    "api_key": custom_api_key
})

result = b.ExtractEntities(
    text="...",
    baml_options={"client_registry": registry}
)
```

## TypeScript Usage

```typescript
import { b } from './baml_client';
import type { ExtractedEntity } from './baml_client/types';

// Synchronous
const entities: ExtractedEntity[] = await b.ExtractEntities({
  text: "Google was founded by Larry Page and Sergey Brin."
});

// Streaming
const stream = b.stream.GenerateStory({ topic: "AI" });
for await (const partial of stream) {
  if (partial.title) {
    console.log(`Title: ${partial.title}`);
  }
}
const final = await stream.getFinalResponse();
```

## Common Patterns

### 1. Entity Extraction

```baml
class Person {
  name string
  role string?
  organization string?
}

function ExtractPeople(text: string) -> Person[] {
  client GPT4oMini
  prompt #"
    Extract all people mentioned in the text.
    Include their role and organization if mentioned.

    Text: {{ text }}

    {{ ctx.output_format }}
  "#
}
```

### 2. Classification

```baml
enum Sentiment {
  POSITIVE @alias("pos") @description("Happy, satisfied, enthusiastic")
  NEGATIVE @alias("neg") @description("Angry, disappointed, frustrated")
  NEUTRAL @alias("neu") @description("Factual, informational")
}

function ClassifySentiment(text: string) -> Sentiment {
  client GPT4oMini
  prompt #"
    Classify the sentiment of this text.

    Text: {{ text }}

    {{ ctx.output_format }}
  "#
}
```

### 3. Summarization

```baml
class Summary {
  title string @description("A concise title")
  key_points string[] @description("3-5 main points")
  word_count int
}

function Summarize(document: string, max_words: int) -> Summary {
  client Claude
  prompt #"
    Summarize the following document in {{ max_words }} words or less.

    Document:
    {{ document }}

    {{ ctx.output_format }}
  "#
}
```

### 4. Multi-Step Reasoning

```baml
class ReasoningStep {
  step_number int
  thought string
  action string?
}

class ReasonedAnswer {
  reasoning ReasoningStep[]
  final_answer string
  confidence float
}

function AnswerWithReasoning(question: string, context: string) -> ReasonedAnswer {
  client GPT4
  prompt #"
    {{ _.role("system") }}
    You are a careful reasoner. Think step by step before answering.

    {{ _.role("user") }}
    Context: {{ context }}

    Question: {{ question }}

    Think through this step by step, then provide your answer.
    {{ ctx.output_format }}
  "#
}
```

### 5. Image Analysis

```baml
class ImageAnalysis {
  description string
  objects string[]
  text_content string?
  sentiment Sentiment?
}

function AnalyzeImage(image: image) -> ImageAnalysis {
  client GPT4Vision
  prompt #"
    Analyze this image in detail.

    {{ image }}

    {{ ctx.output_format }}
  "#
}

client<llm> GPT4Vision {
  provider openai
  options {
    model "gpt-4o"
  }
}
```

### 6. Tool/Function Calling

```baml
class ToolCall {
  tool_name "search" | "calculate" | "lookup"
  arguments map<string, string>
}

class AgentResponse {
  thought string
  tool_calls ToolCall[]?
  final_response string?
}

function AgentStep(query: string, context: string) -> AgentResponse {
  client GPT4
  prompt #"
    You are an AI assistant with access to tools.

    Available tools:
    - search(query): Search the web
    - calculate(expression): Evaluate math
    - lookup(key): Look up information

    Context from previous steps:
    {{ context }}

    User query: {{ query }}

    Think about what to do, then either call tools or provide a final response.
    {{ ctx.output_format }}
  "#
}
```

## Testing and Iteration

### BAML Playground

```bash
# Start playground server
baml test

# Opens browser at http://localhost:3000
```

### Test Cases in BAML

```baml
test SentimentTest {
  functions [ClassifySentiment]
  args {
    text "I love this product! It's amazing!"
  }
  @assert(result == POSITIVE)
}

test ExtractEntitiesTest {
  functions [ExtractEntities]
  args {
    text "Elon Musk is the CEO of Tesla and SpaceX."
  }
  @assert(len(result) >= 3)
}
```

### Python Testing

```python
import pytest
from baml_client import b

@pytest.mark.asyncio
async def test_extract_entities():
    result = await b.ExtractEntities(
        text="Amazon was founded by Jeff Bezos in Seattle."
    )

    assert len(result) >= 2
    names = [e.name for e in result]
    assert "Jeff Bezos" in names or "Bezos" in names
```

## Best Practices

### 1. Schema Design

**DO:**
```baml
class WellDesigned {
  id string @description("Unique identifier")
  name string
  score float @description("Value between 0.0 and 1.0")
  tags string[] @description("Relevant keywords")
}
```

**DON'T:**
```baml
class PoorlyDesigned {
  data map<string, string>  // Too generic
  info string               // Vague naming
}
```

### 2. Prompt Engineering

**DO:**
- Use `@description` annotations to guide the LLM
- Include examples in prompts for complex outputs
- Use `{{ ctx.output_format }}` for structured outputs
- Set appropriate temperature (low for extraction, higher for generation)

**DON'T:**
- Leave ambiguous field names without descriptions
- Rely solely on field names for LLM understanding
- Use high temperature for structured extraction

### 3. Error Handling

```python
from baml_client import b
from baml_client.errors import BamlValidationError

try:
    result = b.ExtractEntities(text=user_input)
except BamlValidationError as e:
    # LLM output didn't match schema
    logger.error(f"Validation failed: {e}")
    # Use fallback or retry logic
except Exception as e:
    # API error, timeout, etc.
    logger.error(f"BAML error: {e}")
```

### 4. Performance Optimization

- Use `gpt-4o-mini` or `claude-3-haiku` for simple tasks
- Reserve powerful models for complex reasoning
- Implement caching for repeated queries
- Use streaming for long-form generation
- Batch similar requests when possible

## Integration Patterns

### With Dagster

```python
from dagster import asset, AssetExecutionContext
from baml_client import b

@asset
def extracted_entities(context: AssetExecutionContext, documents: list[dict]):
    results = []
    for doc in documents:
        entities = b.ExtractEntities(text=doc["content"])
        results.append({
            "doc_id": doc["id"],
            "entities": [e.model_dump() for e in entities]
        })
    return results
```

### With FastAPI

```python
from fastapi import FastAPI
from baml_client import b
from baml_client.types import ExtractedEntity

app = FastAPI()

@app.post("/extract", response_model=list[ExtractedEntity])
async def extract_entities(text: str):
    return await b.ExtractEntities(text=text)
```

### With LangChain

```python
from langchain.tools import tool
from baml_client import b

@tool
def extract_entities(text: str) -> str:
    """Extract named entities from text."""
    entities = b.ExtractEntities(text=text)
    return "\n".join([f"{e.name} ({e.type})" for e in entities])
```

## Troubleshooting

### "Schema validation failed"
- Check that LLM output matches your class definitions
- Add `@description` annotations to guide the LLM
- Lower temperature for more consistent outputs
- Review the raw LLM response in playground

### "Client not found"
- Run `baml generate` after adding new clients
- Check client name matches exactly in function definition
- Verify API key environment variables are set

### "Streaming not working"
- Ensure function returns a complex type (not primitive)
- Use `b.stream.FunctionName()` syntax
- Check model supports streaming

### "Rate limiting"
- Implement retry_policy with exponential backoff
- Use fallback chain with multiple providers
- Add delays between requests

## Resources

- **Documentation**: https://docs.boundaryml.com
- **Playground**: https://www.boundaryml.com/playground
- **GitHub**: https://github.com/BoundaryML/baml
- **Examples**: https://github.com/BoundaryML/baml/tree/main/examples
- **Discord**: https://discord.gg/boundaryml
