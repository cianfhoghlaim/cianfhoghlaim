# Durable Execution: Restate & DBOS — Comprehensive Reference

## Merged From
- `durable/restate/README.md` + all subdirectory READMEs
- `durable/dbos/` — all subdirectory READMEs
- `durable/restate/ai-examples/README.md`
- `durable/restate/ai-examples/a2a/README.md`
- `durable/restate/ai-examples/vercel-ai/template/README.md` + `tour-of-agents/README.md` + `examples/README.md`
- `durable/restate/ai-examples/openai-agents/template/README.md` + `tour-of-agents/README.md`
- `durable/restate/ai-examples/python-patterns/README.md`
- `durable/restate/mcp/README.md`
- `durable/restate/typescript-patterns/README.md`
- `durable/restate/agent47/README.md`
- `durable/dbos/widget-store/README.md`, `s3mirror/README.md`, `reliable-refunds-langchain/README.md`, `queue-worker/README.md`, `hacker-news-agent/README.md`, `document-detective/README.md`, `dbos-toolbox/README.md`, `dbos-node-starter/README.md`, `dbos-node-toolbox/README.md`

---

## Part I: Restate — Durable Execution for AI Agents

### Why Restate?

Restate adds production-grade resilience to AI agent workflows: crash-safe LLM/tool calls, state persistence, retries, suspend/resume, human-in-the-loop, and observability — independent of any specific SDK.

| Use Case | What it Solves |
|---|---|
| **Durable Execution** | Crash-safe LLM/tool calls & idempotent retries |
| **Observability** | Auto-captured trace of every step, retry, and message |
| **Human-in-the-loop** | Suspend while waiting for approval; pay for compute, not wall-clock time |
| **Stateful sessions** | Virtual Objects keep multi-turn conversations isolated and consistent |
| **Multi-agent orchestration** | Reliable RPC, queuing, scheduling between agents |

### SDK Integrations

| Integration | Examples Available |
|---|---|
| **Vercel AI SDK** | Template, Tour of Agents, Next.js deployment examples |
| **OpenAI Agents SDK** | Template, Tour of Agents (Python + TypeScript) |

```typescript
// Vercel AI SDK with Restate
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

### Composable AI Patterns

Restate provides battle-tested patterns in Python and TypeScript:

| Pattern | Description |
|---|---|
| **Prompt Chaining** | Fault-tolerant processing pipelines with LLM calls |
| **Tool Routing** | Auto-route to tools based on LLM outputs |
| **Parallel Tools** | Execute multiple tools concurrently with durable results |
| **Multi-Agent Routing** | Route to specialized agents based on LLM outputs |
| **Human-in-the-loop** | Suspend execution until feedback is received |
| **Chat Sessions** | Long-lived, stateful conversations via Virtual Objects |
| **Orchestrator-Worker** | Break complex tasks into specialized parallel subtasks |
| **Evaluator-Optimizer** | Generate → Evaluate → Improve loop until quality met |
| **Racing Agents** | Race multiple agents, use fastest response |

### Awakeables — Human-in-the-Loop

```typescript
// 1. AI calculates provisional grade
// 2. Generate Approval ID
// 3. Suspend — zero compute consumed while waiting
await ctx.awakeable();
// 4. Days later, teacher clicks "Approve"
// 5. Restate restores state, resumes at next line
finalizeGrade();
```

### Virtual Objects

Stateful entities accessed sequentially — perfect for Classrooms and ExamSessions:
- Concurrency control: One request at a time, preventing race conditions
- State isolation: "Class 10-A" isolated from "Class 10-B"

### Supported Languages

TypeScript, Python, Java, Kotlin, Go, Rust

### Additional Examples

- **MCP:** Restate for exposing tools and resilient tool orchestration
- **A2A:** Google's Agent-to-Agent protocol with Restate as orchestrator
- **Agent47:** Full-stack agent with pubsub, UI components, and types

---

## Part II: DBOS — Durable Backend Operations

DBOS (Database-Backed Operating System) provides durable execution primitives for TypeScript applications. Examples:

### Widget Store
E-commerce widget store with durable operations, database transactions, and reliable order processing.

### S3 Mirror
Mirrors files between S3 buckets with reliable, crash-safe operations.

### Reliable Refunds (LangChain)
LangChain-powered refund processing with durable execution guarantees.

### Queue Worker
Durable queue processing with retry logic and exactly-once semantics.

### Hacker News Agent
AI agent that processes Hacker News content, with a React frontend for interaction.

### Document Detective
Document analysis agent using AI for content extraction and classification.

### DBOS Toolbox
Collection of utility operations and patterns for DBOS applications.

### DBOS Node Starter
Minimal starter template for DBOS projects.

### DBOS Node Toolbox
Toolbox with migrations, database utilities, and common patterns.

### Key DBOS Concepts

- **Durable Execution:** Operations guaranteed to complete, even across server restarts
- **Workflows:** Long-running business processes with state persistence
- **Transactions:** ACID guarantees for database operations
- **Communicators:** External API calls with built-in retry

---

## Resources

- Restate: https://restate.dev | https://docs.restate.dev/ai
- Restate Cloud: https://restate.dev/cloud
- DBOS: https://docs.dbos.dev
- Discord: https://discord.gg/skW3AZ6uGd
