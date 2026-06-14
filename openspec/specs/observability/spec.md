# Observability Capability

## Purpose

`observability` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.


## Background
LLM observability, tracing, prompt management, and evaluation frameworks for monitoring and optimizing AI systems.

## Requirements

### Requirement: LLM Tracing
The system SHALL capture and analyze LLM calls.

#### Scenario: Function Tracing
- **GIVEN** a function decorated with observe
- **WHEN** the function is called
- **THEN** the call is traced with input, output, and metadata

#### Scenario: Manual Trace Creation
- **GIVEN** an LLM call without decorator
- **WHEN** tracing is needed
- **THEN** trace can be created manually with explicit parameters

#### Scenario: Session Tracking
- **GIVEN** multiple LLM calls in a session
- **WHEN** tracking session performance
- **THEN** all calls are grouped under a session

### Requirement: Prompt Management
The system SHALL version and manage prompts.

#### Scenario: Prompt Creation
- **GIVEN** a new prompt with variables
- **WHEN** created in the system
- **THEN** prompt is stored with version and configuration

#### Scenario: Prompt Compilation
- **GIVEN** a prompt with variables
- **WHEN** compiled with specific values
- **THEN** variables are substituted with provided values

#### Scenario: Prompt Versioning
- **GIVEN** an existing prompt
- **WHEN** a new version is created
- **THEN** both versions are available for comparison

### Requirement: A/B Testing
The system SHALL support comparing different prompts and models.

#### Scenario: Variant Comparison
- **GIVEN** multiple prompt variants
- **WHEN** tested on the same queries
- **THEN** results are compared for performance metrics

#### Scenario: Experiment Creation
- **GIVEN** a hypothesis about prompt performance
- **WHEN** an experiment is created
- **THEN** variants can be tested and results analyzed

### Requirement: Evaluation Metrics
The system SHALL provide metrics for RAG and LLM systems.

#### Scenario: Faithfulness Evaluation
- **GIVEN** an RAG system response
- **WHEN** evaluated for faithfulness
- **THEN** score reflects how faithful the answer is to retrieved context

#### Scenario: Answer Relevance
- **GIVEN** a question and answer
- **WHEN** evaluated for relevance
- **THEN** score reflects how relevant the answer is to the question

#### Scenario: Context Precision
- **GIVEN** retrieved contexts for a query
- **WHEN** evaluated for precision
- **THEN** score reflects the precision of retrieved contexts

### Requirement: Cost and Latency Tracking
The system SHALL track LLM costs and response times.

#### Scenario: Cost Calculation
- **GIVEN** LLM calls with token counts
- **WHEN** calculating costs
- **THEN** costs are calculated based on model pricing

#### Scenario: Latency Measurement
- **GIVEN** LLM calls
- **WHEN** measuring performance
- **THEN** latency is tracked for each call

## Supported Frameworks

### Langfuse (>=2.0.0)

**Key Features:**
- Tracing with decorators for automatic capture
- Prompt management with versioning and variable substitution
- A/B testing for prompt and model comparison
- Analytics with deep insights into LLM performance
- Multi-model support for all major LLM providers
- Session tracking for multi-turn conversations
- Evaluation scoring with manual and automated scores
- Cost tracking with configurable pricing
- User feedback capture

**Documentation:** https://langfuse.com/docs

**Skill:** [`.skills/langfuse/SKILL.md`](.skills/langfuse/SKILL.md)

### RAGAS (>=0.1.10)

**Key Features:**
- Trace-based metrics for RAG evaluation
- Multiple metrics: faithfulness, answer relevance, context precision, context recall
- LLM-based evaluation using configurable models
- Custom metrics for domain-specific evaluation
- Dataset support for various RAG datasets
- Batch evaluation with configurable workers
- Result analysis with filtering and statistics

**Documentation:** https://docs.ragas.io

**Skill:** [`.skills/ragas/SKILL.md`](.skills/ragas/SKILL.md)

## Tracing Patterns

### Decorator-Based Tracing

```python
from langfuse.decorators import observe

@observe()
def generate_response(query: str):
    """Trace a simple function."""
    return llm.generate(query)
```

### Manual Trace Creation

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-..."
)

trace = langfuse.trace(
    name="chat_completions",
    metadata={"user_id": "123"}
)

generation = trace.generation(
    name="gpt-4-response",
    model="gpt-4",
    input={"query": "What is AI?"},
    output={"response": "AI is..."},
    usage={"prompt_tokens": 10, "completion_tokens": 20}
)
```

### Session Tracking

```python
# Create session
session = langfuse.create_session(
    user_id="user_123",
    metadata={"subject": "Mathematics", "grade": "Junior Cycle"}
)

# Add traces to session
trace1 = session.trace(name="question_1")
trace2 = session.trace(name="question_2")
```

## Prompt Management

### Creating Prompts

```python
# Create a prompt
prompt = langfuse.create_prompt(
    name="curriculum_tutor",
    prompt="You are a helpful tutor for {subject}. Help students learn {topic}.",
    config={"temperature": 0.7, "max_tokens": 500}
)
```

### Compiling Prompts

```python
# Get prompt with variables
compiled = langfuse.get_prompt("curriculum_tutor").compile(
    subject="Mathematics",
    topic="algebra"
)
```

### Versioning Prompts

```python
# Version prompts
prompt_v2 = langfuse.create_prompt(
    name="curriculum_tutor",
    version=2,
    prompt="You are an expert tutor in {subject}. Guide students through {topic} with examples.",
    config={"temperature": 0.5, "max_tokens": 700}
)
```

## A/B Testing

### Creating Experiments

```python
# Create experiment
experiment = langfuse.create_experiment(
    name="prompt_optimization",
    description="Testing different prompt styles"
)
```

### Running Variants

```python
@observe(name="variant_a")
def run_variant_a(query: str):
    return llm.generate(f"Answer this: {query}")

@observe(name="variant_b")
def run_variant_b(query: str):
    return llm.generate(f"Please provide a detailed answer to: {query}")
```

## Evaluation Metrics

### Answer Quality Metrics

```python
from ragas.metrics import (
    faithfulness,        # How faithful is answer to context
    answer_relevancy,   # How relevant is answer to question
    answer_correctness,   # How correct is the answer
    answer_similarity    # Semantic similarity to ground truth
)
```

### Retrieval Metrics

```python
from ragas.metrics import (
    context_precision,    # Precision of retrieved contexts
    context_recall,       # Recall of relevant contexts
    context_relevancy,   # Relevance of contexts to question
    context_entity_recall # Entity-based recall
)
```

### Critique Metrics

```python
from ragas.metrics import (
    harmfulness,         # Is the answer harmful?
    coherence,           # Is the answer coherent?
    conciseness          # Is the answer concise?
)
```

### Running Evaluation

```python
from ragas import evaluate
from datasets import Dataset

evaluation_data = {
    "question": ["What is the capital of France?"],
    "answer": ["The capital of France is Paris."],
    "contexts": [["Paris is the capital and most populous city of France."]],
    "ground_truths": [["Paris"]]
}

dataset = Dataset.from_dict(evaluation_data)

result = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy, context_precision]
)

print(result.to_pandas())
```

## Scoring

### Manual Scoring

```python
from langfuse import Score

# Add manual scores
generation.score(
    name="relevance",
    value=0.9,
    comment="Highly relevant to user query"
)
```

### Automated Scoring

```python
# Add automated scores
generation.score(
    name="latency",
    value=generation.end_time - generation.start_time,
    comment="Response time in seconds"
)
```

### User Feedback

```python
# Capture user feedback
generation.score(
    name="user_feedback",
    value=1,  # 1-5 scale
    comment="Helpful response"
)
```

## Cost Tracking

### Configuring Pricing

```python
langfuse.configure_costs(
    model_pricing={
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
    }
)
```

### Querying Costs

```python
# Query costs
costs = langfuse.fetch_costs()
```

## Best Practices

### Tracing
1. **Granularity**: Add traces at appropriate levels (session, trace, generation)
2. **Metadata**: Include relevant metadata for filtering and analysis
3. **Context**: Capture user context and environment information

### Prompt Management
1. **Versioning**: Always version prompts when making changes
2. **Variables**: Use clear variable names in prompts
3. **Testing**: A/B test prompts before production deployment

### Evaluation
1. **Regular Testing**: Evaluate regularly during development
2. **A/B Testing**: Compare different RAG implementations
3. **Continuous Improvement**: Use results to improve system

### Analytics
1. **Regular Review**: Regularly review traces and scores
2. **Alerts**: Set up alerts for unusual patterns
3. **Optimization**: Use data to optimize prompts and models

## Configuration

### Environment Variables

```bash
# Langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

# RAGAS
OPENAI_API_KEY=sk-...
RAGAS_LLM_ENDPOINT=https://your-llm-endpoint
```

### Self-Hosting Langfuse

```bash
# Docker
docker run -p 3000:3000 \
  -e LANGFUSE_SALT=your-salt \
  -e DATABASE_URL=postgresql://... \
  langfuse/langfuse

# Kubernetes
helm repo add langfuse https://langfuse.github.io/charts
helm install langfuse langfuse/langfuse
```

## Integration with Other Systems

### Agent Integration
- **Agno**: Trace agent interactions and performance
- **Google ADK**: Monitor multi-agent workflows

### Knowledge Graph Integration
- **Cognee**: Evaluate knowledge graph queries
- **Graphiti Core**: Track temporal knowledge graph operations

### Data Pipeline Integration
- **Dagster**: Monitor pipeline performance and costs
- **DLT**: Track data loading operations

## Metric Selection Guide

| Use Case | Recommended Metrics |
|-----------|-------------------|
| RAG Quality | faithfulness, answer_relevancy, context_precision |
| Retrieval Quality | context_precision, context_recall, context_relevancy |
| Answer Quality | answer_correctness, answer_similarity |
| Safety | harmfulness |
| Coherence | coherence, conciseness |

## Troubleshooting

### No Traces
- Verify public and secret keys are set
- Check decorator is applied to functions
- Ensure tracing is enabled in configuration

### Evaluation Failures
- Verify LLM API key is set
- Check dataset format matches expected schema
- Ensure metrics are properly imported

### High Costs
- Review token usage in traces
- Optimize prompts to reduce tokens
- Consider using smaller models for some tasks
