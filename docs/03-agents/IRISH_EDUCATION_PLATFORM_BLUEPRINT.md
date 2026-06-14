---
truth: partial
---

# Irish Education Platform Blueprint: Agentic Systems for Celtic Education

## Merged From
- `Agentic Education Platform Development.md`
- `AI Agents for Irish Language Resources.md`
- `Agentic Translation Workflow Technologies.md`

---

## Part I: The Agentic Academy — Decentralized Celtic Educational Hub

### 1.1 The Agentic Paradigm

The transition from static Learning Management Systems (LMS) to "Agentic" educational platforms represents a fundamental architectural shift. In the agentic model, the platform is an active collaborator, capable of reasoning, utilizing tools, and maintaining complex state over extended pedagogical horizons. For a British Isles-wide multilingual hub, the goal is to deploy autonomous "Tutor Agents" that can dynamically generate lessons, assess proficiency through interaction, and autonomously transact value within a decentralized economy.

### 1.2 The Architecture of CopilotKit and AgUI

**AgUI (Agent-User Interaction):** An event-based standard that abstracts the connection between the AI agent (backend intelligence) and the user interface (frontend application). For an educational platform, this is transformative — a "Lesson Agent" built on LangGraph (Python) can emit a `show_exercise` event, and AgUI transmits this to the React/Next.js frontend, which renders a specific interactive component (e.g., a drag-and-drop Gaelic sentence constructor).

**Generative UI:** The frontend becomes a "renderer" of agent intent. Bi-directional state synchronization means the agent "sees" student actions in real-time.

**Model Context Protocol (MCP):** MCP provides standardized access to diverse, fragmented datasets:

- **Dictionary MCP:** Wraps search logic for multilingual dictionaries (eDIL, Dúchas.ie)
- **Curriculum MCP:** Exposes lesson plans and exam banks
- **User Record MCP:** Provides safe access to student learning history and reputation score

### 1.3 The Protocol of Value: x402 and Agentic Economics

x402 revives the dormant HTTP 402 "Payment Required" status code to enable autonomous machine-to-machine payments.

**Transaction Flow:**
1. **Resource Request:** Student's Tutor Agent requests a premium resource (e.g., generated exam)
2. **402 Challenge:** Server responds with `402 Payment Required` containing cost, accepted currency, destination address
3. **Autonomous Settlement:** Agent (equipped with Coinbase AgentKit wallet) signs and resends with Payment-Authorization header
4. **Service Delivery:** Server verifies payment and releases content

**Dual-Token System:**

| Token | Name | Role | Format |
|---|---|---|---|
| Utility | "Pinginn" (Penny) | Medium of Exchange | ERC-20 Stablecoin (USDC) |
| Reputation | "Screpall" (Scruple) | Store of Merit | Soulbound Token (SBT) |

By separating "money" (Pinginn) from "grade" (Screpall), the platform prevents "Pay-to-Win" while enabling a functional internal economy.

### 1.4 The Educational Ledger: Smart Contracts

**Optimistic Oracle Pattern (UMA):** Agents submit claims ("Student X completed Lesson Y with 95%"). A challenge window exists where other students or AI agents can dispute. If undisputed, the Screpall reward is minted.

**Ethereum Attestation Service (EAS):** Creates off-chain or on-chain "Attestations" for credentials. A Merkle Root of attestations is published on-chain periodically.

### 1.5 Celtic Cultural Gamification

**Bardic Grade Hierarchy:**

| Level | Ancient Title (Irish) | Role | Platform Privileges |
|---|---|---|---|
| Novice (1-10) | Ollaire | Principle Beginner | Basic lessons |
| Apprentice (11-20) | Tamhan | Grammar and tales | Buy hints with Pinginn |
| Journeyman (21-30) | Drisac | Creative composition | Creative Writing tools |
| Scholar (31-40) | Cli | Must know 80 tales | Unlocks Lore library |
| Master (41-50) | Anruth | Noble Stream | Peer Reviewer for Novices |
| Doctor (50+) | Ollamh | Chief Poet, 350 tales | Governance (DAO voting) |

**Cycle-Based Curriculum:**
- Mythological Cycle → Beginner track (Tuatha Dé Danann, foundational myths)
- Ulster Cycle → Intermediate (Cú Chulainn, action verbs, martial vocabulary)
- Fenian Cycle → Advanced (Fionn mac Cumhaill, nature poetry)
- Historical Cycle → Expert (Kings, complex political language)

---

## Part II: The Neuro-Symbolic Gaeilge Engine — AI for Irish Language Resources

### 2.1 The Challenge of Cognitive Preservation

Preserving Irish language artifacts requires transitioning from static digitization to dynamic cognitive activation. The system must process:
- Historical handwritten manuscripts (National Folklore Collection, Dúchas)
- Leaving Certificate Mathematics papers
- Bilingual documents with Cló Gaelach and standardized text

### 2.2 Computational Linguistics of Cló Gaelach

Irish handwriting presents unique orthographic conventions:
- **Punctum delens:** A dot above a letter indicating lenition (ḃ → bh, ċ → ch) — traditional OCR misinterprets as noise
- **Cló Gaelach:** Gaelic type font with distinctive character shapes
- **Visual density:** Line variance, ink bleed-through

A VLM like **GLM-4.6v** processes images as semantic wholes, not just pixel-to-character mapping. Its native grounding capabilities return bounding box coordinates alongside textual transcription, maintaining spatial indices for paleographers.

### 2.3 Agno Agent Team Topology

**Hierarchical Team Structure:**

1. **Chief Examiner (Orchestrator):** Entry point for all queries. Decomposes user requests using Agno's AgentTeam class with delegate capability.

2. **Palaeographer (Vision Specialist):** Equipped with Z.ai GLM-4.6v via custom MCP client. Solely responsible for visual interpretation of handwriting and diagrams.

3. **Ontologist (Structure Specialist):** Uses BAML tools to parse raw text into strictly typed JSON objects adhering to Leaving Certificate schema.

**Z.ai GLM-4.6 Configuration:**
```python
from agno.models.openai.like import OpenAILike

zhipu_text_model = OpenAILike(
    id="glm-4.6",
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    max_tokens=4096,
    temperature=0.1
)

zhipu_vision_model = OpenAILike(
    id="glm-4.6v",
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)
```

**Vision MCP Integration:**
```python
from agno.tools.mcp import MCPTools

vision_mcp_tools = MCPTools(
    command="npx",
    args=["-y", "@z_ai/mcp-server"],
    env={"Z_AI_API_KEY": os.getenv("ZHIPU_API_KEY"), "Z_AI_MODE": "ZAI"}
)

vision_specialist = Agent(
    name="Palaeographer",
    role="Expert in Irish handwriting and mathematical diagrams",
    model=zhipu_text_model,
    tools=[vision_mcp_tools],
)
```

### 2.4 CocoIndex ETL Pipeline

CocoIndex operates on dataflow programming principles — treating data transformations as a DAG where each step is memoized. PostgreSQL is used as an internal state store to track data lineage:

- Content hashing detects deltas, triggering transformations only for changed pages
- Vital for cost control when using high-end models like GLM-4.6v
- Integrates Agno agents as custom transformation functions

**Pipeline Construction:**
```python
import cocoindex
from cocoindex.sources import LocalFile
from cocoindex.targets import Postgres
from cocoindex.functions import SplitRecursively, SentenceTransformerEmbed

# Define ingestion flow for exam papers
# Source → Chunking → BAML Extraction → Vector Embedding → Graphiti Storage
```

### 2.5 Cognee Knowledge Graph

The system constructs a "Cognitive Federation" using:
- **Agno:** Agentic control plane (3μs agent instantiation)
- **CocoIndex:** Incremental dataflow
- **Cognee:** Semantic graph construction in PostgreSQL + LanceDB
- **BAML:** Schema enforcement for rigorous compliance
- **Langfuse + Ragas:** Monitoring and evaluation

---

## Part III: Agentic Translation Workflow for Celtic Languages

### 3.1 The "Trust Gap" in Generative Translation

For Irish, with complex initial mutations (séimhiú, urú) and dialectal variance (Ulster, Connacht, Munster), probabilistic models often default to An Caighdeán Oifigiúil or anglicized structures, stripping authentic cultural texture.

**The "Agentic Computer" Metaphor:**
- **OS:** Google ADK as Operating System (ArbiterOS)
- **Hardware:** Gemini 3 (Performance Core), T5Gemma-2 (Efficiency Core)
- **Governance Layer:** Enforces deterministic rules on probabilistic outputs

### 3.2 The Cognitive Engine: Gemini 3

**System 2 Reasoning:** Gemini 3's "Deep Thinking" capability uses Adaptive Compute protocols to allocate inference resources dynamically, validating logic against internal benchmarks before output.

**Critic Agent Flow:**
1. Plan: Deconstruct source sentence into semantic units
2. Verify: Check draft against units for fidelity
3. Reflect: Identify cultural nuances missed by drafter
4. Justify: Produce "Thought Signature" — immutable audit log

**Multimodality:** Native support for text, images, audio, video, PDF. SigLIP vision encoder for high-fidelity OCR on handwritten documents. "Pan & Scan" adaptive windowing preserves document layout.

**Cost Optimization:**
- Gemini 3 Pro: Critic/Planner ($0.50/M input tokens) — PhD-level reasoning
- Gemini 3 Flash: Ingestion/Sorting — speed over depth

### 3.3 The Linguistic Workhorse: T5Gemma-2

**Encoder-Decoder Architecture:** Separates understanding (Encoder) from generation (Decoder). The encoder "reads" the entire source before the decoder generates a single token — superior for resolving long-distance dependencies.

**Key Innovations:**
- **Tied Embeddings:** Shared parameters across encoder input, decoder input, decoder output — ~10.5% parameter reduction
- **Merged Attention:** Unified self-attention and cross-attention — faster inference, improved parallelization
- **UL2 Adaptation:** Initialized from Gemma 3 weights, adapted using mixture of denoising tasks — retains broad knowledge while acquiring encoder-decoder structure
- **Multilingual:** 140+ languages including low-resource Celtic

### 3.4 Google ADK Workflow Primitives

**Sequential Agent:** Linear phases — OCR (Gemini) → Text Cleaning → Context Extraction

**Loop Agent:** Draft-Critique-Refine cycle — Drafter (T5Gemma-2) + Critic (Gemini 3) iterate until quality score >95% or zero compliance violations

**Parallel Agent:** "Fan-Out/Gather" for concurrent translation of document sections

**Neuro-Symbolic "Truth Anchoring":** ADK Compliance Agent integrates symbolic Ontology (OWL Knowledge Graph or Glossary). If Glossary mandates "Mionnscríbhinn" for "Affidavit" and the neural model produces "Ráiteas faoi mhionn" (valid but non-standard synonym), the symbolic layer detects the mismatch and forces correction.

### 3.5 Infrastructure: Transformers v5

`transformers serve` provides a high-performance model server with OpenAI-compatible API for local models:
- Hosts T5Gemma-2 Drafter locally to eliminate network overhead
- **Continuous Batching:** Accumulates requests and processes as a batch, prioritizing in-progress sequences — solves latency accumulation in multi-turn agentic loops

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|---|---|---|
| Agent Framework | CopilotKit / Agno | Application-level orchestration |
| UI Protocol | AgUI (Agent-User Interaction) | Event-based agent-frontend communication |
| Data Protocol | MCP (Model Context Protocol) | Standardized tool/resource access |
| Payments | x402 + Coinbase AgentKit | Autonomous machine-to-machine payments |
| Reputation | EAS + Soulbound Tokens | On-chain academic credentials |
| Vision | Z.ai GLM-4.6v | Handwriting recognition, diagram analysis |
| Reasoning | Gemini 3 Pro | System 2 deep reasoning, critique |
| Drafting | T5Gemma-2 | Encoder-decoder translation |
| Orchestration | Google ADK | Workflow primitives (Sequential, Loop, Parallel) |
| ETL | CocoIndex | Incremental dataflow with memoization |
| Knowledge Graph | Cognee + Graphiti | Semantic graph + temporal reasoning |
| Vector DB | LanceDB / pgvector | Hybrid search for curriculum content |
| Schema | BAML | Type-safe LLM extraction |
| Monitoring | Langfuse + Ragas | Observability and evaluation |
| Serving | Transformers v5 | Continuous batching, local model hosting |
