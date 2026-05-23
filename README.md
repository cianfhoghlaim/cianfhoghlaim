# Cianfhoghlaim & Awen Hub
*An Agentic Educational MMO and Data Platform for Celtic Languages and the Irish Curriculum.*

![Architecture Overview](docs/images/hero_banner.jpg) <!-- Update path if needed -->

## The Vision
Cianfhoghlaim (and its interactive frontend, **Awen Hub**) represents a paradigm shift from static Learning Management Systems. It is a decentralised, AI-driven educational MMO. It fuses the comprehensive scale of the **Irish Leaving Certificate** and **Junior Cycle** curricula with cutting-edge web architecture. 

By leveraging autonomous agents, semantic code/knowledge bases, and a Web3 "Learn-to-Earn" economy (utilising the x402 protocol and a dual-token Anam system), Awen Hub provides hyper-personalised, interactive learning experiences wrapped in immersive Celtic RPG aesthetics.

---

## Core Architecture: The Dual-Stack

To maintain a strict separation of concerns, the project is divided into two distinct halves: Python-based Data Engineering and TypeScript-based Full-Stack Web Development.

### 1. `oideachais/data_platform` (Python / Data & Agents)
This is the engine room of the platform, managed with `uv` for lightning-fast Python dependency resolution.
*   **Data Pipelines (`dlt`, `dagster`)**: Ingests, normalises, and tracks provenance for every Irish syllabus, exam paper, and marking scheme. Upgraded to `dlt v1.5+` featuring **dltHub Projects & Caching** for local DuckDB transformations, and `dagster v1.13+` for robust orchestration.
*   **Knowledge Graphs & Memory**: Utilises `graphiti-core` and `cognee` to build temporal context graphs of student progress and curriculum structures.
*   **Agentic Orchestration (`google-adk`, `agno`)**: `Agno` (v2.0+) provides stateless AgentOS workflows, while `Google ADK` (v2.1+) offers a Multi-Agent Workflow Engine for complex task routing between specialist agents.
*   **Deep Web Exploration (`browserbase`, `firecrawl`)**: Agents utilise MCP servers to execute autonomous, JavaScript-rendering web scrapes for dynamic educational content discovery.
*   **Codebase Indexing (`chunkhound`)**: Transforms raw repositories into searchable, AST-chunked semantic databases.

### 2. `oideachais/web_app` (TypeScript / TanStack / Cloudflare)
The user-facing portal, built on the bleeding-edge of the React ecosystem and managed primarily via `bun`.
*   **TanStack Start**: A full-stack SSR/CSR framework providing type-safe file-based routing (`@tanstack/react-router`) and server functions (`createServerFn`), heavily optimised for edge deployment on **Cloudflare**.
*   **CopilotKit & Generative UI**: Moving beyond simple chat windows. Agents utilise `@tanstack/ai` and CopilotKit to stream state changes directly into the UI, rendering dynamic React components (AgUI) in real-time.
*   **MotherDuck Embedded Dives**: Delivers zero-latency, client-side analytics. MotherDuck's dual-execution engine pushes a DuckDB-WASM instance directly into the browser, allowing students to filter and explore massive datasets (like CSO statistics or exam results) instantly.
*   **Celtic Dark Mode (Tailwind v4)**: An immersive UI drawing inspiration from RPGs (*Hades*, *Clair Obscur*). Features deep `slate-900` backgrounds, tactile "Duolingo-style" buttons, Ogham stone noise textures, and specific Celtic-nation accent colours.

---

## Deployment & Development Guide

**Why order matters:** This is a highly distributed system. Agents need API access, pipelines need databases, and the frontend needs the pipelines. Furthermore, **secrets are managed dynamically and must be hydrated before anything else runs.**

### Prerequisites
1.  **[mise](https://mise.jdx.dev/)**: Used to manage tool versions globally and execute directory-specific environment hooks (automatically injecting secrets).
2.  **[uv](https://github.com/astral-sh/uv)**: The blazingly fast Python package installer and resolver.
3.  **[bun](https://bun.sh/)**: The preferred, high-performance JavaScript runtime and package manager used for the `web_app`. (*NPM/Node instructions are retained as legacy fallbacks where strictly necessary for obscure package compatibility*).
4.  **Docker Desktop / OrbStack**: Required for backing services.

### Step-by-Step Initialization

#### Step 1: Infisical & Secrets (The Locket)
*You cannot run MCPs or data pipelines without credentials.*
We use Infisical for centralised secret management, deployed via a sidecar pattern ("Locket").
```bash
# 1. Ensure you have the Infisical CLI installed via your package manager
# 2. Login to your Infisical account
infisical login

# 3. Export secrets to the local environment (Mise hooks normally handle this automatically)
# This resolves your `.infisical.env` template into a hydrated, git-ignored `.env` file.
infisical export --env=dev > .env
```

#### Step 2: Spin Up Backing Infrastructure
Start the vector databases (LanceDB), graph databases (Neo4j), temporal memory services, and the Locket sidecar.
```bash
# Deploys compose.yaml overlaid with sidecar.yaml for secure tmpfs secret mounting
docker compose -f compose.yaml -f sidecar.yaml up -d
```

#### Step 3: Run the Data Platform (Python)
Hydrate MotherDuck and your vector stores with the Irish curriculum datasets.
```bash
cd oideachais/data_platform

# Install dependencies blazingly fast
uv sync

# Run the Dagster UI to orchestrate DLT pipelines manually
uv run dagster dev -m dagster_defs.definitions
```
*(Inside the Dagster UI, trigger the `ireland_curriculum` and `exam_source` assets to pull the latest SEC and NCCA data into your dltHub Projects cache and MotherDuck).*

#### Step 4: Start the Web App (TypeScript)
With data populated and secrets hydrated, spin up the TanStack application.
```bash
cd ../web_app

# Install dependencies using Bun
bun install

# Start the TanStack dev server
bun run dev
```
*(Note: If you encounter specific Vite/Rollup plugin incompatibilities with Bun during builds, fallback to `npm run dev`).*

---

For deeper technical details on specific modules, please consult the respective READMEs inside `oideachais/` and the `.skills/` directory.
