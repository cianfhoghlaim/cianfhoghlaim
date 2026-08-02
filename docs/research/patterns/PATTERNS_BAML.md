# Pattern: BAML (Type-Safe LLM Extraction)

## Critical Constraints

| Constraint | Description | Violation Consequence |
|------------|-------------|----------------------|
| **Schema before extraction** | Define BAML schema before LLM calls | Unstructured, unparseable outputs |
| **Validate outputs** | Always validate extracted data | Runtime type errors |
| **Model fallbacks** | Configure backup models | Single point of failure |
| **Streaming for UX** | Use streaming for real-time feedback | Poor user experience |

---

## BAML Architecture

```
Content (text/image/audio)
        ↓
BAML Schema Definition (.baml files)
        ↓
BAML Compiler (generates typed client)
        ↓
LLM Call (with structured output)
        ↓
Validated Typed Object
```

---

## Schema Patterns

### Pattern 1: Basic Entity Extraction

**When to use**: Extracting structured data from unstructured text.

**Schema Definition** (`baml_src/resume.baml`):
```baml
// Define the output structure
class Resume {
    name string @description("Full name of the candidate")
    email string? @description("Email address if present")
    phone string? @description("Phone number if present")
    experience Experience[] @description("Work experience entries")
    skills string[] @description("Technical and soft skills")
    education Education[] @description("Educational background")
}

class Experience {
    company string
    title string
    start_date string @description("Format: YYYY-MM or YYYY")
    end_date string? @description("Format: YYYY-MM, YYYY, or 'Present'")
    description string
}

class Education {
    institution string
    degree string
    field string?
    year int?
}

// Define the extraction function
function ExtractResume(resume_text: string) -> Resume {
    client "openai/gpt-4o-mini"
    prompt #"
        Extract structured resume information from the following text.
        Be precise and extract only what is explicitly stated.

        Resume:
        {{ resume_text }}
    "#
}
```

**Usage** (Python):
```python
from baml_client import b
from baml_client.types import Resume

async def extract_resume(text: str) -> Resume:
    """Extract structured resume data with type safety."""
    result = await b.ExtractResume(resume_text=text)
    return result  # Fully typed Resume object

# Example
resume = await extract_resume(pdf_text)
print(f"Name: {resume.name}")
print(f"Skills: {', '.join(resume.skills)}")
for exp in resume.experience:
    print(f"  {exp.title} at {exp.company}")
```

### Pattern 2: Multimodal Extraction (Images)

**When to use**: Extracting data from images, PDFs, receipts.

**Schema Definition** (`baml_src/receipt.baml`):
```baml
class ReceiptData {
    merchant_name string
    date string @description("Format: YYYY-MM-DD")
    transactions Transaction[]
    subtotal float?
    tax float?
    tip float?
    total float
    payment_method string?
}

class Transaction {
    item_name string
    quantity int @description("Default 1 if not specified")
    unit_price float
    total_price float
}

// Multimodal function accepting image
function ExtractReceipt(receipt_image: image) -> ReceiptData {
    client Gemini25Flash  // Vision-capable model
    prompt #"
        Extract all transaction data from this receipt image.
        Be precise with prices and quantities.
        If a value is unclear, use your best judgment.

        {{ receipt_image }}
    "#
}
```

**Usage**:
```python
from baml_client import b
from baml_client.types import Image

async def process_receipt(image_path: str) -> dict:
    """Process receipt image to structured data."""
    image = Image.from_file(image_path)
    result = await b.ExtractReceipt(receipt_image=image)

    return {
        "merchant": result.merchant_name,
        "date": result.date,
        "total": result.total,
        "items": [
            {"name": t.item_name, "price": t.total_price}
            for t in result.transactions
        ],
    }
```

### Pattern 3: Enum and Union Types

**When to use**: Constraining outputs to specific values.

**Schema Definition**:
```baml
// Enum for fixed categories
enum Sentiment {
    POSITIVE
    NEGATIVE
    NEUTRAL
    MIXED
}

enum ContentType {
    ARTICLE
    BLOG_POST
    NEWS
    DOCUMENTATION
    SOCIAL_MEDIA
}

// Union type for polymorphic responses
class ClassificationResult {
    sentiment Sentiment
    content_type ContentType
    confidence float @description("0.0 to 1.0")
    reasoning string @description("Brief explanation")
}

function ClassifyContent(text: string) -> ClassificationResult {
    client "anthropic/claude-3-5-sonnet"
    prompt #"
        Classify the following content:

        {{ text }}

        Provide sentiment, content type, confidence score, and reasoning.
    "#
}
```

### Pattern 4: Dynamic Schema Generation

**When to use**: When schema structure varies by input type.

**Schema Definition**:
```baml
// Meta-schema for dynamic extraction
class FieldDefinition {
    name string
    type string @description("string, int, float, bool, array, object")
    description string?
    required bool
}

class DynamicSchema {
    entity_type string
    fields FieldDefinition[]
}

// Step 1: Generate schema from content
function InferSchema(document_text: string) -> DynamicSchema {
    client "anthropic/claude-3-5-sonnet"
    prompt #"
        Analyze this document and determine the optimal schema
        for extracting structured data from it.

        Document:
        {{ document_text }}
    "#
}

// Step 2: Extract using inferred schema (requires code)
```

**Usage** (two-step extraction):
```python
async def dynamic_extract(document: str) -> dict:
    # Step 1: Infer schema
    schema = await b.InferSchema(document_text=document)

    # Step 2: Build extraction prompt dynamically
    fields_prompt = "\n".join([
        f"- {f.name} ({f.type}): {f.description or 'N/A'}"
        for f in schema.fields
    ])

    # Step 3: Extract using dynamic prompt
    result = await llm_call(f"""
        Extract the following fields from the document:
        {fields_prompt}

        Document:
        {document}
    """)

    return result
```

---

## Client Configuration

### Pattern 5: Multi-Provider Setup

**When to use**: Production deployments with fallbacks.

**Configuration** (`baml_src/clients.baml`):
```baml
// Primary: OpenAI
client<llm> OpenAI4o {
    provider "openai"
    options {
        model "gpt-4o"
        temperature 0.1
        max_tokens 4096
    }
}

// Secondary: Anthropic
client<llm> Claude35Sonnet {
    provider "anthropic"
    options {
        model "claude-3-5-sonnet-20241022"
        temperature 0.1
        max_tokens 4096
    }
}

// Tertiary: Google
client<llm> Gemini25Flash {
    provider "google-ai"
    options {
        model "gemini-2.5-flash-preview-05-20"
        temperature 0.1
    }
}

// Fallback chain
client<llm> ProductionClient {
    provider "fallback"
    options {
        strategy [OpenAI4o, Claude35Sonnet, Gemini25Flash]
    }
}

// Cost-optimized for simple tasks
client<llm> CheapClient {
    provider "openai"
    options {
        model "gpt-4o-mini"
        temperature 0
    }
}
```

### Pattern 6: Retry Configuration

**When to use**: Handling transient failures.

**Configuration**:
```baml
retry_policy DefaultRetry {
    max_retries 3
    strategy {
        type "exponential_backoff"
        delay_ms 1000
        multiplier 2
        max_delay_ms 10000
    }
}

client<llm> RobustClient {
    provider "openai"
    retry_policy DefaultRetry
    options {
        model "gpt-4o"
        timeout_ms 60000
    }
}
```

---

## Streaming Patterns

### Pattern 7: Streaming Extraction

**When to use**: Real-time feedback during extraction.

**Schema Definition**:
```baml
class StreamingAnalysis {
    summary string @stream(true)
    key_points string[] @stream(true)
    sentiment Sentiment
}

function AnalyzeDocument(doc: string) -> StreamingAnalysis {
    client "openai/gpt-4o"
    prompt #"
        Analyze this document and provide:
        1. A comprehensive summary
        2. Key points as a list
        3. Overall sentiment

        Document:
        {{ doc }}
    "#
}
```

**Usage**:
```python
async def stream_analysis(document: str):
    """Stream analysis results in real-time."""
    stream = b.stream.AnalyzeDocument(doc=document)

    async for partial in stream:
        if partial.summary:
            print(f"Summary (partial): {partial.summary}")
        if partial.key_points:
            print(f"Points so far: {partial.key_points}")

    # Get final complete result
    final = await stream.get_final_response()
    print(f"Sentiment: {final.sentiment}")
```

---

## Curriculum-Specific Schemas

### Pattern 8: Irish Curriculum Extraction

**When to use**: Processing NCCA curriculum documents.

**Schema Definition** (`baml_src/curriculum.baml`):
```baml
enum Subject {
    MATHEMATICS
    IRISH
    ENGLISH
    SCIENCE
    HISTORY
    GEOGRAPHY
    MUSIC
    ART
    PE
    SPHE
    OTHER
}

enum Level {
    JUNIOR_INFANTS
    SENIOR_INFANTS
    FIRST_CLASS
    SECOND_CLASS
    THIRD_CLASS
    FOURTH_CLASS
    FIFTH_CLASS
    SIXTH_CLASS
    FIRST_YEAR
    SECOND_YEAR
    THIRD_YEAR
    TRANSITION_YEAR
    FIFTH_YEAR
    SIXTH_YEAR
}

class LearningOutcome {
    code string @description("e.g., MA.1.1, EN.2.3")
    description string
    description_irish string? @description("Irish translation if available")
    strand string
    strand_unit string?
    skills string[]
}

class CurriculumUnit {
    subject Subject
    level Level
    title string
    title_irish string?
    learning_outcomes LearningOutcome[]
    prerequisites string[] @description("Prior knowledge required")
    cross_curricular_links string[]
}

function ExtractCurriculum(document: string) -> CurriculumUnit {
    client Gemini25Flash
    prompt #"
        Extract curriculum information from this NCCA document.
        Identify learning outcomes, prerequisites, and connections.

        Document:
        {{ document }}
    "#
}
```

### Pattern 9: Exam Paper Analysis

**When to use**: Processing SEC examination papers.

**Schema Definition**:
```baml
enum ExamLevel {
    HIGHER_LEVEL
    ORDINARY_LEVEL
    FOUNDATION_LEVEL
}

class ExamQuestion {
    number string @description("e.g., Q1, Q2(a)")
    marks int
    topic string
    difficulty string @description("easy, medium, hard")
    requires_irish bool @description("True if question is in Irish")
    learning_outcomes string[] @description("Related LO codes")
}

class ExamPaper {
    subject Subject
    year int
    level ExamLevel
    total_marks int
    duration_minutes int
    questions ExamQuestion[]
    topic_distribution map<string, int> @description("Topic -> marks")
}

function AnalyzeExamPaper(paper_text: string) -> ExamPaper {
    client "anthropic/claude-3-5-sonnet"
    prompt #"
        Analyze this SEC examination paper.
        Extract all questions, their marks, topics, and difficulty.

        Paper:
        {{ paper_text }}
    "#
}
```

---

## Integration Points

| Component | Connects To | Pattern |
|-----------|-------------|---------|
| **CocoIndex** | BAMLExtract transform | Structured extraction in flows |
| **Dagster** | Asset outputs | Validated structured data |
| **FastAPI** | Response models | Type-safe API responses |
| **Agents** | Tool outputs | Structured agent results |

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| No schema validation | Always use BAML client, not raw LLM |
| Missing optional markers | Use `?` for truly optional fields |
| Vague descriptions | Add `@description` for complex fields |
| Single model dependency | Configure fallback chain |
| No streaming for long outputs | Enable `@stream(true)` |
| Missing retry policy | Configure exponential backoff |
| Hardcoded model names | Use client aliases |

---

## Testing Patterns

### Pattern 10: Schema Testing

**When to use**: Validating extraction accuracy.

**Implementation**:
```python
import pytest
from baml_client import b

@pytest.fixture
def sample_resume():
    return """
    John Doe
    Email: john@example.com
    Experience:
    - Software Engineer at Acme Inc (2020-Present)
    Skills: Python, TypeScript, SQL
    """

async def test_resume_extraction(sample_resume):
    result = await b.ExtractResume(resume_text=sample_resume)

    assert result.name == "John Doe"
    assert result.email == "john@example.com"
    assert len(result.experience) >= 1
    assert "Python" in result.skills

async def test_missing_optional_fields():
    """Test handling of missing optional data."""
    minimal = "Jane Smith - Software Developer"
    result = await b.ExtractResume(resume_text=minimal)

    assert result.name == "Jane Smith"
    assert result.email is None  # Optional field
    assert result.phone is None
```

---

## References

- Source: `taighde/baml/`, `baml_src/`
- Skills: `.claude/skills/baml/`
- Documentation: https://docs.boundaryml.com
- Examples: `sruth/crypteolas/baml_src/`, `sruth/oideachais/baml_src/`
