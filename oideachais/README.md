# Oideachais: The Core Modules

This directory houses the entirety of the Oideachais platform, strictly partitioned into the `data_platform` (Backend, AI, & Data Engineering) and `web_app` (Frontend & Generative UI).

## 1. The Data Platform (`oideachais/data_platform`)
This is a heavily orchestrated Python environment. It manages the ingestion of thousands of curriculum documents, state exams, and demographic datasets, processing them into semantic knowledge graphs and structured tables for our AI agents to consume.

### Irish Education Assets & Pipelines
The `dlt_sources/ireland/` directory is the crown jewel of our ingestion layer. 
*   **Curriculum Source**: A unified DLT pipeline that crawls `curriculumonline.ie`, `examinations.ie`, and `ncca.ie`. It normalises diverse HTML and PDF inputs into a strict, subject-centric Pydantic model (`LearningOutcome`, `AssessmentInfo`, etc.).
*   **State Examinations**: Extracts decades of past papers, chief examiner reports, marking schemes, and aural exam transcripts (complete with dialect tags: Connacht, Munster, Ulster).
*   **Statistics & GIS**: Integrates with the CSO PxStat API for Census 2022 Small Area statistics, and GeoHive for geospatial boundaries, allowing agents to correlate educational outcomes with local demographics.
*   **dltHub Integration**: We utilise `dlt v1.5+`. DLT sources are now wrapped in `dltHub Projects`, establishing a collaborative YAML manifest. We heavily utilise the **dlt+ Cache**, providing a portable DuckDB compute layer. This allows us to perform massive transformations locally before syncing the final `Datasets` to MotherDuck.

### Agentic Intelligence
*   **Google ADK (v2.1+)**: Serves as our primary Multi-Agent Workflow Engine. It handles dynamic, non-linear execution graphs and native Inter-Agent routing.
*   **Agno (v2.0+)**: Provides our AgentOS runtime. Agents here are completely stateless, pulling context on-the-fly from our unified async knowledge bases.
*   **Memory & Graph**: We use `Graphiti` and `Cognee` to track temporal, episodic memory (e.g., how a student's understanding of a specific physics concept evolves over a semester).
*   **MCP Integration**: `Firecrawl` and `Browserbase` MCP servers allow our agents to autonomously break out of the local environment to scrape JS-rendered dynamic web pages or perform interactive web research.

## 2. The Web Application (`oideachais/web_app`)
This is the user-facing Awen Hub interface. It completely discards legacy React patterns in favour of the modern **TanStack** ecosystem, heavily optimised for deployment to **Cloudflare Pages/Workers**.

### The TanStack Ecosystem
*   **TanStack Start**: The backbone of the application. It handles both Server-Side Rendering (SSR) for initial load speed and SEO, and Client-Side Routing (CSR) for seamless SPA transitions.
*   **File-Based Routing**: Powered by `@tanstack/react-router`, with routes strictly defined in `src/routes/` and type-safe routing trees auto-generated via `routeTree.gen.ts`.
*   **State & Forms**: Uses `@tanstack/react-query` for server state, `@tanstack/react-form` for complex validation (paired with Zod), and `@tanstack/db` for robust local offline-first caching.
*   **Better Auth**: Replaces older auth paradigms, providing a comprehensive, type-safe authentication layer capable of integrating our SIWE (Sign-In with Ethereum) Web3 requirements.

### Generative UI (AgUI) & CopilotKit
We have moved beyond the traditional "chatbot in a sidebar" paradigm.
*   The entire application is wrapped in `<CopilotKit>`.
*   Using `@tanstack/ai-react`, our backend agents don't just stream text; they stream *React Server Components* and state updates. 
*   If an agent needs to show you a map of Gaeltacht regions, it doesn't describe it—it emits an event that renders an interactive `GeospatialMap` component directly into the user's workflow.

### MotherDuck Embedded Dives
To provide instantaneous analytics on heavy datasets (like exploring 10 years of Leaving Cert grading curves), we use **MotherDuck Embedded Dives**.
*   Instead of building complex charting libraries in React that request data from a slow API, our TanStack server functions generate a secure, ephemeral session token.
*   We render an iframe (`/dives`) that loads MotherDuck's WebAssembly-powered DuckDB engine.
*   This creates a "Dual Execution" architecture: heavy lifting is done in the cloud, but the actual filtering, cross-filtering, and rendering happen *locally* in the user's browser with 5-20ms latency.

### Celtic RPG Theming (Tailwind v4)
The UI rejects standard corporate SaaS aesthetics in favour of an immersive, game-like experience.
*   **Navigation 3000**: A 3-panel split view (Sidebar, Main Content, Detail Panel) for deep exploration of curricula.
*   **Tactile Elements**: Buttons feature distinct physical compression (`border-b-4`) to provide satisfying, game-like feedback.
*   **Deep Contrast**: `slate-900` backgrounds offset by vibrant, semantic accent colours representing the Celtic Nations (Emerald, Blue, Red, Purple).
*   **Textures**: Subtle SVG noise filters (`bg-stone-texture`) emulate Ogham stones and historical artifacts.

---

*For detailed setup and deployment instructions, refer to the [Root README](../README.md).*
