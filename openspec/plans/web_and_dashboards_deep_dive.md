# Web & Interactive Dashboards Deep Dive

## Executive Summary

The presentation layer of the `education` workspace is divided into two primary paradigms:
1. **Web Frontend (`education/web`)**: A custom TypeScript-based frontend architecture supporting both a core application and a dedicated dashboard.
2. **Interactive Dashboards (`education/marimo`)**: A comprehensive suite of interactive, reactive notebooks and dashboards powered by Marimo, focusing on data exploration, AI integration, and curriculum analysis.

## 1. Web Frontend Architecture (`education/web`)

The `education/web` directory contains a modern TypeScript frontend ecosystem. It is structurally split into two distinct React applications: a primary application (`src/`) and a `dashboard/` sub-application.

### Technology Stack
*   **Language**: TypeScript
*   **Framework**: React
*   **Routing**: TanStack Router (`@tanstack/react-router`) as evidenced by `src/router.tsx`, `src/routes/`, and `.tanstack/`.
*   **Build Tool**: Vite (`vite.config.ts`)
*   **Styling**: Tailwind CSS (`tailwind.config.js`, `postcss.config.js`)
*   **Package Manager**: pnpm & bun (both `pnpm-lock.yaml` and `bun.lock` are present)

### Primary Application (`education/web/src/`)
This application appears to be the main user-facing platform, incorporating AI and translation features.

**Key Features & Routing:**
*   `/`: Home page (`src/pages/Home.tsx`)
*   `/chat`: Chat interface (`src/pages/Chat.tsx`)
*   `/translation`: Translation services (`src/pages/Translation.tsx`)
*   `/curriculum/compare`: Curriculum comparison tool (`src/pages/Compare.tsx`)

**Component Architecture:**
*   **AGUI (Agentic GUI) Components (`src/components/agui/`)**: A notable architectural feature is the `agui` directory, suggesting an interface designed to interact with autonomous agents. Components include `AgentSlots.tsx`, `ComponentRegistry.tsx`, and various specialized UI elements (`Chart`, `CurriculumCard`, `LearningOutcome`, `TranslationResult`).
*   **Other Domains**: Dedicated component folders exist for `chat`, `curriculum`, `translation`, and general `ui`.
*   **Hooks**: Custom hooks like `use-pipeline-stream.ts` indicate complex data streaming, likely for AI responses or processing pipelines.

### Dashboard Application (`education/web/dashboard/`)
The `dashboard/` directory contains a separate, potentially more complex React application, integrating with Convex for backend services and heavily utilizing CopilotKit.

**Technology Additions:**
*   **Backend as a Service**: Convex (`dashboard/convex/` containing `models.ts`, `schema.ts`, `tasks.ts`, `comparisons.ts`). This implies a real-time, reactive database setup.
*   **AI Integration**: Extensive use of CopilotKit (`dashboard/src/routes/api/copilotkit.ts`, `dashboard/ui/src/components/copilot/`).
*   **UI Library Structure**: The dashboard itself seems to have a secondary `ui/` directory (`dashboard/ui/`), which might be a shared component library or a distinct view.

**Dashboard Features (`dashboard/ui/src/components/`):**
*   **Classroom Management**: `TeacherDashboard`, `StudentProgress`.
*   **Generative Elements**: `AssessmentWidget`, `CurriculumCard`, `PronunciationButton`.
*   **Learning Paths**: `LearningPath`, `LessonNode`, `StreakCounter`.
*   **Voice Interactions**: `DialectSelector`, `PronunciationHelper`, `VoiceSearch`, `Waveform`.
*   **State & Integration Hooks**: Hooks demonstrating deep integration with external systems: `useDagsterSharedState` (data orchestration), `useEducationAgent`, `useCoAgent`, `useIrishTTS` (Text-to-Speech), `useIndexingProgress`.

## 2. Marimo Interactive Dashboards (`education/marimo`)

The `education/marimo` directory represents a significant investment in Python-based, reactive notebooks using the Marimo framework. This layer serves as the analytical, experimental, and interactive data presentation tier.

### Core Capabilities & Structure
Marimo notebooks are organized into numerous functional categories, demonstrating a wide array of use cases:

*   **AI & LLM Integration (`ai/`)**:
    *   Implementations for various providers: Anthropic, Bedrock, DeepSeek, Gemini, Groq, OpenAI.
    *   Advanced features: Generative UI (`generative_ui.py`), tool usage (`chat_with_tools.py`), and code interpretation (`code_interpreter.py`, `dagger_code_interpreter.py`).
*   **Data Ops & Cloud Integration (`cloud/`, `cloudflare_data_ops.py`, `cocoindex_flows.py`)**:
    *   Notebooks interacting with GCP (BigQuery, Storage, Sheets) and Modal (`cloud/modal/`).
*   **Mathematical & Educational Analysis (`maths_examples/`)**:
    *   Specific examples likely tailored to the education domain: `curriculum_network_analysis.py`, `grade_distribution_analysis.py`, `question_difficulty_network.py`, `topic_forecasting.py`, `cross_subject_bridges.py`.
    *   Graph database integration is evident (`neo4j_marimo_bridge.py`).
*   **SQL & Database Connectivity (`sql/`)**:
    *   Extensive examples of connecting Marimo to various data sources: Postgres, SQLite, MotherDuck, DuckDB, LanceDB (`lance-demo.py`), Iceberg (`iceberg-demo.py`).
*   **UI Components & Interactivity (`ui/`, `outputs/`, `layouts/`)**:
    *   Comprehensive usage of Marimo's native UI elements (data editors, charts, forms) and layout structures (grids, slides, columns) to build rich dashboard experiences.
*   **Framework Bridging (`frameworks/`)**:
    *   Demonstrations of embedding or connecting Marimo notebooks with web frameworks like FastAPI, Flask, and FastHTML.

### Deployment & Execution
*   The presence of files like `running_as_a_script/` and Dockerfiles in the main web project suggests that these Marimo notebooks can be deployed as standalone interactive web applications or embedded within the larger web ecosystem.
*   The notebooks serve as a bridge between the data engineering layer (Dagster, dlt) and the end-user, allowing for rapid prototyping of data visualizations and interactive analytical tools before they might be formalized into the React frontend.

## Conclusion

The presentation layer of the `education` project is highly sophisticated, employing a dual-track approach. The React/TypeScript frontend provides robust, structured user experiences with integrated AI (AGUI, CopilotKit) and real-time backend capabilities (Convex). Simultaneously, the Marimo notebooks provide a powerful, Python-native environment for data exploration, rapid dashboard creation, and complex curriculum/mathematical analysis, deeply integrated with the project's data and AI infrastructure.