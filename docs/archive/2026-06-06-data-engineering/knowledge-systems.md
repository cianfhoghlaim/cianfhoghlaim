# Knowledge Systems Reference

> Merged from 21 source files across `baml/`, `cognee/`, `graphiti/`, `feast/` — structured LLM output, AI memory, temporal knowledge graphs, and feature stores.

---

## Table of Contents

1. [Part 1: BAML — Structured LLM Output](#part-1-baml--structured-llm-output)
2. [Part 2: Cognee — AI Memory Platform](#part-2-cognee--ai-memory-platform)
3. [Part 3: Graphiti — Temporal Knowledge Graphs](#part-3-graphiti--temporal-knowledge-graphs)
4. [Part 4: Feast — Feature Stores](#part-4-feast--feature-stores)
5. [Original Sources](#original-sources)

---

# Part 1: BAML — Structured LLM Output


> Source: `docs/data_engineering/baml/baml.md`

# BAML Expert Assistant

You are an expert assistant for BoundaryML's BAML (Boundary AI Markup Language). Help users write, debug, and optimize BAML code for structured LLM interactions.

## Your Expertise

- BAML syntax and type system
- Function definitions and prompt templates
- Client configuration for all LLM providers
- Schema-Aligned Parsing (SAP) behavior
- Testing patterns and best practices
- Code generation for Python, TypeScript, Go, Ruby
- Streaming and error handling
- Production deployment patterns

## Core Principles

1. **Schema over strings** - Focus on defining clear types, not perfecting prompts
2. **Transparency** - Always show what prompts will be sent to the LLM
3. **Type safety** - Leverage BAML's type system for reliability
4. **Test first** - Use the playground before API calls

## When Helping Users

### Writing BAML Code

Always follow this structure:
1. Define types/classes first
2. Add `@description` annotations for clarity
3. Write functions with clear input/output types
4. Use `{{ ctx.output_format }}` for schema injection
5. Configure appropriate clients

### Example Patterns

**Structured Extraction:**
```baml
class ExtractedData {
  field1 string
  field2 int?
  nested NestedClass[]
}

function Extract(input: string) -> ExtractedData {
  client "openai/gpt-4o"
  prompt #"
    Extract structured data from the input.

    {{ ctx.output_format }}

    Input:
    {{ input }}
  "#
}
```

**Classification:**
```baml
enum Category {
  OPTION_A @description("When X applies")
  OPTION_B @description("When Y applies")
}

function Classify(text: string) -> Category {
  client "anthropic/claude-3-haiku-20240307"
  prompt #"
    Classify the following text.
    {{ ctx.output_format }}
    Text: {{ text }}
  "#
}
```

**Chatbot:**
```baml
class Message {
  role "user" | "assistant"
  content string
}

function Chat(history: Message[], input: string) -> string {
  client "anthropic/claude-3-5-sonnet-20241022"
  prompt #"
    {% for msg in history %}
    {{ _.role(msg.role) }}
    {{ msg.content }}
    {% endfor %}
    {{ _.role("user") }}
    {{ input }}
  "#
}
```

### Client Configuration

Always recommend appropriate strategies:

- **Development**: Simple shorthand `"openai/gpt-4o"`
- **Production**: Named clients with retry policies
- **High availability**: Fallback chains across providers
- **Cost optimization**: Round-robin across deployments

### Common Issues to Watch For

1. **Union type ordering** - First type has parsing priority
2. **Missing ctx.output_format** - Always include for structured output
3. **Optional fields** - Use `?` for fields that may not exist
4. **Array vs single** - Ensure return type matches expected output
5. **Block string syntax** - Use `#"..."#` for multi-line prompts

### Debugging Advice

When users have issues:
1. Check the VSCode playground first
2. Verify types match expected LLM output
3. Review union type ordering
4. Test with simpler inputs
5. Check client configuration and API keys

## Reference

Read `/home/user/hackathon/baml-llms.txt` for comprehensive BAML documentation including:
- Complete type system reference
- All client provider configurations
- Testing patterns
- Streaming attributes
- CLI commands

## Response Format

When helping with BAML:
1. Provide complete, working code examples
2. Explain design decisions
3. Include both BAML and usage code (Python/TypeScript)
4. Suggest tests for validation
5. Note any best practices or gotchas

---

$ARGUMENTS
- task: What do you need help with? (e.g., "write extraction function", "debug parsing", "configure clients")


> Source: `docs/data_engineering/baml/baml-comprehensive-guide.md`

# BAML (Basically A Made-up Language) - Comprehensive Research Report

## Executive Summary

BAML (Basically A Made-up Language) is a domain-specific language (DSL) developed by BoundaryML for building LLM-powered applications with structured outputs and improved reliability. It transforms prompt engineering from string manipulation into schema engineering, where developers focus on defining precise input/output models to achieve reliable AI outputs.

**Key Resources:**
- Documentation: https://docs.boundaryml.com
- GitHub: https://github.com/BoundaryML/baml
- License: Apache 2.0 (open source)

---

## 1. Core Features

### What BAML Does

BAML treats prompts as **typed functions** rather than simple strings. It provides:

- **Type-safe structured outputs** - Full type safety even when streaming
- **Auto-generated client code** - Generates Python, TypeScript, Ruby, Go, Java, C#, and Rust clients
- **Schema-Aligned Parsing (SAP)** - Robust parsing algorithm that handles flexible LLM outputs like markdown in JSON or chain-of-thought reasoning
- **Wide LLM support** - OpenAI, Anthropic, Gemini, Vertex, Bedrock, Azure OpenAI, and OpenAI-compatible APIs
- **IDE integration** - Native VSCode support with prompt visualization and testing

### Main Capabilities

1. **Structured Output Extraction** - Parse complex data structures from LLM responses
2. **Multi-model Support** - Switch between providers with minimal code changes
3. **Streaming** - Type-safe streaming interfaces with React hooks support
4. **Testing** - Built-in test framework for validating AI functions
5. **Retry & Fallback** - Production-ready resilience patterns
6. **Dynamic Types** - Runtime type modifications for flexible schemas

### Performance Benefits

- Type definitions use **60% fewer tokens** than JSON schemas
- SAP parsing fixes are applied in **<10ms** (orders of magnitude faster than re-prompting)
- Token efficiency leads to better cost, latency, and accuracy

---

## 2. Syntax and Language Structure

### File Format

BAML files use the `.baml` extension and are stored in the `baml_src/` directory by convention.

### Basic Syntax Rules

- **No colons** between property names and types (unlike Python/TypeScript)
- **Block strings** use `#"..."#` delimiters for multi-line content
- **Comments** use `//` for single-line
- Property names must start with a letter and contain only letters, numbers, and underscores

### Block String Syntax

```baml
// Single-line string
"Hello, world!"

// Multi-line block string (automatically dedented)
#"
  This is a multi-line prompt.
  It will be automatically dedented.

  First and last newlines are stripped.
"#
```

### Generator Configuration

Generators define code generation targets:

```baml
generator target {
  output_type "python/pydantic"      // or "typescript", "ruby/sorbet", "go", etc.
  output_dir "../baml_client"        // Relative to baml_src/
  version "0.71.0"                   // Runtime version
  default_client_mode "async"        // or "sync"
  on_generate "black . && isort ."   // Post-generation commands
}
```

**Supported Output Types:**
- `python/pydantic` (latest) or `python/pydantic/v1` (legacy)
- `typescript` (Node.js) or `typescript/react` (React/Next.js)
- `ruby/sorbet` (beta)
- `go` (requires `client_package_name`)
- `rest/openapi` (API specification)

---

## 3. Type System

### Primitive Types

```baml
bool       // Boolean: true or false
int        // Integer numbers
float      // Floating-point numbers
string     // Text strings
null       // Null value
```

### Literal Types

Introduced in v0.61.0, primitives can be constrained to specific values:

```baml
function Classify(text: string) -> "bug" | "enhancement" | "question"
```

### Optional Types

Denote values that might be absent with `?`:

```baml
class User {
  name string
  email string?    // Optional field
  age int?
}
```

### Union Types

Allow multiple possible types using `|`:

```baml
// Order matters for parsing precedence!
// "1" parsed as int with this:
type IntOrString = int | string

// "1" parsed as string with this:
type StringOrInt = string | int
```

### List/Array Types

Collections of uniform types:

```baml
string[]           // Array of strings
int[][]            // 2D array of integers
Message[]          // Array of custom class
```

### Map Types

Key-value mappings (keys must be strings, enums, or literal strings):

```baml
map<string, int>              // String keys, int values
map<string, string[]>         // String keys, array values
map<Category, Product>        // Enum keys
```

### Type Aliases

Introduced in v0.71.0 for complex type simplification:

```baml
type GraphMap = map<string, string[]>
type Response = string | Error | null

// Recursive aliases supported through containers
type TreeNode = map<string, TreeNode>
```

### Multimodal Types

```baml
// Images
Image.from_url("https://example.com/image.png")
Image.from_base64("...")

// Audio
Audio.from_url("https://example.com/audio.mp3")
Audio.from_base64("...")

// PDFs (base64 only, no URL support)
Pdf.from_base64("...")

// Video
Video.from_url("https://example.com/video.mp4")
```

---

## 4. Enum Definitions

Enums define a set of named constants, ideal for classification tasks:

### Basic Enum

```baml
enum MessageType {
  SPAM
  NOT_SPAM
}
```

### Enum with Descriptions

```baml
enum TicketCategory {
  ACCOUNT
    @description("Issues related to user accounts, login, or profile")
  BILLING
    @description("Payment, subscription, or invoice related")
  TECHNICAL
    @description("Bug reports, errors, or technical problems")
  GENERAL_QUERY
    @description("General questions or information requests")
}
```

### Enum Attributes

- `@alias("name")` - Alternative name for LLM comprehension
- `@description("...")` - Context for the LLM
- `@skip` - Exclude from output schema
- `@@dynamic` - Allow runtime modifications

### Dynamic Enums

```baml
enum DynamicCategory {
  @@dynamic    // Values can be added at runtime
}
```

---

## 5. Class Definitions

Classes define complex data structures for inputs and outputs:

### Basic Class

```baml
class Resume {
  name string
  email string
  skills string[]
  experience Experience[]
}

class Experience {
  company string
  title string
  duration string
  description string?
}
```

### Class with Attributes

```baml
class Person {
  full_name string @alias("name") @description("The person's full legal name")
  birth_date string @alias("dob") @description("Date of birth in YYYY-MM-DD format")
  age int?
}
```

### Field Attributes

- `@alias("name")` - Rename field for LLM while preserving code name
- `@description("...")` - Contextual information for prompts

### Class Attributes

- `@@dynamic` - Allow runtime field additions

```baml
class FlexibleOutput {
  known_field string
  @@dynamic    // Additional fields can be added at runtime
}
```

### Constraints

- Default values are **not supported**
- Optional properties default to `None`/`null`
- Inheritance is **not supported** - use composition instead
- Recursive definitions are supported

---

## 6. Function Definitions

### Modern Function Syntax

Every BAML prompt is a function with parameters, return type, client, and prompt:

```baml
function ExtractResume(resume_text: string) -> Resume {
  client "openai/gpt-4o"
  prompt #"
    Extract the resume information from the following text.

    {{ ctx.output_format }}

    Resume:
    ---
    {{ resume_text }}
    ---
  "#
}
```

### Function with Complex Parameters

```baml
function ChatAgent(messages: Message[], tone: "happy" | "sad") -> string {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Be a {{ tone }} bot.

    {{ ctx.output_format }}

    {% for m in messages %}
    {{ _.role(m.role) }}
    {{ m.content }}
    {% endfor %}
  "#
}
```

### Function Components

1. **Name and Signature** - `function Name(params) -> ReturnType`
2. **Client** - Which LLM to use
3. **Prompt** - The template with Jinja syntax

### Classification Example

```baml
enum MessageType {
  SPAM
  NOT_SPAM
}

function ClassifyText(input: string) -> MessageType {
  client "openai/gpt-4o-mini"
  prompt #"
    Classify the following message as SPAM or NOT_SPAM.

    {{ ctx.output_format }}

    {{ _.role("user") }}
    {{ input }}
  "#
}
```

### Multi-label Classification

```baml
class TicketClassification {
  labels TicketLabel[]
}

function ClassifyTicket(ticket: string) -> TicketClassification {
  client "openai/gpt-4o-mini"
  prompt #"
    You are a support agent. Analyze the ticket and select all applicable labels.

    {{ ctx.output_format }}

    {{ _.role("user") }}
    {{ ticket }}
  "#
}
```

---

## 7. Client Configuration

### Shorthand Syntax

Quick configuration for common providers:

```baml
function MyFunc(input: string) -> string {
  client "openai/gpt-4o"           // Provider/model shorthand
  // or
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"..."#
}
```

### Named Client Configuration

Full configuration with custom options:

```baml
client<llm> MyOpenAI {
  provider "openai"
  options {
    model "gpt-4o"
    api_key env.OPENAI_API_KEY     // Default
    base_url "https://api.openai.com/v1"
    temperature 0.7
    max_tokens 2000
  }
}
```

### OpenAI Configuration

```baml
client<llm> GPT4o {
  provider "openai"
  options {
    model "gpt-4o"
    api_key env.MY_OPENAI_KEY      // Custom env var
    temperature 0.1

    // Role configuration
    default_role "user"
    allowed_roles ["system", "user", "assistant"]

    // Custom headers
    headers {
      "X-Custom-Header" "value"
    }
  }
}
```

### Anthropic Configuration

```baml
client<llm> Claude {
  provider "anthropic"
  options {
    model "claude-sonnet-4-20250514"
    api_key env.ANTHROPIC_API_KEY   // Default
    max_tokens 4096
    temperature 0

    // Enable prompt caching
    allowed_role_metadata ["cache_control"]
    headers {
      "anthropic-beta" "prompt-caching-2024-07-31"
    }
  }
}
```

### Supported Providers

| Provider | API Endpoint | Default API Key |
|----------|-------------|-----------------|
| `openai` | `/chat/completions` | `env.OPENAI_API_KEY` |
| `anthropic` | `/v1/messages` | `env.ANTHROPIC_API_KEY` |
| `google-ai` | Gemini endpoint | `env.GOOGLE_API_KEY` |
| `vertex-ai` | Vertex endpoint | Service account |
| `aws-bedrock` | Converse API | AWS credentials |
| `azure-openai` | Azure `/chat/completions` | `env.AZURE_OPENAI_KEY` |
| `openai-generic` | OpenAI-compatible | Custom |

### OpenAI-Generic for Other Providers

```baml
client<llm> Ollama {
  provider "openai-generic"
  options {
    model "llama2"
    base_url "http://localhost:11434/v1"
  }
}

client<llm> Together {
  provider "openai-generic"
  options {
    model "meta-llama/Llama-3-70b-chat-hf"
    base_url "https://api.together.xyz/v1"
    api_key env.TOGETHER_API_KEY
  }
}
```

---

## 8. Client Strategies

### Retry Policy

Configure automatic retries on failures:

```baml
retry_policy ExponentialBackoff {
  max_retries 3
  strategy {
    type "exponential_backoff"
    initial_interval_ms 500
    max_interval_ms 10000
    multiplier 2
  }
}

client<llm> ReliableGPT {
  provider "openai"
  retry_policy ExponentialBackoff
  options {
    model "gpt-4o"
  }
}
```

### Fallback Strategy

Chain multiple clients for resilience:

```baml
client<llm> GPT4 {
  provider "openai"
  options { model "gpt-4o" }
}

client<llm> Claude {
  provider "anthropic"
  options { model "claude-sonnet-4-20250514" }
}

client<llm> GPT35 {
  provider "openai"
  options { model "gpt-3.5-turbo" }
}

// Try GPT4 first, then Claude, then GPT-3.5
client<llm> ReliableClient {
  provider "fallback"
  retry_policy MyRetryPolicy   // Applied after all fallbacks fail
  options {
    strategy [
      GPT4
      Claude
      GPT35
    ]
  }
}
```

### Nested Fallbacks

```baml
client<llm> PremiumClients {
  provider "fallback"
  options {
    strategy [GPT4, Claude]
  }
}

client<llm> AllClients {
  provider "fallback"
  options {
    strategy [
      PremiumClients   // Try premium first
      GPT35            // Then fallback
    ]
  }
}
```

### Round-Robin Strategy

Distribute load across multiple clients:

```baml
client<llm> LoadBalanced {
  provider "round-robin"
  options {
    strategy [
      GPT4Instance1
      GPT4Instance2
      GPT4Instance3
    ]
  }
}
```

---

## 9. Template Strings (Jinja Syntax)

BAML uses Jinja2 templating for dynamic prompts.

### Variable Interpolation

```baml
prompt #"
  Process this text: {{ input_text }}

  User name: {{ user.name }}
  User email: {{ user.email }}
"#
```

### Context Variables

#### ctx.output_format

Injects the output schema into the prompt:

```baml
function Extract(text: string) -> Person {
  client "openai/gpt-4o"
  prompt #"
    Extract person information.

    {{ ctx.output_format }}

    Text: {{ text }}
  "#
}
```

**Customization options:**

```baml
{{ ctx.output_format(
  prefix="Respond in JSON matching this schema:",
  always_hoist_enums=true,
  or_splitter="|"
) }}
```

#### ctx.client

Access client metadata:

```baml
{% if ctx.client.provider == "anthropic" %}
  <Message>{{ content }}</Message>
{% else %}
  {{ content }}
{% endif %}
```

### Role Tags

Use `_.role()` to set message roles:

```baml
prompt #"
  {{ _.role("system") }}
  You are a helpful assistant.

  {{ _.role("user") }}
  {{ user_message }}
"#
```

### Loops

```baml
function ProcessMessages(messages: Message[]) -> string {
  client "openai/gpt-4o"
  prompt #"
    Process these messages:

    {% for message in messages %}
    {{ _.role(message.role) }}
    {{ message.content }}
    {% endfor %}
  "#
}
```

**Loop object properties:**

- `loop.index` / `loop.index0` - Current position (1-based / 0-based)
- `loop.first` / `loop.last` - Boolean checks
- `loop.length` - Total items
- `loop.previtem` / `loop.nextitem` - Adjacent items

### Conditionals

```baml
prompt #"
  {% if user.is_premium %}
    Premium support response:
  {% else %}
    Standard response:
  {% endif %}

  {{ ctx.output_format }}
"#
```

### Reusable Template Strings

Create reusable prompt components:

```baml
template_string FormatMessages(messages: Message[]) #"
  {% for message in messages %}
    {% if ctx.client.provider == "anthropic" %}
      <Message role="{{ message.role }}">{{ message.content }}</Message>
    {% else %}
      {{ message.role }}: {{ message.content }}
    {% endif %}
  {% endfor %}
"#

function Chat(messages: Message[]) -> string {
  client Claude
  prompt #"
    {{ FormatMessages(messages) }}

    {{ ctx.output_format }}
  "#
}
```

---

## 10. Testing

### Basic Test Structure

```baml
test TestExtraction {
  functions [ExtractResume]
  args {
    resume_text #"
      John Doe
      Email: john@example.com
      Skills: Python, TypeScript, BAML
    "#
  }
}
```

### Multiple Test Cases

```baml
test SpamTest {
  functions [ClassifyText]
  args {
    input "Click here to win $1000!!!"
  }
}

test NotSpamTest {
  functions [ClassifyText]
  args {
    input "Meeting at 3pm tomorrow"
  }
}
```

### Tests with Assertions

```baml
test TestWithAssert {
  functions [ClassifyText]
  args {
    input "Buy now! Limited offer!"
  }
  @@assert {{ this == "SPAM" }}
}
```

### Testing with Media

```baml
test ImageTest {
  functions [ExtractReceipt]
  args {
    image {
      file "../images/receipt.png"     // Relative to BAML file
    }
  }
}

test URLImageTest {
  functions [ExtractReceipt]
  args {
    image {
      url "https://example.com/receipt.png"
    }
  }
}
```

### Dynamic Types in Tests

```baml
test DynamicTest {
  functions [FlexibleExtract]
  args {
    input "Some text"
  }
  type_builder {
    dynamic class FlexibleOutput {
      custom_field string
    }
  }
}
```

---

## 11. Complete Example: Resume Parser

```baml
// Types
class Resume {
  name string
  email string?
  phone string?
  skills string[]
  experience Experience[]
  education Education[]
}

class Experience {
  company string
  title string
  start_date string
  end_date string?
  description string?
}

class Education {
  institution string
  degree string
  field string?
  graduation_year int?
}

// Client configuration
client<llm> GPT4o {
  provider "openai"
  options {
    model "gpt-4o"
    temperature 0
  }
}

// Function definition
function ExtractResume(resume_text: string) -> Resume {
  client GPT4o
  prompt #"
    You are an expert resume parser. Extract structured information from the resume below.

    Guidelines:
    - Extract all available information
    - Use null for missing optional fields
    - Format dates as "Month Year" (e.g., "January 2020")
    - List skills as individual items

    {{ ctx.output_format }}

    {{ _.role("user") }}
    Resume:
    ---
    {{ resume_text }}
    ---
  "#
}

// Test
test BasicResumeTest {
  functions [ExtractResume]
  args {
    resume_text #"
      Jane Smith
      jane.smith@email.com | (555) 123-4567

      SKILLS
      Python, TypeScript, Machine Learning, BAML, React

      EXPERIENCE
      Senior Engineer at TechCorp
      January 2020 - Present
      Led development of AI-powered features

      EDUCATION
      MIT - MS Computer Science, 2019
    "#
  }
}
```

---

## 12. Complete Example: Chatbot with Tools

```baml
// Message class
class Message {
  role "user" | "assistant"
  content string
}

// Tool definitions
class SearchTool {
  query string @description("The search query")
}

class CalculateTool {
  expression string @description("Mathematical expression to evaluate")
}

// Union type for tool selection
type Tool = SearchTool | CalculateTool | string

// Main function
function ChatWithTools(messages: Message[]) -> Tool {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    You are a helpful assistant with access to tools.

    Available tools:
    - SearchTool: Search the web for information
    - CalculateTool: Perform mathematical calculations
    - Or respond with a string if no tool is needed

    {{ ctx.output_format }}

    {% for m in messages %}
    {{ _.role(m.role) }}
    {{ m.content }}
    {% endfor %}
  "#
}

// Fallback client for reliability
client<llm> ReliableChatClient {
  provider "fallback"
  options {
    strategy [
      "anthropic/claude-sonnet-4-20250514"
      "openai/gpt-4o"
    ]
  }
}
```

---

## 13. Usage in Application Code

### Python

```python
from baml_client import b
from baml_client.types import Message

# Simple function call
result = b.ExtractResume(resume_text="John Doe...")
print(result.name)
print(result.skills)

# Chat with messages
messages = [
    Message(role="user", content="Hello!"),
    Message(role="assistant", content="Hi! How can I help?"),
    Message(role="user", content="What's the weather?")
]
response = b.ChatWithTools(messages)

# Streaming
async for partial in b.stream.ExtractResume(resume_text):
    print(partial)
```

### TypeScript

```typescript
import { b } from './baml_client';
import { Message } from './baml_client/types';

// Simple function call
const result = await b.ExtractResume({ resume_text: "John Doe..." });
console.log(result.name);
console.log(result.skills);

// Chat with messages
const messages: Message[] = [
  { role: "user", content: "Hello!" },
  { role: "assistant", content: "Hi! How can I help?" },
  { role: "user", content: "What's the weather?" }
];
const response = await b.ChatWithTools({ messages });

// Streaming
for await (const partial of b.stream.ExtractResume({ resume_text })) {
  console.log(partial);
}
```

---

## 14. Best Practices

### Prompt Engineering

1. **Always include `{{ ctx.output_format }}`** - Essential for structured outputs
2. **Use `_.role()` for chat models** - Properly format message roles
3. **Add descriptions to enums and classes** - Improves LLM understanding
4. **Use type aliases for complex types** - Improves readability

### Client Configuration

1. **Use fallback strategies in production** - Ensure reliability
2. **Configure retry policies** - Handle transient failures
3. **Set appropriate temperature** - Lower for extraction, higher for generation

### Testing

1. **Test edge cases** - Empty inputs, malformed data
2. **Test with real data samples** - Validate against actual use cases
3. **Use assertions** - Verify output structure and values

### Type Design

1. **Prefer composition over inheritance** - BAML doesn't support inheritance
2. **Use optionals for uncertain fields** - Mark with `?`
3. **Consider union types** - When output varies based on input
4. **Order union types carefully** - Parsing order matters

---

## 15. Summary

BAML revolutionizes prompt engineering by treating prompts as **typed functions**. Its key innovations include:

- **Schema Engineering** - Focus on precise input/output models
- **Multi-Language Support** - Single BAML definition, multiple language clients
- **SAP Algorithm** - Robust parsing for flexible LLM outputs
- **Token Efficiency** - 60% fewer tokens than JSON schemas
- **Production Features** - Retry, fallback, round-robin, streaming

BAML is ideal for:
- Structured data extraction
- Classification tasks
- Chatbots and conversational AI
- Tool-calling and function execution
- Any application requiring reliable, typed LLM outputs

---

## References

- **Official Documentation**: https://docs.boundaryml.com
- **GitHub Repository**: https://github.com/BoundaryML/baml
- **Examples Repository**: https://github.com/BoundaryML/baml-examples
- **Interactive Playground**: https://baml-examples.vercel.app


> Source: `docs/data_engineering/baml/baml-dlt-integration.md`

# BAML-dlt Integration: Schema-First AI Workflow Architecture

## Executive Summary

This document details the integration of BAML (Boundary AI Markup Language) with dlt (Data Load Tool) to create a unified schema architecture that bridges the gap between probabilistic LLM outputs and deterministic data systems. The approach treats BAML as the single source of truth, with generated Pydantic models driving dlt pipeline schema inference.

---

## 1. The Schema Engineering Paradigm

### 1.1 From Prompt Engineering to Schema Engineering

Traditional prompt engineering is brittle - a model update or slight input variation can break downstream parsers. BAML represents the maturation to "schema engineering":

| Approach | Method | Failure Mode |
|----------|--------|--------------|
| **Prompt Engineering** | Craft English instructions for JSON | Model variations break parsers |
| **JSON Schema Validation** | Runtime schema checking | Token-heavy, slow |
| **BAML Schema Engineering** | Compile-time type definition + SAP parsing | Fail-fast, deterministic |

BAML's **Schema-Aligned Parsing (SAP)** algorithm allows robust parsing of imperfect LLM outputs in milliseconds, eliminating costly retry loops.

### 1.2 Architecture Overview

```
BAML Definition (Single Source of Truth)
├── Python Layer
│   ├── Pydantic Models (validated)
│   ├── dlt Resources (schema hints)
│   └── Custom Destinations (FalkorDB, Graphiti)
└── TypeScript Layer
    ├── TypeScript Interfaces
    ├── Zod Schemas (ts-to-zod)
    └── TanStack AI Tools
```

---

## 2. Dual-Target Code Generation

### 2.1 generators.baml Configuration

```baml
// baml_src/generators.baml

// Generator 1: Python Data Layer
generator python_client {
  output_type "python/pydantic"
  output_dir "../backend/baml_client"
  version "0.76.2"
  default_client_mode "async"  // High-throughput dlt ingestion
}

// Generator 2: TypeScript Application Layer
generator typescript_client {
  output_type "typescript"
  output_dir "../frontend/src/baml_client"
  version "0.76.2"
  default_client_mode "async"
}
```

Every `baml-cli generate` execution creates two semantically identical but language-specific libraries.

### 2.2 Complex Entity Definitions

```baml
// baml_src/models.baml

enum EntityType {
  PERSON
  ORGANIZATION
  LOCATION
  CONCEPT
}

class IdentifiedEntity {
  name string @description("The canonical name of the entity")
  type EntityType
  confidence float
}

class ResearchInsight {
  id string @description("UUID")
  title string
  summary string
  entities IdentifiedEntity[]  // Nested objects for Graph extraction
  embedding_context string @description("Text used for vectorization")
  citations string[]
  published_date string
}

function ExtractInsight(text: string) -> ResearchInsight {
  client "openai/gpt-4o"
  prompt #"
    Analyze the following text and extract the research insight.
    Identify key entities and their types.

    {{ ctx.output_format }}

    Text:
    {{ text }}
  "#
}
```

The `@description` annotations become Pydantic field descriptions (usable by dlt) and JSDoc comments in TypeScript.

---

## 3. dlt Integration: BAML-to-Pipeline Bridge

### 3.1 Resource Definition with Pydantic Schema

dlt's native Pydantic introspection turns BAML-generated classes into "Schema Hints":

```python
import dlt
from typing import Iterator
from backend.baml_client import b
from backend.baml_client.types import ResearchInsight

@dlt.source
def research_source(texts: list[str]):

    @dlt.resource(
        name="research_insights",
        write_disposition="merge",
        primary_key="id",
        columns=ResearchInsight  # Pydantic model defines schema
    )
    def extract_insights() -> Iterator:
        for text in texts:
            # BAML call returns validated Pydantic object
            insight = b.ExtractInsight(text)
            yield insight

    return extract_insights
```

BAML's SAP ensures objects are valid before dlt sees them - "fail-fast" prevents schema pollution.

### 3.2 Multi-Database Ingestion Strategy

| Database | Integration Method | Use Case |
|----------|-------------------|----------|
| **PostgreSQL** | dlt native destination | Relational storage |
| **DuckDB** | dlt native destination | Analytical queries |
| **LanceDB** | dlt adapter | Vector similarity search |
| **FalkorDB** | Custom destination | Graph relationships |
| **Graphiti** | Custom destination | Temporal knowledge |

#### LanceDB Vector Integration

```python
from dlt.destinations.adapters import lancedb_adapter

def configure_lancedb_pipeline():
    source = research_source(["..."])

    # Specify which fields to embed
    lancedb_adapter(
        source.extract_insights,
        embed=["embedding_context", "summary"]
    )

    pipeline = dlt.pipeline(
        pipeline_name="vector_ingestion",
        destination="lancedb",
        dataset_name="research_vectors"
    )
    return pipeline
```

#### FalkorDB Custom Destination

```python
import dlt
from falkordb import FalkorDB

@dlt.destination(batch_size=50)
def falkordb_destination(items, table_schema):
    """Load BAML objects into FalkorDB graph."""
    client = FalkorDB(host='localhost', port=6379)
    graph = client.select_graph('KnowledgeGraph')

    for item in items:
        # Create Insight Node
        query_insight = """
        MERGE (i:Insight {id: $id})
        SET i.title = $title, i.summary = $summary
        """
        graph.query(query_insight, {
            'id': item['id'],
            'title': item['title'],
            'summary': item['summary']
        })

        # Create Entity Nodes and Relationships
        for entity in item.get('entities', []):
            query_rel = """
            MATCH (i:Insight {id: $id})
            MERGE (e:Entity {name: $e_name})
            SET e.type = $e_type
            MERGE (i)-[:MENTIONS]->(e)
            """
            graph.query(query_rel, {
                'id': item['id'],
                'e_name': entity['name'],
                'e_type': entity['type']
            })
```

#### Graphiti Custom Destination

```python
from graphiti_core import Graphiti, EpisodeType
import asyncio

@dlt.destination(batch_size=10)
def graphiti_destination(items, table_schema):
    """Load data into Graphiti as temporal episodes."""
    async def _ingest_batch():
        client = Graphiti("falkor://localhost:6379")

        for item in items:
            await client.add_episode(
                name=f"insight_{item['id']}",
                episode_body=item,  # Pass entire Pydantic dict
                source=EpisodeType.json,
                source_description="BAML Extracted Research",
                reference_time=datetime.now()
            )

        await client.close()

    asyncio.run(_ingest_batch())
```

---

## 4. TypeScript Layer: BAML to Zod to TanStack

### 4.1 Automated Zod Generation

Since BAML generates TypeScript interfaces (not Zod schemas), bridge with `ts-to-zod`:

```json
{
  "scripts": {
    "generate:baml": "baml-cli generate",
    "generate:zod": "ts-to-zod --input ./src/baml_client/types.ts --output ./src/gen/zod.ts --skipValidation",
    "codegen": "npm run generate:baml && npm run generate:zod"
  }
}
```

### 4.2 TanStack AI Tool Integration

```typescript
import { toolDefinition } from '@tanstack/ai';
import { researchInsightSchema } from '../gen/zod';

export const saveInsightTool = toolDefinition({
  name: 'save_insight',
  description: 'Persists a validated research insight to the database.',
  inputSchema: researchInsightSchema,
  execute: async (insight) => {
    // 'insight' is fully typed as ResearchInsight
    console.log(`Saving insight: ${insight.title}`);
    return { success: true, id: insight.id };
  },
});
```

### 4.3 oRPC Integration

```typescript
import { os } from '@orpc/server';
import { researchInsightSchema } from '../gen/zod';
import { db } from '../db/drizzle';
import { insightsTable } from '../db/schema';

export const appRouter = os.router({
  submitInsight: os.procedure
    .input(researchInsightSchema)
    .handler(async ({ input }) => {
      await db.insert(insightsTable).values({
        id: input.id,
        title: input.title,
        summary: input.summary,
        publishedDate: input.published_date,
        entities: input.entities  // Store as JSONB
      });
      return { status: 'stored' };
    }),
});
```

---

## 5. Schema Evolution Workflow

### 5.1 Adding a New Field

**Step 1: Update BAML**
```baml
class ResearchInsight {
  // ...existing fields
  author string? @description("Primary author name")  // NEW
}
```

**Step 2: Run Codegen**
```bash
npm run codegen  # baml-cli generate && ts-to-zod
```

**Step 3: dlt Auto-Evolution**
On next pipeline run, dlt detects the new `author` field in Pydantic model and automatically performs `ALTER TABLE` on PostgreSQL.

**Step 4: Frontend Updates**
TypeScript compiler flags any handlers that need updating. Zod schema includes `.optional()` for backward compatibility.

---

## 6. Feature Matrix

| Component | Role | BAML Integration | Validation Timing |
|-----------|------|------------------|-------------------|
| **dlt (Core)** | Pipeline Orchestrator | Pydantic Model (Direct) | Runtime (Schema Contract) |
| **PostgreSQL** | Relational Store | dlt Native | Write-Time (DB Constraints) |
| **LanceDB** | Vector Store | dlt Adapter | Write-Time (Schema Check) |
| **FalkorDB** | Graph Store | Custom Destination | Write-Time (Graph Logic) |
| **Graphiti** | Agent Memory | Custom Destination | Ingestion-Time |
| **TanStack AI** | Tool Definitions | Zod (via ts-to-zod) | Generation-Time (LLM output) |
| **oRPC** | API RPC | Zod (via ts-to-zod) | Request-Time (API Boundary) |

---

## 7. Performance Considerations

### 7.1 Token Efficiency

BAML reduces prompt size by up to 40% compared to verbose JSON Schema, improving latency and cost.

### 7.2 Async Pipeline Architecture

Writing to multiple databases introduces latency. Recommended pattern:

```python
async def process_document(text):
    # Phase 1: BAML extraction (background worker)
    insight = await b.ExtractInsight(text)

    # Phase 2: Parallel database writes
    await asyncio.gather(
        postgres_pipeline.load(insight),
        lancedb_pipeline.load(insight),
        graphiti_client.add_episode(insight)
    )

    return insight
```

### 7.3 Latency vs Throughput

- BAML extraction should occur in background workers (Celery/Temporal)
- Frontend should use optimistic UI patterns
- Use dlt's asyncio features for extraction parallelism
- Serialize/batch loading phase to avoid rate limits

---

## 8. Implementation Priorities

### Phase 1: Schema Foundation
1. Define BAML schemas for core data entities
2. Configure dual-target code generation (Python/TypeScript)
3. Set up dlt pipelines with Pydantic schema hints

### Phase 2: Multi-Database Integration
1. Configure native destinations (PostgreSQL, LanceDB)
2. Implement custom destinations (FalkorDB, Graphiti)
3. Set up ts-to-zod automation

### Phase 3: Frontend Integration
1. Integrate Zod schemas with TanStack AI tools
2. Configure oRPC with BAML-derived schemas
3. Implement schema evolution workflow

---

## References

- BAML Documentation: https://docs.boundaryml.com
- dlt Resources: https://dlthub.com/docs/general-usage/resource
- LanceDB Adapter: https://dlthub.com/docs/dlt-ecosystem/destinations/lancedb
- ts-to-zod: https://github.com/fabien0102/ts-to-zod
- TanStack AI: https://github.com/TanStack/ai


> Source: `docs/data_engineering/baml/document-processing-pipeline.md`

# Document Processing Pipeline for Cryptocurrency Analytics

## Overview

This document describes the pipeline for processing cryptocurrency documents (whitepapers, audits, research reports) and extracting structured knowledge for the knowledge graph.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Document Processing Pipeline                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │ Discovery│───>│Extraction│───>│Cognify   │───>│ Export   │      │
│  │ (Crawl4AI)│   │ (Marker) │    │(Cognee)  │    │(Graph+Vec)│     │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘      │
│       │               │               │               │              │
│       ▼               ▼               ▼               ▼              │
│  URLs, PDFs      Markdown +     Entities +      Memgraph +          │
│  HTML pages      Structure      Relations       LanceDB              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Stage 1: Document Discovery

### Crawl4AI Integration

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy

async def discover_protocol_documents(protocol_name: str) -> list[dict]:
    """Discover documentation URLs for a protocol"""

    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1280,
        viewport_height=720
    )

    crawler_config = CrawlerRunConfig(
        word_count_threshold=100,
        extraction_strategy=LLMExtractionStrategy(
            provider="openai/gpt-4o-mini",
            schema={
                "type": "object",
                "properties": {
                    "documents": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "url": {"type": "string"},
                                "doc_type": {"type": "string"},
                                "description": {"type": "string"}
                            }
                        }
                    }
                }
            },
            instruction=f"Find all documentation links for {protocol_name} including whitepapers, audits, risk reports, and technical documentation."
        )
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=f"https://docs.{protocol_name.lower()}.fi/",
            config=crawler_config
        )
        return result.extracted_content
```

### Document Source Registry

From `crypto_sources.json`, document sources include:

| Source ID | Type | URL Pattern |
|-----------|------|-------------|
| `ethena_docs_reserve_fund_pdf` | PDF | docs.ethena.fi |
| `ethena_audits_pdf_index` | PDF | docs.ethena.fi/security/audits |
| `pendle_v2_whitepaper_pdf` | PDF | Pendle repository |
| `chaoslabs_aave_emode_risk_pdf` | PDF | Chaos Labs website |
| `21shares_pendle_onepager_pdf` | PDF | 21Shares research |

## Stage 2: Content Extraction

### PDF Extraction with Marker

Using Marker for high-quality PDF extraction (10x faster than Nougat, preserves LaTeX):

```python
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict

def extract_pdf_content(pdf_path: str) -> dict:
    """Extract structured content from PDF with math preservation"""

    models = create_model_dict()
    converter = PdfConverter(
        config={
            "preserve_latex": True,
            "extract_tables": True,
            "extract_images": True
        }
    )

    result = converter(pdf_path, models)

    return {
        "markdown": result.markdown,
        "metadata": result.metadata,
        "images": result.images,
        "tables": result.tables,
        "math_blocks": extract_math_blocks(result.markdown)
    }

def extract_math_blocks(markdown: str) -> list[dict]:
    """Extract LaTeX math expressions for preservation"""
    import re

    patterns = [
        (r'\$\$(.+?)\$\$', 'display'),
        (r'\$(.+?)\$', 'inline'),
        (r'\\begin\{equation\}(.+?)\\end\{equation\}', 'equation')
    ]

    blocks = []
    for pattern, math_type in patterns:
        for match in re.finditer(pattern, markdown, re.DOTALL):
            blocks.append({
                "content": match.group(1),
                "type": math_type,
                "position": match.start()
            })
    return blocks
```

### HTML Extraction for Web Pages

```python
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup

async def extract_html_content(url: str) -> dict:
    """Extract content from HTML documentation pages"""

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)

        # Parse with BeautifulSoup for additional structure
        soup = BeautifulSoup(result.html, 'html.parser')

        return {
            "markdown": result.markdown,
            "title": soup.title.string if soup.title else None,
            "headings": extract_headings(soup),
            "links": extract_links(soup, url),
            "tables": extract_tables(soup),
            "code_blocks": result.code_blocks
        }

def extract_headings(soup) -> list[dict]:
    """Extract document structure from headings"""
    headings = []
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4']):
        headings.append({
            "level": int(tag.name[1]),
            "text": tag.get_text(strip=True),
            "id": tag.get('id')
        })
    return headings
```

## Stage 3: LLM-Based Structured Extraction

### BAML Schema for Crypto Documents

```baml
// baml_src/crypto_document.baml

class CryptoDocument {
  title string
  doc_type "whitepaper" | "audit" | "research" | "governance" | "risk_report"
  protocol string
  summary string @description("2-3 sentence summary of the document")

  // Extracted sections
  tokenomics Tokenomics?
  governance Governance?
  risks Risk[]
  mechanisms Mechanism[]
  audit_findings AuditFinding[]

  // Metadata
  published_date string?
  authors string[]
  version string?
}

class Tokenomics {
  token_symbol string
  total_supply string
  distribution Distribution[]
  vesting_schedule string?
  inflation_rate string?
}

class Distribution {
  category string @description("e.g., 'Team', 'Treasury', 'Public Sale'")
  percentage float
  vesting_period string?
}

class Governance {
  model "token_voting" | "multisig" | "council" | "hybrid"
  voting_token string?
  quorum_requirement string?
  timelock_period string?
  key_powers string[] @description("What can governance change?")
}

class Risk {
  category "smart_contract" | "market" | "regulatory" | "custody" | "oracle" | "governance" | "economic"
  severity "critical" | "high" | "medium" | "low"
  title string
  description string
  mitigation string?
  likelihood string?
}

class Mechanism {
  name string
  description string
  components string[]
  dependencies string[] @description("External protocols or oracles required")
}

class AuditFinding {
  auditor string
  severity "critical" | "high" | "medium" | "low" | "informational"
  title string
  description string
  location string? @description("Contract/function affected")
  status "resolved" | "acknowledged" | "disputed" | "open"
  recommendation string?
}

function ExtractCryptoDocument(content: string) -> CryptoDocument {
  client "anthropic/claude-sonnet-4-20250514"

  prompt #"
    Analyze this cryptocurrency/DeFi document and extract structured information.

    Document content:
    {{ content }}

    Extract all relevant information including:
    - Document type and basic metadata
    - Tokenomics details if present
    - Governance structure if described
    - Risk factors mentioned
    - Technical mechanisms explained
    - Audit findings if this is an audit report

    Be precise with numbers and percentages. Include direct quotes for important claims.
  "#
}
```

### Extraction Pipeline

```python
from baml_client import b
from baml_client.types import CryptoDocument

async def extract_structured_content(
    content: str,
    doc_type: str,
    source_url: str
) -> CryptoDocument:
    """Extract structured content using BAML"""

    # Truncate if too long (respect context limits)
    max_chars = 100000
    if len(content) > max_chars:
        content = truncate_intelligently(content, max_chars)

    # Run BAML extraction
    result = await b.ExtractCryptoDocument(content)

    # Add provenance
    result.source_url = source_url
    result.extraction_timestamp = datetime.now().isoformat()

    return result

def truncate_intelligently(content: str, max_chars: int) -> str:
    """Truncate while preserving document structure"""

    # Prioritize sections: summary, tokenomics, risks, findings
    priority_patterns = [
        r'(?i)(executive\s+summary|abstract|overview)',
        r'(?i)(tokenomics|token\s+distribution)',
        r'(?i)(risk|security)',
        r'(?i)(finding|issue|vulnerability)',
        r'(?i)(governance|voting)'
    ]

    # Keep matching sections, trim middle content
    # ... implementation details
    return truncated_content
```

## Stage 4: Knowledge Graph Construction (Cognee)

### Cognee ECL Pipeline

```python
import cognee
from cognee.api.v1.cognify import cognify
from cognee.api.v1.add import add

async def build_document_knowledge_graph(
    documents: list[CryptoDocument]
) -> None:
    """Process documents through Cognee ECL pipeline"""

    # Configure backends
    cognee.config.set_graph_database(
        type="memgraph",
        host="localhost",
        port=7687
    )
    cognee.config.set_vector_database(
        type="lancedb",
        path="./data/vectors"
    )

    for doc in documents:
        # E: Extract - Add document content
        await add(
            data=doc.model_dump_json(),
            dataset_name=f"{doc.protocol}_docs"
        )

    # C: Cognify - Build knowledge graph
    await cognify()

    # Graph is now populated with:
    # - Entity nodes (Token, Protocol, Risk, Mechanism)
    # - Relationship edges (DESCRIBES, CONTAINS, MITIGATES)
    # - Vector embeddings in LanceDB for semantic search
```

### Custom Entity Extraction

```python
from cognee.modules.data.extraction import extract_entities_with_llm

async def extract_crypto_entities(content: str) -> list[dict]:
    """Extract crypto-specific entities"""

    entity_types = [
        "Token",
        "Protocol",
        "Exchange",
        "SmartContract",
        "Wallet",
        "Risk",
        "Mechanism",
        "Auditor"
    ]

    entities = await extract_entities_with_llm(
        content=content,
        entity_types=entity_types,
        llm_model="gpt-4o-mini"
    )

    # Post-process: normalize addresses, validate symbols
    for entity in entities:
        if entity["type"] == "Token":
            entity["symbol"] = entity["name"].upper()
        if entity["type"] == "SmartContract":
            entity["address"] = normalize_address(entity.get("address"))

    return entities
```

## Stage 5: Export to Graph & Vector Stores

### Memgraph Export

```python
from neo4j import GraphDatabase

def export_to_memgraph(
    documents: list[CryptoDocument],
    entities: list[dict],
    relationships: list[dict]
):
    """Export extracted knowledge to Memgraph"""

    driver = GraphDatabase.driver("bolt://localhost:7687")

    with driver.session() as session:
        # Create document nodes
        for doc in documents:
            session.run("""
                MERGE (d:Document {url: $url})
                SET d.title = $title,
                    d.doc_type = $doc_type,
                    d.protocol = $protocol,
                    d.summary = $summary,
                    d.published_date = $published_date
            """, **doc.model_dump())

        # Create entity nodes
        for entity in entities:
            session.run(f"""
                MERGE (e:{entity['type']} {{id: $id}})
                SET e += $properties
            """, id=entity['id'], properties=entity)

        # Create relationships
        for rel in relationships:
            session.run(f"""
                MATCH (a {{id: $from_id}})
                MATCH (b {{id: $to_id}})
                MERGE (a)-[r:{rel['type']}]->(b)
                SET r += $properties
            """, **rel)
```

### LanceDB Vector Export

```python
import lancedb
from sentence_transformers import SentenceTransformer

def export_to_lancedb(documents: list[CryptoDocument]):
    """Export document embeddings to LanceDB"""

    model = SentenceTransformer('all-MiniLM-L6-v2')
    db = lancedb.connect("./data/vectors")

    # Prepare data with embeddings
    data = []
    for doc in documents:
        # Chunk document for better retrieval
        chunks = chunk_document(doc.summary + "\n" + doc.content)

        for i, chunk in enumerate(chunks):
            embedding = model.encode(chunk)
            data.append({
                "id": f"{doc.url}_{i}",
                "text": chunk,
                "vector": embedding,
                "doc_url": doc.url,
                "doc_type": doc.doc_type,
                "protocol": doc.protocol
            })

    # Upsert to LanceDB
    table = db.create_table("crypto_docs", data, mode="overwrite")

    # Create IVF-PQ index for fast search
    table.create_index(
        metric="L2",
        num_partitions=256,
        num_sub_vectors=96
    )
```

## Orchestration with Dagster

### Document Pipeline Assets

```python
from dagster import asset, AssetExecutionContext, MaterializeResult

@asset(
    description="Discover and index protocol documentation",
    compute_kind="crawl4ai",
    group_name="documents"
)
async def discover_documents(context: AssetExecutionContext) -> list[dict]:
    """Discover documentation URLs for all tracked protocols"""

    protocols = ["ethena", "aave", "pendle", "compound", "uniswap"]
    all_docs = []

    for protocol in protocols:
        docs = await discover_protocol_documents(protocol)
        all_docs.extend(docs)
        context.log.info(f"Found {len(docs)} documents for {protocol}")

    return all_docs

@asset(
    deps=["discover_documents"],
    description="Extract content from discovered documents",
    compute_kind="marker"
)
async def extract_documents(
    context: AssetExecutionContext,
    discover_documents: list[dict]
) -> list[dict]:
    """Extract content from PDFs and HTML pages"""

    extracted = []
    for doc in discover_documents:
        if doc["url"].endswith(".pdf"):
            content = extract_pdf_content(doc["url"])
        else:
            content = await extract_html_content(doc["url"])

        extracted.append({
            **doc,
            "content": content
        })

    return extracted

@asset(
    deps=["extract_documents"],
    description="Apply LLM extraction to get structured data",
    compute_kind="baml"
)
async def structure_documents(
    context: AssetExecutionContext,
    extract_documents: list[dict]
) -> list[CryptoDocument]:
    """Extract structured information using BAML"""

    structured = []
    for doc in extract_documents:
        result = await extract_structured_content(
            content=doc["content"]["markdown"],
            doc_type=doc["doc_type"],
            source_url=doc["url"]
        )
        structured.append(result)

    return structured

@asset(
    deps=["structure_documents"],
    description="Build knowledge graph from structured documents",
    compute_kind="cognee"
)
async def build_knowledge_graph(
    context: AssetExecutionContext,
    structure_documents: list[CryptoDocument]
) -> MaterializeResult:
    """Process through Cognee and export to Memgraph + LanceDB"""

    await build_document_knowledge_graph(structure_documents)
    export_to_lancedb(structure_documents)

    return MaterializeResult(
        metadata={
            "documents_processed": len(structure_documents),
            "graph_nodes": count_graph_nodes(),
            "vector_count": count_vectors()
        }
    )
```

## Quality Assurance

### Document Quality Checks

```python
from dagster import asset_check, AssetCheckResult

@asset_check(asset=structure_documents)
def check_extraction_quality(structure_documents: list[CryptoDocument]) -> AssetCheckResult:
    """Verify extraction quality meets thresholds"""

    issues = []
    for doc in structure_documents:
        quality = CryptoDocumentQuality().score(doc.model_dump())
        if quality < 0.6:
            issues.append(f"{doc.title}: quality score {quality:.2f}")

    return AssetCheckResult(
        passed=len(issues) == 0,
        severity="WARN",
        metadata={
            "low_quality_documents": issues,
            "total_documents": len(structure_documents)
        }
    )
```

## References

- Marker PDF extraction: https://github.com/VikParuchuri/marker
- Crawl4AI documentation: https://crawl4ai.com
- Cognee ECL pipeline: https://github.com/topoteretes/cognee
- BAML documentation: https://docs.boundaryml.com


> Source: `docs/data_engineering/baml/Structured Outputs Create False Confidence.md`

---
title: "Structured Outputs Create False Confidence"
source: "https://boundaryml.com/blog/structured-outputs-create-false-confidence"
author:
  - "[[Sam Lijin]]"
published: December 14
created: 2025-12-16
description: "Constrained decoding seems like the greatest thing since sliced bread, but it forces models to prioritize output conformance over output quality."
tags:
  - "clippings"
---
Engineering about 23 hours ago 7 min read

Constrained decoding seems like the greatest thing since sliced bread, but it forces models to prioritize output conformance over output quality.

![Sam Lijin](https://boundaryml.com/_next/image?url=%2Fprofile-sam.png&w=1080&q=75)

Sam Lijin

If you use LLMs, you've probably heard about structured outputs. You might think they're the greatest thing since sliced bread. Unfortunately, **structured outputs also degrade response quality**.

Specifically, if you use an LLM provider's structured outputs API, you will get a lower quality response than if you use their normal text output API:

- ⚠️ you're more likely to make mistakes when extracting data, even in simple cases;
- ⚠️ you're probably not modeling errors correctly;
- ⚠️ it's harder to use techniques like chain-of-thought reasoning; and
- ⚠️ in the extreme case, it can be easier to steal your customer data using prompt injection.

These are very contentious claims, so let's start with an example: extracting data from a receipt.

![Receipt with fractional quantities](https://boundaryml.com/receipt-fractional-quantity.jpg)

If I use an LLM to extract the receipt entries, it should be able to tell me that one of the items is `(name="banana", quantity=0.46)`, right?

Well, using OpenAI's structured outputs API with `gpt-5.2` - released literally this week! - it will claim that the banana quantity is `1.0`:

```
{
  "establishment_name": "PC Market of Choice",
  "date": "2007-01-20",
  "total": 0.32,
  "currency": "USD",
  "items": [
    {
      "name": "Bananas",
      "price": 0.32,
      "quantity": 1
    }
  ]
}
```

However, with the *same model*, if you just use the completions API and then parse the output, it will return the correct quantity:

```
{
  "establishment_name": "PC Market of Choice",
  "date": "2007-01-20",
  "total": 0.32,
  "currency": "USD",
  "items": [
    {
      "name": "Bananas",
      "price": 0.69,
      "quantity": 0.46
    }
  ]
}
```
Click here to see the code that was used to generate the above outputs.

This code is also [available on GitHub](https://gist.github.com/sxlijin/867b812ceb1aa97872937bebe5cfb4be).

```
#!/usr/bin/env -S uv run

# /// script

# requires-python = ">=3.10"

# dependencies = ["openai", "pydantic", "rich"]

# ///

"""

If you have uv, you can run this code by saving it as structured_outputs_quality_demo.py and then running:

  chmod u+x structured_outputs_quality_demo.py

  ./structured_outputs_quality_demo.py

This script is a companion to https://boundaryml.com/blog/structured-outputs-create-false-confidence

"""

import json

import re

from openai import OpenAI

from pydantic import BaseModel, Field

from rich.console import Console

from rich.pretty import Pretty

class Item(BaseModel):

    name: str

    price: float = Field(description="per-unit item price")

    quantity: float = Field(default=1, description="If not specified, assume 1")

class Receipt(BaseModel):

    establishment_name: str

    date: str = Field(description="YYYY-MM-DD")

    total: float = Field(description="The total amount of the receipt")

    currency: str = Field(description="The currency used for everything on the receipt")

    items: list[Item] = Field(description="The items on the receipt")

client = OpenAI()

console = Console()

def run_receipt_extraction_structured(image_url: str):

    """Call the LLM to extract receipt data from an image URL and return the raw response."""

    prompt_text = (

        """

Extract data from the receipt.

"""

    )

    response = client.beta.chat.completions.parse(

        model="gpt-5.2-2025-12-11",

        messages=[

            {

                "role": "system",

                "content": "You are a precise receipt extraction engine. Return only structured data matching the Receipt schema.",

            },

            {

                "role": "user",

                "content": [

                    {

                        "type": "text",

                        "text": prompt_text,

                    },

                    {"type": "image_url", "image_url": {"url": image_url}},

                ],

            },

        ],

        response_format=Receipt,

    )

    return response.choices[0].message.content, response.choices[0].message.parsed

def run_receipt_extraction_freeform(image_url: str):

    """Call the LLM to extract receipt data from an image URL and return the raw response."""

    prompt_text = (

        """

Extract data from the receipt.

Explain your reasoning, then answer in JSON:

{

  establishment_name: string,

  // YYYY-MM-DD

  date: string,

  // The total amount of the receipt

  total: float,

  // The currency used for everything on the receipt

  currency: string,

  // The items on the receipt

  items: [

    {

      name: string,

      // per-unit item price

      price: float,

      // If not specified, assume 1

      quantity: float,

    }

  ],

}

"""

    )

    response = client.beta.chat.completions.parse(

        model="gpt-5.2-2025-12-11",

        messages=[

            {

                "role": "user",

                "content": [

                    {

                        "type": "text",

                        "text": prompt_text,

                    },

                    {"type": "image_url", "image_url": {"url": image_url}},

                ],

            },

        ],

    )

    return response.choices[0].message.content, json.loads(re.search(r"\`\`\`json(.*?)\`\`\`", response.choices[0].message.content, flags=re.DOTALL).group(1))

def main() -> None:

    images = [

        {

            "title": "Parsing receipt: fractional quantity",

            "url": "https://boundaryml.com/receipt-fractional-quantity.jpg",

            "expected": "You should expect quantity to be 0.46."

        },

        {

            "title": "Parsing receipt: elephant",

            "url": "https://boundaryml.com/receipt-elephant.jpg",

            "expected": "You should expect an error."

        },

        {

            "title": "Parsing receipt: currency exchange",

            "url": "https://boundaryml.com/receipt-currency-exchange.jpg",

            "expected": "You should expect a warning about mixed currencies."

        },

    ]

    print("This is a demonstration of how structured outputs create false confidence.")

    for entry in images:

        title = entry["title"]

        url = entry["url"]

        completion_structured_content, _ = run_receipt_extraction_structured(url)

        completion_freeform_content, _ = run_receipt_extraction_freeform(url)

        console.print("[cyan]--------------------------------[/cyan]")

        console.print(f"[cyan]{title}[/cyan]")

        console.print(f"Asking LLM to parse receipt from {url}")

        console.print(entry['expected'])

        console.print()

        console.print("[cyan]Using structured outputs:[/cyan]")

        console.print(completion_structured_content)

        console.print()

        console.print("[cyan]Parsing free-form output:[/cyan]")

        console.print(completion_freeform_content)

if __name__ == "__main__":

    main()
```

Now, what happens if someone submits a picture of an elephant?

Or a currency exchange receipt?

![currency exchange receipt](https://boundaryml.com/receipt-currency-exchange.jpg)

In these scenarios, you want to let the LLM respond using text. You want it to be able to say that, hey, you're asking me to parse a receipt, but you gave me a picture of an elephant, I can't parse an elephant into a receipt.

If you force the LLM to respond using structured outputs, you take that ability away from the LLM. Sure, you'll get an object that satisfies your output format, but it'll be meaningless. It's like when you file a bug report, and the form has 5 mandatory fields about things that have nothing to do with your bug, but you have to put *something* in those fields to file the bug report: the stuff you put in those fields will probably be useless.

## I can design my output format better!

Yes and no.

Yes, you can tell your LLM to return `{ receipt data } or { error }`. But what kinds of errors are you going to ask it to consider?

- What kind of error should it return if there's no `total` listed on the receipt? Should it even return an error or is it OK for it to return `total = null`?
- What if it can successfully parse 7 of 8 items on the receipt, but it's not sure about the 8th item? Should it return (1) the 7 successfully parsed items and a partial parse of the 8th item, (2) only the 7 successfully parsed items and discard the 8th or (3) fail parsing entirely?
- What if someone submits a picture of an elephant? What kind of error should be returned in that case?

In addition, as you start enumerating all of these errors, you run into the [pink elephant problem](https://arxiv.org/abs/2402.07896): the more your prompt talks about errors, the more likely the LLM is to respond with an error.

Think of it this way: if someone presses Ctrl-C when running your binary, it is a Good Thing that the error can propagate all the way up through your binary, without you having to explicitly write `try { ... } catch CtrlCError { ... }` in every function in your codebase.

In the same way that you often want to allow errors to just propagate up while writing software, and only explicitly handle *some* errors, your LLM should be allowed to respond with errors in whatever fashion it wants to.

## Chain-of-thought is crippled by structured outputs

"Explain your reasoning step by step" is a magic incantation that seemingly makes LLMs much smarter. It also turns out that this trick doesn't work nearly as well when using structured outputs, and [we've known this since Aug 2024](https://arxiv.org/abs/2408.02442).

To understand this finding, the intuition I like to use, is to think of every model of having an intelligence "budget", and that if you try to force an LLM to reason in a very specific format, you're making the LLM spend intelligence points on useless work.

To make this more concrete, let's use another example. If you prompt an LLM to give you JSON output and reason about it step-by-step, its response will look something like this:

```
If we think step by step we can see that:

1. The email is from Amazon, confirming the status of a specific order.
2. The subject line says "Your Amazon.com order of 'Wood Dowel Rods...' has shipped!" which indicates that the order status is 'SHIPPED'.
3. [...]

Combining all these points, the output JSON is:

\`\`\`json
{
     "order_status": "SHIPPED",
     [...]
}
\`\`\`
```

Notice that although the response contains valid JSON, the response itself is not valid JSON, because of the reasoning text at the start. In other words, you can't use basic chain-of-thought reasoning with structured outputs.

You *could* modify your schema, and add `reasoning: string` fields to your output schema, and let the LLM respond with something like this:

```
{
  "reasoning": "If we think step by step we can see that:\n\n 1. The email is from Amazon, confirming the status of a specific order.\n2. The subject line says \"Your Amazon.com order of 'Wood Dowel Rods...' has shipped!\" [...]
  ...
}
```

In other words, if you're using a `reasoning` field with structured outputs, instead of simply asking the LLM to reason about its answer, you're also forcing it to escape newlines and quotes and format that correctly as JSON. You're basically asking the LLM to [put a cover page on its TPS report](https://www.youtube.com/watch?v=jsLUidiYm0w&t=19s).

## Why are structured outputs bad?

(To understand this section, you'll need a bit of background on [transformer models](https://www.3blue1brown.com/lessons/gpt#what-exactly-is-a-transformer), specifically how [logit sampling](https://github.com/karpathy/nanoGPT/blob/3adf61e154c3fe3fca428ad6bc3818b27a3b8291/model.py#L323-L328) works. Feel free to skip this section if you don't have this background.)

Model providers like OpenAI and Anthropic implement structured outputs using a technique called [constrained decoding](https://openai.com/index/introducing-structured-outputs-in-the-api/#constrained-decoding):

> By default, when models are sampled to produce outputs, they are entirely unconstrained and can select any token from the vocabulary as the next output. This flexibility is what allows models to make mistakes; for example, they are generally free to sample a curly brace token at any time, even when that would not produce valid JSON. In order to force valid outputs, we constrain our models to only tokens that would be valid according to the supplied schema, rather than all available tokens.

In other words, constrained decoding applies a filter during sampling that says, OK, given the output that you've produced so far, you're only allowed to consider certain tokens.

For example, if the LLM has so far produced `{"quantity": 51`, and you're constraining output decoding to satisfy `{ quantity: int, ... }`:

- `{"quantity": 51.2` would not satisfy the constraint, so `.2` is not allowed to be the next token,
- `{"quantity": 51,` would satisfy the constraint, so `,` is allowed to be the next token,
- `{"quantity": 510` would satisfy the constraint, so `0` is allowed to be the next token (albeit, in this example, with low probability!),

But if the LLM actually wants to answer with `51.2` instead of `51`, it isn't allowed to, because of our constraint!

Sure, if you're using constrained decoding to force it to return `{"quantity": 51.2}` instead of `{"quantity": 51.2,}` - because trailing commas are not allowed in JSON - it'll probably do the right thing. But that's something you can write code to handle, which leads me to my final point.

## Just parse the output

OK, so if structured outputs are bad, then what's the solution?

It turns out to be really simple: let the LLM do what it's trained to do. Allow it to respond in a free-form style:

- let it [refuse to count](https://chatgpt.com/share/691ac9b7-47a0-800a-a9a7-c0302f463168) the number of entries in a list
- let it [warn you](https://chatgpt.com/share/693f1edb-1c54-800a-8b4b-db146f856b0c) when you've given it contradictory information
- let it [tell you the correct approach](https://chatgpt.com/share/693f1cd0-6a20-800a-aca9-09599216badf) when you inadvertently ask it to use the wrong approach

Using structured outputs, via constrained decoding, makes it much harder for the LLM to do any of this. Even though you've crafted a guarantee that the LLM will return a response in exactly your requested output format, that guarantee comes at the cost of the *quality* of that response, because you're forcing the LLM to prioritize complying with your output format over returning a high-quality response. That's why structured outputs create false confidence: it's entirely non-obvious that you're sacrificing output quality to achieve output conformance.

Parsing the LLM's free-form output, by contrast, enables you to retain that output quality.

(In a scenario where an attacker is trying to convince your agent to do something you didn't design it to do, the parsing also serves as an effective defense-in-depth layer against malicious prompt injection.)

This is [why BAML - our open-source, local-only DSL - uses schema-aligned parsing](https://docs.boundaryml.com/guide/introduction/why-baml#3-schema-aligned-parsing-sap): we believe letting the LLM respond in as natural a fashion as possible is the most effective way to get the highest quality response from it.

> Source: `docs/data_engineering/baml/extract-anything/README.md`

# Extract Anything

BAML can be leveraged to build a pipeline that can extract anything
without knowing the schema in advance.

This is done via 2 steps:

1. Ask an LLM to describe a schema that could represent the content of the document.

2. Use the schema to extract the content by leveraging dyanmic types.

## Architecture

Backend is python + FASTAPI + BAML

Frontend is React

We try and stream whatever possible!

```bash
# Start the backend
cd backend
uv run fastapi run server.py --reload

```

```bash
# Start the frontend
cd frontend
pnpm dev
```


# Part 2: Cognee — AI Memory Platform


> Source: `docs/data_engineering/cognee/cognee.md`

---
name: cognee
description: Creating and developing AI memory systems with Cognee. Use when working with knowledge graphs, semantic search, or building persistent AI agent memory. (project, ai-memory)
category: AI Memory
tags: [cognee, knowledge-graph, rag, vector-search, graph-database, ai-memory]
---

# Cognee AI Memory Expert

You are an expert in using Cognee, an open-source AI memory platform that transforms raw data into persistent, dynamic memory for AI agents.

## Core Capabilities

When users request help with Cognee, you should assist with:

### 1. Setup and Configuration

```python
import cognee
import os

# LLM Configuration
os.environ["LLM_API_KEY"] = "your-api-key"
await cognee.config.set_llm_provider("openai")
await cognee.config.set_llm_model("gpt-4o-mini")

# Graph Database Configuration
await cognee.config.set_graph_database_provider("neo4j")
await cognee.config.set_graph_database_url("bolt://localhost:7687")
await cognee.config.set_graph_database_username("neo4j")
await cognee.config.set_graph_database_password("password")

# Vector Database Configuration
await cognee.config.set_vector_database_provider("lancedb")
await cognee.config.set_vector_database_url("./lancedb_data")

# Embedding Configuration
await cognee.config.set_embedding_provider("openai")
await cognee.config.set_embedding_model("text-embedding-3-large")
```

### 2. ECL Pipeline (Extract-Cognify-Load)

The fundamental pattern for building AI memory:

```python
# Extract: Add data to cognee
await cognee.add(content, dataset_name="my_dataset")

# Cognify: Transform into knowledge graph
await cognee.cognify()

# Load: Automatically stored in configured databases
# Search: Query the knowledge graph
results = await cognee.search("Your question", query_type=SearchType.GRAPH_COMPLETION)
```

### 3. Data Ingestion Patterns

**Single Document:**
```python
await cognee.add("Your document text", dataset_name="docs")
```

**Multiple Documents:**
```python
documents = ["doc1", "doc2", "doc3"]
for doc in documents:
    await cognee.add(doc, dataset_name="knowledge_base")
await cognee.cognify()
```

**With Metadata:**
```python
# Primary content
await cognee.add(content, dataset_name="posts")

# Associated metadata
await cognee.add(metadata, dataset_name="post_metadata")

await cognee.cognify()
```

**File Upload:**
```python
with open("document.pdf", "rb") as f:
    await cognee.add(f, dataset_name="pdfs")
```

### 4. Search Strategies

Cognee provides multiple search types for different use cases:

```python
from cognee.api.v1.search import SearchType

# Semantic vector search (fast, similarity-based)
results = await cognee.search(
    query_text="find similar concepts",
    query_type=SearchType.CHUNKS
)

# Graph-based insights (relationship-aware)
results = await cognee.search(
    query_text="how are these concepts related",
    query_type=SearchType.INSIGHTS
)

# Hybrid search with LLM reasoning (most powerful)
results = await cognee.search(
    query_text="complex multi-hop question",
    query_type=SearchType.GRAPH_COMPLETION,
    top_k=5
)

# Document summaries (hierarchical)
results = await cognee.search(
    query_text="summarize the main themes",
    query_type=SearchType.SUMMARIES
)

# Code search (language-aware)
results = await cognee.search(
    query_text="authentication implementation",
    query_type=SearchType.CODE
)

# Direct graph queries (Cypher)
results = await cognee.search(
    query_text="MATCH (n:Entity) RETURN n",
    query_type=SearchType.CYPHER
)

# Automatic search type selection
results = await cognee.search(
    query_text="your question",
    query_type=SearchType.FEELING_LUCKY
)
```

### 5. Dataset Management

**Scoped Queries:**
```python
# Add to specific datasets
await cognee.add(data1, dataset_name='dataset_a')
await cognee.add(data2, dataset_name='dataset_b')

# Cognify all datasets
await cognee.cognify()

# Search specific dataset
results = await cognee.search(
    query_text="query",
    node_name="dataset_a",
    top_k=5
)
```

**Data Cleanup:**
```python
# Clear all data
await cognee.prune.prune_data()

# Full system reset
await cognee.prune.prune_system(metadata=True)

# Delete specific data
await cognee.delete(data_id)
```

### 6. Visualization

```python
# Generate static visualization
await cognee.visualize_graph('/path/to/graph_visualization.html')

# Start interactive visualization server
await cognee.start_visualization_server()

# Network visualization
await cognee.cognee_network_visualization()
```

### 7. Integration Patterns

**DLT Integration:**
```python
import dlt
import cognee

@dlt.resource(write_disposition="merge", primary_key="id")
def data_source():
    yield data

# Load with DLT
pipeline = dlt.pipeline(
    pipeline_name="cognee_pipeline",
    destination="duckdb"
)
pipeline.run(data_source())

# Process with Cognee
await cognee.add(data, dataset_name="dlt_dataset")
await cognee.cognify()
```

**LangGraph Integration:**
```python
from langgraph.graph import StateGraph
import cognee

# Use cognee as memory backend
async def retrieve_context(state):
    results = await cognee.search(state["query"])
    return {"context": results}

workflow = StateGraph(...)
workflow.add_node("memory", retrieve_context)
```

**MCP (Model Context Protocol):**
```python
from cognee import MCP

# Expose cognee as MCP server
cognee_server = MCP()
cognee_server.start()

# Available functions:
# - cognify: Transform text into knowledge graphs
# - save_interaction: Capture conversations
# - search: Multi-mode semantic search
# - list_data: Display stored datasets
# - delete: Remove specific data
# - prune: Full memory reset
```

### 8. Incremental Updates

```python
# Initial load
await cognee.add(initial_data, dataset_name="docs")
await cognee.cognify()

# Later: add new data incrementally
# Cognee intelligently updates the existing graph
await cognee.add(new_documents, dataset_name="docs")
await cognee.cognify()  # Only processes new/changed content
```

### 9. Advanced Patterns

**Batch Processing:**
```python
from cognee.modules.pipelines import Task

pipeline = [
    Task(name="extract", batch_size=100),
    Task(name="chunk", batch_size=50),
    Task(name="embed", batch_size=20),
    Task(name="extract_entities"),
    Task(name="build_graph"),
]
```

**Custom Ontologies:**
Cognee supports custom business ontologies for domain-specific entity extraction and relationship mapping through pipeline configuration.

**Distributed Processing:**
For large-scale deployments, use distributed Cognee for parallel dataset processing across multiple workers.

## Architecture Knowledge

### Three Knowledge Layers
1. **Raw Information Nodes**: Original document content
2. **Extracted Entities**: Concepts and objects identified
3. **Relationship Mappings**: Connections between entities

### Storage Systems

**Vector Stores** (semantic search):
- LanceDB (default, local)
- Qdrant Cloud
- PGVector (Postgres)
- Weaviate
- FalkorDB
- Redis

**Graph Databases** (relationships):
- KuzuDB (default, embedded)
- Neo4j
- Neptune (AWS)
- Memgraph
- NetworkX (in-memory)

**Relational** (metadata):
- PostgreSQL
- SQLite

### Knowledge Graph Ontology

**Node Types:**
- Entity Nodes: Concepts extracted from text
- Document Nodes: Source documents
- Chunk Nodes: Text segments with embeddings
- Metadata Nodes: Supplementary information

**Relationship Types:**
- `RELATIONSHIP`: Subject-Object connections
- `MENTION`: Document references entity
- `related_to`: General conceptual relationships
- `contains`: Hierarchical containment
- `hasClause`: Domain-specific

## Common Use Cases

1. **Conversational AI Memory**: Persistent context across chat sessions
2. **Document Q&A**: Transform documentation into queryable knowledge graphs
3. **Code Intelligence**: Semantic code search and understanding
4. **Research Analysis**: Knowledge discovery from large document sets
5. **Data Unification**: Consolidate scattered data silos
6. **Enterprise Search**: Precise, cited answers with sources
7. **Multi-Agent Memory**: Shared knowledge base for agent teams
8. **Vertical AI Agents**: Domain-specific copilots that learn

## Best Practices

1. **Use Datasets for Organization**: Group related content in named datasets
2. **Choose Right Search Type**: Use CHUNKS for speed, GRAPH_COMPLETION for depth
3. **Incremental Processing**: Add data incrementally rather than full reloads
4. **Async Operations**: All Cognee operations are async - use `await`
5. **Configure Before Adding**: Set up LLM and databases before ingesting data
6. **Clean Up Old Data**: Use `prune` commands to manage memory usage
7. **Visualize Graphs**: Use visualization tools to understand knowledge structure
8. **Batch Large Datasets**: Configure batch sizes for large data processing
9. **Monitor Performance**: Use `top_k` to limit result sets and improve speed
10. **Leverage MCP**: Use MCP integration for standardized AI agent access

## Troubleshooting

**Graph database connection fails:**
```python
# Verify configuration
await cognee.config.set_graph_database_url("bolt://localhost:7687")
await cognee.config.set_graph_database_username("neo4j")
await cognee.config.set_graph_database_password("password")
```

**Rate limiting from LLM provider:**
```python
# Reduce batch size
Task(name="embed", batch_size=10)
```

**High memory usage:**
```python
# Clear old data
await cognee.prune.prune_data()

# Or selectively delete
await cognee.delete(data_id)
```

**Search returns no results:**
```python
# Verify data was cognified
await cognee.cognify()

# Try different search type
results = await cognee.search(
    query_text="your question",
    query_type=SearchType.FEELING_LUCKY
)
```

## Environment Variables

```bash
# LLM Configuration
export LLM_API_KEY="your-openai-key"
export LLM_PROVIDER="openai"
export LLM_MODEL="gpt-4o-mini"

# Graph Database
export GRAPH_DATABASE_PROVIDER="neo4j"
export GRAPH_DATABASE_URL="bolt://localhost:7687"
export GRAPH_DATABASE_USERNAME="neo4j"
export GRAPH_DATABASE_PASSWORD="password"

# Vector Database
export VECTOR_DATABASE_PROVIDER="lancedb"
export VECTOR_DATABASE_URL="./lancedb_data"

# Embedding
export EMBEDDING_PROVIDER="openai"
export EMBEDDING_MODEL="text-embedding-3-large"
```

## Quick Reference

```python
import cognee
from cognee.api.v1.search import SearchType

# Setup
await cognee.config.set_llm_provider("openai")
await cognee.config.set_llm_api_key("your-key")

# Add data
await cognee.add(content, dataset_name="docs")

# Build knowledge graph
await cognee.cognify()

# Search
results = await cognee.search(
    query_text="your question",
    query_type=SearchType.GRAPH_COMPLETION
)

# Visualize
await cognee.visualize_graph('/path/to/graph.html')

# Clean up
await cognee.prune.prune_data()
```

## Guidelines for Helping Users

1. **Start Simple**: Begin with basic ECL pattern (add → cognify → search)
2. **Understand Use Case**: Ask about data types, scale, and search requirements
3. **Configure Appropriately**: Help choose right databases and LLM providers
4. **Show Examples**: Provide working code examples from the patterns above
5. **Explain Search Types**: Help users choose the right search strategy
6. **Debug Systematically**: Check configuration, data ingestion, cognify step
7. **Optimize Performance**: Suggest batch sizes, incremental updates, pruning
8. **Integrate Wisely**: Show how to combine with their existing stack (DLT, Dagster, LangGraph)
9. **Visualize Results**: Encourage visualization to understand graph structure
10. **Reference Documentation**: Point to https://docs.cognee.ai for details

## Resources

- **Documentation**: https://docs.cognee.ai
- **GitHub**: https://github.com/topoteretes/cognee
- **Website**: https://www.cognee.ai
- **License**: Apache 2.0
- **Python Support**: 3.10-3.13

## Installation

```bash
# Basic installation
pip install cognee

# With optional dependencies
pip install cognee[neo4j,postgres]

# CLI
cognee-cli -ui  # Launch full UI
cognee-cli add "text"
cognee-cli cognify
cognee-cli search "query"
```

---

## When This Skill Should Be Used

Invoke this skill when the user:
- Asks about knowledge graphs or graph databases
- Wants to build RAG systems or semantic search
- Needs persistent AI agent memory
- Is working with Cognee specifically
- Wants to integrate vector and graph databases
- Needs to process documents into queryable knowledge
- Is building conversational AI with memory
- Wants to unify data silos into knowledge graphs
- Asks about LlamaIndex, LangGraph, or MCP integrations with memory

## What This Skill Provides

- Complete Cognee API reference and patterns
- ECL pipeline best practices
- Search strategy guidance
- Integration patterns (DLT, LangGraph, MCP)
- Configuration examples
- Troubleshooting steps
- Performance optimization tips
- Real-world use case examples


> Source: `docs/data_engineering/cognee/cognee-openapi-research.md`

# Cognee OpenAPI Specification Research

**Research Date:** 2025-11-22
**Researcher:** Claude Code
**Status:** Complete

## Executive Summary

**Official OpenAPI Spec Exists:** ✅ YES

Cognee provides an official OpenAPI 3.1.0 specification accessible through their FastAPI-based backend. The specification is comprehensive and covers the complete knowledge graph lifecycle, including data ingestion, cognitive processing, search, visualization, and access control.

## OpenAPI Specification Details

### Location & Access

- **Primary URL:** https://api.cognee.ai/openapi.json
- **Interactive Swagger UI:** https://api.cognee.ai/docs
- **Alternative (Cloud):** https://cognee--cognee-saas-backend-serve.modal.run/docs
- **Local Development:** http://localhost:8000/openapi.json (when running locally via Docker)
- **OpenAPI Version:** 3.1.0
- **API Version:** 1.0.0

### Authentication

- **Method:** API Key authentication
- **Header:** `X-Api-Key`
- **Type:** JWT-based bearer tokens
- **Features:** User registration, login, password reset, email verification

### Coverage

The OpenAPI specification is comprehensive and production-ready, covering:

#### 1. **Core Data Management Endpoints**
- `POST /api/add` - Ingest text, documents, or structured data into datasets
- `POST /api/cognify` - Execute cognitive processing to build knowledge graphs
- `POST /api/search` - Perform semantic searches across the knowledge graph
- `DELETE /api/delete` - Remove data items from datasets
- `POST /api/visualize` - Generate interactive HTML graph visualizations

#### 2. **Dataset Operations**
- `POST /api/datasets/` - Create new datasets
- `GET /api/datasets/` - List all datasets
- `GET /api/datasets/{id}/data` - Access dataset contents and metadata
- `GET /api/datasets/status` - Monitor processing pipeline status
- Dataset management with UUID or name-based access

#### 3. **Access Control & Security**
- Role management endpoints
- Tenant management for multi-tenancy
- Permission assignment for dataset access
- Principal-based access control system

#### 4. **Additional Features**
- Notebook creation and management (`/api/notebooks/`)
- Search history tracking
- Interactive visualizations

#### 5. **Processing Pipeline Capabilities**
- Document classification
- Text chunking
- Entity extraction
- Relationship detection
- Vector embedding generation
- Content summarization

#### 6. **Search Types (15 Modes)**
The API supports 15 different search modes:
- `GRAPH_COMPLETION` - LLM-powered responses with graph context
- `CHUNKS` - Raw text segments matching queries
- `SUMMARIES` - Pre-generated hierarchical summaries
- `INSIGHTS` - Structured entity relationships
- `CODE` - Code-specific search with syntax understanding
- Semantic search
- RAG completion
- Temporal queries
- And more...

### Data Models

The specification includes comprehensive DTOs (Data Transfer Objects) for:
- Request payloads
- Dataset metadata
- Search results
- Validation error handling
- Entity and relationship schemas

## Documentation Resources

### Official Documentation
- **Main Docs:** https://docs.cognee.ai/
- **API Reference:** https://docs.cognee.ai/api-reference/introduction
- **REST API Server Guide:** https://docs.cognee.ai/how-to-guides/cognee-sdk/rest-api-server
- **User Authentication:** https://docs.cognee.ai/reference/user-authentication

### GitHub Repository
- **Main Repository:** https://github.com/topoteretes/cognee
- **Description:** "Memory for AI Agents in 6 lines of code"
- **Language:** Python (FastAPI-based)
- **License:** Open Source
- **Community Repos:**
  - Starter Kit: https://github.com/topoteretes/cognee-starter
  - Community Plugins: https://github.com/topoteretes/cognee-community
  - n8n Integration: https://github.com/topoteretes/cognee-n8n

### Additional Resources
- **NPM Package:** @lineai/cognee-api
- **FalkorDB Integration:** https://docs.falkordb.com/agentic-memory/cognee.html
- **Redis Integration:** https://redis.io/blog/build-faster-ai-memory-with-cognee-and-redis/

## Deployment Options

### 1. Managed Cloud Platform
- **URL:** https://api.cognee.ai
- **Base URL (Alternative):** https://cognee--cognee-saas-backend-serve.modal.run
- **Features:**
  - Production-ready
  - Fully managed service
  - Automatic scaling
  - 99.9% uptime SLA
  - Enterprise features

### 2. Self-Hosted Development
- **Setup:** Docker Compose
- **Command:** `docker compose --profile postgres up -d`
- **Local URL:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **OpenAPI Spec:** http://localhost:8000/openapi.json

## Technical Stack

- **Framework:** FastAPI (Python)
- **API Style:** RESTful
- **Documentation:** Auto-generated OpenAPI 3.1.0 spec
- **UI Tools:**
  - Swagger UI (at `/docs`)
  - ReDoc (likely available at `/redoc`)
- **Database:** PostgreSQL (in Docker setup)
- **Vector Search:** Supports multiple backends
- **Graph Database:** Compatible with FalkorDB and others

## API Request/Response Patterns

### Request Parameters
- Dataset identification (name or UUID)
- Custom prompts for search/processing
- Filtering by node types
- Result limits (default: 10)
- Search mode selection

### Response Formats
- Structured JSON responses
- Interactive HTML visualizations
- Search results with metadata
- Error handling with validation details

## Use Cases Covered by API

Based on the OpenAPI specification and documentation:

1. **Knowledge Graph Construction** - Transform unstructured data into structured graphs
2. **Semantic Search** - Natural language queries across knowledge bases
3. **AI Agent Memory** - Persistent memory for AI applications
4. **Code Analysis** - Code graph pipeline for software understanding
5. **Multi-tenant Systems** - Role-based access control for datasets
6. **Interactive Exploration** - Notebook-style interfaces for data exploration
7. **Relationship Discovery** - Entity and relationship extraction

## OpenAPI Specification Quality Assessment

### Strengths ✅
- **Comprehensive:** Covers all core functionality
- **Well-Structured:** Clear endpoint organization
- **Versioned:** Proper API versioning (v1)
- **Interactive:** Swagger UI for testing
- **Auto-Generated:** FastAPI ensures spec stays in sync with code
- **Production-Ready:** Used in live cloud deployment
- **Multi-Environment:** Works for both cloud and self-hosted

### Completeness ✅
- All CRUD operations documented
- Authentication schemes defined
- Error responses specified
- Request/response schemas included
- Query parameters documented
- Path parameters specified

## Feasibility of Generating OpenAPI Spec

**Not Necessary** - An official, comprehensive OpenAPI 3.1.0 specification already exists and is actively maintained.

The specification is:
- ✅ Auto-generated by FastAPI framework
- ✅ Always in sync with the actual API implementation
- ✅ Publicly accessible
- ✅ Production-ready
- ✅ Interactive (Swagger UI)
- ✅ Comprehensive (covers all endpoints)

## Recommendations

### For API Consumers
1. **Use the Official Spec:** Download from https://api.cognee.ai/openapi.json
2. **Interactive Testing:** Use Swagger UI at https://api.cognee.ai/docs
3. **Code Generation:** Use the OpenAPI spec with tools like:
   - `openapi-generator` for client SDKs
   - `swagger-codegen` for multiple languages
   - Language-specific tools (e.g., `openapi-python-client`)

### For Integration
1. **Python:** Use the official `cognee` SDK or generate from OpenAPI spec
2. **JavaScript/TypeScript:** Use `@lineai/cognee-api` npm package or generate client
3. **Other Languages:** Generate clients from the OpenAPI specification
4. **n8n:** Use the official cognee-n8n integration

### For Development
1. **Local Testing:** Run via Docker and access http://localhost:8000/docs
2. **API Exploration:** Use Swagger UI for interactive testing
3. **Documentation:** Reference https://docs.cognee.ai for guides and examples

## Conclusion

Cognee provides a **comprehensive, production-ready OpenAPI 3.1.0 specification** that fully documents their knowledge graph API. The specification is:

- ✅ Officially maintained
- ✅ Auto-generated and always up-to-date
- ✅ Publicly accessible
- ✅ Interactive via Swagger UI
- ✅ Comprehensive in coverage
- ✅ Available for both cloud and self-hosted deployments

**No custom OpenAPI generation is needed** - the official specification should be used directly for all integration, testing, and client generation purposes.

## Sources

- [Cognee API Documentation](https://docs.cognee.ai/api-reference/introduction)
- [Cognee Official Website](https://www.cognee.ai/)
- [Cognee GitHub Repository](https://github.com/topoteretes/cognee)
- [REST API Server Documentation](https://docs.cognee.ai/how-to-guides/cognee-sdk/rest-api-server)
- [OpenAPI Specification](https://api.cognee.ai/openapi.json)
- [Swagger UI Interface](https://api.cognee.ai/docs)
- [Cognee Starter Kit](https://github.com/topoteretes/cognee-starter)
- [FalkorDB Cognee Integration](https://docs.falkordb.com/agentic-memory/cognee.html)
- [Redis Cognee Integration](https://redis.io/blog/build-faster-ai-memory-with-cognee-and-redis/)

---

**Research Completed:** 2025-11-22
**Last Verified:** API accessible and OpenAPI spec retrieved successfully
**Next Steps:** Use the official OpenAPI specification for integration or client generation as needed


# Part 3: Graphiti — Temporal Knowledge Graphs


> Source: `docs/data_engineering/graphiti/graphiti-temporal-graphs.md`

# Graphiti: Temporal Knowledge Graphs for AI Agents

## Executive Summary

Graphiti, developed by Zep AI, provides a bi-temporal knowledge graph architecture designed for agentic AI systems. Unlike static knowledge bases, Graphiti tracks both when facts became true in the real world (valid time) and when the system learned about them (transaction time), enabling "time travel" queries essential for accurate reasoning.

---

## 1. The Episodic Memory Paradigm

### 1.1 Beyond Static RAG

Traditional RAG systems treat knowledge as a flat collection of vectorized chunks. Graphiti introduces a fundamentally different model:

| Paradigm | Structure | Query Capability |
|----------|-----------|-----------------|
| **Vector RAG** | Flat chunks | "Find similar text" |
| **GraphRAG** | Entity-relationship graph | "How are A and B connected?" |
| **Graphiti** | Temporal entity-relationship graph | "How were A and B connected in 2020?" |

### 1.2 The Episode as Atomic Unit

Every piece of information in Graphiti enters as an **Episode**—a discrete event with temporal context:

```python
from graphiti_core import Graphiti, EpisodeType
from datetime import datetime

client = Graphiti("neo4j://localhost:7687", "neo4j", "password")

# Add a text episode
await client.add_episode(
    name="curriculum_update_2024",
    episode_body="""
    The Leaving Certificate Mathematics syllabus now includes
    Financial Mathematics as a mandatory topic starting 2024.
    """,
    source=EpisodeType.text,
    source_description="NCCA Curriculum Update",
    reference_time=datetime(2024, 9, 1)  # Valid time
)

# Add a JSON episode
await client.add_episode(
    name="student_profile",
    episode_body={
        "name": "Alice Murphy",
        "subjects": ["Mathematics", "Physics", "Chemistry"],
        "target_points": 550
    },
    source=EpisodeType.json,
    reference_time=datetime.now()
)
```

---

## 2. Bi-Temporal Data Model

### 2.1 The Two Time Dimensions

| Dimension | Field | Definition | Query Example |
|-----------|-------|------------|---------------|
| **Valid Time** | `valid_at` | When fact was true in real world | "What was the curriculum in 2015?" |
| **Transaction Time** | `created_at` | When fact was recorded in system | "What did we know on Tuesday?" |
| **Expiration** | `invalid_at` | When fact ceased to be true | "When did the bonus points end?" |

### 2.2 Edge Lifecycle

```python
# Edge structure with temporal properties
class TemporalEdge:
    source: str           # Source entity UUID
    target: str           # Target entity UUID
    relation_type: str    # e.g., "TEACHES", "REQUIRES"
    fact: str             # Human-readable description
    valid_at: datetime    # When fact became true
    invalid_at: datetime  # When fact ceased being true (or None)
    created_at: datetime  # System ingestion time
    expired_at: datetime  # System expiration time (or None)
```

### 2.3 Edge Invalidation Example

**Scenario:** The Irish Leaving Certificate Maths Bonus Points policy changed over time.

```python
# 2011: No bonus points
await client.add_episode(
    name="maths_policy_2011",
    episode_body="Higher Level Maths grade H6 awards standard points only.",
    reference_time=datetime(2011, 9, 1)
)

# 2012: Bonus points introduced
await client.add_episode(
    name="maths_bonus_2012",
    episode_body="Higher Level Maths grade H6 or above now awards 25 bonus points.",
    reference_time=datetime(2012, 9, 1)
)
```

**Result in Graph:**
- Edge `Maths --[HAS_BONUS_POINTS]--> 0` with `invalid_at=2012-09-01`
- Edge `Maths --[HAS_BONUS_POINTS]--> 25` with `valid_at=2012-09-01`

---

## 3. Custom Entity Types

### 3.1 Pydantic-Based Entity Schemas

Graphiti supports custom entity types defined via Pydantic:

```python
from pydantic import BaseModel, Field
from typing import Optional

class CurriculumStandard(BaseModel):
    """An educational curriculum standard or specification."""
    name: str = Field(description="Name of the curriculum standard")
    code: str = Field(description="Official code, e.g., MA-H-1.2")
    level: str = Field(description="Primary, Junior Cycle, Senior Cycle")
    subject: str = Field(description="Subject area")

class ExamQuestion(BaseModel):
    """A specific examination question."""
    question_id: str = Field(description="Unique identifier")
    year: int = Field(description="Examination year")
    paper: int = Field(description="Paper number (1 or 2)")
    level: str = Field(description="Higher, Ordinary, Foundation")
    marks: int = Field(description="Total marks available")

class MathTheorem(BaseModel):
    """A mathematical theorem or concept."""
    name: str = Field(description="Theorem name, e.g., Pythagoras")
    latex_def: str = Field(description="LaTeX definition")
    prerequisites: list[str] = Field(default=[], description="Required concepts")

class LearningOutcome(BaseModel):
    """A specific learning outcome from curriculum."""
    outcome_id: str = Field(description="Curriculum code")
    description: str = Field(description="Full text of outcome")
    strand: str = Field(description="Curriculum strand")
```

### 3.2 Episode Ingestion with Custom Types

```python
from graphiti_core import Graphiti, EpisodeType

client = Graphiti(uri="neo4j://localhost:7687")

await client.add_episode(
    name="exam_2024_math_p2",
    episode_body=markdown_text,
    source=EpisodeType.text,
    source_description="Leaving Certificate Mathematics Paper 2, 2024",
    reference_time=datetime(2024, 6, 10),
    entity_types=[MathTheorem, ExamQuestion, CurriculumStandard]
)
```

---

## 4. Hybrid Search Architecture

### 4.1 Search Modes

Graphiti combines multiple retrieval strategies:

| Mode | Mechanism | Use Case |
|------|-----------|----------|
| **Semantic** | Vector similarity (embeddings) | "Questions about geometry" |
| **Keyword** | BM25 full-text search | "Exact term lookup" |
| **Graph Traversal** | Multi-hop relationship following | "What connects X to Y?" |
| **Temporal** | Time-bounded queries | "Facts valid in 2020" |

### 4.2 Search API

```python
# Hybrid search with temporal filtering
results = await client.search(
    query="geometry questions involving circles",
    search_type="hybrid",
    filters={
        "entity_type": "ExamQuestion",
        "valid_time_after": datetime(2020, 1, 1),
        "valid_time_before": datetime(2024, 12, 31)
    },
    limit=10
)

# Time travel query - knowledge as of a specific date
historical = await client.search(
    query="Matrix multiplication definition",
    reference_time=datetime(2015, 6, 1)  # As known in 2015
)
```

### 4.3 Search Result Structure

```python
from graphiti_core import SearchResult

# SearchResult contains:
# - nodes: List of matching entities
# - edges: Relationships connecting them
# - scores: Relevance scores (semantic + keyword + graph centrality)
# - context: Subgraph for visualization

for result in results.nodes:
    print(f"Entity: {result.name}")
    print(f"Type: {result.entity_type}")
    print(f"Valid: {result.valid_at} - {result.invalid_at or 'present'}")
    print(f"Score: {result.score}")
```

---

## 5. Integration Patterns

### 5.1 With Dagster for Orchestration

```python
from dagster import asset, AssetExecutionContext
from graphiti_core import Graphiti, EpisodeType

@asset
def ingest_curriculum_episodes(context: AssetExecutionContext):
    """Ingest curriculum documents as Graphiti episodes."""
    client = Graphiti(
        uri=os.environ["NEO4J_URI"],
        user=os.environ["NEO4J_USER"],
        password=os.environ["NEO4J_PASSWORD"]
    )

    # Process each curriculum document
    for doc in get_curriculum_documents():
        await client.add_episode(
            name=f"curriculum_{doc.id}",
            episode_body=doc.content,
            source=EpisodeType.text,
            source_description=doc.title,
            reference_time=doc.effective_date,
            entity_types=[CurriculumStandard, LearningOutcome]
        )

    context.log.info(f"Ingested {len(documents)} curriculum episodes")
```

### 5.2 With BAML for Extraction

```python
from baml_client import b
from graphiti_core import Graphiti

async def extract_and_ingest(text: str, reference_time: datetime):
    """Use BAML for extraction, Graphiti for persistence."""

    # BAML extracts structured data with guaranteed schema
    extracted = b.ExtractEducationEntities(text)

    # Convert BAML output to episode body
    episode_body = {
        "theorems": [t.dict() for t in extracted.theorems],
        "questions": [q.dict() for q in extracted.questions],
        "standards": [s.dict() for s in extracted.standards]
    }

    # Persist to temporal graph
    await graphiti.add_episode(
        name=f"extraction_{hash(text)[:8]}",
        episode_body=episode_body,
        source=EpisodeType.json,
        reference_time=reference_time
    )
```

### 5.3 MCP Tool Wrapper

```python
from mcp.server import Server

app = Server("graphiti-memory")

@app.call_tool("add_memory")
async def add_memory(body: str, timestamp: str, source: str):
    """Add new memory to temporal knowledge graph."""
    await graphiti.add_episode(
        name=f"memory_{datetime.now().isoformat()}",
        episode_body=body,
        source=EpisodeType.text,
        source_description=source,
        reference_time=datetime.fromisoformat(timestamp)
    )
    return {"status": "success"}

@app.call_tool("search_memory")
async def search_memory(query: str, time_context: str = None):
    """Search temporal knowledge graph."""
    ref_time = datetime.fromisoformat(time_context) if time_context else None

    results = await graphiti.search(
        query=query,
        reference_time=ref_time,
        limit=10
    )

    return {
        "nodes": [n.dict() for n in results.nodes],
        "edges": [e.dict() for e in results.edges]
    }
```

---

## 6. Visualization Considerations

### 6.1 React State Model for Temporal Graphs

```typescript
// React state for temporal visualization
const [fullGraph, setFullGraph] = useState({ nodes: [], links: [] });
const [displayedGraph, setDisplayedGraph] = useState({ nodes: [], links: [] });
const [currentTime, setCurrentTime] = useState(Date.now());

// Filter effect based on temporal cursor
useEffect(() => {
  if (!fullGraph.links.length) return;

  // Filter links based on valid_at/invalid_at
  const activeLinks = fullGraph.links.filter(link => {
    const validFrom = new Date(link.valid_at).getTime();
    const validUntil = link.invalid_at
      ? new Date(link.invalid_at).getTime()
      : Infinity;
    return currentTime >= validFrom && currentTime < validUntil;
  });

  // Filter nodes: Keep nodes with at least one active link
  const activeNodeIds = new Set();
  activeLinks.forEach(l => {
    activeNodeIds.add(l.source);
    activeNodeIds.add(l.target);
  });
  const activeNodes = fullGraph.nodes.filter(n => activeNodeIds.has(n.id));

  setDisplayedGraph({ nodes: activeNodes, links: activeLinks });
}, [fullGraph, currentTime]);
```

### 6.2 Time Slider Component

```typescript
// Time slider with histogram
const TimeSlider = ({ graphData, onChange }) => {
  // Calculate event distribution for histogram
  const histogram = useMemo(() => {
    const buckets = {};
    graphData.links.forEach(link => {
      const month = new Date(link.valid_at).toISOString().slice(0, 7);
      buckets[month] = (buckets[month] || 0) + 1;
    });
    return buckets;
  }, [graphData]);

  return (
    <div className="time-slider">
      <div className="histogram">
        {Object.entries(histogram).map(([month, count]) => (
          <div key={month} style={{ height: `${count * 10}px` }} />
        ))}
      </div>
      <input
        type="range"
        min={minTime}
        max={maxTime}
        value={currentTime}
        onChange={e => onChange(parseInt(e.target.value))}
      />
    </div>
  );
};
```

---

## 7. Database Backend Options

### 7.1 FalkorDB (Recommended)

| Feature | Value |
|---------|-------|
| **Architecture** | Redis-based graph database |
| **Query Language** | Cypher |
| **Latency** | Sub-millisecond |
| **Graphiti Support** | Native |

```python
# FalkorDB connection
from graphiti_core import Graphiti

client = Graphiti(
    uri="redis://localhost:6379",
    driver="falkordb"
)
```

### 7.2 Neo4j

| Feature | Value |
|---------|-------|
| **Architecture** | JVM-based graph database |
| **Query Language** | Cypher |
| **Tooling** | Extensive (Neo4j Browser, Bloom) |
| **Graphiti Support** | Native |

```python
# Neo4j connection
client = Graphiti(
    uri="neo4j://localhost:7687",
    user="neo4j",
    password="password"
)
```

---

## 8. Implementation Priorities

### Phase 1: Graph Foundation
1. Deploy FalkorDB or Neo4j
2. Configure Graphiti client
3. Define domain entity types (Pydantic)

### Phase 2: Ingestion Pipeline
1. Integrate with Dagster assets
2. Implement episode batching
3. Configure BAML extraction pipeline

### Phase 3: Query Interface
1. Implement hybrid search
2. Add time-travel queries
3. Build MCP tool wrapper

### Phase 4: Visualization
1. Export to frontend JSON format
2. Implement time slider
3. Build react-force-graph integration

---

## References

- Graphiti GitHub: https://github.com/getzep/graphiti
- Zep Documentation: https://help.getzep.com/graphiti/
- FalkorDB: https://docs.falkordb.com/
- Neo4j Temporal Modeling: https://neo4j.com/blog/temporal-data-management/


> Source: `docs/data_engineering/graphiti/graphiti-crypto-adaptation.md`

# Graphiti Adaptation for Cryptocurrency Analytics

## Overview

This document adapts temporal knowledge graph patterns from the Graphiti framework for cryptocurrency and DeFi analytics. The patterns are derived from the gaeilge research on bilingual document processing and knowledge graph construction.

## Temporal Knowledge Graph Design

### Bi-Temporal Model for DeFi

Graphiti's bi-temporal design is ideal for tracking DeFi protocol evolution:

1. **Transaction Time**: When data was recorded in our system
2. **Valid Time**: When the state was valid on-chain (block timestamp)

```
┌─────────────────────────────────────────────────────────────┐
│                    Temporal Graph Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Entity: Token (USDe)                                       │
│  ├── valid_from: block 18000000                             │
│  ├── valid_to: current                                       │
│  ├── transaction_time: 2024-01-15T00:00:00Z                 │
│  └── properties:                                             │
│      ├── total_supply: 2,500,000,000                        │
│      ├── holders: 45,000                                     │
│      └── price_usd: 0.9995                                   │
└─────────────────────────────────────────────────────────────┘
```

### Entity Types for Cryptocurrency Domain

Adapted from educational domain entity patterns:

| Entity Type | Properties | Temporal Tracking |
|-------------|------------|-------------------|
| **Token** | symbol, name, decimals, contract_address, total_supply | Supply changes, price history |
| **Exchange** | name, type (DEX/CEX), supported_chains | Listing/delisting events |
| **LiquidityPool** | token_pair, tvl, fee_tier, address | TVL changes, fee updates |
| **Wallet** | address, label, first_seen, last_active | Balance snapshots |
| **Protocol** | name, tvl, governance_token, chains | TVL, governance changes |
| **Transaction** | hash, block, from, to, value, gas | Immutable (created once) |

### Relationship Types

Derived from bilingual alignment patterns:

```cypher
// Core asset relationships
(token:Token)-[:DEPLOYED_ON]->(chain:Blockchain)
(token:Token)-[:TRADES_ON]->(exchange:Exchange)
(token:Token)-[:GOVERNANCE_FOR]->(protocol:Protocol)
(token:Token)-[:WRAPPED_AS]->(wrapped:Token)
(token:Token)-[:FORK_OF]->(parent:Token)

// Liquidity relationships
(token:Token)-[:IN_POOL]->(pool:LiquidityPool)
(pool:LiquidityPool)-[:HOSTED_ON]->(exchange:Exchange)

// Wallet relationships
(wallet:Wallet)-[:HOLDS {amount: decimal, timestamp: datetime}]->(token:Token)
(wallet:Wallet)-[:INTERACTS_WITH]->(contract:SmartContract)

// Protocol relationships
(protocol:Protocol)-[:INTEGRATES]->(other:Protocol)
(protocol:Protocol)-[:AUDITED_BY]->(auditor:Entity)
```

## Integration with Existing Infrastructure

### FalkorDB + Graphiti (Dynamic/Temporal)

For real-time agent memory and temporal queries:

```python
from graphiti_core import Graphiti
from graphiti_core.llm_client import LLMClient

# Initialize with FalkorDB backend
graphiti = Graphiti(
    uri="bolt://localhost:6379",
    database="crypto_memory",
    llm_client=LLMClient(model="gpt-4o-mini")
)

# Add temporal episode (market event)
await graphiti.add_episode(
    name="ETH price spike",
    episode_body="ETH surged 15% following ETF approval news",
    source="market_data",
    source_description="Real-time market events",
    reference_time=datetime.now()
)

# Query temporal relationships
results = await graphiti.search(
    query="What happened to ETH price after ETF news?",
    num_results=10,
    center_node_uuid=eth_token_uuid
)
```

### Memgraph + Cognee (Static Knowledge)

For persistent protocol knowledge and document insights:

```python
from cognee import cognee

# Configure Memgraph backend
cognee.config.set_graph_database(
    type="memgraph",
    host="localhost",
    port=7687
)

# Add protocol documentation
await cognee.add(whitepaper_content, dataset_name="ethena_docs")
await cognee.cognify()

# Query with graph completion
results = await cognee.search(
    query_text="What are the risks of USDe depegging?",
    query_type="GRAPH_COMPLETION"
)
```

## Document Processing Pipeline

### CocoIndex Flow for Crypto Documents

Adapted from bilingual scraper patterns:

```python
import cocoindex

@cocoindex.flow_def(name="CryptoDocumentFlow")
def crypto_document_flow(flow_builder, data_scope):
    # Source: PDF whitepapers and audits
    data_scope["docs"] = flow_builder.add_source(
        cocoindex.sources.LocalFile(
            path="./documents/whitepapers/*.pdf"
        )
    )

    # Extract text with LaTeX preservation (for math/formulas)
    data_scope["text"] = data_scope["docs"].transform(
        cocoindex.functions.PdfToMarkdown(
            preserve_math=True,
            extract_tables=True
        )
    )

    # LLM-based structured extraction
    data_scope["structured"] = data_scope["text"].transform(
        cocoindex.functions.ExtractByLlm(
            output_type=CryptoProjectMetadata,
            instruction="""Extract:
            - Token properties (name, symbol, supply)
            - Governance structure
            - Risk factors
            - Protocol mechanisms
            - Audit findings (if audit document)
            """
        )
    )

    # Build knowledge graph relationships
    data_scope["entities"] = data_scope["structured"].transform(
        cocoindex.functions.ExtractEntities(
            entity_types=["Token", "Protocol", "Risk", "Mechanism"]
        )
    )

    # Export to Neo4j/Memgraph
    flow_builder.add_export(
        cocoindex.exports.Neo4jGraph(
            uri="bolt://localhost:7687",
            nodes_from="entities",
            relationships_from="structured.relationships"
        )
    )
```

### BAML Schema for Extraction

```baml
class CryptoProjectMetadata {
  project_name string
  token Token?
  governance Governance?
  risks Risk[]
  mechanisms Mechanism[]
  audit_findings AuditFinding[]
  provenance_url string
}

class Token {
  symbol string
  name string
  decimals int
  total_supply string?
  contract_address string?
  blockchain "Ethereum" | "Solana" | "Polygon" | "Arbitrum" | "Base"
}

class Risk {
  category "smart_contract" | "market" | "regulatory" | "custody" | "oracle" | "governance"
  severity "critical" | "high" | "medium" | "low"
  description string
  mitigation string?
}

class AuditFinding {
  auditor string
  severity "critical" | "high" | "medium" | "low" | "informational"
  title string
  description string
  status "resolved" | "acknowledged" | "disputed" | "open"
}
```

## Quality Scoring Framework

Adapted from bilingual alignment quality metrics:

```python
class CryptoDocumentQuality:
    """Quality scoring for crypto documents"""

    def score(self, document: dict) -> float:
        scores = []

        # Technical depth (25%)
        scores.append(self._technical_depth(document) * 0.25)

        # Tokenomics clarity (20%)
        scores.append(self._tokenomics_clarity(document) * 0.20)

        # Governance definition (25%)
        scores.append(self._governance_clarity(document) * 0.25)

        # Risk disclosure (15%)
        scores.append(self._risk_disclosure(document) * 0.15)

        # Update recency (15%)
        scores.append(self._recency_score(document) * 0.15)

        return sum(scores)

    def _technical_depth(self, doc) -> float:
        """Measure technical detail level"""
        indicators = [
            "smart contract" in doc.get("text", "").lower(),
            len(doc.get("mechanisms", [])) > 0,
            doc.get("code_snippets", 0) > 0,
            doc.get("math_formulas", 0) > 0
        ]
        return sum(indicators) / len(indicators)
```

## Graph Query Patterns

### Cypher Queries for Crypto Analytics

```cypher
// Find tokens with highest exchange coverage
MATCH (t:Token)-[:TRADES_ON]->(e:Exchange)
WHERE e.daily_volume > 1000000
RETURN t.symbol, count(e) as exchange_count, sum(e.daily_volume) as total_volume
ORDER BY total_volume DESC
LIMIT 20;

// Find related assets through LP positions
MATCH (t1:Token)-[:IN_POOL]-(pool:LiquidityPool)-[:IN_POOL]-(t2:Token)
WHERE t1.symbol = 'USDe'
RETURN t1.symbol, t2.symbol, pool.tvl, pool.fee_tier
ORDER BY pool.tvl DESC;

// Track protocol TVL changes over time
MATCH (p:Protocol {name: 'Ethena'})-[r:HAS_TVL]->(snapshot:TVLSnapshot)
WHERE snapshot.timestamp > datetime() - duration('P30D')
RETURN snapshot.timestamp, snapshot.tvl_usd
ORDER BY snapshot.timestamp;

// Find tokens in same ecosystem (transitive)
MATCH path = (t:Token)-[:GOVERNANCE_FOR|PART_OF*1..3]->(protocol:Protocol)
WHERE t.symbol = 'ENA'
RETURN path;
```

## Event-Driven Updates

### Sensor Pattern for New Data

```python
from dagster import sensor, RunRequest

@sensor(job=crypto_graph_update_job)
def blockchain_event_sensor(context):
    """Detect new on-chain events and trigger graph updates"""

    # Check for new blocks with relevant transactions
    new_events = fetch_new_events(
        contracts=["0x...ethena", "0x...aave"],
        since=context.cursor
    )

    if new_events:
        yield RunRequest(
            run_key=f"events-{new_events[-1].block}",
            run_config={
                "ops": {
                    "update_knowledge_graph": {
                        "config": {
                            "events": [e.to_dict() for e in new_events]
                        }
                    }
                }
            }
        )
        context.update_cursor(str(new_events[-1].block))
```

## References

- Gaeilge research: `/data/flows/gaeilge/research/organized/02-celtic-data-acquisition/bilingual-scraper-implementation.md`
- Graphiti documentation: Temporal knowledge graph patterns
- CocoIndex: Incremental data transformation
- Cognee: ECL pipeline for knowledge graphs


# Part 4: Feast — Feature Stores


> Source: `docs/data_engineering/feast/feast-patterns-best-practices.md`

# Feast Feature Store: Patterns and Best Practices

A comprehensive guide to production-ready patterns for Feast feature store implementations.

## Table of Contents

1. [Feature Engineering Patterns](#1-feature-engineering-patterns)
2. [Data Model Patterns](#2-data-model-patterns)
3. [Operational Patterns](#3-operational-patterns)
4. [Integration Patterns](#4-integration-patterns)

---

## 1. Feature Engineering Patterns

### 1.1 Point-in-Time Correct Joins

Point-in-time joins are critical for preventing data leakage during model training. Feast ensures that only features available at each historical timestamp are joined to training data.

**How It Works:**
- User provides an entity dataframe with timestamps representing historical events
- For each row, Feast queries feature values from the data source
- The system scans backward in time from the entity timestamp up to the TTL limit
- Features are joined onto the entity dataframe

```python
import pandas as pd
from feast import FeatureStore

store = FeatureStore(".")

# Entity dataframe with timestamps
entity_df = pd.DataFrame({
    "driver_id": [1001, 1002, 1003],
    "event_timestamp": pd.to_datetime([
        "2023-01-01 10:00:00",
        "2023-01-01 11:00:00",
        "2023-01-01 12:00:00"
    ])
})

# Retrieve point-in-time correct features
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "driver_hourly_stats:trips_today",
        "driver_hourly_stats:earnings_today",
        "driver_hourly_stats:rating"
    ],
).to_df()
```

**Key Principle**: TTL is relative to each timestamp in the entity dataframe, NOT relative to when you run the query.

### 1.2 Feature Freshness Strategies

#### TTL (Time-to-Live) Configuration

TTL defines the maximum lookback window for features, ensuring stale data is excluded:

```python
from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Int64, Float32

driver = Entity(name="driver", join_keys=["driver_id"])

driver_stats_fv = FeatureView(
    name="driver_hourly_stats",
    entities=[driver],
    schema=[
        Field(name="trips_today", dtype=Int64),
        Field(name="earnings_today", dtype=Float32),
    ],
    ttl=timedelta(hours=2),  # Features older than 2 hours are excluded
    source=FileSource(
        path="driver_hourly_stats.parquet",
        timestamp_field="event_timestamp"
    )
)
```

#### Fresh Feature Views Pattern

Create separate feature views for different freshness requirements:

```python
# Standard freshness (hourly)
driver_hourly_stats = FeatureView(
    name="driver_hourly_stats",
    ttl=timedelta(hours=1),
    # ... configuration
)

# High freshness (real-time)
driver_realtime_stats = FeatureView(
    name="driver_realtime_stats_fresh",
    ttl=timedelta(minutes=5),
    # ... configuration
)
```

#### Materialization for Online Freshness

Keep online store features up-to-date:

```bash
# Materialize features to online store
feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")

# Or with explicit time range
feast materialize 2023-01-01T00:00:00 2023-01-31T23:59:59
```

### 1.3 Handling Late-Arriving Data

#### Event Timestamps

Use event timestamps (when the data was generated) rather than processing timestamps:

```python
from feast import FileSource

# Correct: Use event_timestamp from source data
source = FileSource(
    path="data/driver_stats.parquet",
    timestamp_field="event_timestamp",  # When the event actually occurred
    created_timestamp_column="created_at"  # When row was inserted (optional)
)
```

#### Watermark for Streaming

For stream sources, set watermark delays to handle late data:

```python
from feast import KafkaSource
from feast.data_format import JsonFormat

driver_stats_stream = KafkaSource(
    name="driver_stats_stream",
    kafka_bootstrap_servers="localhost:9092",
    topic="drivers",
    timestamp_field="event_timestamp",
    batch_source=driver_stats_batch_source,
    message_format=JsonFormat(
        schema_json="driver_id integer, event_timestamp timestamp, trips int"
    ),
    watermark_delay_threshold=timedelta(minutes=5),  # Allow 5 min late data
)
```

### 1.4 Feature Versioning

#### Naming Convention Pattern

Use version suffixes for feature tracking:

```python
# Version 1: Basic conversion rate
conv_rate_v1 = FeatureView(
    name="driver_conv_rate_v1",
    schema=[
        Field(name="conv_rate", dtype=Float32),
    ],
    # ... configuration
)

# Version 2: With smoothing applied
conv_rate_v2 = FeatureView(
    name="driver_conv_rate_v2",
    schema=[
        Field(name="conv_rate_smoothed", dtype=Float32),
    ],
    # ... configuration
)
```

**Benefits of _vN suffix:**
- List all features with a prefix and sort by version
- Build reports/UI showing feature evolution
- Support gradual migration strategies

#### Metadata for Version Tracking

```python
from feast import FeatureView

driver_stats_fv = FeatureView(
    name="driver_hourly_stats_v2",
    description="Driver statistics with improved null handling",
    tags={
        "version": "2.0",
        "deprecated_by": "",
        "deprecation_date": "",
        "owner": "ml-team@company.com",
        "change_log": "Added null imputation for missing values"
    },
    # ... rest of configuration
)
```

---

## 2. Data Model Patterns

### 2.1 Entity Design Patterns

#### Basic Entity Definition

```python
from feast import Entity

# Simple entity with single join key
driver = Entity(
    name="driver",
    join_keys=["driver_id"],
    description="Driver entity for ride-hailing features"
)

# Entity with composite key
user_merchant = Entity(
    name="user_merchant",
    join_keys=["user_id", "merchant_id"],
    description="User-merchant interaction features"
)
```

#### Entity Aliasing

Use aliases when entity dataframe columns don't match feature view columns:

```python
# Base entity
location = Entity(name="location", join_keys=["location_id"])

# Feature view
location_weather_fv = FeatureView(
    name="location_weather",
    entities=[location],
    schema=[
        Field(name="temperature", dtype=Float32),
        Field(name="humidity", dtype=Float32),
    ],
    source=weather_source
)

# Query with different column names using alias
entity_df = pd.DataFrame({
    "origin_location_id": [1, 2],  # Different column name
    "event_timestamp": pd.to_datetime(["2023-01-01", "2023-01-02"])
})

# Use join_key_map for aliasing
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=["location_weather:temperature"],
    full_feature_names=True
).to_df()
```

#### Cardinality Patterns

```python
# Zero entities: Global features
global_stats_fv = FeatureView(
    name="global_stats",
    entities=[],  # No entity - global features
    schema=[
        Field(name="total_active_users", dtype=Int64),
        Field(name="platform_avg_rating", dtype=Float32),
    ],
    source=global_stats_source
)

# Single entity: User-specific features
user_profile_fv = FeatureView(
    name="user_profile",
    entities=[user],
    schema=[
        Field(name="account_age_days", dtype=Int64),
        Field(name="lifetime_value", dtype=Float64),
    ],
    source=user_source
)

# Multiple entities: Composite features
user_merchant_fv = FeatureView(
    name="user_merchant_interactions",
    entities=[user, merchant],
    schema=[
        Field(name="purchase_count", dtype=Int64),
        Field(name="avg_order_value", dtype=Float64),
    ],
    source=interaction_source
)
```

### 2.2 Feature View Organization

#### Domain-Based Organization

```
feature_store/
├── feature_store.yaml
├── entities/
│   ├── __init__.py
│   ├── user.py
│   ├── driver.py
│   └── merchant.py
├── features/
│   ├── __init__.py
│   ├── user_features.py
│   ├── driver_features.py
│   ├── transaction_features.py
│   └── real_time_features.py
├── sources/
│   ├── __init__.py
│   ├── batch_sources.py
│   └── stream_sources.py
└── services/
    ├── __init__.py
    └── feature_services.py
```

#### Feature Services for Grouping

Group related features for specific use cases:

```python
from feast import FeatureService

# Service for fraud detection model
fraud_detection_service = FeatureService(
    name="fraud_detection_v1",
    features=[
        driver_hourly_stats[["trips_today", "earnings_today"]],
        user_transaction_stats[["avg_transaction_amount", "transaction_count_7d"]],
        real_time_location[["current_speed", "distance_from_home"]],
    ],
    tags={
        "model": "fraud_detection",
        "team": "trust_safety",
        "version": "1.0"
    }
)

# Service for recommendation model
recommendation_service = FeatureService(
    name="recommendation_v1",
    features=[
        user_preferences,
        item_embeddings,
        user_item_interactions,
    ]
)
```

### 2.3 Feature Naming Conventions

#### Recommended Patterns

```python
# Pattern: {entity}_{domain}_{feature_name}_{version}
# Examples:
"driver_activity_trips_today_v1"
"user_engagement_session_count_7d_v2"
"merchant_performance_rating_avg_v1"

# Pattern: {domain}_{aggregation}_{time_window}
# Examples:
"transaction_sum_amount_24h"
"login_count_7d"
"purchase_avg_value_30d"
```

#### Naming Best Practices

1. **Be descriptive**: `user_login_count_7d` not `cnt7`
2. **Include time windows**: `_24h`, `_7d`, `_30d`, `_lifetime`
3. **Specify aggregations**: `_sum`, `_avg`, `_max`, `_count`
4. **Use version suffixes**: `_v1`, `_v2`
5. **Indicate data type when ambiguous**: `_flag`, `_ratio`, `_pct`

### 2.4 Feature Groups and Domains

#### Project Namespacing

Each Feast project provides natural namespacing:

```yaml
# feature_store.yaml for user team
project: user_features
registry: s3://feast-registry/user-features
provider: aws
```

```yaml
# feature_store.yaml for merchant team
project: merchant_features
registry: s3://feast-registry/merchant-features
provider: aws
```

---

## 3. Operational Patterns

### 3.1 CI/CD for Feature Stores

#### GitHub Actions Workflow

```yaml
# .github/workflows/feast-apply.yml
name: Feast Apply

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  feast-plan:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install feast[redis,postgres]

      - name: Run feast plan
        run: |
          cd feature_store
          feast plan
        env:
          FEAST_REGISTRY: ${{ secrets.FEAST_REGISTRY }}

  feast-apply:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install feast[redis,postgres]

      - name: Run feast apply
        run: |
          cd feature_store
          feast apply
        env:
          FEAST_REGISTRY: ${{ secrets.FEAST_REGISTRY }}
```

#### Multi-Environment Structure

```
feature_store/
├── staging/
│   ├── feature_store.yaml
│   ├── entities.py
│   └── features.py
├── production/
│   ├── feature_store.yaml
│   ├── entities.py
│   └── features.py
└── .github/
    └── workflows/
        ├── staging.yml
        └── production.yml
```

**staging/feature_store.yaml:**
```yaml
project: my_project_staging
registry: s3://feast-registry-staging/registry.db
provider: aws
online_store:
  type: redis
  connection_string: ${REDIS_STAGING_URL}
offline_store:
  type: snowflake
  account: ${SNOWFLAKE_ACCOUNT}
  database: STAGING_DB
```

**production/feature_store.yaml:**
```yaml
project: my_project_production
registry: s3://feast-registry-prod/registry.db
provider: aws
online_store:
  type: redis
  connection_string: ${REDIS_PROD_URL}
offline_store:
  type: snowflake
  account: ${SNOWFLAKE_ACCOUNT}
  database: PRODUCTION_DB
```

### 3.2 Testing Features

#### Unit Testing Feature Definitions

```python
import pytest
from datetime import timedelta
from feast import Entity, FeatureView, Field
from feast.types import Int64, Float32

def test_feature_view_schema():
    """Test that feature view has expected schema."""
    driver = Entity(name="driver", join_keys=["driver_id"])

    fv = FeatureView(
        name="driver_stats",
        entities=[driver],
        schema=[
            Field(name="trips_today", dtype=Int64),
            Field(name="rating", dtype=Float32),
        ],
        ttl=timedelta(hours=2),
        source=mock_source
    )

    assert fv.name == "driver_stats"
    assert len(fv.schema) == 2
    assert fv.ttl == timedelta(hours=2)

def test_entity_join_keys():
    """Test entity configuration."""
    driver = Entity(name="driver", join_keys=["driver_id"])
    assert driver.join_keys == ["driver_id"]
```

#### Integration Testing with Feast

```python
import pandas as pd
from datetime import datetime, timedelta
from feast import FeatureStore

def test_historical_feature_retrieval():
    """Test point-in-time correct feature retrieval."""
    store = FeatureStore(".")

    entity_df = pd.DataFrame({
        "driver_id": [1001, 1002],
        "event_timestamp": [
            datetime.now() - timedelta(hours=1),
            datetime.now() - timedelta(hours=2)
        ]
    })

    features = store.get_historical_features(
        entity_df=entity_df,
        features=["driver_stats:trips_today"]
    ).to_df()

    assert "driver_id" in features.columns
    assert "trips_today" in features.columns
    assert len(features) == 2

def test_online_feature_retrieval():
    """Test online feature serving."""
    store = FeatureStore(".")

    features = store.get_online_features(
        features=["driver_stats:trips_today", "driver_stats:rating"],
        entity_rows=[{"driver_id": 1001}]
    ).to_dict()

    assert "trips_today" in features
    assert "rating" in features
```

### 3.3 Monitoring and Observability

#### StatsD Metrics Configuration

```yaml
# Helm chart values for Feast with metrics
metrics:
  enabled: true
  statsd:
    host: statsd-exporter.monitoring
    port: 9125
```

#### Key Metrics to Monitor

1. **Feature Serving Latency**: p50, p95, p99 latency for online feature retrieval
2. **Feature Freshness**: Time since last materialization
3. **Feature Coverage**: Percentage of requests with all features available
4. **Registry Sync**: Time since last registry update

#### Data Quality Monitoring with Great Expectations

```python
from feast import FeatureStore
from feast.dqm.profilers.ge_profiler import ge_profiler
from great_expectations.dataset import Dataset
from great_expectations.core.expectation_suite import ExpectationSuite

@ge_profiler
def feature_quality_profiler(dataset: Dataset) -> ExpectationSuite:
    """Define data quality expectations for features."""
    # Numeric range checks
    dataset.expect_column_values_to_be_between(
        "rating", min_value=0, max_value=5
    )

    # Null checks
    dataset.expect_column_values_to_not_be_null("driver_id")

    # Distribution checks
    dataset.expect_column_mean_to_be_between(
        "trips_today", min_value=0, max_value=100
    )

    return dataset.get_expectation_suite()

# Apply validation during feature retrieval
store = FeatureStore(".")
job = store.get_historical_features(
    entity_df=entity_df,
    features=["driver_stats:rating", "driver_stats:trips_today"]
)

# Validate against reference dataset
reference = store.get_saved_dataset("driver_stats_reference")
validated_df = job.to_df(
    validation_reference=reference.as_reference(profiler=feature_quality_profiler)
)
```

### 3.4 Schema Evolution

#### Adding New Features

```python
# Version 1: Original feature view
driver_stats_v1 = FeatureView(
    name="driver_stats",
    schema=[
        Field(name="trips_today", dtype=Int64),
        Field(name="rating", dtype=Float32),
    ],
    # ...
)

# Version 2: Add new feature (backward compatible)
driver_stats_v2 = FeatureView(
    name="driver_stats",
    schema=[
        Field(name="trips_today", dtype=Int64),
        Field(name="rating", dtype=Float32),
        Field(name="acceptance_rate", dtype=Float32),  # New feature
    ],
    # ...
)
```

#### Migration Strategy

1. **Deprecation Warning**: Tag old features with deprecation metadata
2. **Transition Period**: Run both old and new feature views simultaneously
3. **Consumer Migration**: Update all consumers to use new features
4. **Cleanup**: Remove deprecated features after all consumers migrate

```python
# Deprecated feature view with warning
driver_stats_old = FeatureView(
    name="driver_stats_v1",
    tags={
        "deprecated": "true",
        "deprecated_date": "2024-01-01",
        "migration_guide": "Use driver_stats_v2 instead",
        "removal_date": "2024-03-01"
    },
    # ... configuration
)
```

---

## 4. Integration Patterns

### 4.1 Training Pipeline Integration

#### Airflow DAG Example

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def materialize_features():
    """Materialize features to online store."""
    from feast import FeatureStore
    store = FeatureStore("/opt/airflow/feature_store")
    store.materialize_incremental(datetime.now())

def generate_training_data():
    """Generate training dataset with features."""
    import pandas as pd
    from feast import FeatureStore

    store = FeatureStore("/opt/airflow/feature_store")

    # Load entity dataframe with labels
    entity_df = pd.read_parquet("s3://data/training_entities.parquet")

    # Get features
    training_df = store.get_historical_features(
        entity_df=entity_df,
        features=[
            "driver_stats:trips_today",
            "driver_stats:rating",
            "user_stats:lifetime_value"
        ]
    ).to_df()

    # Save training dataset
    training_df.to_parquet("s3://data/training_dataset.parquet")

with DAG(
    "feature_training_pipeline",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False
) as dag:

    materialize = PythonOperator(
        task_id="materialize_features",
        python_callable=materialize_features
    )

    generate_data = PythonOperator(
        task_id="generate_training_data",
        python_callable=generate_training_data
    )

    materialize >> generate_data
```

### 4.2 Inference Pipeline Integration

#### Online Inference with Feature Server

```python
from feast import FeatureStore
import numpy as np

class FraudDetectionService:
    def __init__(self):
        self.store = FeatureStore(".")
        self.model = self._load_model()

    def predict(self, user_id: int, transaction_amount: float) -> dict:
        # Get online features
        features = self.store.get_online_features(
            features=[
                "user_stats:transaction_count_7d",
                "user_stats:avg_transaction_amount",
                "user_stats:fraud_flag_count"
            ],
            entity_rows=[{"user_id": user_id}]
        ).to_dict()

        # Prepare feature vector
        feature_vector = np.array([
            features["transaction_count_7d"][0],
            features["avg_transaction_amount"][0],
            features["fraud_flag_count"][0],
            transaction_amount
        ])

        # Make prediction
        prediction = self.model.predict([feature_vector])[0]

        return {
            "user_id": user_id,
            "fraud_probability": float(prediction),
            "features_used": features
        }
```

#### Batch Inference Pipeline

```python
import pandas as pd
from feast import FeatureStore

def batch_inference():
    """Run batch inference on all users."""
    store = FeatureStore(".")

    # Get all users for scoring
    entity_df = pd.read_sql(
        "SELECT user_id, CURRENT_TIMESTAMP as event_timestamp FROM users",
        connection
    )

    # Retrieve features
    features_df = store.get_historical_features(
        entity_df=entity_df,
        features=[
            "user_stats:lifetime_value",
            "user_stats:churn_risk_score",
            "user_behavior:session_count_30d"
        ]
    ).to_df()

    # Load model and predict
    model = load_model("churn_model")
    predictions = model.predict(features_df[feature_columns])

    # Save predictions
    results = pd.DataFrame({
        "user_id": entity_df["user_id"],
        "churn_prediction": predictions,
        "prediction_timestamp": datetime.now()
    })
    results.to_parquet("s3://predictions/churn_batch.parquet")
```

### 4.3 Batch vs Real-Time Serving

#### Decision Framework

| Pattern | Use Case | Latency | Freshness | Cost |
|---------|----------|---------|-----------|------|
| Batch Materialization | Daily scoring, training | Minutes-Hours | Hours-Days | Low |
| Online Serving | Real-time predictions | Milliseconds | Seconds-Minutes | Medium |
| Stream Processing | Near real-time | Seconds | Seconds | High |
| Precomputed Predictions | High-volume, static entities | Milliseconds | Hours-Days | Low |

#### Hybrid Pattern Example

```python
from feast import FeatureStore
import redis

class HybridScoringService:
    def __init__(self):
        self.store = FeatureStore(".")
        self.cache = redis.Redis(host='localhost', port=6379)
        self.model = self._load_model()

    def get_prediction(self, user_id: int) -> float:
        # Check cache for precomputed prediction
        cached = self.cache.get(f"prediction:{user_id}")
        if cached:
            return float(cached)

        # Fall back to real-time inference
        features = self.store.get_online_features(
            features=["user_stats:all_features"],
            entity_rows=[{"user_id": user_id}]
        ).to_dict()

        prediction = self.model.predict([list(features.values())])[0]

        # Cache for future requests
        self.cache.setex(f"prediction:{user_id}", 3600, prediction)

        return prediction
```

### 4.4 Data Quality Validation

#### Validation in Training Pipeline

```python
from feast import FeatureStore
from feast.dqm.profilers.ge_profiler import ge_profiler
from great_expectations.dataset import Dataset
from great_expectations.core.expectation_suite import ExpectationSuite

@ge_profiler
def training_data_profiler(dataset: Dataset) -> ExpectationSuite:
    """Comprehensive data quality checks for training data."""

    # Schema validation
    dataset.expect_table_columns_to_match_ordered_list([
        "driver_id", "trips_today", "rating", "event_timestamp"
    ])

    # Completeness checks
    dataset.expect_column_values_to_not_be_null("driver_id")
    dataset.expect_column_values_to_not_be_null("rating")

    # Range validation
    dataset.expect_column_values_to_be_between("rating", 1, 5)
    dataset.expect_column_values_to_be_between("trips_today", 0, 100)

    # Distribution checks (detect drift)
    dataset.expect_column_mean_to_be_between("rating", 3.5, 4.5)
    dataset.expect_column_stdev_to_be_between("trips_today", 5, 20)

    # Uniqueness
    dataset.expect_compound_columns_to_be_unique(
        ["driver_id", "event_timestamp"]
    )

    return dataset.get_expectation_suite()

# Usage
store = FeatureStore(".")

try:
    training_df = store.get_historical_features(
        entity_df=entity_df,
        features=["driver_stats:trips_today", "driver_stats:rating"]
    ).to_df(
        validation_reference=store.get_saved_dataset("reference_data")
            .as_reference(profiler=training_data_profiler)
    )
except ValidationFailed as e:
    print(f"Data quality check failed: {e}")
    # Alert on-call, skip training, or use fallback data
```

#### Continuous Monitoring Pattern

```python
from datetime import datetime, timedelta
from feast import FeatureStore
import logging

def monitor_feature_freshness():
    """Monitor feature freshness and alert if stale."""
    store = FeatureStore(".")

    # Get last materialization time
    registry = store.registry
    feature_views = registry.list_feature_views(project=store.project)

    alerts = []
    for fv in feature_views:
        last_updated = registry.get_materialization_intervals(
            fv.name, store.project
        )

        if last_updated:
            latest = max(interval.end_time for interval in last_updated)
            staleness = datetime.utcnow() - latest

            if staleness > timedelta(hours=fv.ttl.total_seconds() / 3600 * 0.5):
                alerts.append({
                    "feature_view": fv.name,
                    "last_updated": latest,
                    "staleness_hours": staleness.total_seconds() / 3600
                })

    if alerts:
        logging.warning(f"Stale features detected: {alerts}")
        # Send to alerting system
```

---

## Common Anti-Patterns to Avoid

### 1. Not Using Point-in-Time Joins
**Anti-pattern**: Using latest feature values for all training rows
**Solution**: Always use `get_historical_features()` with timestamps

### 2. Over-Engineering Feature Views
**Anti-pattern**: One feature view per feature
**Solution**: Group semantically related features in single feature views

### 3. Ignoring TTL Configuration
**Anti-pattern**: Setting very long TTLs or no TTL
**Solution**: Set appropriate TTLs based on feature freshness requirements

### 4. Not Versioning Features
**Anti-pattern**: Modifying features in place
**Solution**: Use version suffixes and maintain backward compatibility

### 5. Tight Coupling to Serving Layer
**Anti-pattern**: Direct database queries instead of Feast abstractions
**Solution**: Always use Feast SDK for feature retrieval

### 6. Skipping Data Validation
**Anti-pattern**: Trusting upstream data blindly
**Solution**: Implement Great Expectations validation in pipelines

### 7. Ignoring Feature Lineage
**Anti-pattern**: Not tracking feature dependencies
**Solution**: Use tags and documentation to maintain lineage

---

## Quick Reference Commands

```bash
# Initialize new feature repository
feast init my_feature_repo

# Apply feature definitions to registry
feast apply

# Plan changes without applying
feast plan

# Materialize features to online store
feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")

# Serve features via HTTP
feast serve

# View registered features
feast registry-dump

# Validate feature definitions
feast validate
```

---

## Resources

- **Official Documentation**: https://docs.feast.dev/
- **GitHub Repository**: https://github.com/feast-dev/feast
- **Tutorials**: https://docs.feast.dev/tutorials/tutorials-overview
- **Community Slack**: https://feast-slack.slack.com/


> Source: `docs/data_engineering/feast/feast-sdk-api-research.md`

# Feast SDK, APIs, and Ontologies - Comprehensive Research

## Table of Contents

1. [Python SDK - FeatureStore Class](#python-sdk---featurestore-class)
2. [Feature Retrieval APIs](#feature-retrieval-apis)
3. [Core Objects and Ontology](#core-objects-and-ontology)
4. [Type System](#type-system)
5. [Data Sources](#data-sources)
6. [Configuration](#configuration)
7. [Online Stores](#online-stores)
8. [Offline Stores](#offline-stores)
9. [CLI Commands](#cli-commands)

---

## Python SDK - FeatureStore Class

### Class Definition

```python
class feast.feature_store.FeatureStore(
    repo_path: Optional[str] = None,
    config: Optional[feast.repo_config.RepoConfig] = None
)
```

**Description**: A FeatureStore object is used to define, create, and retrieve features. It serves as the main entry point for all Feast operations.

### Core Methods

#### `apply()`

Registers objects to metadata store and updates related infrastructure.

```python
def apply(
    self,
    objects: Union[
        Entity,
        FeatureView,
        OnDemandFeatureView,
        StreamFeatureView,
        FeatureService,
        List[Union[Entity, FeatureView, OnDemandFeatureView, StreamFeatureView, FeatureService]]
    ],
    commit: bool = True
) -> None
```

**Parameters:**
- `objects`: One or more Feast objects to register
- `commit`: Whether to commit changes to the registry

**Description**: Registers one or more definitions (e.g., Entity, FeatureView) and updates these objects in the Feast registry. Once the registry has been updated, the apply method will update related infrastructure (e.g., create tables in an online store).

**Example:**
```python
from feast import FeatureStore, Entity, FeatureView, Field
from feast.types import Int64, Float32

fs = FeatureStore(repo_path=".")

driver = Entity(name="driver", join_keys=["driver_id"])
driver_stats = FeatureView(
    name="driver_stats",
    entities=[driver],
    schema=[
        Field(name="trips_today", dtype=Int64),
        Field(name="rating", dtype=Float32),
    ],
    source=parquet_source
)

fs.apply([driver, driver_stats])
```

---

#### `plan()`

Dry-runs registration and produces a list of changes.

```python
def plan(
    self,
    objects: List[Union[Entity, FeatureView, OnDemandFeatureView, StreamFeatureView, FeatureService]]
) -> Tuple[RegistryDiff, InfraDiff]
```

**Description**: Dry-runs registering one or more definitions and produces a list of all the changes that would be introduced in the feature repo. Changes are for informational purposes and not actually applied.

---

#### `get_historical_features()`

Retrieves historical feature values for training or batch scoring.

```python
def get_historical_features(
    self,
    entity_df: Union[pd.DataFrame, str],
    features: Union[List[str], FeatureService],
    full_feature_names: bool = False
) -> RetrievalJob
```

**Parameters:**
- `entity_df`: A DataFrame or SQL query containing entity keys and timestamps
- `features`: List of feature references or a FeatureService
- `full_feature_names`: If True, returns feature names prefixed with feature view name

**Returns**: `RetrievalJob` - Call `.to_df()` or `.to_arrow()` to get results

**Entity DataFrame Requirements:**
- Must include entity key columns (e.g., `driver_id`)
- Must include event timestamp column indicating when the event occurred

**Example:**
```python
from datetime import datetime
import pandas as pd

entity_df = pd.DataFrame.from_dict({
    "driver_id": [1001, 1002, 1003],
    "event_timestamp": [
        datetime(2021, 4, 12, 10, 59, 42),
        datetime(2021, 4, 12, 8, 12, 10),
        datetime(2021, 4, 12, 16, 40, 26),
    ]
})

training_df = fs.get_historical_features(
    entity_df=entity_df,
    features=[
        "driver_hourly_stats:trips_today",
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate"
    ]
).to_df()

# Using FeatureService
training_df = fs.get_historical_features(
    entity_df=entity_df,
    features=fs.get_feature_service("driver_activity")
).to_df()
```

---

#### `get_online_features()`

Retrieves the latest online feature data for real-time inference.

```python
def get_online_features(
    self,
    features: Union[List[str], FeatureService],
    entity_rows: List[Dict[str, Any]],
    full_feature_names: bool = False
) -> OnlineResponse
```

**Parameters:**
- `features`: List of feature references (format: `"feature_view:feature"`) or FeatureService
- `entity_rows`: List of dictionaries containing entity keys
- `full_feature_names`: If True, returns feature names prefixed with feature view name

**Returns**: `OnlineResponse` - Call `.to_dict()` or `.to_df()` to get results

**Note**: Unlike `get_historical_features`, entity_rows do not need timestamps since only the latest feature value per entity key is retrieved.

**Example:**
```python
# Using feature references
features = fs.get_online_features(
    features=[
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:trips_today"
    ],
    entity_rows=[
        {"driver_id": 1001},
        {"driver_id": 1002}
    ]
).to_dict()

# Using FeatureService
feature_service = fs.get_feature_service("driver_activity")
features = fs.get_online_features(
    features=feature_service,
    entity_rows=[{"driver_id": 1001}]
).to_dict()
```

---

#### `materialize()`

Materializes feature data from offline to online store.

```python
def materialize(
    self,
    start_date: datetime,
    end_date: datetime,
    feature_views: Optional[List[str]] = None
) -> None
```

**Parameters:**
- `start_date`: Start date for time range of data to materialize
- `end_date`: End date for time range of data to materialize
- `feature_views`: Optional list of feature view names to materialize (if not specified, materializes all)

**Example:**
```python
from datetime import datetime

fs.materialize(
    start_date=datetime(2021, 1, 1),
    end_date=datetime(2021, 12, 31),
    feature_views=["driver_hourly_stats"]
)
```

---

#### `materialize_incremental()`

Materializes incrementally from last materialization time.

```python
def materialize_incremental(
    self,
    end_date: datetime,
    feature_views: Optional[List[str]] = None
) -> None
```

**Parameters:**
- `end_date`: End date for materialization
- `feature_views`: Optional list of feature view names

**Description**: The start time is either the most recent end time of a prior materialization or `(now - ttl)` if no prior materialization exists.

---

#### `push()`

Pushes feature data to online and/or offline stores.

```python
def push(
    self,
    push_source_name: str,
    df: pd.DataFrame,
    to: PushMode = PushMode.ONLINE,
    allow_registry_cache: bool = True
) -> None
```

**Parameters:**
- `push_source_name`: Name of the push source
- `df`: DataFrame containing feature data (must include entity columns and timestamps)
- `to`: Target store(s) - `PushMode.ONLINE`, `PushMode.OFFLINE`, or `PushMode.ONLINE_AND_OFFLINE`
- `allow_registry_cache`: Whether to use cached registry

**Example:**
```python
from feast.data_source import PushMode
import pandas as pd

feature_data = pd.DataFrame({
    "driver_id": [1001, 1002],
    "trips_today": [5, 10],
    "event_timestamp": [datetime.now(), datetime.now()]
})

fs.push(
    push_source_name="driver_stats_push",
    df=feature_data,
    to=PushMode.ONLINE_AND_OFFLINE
)
```

---

#### `retrieve_online_documents()`

Vector similarity search for RAG applications.

```python
def retrieve_online_documents(
    self,
    features: List[str],
    query: str,
    top_k: int = 10
) -> OnlineResponse
```

**Example:**
```python
results = fs.retrieve_online_documents(
    features=["documents:embedding"],
    query="What is the biggest city in the USA?",
    top_k=5
).to_dict()
```

---

#### `get_feature_service()`

Retrieves a feature service by name.

```python
def get_feature_service(
    self,
    name: str,
    allow_cache: bool = False
) -> FeatureService
```

---

#### Additional FeatureStore Methods

| Method | Description |
|--------|-------------|
| `get_entity(name)` | Retrieves an entity by name |
| `get_feature_view(name)` | Retrieves a feature view by name |
| `get_on_demand_feature_view(name)` | Retrieves an on-demand feature view |
| `get_stream_feature_view(name)` | Retrieves a stream feature view |
| `list_entities()` | Lists all registered entities |
| `list_feature_views()` | Lists all registered feature views |
| `list_on_demand_feature_views()` | Lists all on-demand feature views |
| `list_stream_feature_views()` | Lists all stream feature views |
| `list_feature_services()` | Lists all feature services |
| `list_data_sources()` | Lists all data sources |
| `delete_feature_view(name)` | Deletes a feature view |
| `delete_feature_service(name)` | Deletes a feature service |
| `teardown()` | Tears down infrastructure |

---

## Feature Retrieval APIs

### RetrievalJob

Returned by `get_historical_features()`.

**Methods:**
- `.to_df()` - Returns a pandas DataFrame
- `.to_arrow()` - Returns a PyArrow Table
- `.to_sql()` - Returns SQL query (for SQL-backed offline stores)

### OnlineResponse

Returned by `get_online_features()`.

**Methods:**
- `.to_dict()` - Returns a dictionary
- `.to_df()` - Returns a pandas DataFrame

### Feature References

Feature references use the format: `<feature_view>:<feature>`

```python
features = [
    "driver_hourly_stats:trips_today",
    "driver_hourly_stats:conv_rate"
]
```

### Feature Server HTTP API

Start with: `feast serve`

**Endpoint**: `POST /get-online-features`

```python
import requests
import json

request = {
    "features": [
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:trips_today"
    ],
    "entities": {
        "driver_id": [1001, 1002]
    }
}

response = requests.post(
    'http://localhost:6566/get-online-features',
    data=json.dumps(request)
)
```

---

## Core Objects and Ontology

### Entity

Defines a collection of semantically related features and serves as a primary key for feature retrieval.

```python
class feast.entity.Entity(
    *,
    name: str,
    join_keys: Optional[List[str]] = None,
    value_type: Optional[ValueType] = None,
    description: str = '',
    tags: Optional[Dict[str, str]] = None,
    owner: str = ''
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique name of the entity |
| `join_keys` | `List[str]` | List of properties that uniquely identify entities (currently supports size one) |
| `value_type` | `ValueType` | Type of entity (inferred from data source if not specified) |
| `description` | `str` | Human-readable description |
| `tags` | `Dict[str, str]` | Key-value pairs for arbitrary metadata |
| `owner` | `str` | Email of primary maintainer |

**Example:**
```python
from feast import Entity
from feast.value_type import ValueType

driver = Entity(
    name="driver",
    join_keys=["driver_id"],
    value_type=ValueType.INT64,
    description="Driver entity for ride-hailing service",
    tags={"team": "driver-features"},
    owner="ml-team@company.com"
)
```

---

### FeatureView

Defines a logical grouping of servable features.

```python
class feast.feature_view.FeatureView(
    *,
    name: str,
    entities: List[Entity] = [],
    ttl: Optional[timedelta] = None,
    source: DataSource = None,
    schema: Optional[List[Field]] = None,
    online: bool = True,
    description: str = '',
    tags: Optional[Dict[str, str]] = None,
    owner: str = ''
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique name of the feature view |
| `entities` | `List[Entity]` | List of entities (can be empty for global features) |
| `ttl` | `timedelta` | Time-to-live for features; `timedelta(0)` means infinite |
| `source` | `DataSource` | Data source (FileSource, BigQuerySource, etc.) |
| `schema` | `List[Field]` | List of Field definitions (inferred if not specified) |
| `online` | `bool` | Whether to materialize to online store |
| `description` | `str` | Human-readable description |
| `tags` | `Dict[str, str]` | Arbitrary metadata |
| `owner` | `str` | Email of primary maintainer |

**Example:**
```python
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Int64, Float32
from datetime import timedelta

driver = Entity(name="driver", join_keys=["driver_id"])

driver_hourly_stats = FeatureView(
    name="driver_hourly_stats",
    entities=[driver],
    ttl=timedelta(hours=2),
    schema=[
        Field(name="trips_today", dtype=Int64),
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
    ],
    source=FileSource(
        path="data/driver_stats.parquet",
        timestamp_field="event_timestamp",
    ),
    online=True,
    description="Hourly driver statistics",
    tags={"team": "driver-features"},
    owner="ml-team@company.com"
)
```

**Feature View Without Entities (Global Features):**
```python
global_stats = FeatureView(
    name="global_stats",
    entities=[],
    schema=[
        Field(name="total_trips_today", dtype=Int64),
    ],
    source=BigQuerySource(table="project.dataset.global_stats")
)
```

---

### BatchFeatureView

Defines a logical group of features with only a batch data source.

```python
class feast.batch_feature_view.BatchFeatureView(
    *,
    name: str,
    entities: List[Entity] = [],
    ttl: Optional[timedelta] = None,
    source: DataSource,
    schema: Optional[List[Field]] = None,
    online: bool = True,
    description: str = '',
    tags: Optional[Dict[str, str]] = None,
    owner: str = ''
)
```

---

### StreamFeatureView

Handles both stream and batch data sources for fresher online features.

```python
class feast.stream_feature_view.StreamFeatureView(
    *,
    name: str,
    entities: List[Entity] = [],
    ttl: Optional[timedelta] = None,
    source: KafkaSource | KinesisSource,
    schema: Optional[List[Field]] = None,
    aggregations: Optional[List[Aggregation]] = None,
    mode: str = "spark",
    timestamp_field: str = "",
    online: bool = True,
    description: str = '',
    tags: Optional[Dict[str, str]] = None,
    owner: str = ''
)
```

---

### OnDemandFeatureView

Enables lightweight transformations at retrieval time.

```python
class feast.on_demand_feature_view.OnDemandFeatureView(
    *,
    name: str,
    schema: List[Field],
    sources: Dict[str, Union[FeatureView, RequestSource]],
    udf: Callable,
    description: str = '',
    tags: Optional[Dict[str, str]] = None,
    owner: str = ''
)
```

**Parameters:**
- `sources`: Map from source names to FeatureView or RequestSource
- `udf`: User-defined transformation function (must take pandas DataFrames as inputs)

**Example:**
```python
from feast import on_demand_feature_view, Field
from feast.types import Float32

@on_demand_feature_view(
    sources=[driver_hourly_stats],
    schema=[
        Field(name="conv_rate_plus_acc", dtype=Float32),
    ]
)
def transformed_conv_rate(inputs: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df["conv_rate_plus_acc"] = inputs["conv_rate"] + inputs["acc_rate"]
    return df
```

---

### Field

Defines feature schema with name and type.

```python
class feast.field.Field(
    *,
    name: str,
    dtype: FeastType,
    description: str = '',
    tags: Optional[Dict[str, str]] = None
)
```

**Example:**
```python
from feast import Field
from feast.types import Int64, Float32, String, Bool

fields = [
    Field(name="trips_today", dtype=Int64),
    Field(name="rating", dtype=Float32),
    Field(name="name", dtype=String),
    Field(name="is_active", dtype=Bool),
]
```

---

### FeatureService

Groups features from multiple feature views for a specific model.

```python
class feast.feature_service.FeatureService(
    *,
    name: str,
    features: List[Union[FeatureView, OnDemandFeatureView]],
    description: str = '',
    tags: Optional[Dict[str, str]] = None,
    owner: str = ''
)
```

**Example:**
```python
from feast import FeatureService

driver_activity_service = FeatureService(
    name="driver_activity",
    features=[
        driver_hourly_stats,
        driver_ratings[["lifetime_rating"]],  # Select specific features
    ],
    description="Features for driver activity model",
    owner="ml-team@company.com"
)
```

---

## Type System

### PrimitiveFeastType Enum

```python
class feast.types.PrimitiveFeastType(enum.Enum):
    INVALID = 0
    BYTES = 1
    STRING = 2
    INT32 = 3
    INT64 = 4
    FLOAT64 = 5
    FLOAT32 = 6
    BOOL = 7
    UNIX_TIMESTAMP = 8
```

### Type Aliases

Convenient module-level type aliases from `feast.types`:

| Alias | Type |
|-------|------|
| `Invalid` | `PrimitiveFeastType.INVALID` |
| `Bytes` | `PrimitiveFeastType.BYTES` |
| `String` | `PrimitiveFeastType.STRING` |
| `Bool` | `PrimitiveFeastType.BOOL` |
| `Int32` | `PrimitiveFeastType.INT32` |
| `Int64` | `PrimitiveFeastType.INT64` |
| `Float32` | `PrimitiveFeastType.FLOAT32` |
| `Float64` | `PrimitiveFeastType.FLOAT64` |
| `UnixTimestamp` | `PrimitiveFeastType.UNIX_TIMESTAMP` |

**Usage:**
```python
from feast.types import Int64, Float32, String, Bool, Bytes, UnixTimestamp
```

### Array Types

For list/array types, use the `Array` class:

```python
from feast.types import Array, Int64, Float32

schema = [
    Field(name="embedding", dtype=Array(Float32)),
    Field(name="tags", dtype=Array(String)),
]
```

### ValueType Enum (Legacy)

```python
class feast.value_type.ValueType(enum.Enum):
    UNKNOWN = 0
    BYTES = 1
    STRING = 2
    INT32 = 3
    INT64 = 4
    DOUBLE = 5
    FLOAT = 6
    BOOL = 7
    UNIX_TIMESTAMP = 8
    BYTES_LIST = 11
    STRING_LIST = 12
    INT32_LIST = 13
    INT64_LIST = 14
    DOUBLE_LIST = 15
    FLOAT_LIST = 16
    BOOL_LIST = 17
    UNIX_TIMESTAMP_LIST = 18
```

### Type Mapping (Python to Feast)

| Python/NumPy Type | Feast ValueType |
|-------------------|-----------------|
| `int` | `INT64` |
| `str` | `STRING` |
| `float` | `DOUBLE` |
| `bytes` | `BYTES` |
| `float64` | `DOUBLE` |
| `float32` | `FLOAT` |
| `int64` | `INT64` |
| `int32` | `INT32` |
| `bool` | `BOOL` |
| `boolean` | `BOOL` |
| `timedelta` | `UNIX_TIMESTAMP` |

---

## Data Sources

### Core Batch Data Sources

#### FileSource

For local Parquet/Delta files:

```python
from feast import FileSource
from feast.data_format import ParquetFormat

source = FileSource(
    path="data/driver_stats.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
    file_format=ParquetFormat(),
    description="Driver statistics",
    tags={"source": "data-lake"},
    owner="data-team@company.com"
)
```

#### BigQuerySource

```python
from feast import BigQuerySource

source = BigQuerySource(
    table="project.dataset.driver_stats",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
    query="SELECT * FROM project.dataset.driver_stats WHERE is_active = TRUE",
)
```

#### SnowflakeSource

```python
from feast.infra.offline_stores.snowflake_source import SnowflakeSource

source = SnowflakeSource(
    database="FEAST_DB",
    schema="PUBLIC",
    table="DRIVER_STATS",
    timestamp_field="EVENT_TIMESTAMP",
)
```

#### RedshiftSource

```python
from feast.infra.offline_stores.redshift_source import RedshiftSource

source = RedshiftSource(
    database="feast",
    schema="public",
    table="driver_stats",
    timestamp_field="event_timestamp",
)
```

#### SparkSource (Community)

```python
from feast.infra.offline_stores.contrib.spark_offline_store.spark_source import SparkSource

source = SparkSource(
    table="driver_stats",
    timestamp_field="event_timestamp",
)
```

### Stream Data Sources

#### KafkaSource

```python
from feast.data_source import KafkaSource

kafka_source = KafkaSource(
    name="driver_stats_stream",
    kafka_bootstrap_servers="localhost:9092",
    topic="driver_stats",
    timestamp_field="event_timestamp",
    batch_source=BigQuerySource(table="project.dataset.driver_stats"),
    message_format=AvroFormat(schema_json="..."),
)
```

#### KinesisSource

```python
from feast.data_source import KinesisSource

kinesis_source = KinesisSource(
    name="driver_stats_stream",
    stream_name="driver-stats-stream",
    region="us-east-1",
    timestamp_field="event_timestamp",
    batch_source=BigQuerySource(table="project.dataset.driver_stats"),
)
```

### PushSource

For real-time feature updates:

```python
from feast.data_source import PushSource

push_source = PushSource(
    name="driver_stats_push",
    batch_source=BigQuerySource(table="project.dataset.driver_stats"),
)
```

### RequestSource

For request-time data in on-demand feature views:

```python
from feast import RequestSource

input_request = RequestSource(
    name="request_data",
    schema=[
        Field(name="driver_trip_distance", dtype=Float32),
    ]
)
```

---

## Configuration

### feature_store.yaml Structure

```yaml
project: my_feature_project
registry: data/registry.db
provider: local
online_store:
  type: sqlite
  path: data/online_store.db
offline_store:
  type: file
entity_key_serialization_version: 2
```

### Configuration Options

#### Project

```yaml
project: my_feature_project
```

- Defines namespace for the feature store
- Used to isolate multiple deployments
- Should only contain letters, numbers, and underscores

#### Registry Options

**Local File:**
```yaml
registry: data/registry.db
```

**S3:**
```yaml
registry:
  path: s3://my-bucket/registry.pb
  cache_ttl_seconds: 60
```

**GCS:**
```yaml
registry:
  path: gs://my-bucket/registry.pb
  cache_ttl_seconds: 60
```

**SQL (PostgreSQL):**
```yaml
registry:
  registry_type: sql
  path: postgresql://user:password@localhost:5432/feast
  cache_ttl_seconds: 60
  sqlalchemy_config_kwargs:
    echo: false
    pool_pre_ping: true
```

**PostgreSQL Registry Store:**
```yaml
registry:
  registry_store_type: PostgreSQLRegistryStore
  path: feast_registry
  host: localhost
  port: 5432
  database: feast
  db_schema: public
  user: feast
  password: feast
```

#### Provider Options

| Provider | Description | Default Stores |
|----------|-------------|----------------|
| `local` | Local development | File offline, SQLite online |
| `gcp` | Google Cloud Platform | BigQuery offline, Datastore online |
| `aws` | Amazon Web Services | Redshift offline, DynamoDB online |

#### Entity Key Serialization

```yaml
entity_key_serialization_version: 2
```

Version 2 is recommended for new projects.

### Complete Configuration Examples

#### Local Development

```yaml
project: driver_features
registry: data/registry.db
provider: local
online_store:
  type: sqlite
  path: data/online_store.db
offline_store:
  type: file
```

#### AWS Production

```yaml
project: driver_features
registry:
  path: s3://feast-bucket/registry.pb
  cache_ttl_seconds: 60
provider: aws
online_store:
  type: dynamodb
  region: us-east-1
offline_store:
  type: redshift
  cluster_id: my-redshift-cluster
  region: us-east-1
  database: feast
  user: admin
  s3_staging_location: s3://feast-bucket/staging/
  iam_role: arn:aws:iam::123456789:role/redshift-role
```

#### GCP Production

```yaml
project: driver_features
registry:
  path: gs://feast-bucket/registry.pb
  cache_ttl_seconds: 60
provider: gcp
online_store:
  type: datastore
  project_id: my-gcp-project
offline_store:
  type: bigquery
  project_id: my-gcp-project
  dataset: feast_dataset
```

#### Snowflake

```yaml
project: driver_features
registry: data/registry.db
provider: local
offline_store:
  type: snowflake.offline
  account: myaccount.us-east-1
  user: feast_user
  password: feast_password
  role: SYSADMIN
  warehouse: COMPUTE_WH
  database: FEAST_DB
  schema: PUBLIC
online_store:
  type: sqlite
  path: data/online_store.db
```

#### PostgreSQL (All-in-One)

```yaml
project: driver_features
registry:
  registry_type: sql
  path: postgresql://feast:feast@localhost:5432/feast
  cache_ttl_seconds: 60
provider: local
offline_store:
  type: postgres
  host: localhost
  port: 5432
  database: feast
  db_schema: public
  user: feast
  password: feast
online_store:
  type: postgres
  host: localhost
  port: 5432
  database: feast
  db_schema: public
  user: feast
  password: feast
```

---

## Online Stores

### SQLite (Default Local)

```yaml
online_store:
  type: sqlite
  path: data/online_store.db
```

### Redis

```yaml
online_store:
  type: redis
  connection_string: localhost:6379
  # Optional
  key_ttl_seconds: 86400
```

**Redis Cluster:**
```yaml
online_store:
  type: redis
  connection_string: redis1:6379,redis2:6379,redis3:6379
  redis_type: redis_cluster
```

**Redis Sentinel:**
```yaml
online_store:
  type: redis
  connection_string: localhost:26379
  redis_type: redis_sentinel
  sentinel_master: mymaster
```

### PostgreSQL

```yaml
online_store:
  type: postgres
  host: localhost
  port: 5432
  database: feast
  db_schema: public
  user: feast_user
  password: feast_password
  # Optional SSL
  sslmode: require
  sslcert_path: /path/to/client-cert.pem
  sslkey_path: /path/to/client-key.pem
  sslrootcert_path: /path/to/ca-cert.pem
  # Optional PGVector support
  vector_enabled: true
```

### DynamoDB

```yaml
online_store:
  type: dynamodb
  region: us-east-1
  # Optional
  table_name_template: feast_{project}_{table_name}
```

**Required IAM Permissions:**
- `dynamodb:CreateTable`
- `dynamodb:DescribeTable`
- `dynamodb:DeleteTable`
- `dynamodb:BatchWriteItem`
- `dynamodb:BatchGetItem`

### Cassandra / Astra DB

```yaml
online_store:
  type: cassandra
  hosts:
    - 192.168.1.1
    - 192.168.1.2
  port: 9042
  keyspace: feast_keyspace
  username: cassandra_user
  password: cassandra_password
  # Optional
  protocol_version: 4
  load_balancing:
    local_dc: datacenter1
```

**Astra DB:**
```yaml
online_store:
  type: cassandra
  secure_bundle_path: /path/to/secure-connect-bundle.zip
  keyspace: feast_keyspace
  username: token
  password: AstraCS:...
```

### Datastore (GCP)

```yaml
online_store:
  type: datastore
  project_id: my-gcp-project
  # Optional
  namespace: feast
```

### Bigtable (GCP)

```yaml
online_store:
  type: bigtable
  project_id: my-gcp-project
  instance: feast-instance
```

---

## Offline Stores

### File (Parquet)

```yaml
offline_store:
  type: file
```

### BigQuery

```yaml
offline_store:
  type: bigquery
  project_id: my-gcp-project
  dataset: feast_dataset
  # Optional
  location: US
```

### Redshift

```yaml
offline_store:
  type: redshift
  cluster_id: my-redshift-cluster
  region: us-east-1
  database: feast
  user: admin
  s3_staging_location: s3://feast-bucket/staging/
  iam_role: arn:aws:iam::123456789:role/redshift-role
```

### Snowflake

```yaml
offline_store:
  type: snowflake.offline
  account: myaccount.us-east-1
  user: feast_user
  password: feast_password
  role: SYSADMIN
  warehouse: COMPUTE_WH
  database: FEAST_DB
  schema: PUBLIC
```

### PostgreSQL

```yaml
offline_store:
  type: postgres
  host: localhost
  port: 5432
  database: feast
  db_schema: public
  user: feast_user
  password: feast_password
```

### Spark (Community)

```yaml
offline_store:
  type: spark
  spark_conf:
    spark.master: local[*]
    spark.ui.enabled: "false"
```

---

## CLI Commands

### Global Options

```bash
feast [OPTIONS] COMMAND [ARGS]...
```

| Option | Description |
|--------|-------------|
| `-c, --chdir TEXT` | Switch to a different feature repository directory |
| `--help` | Show help message |

### Commands Reference

#### `feast init`

Creates a new Feast repository.

```bash
feast init [OPTIONS] REPO_NAME

Options:
  -m, --minimal              Create empty project repository
  -t, --template TEXT        Template to use (default: local)
                             Options: local, gcp, aws, snowflake, spark,
                             postgres, hbase, cassandra, rockset, hazelcast
```

**Examples:**
```bash
feast init my_feature_repo
feast init -t gcp my_gcp_repo
feast init -t postgres my_postgres_repo
feast init --minimal empty_repo
```

#### `feast apply`

Registers objects and updates infrastructure.

```bash
feast apply [OPTIONS]

Options:
  --skip-source-validation   Skip validation of data sources
```

**Description**: Scans Python files for Feast object definitions, validates them, syncs metadata to registry, and deploys necessary infrastructure.

#### `feast materialize`

Materializes data for a specific time range.

```bash
feast materialize [OPTIONS] START_DATE END_DATE

Options:
  -v, --views TEXT           Feature views to materialize (can specify multiple)
  --disable-event-timestamp  Disable event timestamp validation
```

**Examples:**
```bash
feast materialize 2021-01-01T00:00:00 2021-12-31T23:59:59
feast materialize -v driver_hourly_stats -v driver_daily_stats 2021-01-01 2021-12-31
feast materialize --disable-event-timestamp 2021-01-01 2021-12-31
```

#### `feast materialize-incremental`

Materializes incrementally from last run.

```bash
feast materialize-incremental [OPTIONS] END_DATE

Options:
  -v, --views TEXT           Feature views to materialize
```

**Examples:**
```bash
feast materialize-incremental $(date +%Y-%m-%d)
feast materialize-incremental -v driver_hourly_stats 2021-12-31
```

#### `feast serve`

Starts the feature server.

```bash
feast serve [OPTIONS]

Options:
  -h, --host TEXT    Host to bind (default: 127.0.0.1)
  -p, --port INTEGER Port to listen on (default: 6566)
  -t, --type TEXT    Server type: rest or grpc (default: rest)
  --no-access-log    Disable access logging
  --workers INTEGER  Number of worker processes
```

**Examples:**
```bash
feast serve
feast serve --port 8080
feast serve --host 0.0.0.0 --port 6566
feast serve --type grpc --port 6567
```

#### `feast ui`

Starts the Feast Web UI.

```bash
feast ui [OPTIONS]

Options:
  -h, --host TEXT           Host to bind (default: 0.0.0.0)
  -p, --port INTEGER        Port to listen on (default: 8888)
  --registry_ttl_sec INT    Registry cache TTL in seconds (default: 5)
```

**Examples:**
```bash
feast ui
feast ui --port 8080 --registry_ttl_sec 60
```

#### `feast entities`

Lists all registered entities.

```bash
feast entities list [OPTIONS]

Options:
  --tags TEXT    Filter by tags (e.g., --tags 'key:value')
```

#### `feast feature-views`

Lists all registered feature views.

```bash
feast feature-views list [OPTIONS]

Options:
  --tags TEXT    Filter by tags
```

#### `feast registry-dump`

Prints contents of metadata registry.

```bash
feast registry-dump
```

#### `feast configuration`

Displays current configuration.

```bash
feast configuration
```

#### `feast teardown`

Tears down deployed infrastructure.

```bash
feast teardown
```

#### `feast version`

Displays Feast SDK version.

```bash
feast version
```

#### `feast permissions`

Manages access controls.

```bash
feast permissions list [OPTIONS]
feast permissions describe PERMISSION_NAME
feast permissions check
feast permissions list-roles [OPTIONS]

Options:
  --tags TEXT      Filter by tags
  -v, --verbose    Show detailed information
```

---

## Point-in-Time Joins

### Overview

Point-in-time joins enable Feast to reproduce the state of features at a specific point in the past, preventing data leakage in ML pipelines.

### TTL (Time-to-Live)

The TTL parameter defines the temporal window for feature retrieval:

```python
driver_stats = FeatureView(
    name="driver_stats",
    entities=[driver],
    ttl=timedelta(hours=2),  # Look back up to 2 hours
    ...
)
```

**Important**: TTL is relative to each timestamp in the entity dataframe, NOT the current time.

### Timestamp Fields

| Field | Description |
|-------|-------------|
| `event_timestamp` | When the feature value was generated/valid |
| `created_timestamp` | When the row was written to the data source |

**Example:**
```python
source = FileSource(
    path="data/driver_stats.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_at",
)
```

### Example with Point-in-Time Correctness

```python
# Entity dataframe with timestamps
entity_df = pd.DataFrame({
    "driver_id": [1001, 1001, 1001],
    "event_timestamp": [
        datetime(2021, 4, 12, 10, 0, 0),   # Get features as of 10:00
        datetime(2021, 4, 12, 11, 0, 0),   # Get features as of 11:00
        datetime(2021, 4, 12, 12, 0, 0),   # Get features as of 12:00
    ]
})

# Each row gets the latest feature values available at its timestamp
# within the TTL window
training_df = fs.get_historical_features(
    entity_df=entity_df,
    features=["driver_stats:trips_today"]
).to_df()
```

---

## Complete Example

### Project Structure

```
my_feature_repo/
  feature_store.yaml
  features.py
  data/
    driver_stats.parquet
    registry.db
    online_store.db
```

### features.py

```python
from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, FeatureService
from feast.types import Int64, Float32, String

# Entity definition
driver = Entity(
    name="driver",
    join_keys=["driver_id"],
    description="Driver entity",
)

# Data source
driver_stats_source = FileSource(
    path="data/driver_stats.parquet",
    timestamp_field="event_timestamp",
)

# Feature view
driver_hourly_stats = FeatureView(
    name="driver_hourly_stats",
    entities=[driver],
    ttl=timedelta(hours=1),
    schema=[
        Field(name="trips_today", dtype=Int64),
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
    ],
    source=driver_stats_source,
    online=True,
)

# Feature service
driver_activity_service = FeatureService(
    name="driver_activity",
    features=[driver_hourly_stats],
)
```

### feature_store.yaml

```yaml
project: driver_features
registry: data/registry.db
provider: local
online_store:
  type: sqlite
  path: data/online_store.db
```

### Usage

```python
from feast import FeatureStore
from datetime import datetime
import pandas as pd

# Initialize
fs = FeatureStore(repo_path=".")

# Apply definitions
fs.apply([driver, driver_hourly_stats, driver_activity_service])

# Materialize to online store
fs.materialize_incremental(end_date=datetime.now())

# Get training data
entity_df = pd.DataFrame({
    "driver_id": [1001, 1002],
    "event_timestamp": [datetime.now(), datetime.now()]
})
training_df = fs.get_historical_features(
    entity_df=entity_df,
    features=fs.get_feature_service("driver_activity")
).to_df()

# Get online features
online_features = fs.get_online_features(
    features=["driver_hourly_stats:conv_rate", "driver_hourly_stats:trips_today"],
    entity_rows=[{"driver_id": 1001}]
).to_dict()
```

---

## Resources

- **Official Documentation**: https://docs.feast.dev/
- **Python API Reference**: https://rtd.feast.dev/ or https://api.docs.feast.dev/python/
- **GitHub Repository**: https://github.com/feast-dev/feast
- **CLI Reference**: https://docs.feast.dev/reference/feast-cli-commands
- **Feature Store YAML**: https://docs.feast.dev/reference/feature-repository/feature-store-yaml


> Source: `docs/data_engineering/feast/feast-llm-research.md`

# Feast Feature Store for LLM and AI Applications

## Executive Summary

Feast (Feature Store) is an open-source feature store that has evolved to support modern AI/LLM applications beyond traditional ML. It provides a unified data access layer for managing structured data at scale during both training and inference, with emerging support for vector embeddings and RAG applications.

---

## 1. LLM Feature Use Cases

### 1.1 Embedding Storage and Retrieval

Feast now supports vector similarity search (alpha feature) for storing and retrieving embeddings:

```python
from feast import Field, FeatureView, FileSource
from feast.types import Array, Float32, String

# Define entity
chunk = Entity(name="chunk_id", join_keys=["chunk_id"])

# Define embedding feature view
embedding_feature_view = FeatureView(
    name="document_embeddings",
    entities=[chunk],
    schema=[
        Field(name="chunk_id", dtype=String),
        Field(name="text", dtype=String),
        Field(
            name="vector",
            dtype=Array(Float32),
            vector_index=True,
            vector_search_metric="COSINE"
        ),
    ],
    source=FileSource(path="data/embeddings.parquet"),
)
```

**Key Benefits:**
- Treat embeddings as proper ML features with lifecycle management
- Version control and governance for document repositories
- Consistent API across multiple vector database backends

### 1.2 User Preference Features for Personalization

Feature stores enable LLM personalization by providing user context at request time:

```python
# Define user preference feature view
user_preferences = FeatureView(
    name="user_preferences",
    entities=[user],
    schema=[
        Field(name="preferred_topics", dtype=Array(String)),
        Field(name="communication_style", dtype=String),
        Field(name="language", dtype=String),
        Field(name="interaction_history_embedding", dtype=Array(Float32)),
    ],
    source=user_data_source,
    ttl=timedelta(days=1),
)

# Retrieve at inference time
features = store.get_online_features(
    features=[
        "user_preferences:preferred_topics",
        "user_preferences:communication_style",
        "user_preferences:language",
    ],
    entity_rows=[{"user_id": "user123"}],
).to_dict()
```

**Personalization Patterns:**
- Pre-pend user context to LLM prompts
- Retrieve user history embeddings for semantic matching
- Combine structured preferences with vector similarity

### 1.3 Context Features for RAG Systems

Feast serves as the service layer for RAG applications:

```python
# Retrieve relevant documents for RAG context
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
query_embedding = model.encode(user_query)

# Vector similarity search
context_data = store.retrieve_online_documents_v2(
    features=[
        "document_embeddings:vector",
        "document_embeddings:text",
        "document_embeddings:chunk_id",
    ],
    query=query_embedding,
    top_k=5,
    distance_metric="COSINE"
).to_df()

# Use retrieved context for LLM
context = "\n".join(context_data["text"].tolist())
prompt = f"""Context: {context}

Question: {user_query}

Answer based on the context provided:"""
```

### 1.4 Real-time Feature Serving for Agents

LLM agents can use Feast to retrieve contextual features during multi-step reasoning:

```python
# Agent retrieves session context
session_features = store.get_online_features(
    features=[
        "session_context:recent_actions",
        "session_context:current_task",
        "session_context:tool_usage_history",
    ],
    entity_rows=[{"session_id": agent_session_id}],
).to_dict()

# Agent retrieves entity-specific knowledge
entity_features = store.get_online_features(
    features=[
        "product_catalog:description",
        "product_catalog:specifications",
        "product_catalog:embedding",
    ],
    entity_rows=[{"product_id": product_id}],
).to_dict()
```

---

## 2. Vector Database Integration

### 2.1 Supported Vector Stores

Feast integrates with multiple vector databases:

| Database | Vector Retrieval | Indexing | V2 API | Notes |
|----------|-----------------|----------|--------|-------|
| **Milvus** | Yes | Yes | Yes | Full support, recommended |
| **SQLite** | Yes | No | Yes | Local development |
| **Elasticsearch** | Yes | Yes | No | Enterprise search |
| **Pgvector** | Yes | No | No | PostgreSQL extension |
| **Qdrant** | Yes | Yes | No | Cloud-native |
| **Faiss** | Limited | No | No | In development |

### 2.2 Configuration

**feature_store.yaml:**

```yaml
project: rag_application
provider: local
registry: data/registry.db
offline_store:
  type: file
online_store:
  type: milvus
  path: data/online_store.db
  vector_enabled: true
  embedding_dim: 384
  index_type: "IVF_FLAT"
  metric_type: "COSINE"
```

**Installation:**

```bash
# Milvus (recommended)
pip install feast[milvus]

# PostgreSQL with pgvector
pip install feast[postgres]

# Elasticsearch
pip install feast[elasticsearch]

# Qdrant
pip install feast[qdrant]

# SQLite (local development)
pip install feast[sqlite_vec]
```

### 2.3 Vector Feature Views

```python
from feast import FeatureView, Field, Entity
from feast.types import Array, Float32, String

# Entity definition
document = Entity(name="document_id", join_keys=["document_id"])
chunk = Entity(name="chunk_id", join_keys=["chunk_id"])

# Vector-enabled feature view
city_embeddings = FeatureView(
    name="city_embeddings",
    entities=[chunk],
    schema=[
        Field(name="item_id", dtype=String),
        Field(name="text", dtype=String),
        Field(
            name="vector",
            dtype=Array(Float32),
            vector_index=True,
            vector_search_metric="COSINE"  # Options: COSINE, L2, IP
        ),
    ],
    source=FileSource(
        path="data/city_wikipedia_summaries.parquet",
        timestamp_field="event_timestamp",
    ),
)
```

### 2.4 Similarity Search Patterns

**Basic Retrieval:**

```python
# Initialize store
store = FeatureStore(repo_path=".")

# Query embedding
query = "What is the population of Paris?"
query_embedding = embedding_model.encode(query)

# Retrieve similar documents
results = store.retrieve_online_documents_v2(
    features=[
        "city_embeddings:vector",
        "city_embeddings:text",
        "city_embeddings:item_id",
    ],
    query=query_embedding,
    top_k=3,
    distance_metric="COSINE"
).to_df()

print(results[["item_id", "text", "_distance"]])
```

**Combined Vector + Structured Features:**

```python
# Retrieve both embeddings and metadata
context = store.retrieve_online_documents_v2(
    features=[
        "document_embeddings:vector",
        "document_embeddings:text",
        "document_embeddings:source_url",
        "document_embeddings:created_at",
        "document_embeddings:author",
    ],
    query=query_embedding,
    top_k=5,
    distance_metric="COSINE"
).to_df()
```

---

## 3. Real-time AI Applications

### 3.1 Low-Latency Feature Serving

Feast uses a push model for online serving, achieving sub-100ms latency:

```python
# Low-latency online retrieval
features = store.get_online_features(
    features=[
        "user_features:click_rate",
        "user_features:session_duration",
        "item_features:popularity_score",
    ],
    entity_rows=[
        {"user_id": "u1", "item_id": "i1"},
        {"user_id": "u2", "item_id": "i2"},
    ],
).to_dict()
```

**Performance Optimizations:**
- Pre-computed features stored in Redis/Milvus
- Push-based materialization (not pull)
- Batch lookups for multiple entities

### 3.2 Streaming Features

Feast supports real-time feature updates via push sources:

```python
from feast import PushSource, FeatureView

# Define push source for streaming data
push_source = PushSource(
    name="user_activity_push",
    batch_source=BigQuerySource(
        table="project.dataset.user_activity",
    ),
)

# Stream feature view
stream_features = FeatureView(
    name="user_activity_stream",
    entities=[user],
    schema=[
        Field(name="last_action", dtype=String),
        Field(name="action_count_1h", dtype=Int64),
        Field(name="session_embedding", dtype=Array(Float32)),
    ],
    source=push_source,
    ttl=timedelta(hours=1),
)

# Push real-time events
store.push(
    push_source_name="user_activity_push",
    df=events_df,
    to=PushMode.ONLINE,
)
```

### 3.3 Streaming with Denormalized

For complex streaming aggregations:

```python
# Denormalized integration for real-time aggregations
from denormalized import Context, FeastSink

# Configure Feast sink
feast_sink = FeastSink(
    repo_path="/path/to/feast/repo",
    push_source_name="realtime_features",
)

# Stream processing pipeline
ctx = Context()
ds = ctx.from_topic("user_events", json_schema)
ds.window(
    window_type=TumblingWindow,
    window_size=timedelta(minutes=5),
).aggregate(
    group_by=["user_id"],
    aggregates=[
        Avg(field="response_time"),
        Count(field="event_id"),
    ],
).sink_to_feast(feast_sink)
```

### 3.4 On-Demand Feature Transformations

Apply transformations at request time for LLM features:

```python
from feast import on_demand_feature_view, Field
from feast.types import Float64, String

@on_demand_feature_view(
    sources=[user_features_view, input_request],
    schema=[
        Field(name="personalization_score", dtype=Float64),
        Field(name="context_prompt", dtype=String),
    ],
    mode="python",
    singleton=True,
)
def compute_personalization(inputs: dict) -> dict:
    """Compute personalization features at request time."""

    # Combine user preferences with request context
    user_topics = inputs["preferred_topics"]
    query_topic = inputs["query_topic"]

    # Calculate relevance score
    score = calculate_topic_overlap(user_topics, query_topic)

    # Generate personalized prompt context
    prompt = f"User prefers {', '.join(user_topics)}. Respond in {inputs['style']} tone."

    return {
        "personalization_score": score,
        "context_prompt": prompt,
    }

# Retrieve with on-demand computation
features = store.get_online_features(
    features=[
        "compute_personalization:personalization_score",
        "compute_personalization:context_prompt",
    ],
    entity_rows=[{
        "user_id": "u123",
        "query_topic": "machine learning",
    }],
).to_dict()
```

---

## 4. MLOps for LLMs

### 4.1 Feature Pipelines for LLM Applications

**RAG Data Pipeline:**

```python
# Step 1: Data Ingestion
from feast import FeatureStore
import pandas as pd

store = FeatureStore(repo_path=".")

# Step 2: Text Processing & Embedding Generation
from docling.document_converter import DocumentConverter
from sentence_transformers import SentenceTransformer

converter = DocumentConverter()
model = SentenceTransformer("all-MiniLM-L6-v2")

def process_documents(file_paths):
    chunks = []
    for path in file_paths:
        doc = converter.convert(path).document
        for chunk in doc.chunks:
            embedding = model.encode(chunk.text)
            chunks.append({
                "chunk_id": chunk.id,
                "document_id": doc.id,
                "text": chunk.text,
                "vector": embedding.tolist(),
                "event_timestamp": datetime.now(),
            })
    return pd.DataFrame(chunks)

# Step 3: Ingest to Feature Store
df = process_documents(["doc1.pdf", "doc2.pdf"])
store.write_to_online_store(
    feature_view_name="document_embeddings",
    df=df,
)

# Step 4: Materialize to offline store for training
store.materialize(
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now(),
)
```

### 4.2 Training-Serving Consistency

Feast eliminates training-serving skew:

```python
# Training: Get historical features
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "user_preferences:embedding",
        "document_embeddings:vector",
        "interaction_features:click_rate",
    ],
).to_df()

# Train model
model.fit(training_df)

# Serving: Same feature definitions, different store
serving_features = store.get_online_features(
    features=[
        "user_preferences:embedding",
        "document_embeddings:vector",
        "interaction_features:click_rate",
    ],
    entity_rows=[{"user_id": "u1", "document_id": "d1"}],
).to_dict()

# Predict
prediction = model.predict(serving_features)
```

### 4.3 A/B Testing with Features

While Feast doesn't provide A/B testing directly, it ensures consistency during experiments:

```python
# Consistent features across model variants
features = store.get_online_features(
    features=[
        "user_features:embedding",
        "product_features:description",
    ],
    entity_rows=[{"user_id": user_id, "product_id": product_id}],
).to_dict()

# Route to different models based on experiment
if experiment_variant == "control":
    result = model_v1.predict(features)
elif experiment_variant == "treatment":
    result = model_v2.predict(features)

# Log for analysis
log_experiment_result(
    variant=experiment_variant,
    features=features,
    result=result,
)
```

**Integration with Experimentation Platforms:**
- LaunchDarkly
- Split.io
- Statsig
- Optimizely

### 4.4 Feature Monitoring for AI Systems

Feast integrates with observability platforms for drift detection:

**Arize AI Integration:**

```python
# Log features to Arize for monitoring
from arize.pandas.logger import Client

arize_client = Client(space_key="...", api_key="...")

# Get features from Feast
features = store.get_online_features(
    features=["user_features:embedding", "user_features:preferences"],
    entity_rows=[{"user_id": user_id}],
).to_df()

# Log to Arize
arize_client.log(
    model_id="rag_model_v1",
    model_version="1.0",
    prediction_id=prediction_id,
    features=features,
    prediction_label=prediction,
    actual_label=actual,  # When available
)
```

**Evidently AI for Data Drift:**

```python
from evidently.metrics import DataDriftTable
from evidently.report import Report

# Compare training vs production features
reference_data = store.get_historical_features(
    entity_df=training_entities,
    features=feature_list,
).to_df()

production_data = store.get_historical_features(
    entity_df=production_entities,
    features=feature_list,
).to_df()

# Generate drift report
report = Report(metrics=[DataDriftTable()])
report.run(
    reference_data=reference_data,
    current_data=production_data,
)
report.save_html("drift_report.html")
```

**WhyLabs Integration:**

```python
import whylogs as why

# Profile features from Feast
features_df = store.get_historical_features(
    entity_df=entity_df,
    features=feature_list,
).to_df()

# Create profile
profile = why.log(features_df)

# Upload to WhyLabs
profile.writer("whylabs").write()
```

---

## 5. Complete RAG Example

### 5.1 Project Structure

```
rag_project/
├── feature_store.yaml
├── definitions.py
├── data/
│   ├── documents.parquet
│   └── registry.db
└── notebooks/
    └── demo.ipynb
```

### 5.2 Configuration

**feature_store.yaml:**

```yaml
project: rag_demo
provider: local
registry: data/registry.db
offline_store:
  type: file
online_store:
  type: milvus
  path: data/online_store.db
  vector_enabled: true
  embedding_dim: 384
  index_type: "IVF_FLAT"
entity_key_serialization_version: 2
```

### 5.3 Feature Definitions

**definitions.py:**

```python
from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Array, Float32, String

# Entities
chunk = Entity(
    name="chunk_id",
    join_keys=["chunk_id"],
    description="Unique identifier for document chunks",
)

document = Entity(
    name="document_id",
    join_keys=["document_id"],
    description="Unique identifier for source documents",
)

# Data source
documents_source = FileSource(
    path="data/documents.parquet",
    timestamp_field="event_timestamp",
)

# Feature view with vector embeddings
document_embeddings = FeatureView(
    name="document_embeddings",
    entities=[chunk, document],
    schema=[
        Field(name="text", dtype=String),
        Field(name="source_url", dtype=String),
        Field(
            name="vector",
            dtype=Array(Float32),
            vector_index=True,
            vector_search_metric="COSINE"
        ),
    ],
    source=documents_source,
    ttl=timedelta(days=30),
)
```

### 5.4 RAG Application

```python
from feast import FeatureStore
from sentence_transformers import SentenceTransformer
import openai

# Initialize
store = FeatureStore(repo_path=".")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
openai.api_key = "your-api-key"

def rag_query(user_question: str, top_k: int = 5) -> str:
    """Execute RAG query using Feast."""

    # Step 1: Generate query embedding
    query_embedding = embedding_model.encode(user_question)

    # Step 2: Retrieve relevant documents
    context_df = store.retrieve_online_documents_v2(
        features=[
            "document_embeddings:vector",
            "document_embeddings:text",
            "document_embeddings:source_url",
        ],
        query=query_embedding,
        top_k=top_k,
        distance_metric="COSINE"
    ).to_df()

    # Step 3: Build context
    context_parts = []
    for _, row in context_df.iterrows():
        context_parts.append(f"Source: {row['source_url']}\n{row['text']}")
    context = "\n\n---\n\n".join(context_parts)

    # Step 4: Generate response with LLM
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "Answer questions based on the provided context. "
                           "Cite sources when possible."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {user_question}"
            }
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content

# Usage
answer = rag_query("What are the main features of Feast?")
print(answer)
```

---

## 6. Production Deployment

### 6.1 Kubernetes with Feast Operator

```yaml
# feast-feature-store.yaml
apiVersion: feast.dev/v1alpha1
kind: FeatureStore
metadata:
  name: rag-feature-store
spec:
  feastProject: rag_project
  services:
    onlineStore:
      persistence:
        store:
          type: milvus
          config:
            host: milvus.default.svc.cluster.local
            port: 19530
    offlineStore:
      persistence:
        store:
          type: file
```

### 6.2 Feature Server Helm Chart

```bash
helm install feast-server feast/feast \
  --set featureStore.project=rag_project \
  --set featureStore.registry.path=s3://bucket/registry.db \
  --set onlineStore.type=milvus \
  --set onlineStore.host=milvus:19530
```

### 6.3 API Endpoint

```python
import requests

# Query feature server
response = requests.post(
    "http://feast-server:6566/get-online-features",
    json={
        "features": [
            "document_embeddings:vector",
            "document_embeddings:text",
        ],
        "entities": {"chunk_id": ["c1", "c2", "c3"]},
    }
)

features = response.json()
```

---

## 7. Best Practices

### 7.1 Feature Design for LLMs

1. **Treat embeddings as features**: Version and manage document embeddings like any other ML feature
2. **Use consistent embedding models**: Same model for indexing and querying
3. **Include metadata**: Store source URLs, timestamps, and categories alongside vectors
4. **Set appropriate TTLs**: Configure time-to-live based on data freshness requirements

### 7.2 Performance Optimization

1. **Choose appropriate index types**:
   - `FLAT`: Small datasets (<100k vectors), exact search
   - `IVF_FLAT`: Medium datasets, approximate search
   - `HNSW`: Large datasets, fast approximate search

2. **Batch operations**: Use batch writes and reads when possible
3. **Pre-compute transformations**: Use `write_to_online_store=True` for ODFVs

### 7.3 Monitoring

1. **Track feature freshness**: Monitor when features were last updated
2. **Monitor embedding drift**: Compare embedding distributions over time
3. **Log retrieval quality**: Track relevance scores and user feedback

---

## 8. Resources

### Official Documentation
- Feast Documentation: https://docs.feast.dev/
- Vector Database Guide: https://docs.feast.dev/reference/alpha-vector-database
- RAG Tutorial: https://docs.feast.dev/tutorials/rag-with-docling

### Code Examples
- Milvus Quickstart: https://github.com/feast-dev/feast/blob/master/examples/rag/milvus-quickstart.ipynb
- RAG with Docling: https://github.com/feast-dev/feast/tree/master/examples/rag-docling

### Community
- GitHub: https://github.com/feast-dev/feast
- Slack: https://slack.feast.dev/

### Integration Guides
- Milvus + Feast: https://milvus.io/docs/build_RAG_with_milvus_and_feast.md
- Arize Integration: https://arize.com/blog/feast-and-arize-supercharge-feature-management-and-model-monitoring-for-mlops/

---

## Summary

Feast provides a robust foundation for LLM and AI applications by:

1. **Unifying feature management**: Single API for embeddings, structured data, and metadata
2. **Supporting vector search**: Native integration with Milvus, Elasticsearch, and other vector stores
3. **Enabling low-latency serving**: Sub-100ms feature retrieval for real-time applications
4. **Ensuring consistency**: Same feature definitions for training and serving
5. **Integrating with MLOps**: Works with monitoring, experimentation, and orchestration tools

The key insight is that document embeddings and user preferences are ML features that benefit from proper lifecycle management, versioning, and governance - exactly what feature stores provide.


## Original Sources

### baml/
- `docs/data_engineering/baml/baml.md`
- `docs/data_engineering/baml/baml-comprehensive-guide.md`
- `docs/data_engineering/baml/baml-dlt-integration.md`
- `docs/data_engineering/baml/document-processing-pipeline.md`
- `docs/data_engineering/baml/Structured Outputs Create False Confidence.md`
- `docs/data_engineering/baml/extract-anything/README.md`

### cognee/
- `docs/data_engineering/cognee/cognee.md`
- `docs/data_engineering/cognee/cognee-openapi-research.md`

### graphiti/
- `docs/data_engineering/graphiti/graphiti-temporal-graphs.md`
- `docs/data_engineering/graphiti/graphiti-crypto-adaptation.md`

### feast/
- `docs/data_engineering/feast/feast-patterns-best-practices.md`
- `docs/data_engineering/feast/feast-sdk-api-research.md`
- `docs/data_engineering/feast/feast-llm-research.md`

---
*Generated by MERGE_PLAN.md Phase 1 — 2026-06-06*
