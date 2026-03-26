# Durable Workflow Comparison: Temporal vs Restate vs DBOS

## Executive Summary

This analysis compares three durable workflow systems based on examples in `/data/flows/crypto/examples/`. The recommendation is a **hybrid approach**: Restate for TypeScript orchestration and DBOS for Python agent workflows.

---

## 1. Temporal

### Source Examples
- `examples/temporal/crypto-trading-agents/` - Full trading agent system
- `examples/temporal/temporal-boost/` - Framework for easier Temporal development

### Architecture Patterns

#### Workflow Types Observed
1. **Broker Agent Workflow** - Long-running state machine for user interface
2. **Execution Agent Workflow** - Trading decisions with dynamic prompt management
3. **Judge Agent Workflow** - "LLM as Judge" for autonomous performance evaluation
4. **Ensemble Workflow** - Shared bus for cross-agent coordination
5. **Execution Ledger Workflow** - Transactional ledger with P&L tracking

#### Key Patterns
- **Signal-driven execution**: Agents receive "nudges" via Temporal signals (25-second intervals)
- **Query-based analytics**: Rich query interfaces for portfolio status, evaluations
- **Continue-as-new**: Prevents workflow history explosion (every 3600 cycles)
- **MCP Server integration**: FastMCP exposes workflows as tools

#### Durability Model
- Event-sourced workflow history
- Replays entire workflow from start on failure
- Deterministic code execution enforced
- State maintained in workflow variables

### Strengths for Crypto
- 24/7 durability for always-on crypto markets
- Immutable audit trail for compliance
- Multi-venue routing orchestration
- Built-in "profit scraping" pattern

### Weaknesses
- Heavy infrastructure (server cluster required)
- Steep learning curve (workflow definition language)
- ~100ms signal delivery latency
- History explosion requires continue-as-new management

### temporal-boost Framework
Simplifies Temporal development with:
- `BoostApp` class for single-line setup
- Auto-discovery of workflows/activities
- FastStream integration for event-driven patterns
- Built-in CLI (`run all`, `run <worker>`, `cron`, `exec`)
- YAML/env-var configuration

---

## 2. Restate

### Source Examples
- `examples/restate/mcp/` - MCP server integration
- `examples/restate/typescript-patterns/` - TypeScript workflow patterns

### Architecture Patterns

#### Handler Types
- `restate.service()` - Stateless request/response
- `restate.object()` - Stateful virtual objects (keyed state, sessions)
- `restate.workflow()` - Long-running workflow orchestration

#### Pattern Catalog from Examples
1. **Chaining** - Sequential LLM calls with durable steps
2. **Tool Routing** - LLM decides tool, execute durably, loop
3. **Parallel Tools** - `RestatePromise.all()` for distributed parallel execution
4. **Multi-Agent Routing** - Classify request → route to specialist
5. **Human-in-the-Loop** - `ctx.awakeable()` for suspend/resume
6. **Chat Sessions** - Virtual objects store conversation memory
7. **Evaluator-Optimizer** - Generate → Evaluate → Improve loop

#### Durability Model
- Journal-based (NOT event replay like Temporal)
- Each `ctx.run()` writes a journal entry
- On failure, replays from last entry (not entire workflow)
- Handlers are idempotent by construction

### MCP Integration
- Tools marked with `"mcp.type": "tool"` metadata
- Dynamic discovery via Restate Admin API
- Zod schemas compiled to JSON Schema for validation
- Tools execute with full durability guarantees

### Strengths for Crypto
- TypeScript-first design (aligns with frontend stack)
- Native MCP support for AI agent integration
- Light operational overhead (single binary)
- Journal-based recovery (faster than event replay)
- Virtual objects perfect for per-user/per-session state

### Weaknesses
- Requires Restate server (additional dependency)
- Less mature ecosystem than Temporal
- Limited complex workflow patterns vs Temporal

---

## 3. DBOS

### Source Examples
- `examples/dbos/pydantic/` - PydanticAI integration with durable execution
- `examples/dbos/document-detective/` - Document processing pipeline
- `examples/dbos/hacker-news-agent/` - Agentic news processing (TypeScript)

### Architecture Patterns

#### Durable Execution Pattern
```python
# Standard PydanticAI Agent
questioner_agent = Agent(...)

# Wrapped with DBOS durability
dbos_questioner_agent = DBOSAgent(questioner_agent)
```

#### Workflow Primitives
- `@DBOS.workflow()` - Durable workflow decorator
- `@DBOS.step()` - Granular fault isolation
- `queue.enqueue()` - Concurrent queue processing
- `SetWorkflowID()` - Deterministic workflow identification

### Durability Model
- Database-backed (PostgreSQL)
- Persists agent executions to workflow table
- Automatic recovery using workflow IDs
- Resumable with workflow handles

### Strengths for Crypto
- Minimal infrastructure (just Postgres)
- Native PydanticAI support (extends to Agno)
- Type-safe via Pydantic models
- Document processing patterns ready for crypto docs
- Lowest operational complexity

### Weaknesses
- Vertical scaling only (DB limits)
- No native MCP support
- Less sophisticated workflow patterns
- Single-language focus (Python primary)

---

## 4. Comparison Matrix

| Aspect | Temporal | Restate | DBOS |
|--------|----------|---------|------|
| **Setup Complexity** | High (cluster) | Medium (binary) | Low (Postgres) |
| **TypeScript Support** | SDK available | Native, excellent | TypeScript SDK |
| **Python Support** | Good SDK | Polyglot | Excellent (native) |
| **BAML Integration** | Manual wrapping | Natural via MCP | Native Pydantic |
| **MCP Support** | None | Built-in | None |
| **Durability Model** | Event replay | Journal-based | Database-backed |
| **Recovery Speed** | Slow (full replay) | Fast (from step) | Fast (from DB) |
| **Scaling** | Horizontal | Horizontal | Vertical |
| **Learning Curve** | Steep | Moderate | Gentle |
| **Maturity** | Production-proven | Growing | Growing |
| **AI Agent Patterns** | Manual | First-class | First-class |

---

## 5. Crypto-Specific Considerations

### Transaction Reconciliation
- **Temporal**: Excellent for multi-step confirmation workflows (see crypto-trading-agents ledger)
- **Restate**: Good for idempotent blockchain submissions
- **DBOS**: Simpler, better for single-step retries

### Real-time Analytics
- **Temporal**: Can orchestrate, but not streaming-native
- **Restate**: Better for event-driven patterns
- **DBOS**: Best combined with RisingWave for streaming

### Agent Orchestration
- **Temporal**: Judge agent pattern is sophisticated
- **Restate**: MCP integration makes AI agents first-class
- **DBOS**: DBOSAgent wrapper is simplest

---

## 6. Recommendation: Hybrid Architecture

### TypeScript Layer: Restate
- Frontend orchestration and UI state
- MCP server exposing tools to Claude/AI agents
- Durable workflows for multi-step crypto operations
- WebSocket streaming for real-time updates

### Python Layer: DBOS
- Data pipelines (crawl4ai, dlt, RisingWave)
- Agno agents wrapped with DBOSAgent
- ML inference and blockchain RPC
- Document processing workflows

### Integration Pattern
```
┌─────────────────────────────────────────────────────┐
│  TanStack Start (Frontend)                          │
│  - React components, shadcn UI                      │
│  - DuckDB-Wasm for client analytics                 │
└─────────────────────────────────────────────────────┘
                    ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────┐
│  Restate Server (TypeScript Orchestration)          │
│  - MCP tools for AI agent integration               │
│  - Virtual objects for user sessions                │
│  - Durable workflows for multi-step operations      │
└─────────────────────────────────────────────────────┘
                    ↓ HTTP calls
┌─────────────────────────────────────────────────────┐
│  Python Services (DBOS + Agno)                      │
│  - Agno agents with DBOSAgent durability            │
│  - Data pipelines (crawl4ai → dlt → R2)             │
│  - Blockchain RPC interactions                      │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  Data Layer                                         │
│  - RisingWave (streaming SQL)                       │
│  - Dragonfly (cache + queue)                        │
│  - Cognee + LanceDB (knowledge)                     │
│  - Cloudflare R2 (storage)                          │
└─────────────────────────────────────────────────────┘
```

---

## 7. Migration Paths

### From Temporal Examples
- Port workflow patterns to Restate virtual objects
- Use `ctx.run()` instead of activities
- Replace signals with method calls
- Use awakeables for long waits (vs activity completion)

### BAML Integration
- Restate: BAML functions exposed as MCP tools
- DBOS: BAML outputs as Pydantic models for DBOSAgent

### Temporal Patterns Worth Keeping
- "LLM as Judge" self-improvement loop (port to Restate)
- Profit scraping system (implement in ledger service)
- Context manager token budgeting (use in both layers)

---

## References

- `/examples/temporal/crypto-trading-agents/README.md`
- `/examples/temporal/temporal-boost/README.md`
- `/examples/restate/README.md`
- `/examples/restate/typescript-patterns/README.md`
- `/examples/dbos/pydantic/README.md`
