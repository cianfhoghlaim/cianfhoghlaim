---
title: "ML Pipelines & Observability"
domain: ai_ml
date: 2026-06-06
migration_source: docs/bunchloch/meaisínfhoghlaim + docs/bunchloch/teanga
ccc_query_hints: ["ml pipelines mlflow langfuse litellm experiment tracking model registry observability"]
source_files: "3 files from meaisínfhoghlaim and teanga"
---
# ML Pipelines & Observability

> Merged from 3 source files across the meaisínfhoghlaim and teanga document collections. Migration date: 2026-06-06.

## Table of Contents

- [langfuse-guide](#langfuse-guide-md)
- [litellm-comprehensive-guide](#litellm-comprehensive-guide-md)
- [litellm-deployment-guide](#litellm-deployment-guide-md)

---

## langfuse-guide

<!-- BEGIN: original content from langfuse-guide.md -->

*Source: `docs/bunchloch/meaisínfhoghlaim/langfuse-guide.md` (12711 words, 4481 lines)*

# Langfuse LLM Observability Platform - Comprehensive Research

## Executive Summary

Langfuse is an open-source LLM engineering platform (YC W23) that provides comprehensive observability, tracing, and analytics for LLM-powered applications. It enables teams to debug, analyze, and iterate on LLM applications through detailed tracing, cost tracking, evaluation, and prompt management capabilities.

**Key Stats:**
- Open source on GitHub
- Available as Cloud (SaaS) or self-hosted
- Supports Python, JavaScript/TypeScript SDKs
- Integrates with OpenTelemetry, LangChain, LlamaIndex, LiteLLM, and 50+ other frameworks
- Pricing: Traces + Observations + Scores

---

## 1. CORE ARCHITECTURE AND CONCEPTS

### 1.1 What is Langfuse

Langfuse is a purpose-built LLM observability platform that captures:
- Complete execution traces of LLM interactions
- Input/output data for every step in an application
- Latency and cost metrics for each operation
- User interactions and sessions
- Evaluation scores and feedback

**Core Purpose:**
Enable teams to collaboratively monitor, debug, analyze, and iterate on LLM applications in production and development environments.

### 1.2 Core Entities: The Data Model

#### Traces
- **Definition**: A single execution of an LLM feature, from start to finish
- **Purpose**: Container for all operations occurring in a request
- **Characteristics:**
  - Usually corresponds to a single API call to an application
  - Contains overall input/output data
  - Holds metadata: session_id, user_id, tags
  - Shares same ID as OTel trace (OpenTelemetry compatibility)
  - Has timestamps and execution duration
- **Key Attributes:**
  - `trace_id`: Unique identifier
  - `name`: Human-readable name
  - `user_id`: Associated user
  - `session_id`: Grouping with other traces
  - `metadata`: Custom key-value pairs
  - `tags`: Array of categorization tags
  - `input`, `output`: Trace-level data
  - `duration`: Total execution time

#### Observations
- **Definition**: Individual execution steps within a trace
- **Purpose**: Record granular operations in a trace hierarchy
- **Types of Observations:**

  1. **Event** - Discrete tracking points (no duration)
  2. **Span** - Generic operation with duration/timing
  3. **Generation** - LLM call with model, prompts, completions, tokens, costs
  4. **Agent** - Flow decision-making component
  5. **Tool** - External API call (weather API, search, etc.)
  6. **Chain** - Links context between application steps
  7. **Retriever** - Data retrieval (vector store, database)
  8. **Embedding** - Vector generation with tokens/costs
  9. **Guardrail** - Content protection component
  10. **Evaluator** - Output assessment function

- **Key Attributes (shared):**
  - `observation_id`: Unique ID
  - `trace_id`: Parent trace
  - `parent_observation_id`: Nesting support
  - `start_time`, `end_time`: Duration tracking
  - `input`, `output`: Data for the operation
  - `metadata`: Custom attributes
  - `status`: success, error, etc.
  - `level`: log level classification

#### Generations (Specialized Span)
- **Definition**: Specialized observation for LLM calls
- **Unique Attributes:**
  - `model`: Model name (OpenAI, Claude, etc.)
  - `model_parameters`: Temperature, max_tokens, etc.
  - `usage_details`: Token counts (input, output, cached, reasoning, audio, etc.)
  - `cost_details`: Calculated costs by token type
  - `prompt`: The input prompt(s)
  - `completion`: The model response
  - `top_level_spans`: Can be root-level operations in traces
  - `finish_reason`: Model's completion reason
  - `temperature`, `max_tokens`, etc.: Model-specific parameters

### 1.3 Data Model Relationships

```
Trace (single request)
├── Observation (step)
│   ├── Event (discrete point)
│   ├── Span (operation)
│   │   └── Generation (LLM call)
│   │       ├── Prompt data
│   │       ├── Completion data
│   │       └── Token/cost metrics
│   ├── Tool
│   ├── Retriever
│   └── [other observation types]
├── Sessions (optional grouping across traces)
├── Scores (evaluations on trace/observation)
└── Metadata & Tags
```

**Key Features:**
- Observations nest hierarchically (parent-child relationships)
- Automatic nesting via OpenTelemetry context propagation
- Manual nesting by setting parent_observation_id
- Traces can be linked across distributed systems via trace IDs

### 1.4 Sessions and User Tracking

#### Sessions
- **Definition**: Logical grouping of traces and observations across multiple API calls
- **Use Cases:**
  - Multi-turn conversations (chatbot interactions)
  - Extended workflows spanning multiple traces
  - Session replay for user interactions
  - Batch processes with related operations
- **Implementation:**
  - `session_id`: US-ASCII string < 200 characters
  - Propagate via `propagate_attributes(session_id="...")`
  - All observations with same session_id grouped together
  - Support for session bookmarking, sharing, annotations

#### User Tracking
- **Definition**: Map traces and observations to individual users
- **Implementation:**
  - `user_id`: Username, email, or unique identifier
  - Propagate via `propagate_attributes(user_id="...")`
- **Features:**
  - User Explorer dashboard showing all users
  - Segment by token usage, trace count, feedback
  - Cost and usage attribution per user
  - User activity traces and history

### 1.5 Metadata and Tagging Systems

#### Metadata
- **Purpose**: Attach arbitrary key-value pairs to observations
- **Scope**: Can be attached to traces, spans, generations, events
- **Propagation**: Child observations automatically inherit parent metadata
- **Use Cases:**
  - Track request context (source, region, environment)
  - Store custom business logic attributes
  - Enable filtering and analysis in dashboards
- **Example:**
  ```python
  with propagate_attributes(metadata={
      "source": "api",
      "region": "us-east-1",
      "user_tier": "premium",
      "feature_flag": "new_rag_v2"
  }):
      # All nested observations inherit this metadata
      result = process_request()
  ```

#### Tags
- **Purpose**: Flexible categorization of traces
- **Scope**: Applied at trace level
- **Usage:**
  - Filter traces in UI and API
  - Group by feature/version/environment
  - Common patterns:
    - App versions: 'app-v1', 'app-v2'
    - Techniques: 'rag', 'cot', 'few-shot'
    - Environments: 'local', 'staging', 'prod'
    - Experiments: 'exp-a', 'exp-b'
- **Implementation:**
  ```python
  langfuse_context.update_current_trace(
      tags=["production", "rag-v2", "user-feedback"]
  )
  ```

#### Scores
- **Definition**: Evaluation metrics on traces, observations, sessions, or dataset runs
- **Types:**
  - Numeric (0-1, 1-10 scale)
  - Categorical (good/bad, happy/sad)
  - Boolean (pass/fail)
- **Features:**
  - Optional comments and reasoning
  - Schema validation via score configs
  - Support for LLM-as-a-Judge scores
  - Manual annotations
  - Custom evaluation pipelines

---

## 2. TRACING AND OBSERVABILITY

### 2.1 How Traces and Spans Work

#### Trace Lifecycle
1. **Initialization**: Trace created with unique ID and timestamp
2. **Observation Logging**: Operations recorded as spans/observations
3. **Nesting**: Child operations nested under parent spans
4. **Completion**: Trace completed with overall metrics
5. **Export**: Data sent to Langfuse backend

#### Context Propagation (OpenTelemetry)
- **Automatic**: When you create a nested span, it automatically becomes a child of current span
- **Manual**: Can explicitly set parent via parent_observation_id
- **Distributed**: Trace IDs propagate across service boundaries
- **Benefit**: No need to manually thread context through function calls

**Example Flow:**
```
Trace: user_request_123
├─ Span: retrieval
│  └─ Operation: vector_search (nested automatically)
├─ Span: llm_generation
│  ├─ Generation: llm_call (OpenAI)
│  └─ Span: post_processing
└─ Span: response_formatting
```

### 2.2 Observation Types and Characteristics

| Type | Purpose | Duration | Tokens/Cost | Key Attributes |
|------|---------|----------|-------------|-----------------|
| **Event** | Discrete occurrences | No | No | message, level |
| **Span** | Generic operations | Yes | No | name, status |
| **Generation** | LLM calls | Yes | Yes | model, prompt, completion |
| **Tool** | API calls | Yes | No | tool_name, result |
| **Retriever** | Data lookups | Yes | No | retriever_name, items |
| **Embedding** | Vector generation | Yes | Yes | model, tokens |
| **Agent** | Decision logic | Yes | No | action, reasoning |
| **Chain** | Step linking | Yes | No | chain_type |
| **Guardrail** | Safety checks | Yes | No | violation_type |
| **Evaluator** | Output assessment | Yes | No | score, reasoning |

### 2.3 Input/Output Tracking

#### What Gets Captured
- **Inputs**: Prompts, queries, function arguments
- **Outputs**: Model completions, API responses, function returns
- **Multi-modal Support**: Text, images, audio, JSON, tables
- **Large Payloads**: Stored in S3/blob storage with database references
- **Streaming**: Capture first token latency separately

#### Serialization
- **JSON Format**: Structured data serialized as JSON
- **Text Format**: Plain text for logs and error messages
- **Automatic Inference**: SDKs automatically capture function arguments/returns
- **Custom Handling**: Can manually specify input/output data

### 2.4 Latency and Cost Tracking

#### Latency Metrics
- **Span Duration**: `end_time - start_time`
- **Time-to-First-Token (TTFT)**: For streaming generations
- **Queue Time**: Wait time before operation starts
- **Components Measured:**
  - Total trace duration
  - Per-operation duration
  - Bottleneck identification
  - Parallelism visualization

#### Cost Tracking
- **Automatic Calculation**: For supported models (OpenAI, Anthropic, Google)
- **Two Mechanisms:**
  1. **Ingestion**: Cost data from LLM provider response
  2. **Inference**: Calculate from tokens if cost not provided
- **Priority**: Ingested cost > Inferred cost
- **Custom Models**: Define custom model prices per project

### 2.5 Token Usage Tracking

#### Usage Types Supported
- **Basic**: `input`, `output`
- **Advanced**: `cached_tokens`, `audio_tokens`, `image_tokens`, `reasoning_tokens`
- **Flexibility**: Any custom usage types supported

#### How It Works
1. **LLM Provider Response**: SDK extracts token counts
2. **Model Definition**: Maps token counts to costs
3. **Calculation**: Applies price per token type
4. **Storage**: Stored with generation for analysis

#### Model Definitions
- **Predefined Models**: 100+ built-in models (OpenAI, Claude, etc.)
- **Custom Models**: Add your own via API or UI
- **Tokenizer Support**: Uses official tokenizers (tiktoken, etc.)
- **Price Management**: Update prices without code changes

```python
# Example: Custom model definition
{
    "model_name": "my-custom-llm",
    "input_cost": 0.001,  # per 1K tokens
    "output_cost": 0.002,
    "cached_tokens_cost": 0.0001,
    "tokenizer": "tiktoken:cl100k_base"
}
```

### 2.6 Trace Timeline Visualization

#### Visualization Modes
1. **Timeline View**: Chronological visualization
   - Observations displayed as bars on timeline
   - Width proportional to duration
   - Color-coded by latency/cost percentiles
   - TTFT shown separately for streaming
   - Hover for detailed latency info

2. **Tree View**: Hierarchical structure
   - Parent-child relationships
   - Expandable/collapsible nodes
   - Shows nesting depth

3. **Graph View**: Network visualization
   - Component relationships
   - Data flow between operations

4. **Detail Panels**: Content inspection
   - Input/output data
   - Metadata and tags
   - Token counts and costs

#### Latency Analysis
- **Identify Bottlenecks**: See which operations are slowest
- **Parallelism**: Understand concurrent operations
- **Comparisons**: Compare latency across versions
- **Debugging**: Inspect individual operations for issues

---

## 3. SELF-HOSTING AND DEPLOYMENT

### 3.1 Deployment Architecture

#### Architecture Components

```
┌─────────────────────────────────────────────┐
│  Application SDKs (Python, JS/TS)           │
│  or OpenTelemetry Integration               │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Langfuse Web Server                        │
│  - REST API endpoint                        │
│  - Authentication (API keys)                │
│  - Request validation                       │
│  - Minimal processing                       │
└──────────────────┬──────────────────────────┘
                   │
                   ▼ (queued)
┌─────────────────────────────────────────────┐
│  Redis (Queue & Cache)                      │
│  - Ingestion queue                          │
│  - Cache for prompts                        │
│  - API key cache                            │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Langfuse Worker (Async Processing)         │
│  - Tokenization                             │
│  - Cost calculation                         │
│  - Data enrichment                          │
│  - Rate limiting                            │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   ┌─────────────┐      ┌──────────────┐
   │ PostgreSQL  │      │ ClickHouse   │
   │ (OLTP)      │      │ (OLAP)       │
   └─────────────┘      └──────────────┘
   - Users, orgs       - Traces, obs.
   - Projects, keys    - Analytics
   - Sessions          - Fast queries
        │                     │
        └──────────┬──────────┘
                   ▼
           ┌──────────────────┐
           │ S3/Blob Storage  │
           │ - Large payloads │
           │ - Multi-modal    │
           └──────────────────┘
```

#### Database Roles

**PostgreSQL (Transactional - OLTP)**
- Users and authentication
- Organizations and projects
- API keys and credentials
- Sessions metadata
- Configuration and state
- Indexes for fast lookups
- Version: >= 12

**ClickHouse (Analytical - OLAP)**
- Traces and their hierarchies
- Observations (all types)
- Scores and evaluations
- Analytics queries
- Time-series data
- Columnar storage for performance
- Version: >= 24.3
- Minimum 16GB RAM for larger deployments
- 3 replicas recommended for production

**Redis (Cache & Queue)**
- Ingestion queue (message buffer)
- Prompt caching
- API key cache (in-memory)
- Session cache
- Can use Redis or Valkey

**S3/Blob Storage (Object Storage)**
- Raw payloads (when > size threshold)
- Multi-modal data (images, audio)
- Large exports
- Backups
- Supports: AWS S3, MinIO, Azure Blob Storage, GCS

### 3.2 Deployment Options

#### 1. Langfuse Cloud (Hosted)
**Best For**: Quick setup, no infrastructure management
- **Availability**: US (Oregon) and EU (Ireland) regions
- **Maintenance**: Handled by Langfuse team
- **Scale**: Enterprise-grade infrastructure
- **Pricing**: Per-unit (traces + observations + scores)
- **Setup Time**: Minutes

#### 2. Docker Compose (Development/Testing)
**Best For**: Local development, proof-of-concept, < 1M traces/month
- **Setup**: Single `docker-compose up`
- **Components**: PostgreSQL, ClickHouse, Redis, Langfuse containers
- **Time**: ~2-3 minutes to ready state
- **Limitations**: No HA, no persistence, security not production-ready
- **Not Recommended**: Production use

#### 3. Kubernetes + Helm (Production)
**Best For**: Production, high availability, scalability
- **Helm Chart**: Community-maintained langfuse/langfuse-k8s
- **Requirements**: Kubernetes 1.19+, Helm 3
- **Components**: Separate deployments for web/worker, managed DBs
- **HA**: Multiple replicas per component
- **Scaling**: Horizontal Pod Autoscaling (HPA), KEDA, VPA
- **Storage**: Persistent volumes for databases
- **Time**: 30+ minutes with proper configuration

#### 4. Cloud Templates (AWS, Azure, GCP)
**Best For**: Quick production setup on specific cloud
- **Infrastructure**: Terraform templates
- **Managed Services**: Managed RDS, managed ClickHouse
- **Networking**: VPCs, security groups configured
- **Time**: 15-30 minutes with defaults

### 3.3 Environment Variables and Configuration

#### Critical Configuration Variables

**Application Core:**
```bash
# Domain and authentication
NEXTAUTH_URL=https://langfuse.mycompany.com
NEXTAUTH_SECRET=<random-256-bit-key>

# Encryption
ENCRYPTION_KEY=<random-256-bit-key>
SALT=<random-salt>

# Database connections
DATABASE_URL=postgresql://user:password@host:5432/langfuse
CLICKHOUSE_URL=http://clickhouse:8123
CLICKHOUSE_PASSWORD=password

# Redis
REDIS_CONNECTION_STRING=redis://redis:6379

# API Configuration
LANGFUSE_BASE_URL=https://langfuse.mycompany.com
```

**Optional Initialization:**
```bash
LANGFUSE_INIT_ORG_ID=org-1
LANGFUSE_INIT_PROJECT_ID=proj-1
LANGFUSE_INIT_USER_EMAIL=admin@company.com
LANGFUSE_INIT_USER_PASSWORD=<secure-password>
```

**Storage & Performance:**
```bash
# S3/Blob storage
S3_ENDPOINT=https://s3.amazonaws.com
S3_BUCKET_NAME=langfuse-bucket
S3_ACCESS_KEY_ID=<key>
S3_SECRET_ACCESS_KEY=<secret>
S3_REGION=us-east-1

# ClickHouse specifics
CLICKHOUSE_CLUSTER_NAME=default
CLICKHOUSE_REPLICATION_FACTOR=3

# Worker configuration
LANGFUSE_INGESTION_QUEUE_PROCESSING_CONCURRENCY=20
LANGFUSE_TRACE_UPSERT_WORKER_CONCURRENCY=20
```

**Security & Compliance:**
```bash
# CORS
ALLOWED_ORIGINS=https://myapp.com,https://api.myapp.com

# Data retention
LANGFUSE_DATA_RETENTION_DAYS=90

# SSO (if using)
OAUTH_PROVIDER_ID=okta
OAUTH_CLIENT_ID=<id>
OAUTH_CLIENT_SECRET=<secret>
```

### 3.4 Docker Deployment

#### Basic Docker Compose Setup
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: langfuse
    volumes:
      - postgres_data:/var/lib/postgresql/data

  clickhouse:
    image: clickhouse/clickhouse-server:latest
    environment:
      CLICKHOUSE_DB: langfuse
    volumes:
      - clickhouse_data:/var/lib/clickhouse
    
  redis:
    image: redis:7-alpine
    
  langfuse-web:
    image: langfuse/langfuse:latest
    depends_on:
      - postgres
      - clickhouse
      - redis
    environment:
      DATABASE_URL: postgresql://langfuse:${POSTGRES_PASSWORD}@postgres:5432/langfuse
      CLICKHOUSE_URL: http://clickhouse:8123
      REDIS_CONNECTION_STRING: redis://redis:6379
      NEXTAUTH_SECRET: ${NEXTAUTH_SECRET}
      ENCRYPTION_KEY: ${ENCRYPTION_KEY}
      SALT: ${SALT}
    ports:
      - "3000:3000"

  langfuse-worker:
    image: langfuse/langfuse:latest
    depends_on:
      - postgres
      - clickhouse
      - redis
    environment:
      # Same as web
      DATABASE_URL: postgresql://langfuse:${POSTGRES_PASSWORD}@postgres:5432/langfuse
      CLICKHOUSE_URL: http://clickhouse:8123
      REDIS_CONNECTION_STRING: redis://redis:6379
    command: "node dist/server.js worker"

volumes:
  postgres_data:
  clickhouse_data:
```

#### Kubernetes Deployment Example
```bash
# Add Helm repository
helm repo add langfuse https://langfuse.github.io/langfuse-k8s
helm repo update

# Install with values file
helm install langfuse langfuse/langfuse -f values.yaml

# Upgrade
helm upgrade langfuse langfuse/langfuse -f values.yaml
```

### 3.5 Database Requirements

#### PostgreSQL Requirements
- **Version**: >= 12 (16+ recommended)
- **RAM**: 2-4GB minimum
- **Storage**: 100GB+ for metadata
- **Connections**: Langfuse needs ~20 connections
- **Timezone**: Must be UTC (required!)
- **Backup**: Regular snapshots recommended
- **Managed Services**: AWS RDS, Azure Database, Google Cloud SQL

#### ClickHouse Requirements
- **Version**: >= 24.3
- **RAM**: 16GB minimum (32GB+ for larger deployments)
- **CPU**: 4+ cores recommended
- **Storage**: 500GB-5TB+ depending on retention
- **Replication**: 3 replicas minimum for HA
- **Timezone**: Must be UTC (required!)
- **Sharding**: Single shard supported (don't use multi-shard)
- **Network**: Low-latency connection to web/worker

#### Scaling Thresholds
| Traces/Month | Recommendation |
|--------------|-----------------|
| < 1M | Docker Compose on VM |
| 1M - 100M | Kubernetes, 2CPU/4GB per container |
| 100M - 1B | Kubernetes, 4CPU/8GB per container, ClickHouse large |
| > 1B | Kubernetes, enterprise ClickHouse, multi-region |

### 3.6 Configuration Best Practices

**Production Hardening:**
```bash
# Memory limits (Node.js)
NODE_OPTIONS=--max-old-space-size=20480

# Keep-alive timeout (prevent 502 errors)
KEEP_ALIVE_TIMEOUT=65000  # Load balancer timeout + 5s

# Connection pooling
DATABASE_CONNECTION_POOL_SIZE=20
DATABASE_CONNECTION_TIMEOUT_SECONDS=30

# Queue optimization
LANGFUSE_INGESTION_QUEUE_BATCH_SIZE=100
LANGFUSE_INGESTION_QUEUE_PROCESSING_TIMEOUT_SECONDS=60

# ClickHouse optimization
CLICKHOUSE_ASYNC_INSERT=true
CLICKHOUSE_ASYNC_INSERT_BUSY_TIMEOUT_MS=5000
```

**Observability & Monitoring:**
```bash
# Health endpoints
HEALTH_CHECK_ENABLED=true

# Metrics (StatsD)
TELEMETRY_ENABLED=true
STATSD_ENABLED=true
STATSD_HOST=localhost
STATSD_PORT=8125

# OpenTelemetry
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

**Data Retention & Privacy:**
```bash
# Data retention policy
LANGFUSE_DATA_RETENTION_DAYS=90

# PII masking (enterprise)
DATA_MASKING_ENABLED=true
DATA_MASKING_PATTERNS=email,ssn,api_key

# GDPR compliance
GDPR_MODE=true
```

---

## 4. INTEGRATIONS AND FRAMEWORKS

### 4.1 Native SDK Support

#### Python SDK v3 (Latest - OpenTelemetry-based)
- **Latest Version**: June 2025 release
- **Installation**: `pip install langfuse`
- **Approach**: Decorator-based or context managers
- **Features**:
  - Automatic input/output capture
  - Async/sync support
  - Context propagation (OpenTelemetry)
  - Minimal code changes required

#### JavaScript/TypeScript SDK
- **Installation**: `npm install langfuse`
- **Supports**: Browser and Node.js
- **Features**: Same as Python SDK
- **Browser SDK**: Lightweight for frontend instrumentation

### 4.2 LangChain Integration

#### Setup
```python
from langfuse.langchain import CallbackHandler

# Initialize handler
langfuse_handler = CallbackHandler(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    base_url="https://cloud.langfuse.com"
)

# Or use environment variables
# LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL
```

#### Usage Patterns

**LCEL Chains (Recommended):**
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

prompt = ChatPromptTemplate.from_template("What is {topic}?")
model = ChatOpenAI()
chain = prompt | model | StrOutputParser()

# Invoke with callback
result = chain.invoke(
    {"topic": "Langfuse"},
    config={"callbacks": [langfuse_handler]}
)
```

**Constructor Callbacks:**
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4",
    callbacks=[langfuse_handler]  # Used for every call
)

response = llm.invoke("What is Langfuse?")
```

**Metadata & Attributes:**
```python
response = chain.invoke(
    {"person": "Obama"},
    config={
        "callbacks": [langfuse_handler],
        "metadata": {
            "langfuse_user_id": "user-123",
            "langfuse_session_id": "session-abc",
            "langfuse_tags": ["production", "rag-v2"]
        }
    }
)
```

#### Supported Methods
- `invoke()` - Synchronous
- `ainvoke()` - Asynchronous
- `batch()` - Batch processing
- `abatch()` - Async batch
- `stream()` - Token streaming
- `astream()` - Async streaming

### 4.3 OpenTelemetry Integration

#### Overview
- **Basis**: Langfuse Python SDK v3 is built on OpenTelemetry
- **Compatibility**: Works with any OTel-instrumented library
- **Automatic**: Any OTel span automatically becomes Langfuse observation
- **Ecosystem**: Integrates with 50+ OTel instrumentation libraries

#### Example: Automatic Anthropic Tracing
```python
from anthropic import Anthropic
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
from langfuse import get_client

# Enable automatic instrumentation
AnthropicInstrumentor().instrument()

# Langfuse client auto-captures all Anthropic calls
langfuse = get_client()

client = Anthropic()
message = client.messages.create(
    model="claude-3-sonnet",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
# Automatically traced in Langfuse
```

#### Compatible Libraries
- **OpenLLMetry** - Generic LLM instrumentation
- **OpenLIT** - Open source observability
- **Anthropic SDK** - Automatic via instrumentation
- **Custom OTel**: Any library with OTel instrumentation

### 4.4 Other Framework Integrations
- **LlamaIndex**: Native integration
- **LiteLLM**: Proxy integration
- **DSPy**: Direct integration
- **LangGraph**: Via LangChain callback
- **Amazon Bedrock**: AWS integration
- **OpenAI SDK**: Direct or wrapper integration
- **Azure OpenAI**: Native integration
- **Custom Frameworks**: OpenTelemetry interface

---

## 5. ADVANCED FEATURES

### 5.1 Evaluations and Scoring

#### Evaluation Methods

**1. LLM-as-a-Judge**
- Uses another LLM to evaluate outputs
- Configurable rubrics and scoring prompts
- Chain-of-thought reasoning captured
- Cost-effective at scale
- More nuanced than metrics

**2. Custom Scores**
- Via Python/JavaScript SDKs
- Via REST API
- Backend evaluation pipeline
- User feedback collection
- Guardrail checks

**3. Human Annotations**
- UI-based scoring interface
- Batch annotation workflows
- Quality assurance
- Training data creation

#### Score Types
- **Numeric**: 0-1, 1-5, 1-10 scales
- **Categorical**: good/bad, happy/neutral/sad
- **Boolean**: pass/fail, approved/rejected

#### Score Analytics
Built-in metrics for evaluation validation:
- Pearson/Spearman correlation (compare evaluators)
- MAE, RMSE (error metrics)
- F1 Score (classification)
- Overall Agreement

### 5.2 Datasets and Experimentation

#### Dataset Structure
- **Dataset**: Collection of test items
- **Item**: Input, expected output, metadata
- **Run**: Execution of application against dataset
- **Comparison**: Side-by-side run comparison

#### Use Cases
- **Benchmarking**: Create standard test sets
- **Regression Detection**: Catch quality drops
- **A/B Testing**: Compare prompts/models
- **Edge Case Management**: Add new cases from production

#### Workflow
```
1. Create Dataset
   ├─ Add Items (inputs + expected outputs)
   ├─ Import from CSV
   └─ Label items

2. Run Experiment
   └─ Execute app against each item
   
3. Evaluate Results
   ├─ Apply LLM-as-Judge
   ├─ Compare across runs
   └─ View metrics
```

### 5.3 Prompt Management and Versioning

#### Core Features
- **Version Control**: Auto-versioned prompt changes
- **Labels**: Production, staging, experiment tags
- **Caching**: Client-side 60s TTL, server Redis cache
- **Protected Labels**: Admin-controlled production labels

#### Workflow
```python
# Fetch prompt (auto-cached)
prompt = langfuse.get_prompt(
    name="summarizer",
    label="production"  # or version=5
)

# Use the prompt template
formatted = prompt.compile(
    text=long_text,
    format_hint="markdown"
)

# Send to LLM
response = client.messages.create(
    model="claude-3-sonnet",
    messages=[{"role": "user", "content": formatted}]
)
```

#### Caching Strategy
- **Default TTL**: 60 seconds
- **Customizable**: Set per call
- **Fallback**: Stale cache returned if fetch fails
- **Async Refresh**: Background update doesn't block

---

## 6. SECURITY, COMPLIANCE, AND OPERATIONS

### 6.1 API Authentication

#### Basic Auth
- **Method**: HTTP Basic Authentication
- **Headers**: `Authorization: Basic base64(public_key:secret_key)`
- **Location**: Project Settings → API Keys

#### API Key Management
- **Public Key**: Identifies project
- **Secret Key**: Authentication credential
- **Scopes**: Project-level (can add org-level)
- **Rotation**: Create new keys, remove old ones
- **Security**: Treat secret key like password

```python
# SDK authentication
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    host="https://cloud.langfuse.com"
)
```

### 6.2 Data Security and Privacy

#### Encryption
- **In Transit**: TLS 1.2+ for all connections
- **At Rest**: AES-256 encryption in database
- **Keys**: Customer-managed in self-hosted

#### Data Retention
- **Default**: Indefinite (until account closed)
- **Configurable**: Per-project retention policies
- **Minimum**: 3 days
- **Purge**: Automatic nightly purge of expired data
- **Deletion**: On-demand via UI or API

#### GDPR Compliance
- **Right to Access**: Export user data
- **Right to Erasure**: Delete traces, projects, accounts
- **Right to Portability**: Export in standard formats
- **Data Minimization**: Collect only necessary data
- **DPA**: Data Processing Agreement available
- **Contact**: privacy@langfuse.com

#### Privacy Controls
- **Data Masking**: Enterprise feature to mask PII
- **IP Anonymization**: Optional
- **No Model Training**: User data never used to train models
- **Compliance Certifications**:
  - SOC2 Type 2
  - ISO 27001
  - Annual penetration tests

### 6.3 Self-Hosted Compliance

#### Database Encryption
- PostgreSQL: Enable at-rest encryption (AWS, Azure, GCP support)
- ClickHouse: Encryption at-rest supported
- Both: Network encryption required (TLS)

#### Network Security
- **VPC Isolation**: Run in private subnets
- **Security Groups**: Restrict access to databases
- **Secrets Management**: Use vault for credentials
- **IP Whitelisting**: Restrict API access

#### Backup & Recovery
- **PostgreSQL**: Regular snapshots (1x daily minimum)
- **ClickHouse**: Point-in-time recovery configured
- **Storage**: S3/bucket replication
- **RPO**: Depends on backup frequency
- **RTO**: Practice recovery procedures

### 6.4 Monitoring and Observability

#### Health Endpoints
```
GET /health - Basic health check
GET /ready - Readiness probe (for K8s)
```

#### Metrics (StatsD)
- `langfuse.queue.ingestion.length` - Queue depth
- `langfuse.trace.processing.duration` - Processing latency
- `langfuse.db.connection.count` - Active connections
- `langfuse.cache.hit_rate` - Cache efficiency

#### Logging
- Application logs: JSON structured format
- Database logs: Query performance and errors
- Queue logs: Processing and retries

### 6.5 Scaling and Performance Optimization

#### Worker Scaling
- **Metric**: Monitor CPU usage (target <50%)
- **Approach**: Scale workers by CPU load
- **Async**: All processing asynchronous
- **Queue**: Redis-backed with configurable concurrency

#### Database Optimization
- **ClickHouse**: Scale vertically (add memory)
- **PostgreSQL**: Connection pooling, indexes
- **Redis**: Monitor key evictions
- **S3**: Enable versioning and lifecycle policies

#### Common Bottlenecks and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| 502/504 errors | Keep-alive timeout | Increase `KEEP_ALIVE_TIMEOUT` |
| High memory usage | Node.js heap | Increase `NODE_OPTIONS --max-old-space-size` |
| Slow queries | Large traces | Add data retention policy |
| Queue backlog | Worker undersized | Add worker replicas/increase concurrency |
| ClickHouse slow | Undersized instance | Scale vertically (add RAM) |

#### Queue Sharding (Advanced)
- **When**: If Redis CPU > 50%
- **How**: Configure `LANGFUSE_INGESTION_QUEUE_SHARDS`
- **Warning**: Don't reduce shards after setting
- **Impact**: Must scale `CONCURRENCY` settings proportionally

---

## 7. DATA FLOW EXAMPLES

### 7.1 Basic LLM Application Trace

```python
from langfuse import observe

@observe()
def process_user_request(user_query: str):
    # Create a trace automatically
    # Capture input/output
    
    retrieval_results = retrieve_context(user_query)
    
    response = generate_response(
        query=user_query,
        context=retrieval_results
    )
    
    return response

@observe()
def retrieve_context(query: str):
    # Nested span created automatically
    results = vector_store.search(query, top_k=5)
    return results

@observe()
def generate_response(query: str, context: list):
    # Another nested span
    prompt = f"Question: {query}\nContext: {context}"
    response = client.messages.create(
        model="claude-3-sonnet",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

# Usage
result = process_user_request("What is Langfuse?")
# Trace captured with all spans!
```

**Resulting Trace Structure:**
```
Trace: process_user_request
├── Input: "What is Langfuse?"
├── Span: retrieve_context
│   ├── Input: "What is Langfuse?"
│   ├── Tool call: vector_store.search
│   └── Output: [results...]
├── Span: generate_response
│   ├── Input: query + context
│   ├── Generation: ChatOpenAI call
│   │   ├── Model: claude-3-sonnet
│   │   ├── Prompt: [formatted prompt]
│   │   ├── Completion: [response text]
│   │   ├── Tokens: {input: 150, output: 75}
│   │   └── Cost: $0.00075
│   └── Output: [final response]
└── Output: [final response]
```

### 7.2 LangChain RAG Application Trace

```python
from langfuse.langchain import CallbackHandler
from langchain_openai import ChatOpenAI
from langchain.retrievers import VectorStoreRetriever
from langchain.chains import RetrievalQA

# Setup Langfuse
handler = CallbackHandler()

# Build chain
llm = ChatOpenAI(model="gpt-4")
retriever = VectorStoreRetriever(vectorstore=my_vectorstore)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)

# Execute with callback
result = qa_chain.invoke(
    {"query": "Tell me about Langfuse"},
    config={
        "callbacks": [handler],
        "metadata": {
            "langfuse_user_id": "user-123",
            "langfuse_session_id": "session-456",
            "langfuse_tags": ["production"]
        }
    }
)

# Automatically captures:
# - Retriever calls and documents
# - LLM calls with token counts
# - Chain execution flow
# - All nested operations
```

### 7.3 Multi-Turn Conversation Trace

```python
from langfuse import observe, propagate_attributes

SESSION_ID = "conv-user-123"

@observe()
def chat_turn(user_message: str, turn_num: int):
    with propagate_attributes(
        session_id=SESSION_ID,
        user_id="user-123",
        metadata={"turn": turn_num}
    ):
        # All operations inherit session/user context
        response = generate_response(user_message)
        return response

# Multiple calls create one session
chat_turn("Hello", turn_num=1)  # Trace 1, Session A
chat_turn("Tell me more", turn_num=2)  # Trace 2, Session A
chat_turn("Thanks", turn_num=3)  # Trace 3, Session A

# Session view shows all 3 traces grouped together
# "Session replay" shows conversation flow
```

---

## 8. PRICING AND COST MODEL

### 8.1 Cloud Pricing

**Billing Unit**: Traces + Observations + Scores

- **Example**: 1,000 traces with 5,000 observations + 500 scores = 6,500 units
- **Free Tier**: Limited monthly usage
- **Paid Tiers**: Stacked pricing (cheaper at scale)
- **Estimate**: 1M units/month ~ $100-200

### 8.2 Self-Hosted Costs

**Infrastructure Costs:**
- PostgreSQL: Managed $20-50/month or self-hosted
- ClickHouse: Managed $100-500/month or self-hosted
- Redis: Managed $10-30/month or self-hosted
- S3/Blob: Pay-per-GB (typically $50-200/month)
- Compute: Kubernetes or VM costs
- Total: $200-1000+/month depending on scale

**Considerations:**
- Software: Open source (free license)
- Support: Enterprise support available
- Dev time: Operational overhead

---

## 9. ARCHITECTURE PATTERNS AND BEST PRACTICES

### 9.1 SDK Integration Patterns

#### Pattern 1: Decorator-based (Simplest)
```python
from langfuse import observe

@observe()
def my_function(arg1, arg2):
    return process(arg1, arg2)
```
**Pros**: Minimal code, automatic capture
**Cons**: Limited customization

#### Pattern 2: Context Manager
```python
from langfuse import get_client

langfuse = get_client()

with langfuse.start_as_current_span(name="operation") as span:
    result = do_work()
    span.update(output=result)
```
**Pros**: Fine-grained control
**Cons**: More boilerplate

#### Pattern 3: Manual SDK Calls (Low-level)
```python
langfuse.trace(
    name="custom-trace",
    input={"query": "..."},
    output={"result": "..."},
    user_id="user-123"
)
```
**Pros**: Maximum control
**Cons**: Most boilerplate

### 9.2 Data Organization Best Practices

1. **Use consistent tags**: Standardize on versions, environments, techniques
2. **Attach metadata early**: Propagate once, inherit down
3. **Set user_id and session_id**: Enable cross-trace analysis
4. **Name observations clearly**: Use action verbs ("retrieve", "generate", "score")
5. **Capture business context**: Include feature flags, user segments, A/B test variants

### 9.3 Cost Optimization

1. **Filter at source**: Don't trace non-critical operations
2. **Sample in production**: Trace 1% of requests, 100% in dev
3. **Use retention policies**: Purge old traces automatically
4. **Compress payloads**: Store minimal necessary data
5. **Batch writes**: Use batch APIs for bulk ingestion

---

## 10. TROUBLESHOOTING AND FAQ

### 10.1 Common Issues

**Issue: Data not appearing in Langfuse**
- Check API keys are correct
- Verify environment variables set
- Check network connectivity to Langfuse endpoint
- Look at SDK logs for errors
- Ensure trace has at least ended (not incomplete)

**Issue: High latency in trace ingestion**
- Check worker CPU usage
- Add more worker replicas
- Verify database performance
- Reduce trace verbosity
- Use sampling in production

**Issue: 502/504 errors**
- Increase `KEEP_ALIVE_TIMEOUT`
- Check Load Balancer idle timeout
- Add more web replicas
- Monitor database connections

**Issue: Out of memory (Node.js)**
- Increase `NODE_OPTIONS --max-old-space-size`
- Reduce batch size
- Add more replicas with smaller batches

### 10.2 Version Compatibility

**Current Versions (2025):**
- SDK v3: OpenTelemetry-native (recommended)
- SDK v2: Legacy (still supported)
- Langfuse >= 3.63.0: Required for SDK v3

**Deprecation:**
- SDK v2: Sunset in 2025
- Migrate via compatibility guides

### 10.3 Getting Help

- **Documentation**: https://langfuse.com/docs
- **Community**: GitHub Discussions
- **Issues**: GitHub Issues for bugs
- **Email**: support@langfuse.com
- **Enterprise**: sales@langfuse.com
- **Privacy**: privacy@langfuse.com

---

## APPENDIX: KEY RESOURCES

### Official Links
- **Homepage**: https://langfuse.com
- **Docs**: https://langfuse.com/docs
- **GitHub**: https://github.com/langfuse/langfuse
- **Cloud**: https://cloud.langfuse.com

### SDKs and Clients
- **Python SDK**: https://github.com/langfuse/langfuse-python
- **JS/TS SDK**: https://github.com/langfuse/langfuse-js
- **Docker**: https://hub.docker.com/r/langfuse/langfuse
- **Helm Charts**: https://github.com/langfuse/langfuse-k8s

### Integration Guides
- **LangChain**: https://langfuse.com/docs/integrations/langchain
- **LlamaIndex**: https://langfuse.com/docs/integrations/llamaindex
- **LiteLLM**: https://langfuse.com/docs/integrations/litellm
- **OpenTelemetry**: https://langfuse.com/docs/integrations/otel

### Deployment Guides
- **Self-hosting**: https://langfuse.com/self-hosting
- **Docker Compose**: https://langfuse.com/self-hosting/deployment/docker-compose
- **Kubernetes**: https://langfuse.com/self-hosting/deployment/kubernetes-helm
- **AWS**: https://langfuse.com/self-hosting/deployment/aws

### Learning Resources
- **Blog**: https://langfuse.com/blog
- **Cookbook**: https://langfuse.com/guides/cookbook
- **YouTube**: Langfuse channel (tutorials and demos)
- **Community**: GitHub Discussions for questions

---

## SUMMARY TABLE: Feature Matrix

| Feature | Cloud | Self-Hosted | Notes |
|---------|-------|-------------|-------|
| Tracing | ✓ | ✓ | Core feature |
| Evaluations | ✓ | ✓ (v3.63+) | LLM-as-Judge, custom scores |
| Prompt Management | ✓ | ✓ | Versioning, caching |
| Datasets | ✓ | ✓ | Experimentation |
| Multi-region | US, EU | On-prem only | Cloud has US/EU |
| SSO/SAML | ✓ | Enterprise | Self-hosted limited |
| Data Retention | Configurable | Configurable | Automatic purge |
| GDPR Compliance | ✓ | Yes | Privacy controls |
| HA/Failover | Built-in | Kubernetes | Cloud managed |
| Cost | Per-unit | Infrastructure | Depends on volume |

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Coverage**: Langfuse v3.63+


---

# Evaluation & Prompt Management

# Comprehensive Research: Langfuse Evaluation and Prompt Management Features

## Table of Contents
1. [Evaluation and Scoring](#evaluation-and-scoring)
2. [Prompt Management](#prompt-management)
3. [Analytics and Dashboards](#analytics-and-dashboards)
4. [Code Examples](#code-examples)
5. [Best Practices](#best-practices)

---

## EVALUATION AND SCORING

### Overview
Langfuse provides three primary evaluation approaches:
- **LLM-as-a-Judge**: Automatic scoring using language models
- **Human Annotations**: Manual evaluation by team members
- **Custom Scoring**: Flexible API/SDK-based scoring for specialized metrics

### 1. Score Types and Data Model

Langfuse supports three flexible score data types:

#### Numeric Scores
- Float values for continuous measurements
- Can have min/max constraints defined in ScoreConfig
- Examples: accuracy ratings (0-1), quality scores (1-10)

#### Categorical Scores
- String values for classification
- Must match predefined categories in ScoreConfig
- Examples: "correct", "partially_correct", "incorrect"

#### Boolean Scores
- Binary assessment (0 or 1)
- Examples: pass/fail, valid/invalid

### 2. Score Configuration & Standardization

Score Configs enforce consistent evaluation schemas across your team:

```python
# Creating a score config via UI ensures standardization
# Navigate to: Project Settings > Scores / Evaluation

# Example configurations:
# - Numeric: min=0, max=1, name="accuracy"
# - Categorical: categories=["good", "fair", "poor"], name="quality"
# - Boolean: true/false for pass/fail scenarios

# When ingesting scores, reference the configId:
langfuse.create_score(
    name="accuracy",
    value=0.95,
    trace_id="trace_123",
    config_id="config_score_123",  # Validates against config schema
    data_type="NUMERIC"
)
```

### 3. LLM-as-a-Judge Evaluation

#### How It Works
An LLM evaluates outputs by:
1. Receiving a trace or dataset entry
2. Assessing quality based on a rubric
3. Scoring and providing chain-of-thought reasoning

#### Key Benefits
- **Scalability**: Score thousands of outputs quickly and cost-effectively
- **Nuance**: Captures complexity (helpfulness, safety, coherence) better than metrics
- **Consistency**: Fixed rubrics enable repeatable scoring

#### Built-in Evaluation Templates
Langfuse provides pre-built templates for:
- Hallucination detection
- Helpfulness assessment
- Relevance scoring
- Toxicity detection
- Correctness evaluation
- Context relevance
- Context correctness
- Conciseness measurement

#### Supported LLMs for Evaluation
Works with any LLM supporting tool/function calling:
- OpenAI
- Azure OpenAI
- Anthropic
- AWS Bedrock
- Any LLM via LiteLLM gateway

#### Implementation Example
```python
# Langfuse handles LLM-as-judge evaluation setup in UI
# Select your evaluator, configure variables, apply to traces/datasets
# Each evaluation creates a full trace for complete visibility

# Access results via API
evaluations = langfuse.api.scores.get_many()
for score in evaluations:
    print(f"Evaluation: {score.name}")
    print(f"Score: {score.value}")
    print(f"Comment: {score.comment}")  # Chain-of-thought reasoning
```

### 4. Human Annotation Workflows

#### Single Item Annotation
Annotate individual traces, sessions, or observations directly from detail views.

#### Annotation Queues for Scale
For large-scale projects:
1. Create named queues with specific score dimensions
2. Assign queue access to team members
3. Process items sequentially with immediate feedback
4. Track progress via summary metrics

#### Team Collaboration Features
```python
# Setup in UI:
# 1. Navigate to Human Annotation
# 2. Click "New queue"
# 3. Select Score Configs for standardized scoring
# 4. Assign team members to queue
# 5. Add traces/sessions to annotate

# Example workflow:
# - Quality Assurance Queue: score "relevance", "correctness"
# - Safety Review Queue: score "toxic_content", "safety_issues"
# - UX Feedback Queue: score "clarity", "helpfulness"
```

#### Benchmarking
Establish human baseline scores to:
- Compare and evaluate other metrics
- Provide clear performance reference
- Enhance objectivity of evaluations

### 5. Custom Scoring via SDK/API

#### Use Cases
1. **User Feedback Collection**: Capture in-app user feedback via Browser SDK
2. **External Evaluation Pipelines**: Continuously monitor quality by fetching traces and running evaluations
3. **Guardrails & Security**: Validate output format, keywords, or length
4. **Runtime Evaluations**: Track if SQL code executed successfully, if JSON is valid
5. **Custom Metrics**: Any specialized evaluation logic

#### Python SDK Implementation
```python
from langfuse import get_client

langfuse = get_client()

# Method 1: Score a specific observation
with langfuse.start_as_current_observation(as_type="generation", name="summary") as gen:
    gen.update(output="summary text...")
    
    # Score the generation
    gen.score(name="conciseness", value=0.8, data_type="NUMERIC")
    
    # Score the entire trace
    gen.score_trace(name="user_feedback", value="positive", data_type="CATEGORICAL")

# Method 2: Score context-aware
with langfuse.start_as_current_observation(as_type="span", name="complex_task") as span:
    # ... task execution ...
    langfuse.score_current_span(name="quality", value=True, data_type="BOOLEAN")
    if task_successful:
        langfuse.score_current_trace(name="success", value=1.0, data_type="NUMERIC")

# Method 3: Low-level create score (when IDs are known)
langfuse.create_score(
    name="fact_check",
    value=0.95,
    trace_id="trace_abc123",
    observation_id="obs_def456",  # Optional
    session_id="session_xyz",      # Optional
    data_type="NUMERIC",
    comment="95% of claims verified"
)

# Update existing scores (by providing score_id)
langfuse.create_score(
    name="fact_check",
    value=0.98,
    score_id="score_existing",  # Updates if exists
    trace_id="trace_abc123",
    data_type="NUMERIC"
)
```

#### JavaScript/TypeScript Implementation
```typescript
import { LangfuseClient } from "@langfuse/client";

const langfuse = new LangfuseClient();

// Fetch scores
const scores = await langfuse.api.scoreV2.get();

// Create score with validation
await langfuse.api.scoreV2.create({
    name: "accuracy",
    value: 0.92,
    traceId: "trace_123",
    dataType: "NUMERIC",
    configId: "config_accuracy",  // Validates against schema
    comment: "Output matches expected format"
});

// Update existing score
await langfuse.api.scoreV2.create({
    id: "score_existing",  // Updates existing score
    name: "accuracy",
    value: 0.95,
    traceId: "trace_123"
});
```

### 6. Datasets and Experiments

#### Dataset Management
Datasets are collections of inputs and expected outputs for systematic testing.

```python
from langfuse import get_client

langfuse = get_client()

# Create dataset
dataset = langfuse.create_dataset(name="customer_support_qa")

# Add items
dataset.items.add(
    input={"query": "How do I reset my password?"},
    expected_output="Password reset link sent to email"
)

dataset.items.add(
    input={"query": "What are your hours?"},
    expected_output="Open 9 AM - 5 PM EST, Monday-Friday"
)

# Fetch for use in experiments
my_dataset = langfuse.get_dataset("customer_support_qa")
```

#### JavaScript/TypeScript
```typescript
// Create dataset
const dataset = await langfuse.api.datasets.create({
    name: "customer_support_qa"
});

// Add items
await langfuse.api.datasetItems.create({
    datasetId: dataset.id,
    input: { query: "How do I reset my password?" },
    expectedOutput: "Password reset link sent to email"
});
```

#### Running Experiments with Evaluators

```python
from langfuse import Evaluation, get_client
from langfuse.openai import OpenAI

# Define evaluator function
def accuracy_evaluator(*, input, output, expected_output, **kwargs):
    """Evaluate if output matches expected output"""
    if expected_output and expected_output.lower() in output.lower():
        return Evaluation(
            name="accuracy",
            value=1.0,
            comment="Output contains expected content"
        )
    return Evaluation(
        name="accuracy",
        value=0.0,
        comment="Output missing expected content"
    )

def length_evaluator(*, input, output, **kwargs):
    """Evaluate response length"""
    return Evaluation(
        name="response_length",
        value=len(output),
        comment=f"{len(output)} characters"
    )

# Define task (what to run)
def my_task(*, item, **kwargs):
    """Your LLM application logic"""
    question = item["input"]["query"]
    response = OpenAI().chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content

# Run experiment
langfuse = get_client()
result = langfuse.run_experiment(
    name="Customer Support QA - GPT-4",
    data=[
        {"input": {"query": "How do I reset password?"}, "expected_output": "Reset link"},
        {"input": {"query": "What are hours?"}, "expected_output": "9 AM - 5 PM EST"}
    ],
    task=my_task,
    evaluators=[accuracy_evaluator, length_evaluator],
    max_concurrency=5
)

# Print results
print(result.format())
```

#### Run-Level Evaluators (Aggregate Metrics)
```python
def average_accuracy(*, item_results, **kwargs):
    """Calculate average accuracy across all items"""
    accuracies = [
        eval.value for result in item_results
        for eval in result.evaluations
        if eval.name == "accuracy"
    ]
    
    if not accuracies:
        return Evaluation(name="avg_accuracy", value=None)
    
    avg = sum(accuracies) / len(accuracies)
    return Evaluation(
        name="avg_accuracy",
        value=avg,
        comment=f"Average: {avg:.2%}"
    )

result = langfuse.run_experiment(
    name="Comprehensive Analysis",
    data=test_data,
    task=my_task,
    evaluators=[accuracy_evaluator],
    run_evaluators=[average_accuracy]  # Aggregate metric
)
```

### 7. External Evaluation Pipelines

For continuous quality monitoring:

```python
from langfuse import get_client
from deepeval import evaluate  # Example: using Deepeval

langfuse = get_client()

# Step 1: Fetch traces from Langfuse
traces = langfuse.api.traces.list()

# Step 2: Run evaluations
for trace in traces:
    # Get the LLM output
    output = trace.output
    
    # Run custom evaluation (e.g., with Deepeval)
    score = evaluate(output)
    
    # Step 3: Send results back to Langfuse
    langfuse.create_score(
        name="deepeval_score",
        value=score,
        trace_id=trace.id,
        data_type="NUMERIC"
    )
```

### 8. User Feedback Collection

#### Explicit Feedback
Direct prompts for user ratings or comments:

```python
# Browser SDK for frontend feedback collection
# Install: npm install @langfuse/web

import { Langfuse } from "@langfuse/web";

const langfuse = new Langfuse({
    publicKey: "pk-lf-...",
    baseUrl: "https://cloud.langfuse.com"
});

// Collect feedback from user
function rateResponse(traceId, rating) {
    langfuse.score({
        name: "user_rating",
        value: rating,  // 1-5 stars
        traceId: traceId,
        dataType: "NUMERIC"
    });
}

// Or categorical feedback
function markResponse(traceId, feedback) {
    langfuse.score({
        name: "user_feedback",
        value: feedback,  // "helpful", "not_helpful", "spam"
        traceId: traceId,
        dataType: "CATEGORICAL"
    });
}
```

#### Implicit Feedback
Inferred from user behavior (clicks, time spent, etc.):

```python
# Track user interactions as implicit feedback
langfuse.create_score(
    name="user_accepted",
    value=1.0 if user_accepted_output else 0.0,
    trace_id=trace_id,
    data_type="BOOLEAN",
    comment="User accepted the generated response"
)

# Track if user re-queried (indicates dissatisfaction)
if user_requeried:
    langfuse.create_score(
        name="user_requery",
        value=1.0,
        trace_id=trace_id,
        data_type="BOOLEAN",
        comment="User submitted a follow-up query"
    )
```

---

## PROMPT MANAGEMENT

### 1. Overview and Core Concepts

Langfuse Prompt Management enables:
- Version control and rollback
- Non-code prompt updates
- A/B testing in production
- Prompt deployment workflows
- Collaboration with non-technical team members

### 2. Prompt Types and Templates

#### Text Prompts
Single string with optional variables:
```python
from langfuse import get_client

langfuse = get_client()

# Create text prompt with variables
langfuse.create_prompt(
    name="summarizer",
    type="text",
    prompt="Summarize the following text in {{language}}:\n\n{{text}}",
    config={
        "model": "gpt-4o",
        "temperature": 0.3
    },
    labels=["production"]
)

# Fetch and compile
prompt = langfuse.get_prompt("summarizer")
compiled = prompt.compile(language="French", text="Long document here...")
```

#### Chat Prompts
Array of messages for conversational models:
```python
langfuse.create_prompt(
    name="customer_support",
    type="chat",
    prompt=[
        {
            "role": "system",
            "content": "You are a helpful customer support assistant. Always be polite and helpful."
        },
        {
            "role": "user",
            "content": "{{customer_question}}"
        }
    ],
    config={
        "model": "gpt-4-turbo",
        "temperature": 0.7,
        "max_tokens": 500
    },
    labels=["production"]
)
```

#### JavaScript/TypeScript
```typescript
// Create text prompt
await langfuse.prompt.create({
    name: "email_writer",
    type: "text",
    prompt: "Write a professional email about {{topic}} in {{tone}} tone",
    labels: ["production"],
    config: {
        model: "gpt-4o",
        temperature: 0.5
    }
});

// Create chat prompt
await langfuse.prompt.create({
    name: "chatbot",
    type: "chat",
    prompt: [
        { role: "system", content: "You are helpful chatbot" },
        { role: "user", content: "{{user_message}}" }
    ],
    labels: ["production"]
});
```

### 3. Prompt Versioning and Labeling

#### Automatic Versioning
Each prompt edit creates a new version with auto-incrementing version number.

#### Labels for Deployment
Special labels for environment and experiment management:

```python
# Fetch production version (default)
prompt = langfuse.get_prompt("customer_support")

# Fetch specific version
prompt_v1 = langfuse.get_prompt("customer_support", version=1)

# Fetch staging version
prompt_staging = langfuse.get_prompt("customer_support", label="staging")

# Fetch for A/B test
prompt_a = langfuse.get_prompt("customer_support", label="prod-a")
prompt_b = langfuse.get_prompt("customer_support", label="prod-b")
```

#### Built-in Labels
- **`production`**: Default version returned by SDKs
- **`latest`**: Most recently created version
- **Custom labels**: `staging`, `dev`, `tenant-1`, `prod-a`, `prod-b`, etc.

#### Label Management
```python
# In UI: Update > Versions tab
# Select version and assign/remove labels
# E.g., assign version 5 to "production"

# Protected Labels (v2.0+)
# Project admins can protect labels like "production"
# Prevents viewer/member roles from modifying
```

### 4. Prompt Deployment Workflow

```
Development → Testing → Staging → Production

1. Create new version in "dev" environment
2. Test with "staging" label
3. Validate performance on dataset
4. Deploy to "production" label
5. Monitor metrics
6. Rollback if needed (reassign production label)
```

### 5. Integration with LangChain

#### Python Example
```python
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Setup
langfuse = get_client()
langfuse_callback = CallbackHandler()

# Create prompt in Langfuse
langfuse.create_prompt(
    name="event-planner",
    prompt="Plan an event titled {{Event Name}}. {{Event Description}} "
           "will be held in {{Location}} on {{Date}}. "
           "Consider: audience, budget, venue, catering, entertainment. "
           "Provide detailed plan including vendors.",
    config={
        "model": "gpt-4o",
        "temperature": 0
    },
    labels=["production"]
)

# Fetch and convert to LangChain format
langfuse_prompt = langfuse.get_prompt("event-planner")

# Note: Langfuse uses {{variable}} but LangChain uses {variable}
langchain_prompt = ChatPromptTemplate.from_template(
    langfuse_prompt.get_langchain_prompt(),  # Converts {{ }} to { }
    metadata={"langfuse_prompt": langfuse_prompt}
)

# Build chain
model = langfuse_prompt.config["model"]
temp = langfuse_prompt.config["temperature"]
llm = ChatOpenAI(model=model, temperature=temp)
chain = langchain_prompt | llm

# Execute with tracing
response = chain.invoke(
    {
        "Event Name": "Wedding",
        "Event Description": "Celebrating union of Julia and Alex",
        "Location": "Central Park, NYC",
        "Date": "June 5, 2024"
    },
    config={"callbacks": [langfuse_callback]}
)
```

#### JavaScript/TypeScript Example
```typescript
import { LangfuseClient } from "@langfuse/client";
import { PromptTemplate } from "@langchain/core/prompts";

const langfuse = new LangfuseClient();

// Create prompt
await langfuse.prompt.create({
    name: "jokes",
    type: "text",
    prompt: "Tell me a joke about {{topic}}",
    labels: ["production"],
    config: {
        model: "gpt-4o",
        temperature: 0.7
    }
});

// Fetch and use
const prompt = await langfuse.prompt.get({
    name: "jokes",
    label: "production"
});

// Convert to LangChain format
const promptTemplate = PromptTemplate.fromTemplate(
    prompt.getLangchainPrompt()
).withConfig({
    metadata: { langfusePrompt: prompt }
});
```

### 6. A/B Testing Prompts in Production

```python
import random
from langfuse import get_client

langfuse = get_client()

def get_response(user_query):
    # Randomly select prompt version
    variant = random.choice(["prod-a", "prod-b"])
    
    # Fetch selected variant
    prompt = langfuse.get_prompt("customer_support", label=variant)
    
    # Use with LLM
    response = openai.chat.completions.create(
        model=prompt.config["model"],
        temperature=prompt.config["temperature"],
        messages=[
            {"role": "user", "content": prompt.compile(query=user_query)}
        ]
    )
    
    # Langfuse automatically tracks which prompt version was used
    # via the metadata linking in your tracing setup
    return response.choices[0].message.content
```

Performance metrics (latency, cost, quality) are automatically tracked per label.

### 7. Configuration Storage

Store model parameters alongside prompts:

```python
langfuse.create_prompt(
    name="analyzer",
    prompt="Analyze {{text}}",
    config={
        "model": "gpt-4o",
        "temperature": 0.2,
        "max_tokens": 1000,
        "top_p": 0.95,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "extract_entities",
                    "description": "Extract entities from text"
                }
            }
        ]
    }
)

# Fetch and apply config
prompt = langfuse.get_prompt("analyzer")
llm_config = prompt.config
```

---

## ANALYTICS AND DASHBOARDS

### 1. Custom Dashboards

#### Creating Dashboards
```
UI: Dashboards > New Dashboard > Configure Query
- Select view (traces, observations, scores)
- Choose dimensions (model, user, feature, prompt_version)
- Select metrics (count, latency, cost, etc.)
- Apply filters and time granularity
```

#### Query Engine Features
- Multi-level aggregations across traces, observations, sessions, scores
- Complex filtering by metadata, timestamps, user properties
- Time granularity: hour, day, week, month

#### Visualization Types
- **Line charts**: Latency trends, cost over time
- **Bar charts**: Model comparison, user metrics
- **Time series**: Real-time monitoring
- **Pie charts**: Cost/usage distribution

#### Example Queries
```
Query 1: Average Latency by Model
View: observations
Dimensions: model
Metrics: avg(latency)
Filter: environment = "production"

Query 2: Cost Breakdown by User
View: observations
Dimensions: userId
Metrics: sum(cost)
Time: daily
Filter: tags.feature = "chat"

Query 3: Quality Score Trends
View: scores-numeric
Dimensions: prompt_version
Metrics: avg(value)
Filter: name = "user_rating"
```

### 2. Cost Tracking and Token Usage

#### Cost Tracking Methods

**Method 1: Automatic Calculation**
For supported models (OpenAI, Anthropic, Google):
```python
# When using integrations, cost is calculated automatically
response = openai.chat.completions.create(model="gpt-4", ...)
# Langfuse extracts token usage and calculates cost

# Token usage available via API
traces = langfuse.api.traces.list()
for trace in traces:
    for obs in trace.observations:
        if obs.model:
            print(f"Model: {obs.model}")
            print(f"Input tokens: {obs.usage.input_tokens}")
            print(f"Output tokens: {obs.usage.output_tokens}")
            print(f"Cost: ${obs.cost_usd}")
```

**Method 2: Custom Model Definitions**
```
UI: Project Settings > Models > + New Model

Configure:
- Model name (e.g., "my-custom-model")
- Tokenizer (regex pattern matching)
- Pricing per token type:
  - input_tokens: $0.001 per token
  - output_tokens: $0.002 per token
  - cached_tokens: $0.0001 per token
```

**Method 3: Manual Cost Ingestion**
```python
langfuse.create_observation(
    type="generation",
    name="llm_call",
    model="custom-model",
    usage={
        "input_tokens": 100,
        "output_tokens": 50,
        "cached_tokens": 10
    },
    cost_usd=0.00123  # Or provide usage and let cost calculate
)
```

#### Usage Types
Standard types:
- `input`, `output` (all models)
- `cached_tokens` (when using cache)
- `audio_tokens`, `image_tokens` (multimodal models)

Custom types:
```python
# Define custom usage types
usage = {
    "reasoning_tokens": 1000,  # For reasoning models
    "multimodal_tokens": 500,
    "api_calls": 5             # Custom metrics
}
```

#### Important: Reasoning Models (o1, etc.)
Cost inference cannot work without explicit token usage:
```python
# Must provide token usage for o1 models
langfuse.create_observation(
    type="generation",
    model="o1",
    usage={
        "input_tokens": 500,
        "output_tokens": 1500,
        "reasoning_tokens": 5000  # Explicitly required
    }
)

# With integrations (LangChain, LiteLLM), tokens collected automatically
```

### 3. Metrics API

#### Endpoint
`GET /api/public/metrics`

#### Basic Query Structure
```python
import requests

# Example: Daily cost by model
query = {
    "view": "observations",
    "dimensions": ["model"],
    "metrics": ["totalCost", "count"],
    "filters": [
        {
            "name": "timestamp",
            "operator": "gte",
            "value": "2024-01-01"
        }
    ],
    "timeGranularity": "day"
}

response = requests.get(
    "https://cloud.langfuse.com/api/public/metrics",
    json=query,
    headers={
        "Authorization": f"Bearer {API_KEY}"
    }
)

results = response.json()
# Returns aggregated metrics grouped by dimensions
```

#### Supported Views
- `traces`: Count, latency by trace name, user
- `observations`: Latency, token usage, cost by model, user
- `scores-numeric`: Average/percentile scores
- `scores-categorical`: Score counts by category

#### Aggregation Functions
- `count`, `sum`, `avg`, `min`, `max`
- Percentiles: `p50`, `p75`, `p90`, `p95`, `p99`

#### Example Queries

**Query 1: Token usage by model this month**
```json
{
  "view": "observations",
  "dimensions": ["model"],
  "metrics": ["totalTokens", "totalCost"],
  "filters": [{
    "name": "timestamp",
    "operator": "gte",
    "value": "2024-11-01"
  }]
}
```

**Query 2: Cost by user (last 7 days)**
```json
{
  "view": "observations",
  "dimensions": ["userId"],
  "metrics": ["totalCost", "count"],
  "filters": [{
    "name": "timestamp",
    "operator": "gte",
    "value": "2024-11-12"
  }],
  "timeGranularity": "day"
}
```

**Query 3: Latency percentiles by feature**
```json
{
  "view": "observations",
  "dimensions": ["tags.feature"],
  "metrics": ["p50(latency)", "p95(latency)", "p99(latency)"]
}
```

### 4. Daily Metrics API

For retrieving aggregated daily usage and cost metrics:

```python
# Request daily metrics
response = requests.get(
    "https://cloud.langfuse.com/api/public/daily-metrics",
    params={
        "from": "2024-11-01",
        "to": "2024-11-30",
        "groupBy": "userId"
    },
    headers={"Authorization": f"Bearer {API_KEY}"}
)

# Returns:
# {
#   "data": [
#     {
#       "date": "2024-11-01",
#       "userId": "user_123",
#       "usage": {
#         "input_tokens": 10000,
#         "output_tokens": 5000,
#         "requests": 25
#       },
#       "cost": 0.087
#     }
#   ]
# }
```

### 5. Data Relationships and Scoring

#### Trace-Observation Relationships
```
Trace (overall interaction)
├── Observation 1 (e.g., LLM generation)
│   └── Child observations
├── Observation 2 (e.g., database query)
└── Observation 3 (e.g., API call)

Scores can attach to any level:
- Trace-level: Overall session quality
- Observation-level: Specific step evaluation
```

#### Scoring Architecture
```python
# Trace-level score (evaluates entire interaction)
langfuse.create_score(
    name="user_satisfaction",
    value=4.5,
    trace_id="trace_123",
    data_type="NUMERIC"
)

# Observation-level score (evaluates specific step)
langfuse.create_score(
    name="output_quality",
    value=0.95,
    observation_id="obs_456",  # Specific LLM call
    trace_id="trace_123",
    data_type="NUMERIC"
)

# Session-level score (evaluates multiple traces)
langfuse.create_score(
    name="conversation_quality",
    value="excellent",
    session_id="session_789",
    data_type="CATEGORICAL"
)
```

#### Querying Related Data
```python
# Fetch trace with all observations and scores
trace = langfuse.api.traces.get("trace_123")

# Access nested data
for obs in trace.observations:
    print(f"Observation: {obs.name}")
    
    # Scores are linked via reference
    scores = langfuse.api.scores.list(
        observation_id=obs.id
    )
    for score in scores:
        print(f"  Score: {score.name} = {score.value}")
```

---

## CODE EXAMPLES

### Complete Evaluation Workflow Example

```python
from langfuse import Evaluation, get_client
from langfuse.openai import OpenAI
from langfuse.langchain import CallbackHandler

# Setup
langfuse = get_client()
callback_handler = CallbackHandler()

# 1. Create dataset
dataset = langfuse.create_dataset("qa-benchmark")
dataset.items.add(
    input={"question": "What is the capital of France?"},
    expected_output="Paris"
)
dataset.items.add(
    input={"question": "Who wrote Romeo and Juliet?"},
    expected_output="William Shakespeare"
)

# 2. Define evaluators
def accuracy_eval(*, input, output, expected_output, **kwargs):
    match = expected_output.lower() in output.lower()
    return Evaluation(
        name="accuracy",
        value=1.0 if match else 0.0,
        comment="Correct" if match else "Incorrect"
    )

def helpfulness_eval(*, output, **kwargs):
    # Could use LLM for nuanced evaluation
    score = 1.0 if len(output) > 50 else 0.5
    return Evaluation(
        name="helpfulness",
        value=score,
        comment=f"Response: {len(output)} chars"
    )

# 3. Create prompt
langfuse.create_prompt(
    name="qa-answerer",
    prompt="Answer this question: {{question}}",
    config={"model": "gpt-4o", "temperature": 0},
    labels=["production"]
)

# 4. Define task
def qa_task(*, item, **kwargs):
    prompt = langfuse.get_prompt("qa-answerer")
    response = OpenAI().chat.completions.create(
        model=prompt.config["model"],
        messages=[{
            "role": "user",
            "content": prompt.compile(question=item["input"]["question"])
        }]
    )
    return response.choices[0].message.content

# 5. Run experiment
result = langfuse.run_experiment(
    name="QA Model - GPT-4o",
    data=langfuse.get_dataset("qa-benchmark").items,
    task=qa_task,
    evaluators=[accuracy_eval, helpfulness_eval]
)

# 6. View results
print(result.format())

# 7. Query results programmatically
traces = langfuse.api.traces.list(name="QA Model - GPT-4o")
for trace in traces:
    scores = langfuse.api.scores.list(trace_id=trace.id)
    for score in scores:
        print(f"{trace.id}: {score.name} = {score.value}")
```

### Frontend User Feedback Collection

```typescript
// Browser SDK for collecting user feedback

import { Langfuse } from "@langfuse/web";

const langfuse = new Langfuse({
    publicKey: "pk-lf-...",
    baseUrl: "https://cloud.langfuse.com"
});

// Capture current trace ID from your application
const currentTraceId = localStorage.getItem("langfuse_trace_id");

// Rating widget
function createRatingWidget(traceId) {
    const container = document.getElementById("feedback");
    
    for (let i = 1; i <= 5; i++) {
        const button = document.createElement("button");
        button.textContent = "⭐".repeat(i);
        button.onclick = () => {
            // Send feedback to Langfuse
            langfuse.score({
                name: "user_rating",
                value: i,
                traceId: traceId,
                dataType: "NUMERIC"
            });
            
            // Notify user
            container.innerHTML = "Thanks for your feedback!";
        };
        container.appendChild(button);
    }
}

// Thumbs up/down widget
function createThumbsWidget(traceId) {
    const thumbsUp = document.getElementById("thumbs-up");
    const thumbsDown = document.getElementById("thumbs-down");
    
    thumbsUp.onclick = () => {
        langfuse.score({
            name: "user_thumbs",
            value: "thumbs_up",
            traceId: traceId,
            dataType: "CATEGORICAL"
        });
    };
    
    thumbsDown.onclick = () => {
        langfuse.score({
            name: "user_thumbs",
            value: "thumbs_down",
            traceId: traceId,
            dataType: "CATEGORICAL"
        });
    };
}

// Initialize on page load
createRatingWidget(currentTraceId);
createThumbsWidget(currentTraceId);
```

---

## BEST PRACTICES

### 1. Evaluation Strategy

#### Multi-Method Approach
Don't rely on a single evaluation technique:
- Use human annotation for baseline
- Deploy LLM-as-judge for scalability
- Collect user feedback for real-world signal
- Implement custom metrics for domain-specific needs

#### Offline vs Online Evaluation
```
Development:
- Build test dataset (20-50 representative samples)
- Run experiments with multiple evaluators
- Validate changes before production

Production:
- Monitor key quality metrics
- Collect user feedback
- Track performance trends
- Alert on regressions
```

### 2. Cost Optimization

#### Monitor Spending
```python
# Regular cost queries
query = {
    "view": "observations",
    "dimensions": ["model"],
    "metrics": ["totalCost", "count"],
    "timeGranularity": "day"
}

# Set up alerts if costs exceed budget
total_cost = sum(result["totalCost"] for result in daily_results)
if total_cost > daily_budget:
    send_alert(f"Daily cost ${total_cost} exceeds budget")
```

#### Optimize Model Selection
- Use cheaper models for simple tasks
- Reserve expensive models for complex reasoning
- Cache common prompts and responses
- Batch requests when possible

### 3. Prompt Management Best Practices

#### Version Control Discipline
1. Never edit production prompt directly
2. Create new version first
3. Test on "staging" label
4. Validate with dataset experiments
5. Deploy to "production" only after validation

#### Documentation
```python
# Include description in prompt config
langfuse.create_prompt(
    name="classifier",
    prompt="Classify: {{text}}",
    config={
        "model": "gpt-4o",
        "description": "Classify support tickets into categories",
        "changelog": "v2: Added instruction for multi-class output",
        "created": "2024-11-15"
    }
)
```

### 4. Team Collaboration

#### Annotation Queue Setup
```
1. Define score configs (standardize evaluation)
   - Quality: good/fair/poor
   - Relevance: 0-10 scale
   - Correctness: binary

2. Create annotation queues
   - Quality Review Queue
   - Safety Review Queue
   - User Experience Queue

3. Assign team members
4. Track progress and consensus
```

#### Role-Based Access
- **Admin/Owner**: Create configs, protect labels
- **Member**: Annotate, create datasets
- **Viewer**: Read dashboards, view scores

### 5. Monitoring and Alerting

#### Key Metrics to Monitor
- Quality scores (trends, drops)
- Response latency (p50, p95, p99)
- Error rates and failure modes
- Cost per transaction
- Token usage patterns

#### Dashboard Setup
```
Quality Dashboard:
- Average accuracy by model
- User satisfaction trends
- Error rate by feature

Performance Dashboard:
- Latency trends
- Token usage vs cost
- Model comparison

Cost Dashboard:
- Daily spend by model
- Cost per user/feature
- Budget tracking
```

### 6. Handling Edge Cases

#### Reasoning Models
Always provide explicit token counts for o1 models:
```python
langfuse.create_observation(
    model="o1",
    usage={
        "input_tokens": 500,
        "output_tokens": 1500,
        "reasoning_tokens": 10000  # Must explicit
    }
)
```

#### Multi-turn Conversations
```python
# Use sessions to group related traces
trace = langfuse.create_trace(
    name="customer_conversation",
    session_id="conversation_123",
    user_id="user_456"
)

# Score overall conversation, not individual turns
langfuse.create_score(
    name="conversation_quality",
    value=4.5,
    session_id="conversation_123"
)
```

---

## Summary and Key Takeaways

### Evaluation Framework
- **Langfuse Scores**: Flexible objects for any evaluation metric
- **Three Methods**: LLM-as-judge (scalable), Human annotation (accurate), Custom scoring (flexible)
- **Score Configs**: Standardize evaluation across teams
- **Datasets**: Curate test data for systematic evaluation

### Prompt Management
- **Version Control**: Track all changes with automatic versioning
- **Labels**: Deploy to different environments/experiments
- **Non-code Updates**: Modify prompts without redeploying
- **A/B Testing**: Compare prompt versions in production

### Analytics
- **Custom Dashboards**: Build dashboards with flexible queries
- **Cost Tracking**: Monitor spend by model, user, feature
- **Metrics API**: Export data for custom analytics
- **Performance Monitoring**: Track quality, latency, errors

### Recommended Workflow
1. Create datasets with representative inputs
2. Implement multi-method evaluation
3. Version prompts and manage via labels
4. Monitor quality metrics continuously
5. Iterate based on evaluation results
6. Scale successful approaches production-wide


---

# SDK Integrations

# Langfuse: Comprehensive SDK, Integrations, and API Patterns Research

## Table of Contents

1. [Python SDK](#python-sdk)
2. [JavaScript/TypeScript SDK](#javascripttypescript-sdk)
3. [Framework Integrations](#framework-integrations)
4. [API and OpenTelemetry](#api-and-opentelemetry)
5. [No-Code Platform Integrations](#no-code-platform-integrations)
6. [Best Practices](#best-practices)

---

## Python SDK

### Overview

The Langfuse Python SDK v3 is built on OpenTelemetry for robust observability and context propagation. The latest version (v3.10.1+) provides three instrumentation approaches:

1. **Decorator pattern** (`@observe`) - Simplest, automatic nesting
2. **Context managers** - Recommended for chunks of work, explicit control
3. **Manual observations** - Maximum control with explicit span lifecycle management

### Installation

```bash
pip install langfuse
```

### Basic Setup

```python
from langfuse import get_client, observe, propagate_attributes

# Initialize client (uses environment variables by default)
langfuse = get_client()

# Environment variables:
# LANGFUSE_SECRET_KEY="sk-lf-..."
# LANGFUSE_PUBLIC_KEY="pk-lf-..."
# LANGFUSE_BASE_URL="https://cloud.langfuse.com"  # EU region
# or LANGFUSE_BASE_URL="https://us.cloud.langfuse.com"  # US region

# Or explicit initialization:
langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    base_url="https://cloud.langfuse.com"
)
```

### 1. Decorator Pattern (@observe)

The simplest approach for automatic tracing with minimal code changes.

#### Basic Function Tracing

```python
from langfuse import observe, get_client

@observe()
def process_user_query(query: str) -> str:
    """Automatically traced function"""
    result = some_processing(query)
    return result

@observe()
async def async_process(query: str) -> str:
    """Supports async functions"""
    result = await async_operation(query)
    return result

# Functions are automatically traced
result = process_user_query("What is AI?")
```

#### With Custom Names and Attributes

```python
from langfuse import observe

@observe(
    name="custom-span-name",
    as_type="chain"  # Can be: span, generation, retrieval, tool, agent
)
def complex_pipeline(input_data: dict) -> dict:
    # ... implementation ...
    return output

@observe(
    name="llm-generation",
    as_type="generation"
)
def call_llm(prompt: str, model: str = "gpt-4o") -> str:
    # ... LLM call ...
    return response
```

#### Propagating Attributes with Decorator

```python
from langfuse import observe, propagate_attributes

@observe()
def user_workflow(user_id: str, session_id: str, query: str):
    """Propagate user context to all child spans"""
    with propagate_attributes(
        user_id=user_id,
        session_id=session_id,
        tags=["production", "user-request"],
        metadata={"email": "user@example.com", "tier": "premium"},
        version="1.0.0"
    ):
        # All child observations inherit these attributes
        result = process_query(query)
        store_result(result)
    return result

# Usage
user_workflow(
    user_id="user_123",
    session_id="session_abc",
    query="What is machine learning?"
)
```

### 2. Context Managers

Recommended approach for explicit control and automatic nesting of observations.

#### Basic Context Manager Usage

```python
from langfuse import get_client

langfuse = get_client()

def example_with_context_managers():
    # Create a root span
    with langfuse.start_as_current_span(
        name="user-request-pipeline",
        input={"user_query": "Tell me about AI"},
    ) as root_span:
        # This span is now the active observation in the context
        
        # Child observations created within this block are automatically nested
        with langfuse.start_as_current_span(
            name="retrieve-context",
        ) as retrieval_span:
            documents = retrieve_documents("AI")
            retrieval_span.update(output={"doc_count": len(documents)})
        
        # Update root span with final output
        root_span.update(output={"status": "completed"})
```

#### Generation (LLM Call) Observations

```python
from langfuse import get_client
import openai

langfuse = get_client()

def llm_call_with_generation():
    with langfuse.start_as_current_generation(
        name="llm-response",
        model="gpt-4o",
        input={
            "messages": [
                {"role": "user", "content": "What is AI?"}
            ]
        }
    ) as generation:
        # Make LLM call
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "What is AI?"}]
        )
        
        # Update generation with LLM output
        generation.update(
            output=response.choices[0].message.content,
            usage={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens
            }
        )
```

#### Nested Context Managers

```python
from langfuse import get_client

langfuse = get_client()

def complex_retrieval_pipeline():
    with langfuse.start_as_current_span(
        name="rag-pipeline",
        input={"query": "Who won the World Cup in 2022?"}
    ) as pipeline:
        
        # Step 1: Retrieve documents
        with langfuse.start_as_current_span(
            name="vector-search",
            as_type="retrieval"
        ) as retrieval:
            docs = vector_db.search("World Cup 2022")
            retrieval.update(
                output={"document_count": len(docs), "documents": docs}
            )
        
        # Step 2: Call LLM with retrieved context
        with langfuse.start_as_current_generation(
            name="answer-generation",
            model="gpt-4o",
            input={"context": docs, "query": "Who won?"}
        ) as generation:
            answer = llm_generate(docs, "Who won?")
            generation.update(output=answer)
        
        # Final output
        pipeline.update(output={"answer": answer})
```

#### Observation Types

```python
from langfuse import get_client

langfuse = get_client()

# Generic span
with langfuse.start_as_current_observation(
    as_type="span",
    name="processing"
) as span:
    pass

# LLM generation
with langfuse.start_as_current_observation(
    as_type="generation",
    name="llm-call",
    model="gpt-4o"
) as gen:
    pass

# Retrieval operation
with langfuse.start_as_current_observation(
    as_type="retrieval",
    name="vector-search"
) as ret:
    pass

# Tool/Function call
with langfuse.start_as_current_observation(
    as_type="tool",
    name="calculator"
) as tool:
    pass

# Agent workflow
with langfuse.start_as_current_observation(
    as_type="agent",
    name="react-agent"
) as agent:
    pass
```

### 3. Manual Observations

For fine-grained control over observation lifecycle.

```python
from langfuse import get_client

langfuse = get_client()

# Manual span management
span = langfuse.start_span(
    name="manual-processing",
    input={"data": "input_value"}
)

try:
    # Do some work
    result = process_data()
    span.end(output=result)
except Exception as e:
    span.end(error=str(e))

# Manual generation
generation = langfuse.start_generation(
    name="llm-call",
    model="gpt-4o",
    input={"prompt": "Hello"}
)

try:
    response = openai.ChatCompletion.create(...)
    generation.end(output=response.content)
except Exception as e:
    generation.end(error=str(e))
```

### 4. Advanced Features

#### Batch Processing and Flushing

```python
from langfuse import get_client

langfuse = get_client()

# Configuration for batching
langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    flush_at=100,  # Flush after 100 events
    flush_interval=10,  # Flush every 10 seconds
)

# Manual flush
langfuse.flush()

# For short-lived environments (serverless), use shutdown
langfuse.shutdown()  # Blocks until all events are flushed
```

#### Attribute Propagation

```python
from langfuse import observe, propagate_attributes, get_client

# Propagate attributes to all child observations
def workflow_with_propagation(user_id: str, session_id: str):
    with propagate_attributes(
        user_id=user_id,
        session_id=session_id,
        tags=["production", "batch-processing"],
        metadata={
            "region": "us-east-1",
            "tier": "premium",
            "experiment": "variant_a"
        },
        version="2.0.0"
    ):
        # All observations created here inherit these attributes
        langfuse = get_client()
        with langfuse.start_as_current_span("main-task") as span:
            subtask()
```

#### Error Handling and Logging

```python
from langfuse import observe, get_client

@observe(as_type="span")
def error_handling_example(data):
    langfuse = get_client()
    
    with langfuse.start_as_current_span("risky-operation") as span:
        try:
            result = risky_operation(data)
            span.update(output=result)
        except ValueError as e:
            # Span will record the error
            span.update(level="ERROR")
            raise
        except Exception as e:
            span.update(
                output={"error": str(e)},
                level="ERROR"
            )
            return None
```

#### Async Support

```python
from langfuse import observe, get_client

@observe()
async def async_pipeline(query: str):
    """Supports async/await"""
    langfuse = get_client()
    
    with langfuse.start_as_current_span("async-chain") as span:
        # Async operations
        results = await asyncio.gather(
            fetch_documents(query),
            fetch_embeddings(query)
        )
        span.update(output={"status": "gathered"})
        
        # Async LLM call
        with langfuse.start_as_current_generation(
            name="async-llm",
            model="gpt-4o"
        ) as gen:
            response = await openai.ChatCompletion.acreate(...)
            gen.update(output=response.content)
```

---

## JavaScript/TypeScript SDK

### Overview

The Langfuse TypeScript SDK v4 (GA in August 2025) is built on OpenTelemetry v2, providing robust observability for JavaScript/Node.js applications. Three main instrumentation approaches:

1. **`startActiveObservation`** - Callback-based with automatic lifecycle management
2. **`observe`** - Decorator/wrapper pattern for existing functions
3. **`startObservation`** - Manual control with `endObservation`

### Installation

```bash
npm install @langfuse/tracing
# or
pnpm add @langfuse/tracing
```

### Basic Setup

```typescript
import { LangfuseSpanProcessor } from "@langfuse/otel";
import { NodeTracerProvider } from "@opentelemetry/sdk-node";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";

// Initialize tracer provider
const provider = new NodeTracerProvider({
  resource: new Resource({
    "service.name": "my-app",
  }),
});

// Add Langfuse exporter
provider.addSpanProcessor(
  new LangfuseSpanProcessor({
    publicKey: process.env.LANGFUSE_PUBLIC_KEY,
    secretKey: process.env.LANGFUSE_SECRET_KEY,
    baseUrl: process.env.LANGFUSE_BASE_URL,
  })
);

provider.register();

// Environment variables:
// LANGFUSE_PUBLIC_KEY="pk-lf-..."
// LANGFUSE_SECRET_KEY="sk-lf-..."
// LANGFUSE_BASE_URL="https://cloud.langfuse.com"
```

### 1. startActiveObservation (Recommended)

The recommended approach with automatic lifecycle management and context handling.

#### Basic Usage

```typescript
import { startActiveObservation } from "@langfuse/tracing";

await startActiveObservation(
  "my-first-trace",
  async (span) => {
    span.update({
      input: "Hello, Langfuse!",
      output: "This is my first trace!"
    });
  }
);
```

#### With Nested Observations

```typescript
import { startActiveObservation } from "@langfuse/tracing";

async function retrieverQAPipeline(query: string) {
  await startActiveObservation(
    "rag-pipeline",
    async (pipelineSpan) => {
      pipelineSpan.update({
        input: { query },
        metadata: { type: "rag" }
      });

      // Nested retrieval
      await startActiveObservation(
        "vector-search",
        async (retrievalSpan) => {
          const documents = await vectorStore.search(query);
          retrievalSpan.update({
            output: {
              documentCount: documents.length,
              documents
            },
            metadata: { vectorDb: "pinecone" }
          });
        },
        { asType: "retrieval" }
      );

      // Nested generation
      await startActiveObservation(
        "llm-generation",
        async (generationSpan) => {
          const response = await openai.chat.completions.create({
            model: "gpt-4o",
            messages: [
              {
                role: "system",
                content: `You are a helpful assistant. Use the following context: ${documents}`
              },
              { role: "user", content: query }
            ]
          });

          generationSpan.update({
            output: response.choices[0].message.content,
            usage: {
              inputTokens: response.usage?.prompt_tokens,
              outputTokens: response.usage?.completion_tokens
            }
          });
        },
        { asType: "generation", model: "gpt-4o" }
      );

      pipelineSpan.update({ output: { status: "completed" } });
    },
    { asType: "agent" }
  );
}
```

#### Observation Types

```typescript
import { startActiveObservation } from "@langfuse/tracing";

// Generic span
await startActiveObservation(
  "processing",
  async (span) => {
    // implementation
  },
  { asType: "span" }
);

// LLM generation
await startActiveObservation(
  "llm-call",
  async (gen) => {
    // implementation
  },
  { asType: "generation", model: "gpt-4o" }
);

// Retrieval
await startActiveObservation(
  "vector-search",
  async (ret) => {
    // implementation
  },
  { asType: "retrieval" }
);

// Tool/Function
await startActiveObservation(
  "calculator",
  async (tool) => {
    // implementation
  },
  { asType: "tool" }
);

// Agent
await startActiveObservation(
  "agent-workflow",
  async (agent) => {
    // implementation
  },
  { asType: "agent" }
);
```

### 2. observe (Decorator Pattern)

Wrap existing functions without modifying their logic.

#### Basic Function Wrapping

```typescript
import { observe } from "@langfuse/tracing";

const tracedFunction = observe(async (source: string) => {
  return { data: `some data from ${source}` };
});

const result = await tracedFunction("API");
```

#### With Custom Options

```typescript
import { observe, updateActiveObservation } from "@langfuse/tracing";

const llmCall = observe(
  async (prompt: string) => {
    updateActiveObservation({
      metadata: { model: "gpt-4o", temperature: 0.7 }
    });

    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [{ role: "user", content: prompt }]
    });

    return response.choices[0].message.content;
  },
  {
    name: "llm-generation",
    asType: "generation"
  }
);

const answer = await llmCall("What is AI?");
```

#### Wrapping Methods

```typescript
import { observe } from "@langfuse/tracing";

class DataProcessor {
  private vectorStore: VectorStore;

  retrieveDocuments = observe(
    async (query: string) => {
      return this.vectorStore.search(query);
    },
    { name: "vector-search", asType: "retrieval" }
  );

  generateResponse = observe(
    async (context: string, query: string) => {
      const response = await openai.chat.completions.create({
        model: "gpt-4o",
        messages: [
          { role: "system", content: `Context: ${context}` },
          { role: "user", content: query }
        ]
      });
      return response.choices[0].message.content;
    },
    { name: "response-generation", asType: "generation" }
  );
}
```

### 3. Manual Control (startObservation)

For fine-grained control over observation lifecycle.

```typescript
import { startObservation, endObservation } from "@langfuse/tracing";

// Manual span management
const spanId = startObservation({
  name: "manual-processing",
  input: { data: "input_value" }
});

try {
  const result = await processData();
  endObservation(spanId, {
    output: result
  });
} catch (error) {
  endObservation(spanId, {
    output: { error: String(error) }
  });
}
```

### 4. Attribute Propagation

```typescript
import {
  startActiveObservation,
  propagateAttributes
} from "@langfuse/tracing";

await startActiveObservation(
  "user-workflow",
  async (span) => {
    await propagateAttributes(
      {
        userId: "user_123",
        sessionId: "session_abc",
        tags: ["production", "premium-tier"],
        metadata: {
          email: "user@example.com",
          region: "us-east-1",
          experiment: "variant_a"
        },
        version: "1.0.0"
      },
      async () => {
        // All observations created here inherit these attributes
        // including nested startActiveObservation calls
        await processUserRequest();
      }
    );
  }
);
```

### 5. Serverless / Short-Lived Environments

Critical for Vercel, AWS Lambda, and other serverless platforms.

#### Vercel/Next.js with waitUntil

```typescript
import { startActiveObservation } from "@langfuse/tracing";
import { waitUntil } from "@vercel/functions";

export async function POST(request: Request) {
  const promise = startActiveObservation(
    "api-request",
    async (span) => {
      span.update({
        input: await request.json()
      });

      const result = await processRequest();
      span.update({ output: result });

      return result;
    }
  );

  waitUntil(promise);
  return new Response(JSON.stringify(await promise));
}
```

#### AWS Lambda with Flushing

```typescript
import { startActiveObservation } from "@langfuse/tracing";
import { langfuseSpanProcessor } from "@langfuse/otel";

export async function handler(event: any, context: any) {
  try {
    await startActiveObservation(
      "lambda-execution",
      async (span) => {
        span.update({
          input: event,
          metadata: { functionName: context.functionName }
        });

        const result = await processEvent(event);
        span.update({ output: result });

        return result;
      }
    );
  } finally {
    // Critical: Force flush before Lambda returns
    await langfuseSpanProcessor.forceFlush();
  }
}
```

### 6. Error Handling

```typescript
import { startActiveObservation } from "@langfuse/tracing";

async function processWithErrorHandling() {
  try {
    await startActiveObservation(
      "risky-operation",
      async (span) => {
        try {
          const result = await riskyOperation();
          span.update({ output: result });
        } catch (error) {
          span.update({
            output: { error: String(error) },
            level: "ERROR"
          });
          throw error;
        }
      }
    );
  } catch (error) {
    console.error("Failed:", error);
  }
}
```

---

## Framework Integrations

### LangChain Integration

#### Python LangChain

##### Setup

```bash
pip install langfuse langchain langchain_openai langchain_community
```

##### Basic Usage

```python
from langfuse.langchain import CallbackHandler
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize callback handler
langfuse_handler = CallbackHandler()

# Create chain
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{input}")
])

model = ChatOpenAI(model="gpt-4o")
chain = prompt | model | StrOutputParser()

# Single invocation
result = chain.invoke(
    {"input": "What is AI?"},
    config={"callbacks": [langfuse_handler]}
)

# Batch processing
results = chain.batch(
    [
        {"input": "What is AI?"},
        {"input": "What is ML?"},
        {"input": "What is DL?"}
    ],
    config={"callbacks": [langfuse_handler]}
)

# Async support
async_result = await chain.ainvoke(
    {"input": "What is AI?"},
    config={"callbacks": [langfuse_handler]}
)

# Streaming
for chunk in chain.stream(
    {"input": "What is AI?"},
    config={"callbacks": [langfuse_handler]}
):
    print(chunk, end="", flush=True)
```

##### With Distributed Tracing

```python
from langfuse.langchain import CallbackHandler
from langfuse import get_client

langfuse_handler = CallbackHandler(
    trace_name="my-custom-trace",
    session_id="session_123",
    user_id="user_456",
    tags=["production"],
    metadata={"version": "1.0"}
)

result = chain.invoke(
    {"input": "Query"},
    config={"callbacks": [langfuse_handler]}
)
```

##### RetrievalQA Example

```python
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langfuse.langchain import CallbackHandler

# Setup
loader = WebBaseLoader("https://example.com")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
split_docs = splitter.split_documents(docs)

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(split_docs, embeddings)

# Chain
llm = ChatOpenAI(model="gpt-4o")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# With tracing
langfuse_handler = CallbackHandler()
result = qa_chain.run(
    "What is the main topic?",
    callbacks=[langfuse_handler]
)
```

#### JavaScript/TypeScript LangChain

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { startActiveObservation } from "@langfuse/tracing";

const llm = new ChatOpenAI({ modelName: "gpt-4o" });

const prompt = ChatPromptTemplate.fromMessages([
  ["system", "You are a helpful assistant."],
  ["user", "{input}"],
]);

const chain = prompt.pipe(llm).pipe(new StringOutputParser());

// Traced invocation
await startActiveObservation(
  "langchain-query",
  async (span) => {
    const result = await chain.invoke({
      input: "What is AI?"
    });

    span.update({
      output: result,
      metadata: { chainType: "langchain" }
    });
  }
);
```

### LlamaIndex Integration

#### Python LlamaIndex

##### Via Callback Handler

```python
from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager
from langfuse.llama_index import LlamaIndexCallbackHandler
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Setup
langfuse_callback = LlamaIndexCallbackHandler()
Settings.callback_manager = CallbackManager([langfuse_callback])

# Load and index
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("What is the main topic?")
```

##### Via Instrumentation Module (Beta)

```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
import base64
import os

# Setup OTEL
LANGFUSE_AUTH = base64.b64encode(
    f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
).decode()

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "https://cloud.langfuse.com/api/public/otel"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))

# Instrument LlamaIndex
LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

# All LlamaIndex operations are now traced
```

### OpenAI SDK Integration

#### Python OpenAI

```python
from langfuse.openai import OpenAI as LangfuseOpenAI

# Direct drop-in replacement
client = LangfuseOpenAI(
    api_key="sk-...",
    public_key="pk-lf-...",
    secret_key="sk-lf-..."
)

# All OpenAI calls are automatically traced
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)

# With session context
client = LangfuseOpenAI(
    api_key="sk-...",
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    langfuse_session_id="session_123",
    langfuse_user_id="user_456",
    langfuse_tags=["production"],
    langfuse_metadata={"version": "1.0"}
)
```

#### TypeScript OpenAI

```typescript
import { observeOpenAI } from "@langfuse/openai";
import OpenAI from "openai";
import { startActiveObservation } from "@langfuse/tracing";

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

await startActiveObservation(
  "user-request",
  async (span) => {
    // Wrap OpenAI client with Langfuse observation
    const tracedClient = observeOpenAI(client, {
      parent: span,
      generationName: "chat-completion"
    });

    const response = await tracedClient.chat.completions.create({
      model: "gpt-4o",
      messages: [{ role: "user", content: "What is AI?" }]
    });

    span.update({
      output: response.choices[0].message.content
    });
  }
);
```

### Anthropic Integration

#### Python Anthropic (via OpenTelemetry)

```python
from anthropic import Anthropic
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
import base64
import os

# Setup OpenTelemetry
LANGFUSE_AUTH = base64.b64encode(
    f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
).decode()

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "https://cloud.langfuse.com/api/public/otel"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))

# Instrument Anthropic
AnthropicInstrumentor().instrument(tracer_provider=tracer_provider)

# All Anthropic calls are now traced
client = Anthropic(api_key="sk-ant-...")
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Instructor Integration (Structured Outputs)

```python
from langfuse.openai import OpenAI as LangfuseOpenAI
import instructor
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str = Field(description="The user's name")
    age: int = Field(description="The user's age")
    email: str = Field(description="The user's email")

# Setup Langfuse OpenAI client
client = LangfuseOpenAI(
    api_key="sk-...",
    public_key="pk-lf-...",
    secret_key="sk-lf-..."
)

# Patch with instructor
patched_client = instructor.from_openai(client)

# Structured output is automatically traced
user = patched_client.chat.completions.create(
    model="gpt-4o",
    response_model=User,
    messages=[
        {"role": "user", "content": "Extract user info from: John is 30 years old and his email is john@example.com"}
    ]
)

print(user.name)  # "John"
print(user.age)   # 30
```

### Vercel AI SDK Integration

#### Next.js Integration

```typescript
import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";
import { startActiveObservation } from "@langfuse/tracing";

export async function POST(request: Request) {
  try {
    const { messages } = await request.json();

    const result = await startActiveObservation(
      "ai-generation",
      async (span) => {
        const { text, usage } = await generateText({
          model: openai("gpt-4o"),
          system: "You are a helpful assistant.",
          messages,
          experimental_telemetry: {
            isEnabled: true
          }
        });

        span.update({
          output: text,
          usage: {
            inputTokens: usage.promptTokens,
            outputTokens: usage.completionTokens
          }
        });

        return text;
      }
    );

    return new Response(JSON.stringify({ text: result }));
  } catch (error) {
    console.error("Error:", error);
    return new Response("Error", { status: 500 });
  }
}
```

### LiteLLM Integration

#### Via LiteLLM Proxy

```yaml
# litellm_config.yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: sk-...

litellm_settings:
  callbacks: ["langfuse_otel"]
  database_url: "postgresql://user:pass@localhost/litellm"
  drop_params: true
  allow_duplicate_keys: false
```

Environment setup:
```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export OTEL_EXPORTER_OTLP_ENDPOINT="https://cloud.langfuse.com/api/public/otel"
```

Launch proxy:
```bash
litellm --config /path/to/litellm_config.yaml
```

#### Python LiteLLM SDK

```python
from litellm import completion
import os

os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."

# All calls automatically traced via LiteLLM's callback system
response = completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
    langfuse_metadata={
        "user_id": "user_123",
        "session_id": "session_abc",
        "tags": ["production"]
    }
)
```

### AWS Bedrock Integration

#### Python with @observe Decorator

```python
from langfuse import observe
import boto3
import json

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

@observe(as_type="generation")
def call_bedrock_claude(prompt: str) -> str:
    """Call AWS Bedrock Claude model with tracing"""
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-06-01",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
    )

    result = json.loads(response['body'].read())
    return result['content'][0]['text']

# Usage
answer = call_bedrock_claude("What is AWS Bedrock?")
```

#### With Context Manager

```python
from langfuse import get_client
import boto3
import json

langfuse = get_client()
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def bedrock_rag_pipeline(query: str):
    with langfuse.start_as_current_span(
        name="bedrock-rag",
        input={"query": query}
    ) as pipeline:
        
        # Retrieve documents
        with langfuse.start_as_current_span(
            name="retrieval",
            as_type="retrieval"
        ) as retrieval:
            documents = vector_store.search(query)
            retrieval.update(output={"doc_count": len(documents)})
        
        # Call Bedrock
        with langfuse.start_as_current_generation(
            name="bedrock-claude",
            model="claude-3-5-sonnet"
        ) as generation:
            context = "\n".join([doc.page_content for doc in documents])
            
            response = bedrock.invoke_model(
                modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-06-01",
                    "max_tokens": 1024,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Context:\n{context}\n\nQuestion: {query}"
                        }
                    ]
                })
            )
            
            result = json.loads(response['body'].read())
            answer = result['content'][0]['text']
            generation.update(output=answer)
        
        pipeline.update(output={"answer": answer})
```

---

## API and OpenTelemetry

### REST API Overview

Langfuse provides a public REST API for direct integration without SDKs.

#### Authentication

Uses HTTP Basic Auth with Langfuse API keys:

```bash
# Format
Authorization: Basic <base64(public_key:secret_key)>

# Example with curl
curl -u pk-lf-...:sk-lf-... https://cloud.langfuse.com/api/public/projects

# Python
import requests
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth("pk-lf-...", "sk-lf-...")
response = requests.get(
    "https://cloud.langfuse.com/api/public/projects",
    auth=auth
)
```

#### Base URLs

- **EU Region**: `https://cloud.langfuse.com`
- **US Region**: `https://us.cloud.langfuse.com`
- **HIPAA Region**: `https://hipaa.cloud.langfuse.com`
- **Local**: `http://localhost:3000`

#### Key Endpoints

```
GET    /api/public/projects                 - List projects
POST   /api/public/ingestion                - Ingest observations (batch)
POST   /api/public/ingestion/event          - Single event ingestion
GET    /api/public/traces/{traceId}         - Get trace details
GET    /api/public/observations/{obsId}     - Get observation details
GET    /api/public/sessions/{sessionId}     - Get session details
```

#### Batch Ingestion

```python
import requests
from requests.auth import HTTPBasicAuth
import json

auth = HTTPBasicAuth("pk-lf-...", "sk-lf-...")

# Batch multiple events
events = [
    {
        "id": "trace-1",
        "type": "trace-create",
        "timestamp": "2025-01-01T12:00:00Z",
        "body": {
            "id": "trace-1",
            "userId": "user_123",
            "sessionId": "session_abc",
            "metadata": {"version": "1.0"}
        }
    },
    {
        "id": "span-1",
        "type": "observation-create",
        "timestamp": "2025-01-01T12:00:00Z",
        "body": {
            "id": "span-1",
            "traceId": "trace-1",
            "type": "span",
            "name": "processing",
            "input": {"data": "test"},
            "output": {"result": "done"},
            "startTime": "2025-01-01T12:00:00Z",
            "endTime": "2025-01-01T12:00:01Z"
        }
    }
]

response = requests.post(
    "https://cloud.langfuse.com/api/public/ingestion",
    auth=auth,
    json={"batch": events}
)

print(response.status_code)  # 207 (partial success possible)
print(response.json())
```

### OpenTelemetry Integration

#### OTEL Endpoint

Langfuse accepts OpenTelemetry Protocol (OTLP) traces at the `/api/public/otel` endpoint.

#### Python OTEL Setup

```python
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import base64
import os

# Setup auth
LANGFUSE_AUTH = base64.b64encode(
    f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
).decode()

# Configure exporter
exporter = OTLPSpanExporter(
    endpoint="https://cloud.langfuse.com/api/public/otel",
    headers=(("Authorization", f"Basic {LANGFUSE_AUTH}"),)
)

# Setup tracer
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))

# Use tracer
tracer = tracer_provider.get_tracer(__name__)
with tracer.start_as_current_span("my-span") as span:
    span.set_attribute("custom.attribute", "value")
```

#### Langfuse-Specific OTEL Attributes

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("llm-call") as span:
    # Langfuse-specific attributes
    span.set_attribute("langfuse.observation.type", "generation")
    span.set_attribute("langfuse.observation.model", "gpt-4o")
    span.set_attribute("langfuse.observation.input", '{"prompt": "Hello"}')
    span.set_attribute("langfuse.observation.output", '{"response": "Hi"}')
    span.set_attribute("langfuse.trace.user_id", "user_123")
    span.set_attribute("langfuse.trace.session_id", "session_abc")
    span.set_attribute("langfuse.trace.tags", ["production"])
    span.set_attribute("langfuse.trace.metadata", '{"version": "1.0"}')
```

#### OpenLIT Integration

```python
import openlit
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry import trace
import base64
import os

# Setup OTEL for Langfuse
LANGFUSE_AUTH = base64.b64encode(
    f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
).decode()

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "https://cloud.langfuse.com/api/public/otel"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(tracer_provider)

# Initialize OpenLIT instrumentation
openlit.init(disable_batch=True)

# All instrumented libraries now send traces to Langfuse
```

---

## No-Code Platform Integrations

### Dify Integration

```yaml
# In Dify app settings:
# Navigate to Monitoring > Third-party LLMOps
# Provider: Langfuse
# Endpoint: https://cloud.langfuse.com
# Public Key: pk-lf-...
# Secret Key: sk-lf-...
```

Benefits:
- Automatic tracing of all Dify workflows
- Session/chat history tracking
- User interaction analytics
- Cost and token monitoring
- A/B testing and evaluation

### Flowise Integration

```json
// In Flowise Credentials:
{
  "name": "Langfuse",
  "type": "langfuse",
  "publicKey": "pk-lf-...",
  "secretKey": "sk-lf-...",
  "baseURL": "https://cloud.langfuse.com"
}
```

### Langflow Integration

```bash
# Start Langflow with Langfuse environment variables
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_BASE_URL="https://cloud.langfuse.com"

python -m langflow run
```

---

## Best Practices

### 1. Batching and Flushing

```python
# Production setup with optimized batching
langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    flush_at=100,       # Flush after 100 events
    flush_interval=30,  # Or every 30 seconds
)

# In FastAPI/Flask shutdown
@app.on_event("shutdown")
def shutdown():
    langfuse.shutdown()  # Blocks until all flushed
```

### 2. Error Handling

```python
from langfuse import observe, get_client

@observe()
def robust_function(data):
    langfuse = get_client()
    
    try:
        result = process(data)
        return result
    except ValueError as e:
        langfuse.update_current_trace(tags=["error"])
        raise
    finally:
        langfuse.flush()  # In short-lived apps
```

### 3. Session Management

```python
from langfuse import propagate_attributes

def user_conversation(user_id: str, session_id: str):
    """Track multi-turn conversations"""
    with propagate_attributes(
        user_id=user_id,
        session_id=session_id,  # Same for all turns
        metadata={"conversation_type": "support"}
    ):
        # Multiple interactions within same session
        response1 = chat_turn("Hello")
        response2 = chat_turn("Tell me more")
```

### 4. Cost Tracking (Token Usage)

```python
from langfuse import get_client

@observe(as_type="generation")
def call_llm(prompt: str):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    
    langfuse = get_client()
    langfuse.update_current_trace(
        metadata={
            "cost": calculate_cost(
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
                "gpt-4o"
            )
        }
    )
    
    return response.choices[0].message.content
```

### 5. Metadata Organization

```python
# Use structured metadata for filtering/analytics
with propagate_attributes(
    metadata={
        "request_id": uuid.uuid4().hex,
        "user_tier": "premium",
        "region": "us-east-1",
        "feature": "recommendation_engine",
        "experiment": "variant_b",
        "deployment": "production"
    }
):
    process_request()
```

### 6. Serverless Best Practices

```typescript
// TypeScript in Next.js API route
import { startActiveObservation } from "@langfuse/tracing";
import { langfuseSpanProcessor } from "@langfuse/otel";

export async function POST(request: Request) {
  try {
    const result = await startActiveObservation(
      "api-call",
      async (span) => {
        const data = await request.json();
        span.update({ input: data });

        const output = await process(data);
        span.update({ output });

        return output;
      }
    );

    return Response.json(result);
  } finally {
    // CRITICAL: Flush before function exits
    await langfuseSpanProcessor.forceFlush();
  }
}
```

---

## Summary Table

| Feature | Python SDK | TypeScript SDK | LangChain | OpenAI | LiteLLM | Bedrock |
|---------|-----------|----------------|-----------|--------|---------|---------|
| Decorators | ✓ @observe | ✓ observe() | ✓ Callback | - | ✓ Auto | ✓ @observe |
| Context Managers | ✓ start_as_current | ✓ startActiveObservation | - | - | - | - |
| Async Support | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Batch Processing | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| Session Tracking | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Error Tracking | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Nested Spans | ✓ OTel | ✓ OTel | ✓ | ✓ | ✓ | ✓ |
| Token Usage | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## Resources

- **Official Docs**: https://langfuse.com/docs
- **Python SDK**: https://github.com/langfuse/langfuse-python
- **TypeScript SDK**: https://github.com/langfuse/langfuse-js
- **API Reference**: https://api.reference.langfuse.com/
- **Cookbook Examples**: https://langfuse.com/guides



<!-- END: original content from langfuse-guide.md -->

---

## litellm-comprehensive-guide

<!-- BEGIN: original content from litellm-comprehensive-guide.md -->

*Source: `docs/bunchloch/meaisínfhoghlaim/litellm-comprehensive-guide.md` (10267 words, 4477 lines)*

# LiteLLM API Patterns and Usage Conventions - Comprehensive Research

## 1. MODEL NAMING CONVENTIONS

### General Pattern
LiteLLM uses provider-prefixed model identifiers: `model=<provider_name>/<model_name>`

### Provider-Specific Naming Examples

#### OpenAI
```python
# Chat completions
model = "openai/gpt-4o"
model = "openai/gpt-4-turbo"
model = "openai/gpt-3.5-turbo"

# Text completions (deprecated but supported)
# ⚠️ DEPRECATED: text-davinci-003 is discontinued by OpenAI as of Jan 2024
# Use gpt-3.5-turbo-instruct or gpt-4o for new projects
model = "text-completion-openai/text-davinci-003"
```

#### Azure OpenAI
```python
# Standard models
model = "azure/<deployment_name>"

# O-series models (reasoning)
model = "azure/o_series/<deployment_name>"
# OR auto-detected: model = "azure/o1-deployment"

# GPT-5 series
model = "azure/gpt5_series/<deployment_name>"
# OR auto-detected: model = "azure/gpt-5-deployment"

# Text completion
model = "azure_text/<deployment_name>"
```

#### AWS Bedrock
```python
# Default route
model = "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0"

# Converse API
model = "bedrock/converse/anthropic.claude-opus-4-1-20250805-v1:0"

# Invoke API
model = "bedrock/invoke/anthropic.claude-3-sonnet-20240229-v1:0"

# Specialized routes
model = "bedrock/deepseek_r1/arn:aws:bedrock:region:account:imported-model/id"
model = "bedrock/llama/meta.llama2-70b-chat-v1"
model = "bedrock/qwen3/qwen/qwen3-vl"
```

Bedrock naming format: `bedrock/{provider}.{model-id}-{version}:{revision}`
- Provider: `anthropic`, `meta`, `cohere`, `mistral`, `amazon`, `ai21`

#### Anthropic (Direct)
```python
model = "anthropic/claude-opus-4-1-20250805"
model = "anthropic/claude-3-5-sonnet-20240620"
model = "anthropic/claude-3-haiku-20240307"
# ⚠️ DEPRECATED: claude-2.1 and claude-instant-1.2 are legacy models
# Use claude-3-5-sonnet or claude-3-haiku for new projects
model = "anthropic/claude-2.1"  # Legacy - avoid for new projects
model = "anthropic/claude-instant-1.2"  # Legacy - avoid for new projects
```

#### Other Popular Providers
```python
model = "openrouter/google/palm-2-chat-bison"
model = "huggingface/WizardLM/WizardCoder-Python-34B-V1.0"
model = "ollama/llama2"
model = "cohere/command-r-plus"
model = "vertexai/gemini-1.5-pro"
model = "nvidia_nim/mistral-7b-instruct-v3"
model = "together_ai/meta-llama/Llama-3-70b-chat-hf"
```

### Proxy Configuration (config.yaml)
```yaml
model_list:
  - model_name: "gpt-3.5"  # User-facing name
    litellm_params:
      model: "openai/gpt-3.5-turbo"  # Actual model sent to LiteLLM
      api_key: "${OPENAI_API_KEY}"  # Environment variable reference
      api_base: "https://api.openai.com/v1"

  - model_name: "gpt-4-azure"
    litellm_params:
      model: "azure/gpt-4-deployment"
      api_key: "${AZURE_API_KEY}"
      api_base: "${AZURE_API_BASE}"
      api_version: "2024-08-01-preview"
```

### Provider-Specific Parameters
Access provider-specific parameters via `litellm.<provider_name>Config`:

```python
from litellm import AzureOpenAIConfig, OpenAIConfig

# Set provider-specific defaults
openai_config = OpenAIConfig(
    organization="org-123",
    timeout=30
)

# Azure-specific
azure_config = AzureOpenAIConfig(
    api_version="2024-08-01-preview"
)
```

---

## 2. MESSAGE FORMAT AND ROLES

### Standard Message Structure
Each message must include `role` and `content`, with optional metadata:

```python
{
    "role": "system|user|assistant|function|tool",
    "content": "string | list[dict] | None",  # None allowed for assistant with function calls
    "name": "string",  # Required if role="function", optional otherwise
    "function_call": {...},  # Optional: function call object
    "tool_call_id": "string"  # Optional: links to previous tool_call
}
```

### Role Types

| Role | Purpose | Content |
|------|---------|---------|
| `system` | Sets context, instructions, and behavior | Usually a string instruction |
| `user` | User input/requests | String or vision content array |
| `assistant` | Model responses | Text, function calls, or tool calls |
| `function` | Function execution result | String result or error message |
| `tool` | Tool/function call result | String result or error message |

### Basic Completion Example
```python
from litellm import completion

messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant specialized in Python programming."
    },
    {
        "role": "user",
        "content": "How do I read a file in Python?"
    }
]

response = completion(
    model="openai/gpt-4o",
    messages=messages,
    temperature=0.7,
    max_tokens=500
)

print(response['choices'][0]['message']['content'])
```

### Multi-turn Conversation Pattern
```python
import litellm

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the capital of France?"},
]

# First turn
response1 = litellm.completion(model="openai/gpt-4o", messages=messages)
assistant_response = response1['choices'][0]['message']['content']

# Add to conversation
messages.append({"role": "assistant", "content": assistant_response})
messages.append({"role": "user", "content": "When was it founded?"})

# Second turn with context
response2 = litellm.completion(model="openai/gpt-4o", messages=messages)
```

### Message Content Variations

#### Text Only
```python
{"role": "user", "content": "Hello, how are you?"}
```

#### Vision/Image Content
```python
{
    "role": "user",
    "content": [
        {"type": "text", "text": "What's in this image?"},
        {
            "type": "image_url",
            "image_url": {
                "url": "https://example.com/image.jpg",
                # Optional: specify format explicitly
                "format": "image/jpeg"
            }
        }
    ]
}

# OR base64 encoded
{
    "role": "user",
    "content": [
        {"type": "text", "text": "Analyze this image"},
        {
            "type": "image_url",
            "image_url": {
                "url": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
            }
        }
    ]
}
```

### Custom Prompt Templates
For providers like HuggingFace, Ollama, Together AI:

```python
litellm.completion(
    model="ollama/llama2",
    messages=messages,
    pre_message="[INST]",  # Prefix for messages
    post_message="[/INST]"  # Suffix for messages
)
```

### Role Alternation Handling
Some models require alternating message roles (user → assistant → user):

```python
# Problem: consecutive user messages
messages = [
    {"role": "user", "content": "First question"},
    {"role": "user", "content": "Second question"}  # ERROR for some models
]

# Solution: Insert empty assistant messages for compatibility
messages = [
    {"role": "user", "content": "First question"},
    {"role": "assistant", "content": ""},  # Placeholder
    {"role": "user", "content": "Second question"}
]
```

### Prefix Assistant Messages
Pre-fill assistant responses for few-shot examples:

```python
messages = [
    {"role": "system", "content": "You are a JSON formatter."},
    {"role": "user", "content": "Format: {'name': 'John'}"},
    {
        "role": "assistant",
        "content": '{"name": "John"}'  # Pre-filled example
    },
    {"role": "user", "content": "Format: {'name': 'Jane', 'age': 30}"}
]
```

---

## 3. FUNCTION CALLING AND TOOL USE PATTERNS

### Function Definition Schema
```python
tools = [
    {
        "type": "function",  # Always "function"
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and state, e.g., 'San Francisco, CA'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# Alternative format (backward compatible)
functions = [
    {
        "name": "get_weather",
        "description": "...",
        "parameters": {...}
    }
]
```

### Basic Function Calling Flow
```python
from litellm import completion
import json

def get_weather(location: str, unit: str = "celsius") -> str:
    """Mock weather function"""
    return f"Weather in {location}: 72°{unit[0].upper()}"

# Step 1: Call model with tools
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant with access to weather information."
    },
    {
        "role": "user",
        "content": "What's the weather in San Francisco?"
    }
]

response = completion(
    model="openai/gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto"  # "auto", "required", or specific tool name
)

# Step 2: Parse tool call
if response['choices'][0]['message'].get('tool_calls'):
    tool_call = response['choices'][0]['message']['tool_calls'][0]
    function_name = tool_call['function']['name']
    function_args = json.loads(tool_call['function']['arguments'])
    
    # Step 3: Execute function
    if function_name == "get_weather":
        result = get_weather(**function_args)
    
    # Step 4: Add results to conversation
    messages.append({"role": "assistant", "content": response['choices'][0]['message']['content'], "tool_calls": tool_call})
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call['id'],
        "name": function_name,
        "content": result
    })
    
    # Step 5: Get final response
    final_response = completion(model="openai/gpt-4o", messages=messages)
    print(final_response['choices'][0]['message']['content'])
```

### Parallel Function Calling
```python
# Model can call multiple functions at once
response = completion(
    model="openai/gpt-4-turbo",  # Must support parallel calls
    messages=[
        {
            "role": "user",
            "content": "What's the weather in San Francisco, Tokyo, and Paris?"
        }
    ],
    tools=tools
)

# response['choices'][0]['message']['tool_calls'] contains multiple calls
tool_calls = response['choices'][0]['message']['tool_calls']

# Process all calls
results = []
for tool_call in tool_calls:
    function_name = tool_call['function']['name']
    args = json.loads(tool_call['function']['arguments'])
    result = execute_function(function_name, args)
    results.append({
        "tool_call_id": tool_call['id'],
        "result": result
    })
```

### Function Calling with Specific Tool Selection
```python
# Force specific tool
response = completion(
    model="openai/gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "get_weather"}}
)

# Disable tool use
response = completion(
    model="openai/gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="none"  # Never call tools, respond normally
)
```

### Model Support Detection
```python
import litellm

# Check if model supports function calling
supports_fc = litellm.supports_function_calling(model="openai/gpt-4o")
# Returns: True

# Check parallel function calling
supports_parallel = litellm.supports_parallel_function_calling(model="openai/gpt-4o")
# Returns: True

# For models without native support, use prompt injection
response = litellm.completion(
    model="ollama/llama2",
    messages=messages,
    tools=tools,
    add_function_to_prompt=True  # Embed function schema in prompt
)
```

### Helper: Convert Python Function to Schema
```python
from litellm import function_to_dict

def get_weather(location: str, unit: str = "celsius") -> str:
    """
    Get the current weather in a given location.
    
    Args:
        location: The city and state, e.g. San Francisco, CA
        unit: Temperature unit (celsius or fahrenheit)
    
    Returns:
        Weather description
    """
    pass

# Auto-generate schema from docstring
function_schema = function_to_dict(get_weather)
tools = [{"type": "function", "function": function_schema}]
```

### Fallback for Function Calling
```python
# Use prompt-based function calling for unsupported models
response = completion(
    model="anthropic/claude-3-haiku-20240307",
    messages=messages,
    tools=tools,
    add_function_to_prompt=True  # For models without native support
)
```

---

## 4. ASYNC VS SYNC PATTERNS

### Sync Completion (Blocking)
```python
from litellm import completion

# Simple blocking call
response = completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response['choices'][0]['message']['content'])
```

### Async Completion (Non-blocking)
```python
import asyncio
from litellm import acompletion

async def main():
    response = await acompletion(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print(response['choices'][0]['message']['content'])

# Run
asyncio.run(main())
```

### Async with Streaming
```python
async def stream_response():
    response = await acompletion(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": "Write a poem"}],
        stream=True
    )
    
    async for chunk in response:
        # Process each chunk as it arrives
        if chunk['choices'][0].get('delta', {}).get('content'):
            print(chunk['choices'][0]['delta']['content'], end='')

asyncio.run(stream_response())
```

### Sync Streaming
```python
from litellm import completion

response = completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "Write a poem"}],
    stream=True
)

# Iterate over chunks
for chunk in response:
    if chunk['choices'][0].get('delta', {}).get('content'):
        print(chunk['choices'][0]['delta']['content'], end='')
```

### Build Complete Response from Stream
```python
import litellm

stream_response = completion(
    model="openai/gpt-4o",
    messages=messages,
    stream=True
)

# Reconstruct full response from chunks
complete_response = litellm.stream_chunk_builder(
    stream_response,
    messages=messages
)

print(complete_response)
```

### Concurrent Requests
```python
import asyncio
from litellm import acompletion

async def call_model(prompt: str) -> str:
    response = await acompletion(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

async def main():
    # Run multiple requests concurrently
    results = await asyncio.gather(
        call_model("What is 2+2?"),
        call_model("What is the capital of France?"),
        call_model("What is the largest planet?")
    )
    
    for result in results:
        print(result)

asyncio.run(main())
```

### Timeout Configuration
```python
from litellm import completion

# Set timeout in seconds
response = completion(
    model="openai/gpt-4o",
    messages=messages,
    request_timeout=30  # 30 second timeout
)
```

### Streaming Chunk Limits (Infinite Loop Protection)
```python
import litellm

# Set maximum repeated chunks before error
litellm.REPEATED_STREAMING_CHUNK_LIMIT = 100

response = completion(
    model="openai/gpt-4o",
    messages=messages,
    stream=True
)

for chunk in response:
    # If same chunk repeats >100 times, raises InternalServerError
    print(chunk)
```

---

## 5. CALLBACK HANDLERS AND HOOKS

### Custom Logger Class Pattern
```python
from litellm import CustomLogger
import litellm

class MyCustomLogger(CustomLogger):
    """Custom logging implementation"""
    
    def log_pre_api_call(self, model, messages, kwargs):
        print(f"Calling {model} with {len(messages)} messages")
    
    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        print(f"API call took {end_time - start_time} seconds")
    
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Sync success callback"""
        print(f"Success: {kwargs['model']}")
        print(f"Cost: ${kwargs.get('response_cost', 0)}")
        print(f"Usage: {response_obj.usage}")
    
    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """Sync failure callback"""
        print(f"Failed: {kwargs['model']}")
        print(f"Error: {response_obj}")
    
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Async success callback - recommended for proxy"""
        print(f"Async success: {kwargs['model']}")
        # Send to external service
        # await send_to_analytics_service(...)
    
    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """Async failure callback"""
        print(f"Async failure: {kwargs['model']}")

# Register custom logger
custom_logger = MyCustomLogger()
litellm.callbacks = [custom_logger]

# Now all completions use the custom logger
response = litellm.completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Simple Callback Functions
```python
import litellm

# Cost tracking callback
def cost_tracker(kwargs, completion_response, start_time, end_time):
    """Track costs for all completions"""
    cost = kwargs.get("response_cost", 0)
    model = kwargs.get("model", "unknown")
    print(f"Model {model} cost: ${cost}")

# Register callback
litellm.success_callback = [cost_tracker]

# Error tracking callback
def error_handler(kwargs, response_obj, start_time, end_time):
    """Handle failures"""
    print(f"Error with {kwargs['model']}: {response_obj}")

litellm.failure_callback = [error_handler]
```

### Input/Pre-call Tracking
```python
import litellm

def log_input(kwargs, completion_response, start_time, end_time):
    """Log transformed inputs before API call"""
    messages = kwargs.get("messages", [])
    model = kwargs.get("model")
    print(f"Input to {model}: {len(messages)} messages")
    print(f"First message: {messages[0]['content'][:100]}...")

litellm.input_callback = [log_input]
```

### Response Cost Tracking
```python
import litellm

total_costs = {}

def track_cost(kwargs, completion_response, start_time, end_time):
    """Track costs by model"""
    model = kwargs['model']
    cost = kwargs.get('response_cost', 0)
    
    if model not in total_costs:
        total_costs[model] = 0
    total_costs[model] += cost

litellm.success_callback = [track_cost]

# Later, check costs
print(f"Total costs by model: {total_costs}")
```

### Async Callbacks for Streaming
```python
import litellm
import asyncio

async def async_cost_tracker(kwargs, completion_response, start_time, end_time):
    """Async callback for streaming"""
    cost = kwargs.get("response_cost", 0)
    model = kwargs.get("model")
    
    # Can call async functions
    # await send_to_service(model, cost)
    print(f"Async: {model} cost ${cost}")

litellm.success_callback = [async_cost_tracker]

async def main():
    response = await litellm.acompletion(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": "Hello"}]
    )

asyncio.run(main())
```

### Proxy-Specific Hooks

#### Pre-call Hook (Modify/Reject Requests)
```python
# In proxy configuration file
from fastapi import HTTPException

async def async_pre_call_hook(user_api_key_dict, cache, data, call_type):
    """
    Modify or reject requests before API call.
    Most powerful intervention point in proxy request lifecycle.
    """
    
    # Modify model
    if data.get("model") == "gpt-3.5-turbo":
        data["model"] = "gpt-4o"  # Upgrade model
    
    # Reject requests
    if "sensitive" in str(data.get("messages", "")):
        raise HTTPException(
            status_code=400,
            detail={"error": "Sensitive content detected"}
        )
    
    # Transform messages
    if data.get("messages"):
        data["messages"] = transform_messages(data["messages"])
    
    return data
```

#### Post-call Success Hook (Add Metadata)
```python
async def async_post_call_success_hook(data: dict, response: dict):
    """
    Add metadata or headers to response.
    Runs after successful LLM call.
    """
    # Add custom header
    if not response.get("_response_ms"):
        response["_response_ms"] = data.get("response_ms", 0)
    
    # Add request tracing
    response["_request_id"] = data.get("request_id")
    
    return response
```

#### Post-call Failure Hook (Error Handling)
```python
async def async_post_call_failure_hook(data: dict, exception: Exception):
    """Handle failed requests"""
    print(f"Request failed for {data['model']}: {exception}")
    # Log to error tracking service
```

#### Moderation Hook (Runs in Parallel)
```python
async def async_moderation_hook(data: dict):
    """
    Run content moderation in parallel with LLM call.
    Raises exception to reject request.
    """
    messages = data.get("messages", [])
    
    # Check for policy violations
    for msg in messages:
        if "banned_word" in str(msg.get("content", "")):
            raise HTTPException(
                status_code=400,
                detail={"error": "Content policy violated"}
            )
    
    # Check user permissions
    if data.get("user") == "restricted_user":
        raise HTTPException(
            status_code=403,
            detail={"error": "User not authorized"}
        )
```

#### Streaming Post-call Hook
```python
async def async_post_call_streaming_hook(data: dict, stream: Iterator):
    """Handle streamed responses"""
    # Can process streaming chunks
    for chunk in stream:
        # Modify or filter chunks
        yield chunk
```

### Best Practices for Callbacks
```python
import litellm
import traceback

class RobustLogger(litellm.CustomLogger):
    """Production-ready callback with error handling"""
    
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        try:
            # Keep callbacks lean and fast
            cost = kwargs.get("response_cost", 0)
            model = kwargs.get("model")
            
            # Short operations only
            if cost > 10:  # Log expensive calls
                await self.alert_expensive_call(model, cost)
        
        except Exception as e:
            # Failing callback shouldn't break everything
            print(f"Callback error: {e}")
            traceback.print_exc()
    
    async def alert_expensive_call(self, model: str, cost: float):
        """Send alert for expensive API calls"""
        # Async call to external service
        pass

# Register
litellm.callbacks = [RobustLogger()]
```

---

## 6. CACHING MECHANISMS

### In-Memory Caching (Development/Testing)
```python
import litellm

# Enable simple in-memory cache
litellm.cache = litellm.InMemoryCache()

# First call - cached
response1 = litellm.completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "What is 2+2?"}]
)

# Second call - retrieved from cache (instant)
response2 = litellm.completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "What is 2+2?"}]
)

# responses are identical, but second is instant
assert response1 == response2
```

### Redis Caching (Production)
```python
import litellm

# Configure Redis cache
litellm.cache = litellm.RedisCache(
    host="localhost",
    port=6379,
    db=0
)

# Usage is identical to in-memory
response = litellm.completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "What is AI?"}]
)
```

### Cache Configuration in Proxy
```yaml
# config.yaml
cache:
  type: redis  # or memory
  # Redis config
  host: localhost
  port: 6379
  db: 0
  password: ${REDIS_PASSWORD}
  
  # Cache settings
  default_ttl: 3600  # 1 hour
  supported_call_types: ["completion", "embedding"]

litellm_settings:
  # ... other settings
```

### Disable Cache for Specific Calls
```python
import litellm

litellm.cache = litellm.InMemoryCache()

# This call will be cached
response1 = litellm.completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "What is 2+2?"}]
)

# This call bypasses cache
response2 = litellm.completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    cache={"no-cache": True}  # Skip cache
)

# Disable cache entirely
response3 = litellm.completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    cache={"no-store": True}  # Don't store in cache
)
```

### Proxy Cache Control
```yaml
# Disable caching for specific call types
litellm_settings:
  cache:
    supported_call_types: []  # Disable LLM caching, keep internal
```

### Cache Key Generation
Cache automatically includes:
- Model name
- Messages content
- Temperature and other parameters
- API version

Identical requests = identical cache keys = cache hit

---

## 7. FALLBACKS AND RETRIES

### Basic Retry Configuration
```python
from litellm import Router

# Router with retry policy
router = Router(
    model_list=[
        {
            "model_name": "gpt-4",
            "litellm_params": {
                "model": "openai/gpt-4o",
                "api_key": "${OPENAI_API_KEY}"
            }
        }
    ],
    num_retries=3,  # Retry failed requests 3 times
    request_timeout=30  # 30 second timeout before retry
)

response = router.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Fallback Configuration
```python
fallbacks = [
    {
        "gpt-4": ["gpt-3.5-turbo", "claude-3-opus"]  # Try in order
    }
]

# Fallbacks are sequential
# 1. Try gpt-4 (3 times)
# 2. If fails, try gpt-3.5-turbo (3 times)
# 3. If fails, try claude-3-opus (3 times)
# 4. If all fail, raise error

response = router.completion(
    model="gpt-4",
    messages=messages,
    fallbacks=fallbacks
)
```

### Fallback Types

#### Standard Fallbacks
```python
# Handle: rate limits, timeouts, 500 errors, connection issues
fallbacks = [{"primary-model": ["backup-model", "fallback-model"]}]
```

#### Content Policy Fallbacks
```python
# Triggered by ContentPolicyViolationError
content_policy_fallbacks = {
    "gpt-4": ["gpt-3.5-turbo"]  # Use cheaper model if content blocked
}
```

#### Context Window Fallbacks
```python
# Triggered by ContextWindowExceededError
context_fallbacks = {
    "gpt-3.5-turbo": ["gpt-4"]  # Use larger model if context exceeded
}
```

### Combined Fallback Configuration (config.yaml)
```yaml
model_list:
  - model_name: "my-model"
    litellm_params:
      model: "openai/gpt-4o"
    
litellm_settings:
  num_retries: 3
  request_timeout: 10
  retry_policy: "exponential_backoff"
  fallbacks: [{"my-model": ["gpt-3.5-turbo"]}]
  content_policy_fallbacks: [{"my-model": ["gpt-3.5-turbo-cheap"]}]
  context_window_fallbacks: [{"my-model": ["gpt-4-32k"]}]
  
  # Model cooldown
  allowed_fails: 3  # Fail >3 times in 1 min = cooldown
  cooldown_time: 30  # Cooldown for 30 seconds
```

### Retry Policy with Exponential Backoff
```python
# Automatic exponential backoff for RateLimitError
# Attempt 1: Retry immediately
# Attempt 2: Wait 1 second + random
# Attempt 3: Wait 2 seconds + random
# etc.

response = router.completion(
    model="gpt-4",
    messages=messages
    # Exponential backoff applied automatically
)
```

### Custom Retry Logic
```python
import litellm
from litellm import RetryPolicy

# Define which errors trigger retries
retry_policy = RetryPolicy(
    num_retries=3,
    retry_on_exceptions=[
        litellm.RateLimitError,
        litellm.ServiceUnavailableError,
        litellm.Timeout
    ]
)

response = litellm.completion(
    model="openai/gpt-4o",
    messages=messages,
    retry_policy=retry_policy
)
```

### Test Fallbacks
```python
# Mock testing without actual failures
response = router.completion(
    model="my-model",
    messages=messages,
    mock_testing_fallbacks=True  # Triggers fallback logic
)
```

### Per-Request Disable
```python
# Skip fallbacks for specific request
response = router.completion(
    model="my-model",
    messages=messages,
    disable_fallbacks=True  # Use only specified model
)
```

### Per-Model Configuration
```yaml
model_list:
  - model_name: "fast-model"
    litellm_params:
      model: "openai/gpt-3.5-turbo"
      temperature: 0.5  # Custom for fallback
    
    # Model-specific settings
    model_info:
      max_tokens: 1000
      rpm: 100  # 100 requests per minute
```

---

## 8. LOAD BALANCING

### Basic Load Balancing
```python
from litellm import Router

# Multiple deployments of same model
model_list = [
    {
        "model_name": "gpt-4",
        "litellm_params": {
            "model": "azure/gpt-4-us-east"
        }
    },
    {
        "model_name": "gpt-4",
        "litellm_params": {
            "model": "azure/gpt-4-us-west"
        }
    },
    {
        "model_name": "gpt-4",
        "litellm_params": {
            "model": "openai/gpt-4o"
        }
    }
]

router = Router(model_list=model_list)

# Router automatically load balances across instances
response = router.completion(
    model="gpt-4",
    messages=messages
    # Randomly or round-robin distributed across 3 deployments
)
```

### Load Balancing Strategies

#### Round-Robin (Default)
```yaml
router_settings:
  routing_strategy: "round_robin"  # Cycle through each deployment
```

#### Least-Busy
```yaml
router_settings:
  routing_strategy: "least_busy"  # Route to least loaded deployment
```

#### Latency-Based
```yaml
router_settings:
  routing_strategy: "latency_based"  # Route to fastest deployment
```

#### Random
```yaml
router_settings:
  routing_strategy: "random"  # Random selection
```

### Regional Load Balancing
```yaml
model_list:
  # US East
  - model_name: "gpt-4"
    litellm_params:
      model: "azure/gpt-4-us-east-1"
      api_base: "https://us-east-1.openai.azure.com"
  
  # US West
  - model_name: "gpt-4"
    litellm_params:
      model: "azure/gpt-4-us-west-1"
      api_base: "https://us-west-1.openai.azure.com"
  
  # Europe
  - model_name: "gpt-4"
    litellm_params:
      model: "azure/gpt-4-eu-west-1"
      api_base: "https://eu-west-1.openai.azure.com"
```

### Model Group Configuration
```yaml
# A model_group contains multiple deployments with same model_name
# They share: same fallbacks, same retries, same rate limits
# They're load balanced together

model_list:
  - model_name: "gpt-4"  # Group 1: 3 deployments
    litellm_params:
      model: "openai/gpt-4o"
  - model_name: "gpt-4"  # Same group
    litellm_params:
      model: "azure/gpt-4-deployment"
  - model_name: "gpt-4"  # Same group
    litellm_params:
      model: "bedrock/claude-3-opus"
  
  - model_name: "gpt-3.5"  # Group 2: different model_name
    litellm_params:
      model: "openai/gpt-3.5-turbo"
```

### Model Group Cooldown
```yaml
litellm_settings:
  allowed_fails: 3  # If model fails > 3 times in 1 minute
  cooldown_time: 30  # Cool down model for 30 seconds
  
  # After cooldown, model re-enters load balancing
```

---

## 9. RATE LIMITING HANDLING

### Per-API Key Rate Limits
```python
# Via /key/generate endpoint
key_response = requests.post(
    "http://localhost:4000/key/generate",
    json={
        "key_alias": "user-123",
        "tpm_limit": 60000,  # Tokens per minute
        "rpm_limit": 100,     # Requests per minute
        "max_budget": 50      # Monthly budget in USD
    },
    headers={"Authorization": f"Bearer {admin_key}"}
)

api_key = key_response.json()["key"]
```

### User Rate Limits
```python
# Set limits for internal user
user_response = requests.post(
    "http://localhost:4000/user/new",
    json={
        "user_id": "user-456",
        "tpm_limit": 120000,
        "rpm_limit": 200,
        "max_budget": 100
    },
    headers={"Authorization": f"Bearer {admin_key}"}
)
```

### Team Rate Limits
```python
# Set shared team budget
team_response = requests.post(
    "http://localhost:4000/team/new",
    json={
        "team_id": "team-789",
        "max_parallel_requests": 10,
        "tpm_limit": 500000,  # Shared across team
        "rpm_limit": 1000,
        "max_budget": 1000
    },
    headers={"Authorization": f"Bearer {admin_key}"}
)
```

### Model-Specific Rate Limits
```python
# Different limits per model on same key
key_config = {
    "key_alias": "user-multi",
    "model_rpm_limit": {
        "gpt-4": 50,           # 50 requests/min for GPT-4
        "gpt-3.5-turbo": 200   # 200 requests/min for GPT-3.5
    },
    "model_tpm_limit": {
        "gpt-4": 30000,        # 30K tokens/min for GPT-4
        "gpt-3.5-turbo": 60000 # 60K tokens/min for GPT-3.5
    }
}
```

### Parallel Request Limits
```python
# Limit concurrent requests
user_config = {
    "user_id": "user-concurrent",
    "max_parallel_requests": 5  # Only 5 concurrent requests
}
```

### Budget Configuration
```python
# Monthly budget with automatic reset
user_config = {
    "user_id": "user-monthly",
    "max_budget": 100,           # $100 USD
    "budget_duration": "30d"     # Reset every 30 days
}

# Daily budget
daily_budget = {
    "max_budget": 10,
    "budget_duration": "1d"      # Reset daily
}

# Hourly budget
hourly_budget = {
    "max_budget": 1,
    "budget_duration": "1h"      # Reset hourly
}
```

### Rate Limit Response Headers
```python
# Response includes rate limit info
headers = {
    "x-litellm-key-remaining-requests": "49",
    "x-litellm-key-remaining-requests-gpt-4": "49",
    "x-litellm-key-remaining-tokens": "119999",
    "x-litellm-key-remaining-tokens-gpt-4": "29999"
}

# Check if budget exceeded
if response.status_code == 429:
    # Rate limit exceeded
    error = response.json()
    print(f"Rate limited: {error['message']}")
```

### Enforce User Parameter (OpenAI Endpoint)
```yaml
litellm_settings:
  enforce_user_param: True  # Require 'user' in /chat/completions calls
```

```python
# Must include 'user' parameter
response = requests.post(
    "http://localhost:4000/chat/completions",
    json={
        "model": "gpt-4",
        "messages": [...],
        "user": "user-123"  # Required if enforce_user_param=True
    }
)
```

### Multi-Instance Rate Limiting
```yaml
# For distributed deployments
litellm_settings:
  EXPERIMENTAL_MULTI_INSTANCE_RATE_LIMITING: True
  redis_host: "redis.example.com"
  redis_port: 6379
  # Syncs rate limits across all proxy instances via Redis
```

### Custom Rate Limit Tier (Enterprise)
```python
# Define custom tier
tier_config = {
    "tier_name": "premium",
    "max_budget": 1000,
    "tpm_limit": 500000,
    "rpm_limit": 2000,
    "model_rpm_limit": {
        "gpt-4": 500,
        "gpt-3.5-turbo": 1000
    }
}

# Assign to key
key_config = {
    "key_alias": "premium-key",
    "tier": "premium"
}
```

---

## 10. COST TRACKING AND BUDGETS

### Automatic Cost Tracking
```python
# LiteLLM automatically tracks costs for known models
response = litellm.completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)

# Response includes cost
print(f"Cost: ${response.get('_response_ms', 0)}")

# Or via callback
def cost_callback(kwargs, response, start_time, end_time):
    cost = kwargs.get('response_cost', 0)
    tokens = response.usage.total_tokens
    print(f"Cost: ${cost} for {tokens} tokens")

litellm.success_callback = [cost_callback]
```

### Track Cost by User/Team
```python
# Include user identifier in request
response = requests.post(
    "http://localhost:4000/chat/completions",
    json={
        "model": "gpt-4",
        "messages": messages,
        "user": "user-456"  # Tracks cost to this user
    }
)

# Cost automatically attributed to user-456
```

### Metadata Tagging
```python
# Add custom tags for cost tracking
response = litellm.completion(
    model="openai/gpt-4o",
    messages=messages,
    metadata={
        "department": "engineering",
        "project": "chatbot",
        "team": "ai-platform"
    }
)

# Can query costs filtered by metadata
```

### View Spend Reports
```python
# Get daily spend by team
spend_report = requests.get(
    "http://localhost:4000/global/spend/report",
    params={
        "group_by": "team",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    },
    headers={"Authorization": f"Bearer {admin_key}"}
)

# Response: Daily breakdown by team
```

### Customer/End-User Budget
```python
# Track customer spend (no separate API key needed)
response = requests.post(
    "http://localhost:4000/chat/completions",
    json={
        "model": "gpt-4",
        "messages": messages,
        "user": "customer-123"  # customer_id
    }
)

# Cost tracked and attributed to customer-123
# Auto-upserts customer with new spend
```

### Budget Manager Class
```python
from litellm import BudgetManager

# Create budget manager
budget_mgr = BudgetManager()

# Set user budgets
budget_mgr.set_user_budget(
    user_id="user-123",
    budget=100,  # $100 USD
    time_period="30d"
)

# Track spending
budget_mgr.add_user_cost(
    user_id="user-123",
    cost=5.50
)

# Check remaining budget
remaining = budget_mgr.get_user_remaining_budget("user-123")
print(f"Remaining: ${remaining}")

# Alert on high spend
if remaining < 10:
    print("User budget low!")
```

### Model-Specific Budgets (Enterprise)
```python
# Different budget per model
key_config = {
    "key_alias": "advanced-user",
    "model_max_budget": {
        "gpt-4": {
            "budget_limit": 50,
            "time_period": "30d"
        },
        "gpt-3.5-turbo": {
            "budget_limit": 100,
            "time_period": "30d"
        }
    }
}

# Each model has independent budget
```

### Cost Tracking in config.yaml
```yaml
litellm_settings:
  # Database for persistent cost tracking
  database_url: "postgresql://user:pass@localhost/litellm"
  
  # Track all requests
  log_spend: True
  
  # Tags automatically added
  user_agent: True  # Track Claude Code, CLI tools, etc.
```

### View Cost by Model
```python
# LiteLLM maintains model pricing database
import litellm

model_info = litellm.get_model_cost_object("openai/gpt-4o")
# Returns: {
#   "input_cost_per_token": 0.000005,
#   "output_cost_per_token": 0.000015,
#   "tokens_per_minute": 500000,
#   ...
# }
```

### Custom Cost Calculation
```python
# For custom/imported models
response = litellm.completion(
    model="custom/my-model",
    messages=messages,
    litellm_cost_per_token={
        "input": 0.001,      # $0.001 per input token
        "output": 0.002      # $0.002 per output token
    }
)

# Cost calculated as:
# (input_tokens * 0.001) + (output_tokens * 0.002)
```

### Budget Enforcement
```yaml
# Budgets are enforced pre-request
# Request rejected if would exceed budget

litellm_settings:
  database_url: "postgresql://..."  # Required for budget enforcement
```

```python
# Check budget before calling
response = requests.post(
    "http://localhost:4000/chat/completions",
    json={
        "model": "gpt-4",
        "messages": messages,
        "user": "user-456"
    }
)

if response.status_code == 401:
    # Budget exceeded
    error = response.json()
    print(f"Budget error: {error['message']}")
```

---

## VISION/IMAGE PATTERNS

### Basic Vision Usage
```python
from litellm import completion

# Check if model supports vision
supports = completion.supports_vision(model="openai/gpt-4-vision-preview")

# Call with image
response = completion(
    model="openai/gpt-4-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/image.jpg"
                    }
                }
            ]
        }
    ]
)

print(response['choices'][0]['message']['content'])
```

### Base64 Encoded Images
```python
import base64

# Read image file
with open("image.jpg", "rb") as img_file:
    image_data = base64.b64encode(img_file.read()).decode("utf-8")

# Use in message
response = completion(
    model="openai/gpt-4-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        }
    ]
)
```

### Multiple Images
```python
response = completion(
    model="openai/gpt-4-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Compare these images"},
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/image1.jpg"}
                },
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/image2.jpg"}
                }
            ]
        }
    ]
)
```

### Proxy Vision Configuration
```yaml
model_list:
  - model_name: "gpt-4-vision"
    litellm_params:
      model: "openai/gpt-4-vision-preview"
    model_info:
      supports_vision: True  # Mark as vision-capable
```

---

## ADDITIONAL FEATURES

### Response Format (JSON)
```python
# Force JSON output
response = completion(
    model="openai/gpt-4o",
    messages=[
        {
            "role": "user",
            "content": "Return user data as JSON"
        }
    ],
    response_format={"type": "json_object"}
)

# Model returns valid JSON
```

### Temperature and Sampling
```python
response = completion(
    model="openai/gpt-4o",
    messages=messages,
    temperature=0.7,  # 0=deterministic, 2=very random
    top_p=0.9,        # Alternative to temperature
    top_k=40,         # Select from top K tokens
    frequency_penalty=0.5,  # Reduce repetition
    presence_penalty=0.5    # Encourage new topics
)
```

### Max Tokens Limit
```python
response = completion(
    model="openai/gpt-4o",
    messages=messages,
    max_tokens=500  # Limit response length
)
```

### Additional Kwargs
```python
# Pass provider-specific parameters
response = completion(
    model="anthropic/claude-3-opus",
    messages=messages,
    max_tokens=2000,
    temperature=0.5,
    # Provider-specific
    top_k=40,
    **{"custom_param": "value"}
)
```

### Provider API Version
```python
# Azure specific API version
response = completion(
    model="azure/gpt-4-deployment",
    messages=messages,
    api_version="2024-08-01-preview"
)
```

### Custom API Base
```python
# Override API endpoint
response = completion(
    model="anthropic/claude-3-opus",
    messages=messages,
    api_base="https://custom-endpoint.example.com"
)
```

---

## ERROR HANDLING

### Exception Types
```python
from litellm import (
    RateLimitError,
    APIError,
    APIConnectionError,
    Timeout,
    AuthenticationError,
    BadRequestError,
    ServiceUnavailableError,
    ContextWindowExceededError,
    ContentPolicyViolationError
)

try:
    response = completion(model="openai/gpt-4o", messages=messages)
except RateLimitError:
    print("Rate limited - implement backoff")
except ContextWindowExceededError:
    print("Context too large - use smaller model or summarize")
except AuthenticationError:
    print("Invalid API key")
except Timeout:
    print("Request timeout")
except ContentPolicyViolationError:
    print("Content policy violated")
except APIError as e:
    print(f"API error: {e}")
```

### OpenAI Compatibility
```python
# All exceptions inherit from OpenAI exception types
# Existing OpenAI error handlers work directly with LiteLLM

try:
    response = litellm.completion(...)
except OpenAI.APIError:  # Works with LiteLLM too
    pass
```

---

## COMPLETE EXAMPLE: PRODUCTION SETUP

```python
import asyncio
import json
import litellm
from litellm import Router, acompletion
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionLiteLLMSetup:
    def __init__(self):
        # Setup caching
        litellm.cache = litellm.RedisCache(
            host="localhost",
            port=6379
        )
        
        # Setup callbacks
        litellm.callbacks = [self.CostTracker(), self.ErrorHandler()]
        
        # Setup router with fallbacks
        self.router = Router(
            model_list=[
                {
                    "model_name": "primary",
                    "litellm_params": {
                        "model": "openai/gpt-4o",
                        "api_key": "${OPENAI_API_KEY}"
                    }
                },
                {
                    "model_name": "primary",
                    "litellm_params": {
                        "model": "azure/gpt-4-deployment",
                        "api_key": "${AZURE_API_KEY}",
                        "api_base": "${AZURE_API_BASE}"
                    }
                },
                {
                    "model_name": "fallback",
                    "litellm_params": {
                        "model": "anthropic/claude-3-opus-20250219",
                        "api_key": "${ANTHROPIC_API_KEY}"
                    }
                }
            ],
            num_retries=3,
            request_timeout=30,
            fallbacks=[{"primary": ["fallback"]}]
        )
    
    class CostTracker(litellm.CustomLogger):
        async def async_log_success_event(self, kwargs, response, start, end):
            cost = kwargs.get('response_cost', 0)
            model = kwargs.get('model')
            tokens = response.usage.total_tokens if hasattr(response, 'usage') else 0
            logger.info(f"Model: {model}, Cost: ${cost:.4f}, Tokens: {tokens}")
    
    class ErrorHandler(litellm.CustomLogger):
        async def async_log_failure_event(self, kwargs, response, start, end):
            logger.error(f"Failed request to {kwargs['model']}: {response}")
    
    async def complete(self, messages, model="primary", **kwargs):
        """Main completion method with all features"""
        try:
            response = await acompletion(
                model=model,
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 2000),
                timeout=30,
                # Caching happens automatically
            )
            return response['choices'][0]['message']['content']
        
        except litellm.RateLimitError:
            logger.warning("Rate limited, waiting...")
            await asyncio.sleep(60)
            return await self.complete(messages, model, **kwargs)
        
        except litellm.ContextWindowExceededError:
            logger.warning("Context too large, summarizing...")
            # Handle by summarizing or using larger model
            raise
        
        except Exception as e:
            logger.error(f"Completion failed: {e}")
            raise

# Usage
async def main():
    setup = ProductionLiteLLMSetup()
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ]
    
    response = await setup.complete(messages)
    print(response)

asyncio.run(main())
```



---

# API Reference

# LiteLLM Proxy - API Reference & Quick Start

## Table of Contents
1. [Quick Reference](#quick-reference)
2. [LLM API Endpoints](#llm-api-endpoints)
3. [Key Management API](#key-management-api)
4. [User Management API](#user-management-api)
5. [Team Management API](#team-management-api)
6. [Spend & Analytics API](#spend--analytics-api)
7. [Admin API](#admin-api)
8. [Health & Status API](#health--status-api)

---

## Quick Reference

### Base URL
```
http://localhost:4000
```

### Authentication
```
Authorization: Bearer sk-<your-key>
```

### Setup Commands

```bash
# 1. Install
pip install 'litellm[proxy]'

# 2. Create config.yaml
cat > config.yaml << 'CONFIGEOF'
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: sk-...

general_settings:
  master_key: sk-1234567890
  database_url: postgresql://...
CONFIGEOF

# 3. Set environment
export OPENAI_API_KEY=sk-...
export DATABASE_URL=postgresql://...
export LITELLM_MASTER_KEY=sk-1234567890

# 4. Run proxy (in shell, not here)
# litellm --config config.yaml

# 5. Generate API key in another shell
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{"models": ["gpt-4o"]}'
```

---

## LLM API Endpoints

### Chat Completions

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {"role": "system", "content": "You are helpful assistant"},
      {"role": "user", "content": "Hello"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 0.9
  }'
```

### Completions

```bash
curl -X POST http://localhost:4000/v1/completions \
  -H "Authorization: Bearer sk-your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "prompt": "Once upon a time",
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

### Embeddings

```bash
curl -X POST http://localhost:4000/v1/embeddings \
  -H "Authorization: Bearer sk-your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "text-embedding-3-small",
    "input": "The quick brown fox"
  }'
```

### List Models

```bash
curl http://localhost:4000/v1/models \
  -H "Authorization: Bearer sk-your-key"
```

### Get Model Info

```bash
curl 'http://localhost:4000/model/info?model=gpt-4o' \
  -H "Authorization: Bearer sk-your-key"
```

---

## Key Management API

### Generate Key

```bash
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "models": ["gpt-4o", "gpt-3.5-turbo"],
    "max_budget": 100.0,
    "budget_duration": "30d",
    "rpm_limit": 100,
    "tpm_limit": 50000
  }'
```

### Get Key Info

```bash
curl 'http://localhost:4000/key/info' \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{"key": "sk-abc123def456"}'
```

### Update Key

```bash
curl -X POST http://localhost:4000/key/update \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "sk-abc123def456",
    "max_budget": 200.0,
    "models": ["gpt-4o"]
  }'
```

### Delete Key

```bash
curl -X POST http://localhost:4000/key/delete \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{"key": "sk-abc123def456"}'
```

### List Keys

```bash
curl 'http://localhost:4000/keys' \
  -H "Authorization: Bearer sk-1234567890"
```

---

## User Management API

### Create User

```bash
curl -X POST http://localhost:4000/user/new \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "user_email": "alice@example.com",
    "role": "internal_user",
    "max_budget": 100.0,
    "budget_duration": "30d"
  }'
```

### Get User Info

```bash
curl 'http://localhost:4000/user/info' \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-123"}'
```

### Update User

```bash
curl -X POST http://localhost:4000/user/update \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "max_budget": 200.0
  }'
```

### Delete User

```bash
curl -X POST http://localhost:4000/user/delete \
  -H "Authorization: Bearer sk-1234567890" \
  -d '{"user_id": "user-123"}'
```

### List Users

```bash
curl 'http://localhost:4000/user/list' \
  -H "Authorization: Bearer sk-1234567890"
```

---

## Team Management API

### Create Team

```bash
curl -X POST http://localhost:4000/team/new \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "team-a",
    "team_alias": "Team A",
    "max_budget": 1000.0,
    "budget_duration": "30d"
  }'
```

### Get Team Info

```bash
curl 'http://localhost:4000/team/info' \
  -H "Authorization: Bearer sk-1234567890" \
  -d '{"team_id": "team-a"}'
```

### Update Team

```bash
curl -X POST http://localhost:4000/team/update \
  -H "Authorization: Bearer sk-1234567890" \
  -d '{
    "team_id": "team-a",
    "max_budget": 2000.0
  }'
```

### Add Team Member

```bash
curl -X POST http://localhost:4000/team/member/add \
  -H "Authorization: Bearer sk-1234567890" \
  -d '{
    "team_id": "team-a",
    "user_id": "user-123",
    "role": "user"
  }'
```

### List Team Members

```bash
curl 'http://localhost:4000/team/members?team_id=team-a' \
  -H "Authorization: Bearer sk-1234567890"
```

### List Teams

```bash
curl 'http://localhost:4000/team/list' \
  -H "Authorization: Bearer sk-1234567890"
```

---

## Spend & Analytics API

### Get Daily Spend

```bash
curl 'http://localhost:4000/spend/daily?start_date=2025-11-01&end_date=2025-11-30' \
  -H "Authorization: Bearer sk-1234567890"
```

### Get Spend by Key

```bash
curl 'http://localhost:4000/key/info' \
  -H "Authorization: Bearer sk-1234567890" \
  -d '{"key": "sk-abc123"}'
```

### Get Spend by User

```bash
curl 'http://localhost:4000/user/info' \
  -H "Authorization: Bearer sk-1234567890" \
  -d '{"user_id": "user-123"}'
```

### Get Spend by Team

```bash
curl 'http://localhost:4000/team/info' \
  -H "Authorization: Bearer sk-1234567890" \
  -d '{"team_id": "team-a"}'
```

---

## Admin API

### Get Proxy Config

```bash
curl 'http://localhost:4000/config' \
  -H "Authorization: Bearer sk-1234567890"
```

### Reload Config

```bash
curl -X POST http://localhost:4000/config/reload \
  -H "Authorization: Bearer sk-1234567890"
```

---

## Health & Status API

### Health Check

```bash
# Full health check
curl http://localhost:4000/health

# Liveness check
curl http://localhost:4000/health/liveliness

# Readiness check
curl http://localhost:4000/health/readiness

# Services health
curl http://localhost:4000/health/services
```

### Response Format

```json
{
  "status": "healthy",
  "timestamp": "2025-11-18T10:00:00Z",
  "models": {
    "gpt-4o": {
      "status": "healthy",
      "latency_ms": 145
    }
  }
}
```

---

## Error Codes

| Code | Error | Solution |
|------|-------|----------|
| 401 | Unauthorized | Check API key starts with 'sk-' |
| 403 | Forbidden | Check key budget and permissions |
| 404 | Not Found | Check model name and endpoint |
| 429 | Rate Limited | Wait or increase rate limits |
| 500 | Server Error | Check logs |
| 503 | Database Unavailable | Check database connection |

---

## Python SDK Examples

### Using LiteLLM SDK

```python
import litellm

litellm.api_base = "http://localhost:4000"
litellm.api_key = "sk-abc123"

response = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### Using OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-abc123",
    base_url="http://localhost:4000"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### Using LangChain

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key="sk-abc123",
    openai_api_base="http://localhost:4000"
)

response = llm.invoke("What is the capital of France?")
print(response.content)
```

---



---

# Proxy Server

# LiteLLM Proxy Server: Comprehensive Research Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation & Quick Start](#installation--quick-start)
3. [CLI Commands](#cli-commands)
4. [Configuration (config.yaml)](#configuration-configyaml)
5. [Virtual Keys & Authentication](#virtual-keys--authentication)
6. [Model Aliases & Routing](#model-aliases--routing)
7. [Spend Tracking & Budgets](#spend-tracking--budgets)
8. [Team & User Management](#team--user-management)
9. [Load Balancing](#load-balancing)
10. [Health Checks](#health-checks)
11. [Logging & Observability](#logging--observability)
12. [Docker Deployment](#docker-deployment)
13. [PostgreSQL Database Setup](#postgresql-database-setup)
14. [Production Best Practices](#production-best-practices)
15. [API Examples](#api-examples)

---

## Overview

### What is LiteLLM Proxy?

LiteLLM Proxy is an **OpenAI-compatible AI Gateway (LLM Proxy)** that provides a unified interface to call 100+ language models with advanced features including:

- **Multi-LLM Support**: Access 100+ models (OpenAI, Azure, Anthropic, Hugging Face, Bedrock, etc.)
- **Unified Interface**: OpenAI ChatCompletions format for all providers
- **Cost Tracking**: Automatic spend tracking per API key, user, team, and model
- **Authentication**: Virtual key management with SHA-256 hashing
- **Load Balancing**: Intelligent routing across multiple deployments
- **Rate Limiting**: RPM/TPM controls at multiple levels
- **Budget Management**: Hard caps and spend limits
- **Error Handling**: Automatic retries and fallbacks
- **Observability**: Integration with Langfuse, Helicone, Datadog, etc.
- **Admin Dashboard**: UI with SSO support
- **Caching**: Prompt caching support
- **Custom Plugins**: Request/response modification capabilities

### Key Statistics

- **Performance**: 8ms P95 latency at 1k RPS
- **Throughput**: 1.5k+ requests/second during load tests
- **Supported Models**: 100+ LLMs across all major providers
- **Database**: PostgreSQL for persistent storage
- **Caching**: Redis support for distributed deployments

---

## Installation & Quick Start

### Prerequisites

```bash
# Install Python 3.8+
python --version

# Install pip dependencies
pip install 'litellm[proxy]'
```

### Minimal Setup

```bash
# Start with a single model
litellm --model gpt-4o

# Start with debugging enabled
litellm --model huggingface/bigcode/starcoder --detailed_debug

# Test the proxy
litellm --test
```

The proxy runs on `http://0.0.0.0:4000` by default.

### Test a Request

```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Say this is a test"}]
  }'
```

---

## CLI Commands

### Installation & Help

```bash
# Install with proxy support
pip install 'litellm[proxy]'

# View available commands
litellm --help
```

### Starting the Proxy

```bash
# Basic startup with single model
litellm --model gpt-4o

# With configuration file
litellm --config /path/to/config.yaml

# With custom port and host
litellm --host 0.0.0.0 --port 8000

# With debugging
litellm --config config.yaml --detailed_debug

# With specified number of workers
litellm --config config.yaml --num_workers 4
```

### CLI Arguments Reference

| Argument | Description | Example |
|----------|-------------|---------|
| `--config` | Path to config.yaml file | `--config config.yaml` |
| `--model` | Model name/ID to use | `--model gpt-4o` |
| `--api_base` | API base URL | `--api_base https://api.openai.com/v1` |
| `--api_key` | API key | `--api_key sk-...` |
| `--alias` | Model alias | `--alias my-gpt4` |
| `--host` | Server host | `--host 0.0.0.0` |
| `--port` | Server port | `--port 8000` |
| `--num_workers` | Number of workers | `--num_workers 4` |
| `--timeout` | Request timeout (seconds) | `--timeout 60` |
| `--max_tokens` | Max tokens in response | `--max_tokens 2048` |
| `--temperature` | Model temperature | `--temperature 0.7` |
| `--debug` | Enable debug mode | `--debug` |
| `--detailed_debug` | Verbose debugging | `--detailed_debug` |
| `--test` | Test the proxy | `--test` |
| `--drop_params` | Drop unmapped params | `--drop_params` |
| `--run_hypercorn` | Use Hypercorn for HTTP/2 | `--run_hypercorn` |

### Environment Variables for CLI

```bash
# Set master key
export LITELLM_MASTER_KEY=sk-1234567890

# Set database URL
export DATABASE_URL=postgresql://user:password@localhost:5432/litellm

# Set log level
export LITELLM_LOG=INFO  # or DEBUG

# Set API keys
export OPENAI_API_KEY=sk-...
export AZURE_API_KEY=...
export ANTHROPIC_API_KEY=...
```

---

## Configuration (config.yaml)

### Basic Structure

```yaml
# Model list configuration
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_API_KEY}
  
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: gpt-3.5-turbo
      api_key: ${OPENAI_API_KEY}

# General proxy settings
general_settings:
  master_key: sk-1234567890
  database_url: postgresql://user:password@localhost:5432/litellm
  
# Router settings for load balancing
router_settings:
  routing_strategy: simple-shuffle
  num_retries: 2
  timeout: 30

# Global LiteLLM settings
litellm_settings:
  log: INFO
  num_retries: 2
```

### Complete Configuration Example

```yaml
# ==================== MODEL CONFIGURATION ====================
model_list:
  # OpenAI Models
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_API_KEY}
      api_base: https://api.openai.com/v1
      rpm: 200
      tpm: 90000
    model_info:
      description: "GPT-4 Omni Model"
      max_tokens: 128000
      mode: chat

  - model_name: gpt-3.5-turbo
    litellm_params:
      model: gpt-3.5-turbo
      api_key: ${OPENAI_API_KEY}
      rpm: 3500
      tpm: 90000

  # Azure OpenAI Models
  - model_name: azure-gpt-4
    litellm_params:
      model: azure/gpt-4
      api_base: ${AZURE_API_BASE}
      api_key: ${AZURE_API_KEY}
      api_version: 2024-02-15-preview
      rpm: 100
      tpm: 40000

  # Anthropic Models
  - model_name: claude-3-opus
    litellm_params:
      model: claude-3-5-sonnet-20241022
      api_key: ${ANTHROPIC_API_KEY}
      rpm: 50
      tpm: 40000

  # Load balancing multiple Azure deployments
  - model_name: gpt-4-prod-1
    litellm_params:
      model: azure/gpt-4
      api_base: ${AZURE_API_BASE_1}
      api_key: ${AZURE_API_KEY_1}
      rpm: 100

  - model_name: gpt-4-prod-2
    litellm_params:
      model: azure/gpt-4
      api_base: ${AZURE_API_BASE_2}
      api_key: ${AZURE_API_KEY_2}
      rpm: 100

# ==================== ROUTING & LOAD BALANCING ====================
router_settings:
  # Routing strategy: simple-shuffle, least-busy, usage-based-routing, latency-based-routing, cost-based-routing
  routing_strategy: simple-shuffle
  
  # Number of retries on failure
  num_retries: 2
  
  # Request timeout in seconds
  timeout: 30
  
  # Model aliases for routing
  model_group_alias:
    "gpt-4": "gpt-4o"
    "gpt-4-turbo": "gpt-4o"
  
  # Fallback models on failure
  fallbacks: 
    - "gpt-4o": ["gpt-3.5-turbo"]
  
  # Context window fallbacks
  context_window_fallbacks:
    - "gpt-4o": ["gpt-4o"]
    - "gpt-3.5-turbo": ["gpt-3.5-turbo-16k"]
  
  # Content policy fallbacks
  content_policy_fallbacks:
    - "gpt-4o": ["gpt-3.5-turbo"]
  
  # Redis for distributed deployments
  redis_host: ${REDIS_HOST}
  redis_password: ${REDIS_PASSWORD}
  redis_port: 6379

# ==================== GENERAL SETTINGS ====================
general_settings:
  # Master key for admin operations (must start with 'sk-')
  master_key: ${LITELLM_MASTER_KEY}
  
  # Database URL (PostgreSQL)
  database_url: ${DATABASE_URL}
  
  # Database connection pool settings
  database_connection_pool_limit: 10
  database_connection_timeout: 60
  
  # Allow requests if database is unavailable (graceful degradation)
  allow_requests_on_db_unavailable: true
  
  # Max parallel requests for the entire proxy
  max_parallel_requests: 10000
  
  # Health checks
  background_health_checks: true
  health_check_interval: 300
  
  # Alerting (supports: slack, email)
  alerting: ["slack"]
  
  # Store models in database for UI
  store_model_in_db: true
  
  # Disable error logs in production
  disable_error_logs: false
  
  # Batch write spend updates (seconds)
  proxy_batch_write_at: 60
  
  # Custom authentication
  # custom_auth: path.to.custom_auth_function
  
  # Encryption salt for API keys
  litellm_salt_key: ${LITELLM_SALT_KEY}
  
  # Default budgets for new internal users
  max_internal_user_budget: 100.0
  internal_user_budget_duration: "30d"

# ==================== LITELLM SETTINGS ====================
litellm_settings:
  # Logging level: DEBUG, INFO, WARNING, ERROR
  log: INFO
  
  # Global number of retries
  num_retries: 2
  
  # Global retry policy
  retry_policy: ExponentialBackoffRetry
  
  # Fallbacks (applies to all models not explicitly configured)
  fallbacks:
    - "gpt-4o": ["gpt-3.5-turbo"]
    - "gpt-3.5-turbo": ["gpt-4o"]
  
  # Cache settings
  cache: true
  cache_type: redis
  cache_host: ${REDIS_HOST}
  cache_port: 6379
  cache_password: ${REDIS_PASSWORD}
  
  # Request timeout
  request_timeout: 60
  
  # Success and failure callbacks for observability
  success_callback: ["langfuse", "helicone"]
  failure_callback: ["langfuse", "helicone"]
  
  # Batch mode for better performance
  batch_mode: true
  
  # Track usage metadata
  track_cost: true

# ==================== ENVIRONMENT VARIABLES ====================
environment_variables:
  OPENAI_API_KEY: ${OPENAI_API_KEY}
  AZURE_API_BASE: ${AZURE_API_BASE}
  AZURE_API_KEY: ${AZURE_API_KEY}
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
  LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY}
  LANGFUSE_SECRET_KEY: ${LANGFUSE_SECRET_KEY}
  HELICONE_API_KEY: ${HELICONE_API_KEY}
  REDIS_HOST: redis
  REDIS_PASSWORD: ${REDIS_PASSWORD}

# ==================== FILE INCLUDES ====================
include:
  - models_config.yaml
  - team_models.yaml
```

### Configuration by File Management

Create separate config files and include them:

```yaml
# main_config.yaml
include:
  - models/openai_models.yaml
  - models/azure_models.yaml
  - models/anthropic_models.yaml
  - teams/team_a_models.yaml

general_settings:
  master_key: ${LITELLM_MASTER_KEY}
  database_url: ${DATABASE_URL}
```

```yaml
# models/openai_models.yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_API_KEY}
```

---

## Virtual Keys & Authentication

### Overview

Virtual keys are bearer tokens stored in the database that identify and authorize requests to the proxy. They require PostgreSQL and a master key to manage.

### Setup Requirements

```bash
# Set environment variables
export DATABASE_URL=postgresql://user:password@localhost:5432/litellm
export LITELLM_MASTER_KEY=sk-1234567890  # Must start with 'sk-'
export LITELLM_SALT_KEY=sk-salt-key     # For encryption
```

### config.yaml Setup

```yaml
general_settings:
  master_key: ${LITELLM_MASTER_KEY}
  database_url: ${DATABASE_URL}
  store_model_in_db: true
```

### Generate Virtual Keys via API

```bash
# Generate a new key
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "models": ["gpt-4o", "gpt-3.5-turbo"],
    "duration": "30d",
    "max_budget": 100.0
  }'

# Response
{
  "key": "sk-skdsjkdsjkd",
  "expires": "2025-01-18",
  "models": ["gpt-4o", "gpt-3.5-turbo"],
  "max_budget": 100.0
}
```

### Get Key Information

```bash
# View key spend and info
curl -X GET http://localhost:4000/key/info \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{"key": "sk-skdsjkdsjkd"}'

# Response
{
  "key": "sk-skdsjkdsjkd",
  "spend": 23.45,
  "max_budget": 100.0,
  "models": ["gpt-4o", "gpt-3.5-turbo"],
  "created_at": "2025-11-18T10:00:00Z"
}
```

### Update or Delete Keys

```bash
# Update a key
curl -X POST http://localhost:4000/key/update \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "sk-skdsjkdsjkd",
    "max_budget": 200.0,
    "models": ["gpt-4o"]
  }'

# Delete a key
curl -X POST http://localhost:4000/key/delete \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{"key": "sk-skdsjkdsjkd"}'
```

### Key Features

- **SHA-256 Hashing**: Keys stored securely in database
- **Multi-tier Caching**: In-memory → Redis → PostgreSQL
- **Key Rotation**: Automatic rotation based on time intervals
- **Custom Headers**: Configure custom key header (default: Authorization)
- **Association**: Keys can be linked to users, teams, or both

---

## Model Aliases & Routing

### Model Group Aliases

```yaml
router_settings:
  model_group_alias:
    # All gpt-4 requests → gpt-4o
    "gpt-4": "gpt-4o"
    
    # All gpt-4-turbo requests → gpt-4o
    "gpt-4-turbo": "gpt-4o"
    
    # Complex aliases with options
    "gpt-4-legacy":
      model: "gpt-3.5-turbo"
      hidden: true  # Don't show in /v1/models
```

### Routing Strategies

```yaml
router_settings:
  # Option 1: Simple-Shuffle (Default, Best Performance)
  # Randomly distributes requests with weighting
  routing_strategy: simple-shuffle
  
  # Option 2: Least-Busy
  # Routes to deployment with fewest active requests
  routing_strategy: least-busy
  
  # Option 3: Usage-Based-Routing
  # Routes based on token usage/limits (not recommended for production)
  routing_strategy: usage-based-routing
  
  # Option 4: Latency-Based-Routing
  # Routes to fastest-responding deployment
  routing_strategy: latency-based-routing
  
  # Option 5: Cost-Based-Routing
  # Routes to lowest cost provider
  routing_strategy: cost-based-routing
```

### Load Balancing Multiple Deployments

```yaml
model_list:
  # Load balance across multiple Azure deployments
  - model_name: gpt-4-prod
    litellm_params:
      model: azure/gpt-4
      api_base: ${AZURE_API_BASE_1}
      api_key: ${AZURE_API_KEY_1}
      rpm: 100
      tpm: 40000

  - model_name: gpt-4-prod
    litellm_params:
      model: azure/gpt-4
      api_base: ${AZURE_API_BASE_2}
      api_key: ${AZURE_API_KEY_2}
      rpm: 100
      tpm: 40000

  - model_name: gpt-4-prod
    litellm_params:
      model: azure/gpt-4
      api_base: ${AZURE_API_BASE_3}
      api_key: ${AZURE_API_KEY_3}
      rpm: 100
      tpm: 40000
```

### Team-Based Model Routing

```bash
# Create a team with model aliases
curl -X POST http://localhost:4000/team/new \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "team-a",
    "team_alias": "Team A",
    "model_aliases": {
      "gpt-4": "gpt-4o",
      "gpt-3.5": "gpt-3.5-turbo"
    }
  }'
```

---

## Spend Tracking & Budgets

### Automatic Cost Tracking

LiteLLM automatically tracks spend for all known models with built-in pricing data.

### Key-Level Budgets

```bash
# Generate a key with budget
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "models": ["gpt-4o"],
    "max_budget": 100.0,
    "budget_duration": "30d"
  }'
```

### View Spend Information

```bash
# Get key spend
curl http://localhost:4000/key/info \
  -H "Authorization: Bearer sk-1234567890" \
  -d '{"key": "sk-skdsjkdsjkd"}'

# Get user spend
curl http://localhost:4000/user/info \
  -H "Authorization: Bearer sk-1234567890" \
  -d '{"user_id": "user123"}'

# Get team spend
curl http://localhost:4000/team/info \
  -H "Authorization: Bearer sk-1234567890" \
  -d '{"team_id": "team-a"}'

# Get daily spend breakdown
curl 'http://localhost:4000/spend/daily?start_date=2025-11-01&end_date=2025-11-30' \
  -H "Authorization: Bearer sk-1234567890"
```

### Budget Types

| Budget Type | Scope | Use Case |
|------------|-------|----------|
| Key-Level | Single API key | Individual app/service limits |
| User-Level | Single user account | Internal user budgets |
| Team-Level | Team of users | Team/department budgets |
| Tag-Based | Requests with tags | Cost center tracking |
| Customer/End-User | Customer accounts | Per-customer billing |
| Provider | LLM provider | Provider-level caps |
| Model | Specific model | Model-level budgets |

### Tag-Based Budget Tracking

```bash
# Create spend tracking by tags
curl -X POST http://localhost:4000/spend/logs \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "spend_logs_metadata": {
      "cost_center": "engineering",
      "project": "recommendation-engine",
      "customer": "customer-123"
    }
  }'
```

---

## Team & User Management

### User Management Hierarchy

```
Organization
  ├── Team A
  │   ├── User 1 (Admin)
  │   ├── User 2 (Member)
  │   └── API Keys
  └── Team B
      ├── User 3 (Admin)
      └── API Keys
```

### User Roles

**Proxy-Wide Roles:**
- **PROXY_ADMIN**: Full control over entire proxy
- **PROXY_ADMIN_VIEWER**: Read-only access to all proxy data
- **INTERNAL_USER**: Can create keys, view own spend

**Team-Specific Roles:**
- **TEAM_ADMIN**: Can manage team members and settings
- **TEAM_USER**: Can view own spend, cannot create/delete keys (configurable)

### Create a User

```bash
curl -X POST http://localhost:4000/user/new \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "user_alias": "alice@company.com",
    "user_email": "alice@company.com",
    "role": "internal_user",
    "teams": ["team-a"],
    "max_budget": 100.0,
    "budget_duration": "30d"
  }'
```

### Create a Team

```bash
curl -X POST http://localhost:4000/team/new \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "team-a",
    "team_alias": "Team A",
    "max_budget": 1000.0,
    "budget_duration": "30d",
    "tpm_limit": 100000,
    "rpm_limit": 1000
  }'
```

### Add User to Team

```bash
curl -X POST http://localhost:4000/team/member/add \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "team-a",
    "user_id": "user-123",
    "role": "user",
    "member_budget": 100.0
  }'
```

### List Teams and Users

```bash
# List all teams
curl http://localhost:4000/team/list \
  -H "Authorization: Bearer sk-1234567890"

# List team members
curl 'http://localhost:4000/team/members?team_id=team-a' \
  -H "Authorization: Bearer sk-1234567890"

# List users
curl http://localhost:4000/user/list \
  -H "Authorization: Bearer sk-1234567890"
```

### Update Team Budget

```bash
curl -X POST http://localhost:4000/team/update \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "team-a",
    "max_budget": 2000.0,
    "budget_duration": "30d"
  }'
```

### CLI User Management

```bash
# Install CLI
pip install litellm-proxy-cli

# List users
litellm-proxy users list --url http://localhost:4000 --key sk-1234567890

# Create user
litellm-proxy users create \
  --url http://localhost:4000 \
  --key sk-1234567890 \
  --email user@example.com \
  --role internal_user \
  --alias "Alice" \
  --team team1 \
  --max-budget 100.0

# Get user
litellm-proxy users get --id user-123

# Delete user
litellm-proxy users delete --id user-123
```

---

## Load Balancing

### Routing Strategies

```yaml
router_settings:
  routing_strategy: simple-shuffle  # Recommended for production
  num_retries: 2
  timeout: 30
```

### Load Balancing Example

```yaml
model_list:
  # Define same model multiple times for load balancing
  - model_name: gpt-4-prod
    litellm_params:
      model: azure/gpt-4
      api_base: ${AZURE_BASE_1}
      api_key: ${AZURE_KEY_1}
      rpm: 100

  - model_name: gpt-4-prod
    litellm_params:
      model: azure/gpt-4
      api_base: ${AZURE_BASE_2}
      api_key: ${AZURE_KEY_2}
      rpm: 100

  - model_name: gpt-4-prod
    litellm_params:
      model: azure/gpt-4
      api_base: ${AZURE_BASE_3}
      api_key: ${AZURE_KEY_3}
      rpm: 100

router_settings:
  routing_strategy: simple-shuffle
  num_retries: 2
  timeout: 30
```

### Rate Limiting with Load Balancing

```yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_KEY}
      rpm: 200     # 200 requests per minute
      tpm: 90000   # 90k tokens per minute
```

### Fallbacks and Cooldowns

```yaml
litellm_settings:
  # Model fallbacks on failure
  fallbacks:
    - "gpt-4o": ["gpt-3.5-turbo"]
    - "gpt-3.5-turbo": ["gpt-4o"]
  
  # Context window fallbacks
  context_window_fallbacks:
    - "gpt-4o": ["gpt-4o"]
    - "gpt-3.5-turbo": ["gpt-3.5-turbo-16k"]

model_list:
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_KEY}
    model_info:
      allowed_fails: 3  # Cooldown after 3 failures/minute
      cooldown_time: 300  # 5 minute cooldown
```

### Redis for Distributed Load Balancing

```yaml
router_settings:
  redis_host: redis.example.com
  redis_password: ${REDIS_PASSWORD}
  redis_port: 6379
  redis_ttl: 300

general_settings:
  database_url: postgresql://...
```

---

## Health Checks

### Health Check Endpoints

```bash
# Full health check (makes API calls)
curl http://localhost:4000/health

# Readiness check (includes database check)
curl http://localhost:4000/health/readiness

# Liveness check (basic alive check)
curl http://localhost:4000/health/liveliness

# Service integrations health
curl http://localhost:4000/health/services

# Shared health status across pods
curl http://localhost:4000/health/shared-status
```

### Background Health Checks Configuration

```yaml
general_settings:
  background_health_checks: true
  health_check_interval: 300  # Check every 5 minutes
  health_check_timeout: 60    # 60 second timeout

model_list:
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_KEY}
    model_info:
      disable_background_health_check: false
      health_check_timeout: 30  # Override for this model
      mode: chat
```

### Custom Health Check Prompt

```bash
export DEFAULT_HEALTH_CHECK_PROMPT="What is 2+2?"
litellm --config config.yaml
```

### Health Check Privacy

```yaml
general_settings:
  health_check_details: false  # Hide URLs and error details in responses
```

---

## Logging & Observability

### Supported Integrations

**Observability Platforms:**
- Langfuse
- Helicone
- Datadog
- Sentry
- Honeycomb
- OpenTelemetry

**Cloud Storage:**
- AWS S3
- Google Cloud Storage
- Azure Blob Storage

**Queues:**
- AWS SQS
- Google Cloud PubSub

**Databases:**
- DynamoDB

**Analytics:**
- Langsmith
- MLflow
- Deepeval
- Lunary
- Arize AI
- Langtrace
- Galileo
- Athina

### Configuration Example

```yaml
litellm_settings:
  # Callbacks on success
  success_callback: ["langfuse", "helicone", "datadog"]
  
  # Callbacks on failure
  failure_callback: ["langfuse", "helicone", "sentry"]
  
  # Message redaction for PII
  redact_message_input: false
  redact_message_output: false

environment_variables:
  LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY}
  LANGFUSE_SECRET_KEY: ${LANGFUSE_SECRET_KEY}
  LANGFUSE_HOST: https://api.langfuse.com
  HELICONE_API_KEY: ${HELICONE_API_KEY}
  DATADOG_API_KEY: ${DATADOG_API_KEY}
```

### Langfuse Integration

```yaml
litellm_settings:
  success_callback: ["langfuse"]
  failure_callback: ["langfuse"]

environment_variables:
  LANGFUSE_PUBLIC_KEY: pk-lf-xxx
  LANGFUSE_SECRET_KEY: sk-lf-xxx
  LANGFUSE_HOST: https://api.langfuse.com
```

### Helicone Integration

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_API_KEY}
      # Add Helicone header
      headers:
        "helicone-auth": "Bearer ${HELICONE_API_KEY}"

litellm_settings:
  success_callback: ["helicone"]

environment_variables:
  HELICONE_API_KEY: ${HELICONE_API_KEY}
```

### S3 Logging

```yaml
litellm_settings:
  success_callback: ["s3"]

environment_variables:
  AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
  AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
  AWS_REGION_NAME: us-east-1
  S3_BUCKET_NAME: litellm-logs
```

### Logging Levels

```bash
# Enable debug logging
export LITELLM_LOG=DEBUG
litellm --config config.yaml

# Info level (default)
export LITELLM_LOG=INFO
litellm --config config.yaml

# Suppress logs
export LITELLM_LOG=WARNING
litellm --config config.yaml
```

---

## Docker Deployment

### Basic Docker Setup

```bash
# Pull official image
docker pull ghcr.io/berriai/litellm:main-stable

# Run with config file
docker run -d \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -e LITELLM_MASTER_KEY=sk-1234567890 \
  -e OPENAI_API_KEY=sk-... \
  -p 4000:4000 \
  --name litellm \
  ghcr.io/berriai/litellm:main-stable \
  --config /app/config.yaml
```

### Docker with Database Support

```bash
# Use database-optimized image
docker run -d \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -e LITELLM_MASTER_KEY=sk-1234567890 \
  -e DATABASE_URL=postgresql://user:password@postgres:5432/litellm \
  -e OPENAI_API_KEY=sk-... \
  -p 4000:4000 \
  --name litellm \
  ghcr.io/berriai/litellm-database:main-stable \
  --config /app/config.yaml
```

### Docker Compose Setup

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: litellm
      POSTGRES_USER: litellm
      POSTGRES_PASSWORD: litellm_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U litellm"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache (optional, for distributed deployments)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # LiteLLM Proxy
  litellm:
    image: ghcr.io/berriai/litellm-database:main-stable
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY:-sk-1234567890}
      LITELLM_SALT_KEY: ${LITELLM_SALT_KEY:-sk-salt-1234567890}
      DATABASE_URL: postgresql://litellm:litellm_password@postgres:5432/litellm
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      AZURE_API_KEY: ${AZURE_API_KEY}
      AZURE_API_BASE: ${AZURE_API_BASE}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      REDIS_HOST: redis
      REDIS_PORT: 6379
      LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY}
      LANGFUSE_SECRET_KEY: ${LANGFUSE_SECRET_KEY}
      HELICONE_API_KEY: ${HELICONE_API_KEY}
      LITELLM_LOG: INFO
    ports:
      - "4000:4000"
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./litellm_logs:/app/logs
    command: >
      litellm --config /app/config.yaml
      --host 0.0.0.0
      --port 4000
      --num_workers 4
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  postgres_data:
```

### Run Docker Compose

```bash
# Create environment file
cat > .env << EOF
LITELLM_MASTER_KEY=sk-1234567890
LITELLM_SALT_KEY=sk-salt-1234567890
OPENAI_API_KEY=sk-...
AZURE_API_KEY=...
AZURE_API_BASE=...
ANTHROPIC_API_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
HELICONE_API_KEY=...


---

# Configuration Examples

# LiteLLM Proxy - Configuration Examples

## Table of Contents
1. [Basic Configuration](#basic-configuration)
2. [Multi-Provider Setup](#multi-provider-setup)
3. [Azure-Focused Setup](#azure-focused-setup)
4. [Advanced Routing](#advanced-routing)
5. [High-Availability Setup](#high-availability-setup)
6. [Cost Optimization Setup](#cost-optimization-setup)
7. [Enterprise Setup](#enterprise-setup)

---

## Basic Configuration

### Minimal config.yaml

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_API_KEY}

general_settings:
  master_key: sk-1234567890
  database_url: ${DATABASE_URL}
```

### Startup Command

```bash
# Install
pip install 'litellm[proxy]'

# Run with config
export OPENAI_API_KEY=sk-...
export DATABASE_URL=postgresql://user:pass@localhost/litellm
export LITELLM_MASTER_KEY=sk-1234567890
litellm --config config.yaml
```

---

## Multi-Provider Setup

### Complete Multi-Provider Configuration

```yaml
model_list:
  # OpenAI Models
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_API_KEY}
      rpm: 200
      tpm: 90000

  - model_name: gpt-3.5-turbo
    litellm_params:
      model: gpt-3.5-turbo
      api_key: ${OPENAI_API_KEY}
      rpm: 3500
      tpm: 90000

  # Anthropic Models
  - model_name: claude-3-5-sonnet
    litellm_params:
      model: claude-3-5-sonnet-20241022
      api_key: ${ANTHROPIC_API_KEY}
      rpm: 50
      tpm: 40000

  # Azure OpenAI Models
  - model_name: azure-gpt-4
    litellm_params:
      model: azure/gpt-4
      api_base: ${AZURE_API_BASE}
      api_key: ${AZURE_API_KEY}
      api_version: 2024-02-15-preview
      rpm: 100
      tpm: 40000

  # Hugging Face Models
  - model_name: mistral-7b
    litellm_params:
      model: huggingface/mistralai/Mistral-7B-Instruct-v0.1
      api_key: ${HUGGINGFACE_API_KEY}
      api_base: https://api-inference.huggingface.co/models
      rpm: 100
      tpm: 20000

  # AWS Bedrock
  - model_name: bedrock-claude
    litellm_params:
      model: bedrock/anthropic.claude-3-sonnet-20240229-v1:0
      aws_access_key_id: ${AWS_ACCESS_KEY_ID}
      aws_secret_access_key: ${AWS_SECRET_ACCESS_KEY}
      aws_region_name: us-east-1

  # Google Vertex AI
  - model_name: vertex-gemini
    litellm_params:
      model: vertex_ai/gemini-pro
      project_id: ${GOOGLE_PROJECT_ID}
      location: us-central1

router_settings:
  routing_strategy: simple-shuffle
  num_retries: 2
  timeout: 30
  
  # Model aliases
  model_group_alias:
    "gpt-4": "gpt-4o"
    "gpt-4-turbo": "gpt-4o"
    "claude": "claude-3-5-sonnet"

general_settings:
  master_key: ${LITELLM_MASTER_KEY}
  database_url: ${DATABASE_URL}
  background_health_checks: true
  health_check_interval: 300

litellm_settings:
  log: INFO
  num_retries: 2
  fallbacks:
    - "gpt-4o": ["gpt-3.5-turbo", "azure-gpt-4"]
    - "claude-3-5-sonnet": ["gpt-4o"]

environment_variables:
  OPENAI_API_KEY: ${OPENAI_API_KEY}
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
  AZURE_API_BASE: ${AZURE_API_BASE}
  AZURE_API_KEY: ${AZURE_API_KEY}
  HUGGINGFACE_API_KEY: ${HUGGINGFACE_API_KEY}
  AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
  AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
  GOOGLE_PROJECT_ID: ${GOOGLE_PROJECT_ID}
```

---

## Azure-Focused Setup

### Multiple Azure Deployments with Load Balancing

```yaml
model_list:
  # GPT-4 Turbo across 3 Azure regions
  - model_name: gpt-4-turbo-prod
    litellm_params:
      model: azure/gpt-4-turbo
      api_base: https://eastus-gpt4.openai.azure.com/
      api_key: ${AZURE_EASTUS_KEY}
      api_version: 2024-02-15-preview
      rpm: 150
      tpm: 40000

  - model_name: gpt-4-turbo-prod
    litellm_params:
      model: azure/gpt-4-turbo
      api_base: https://westeurope-gpt4.openai.azure.com/
      api_key: ${AZURE_WESTEU_KEY}
      api_version: 2024-02-15-preview
      rpm: 150
      tpm: 40000

  - model_name: gpt-4-turbo-prod
    litellm_params:
      model: azure/gpt-4-turbo
      api_base: https://uksouth-gpt4.openai.azure.com/
      api_key: ${AZURE_UKSOUTH_KEY}
      api_version: 2024-02-15-preview
      rpm: 150
      tpm: 40000

  # GPT-35-Turbo across 2 regions
  - model_name: gpt-35-turbo
    litellm_params:
      model: azure/gpt-35-turbo
      api_base: https://eastus-gpt35.openai.azure.com/
      api_key: ${AZURE_EASTUS_KEY}
      api_version: 2024-02-15-preview
      rpm: 500
      tpm: 90000

  - model_name: gpt-35-turbo
    litellm_params:
      model: azure/gpt-35-turbo
      api_base: https://westeurope-gpt35.openai.azure.com/
      api_key: ${AZURE_WESTEU_KEY}
      api_version: 2024-02-15-preview
      rpm: 500
      tpm: 90000

router_settings:
  routing_strategy: latency-based-routing
  num_retries: 2
  timeout: 45
  
  # Fallback from GPT-4 to GPT-3.5 if needed
  fallbacks:
    - "gpt-4-turbo-prod": ["gpt-35-turbo"]

general_settings:
  master_key: ${LITELLM_MASTER_KEY}
  database_url: ${DATABASE_URL}
  background_health_checks: true
  health_check_interval: 300

litellm_settings:
  log: INFO
  num_retries: 3
  
environment_variables:
  AZURE_EASTUS_KEY: ${AZURE_EASTUS_KEY}
  AZURE_WESTEU_KEY: ${AZURE_WESTEU_KEY}
  AZURE_UKSOUTH_KEY: ${AZURE_UKSOUTH_KEY}
```

### Docker Compose for Azure Deployment

```bash
# .env file
LITELLM_MASTER_KEY=sk-1234567890
DATABASE_URL=postgresql://litellm:password@postgres:5432/litellm
AZURE_EASTUS_KEY=...
AZURE_WESTEU_KEY=...
AZURE_UKSOUTH_KEY=...
LITELLM_LOG=INFO
```

---

## Advanced Routing

### Intelligent Routing Based on Model Capabilities

```yaml
model_list:
  # High-performance models
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_API_KEY}
    model_info:
      description: "Best quality, highest cost"
      max_tokens: 128000
      supports_vision: true

  # Balance cost vs quality
  - model_name: gpt-4-turbo
    litellm_params:
      model: gpt-4-turbo-preview
      api_key: ${OPENAI_API_KEY}
    model_info:
      description: "Good quality, moderate cost"
      max_tokens: 128000

  # Budget-friendly option
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: gpt-3.5-turbo
      api_key: ${OPENAI_API_KEY}
      rpm: 3500
      tpm: 90000
    model_info:
      description: "Lower cost, good for simple tasks"
      max_tokens: 16384

  # Specialized models
  - model_name: claude-3-opus
    litellm_params:
      model: claude-3-opus-20240229
      api_key: ${ANTHROPIC_API_KEY}
    model_info:
      description: "Best for reasoning and analysis"
      max_tokens: 200000
      supports_vision: true

router_settings:
  routing_strategy: least-busy
  num_retries: 2
  timeout: 30
  
  # Model aliases for routing based on user needs
  model_group_alias:
    # Route all generic requests to gpt-4o
    "best": "gpt-4o"
    
    # Route budget requests to gpt-3.5
    "budget": "gpt-3.5-turbo"
    
    # Route analysis to Claude
    "analyze": "claude-3-opus"
    
    # Route fallbacks
    "gpt-4": "gpt-4o"
  
  # Fallback chain: GPT-4 → GPT-3.5 → Claude
  fallbacks:
    - "gpt-4o": ["gpt-4-turbo", "gpt-3.5-turbo", "claude-3-opus"]
    - "gpt-4-turbo": ["gpt-3.5-turbo", "claude-3-opus"]
    - "gpt-3.5-turbo": ["claude-3-opus"]
  
  # Context window fallbacks
  context_window_fallbacks:
    - "gpt-3.5-turbo": ["gpt-4-turbo", "gpt-4o"]
    - "gpt-4-turbo": ["gpt-4o"]
  
  # Content policy fallbacks
  content_policy_fallbacks:
    - "gpt-4o": ["gpt-3.5-turbo"]

general_settings:
  master_key: ${LITELLM_MASTER_KEY}
  database_url: ${DATABASE_URL}

litellm_settings:
  log: INFO
```

---

## High-Availability Setup

### Multi-Region with Redis and Database Failover

```yaml
model_list:
  # Primary region
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_API_KEY_PRIMARY}
      rpm: 200
      tpm: 90000

  # Secondary region
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_API_KEY_SECONDARY}
      rpm: 200
      tpm: 90000

  # Tertiary region
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_API_KEY_TERTIARY}
      rpm: 200
      tpm: 90000

router_settings:
  routing_strategy: latency-based-routing
  num_retries: 3
  timeout: 30
  
  # Shared state across regions via Redis
  redis_host: ${REDIS_HOST}
  redis_password: ${REDIS_PASSWORD}
  redis_port: 6379
  redis_ttl: 300

general_settings:
  master_key: ${LITELLM_MASTER_KEY}
  database_url: ${DATABASE_URL}
  
  # Graceful degradation
  allow_requests_on_db_unavailable: true
  
  # Health checks
  background_health_checks: true
  health_check_interval: 60
  
  # Batch writes for consistency
  proxy_batch_write_at: 30

litellm_settings:
  log: INFO
  
  # Aggressive retries for HA
  num_retries: 3
  
  # Use Redis for caching
  cache: true
  cache_type: redis
  cache_host: ${REDIS_HOST}
  cache_port: 6379
  cache_password: ${REDIS_PASSWORD}
  
  # Fallbacks between regions
  fallbacks:
    - "gpt-4o": ["gpt-3.5-turbo"]
```

### Docker Compose with HA

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: litellm
      POSTGRES_USER: litellm
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U litellm"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Proxy instance 1
  litellm-1:
    image: ghcr.io/berriai/litellm-database:main-stable
    environment:
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
      DATABASE_URL: postgresql://litellm:${DB_PASSWORD}@postgres:5432/litellm
      OPENAI_API_KEY: ${OPENAI_API_KEY_PRIMARY}
      REDIS_HOST: redis
      REDIS_PASSWORD: ${REDIS_PASSWORD}
      LITELLM_LOG: INFO
    ports:
      - "4001:4000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Proxy instance 2
  litellm-2:
    image: ghcr.io/berriai/litellm-database:main-stable
    environment:
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
      DATABASE_URL: postgresql://litellm:${DB_PASSWORD}@postgres:5432/litellm
      OPENAI_API_KEY: ${OPENAI_API_KEY_SECONDARY}
      REDIS_HOST: redis
      REDIS_PASSWORD: ${REDIS_PASSWORD}
      LITELLM_LOG: INFO
    ports:
      - "4002:4000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Load balancer (Nginx)
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - litellm-1
      - litellm-2

volumes:
  postgres_data:
```

### Nginx Load Balancer Configuration

```nginx
upstream litellm_backend {
    least_conn;
    server litellm-1:4000 max_fails=3 fail_timeout=30s;
    server litellm-2:4000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name api.example.com;

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://litellm_backend;
    }

    # API endpoints
    location / {
        proxy_pass http://litellm_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 300s;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
```

---

## Cost Optimization Setup

### Budget-Conscious Configuration

```yaml
model_list:
  # Tier 1: Budget models for simple tasks
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: gpt-3.5-turbo
      api_key: ${OPENAI_API_KEY}
      rpm: 3500
      tpm: 90000
    model_info:
      cost_per_1k_input: 0.0005
      cost_per_1k_output: 0.0015

  # Tier 2: Mid-range for complex tasks
  - model_name: gpt-4-turbo
    litellm_params:
      model: gpt-4-turbo-preview
      api_key: ${OPENAI_API_KEY}
      rpm: 200
      tpm: 40000
    model_info:
      cost_per_1k_input: 0.01
      cost_per_1k_output: 0.03

  # Tier 3: Premium for reasoning
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_API_KEY}
      rpm: 200
      tpm: 90000
    model_info:
      cost_per_1k_input: 0.005
      cost_per_1k_output: 0.015

router_settings:
  routing_strategy: cost-based-routing
  num_retries: 2
  
  # Route based on cost
  model_group_alias:
    "cheap": "gpt-3.5-turbo"
    "balanced": "gpt-4-turbo"
    "best": "gpt-4o"

general_settings:
  master_key: ${LITELLM_MASTER_KEY}
  database_url: ${DATABASE_URL}

litellm_settings:
  log: INFO
  track_cost: true
```

### Budget Enforcement

```bash
# Create team with budget limits
curl -X POST http://localhost:4000/team/new \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "finance",
    "team_alias": "Finance Department",
    "max_budget": 5000.0,
    "budget_duration": "30d",
    "tpm_limit": 100000,
    "rpm_limit": 1000
  }'

# Create user with budget
curl -X POST http://localhost:4000/user/new \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "john-doe",
    "user_email": "john@finance.com",
    "role": "internal_user",
    "teams": ["finance"],
    "max_budget": 100.0,
    "budget_duration": "7d"
  }'
```

---

## Enterprise Setup

### Complete Enterprise Configuration

```yaml
model_list:
  # Production models with high rate limits
  - model_name: gpt-4o-prod
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_API_KEY_PROD}
      rpm: 200
      tpm: 90000
    model_info:
      description: "Production GPT-4 Omni"

  - model_name: gpt-3.5-turbo-prod
    litellm_params:
      model: gpt-3.5-turbo
      api_key: ${OPENAI_API_KEY_PROD}
      rpm: 3500
      tpm: 90000

  - model_name: claude-3-opus
    litellm_params:
      model: claude-3-opus-20240229
      api_key: ${ANTHROPIC_API_KEY}

  # Development models with lower limits
  - model_name: gpt-4o-dev
    litellm_params:
      model: gpt-4o
      api_key: ${OPENAI_API_KEY_DEV}
      rpm: 50
      tpm: 20000

  # Azure models for compliance
  - model_name: azure-gpt-4-compliant
    litellm_params:
      model: azure/gpt-4
      api_base: ${AZURE_API_BASE}
      api_key: ${AZURE_API_KEY}
      api_version: 2024-02-15-preview

router_settings:
  routing_strategy: simple-shuffle
  num_retries: 2
  timeout: 30
  redis_host: ${REDIS_HOST}
  redis_password: ${REDIS_PASSWORD}
  redis_port: 6379

general_settings:
  master_key: ${LITELLM_MASTER_KEY}
  database_url: ${DATABASE_URL}
  database_connection_pool_limit: 10
  allow_requests_on_db_unavailable: true
  background_health_checks: true
  health_check_interval: 300
  alerting: ["slack"]
  proxy_batch_write_at: 60
  disable_error_logs: true
  store_model_in_db: true

litellm_settings:
  log: INFO
  num_retries: 2
  fallbacks:
    - "gpt-4o-prod": ["gpt-3.5-turbo-prod"]
    - "gpt-4o-dev": ["gpt-3.5-turbo-prod"]
  context_window_fallbacks:
    - "gpt-3.5-turbo": ["gpt-4o"]
  
  success_callback: ["langfuse", "helicone"]
  failure_callback: ["langfuse", "helicone"]
  
  cache: true
  cache_type: redis
  cache_host: ${REDIS_HOST}
  cache_port: 6379
  cache_password: ${REDIS_PASSWORD}

environment_variables:
  OPENAI_API_KEY_PROD: ${OPENAI_API_KEY_PROD}
  OPENAI_API_KEY_DEV: ${OPENAI_API_KEY_DEV}
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
  AZURE_API_BASE: ${AZURE_API_BASE}
  AZURE_API_KEY: ${AZURE_API_KEY}
  LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY}
  LANGFUSE_SECRET_KEY: ${LANGFUSE_SECRET_KEY}
  HELICONE_API_KEY: ${HELICONE_API_KEY}
  REDIS_HOST: ${REDIS_HOST}
  REDIS_PASSWORD: ${REDIS_PASSWORD}
```

### Enterprise Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: litellm-proxy
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: litellm-proxy
  template:
    metadata:
      labels:
        app: litellm-proxy
    spec:
      containers:
      - name: litellm
        image: ghcr.io/berriai/litellm-database:main-stable
        imagePullPolicy: Always
        ports:
        - containerPort: 4000
          name: http
        env:
        - name: LITELLM_MASTER_KEY
          valueFrom:
            secretKeyRef:
              name: litellm-secrets
              key: master-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: litellm-secrets
              key: database-url
        - name: REDIS_HOST
          value: redis.production.svc.cluster.local
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: litellm-secrets
              key: redis-password
        - name: OPENAI_API_KEY_PROD
          valueFrom:
            secretKeyRef:
              name: llm-keys
              key: openai-prod
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-keys
              key: anthropic
        livenessProbe:
          httpGet:
            path: /health/liveliness
            port: 4000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/readiness
            port: 4000
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: config
          mountPath: /app/config.yaml
          subPath: config.yaml
      volumes:
      - name: config
        configMap:
          name: litellm-config
---
apiVersion: v1
kind: Service
metadata:
  name: litellm-proxy
  namespace: production
spec:
  selector:
    app: litellm-proxy
  ports:
  - protocol: TCP
    port: 4000
    targetPort: 4000
  type: LoadBalancer
```

---

## Testing Configuration

### Test Script

```python
#!/usr/bin/env python3
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:4000"
MASTER_KEY = "sk-1234567890"

def test_health():
    """Test proxy health"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"[{datetime.now()}] Health: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_models():
    """List available models"""
    response = requests.get(
        f"{BASE_URL}/v1/models",
        headers={"Authorization": f"Bearer {MASTER_KEY}"}
    )
    print(f"\n[{datetime.now()}] Models: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_completion():
    """Test chat completion"""
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {MASTER_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Say hello"}],
            "temperature": 0.7
        }
    )
    print(f"\n[{datetime.now()}] Completion: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_health()
    test_models()
    test_completion()
```

---



<!-- END: original content from litellm-comprehensive-guide.md -->

---

## litellm-deployment-guide

*Source: `docs/bunchloch/meaisínfhoghlaim/litellm-deployment-guide.md` (1609 words, 776 lines)*

# LiteLLM Proxy - Deployment & Operations Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Cloud Platform Deployments](#cloud-platform-deployments)
5. [Database Migration](#database-migration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Troubleshooting](#troubleshooting)
8. [Performance Tuning](#performance-tuning)

---

## Local Development

### Quick Start

```bash
# Install dependencies
pip install 'litellm[proxy]'

# Create minimal config
cat > config.yaml << 'EOFCONFIG'
model_list:
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: gpt-3.5-turbo
      api_key: ${OPENAI_API_KEY}

general_settings:
  master_key: sk-local-1234567890
EOFCONFIG

# Set environment variables
export OPENAI_API_KEY=sk-...
export LITELLM_LOG=DEBUG

# Start proxy
litellm --config config.yaml --detailed_debug

# In another terminal, test the proxy
curl http://localhost:4000/v1/models \
  -H "Authorization: Bearer sk-local-1234567890"
```

### Development with PostgreSQL

```bash
# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Create database
createdb litellm_dev

# Set connection string
export DATABASE_URL=postgresql://localhost/litellm_dev
export LITELLM_MASTER_KEY=sk-dev-1234567890
export OPENAI_API_KEY=sk-...

# Start proxy with database
litellm --config config.yaml --detailed_debug
```

### Development Docker Compose

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: litellm_dev
      POSTGRES_HOST_AUTH_METHOD: trust
    ports:
      - "5432:5432"

  litellm:
    image: ghcr.io/berriai/litellm-database:main-latest
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://postgres@postgres:5432/litellm_dev
      LITELLM_MASTER_KEY: sk-dev-1234567890
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      LITELLM_LOG: DEBUG
    ports:
      - "4000:4000"
    volumes:
      - ./config.yaml:/app/config.yaml
    command: litellm --config /app/config.yaml --detailed_debug
```

---

## Docker Deployment

### Single Container

```bash
# Pull image
docker pull ghcr.io/berriai/litellm-database:main-stable

# Create environment file
cat > .env << 'EOFENV'
LITELLM_MASTER_KEY=sk-prod-1234567890
LITELLM_SALT_KEY=sk-salt-1234567890
DATABASE_URL=postgresql://litellm:password@postgres:5432/litellm
OPENAI_API_KEY=sk-...
AZURE_API_KEY=...
AZURE_API_BASE=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LITELLM_LOG=INFO
EOFENV

# Run container
docker run -d \
  --env-file .env \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -p 4000:4000 \
  --name litellm \
  --restart unless-stopped \
  ghcr.io/berriai/litellm-database:main-stable \
  --config /app/config.yaml \
  --num_workers 4

# Check logs
docker logs -f litellm

# Stop container
docker stop litellm
docker rm litellm
```

### Docker Compose with Complete Stack

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DB_NAME:-litellm}
      POSTGRES_USER: ${DB_USER:-litellm}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-litellm_password}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-litellm}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD:-redis_password}
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD:-redis_password}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  litellm:
    image: ghcr.io/berriai/litellm-database:main-stable
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
      LITELLM_SALT_KEY: ${LITELLM_SALT_KEY}
      DATABASE_URL: postgresql://${DB_USER:-litellm}:${DB_PASSWORD:-litellm_password}@postgres:5432/${DB_NAME:-litellm}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      AZURE_API_KEY: ${AZURE_API_KEY}
      AZURE_API_BASE: ${AZURE_API_BASE}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      REDIS_HOST: redis
      REDIS_PASSWORD: ${REDIS_PASSWORD:-redis_password}
      LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY}
      LANGFUSE_SECRET_KEY: ${LANGFUSE_SECRET_KEY}
      HELICONE_API_KEY: ${HELICONE_API_KEY}
      LITELLM_LOG: ${LITELLM_LOG:-INFO}
    ports:
      - "4000:4000"
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./litellm_logs:/app/logs
    command: >
      litellm --config /app/config.yaml
      --host 0.0.0.0
      --port 4000
      --num_workers 4
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  postgres_data:
```

### Run Docker Compose

```bash
# Create .env file
cat > .env << 'EOFENV'
LITELLM_MASTER_KEY=sk-1234567890
LITELLM_SALT_KEY=sk-salt-1234567890
DB_NAME=litellm
DB_USER=litellm
DB_PASSWORD=litellm_password
REDIS_PASSWORD=redis_password
OPENAI_API_KEY=sk-...
AZURE_API_KEY=...
AZURE_API_BASE=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LITELLM_LOG=INFO
EOFENV

# Start services
docker-compose up -d

# View status
docker-compose ps

# View logs
docker-compose logs -f litellm

# Access proxy
curl -H "Authorization: Bearer sk-1234567890" http://localhost:4000/v1/models

# Stop services
docker-compose down

# Remove volumes (careful!)
docker-compose down -v
```

---

## Kubernetes Deployment

### Helm Installation

```bash
# Add Helm repository
helm repo add berriai https://berriai.github.io/litellm-helm
helm repo update

# Create values file
cat > values.yaml << 'EOFHELM'
replicaCount: 3

image:
  repository: ghcr.io/berriai/litellm-database
  tag: main-stable

service:
  type: LoadBalancer
  port: 4000

resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "2000m"

env:
  LITELLM_MASTER_KEY:
    secretKeyRef:
      name: litellm-secrets
      key: master-key
  DATABASE_URL:
    secretKeyRef:
      name: litellm-secrets
      key: database-url
  REDIS_HOST: redis.default.svc.cluster.local
  REDIS_PASSWORD:
    secretKeyRef:
      name: litellm-secrets
      key: redis-password
  OPENAI_API_KEY:
    secretKeyRef:
      name: llm-keys
      key: openai

configMap:
  config.yaml: |
    model_list:
      - model_name: gpt-4o
        litellm_params:
          model: gpt-4o
          api_key: ${OPENAI_API_KEY}

healthCheck:
  enabled: true
  path: /health
EOFHELM

# Install release
helm install litellm berriai/litellm-proxy -f values.yaml

# Check deployment
kubectl get pods -l app=litellm-proxy
kubectl logs -f deployment/litellm-proxy

# Upgrade
helm upgrade litellm berriai/litellm-proxy -f values.yaml

# Uninstall
helm uninstall litellm
```

### Manual Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace litellm

# Create secrets
kubectl create secret generic litellm-secrets \
  --from-literal=master-key=sk-1234567890 \
  --from-literal=database-url=postgresql://... \
  --from-literal=redis-password=... \
  -n litellm

kubectl create secret generic llm-keys \
  --from-literal=openai=sk-... \
  --from-literal=anthropic=... \
  -n litellm

# Create ConfigMap for config.yaml
kubectl create configmap litellm-config \
  --from-file=config.yaml \
  -n litellm

# Deploy PostgreSQL
kubectl apply -f postgres-deployment.yaml -n litellm

# Deploy Redis
kubectl apply -f redis-deployment.yaml -n litellm

# Deploy LiteLLM
kubectl apply -f litellm-deployment.yaml -n litellm

# Check status
kubectl get all -n litellm

# View logs
kubectl logs -f deployment/litellm-proxy -n litellm

# Port forward for testing
kubectl port-forward -n litellm svc/litellm-proxy 4000:4000
```

---

## Cloud Platform Deployments

### AWS ECS (Fargate)

```json
{
  "family": "litellm-proxy",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "litellm",
      "image": "ghcr.io/berriai/litellm-database:main-stable",
      "portMappings": [
        {
          "containerPort": 4000,
          "hostPort": 4000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "LITELLM_LOG",
          "value": "INFO"
        },
        {
          "name": "REDIS_HOST",
          "value": "redis.example.com"
        }
      ],
      "secrets": [
        {
          "name": "LITELLM_MASTER_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:litellm-master-key"
        },
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:litellm-database-url"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:4000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/litellm-proxy",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run

```bash
# Create .env.yaml
cat > .env.yaml << 'EOFENV'
LITELLM_MASTER_KEY: sk-1234567890
LITELLM_SALT_KEY: sk-salt-1234567890
DATABASE_URL: postgresql://...
OPENAI_API_KEY: sk-...
LANGFUSE_PUBLIC_KEY: ...
LANGFUSE_SECRET_KEY: ...
EOFENV

# Deploy to Cloud Run
gcloud run deploy litellm-proxy \
  --image ghcr.io/berriai/litellm-database:main-stable \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --env-vars-file .env.yaml \
  --set-cloudsql-instances project:region:instance
```

### Heroku Deployment

```bash
# Create Procfile
cat > Procfile << 'EOFPROC'
web: litellm --config config.yaml --host 0.0.0.0 --port $PORT
EOFPROC

# Create app
heroku create litellm-proxy

# Set config variables
heroku config:set -a litellm-proxy \
  LITELLM_MASTER_KEY=sk-1234567890 \
  OPENAI_API_KEY=sk-... \
  DATABASE_URL=postgresql://...

# Deploy
git push heroku main

# View logs
heroku logs -f -a litellm-proxy
```

---

## Database Migration

### Initial Setup

```bash
# LiteLLM automatically creates tables on first run
# No manual migration needed!

# Just ensure DATABASE_URL is set:
export DATABASE_URL=postgresql://user:password@host:5432/litellm
litellm --config config.yaml
```

### Backup Database

```bash
# PostgreSQL backup
pg_dump -U litellm -h localhost litellm > backup.sql

# Restore from backup
psql -U litellm -h localhost litellm < backup.sql

# Docker backup
docker exec postgres pg_dump -U litellm litellm > backup.sql
```

### Database Upgrade

```bash
# Update LiteLLM
pip install --upgrade litellm

# Run proxy (migrations happen automatically)
litellm --config config.yaml

# Verify upgrade
psql -U litellm -h localhost litellm -c "\dt"
```

---

## Monitoring & Logging

### Prometheus Metrics

```bash
# Metrics endpoint
curl http://localhost:4000/metrics
```

### Langfuse Integration

```yaml
litellm_settings:
  success_callback: ["langfuse"]
  failure_callback: ["langfuse"]

environment_variables:
  LANGFUSE_PUBLIC_KEY: pk-...
  LANGFUSE_SECRET_KEY: sk-...
```

### Datadog Integration

```yaml
litellm_settings:
  success_callback: ["datadog"]
  failure_callback: ["datadog"]

environment_variables:
  DATADOG_API_KEY: ...
  DATADOG_SITE: datadoghq.com
```

### Log Levels

```bash
# Debug logging
export LITELLM_LOG=DEBUG
litellm --config config.yaml

# Info logging (default)
export LITELLM_LOG=INFO
litellm --config config.yaml

# Warning logging
export LITELLM_LOG=WARNING
litellm --config config.yaml
```

---

## Troubleshooting

### Common Issues

#### Database Connection Error

```
Error: psycopg2.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check PostgreSQL is running
psql -U litellm -h localhost -d litellm -c "SELECT 1"

# Verify connection string
echo $DATABASE_URL

# Test connection with psql
psql $DATABASE_URL
```

#### API Key Not Working

```
Error: Authentication failed - invalid key
```

**Solution:**
```bash
# Check key exists in database
psql $DATABASE_URL -c "SELECT key_name, created_at, spend FROM api_keys LIMIT 5;"

# Generate new key
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{"models": ["gpt-4o"]}'
```

#### Rate Limit Exceeded

```
Error: Rate limit exceeded for model
```

**Solution:**
```bash
# Check current usage
redis-cli -a $REDIS_PASSWORD INFO

# Increase rate limits in config
rpm: 300  # Increase from 200

# Or create key with higher limits
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{"rpm_limit": 500, "tpm_limit": 100000}'
```

#### Budget Exceeded

```
Error: Budget exceeded for this key
```

**Solution:**
```bash
# Check spend
curl http://localhost:4000/key/info \
  -H "Authorization: Bearer sk-1234567890" \
  -d '{"key": "sk-..."}'

# Update budget
curl -X POST http://localhost:4000/key/update \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{"key": "sk-...", "max_budget": 1000.0}'
```

#### Health Check Failing

```
Error: Health check failed for model
```

**Solution:**
```bash
# Check health endpoint
curl http://localhost:4000/health

# View health details
curl http://localhost:4000/health/readiness

# Check model configuration
curl http://localhost:4000/v1/models
```

### Debug Commands

```bash
# Check proxy status
curl http://localhost:4000/health

# List all models
curl http://localhost:4000/v1/models \
  -H "Authorization: Bearer sk-1234567890"

# Test a model
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "test"}]
  }'

# View logs
docker logs litellm

# Check database
psql $DATABASE_URL -c "SELECT * FROM spend_logs ORDER BY created_at DESC LIMIT 5;"
```

---

## Performance Tuning

### Worker Configuration

```bash
# Match workers to CPU cores
# Single core = 1 worker
# 4 cores = 4 workers
# 8 cores = 8 workers

docker run ... --num_workers 4
```

### Connection Pool Tuning

```yaml
general_settings:
  database_connection_pool_limit: 10  # Increase for high concurrency
  database_connection_timeout: 60     # Timeout in seconds
```

### Redis Optimization

```yaml
router_settings:
  redis_host: ${REDIS_HOST}
  redis_password: ${REDIS_PASSWORD}
  redis_port: 6379
  redis_ttl: 300  # Cache TTL in seconds
```

### Request Optimization

```yaml
litellm_settings:
  cache: true                    # Enable caching
  cache_type: redis
  cache_host: ${REDIS_HOST}
  cache_port: 6379
  
  # Batch writes for better throughput
  proxy_batch_write_at: 60      # Batch every 60 seconds
```

### Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Load test the proxy
ab -n 1000 -c 10 \
  -H "Authorization: Bearer sk-1234567890" \
  -H "Content-Type: application/json" \
  -p request.json \
  http://localhost:4000/v1/chat/completions

# Using wrk
wrk -t4 -c100 -d30s \
  -H "Authorization: Bearer sk-1234567890" \
  http://localhost:4000/health
```

---


