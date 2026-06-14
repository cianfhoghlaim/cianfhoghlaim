---
title: "BAML Schema Design & LLM Extraction — Comprehensive Reference"
domain: agents
status: stable
description: "Consolidated guide to BAML (Boundary AI Markup Language): schema design patterns, testing, retry, streaming, error handling, Irish education curriculum schemas, dynamic TypeBuilder, DuckDB/Dragonfly integration, self-healing extraction pipelines, agentic web scraping, and the Adaptive Classroom architecture."
supersedes:
  - docs/agents/BAML_COMPREHENSIVE_GUIDE.md
  - docs/agents/BAML Schemas for Irish Education.md
  - docs/agents/BAML for Syllabus-Driven Data Extraction.md
  - docs/agents/BAML_DUCKDB_DRAGONFLY_ANALYSIS.md
  - docs/agents/baml-patterns-and-best-practices.md
entities:
  - BAMLSchema
  - PrimaryCurriculumArea
  - JuniorCycleScienceSpec
  - QuestionPartSchema
  - CircularMetadata
  - TypeBuilder
  - DuckDBManager
  - DragonflyCache
related_skills:
  - .agents/skills/dignified-python/SKILL.md
  - .agents/skills/irish-edtech/SKILL.md
ccc_query_hints:
  - BAML schema design patterns
  - BAML Irish education extraction schemas
  - BAML TypeBuilder dynamic schema generation
  - baml-cli workflow generate test
  - BAML retry policy fallback client pattern
  - BAML DuckDB Dragonfly data layer
  - BAML self-healing extraction
last_reviewed: 2026-06-13
truth: sole
---

# BAML Schema Design & LLM Extraction — Comprehensive Reference

> **Merged from 2 canonical sources**:
> - `baml-extraction.md` (746 lines, 10 parts) — practical patterns-first reference
> - `BAML_COMPREHENSIVE_GUIDE.md` (1108 lines, 5 parts) — architectural deep-dive
>
> Plus 4 stub files (`baml-patterns-and-best-practices.md`, `BAML Schemas for Irish Education.md`, `BAML for Syllabus-Driven Data Extraction.md`, `BAML_DUCKDB_DRAGONFLY_ANALYSIS.md`) that had only "MERGED INTO" notices — all stubs deleted, no content lost.

---

## Part I: BAML Fundamentals

### Overview

BAML (Boundary AI Markup Language) is a domain-specific language developed by BoundaryML for building type-safe LLM applications. It transforms prompt engineering into schema engineering, enabling developers to define structured outputs, test prompts before deployment, and generate type-safe clients across multiple programming languages.

**Key Value Propositions:**
- Type-safe structured outputs that work on Day 1 of any model release
- Universal LLM support (OpenAI, Anthropic, Gemini, Bedrock, Azure, Ollama, etc.)
- Multi-language code generation (Python, TypeScript, Ruby, Go, Rust, Java, C#)
- Integrated testing and validation directly in the IDE
- Error-tolerant Rust-based parser (Schema-Aligned Parsing) that handles malformed JSON

### baml-cli Workflow

```bash
# Generate client code from .baml files
baml-cli generate
```

Generated structure:
```
baml_client/
├── __init__.py
├── async_client.py      # Async versions of all functions
├── sync_client.py       # Sync versions
├── types.py             # Generated classes and enums
├── partial_types.py     # Partial types for streaming
└── ...
```

### IDE Support

VSCode: Install `Boundary.baml-extension` for syntax highlighting, real-time playground, prompt preview, and auto-generation on save. Also available for JetBrains, Zed.

---

## Part II: Core Design Patterns

### Pattern 1: Structured Data Extraction

BAML excels at extracting structured data from unstructured text. The pattern involves defining a schema and a function that returns that schema.

```baml
class Resume {
  name string
  email string
  phone string?
  skills string[]
  experience Experience[]
}

class Experience {
  company string
  role string
  startDate string
  endDate string?
  description string
}

function ExtractResume(resumeText: string) -> Resume {
  client "openai/gpt-4o"
  prompt #"
    Extract structured information from the following resume.

    {{ ctx.output_format }}

    {{ _.role("user") }}
    {{ resumeText }}
  "#
}
```

**Best Practices:**
- Use `@description` annotations to guide the LLM on field semantics
- Mark optional fields with `?` to handle missing data gracefully
- Use arrays for repeating elements

### Pattern 2: Single-Label Classification

```baml
enum MessageType { SPAM, NOT_SPAM }

function ClassifyMessage(input: string) -> MessageType {
  client "openai/gpt-4o-mini"
  prompt #"Classify the following message as spam or not spam. {{ ctx.output_format }} {{ _.role("user") }} {{ input }}"#
}
```

### Pattern 3: Multi-Label Classification

```baml
enum TicketCategory { ACCOUNT, BILLING, TECHNICAL, GENERAL_QUERY, URGENT }

class TicketClassification {
  categories TicketCategory[]
  priority int @description("Priority from 1 (low) to 5 (high)")
  summary string
}

function ClassifyTicket(ticket: string) -> TicketClassification {
  client "openai/gpt-4o"
  prompt #"Analyze this support ticket and classify it. {{ ctx.output_format }} {{ _.role("user") }} {{ ticket }}"#
}
```

### Pattern 4: Literal Types (Union Types)

```baml
class DealAnalysis {
  dealType "merger" | "acquisition" @description("Type of business deal")
  amount float
  currency string @description("Currency code (USD, EUR, etc.)")
  companies string[]
}
```

### Pattern 5: Multi-Step Workflows and Agents

BAML treats prompts as composable functions, enabling multi-step workflows.

```baml
// Step 1: Extract entities
function ExtractEntities(text: string) -> Entity[] {
  client "openai/gpt-4o"
  prompt #"Extract all named entities from the text. {{ ctx.output_format }} {{ _.role("user") }} {{ text }}"#
}

// Step 2: Classify sentiment for each entity
function AnalyzeSentiment(entity: string, context: string) -> SentimentResult {
  client "openai/gpt-4o-mini"
  prompt #"Analyze sentiment. {{ ctx.output_format }} Entity: {{ entity }} Context: {{ context }}"#
}
```

**Agent Pattern (Python):**
```python
from baml_client import b

def run_agent(initial_query: str):
    messages = [{"role": "user", "content": initial_query}]
    while True:
        response = b.AgentStep(messages=messages)
        if response.action == "complete":
            return response.result
        tool_result = execute_tool(response.tool_call)
        messages.append({"role": "tool", "content": tool_result})
```

### Generative UI (Next.js)

```baml
function GenerateRecipe(recipe: string) -> Recipe {
  client "openai/gpt-4o"
  prompt #"Generate a recipe for: {{ recipe }}"#
}

class Recipe {
  name string @stream.not_null
  servings int @stream.not_null
  ingredients (Ingredient @stream.done)[]
  instructions string[]
}
```

### Dynamic Schemas (Runtime BAML generation)

```baml
class Response {
  @@dynamic  // Allows runtime-generated schema
}

function ExecuteBAML(content: string | image | audio | image[]) -> Response {
  client "openai/gpt-4o"
  prompt #"Extract data from content using generated schema"#
}
```

Two-phase pipeline: Schema Generation → Data Extraction using SSE streaming.

---

## Part III: Testing

### Basic Test Structure

BAML makes testing a first-class citizen. Tests can be written in `.baml` files and run before any application code is written.

```baml
test SpamTest {
  functions [ClassifyMessage]
  args {
    input "Buy cheap watches now! Limited time offer!!!"
  }
  @@assert({{ this == "SPAM" }})
}

test NotSpamTest {
  functions [ClassifyMessage]
  args {
    input "Hey, are we still meeting for coffee tomorrow?"
  }
  @@assert({{ this == "NOT_SPAM" }})
}
```

### Checks vs Asserts

| Directive | Behavior |
|---|---|
| `@@assert` | Hard guarantee — test fails immediately if condition is false |
| `@@check` | Soft validation — test continues, result recorded for inspection |

```baml
test ValidationExample {
  functions [ExtractData]
  args { text "sample text" }
  @@assert({{ this.required_field|length > 0 }})
  @@check(reasonable_length, {{ this.text|length < 1000 }})
  @@check(has_date, {{ this.date != null }})
}
```

### Test Context Variables

| Variable | Description |
|---|---|
| `this` | Computed result (shorthand for `_.result`) |
| `_.result` | Explicit result reference |
| `_.latency_ms` | Execution time in milliseconds |
| `_.checks.$NAME` | Prior check results |

### Media Input Testing

BAML supports testing with images, audio, PDFs, and videos:

```baml
test ImageExtractionTest {
  functions [ExtractFromImage]
  args {
    image {
      file "receipts/sample-receipt.png"  // Relative to baml_src/
    }
  }
}

test URLImageTest {
  functions [ExtractFromImage]
  args {
    image {
      url "https://example.com/image.png"
    }
  }
}
```

---

## Part IV: Retry Strategies & Resilience

### Exponential Backoff

```baml
retry_policy Exponential {
  max_retries 3
  strategy {
    type exponential_backoff
    delay_ms 300
    multiplier 1.5
    max_delay_ms 10000
  }
}
```

### Fallback Clients

```baml
client<llm> GPT4o {
  provider openai
  retry_policy Exponential
  options { model "gpt-4o" temperature 0 api_key env.OPENAI_API_KEY }
}

client<llm> ClaudeBackup {
  provider anthropic
  options { model "claude-3-5-sonnet-20241022" api_key env.ANTHROPIC_API_KEY }
}

client<llm> ResilientClient {
  provider fallback
  options { strategy [GPT4o, ClaudeBackup] }
}
```

### Round-Robin Load Balancing

```baml
client<llm> LoadBalanced {
  provider round-robin
  options {
    strategy [
      "openai/gpt-4o",
      "anthropic/claude-3-5-sonnet-20241022",
      "google-ai/gemini-1.5-pro"
    ]
  }
}
```

**Important:** BAML retries are for API availability issues only. Application errors (malformed requests, validation failures) are NOT retried.

### Complete Production Client Example

```baml
retry_policy Exponential {
  max_retries 3
  strategy { type exponential_backoff delay_ms 200 multiplier 2.0 max_delay_ms 5000 }
}

client<llm> GPT4o {
  provider openai
  retry_policy Exponential
  options { model "gpt-4o" temperature 0 api_key env.OPENAI_API_KEY }
}

client<llm> ClaudeBackup {
  provider anthropic
  options { model "claude-3-5-sonnet-20241022" api_key env.ANTHROPIC_API_KEY }
}

client<llm> ResilientClient {
  provider fallback
  options { strategy [GPT4o, ClaudeBackup] }
}
```

---

## Part V: Streaming

### Type-Safe Streaming

BAML provides type-safe streaming with semantically valid partial objects as tokens arrive.

```baml
class Message {
  message_type string @stream.not_null  // Never null during streaming
  message string                         // Wrapped in StreamState
  metadata Metadata @stream.done         // Only included when complete
}
```

| Annotation | Behavior |
|---|---|
| `@stream.done` | Field only appears when fully parsed |
| `@stream.not_null` | Field will not be null during streaming |
| `@stream.with_state` | Provides streaming state information |

### Python Streaming

```python
from baml_client import b, partial_types

# Sync streaming
def stream_extraction(receipt: str):
    stream = b.stream.ExtractReceiptInfo(receipt)
    for partial in stream:
        print(f"Parsed {len(partial.items or [])} items so far")
        if partial.total:
            print(f"Current total: {partial.total}")
    final = stream.get_final_response()
    return final

# Async streaming
async def async_stream(receipt: str):
    from baml_client.async_client import b
    stream = b.stream.ExtractReceiptInfo(receipt)
    async for partial in stream:
        print(f"Items: {len(partial.items or [])}")
    final = await stream.get_final_response()
    return final
```

---

## Part VI: Error Handling

### Schema-Aligned Parsing (SAP)

BAML uses a Rust-based error-tolerant parser that can:
- Parse malformed JSON (missing closing brackets, trailing commas)
- Extract valid data even from partially correct outputs
- Coerce types automatically
- Trim junk and whitespace

### Field and Class-Level Validation

```baml
class Citation {
  quote string @check(not_empty, {{ this|length > 0 }})
  source string @assert(valid_source, {{ this|length > 0 and this != "unknown" }})
  page int? @check(reasonable, {{ this == null or (this > 0 and this < 10000) }})
}

class DateRange {
  startDate string
  endDate string
  @@assert(end_after_start, {{ this.endDate >= this.startDate }})
}
```

### Runtime Check Inspection

```python
result = b.ExtractCitation(text=input_text)
if not result._checks.not_empty.passed:
    print("Warning: quote was empty")
for check_name, check_result in result._checks.items():
    print(f"{check_name}: {'PASS' if check_result.passed else 'FAIL'}")
```

**Assertion Behavior:**
- Top-level assertion failure → Raises `BamlValidationError`
- Nested assertion failure → Item is removed from container
- Multiple assertions → Evaluated left to right, first failure stops

### Complete Production Example

```baml
// types.baml
class Invoice {
  vendor string @description("Company name of the vendor")
  invoiceNumber string @check(format, {{ this matches "INV-\\d+" }})
  date string @description("Date in YYYY-MM-DD format")
  lineItems LineItem[]
  subtotal float @check(positive, {{ this > 0 }})
  tax float
  total float @assert(matches_sum, {{ (this.subtotal + this.tax - this) | abs < 0.01 }})
}

class LineItem {
  description string @check(not_empty, {{ this|length > 0 }})
  quantity int @assert(positive, {{ this > 0 }})
  unitPrice float
  amount float @check(calculated, {{ (this.quantity * this.unitPrice - this) | abs < 0.01 }})
}

function ExtractInvoice(invoiceText: string) -> Invoice {
  client ResilientClient
  prompt #"Extract structured invoice information. {{ ctx.output_format }} {{ _.role("user") }} {{ invoiceText }}"#
}
```

---

## Part VII: Irish Education BAML Schemas

### The Tripartite Data Landscape

| Domain | Source | Content Type |
|---|---|---|
| **NCCA** (Pedagogical Intent) | curriculumonline.ie, ncca.ie | Curriculum specs, learning outcomes, assessment guidelines |
| **SEC** (Evidentiary Truth) | examinations.ie | Exam papers, marking schemes, chief examiner reports |
| **Dept of Education** (Temporal Governance) | gov.ie | Circular letters with temporal validity |

### Core Entity Metamodel

| Entity | Description | Key Attribute |
|---|---|---|
| CurriculumSpecification | Defining document for a subject | level, subject |
| PedagogicalUnit | Structural division of learning | type: Strand, Element |
| LearningOutcome | Atomic unit of instruction | action_verb, id |
| AssessmentInstrument | Specific test or task | type: Exam Question, CBA |
| EvidenceLogic | Rule for awarding marks | penalty_type, marks |
| PolicyDirective | Administrative rule | circular_id, status |

### Primary Curriculum Framework Schema

```baml
enum PrimaryStage {
  Stage1_JuniorSeniorInfants
  Stage2_FirstSecondClass
  Stage3_ThirdFourthClass
  Stage4_FifthSixthClass
}

class CompetencyLink {
  competency_name: string @description("e.g., 'Being a Digital Learner'")
  context: string @description("How this specific outcome supports the competency")
}

class PrimaryLearningOutcome {
  id: string? @description("Code if available")
  text: string @description("The statement of learning")
  element: string @description("The 'Element' of learning")
  progression_continuum: string?
  key_competencies: CompetencyLink
}

class PrimaryStrand {
  name: string @description("e.g., 'Number', 'Data and Chance'")
  description: string
  outcomes: PrimaryLearningOutcome
}

class PrimaryCurriculumArea {
  name: string @description("e.g., 'Mathematics', 'Language'")
  rationale: string
  strands: PrimaryStrand
  integration_links: string @description("Explicit text mentioning other areas")
}

function ExtractPrimaryFramework(text: string) -> PrimaryCurriculumArea {
  client "openai/gpt-4-turbo"
  prompt #"
    Analyze the text from the Primary Curriculum Framework.
    CRITICAL: The Primary Framework uses a matrix of 'Strands' and 'Elements'.
    Look for specific icons or text labels that indicate 'Key Competencies'.
    Text: {{ text }}
  "#
}
```

### Junior Cycle: Non-Linear Pedagogy

The Junior Cycle Science specification features a "Unifying Strand" (Nature of Science) embedded within contextual strands (Physical World, Biological World, Chemical World, Earth & Space).

```baml
class ScienceOutcome {
  id: string @description("e.g., 'CW4', 'PW2', 'NoS1'")
  strand_type: string @description("Contextual or Unifying")
  strand_name: string @description("e.g., 'Chemical World'")
  text: string
  action_verb: string @description("e.g., 'Investigate', 'Design', 'Evaluate'")
  keywords: string
}

class TransverseLink {
  source_outcome_id: string
  target_nos_id: string @description("Nature of Science outcome ID")
  strength: string @description("High/Medium/Low based on verb analysis")
}

class JuniorCycleScienceSpec {
  unifying_strand: ScienceOutcome
  contextual_strands: ScienceOutcome
  inferred_links: TransverseLink
}

function ExtractScienceSpec(text: string) -> JuniorCycleScienceSpec {
  client "openai/gpt-4-turbo"
  prompt #"
    Extract the Junior Cycle Science Specification.
    Step 1: Identify the 'Nature of Science' outcomes (Unifying Strand).
    Step 2: Identify Contextual outcomes (Physical, Biological, Chemical, Earth/Space).
    Step 3: For each Contextual outcome, analyze the Action Verb.
    If the verb implies data analysis, link to relevant NoS outcome.
    Text: {{ text }}
  "#
}
```

### Senior Cycle: Logic-Gate Marking Schemes

Chemistry, Physics, Biology, and Maths marking schemes are algorithmic with precise penalty rules.

```baml
class PenaltyRule {
  type: string @description("e.g., 'Arithmetic Slip', 'Chemical Error', 'Unit Omission'")
  deduction: float @description("The value to deduct")
  scope: string @description("e.g., 'per occurrence', 'max -3 for this part'")
}

class MarkingPoint {
  correct_answer: string @description("The target value or phrase")
  marks_awarded: int
  valid_alternatives: string @description("Other acceptable answers")
  mandatory_keywords: string @description("Words that MUST be present")
  examiner_notes: string? @description("Guidance like 'accept rounded values'")
}

class QuestionPartSchema {
  part_id: string @description("e.g., '(b)(ii)'")
  total_marks: int
  marking_points: MarkingPoint
  penalties: PenaltyRule
}

function ExtractMarkingScheme(text: string) -> QuestionPartSchema {
  client "openai/gpt-4-turbo"
  prompt #"
    Analyze the Marking Scheme segment. Extract the logic for awarding marks.
    CRITICAL: Identify 'Penalties' and 'Deductions'.
    Distinguish between a 'Slip' (minor error) and a fundamental error.
    Text: {{ text }}
  "#
}
```

### Qualitative Assessment (Arts & Humanities)

```baml
enum AchievementLevel {
  Exceptional
  AboveExpectations
  InLineWithExpectations
  YetToMeetExpectations
}

class RubricDescriptor {
  level: AchievementLevel
  text: string @description("The full descriptive paragraph")
  key_qualities: string @description("Extracted phrases")
  negative_indicators: string @description("Phrases indicating what is missing")
}

class AssessmentTask {
  name: string @description("e.g., 'CBA 1: The Past in My Place'")
  timing: string
  rubrics: RubricDescriptor
}
```

**Semantic Search Application:** Embed student essay → Cosine similarity against RubricDescriptor vectors → "Closest match: In Line with Expectations (Similarity 0.89). To move towards 'Exceptional', add more 'critical evaluation of sources'."

### Policy Layer: Circular Letters

```baml
enum CircularStatus { NewPolicy, Amendment, Repeal, Clarification }

class LinkedCircular {
  id: string
  relationship: string @description("Supersedes, Refers to, Amends")
}

class CircularMetadata {
  circular_id: string @description("e.g., '0003/2018'")
  title: string
  issue_date: string
  effective_date: string
  status: CircularStatus
  linked_circulars: LinkedCircular
  domains_affected: string @description("e.g., 'Leadership', 'Special Needs'")
}

function ExtractCircularMeta(text: string) -> CircularMetadata {
  client "openai/gpt-4-turbo"
  prompt #"
    Analyze the Circular Letter. Extract the ID and Dates.
    CRITICAL: Find the 'Supersedes' or 'Rescinds' text.
    Identify the Domain. Is this about Staffing? Assessment?
    Text: {{ text }}
  "#
}
```

---

## Part VIII: Dynamic TypeBuilder — The Adaptive Classroom

### The Technological Trinity

| Layer | Technology | Role | Key Capability |
|---|---|---|---|
| Cognitive | Agno | Agentic Logic & Memory | Agentic RAG/Chunking |
| Orchestration | Restate.dev | Durable Execution | Awakeables & Virtual Objects |
| Structural | BAML | Schema Enforcement | TypeBuilder for dynamic schemas |

### Two-Pass Generation Algorithm

**Phase 1: Meta-Extraction** — Analyze syllabus structure:
```baml
class GradingCriterion {
  name: string
  description: string
  max_score: int
  code: string  // e.g., "AO1", "AO2"
}

class ExamStructure {
  subject_name: string
  paper_code: string
  sections: string
  criteria: GradingCriterion
}

function ExtractExamStructure(syllabus_text: string) -> ExamStructure {
  client GPT4o
  prompt #"
    Analyze this syllabus. Define the structure of the exam paper.
    Identify the specific Assessment Objectives (AO) or grading criteria used.
    {{ syllabus_text }}
  "#
}
```

**Phase 2: Runtime Type Construction** — Build dynamic Pydantic models:
```python
from baml_client.type_builder import TypeBuilder
from baml_client import b

async def create_dynamic_parser(structure: ExamStructure):
    tb = TypeBuilder()

    # Define AssessmentObjectives class dynamically
    ao_class = tb.add_class("AssessmentObjectives")
    for criterion in structure.criteria:
        ao_class.add_property(criterion.code, tb.float().optional())

    # Define ExamQuestion class utilizing the dynamic AO class
    question_class = tb.add_class("ExamQuestion")
    question_class.add_property("question_number", tb.string())
    question_class.add_property("question_text", tb.string())
    question_class.add_property("max_marks", tb.int())
    question_class.add_property("criteria_breakdown", ao_class)

    tb.function("ExtractQuestions").returns(tb.list(question_class))
    return tb
```

### Why BAML Beats Pure Pydantic

1. **Token Efficiency:** BAML's terse syntax reduces token overhead by 60-80% vs JSON Schema
2. **Schema-Aligned Parsing (SAP):** Fault-tolerant Rust parser recovers malformed JSON
3. **Dynamic TypeBuilder:** Creates precise schemas per syllabus, avoiding "bag of attributes"

### System Integration: The EduFlow Architecture

**Data Pipeline:**
1. Teacher uploads syllabus → Agno calls `b.ExtractExamStructure` (BAML) → stores Meta-Schema
2. Teacher uploads exam paper → Restate triggers `IndexExamSaga` → Agentic Chunking → BAML extraction → pgvector storage
3. Student queries → Hybrid Search (keyword filter + vector similarity): `SELECT * FROM exam_questions WHERE metadata->>'topic' = 'Kinematics' AND (metadata->>'AO2')::int > 0 ORDER BY embedding <=> query_embedding`

### Restate for Durable Grading Workflows

```typescript
const gradingService = restate.service({
  name: "grading",
  handlers: {
    processExam: async (ctx, params) => {
      const questions = await ctx.run("extract_questions", () =>
        callBamlExtraction(params.text, params.syllabusId)
      );
      for (const question of questions) {
        await ctx.run(`index_q_${question.id}`, () =>
          agnoClient.index(question)
        );
      }
      return { status: "indexed", count: questions.length };
    }
  }
});
```

**Teacher Verification (Awakeables):**
1. AI calculates provisional grade
2. Workflow generates Approval ID
3. `await ctx.awakeable()` — function suspends completely, zero compute consumed
4. Teacher clicks "Approve" days later → Restate restores state, resumes at next line

---

## Part IX: DuckDB & Dragonfly Integration (Unified Data Layer)

### Architecture

```
┌─────────────────────────────────────────┐
│        Application Layer                │
│  (React UI, Hono Endpoints, etc.)       │
└────────────────┬────────────────────────┘
         ┌────────▼────────┐
         │  Schema Layer   │  ← BAML for dynamic types
         │  (BAML/Zod)     │  ← Zod for validation
         └────────┬────────┘
┌────────────────▼───────────────────────┐
│     Data Access Layer                  │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ DuckDB   │ │Postgres  │ │Dragonfly│ │
│  │ Analysis │ │ OLTP     │ │ Cache   │ │
│  └──────────┘ └──────────┘ └────────┘ │
└────────────────────────────────────────┘
```

| Aspect | BAML | DuckDB | Dragonfly |
|---|---|---|---|
| Primary Use | Schema generation, LLM structuring | Analytical queries | Caching, session storage |
| Streaming | `@stream.not_null`, `@stream.done` | Arrow IPC | N/A (in-memory) |
| Type Safety | BAML compiler → TS types | SQL + Drizzle types | ioredis typed client |
| Latency | 100-500ms (LLM call) | 10-100ms (local) | <1ms (in-memory) |
| Best For | Dynamic schemas, meta-programming | Large data analysis | Hot data, cache layer |

### DuckDB WASM (Browser) — Singleton Pattern

```typescript
class DuckDBManager {
  private db: any = null;
  private connection: any = null;
  private initPromise: Promise<void> | null = null;

  private async initialize(): Promise<void> {
    if (this.db) return;
    if (this.initPromise) return this.initPromise;
    this.initPromise = this.doInitialize();
    return this.initPromise;
  }

  async query(sql: string): Promise<QueryResult> {
    await this.initialize();
    const startTime = performance.now();
    const result = await this.connection.query(sql);
    // Convert Arrow to table format
  }
}
```

### Cloudflare DuckLake Deployment

```typescript
export class Container extends PkgContainer<EnvWithCustomVariables> {
  constructor(ctx: any, env: EnvWithCustomVariables) {
    super(ctx, env);
    let envConfig: Record<string, string> = {};
    if (env.R2_TOKEN && env.R2_ENDPOINT && env.R2_CATALOG) {
      envConfig = { ...envConfig, R2_TOKEN, R2_ENDPOINT, R2_CATALOG };
    }
    if (env.R2_ACCESS_KEY_ID && env.POSTGRES_HOST) {
      envConfig = { ...envConfig, POSTGRES_USER, ... };
    }
    this.envVars = envConfig;
  }
}
```

### Hono REST API with DuckDB

```typescript
api.post('/query', async (c) => {
  const queryResult = await query(body.query);
  return c.json(queryResult, 200);
});

api.post('/streaming-query', async (c) => {
  c.header('Content-Type', 'application/vnd.apache.arrow.stream');
  return stream(c, async (stream) => {
    const arrowStream = await streamingQuery(body.query, true);
    for await (const chunk of arrowStream) {
      await stream.write(chunk);
    }
  });
});
```

### Read-Through Cache with Hono + Dragonfly

```typescript
app.get("/:shortCode", async (c) => {
  const originalUrl = await cache.get(id);
  if (originalUrl) return c.redirect(originalUrl);  // Cache hit

  const result = await db.query.shortLinksTable.findFirst({
    where: and(eq(shortLinksTable.id, id), gt(shortLinksTable.expiresAt, new Date())),
  });
  if (!result) return c.notFound();
  // Repopulate cache
  await cache.set(result.id, result.originalUrl, "EXAT", expiresAt);
  return c.redirect(originalUrl);
});
```

### Write-Through Cache (Dragonfly)

```typescript
app.post("/short-links", zValidator("json", shortLinkInsertSchema), async (c) => {
  const req: ShortLinkInsert = c.req.valid("json");
  await db.insert(shortLinksTable).values(req).execute();
  const expiresAt = Math.trunc(req.expiresAt.getTime() / 1000);
  await cache.set(req.id, req.originalUrl, "EXAT", expiresAt);
  return c.json(req);
});
```

---

## Part X: Self-Healing Extraction Pipeline (Agentic Web Scraping)

### Neuro-Symbolic Web Intelligence Pipeline

The pipeline achieves a "closed-loop" intelligence cycle: Observation (Browserbase) → Perception (Z.ai GLM 4.6v) → Cognition (Cognee) → Systematization (BAML) → Creation (Ag-UI).

### Infrastructure: Browserbase CDP

```python
@tool
def capture_site_visuals(url: str, session_id: Optional[str] = None) -> str:
    bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])
    session = bb.sessions.create(project_id=os.environ["BROWSERBASE_PROJECT_ID"])
    
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(bb.sessions.connect_url(session.id))
        context = browser.contexts[0]
        page = context.pages[0]
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        
        client = context.new_cdp_session(page)
        res = client.send("Page.captureScreenshot", {
            "format": "png", "quality": 90, "fullpage": True, "captureBeyondViewport": True
        })
        image_data = base64.b64decode(res['data'])
        with open(abs_path, "wb") as f:
            f.write(image_data)
    return abs_path
```

### Perception: Z.ai GLM 4.6v via MCP

MCP tools exposed by the Z.ai Vision MCP Server:
- **ui_to_artifact:** Reverse-engineers visual bitmaps into semantic descriptions
- **extract_text_from_screenshot:** Advanced OCR for complex layouts
- **Web Reader:** Fetches raw DOM text

### Memory: Cognee Knowledge Graphs

```python
class UIComponent(DataPoint):
    name: str
    component_type: str
    description: str

class BrandStyle(DataPoint):
    category: str  # Color, Font, Spacing
    value: str
    usage_context: str

class WebPage(DataPoint):
    url: str
    title: str
```

**Cognify Process:** Z.ai analysis → `cognee.add()` → `cognee.cognify()` → Graph construction

### BAML Template Generation (Agentic Meta-Programming)

The Agno agent acts as a "Meta-Programmer" that writes BAML dynamically:

1. **Query Cognee:** "Does this product page have a SKU? A discount price?"
2. **Generate `.baml` file:** If graph indicates "Review Count" → add `review_count int`
3. **Compile:** BAML compiler generates Python client for type-safe extraction

```python
def generate_extraction_template(schema_description: str) -> str:
    baml_code = f"""
    // Auto-generated BAML Template
    class ExtractedSiteData {{
        headline string @description("The main H1 text")
        cta_label string @description("Text on the primary button")
        colors string @description("List of primary brand hex codes")
    }}
    
    function ExtractData(page_content: string) -> ExtractedSiteData {{
        client "openai/gpt-4o"
        prompt #"Extract the data from the following content: {{{{ page_content }}}} {{{{ ctx.output_format }}}}"#
    }}
    """
    with open("baml_src/auto_generated.baml", "w") as f:
        f.write(baml_code)
    return "BAML Template generated"
```

This creates a **Self-Healing Pipeline**: website layout changes → Z.ai vision detects shift → Cognee graph updates → Agent rewrites BAML template automatically.

---

## Part XI: CocoIndex Flow Strategy for Irish Education

| Flow Name | Source Type | Frequency | BAML Strategy | Graphiti Action |
|---|---|---|---|---|
| CurriculumFlow | curriculumonline.ie | Low (Annual) | ExtractScienceSpec, ExtractPrimaryFramework | Upsert Nodes (Stable) |
| EvidenceFlow | examinations.ie | High (Annual bursts) | ExtractMarkingScheme, ExtractExamQuestion | Append Episodes (Cumulative) |
| PolicyFlow | gov.ie | Ad-hoc (Weekly) | ExtractCircularMeta | Temporal Patching (State Change) |

### Graphiti Temporal Edge Schema

- **ASSESSES:** Connects AssessmentInstrument to LearningOutcome (weighted by Semantic Similarity)
- **DEFINES_QUALITY:** Connects EvidenceLogic to PedagogicalUnit
- **SUPERSEDES:** Temporal operator — Circular 0003/2018 supersedes Circular 29/02
- **EVIDENCES_DIFFICULTY:** Connects ChiefExaminerComment to LearningOutcome

**"Alignment Gap" Algorithm:**
1. Select subject → retrieve all LearningOutcome nodes
2. Traverse ASSESSES edges → count connected ExamQuestion nodes
3. Identify Orphan outcomes (degree_centrality == 0)
4. Report: "The following outcomes have not been assessed in the past 5 exam cycles."

---

## Summary Matrix

| Feature | Benefit |
|---------|---------|
| Schema-first design | Type safety across all languages |
| Built-in testing | Catch issues before deployment |
| Retry/fallback strategies | Production resilience |
| Type-safe streaming | Real-time UI updates |
| IDE playground | Fast iteration cycles |
| Error-tolerant parsing | Handles malformed LLM output |
| Dynamic TypeBuilder | Adapt schemas at runtime |
| Agentic meta-programming | Self-healing extraction logic |

---

## Resources

- Documentation: https://docs.boundaryml.com
- GitHub: https://github.com/BoundaryML/baml
- Examples: https://github.com/BoundaryML/baml-examples
- VSCode Extension: `Boundary.baml-extension`
