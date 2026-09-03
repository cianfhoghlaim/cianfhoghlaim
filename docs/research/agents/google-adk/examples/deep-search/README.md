# Deep Search Agent Development Kit (ADK) Quickstart

> **Note:** This agent was previously named `gemini-fullstack` and has been renamed to `deep-search`. If you're looking for the old `gemini-fullstack` agent, you're in the right place! All functionality remains the same.

The **Deep Search Agent Development Kit (ADK) Quickstart** is a production-ready blueprint for building a sophisticated, fullstack research agent with Gemini. It's built to demonstrate how the ADK helps structure complex agentic workflows, build modular agents, and incorporate critical Human-in-the-Loop (HITL) steps.

<table>
  <thead>
    <tr>
      <th colspan="2">Key Features</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>🏗️</td>
      <td><strong>Fullstack & Production-Ready:</strong> A complete React frontend and ADK-powered FastAPI backend, with deployment options for <a href="https://cloud.google.com/run">Google Cloud Run</a> and <a href="https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview">Vertex AI Agent Engine</a>.</td>
    </tr>
    <tr>
      <td>🧠</td>
      <td><strong>Advanced Agentic Workflow:</strong> The agent uses Gemini to <strong>strategize</strong> a multi-step plan, <strong>reflect</strong> on findings to identify gaps, and <strong>synthesize</strong> a final, comprehensive report.</td>
    </tr>
    <tr>
      <td>🔄</td>
      <td><strong>Iterative & Human-in-the-Loop Research:</strong> Involves the user for plan approval, then autonomously loops through searching (via Gemini function calling) and refining its results until it has gathered sufficient information.</td>
    </tr>
  </tbody>
</table>

Here is the agent in action:

<img src="https://github.com/GoogleCloudPlatform/agent-starter-pack/blob/main/docs/images/adk_gemini_fullstack.gif?raw=true" width="80%" alt="Gemini Fullstack ADK Preview">

This project adapts concepts from the [Gemini FullStack LangGraph Quickstart](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart) for the frontend app. 

## 🚀 Getting Started: From Zero to Running Agent in 1 Minute
**Prerequisites:** **[Python 3.10+](https://www.python.org/downloads/)**, **[Node.js](https://nodejs.org/)**, **[uv](https://github.com/astral-sh/uv)**

You have two options to get started. Choose the one that best fits your setup:

*   A. **[Google AI Studio (Recommended)](#a-google-ai-studio-recommended)**: The quickest way to get started using a **Google AI Studio API key**. This method involves cloning the sample repository.
*   B. **[Google Cloud Vertex AI](#b-google-cloud-vertex-ai)**: Choose this path if you want to use an existing **Google Cloud project** for authentication and deployment. This method generates a new, prod-ready project using the [agent-starter-pack](https://goo.gle/agent-starter-pack) including all the deployment scripts required.

---

### A. Google AI Studio (Recommended)

You'll need a **[Google AI Studio API Key](https://aistudio.google.com/app/apikey)**.

#### Step 1: Clone Repository
Clone the repository and `cd` into the project directory.

```bash
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents/deep-search
```

#### Step 2: Set Environment Variables
Create a `.env` file in the `app` folder with your API key (see `.env.example` for reference):

```bash
echo "GOOGLE_API_KEY=YOUR_AI_STUDIO_API_KEY" >> app/.env
```

#### Step 3: Install & Run
From the `deep-search` directory, install dependencies and start the servers.

```bash
make install && make dev
```
Your agent is now running at `http://localhost:5173`.

---

### B. Google Cloud Vertex AI (via Agent Starter Pack)

Use the [Agent Starter Pack](https://goo.gle/agent-starter-pack) to create a production-ready project with deployment scripts. This is ideal for cloud deployment scenarios.

You'll need: **[Google Cloud SDK](https://cloud.google.com/sdk/docs/install)** and a **Google Cloud Project** with the **Vertex AI API** enabled.

<details>
<summary>📁 Alternative: Using the cloned repository with Vertex AI</summary>

If you've already cloned the repository (as in Option A) and want to use Vertex AI instead of AI Studio, create a `.env` file in the `app` folder with:

```bash
echo "GOOGLE_GENAI_USE_VERTEXAI=TRUE" >> app/.env
echo "GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID" >> app/.env
echo "GOOGLE_CLOUD_LOCATION=us-central1" >> app/.env
```

Make sure you're authenticated with Google Cloud:
```bash
gcloud auth application-default login
```

Then run `make install && make dev` to start the agent.
</details>

#### Step 1: Create Project from Template
This command uses the [Agent Starter Pack](https://goo.gle/agent-starter-pack) to create a new directory (`my-fullstack-agent`) with all the necessary code.
```bash
# Create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate # On Windows: .venv\Scripts\activate

# Install the starter pack and create your project
pip install --upgrade agent-starter-pack
agent-starter-pack create my-fullstack-agent -a adk@deep-search
```
<details>
<summary>⚡️ Alternative: Using uv</summary>

If you have [`uv`](https://github.com/astral-sh/uv) installed, you can create and set up your project with a single command:
```bash
uvx agent-starter-pack create my-fullstack-agent -a adk@deep-search
```
This command handles creating the project without needing to pre-install the package into a virtual environment.
</details>

You'll be prompted to select a deployment option (Agent Engine or Cloud Run) and verify your Google Cloud credentials.

#### Step 2: Install & Run
Navigate into your **newly created project folder**, then install dependencies and start the servers.
```bash
cd my-fullstack-agent && make install && make dev
```
Your agent is now running at `http://localhost:5173`.

## ☁️ Cloud Deployment

> **Note:** Cloud deployment applies only to projects created with **agent-starter-pack** (Option B).

**Prerequisites:**
```bash
gcloud components update
gcloud config set project YOUR_PROJECT_ID
```

#### Option 1: Deploy with ADK Web UI (Default)

For a quick deployment using the built-in [adk-web](https://github.com/google/adk-web) interface:

```bash
make deploy IAP=true
```

#### Option 2: Deploy with Custom UI (React Frontend)

This agent includes a custom React frontend. To deploy it:

1. **Configure the Dockerfile** - See the [Deploy UI Guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/deploy-ui.html) for the required Dockerfile changes.

2. **Deploy with the frontend port:**
```bash
make deploy IAP=true PORT=5173
```

#### After Deployment

Once deployed, grant users access to your IAP-protected service by following the [Manage User Access](https://cloud.google.com/run/docs/securing/identity-aware-proxy-cloud-run#manage_user_or_group_access) documentation.

For production deployments with CI/CD, see the [Agent Starter Pack Development Guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html#b-production-ready-deployment-with-ci-cd).

## Agent Details

| Attribute | Description |
| :--- | :--- |
| **Interaction Type** | Workflow |
| **Complexity** | Advanced |
| **Agent Type** | Multi Agent |
| **Components** | Multi-agent, Function calling, Web search, React frontend, Human-in-the-Loop |
| **Vertical** | Horizontal |

## How the Agent Thinks: A Two-Phase Workflow

The backend agent, defined in `app/agent.py`, follows a sophisticated workflow to move from a simple topic to a fully-researched report.

The following diagram illustrates the agent's architecture and workflow:

![ADK Gemini Fullstack Architecture](https://github.com/GoogleCloudPlatform/agent-starter-pack/blob/main/docs/images/adk_gemini_fullstack_architecture.png?raw=true)

This process is broken into two main phases:

### Phase 1: Plan & Refine (Human-in-the-Loop)

This is the collaborative brainstorming phase.

1.  **You provide a research topic.**
2.  The agent generates a high-level research plan with several key goals (e.g., "Analyze the market impact," "Identify key competitors").
3.  The plan is presented to **you**. You can approve it, or chat with the agent to add, remove, or change goals until you're satisfied. Nothing happens without your explicit approval.

The plan will contains following tags as a signal to downstream agents,
  - Research Plan Tags

    - [RESEARCH]: Guides info gathering via search.
    - [DELIVERABLE]: Guides creation of final outputs (e.g., tables, reports).
  
  - Plan Refinement Tags

    - [MODIFIED]: Goal was updated.
    - [NEW]: New goal added per user.
    - [IMPLIED]: Deliverable proactively added by AI.

### Phase 2: Execute Autonomous Research

Once you approve the plan, the agent's `research_pipeline` takes over and works autonomously.

1.  **Outlining:** It first converts the approved plan into a structured report outline (like a table of contents).
2.  **Iterative Research & Critique Loop:** For each section of the outline, it repeats a cycle:
    *   **Search:** It performs web searches to gather information.
    *   **Critique:** A "critic" model evaluates the findings for gaps or weaknesses.
    *   **Refine:** If the critique finds weaknesses, the agent generates more specific follow-up questions and searches again. This loop continues until the research meets a high-quality bar.
3.  **Compose Final Report:** After the research loop is complete, a final agent takes all the verified findings and writes a polished report, automatically adding inline citations that link back to the original sources.

You can edit key parameters (Gemini models, research loop iterations) in the `ResearchConfiguration` dataclass within `app/config.py`.

## Customization

You can modify and extend this agent's behavior by editing the backend code.

*   **Modifying Agent Logic:** The core logic for all sub-agents (planner, researcher, critic, composer) is defined in `app/agent.py`. You can change the prompts, tools, or reasoning steps by modifying the agent definitions here.
*   **Adjusting Research Parameters:** Key parameters, such as the Gemini models used or the number of research loop iterations, can be adjusted in the `ResearchConfiguration` dataclass within `app/config.py`.
*   **Syncing with Frontend:** The frontend UI integrates with the backend through specific agent names that process outputs differently (e.g., research findings vs. final report), update the activity timeline with appropriate titles/icons, and track research metrics like website counts. 
    Important agent names include:
    * `section_researcher` & `enhanced_search_executor` - track websites consulted
    * `report_composer_with_citations` - processes final report
    * `interactive_planner_agent` - updates AI messages during planning
    * `plan_generator` and `section_planner` - used for timeline labels
    
    If you rename agents in `app/agent.py`, you must update their names in the frontend code (`/ui`) to maintain functionality.


### Example Interaction

> **User:** A report on the last Google I/O
>
> **Agent:** Here's a research plan for a report on the last Google I/O:
>
> *   Analyze the key announcements and product updates made at Google I/O 2025.
> *   Identify the central themes and strategic directions emphasized by Google during the event, particularly concerning AI, Android, and other emerging technologies like Android XR.
> *   Investigate the reception and industry impact of the major product unveilings and feature enhancements.
> *   Examine any significant shifts or continuities in Google's developer strategy as presented at the conference.
> *   Assess the implications of the announced technologies and initiatives for developers, consumers, and the broader tech landscape.
>
> Does this plan look good, or would you like to refine it further? Once approved, I can initiate the research.
>
> **User:** Looks good!
> *(The agent proceeds to autonomously execute the research, showing its progress on the timeline.)*
>
> **Agent:**
> 
> Google I/O 2025: Key Announcements and Highlights
> ....

## Troubleshooting

If you encounter issues while setting up or running this agent, here are some resources to help you troubleshoot:
- [ADK Documentation](https://google.github.io/adk-docs/): Comprehensive documentation for the Agent Development Kit
- [Vertex AI Authentication Guide](https://cloud.google.com/vertex-ai/docs/authentication): Detailed instructions for setting up authentication
- [Agent Starter Pack Troubleshooting](https://googlecloudplatform.github.io/agent-starter-pack/guide/troubleshooting.html): Common issues


## 🛠️ Technologies Used

### Backend
*   [**Agent Development Kit (ADK)**](https://github.com/google/adk-python): The core framework for building the stateful, multi-turn agent.
*   [**FastAPI**](https://fastapi.tiangolo.com/): High-performance web framework for the backend API.
*   [**Google Gemini**](https://cloud.google.com/vertex-ai/generative-ai/docs): Used for planning, reasoning, search query generation, and final synthesis.

### Frontend
*   [**React**](https://reactjs.org/) (with [Vite](https://vitejs.dev/)): For building the interactive user interface.
*   [**Tailwind CSS**](https://tailwindcss.com/): For utility-first styling.
*   [**Shadcn UI**](https://ui.shadcn.com/): A set of beautifully designed, accessible components.

## Disclaimer

This agent sample is provided for illustrative purposes only. It serves as a basic example of an agent and a foundational starting point for individuals or teams to develop their own agents.

Users are solely responsible for any further development, testing, security hardening, and deployment of agents based on this sample. We recommend thorough review, testing, and the implementation of appropriate safeguards before using any derived agent in a live or critical system.
