# Marimo Reference

> Merged from 41 source files in `marimo/` — skill, KCG summary, Cloudflare deployment, examples, and integration patterns.

---

## Core Marimo Skill


> Source: `docs/data_engineering/marimo/marimo.md`

---
name: Marimo Notebook Assistant
description: Expert assistant for marimo reactive Python notebooks - helps with UI components, reactivity patterns, data visualization, and deployment.
category: Development
tags: [marimo, notebooks, python, data-science, reactive]
---

# Marimo Notebook Assistant

You are a specialized assistant for marimo, the reactive Python notebook framework. You have deep knowledge of marimo's reactive dataflow model, UI components, and best practices.

## Your Expertise

You understand:
- **Reactive Dataflow Model** - DAG-based execution, automatic dependency tracking, deterministic order
- **UI Components** - All mo.ui.* elements, reactivity patterns, forms, composite elements
- **Layout & Output** - mo.hstack, mo.vstack, mo.md, mo.accordion, callouts, styling
- **Control Flow** - mo.stop(), mo.state(), caching strategies, lazy evaluation
- **Data Handling** - DataFrames, interactive tables, SQL support, chart integrations
- **AI Integration** - mo.ui.chat, LLM providers, RAG patterns, generative UI
- **Deployment** - Run as app, WASM export, script execution, ASGI integration

## Reference Materials

Always consult these files in the project root when needed:
- `/home/user/hackathon/marimo-llms.txt` - Comprehensive marimo API and patterns reference

## Your Approach

1. **Understand the Use Case**
   - Is this a data exploration notebook, an interactive app, or a script?
   - What level of interactivity is needed?
   - Are there performance considerations (large datasets, expensive computations)?

2. **Follow Marimo Conventions**
   - Assign UI elements to global variables for reactivity
   - Return outputs from cells as tuples
   - Use `mo.stop()` to gate expensive computation
   - Prefer standard UI reactivity over `mo.state()` (99% of cases)

3. **Provide Working Code**
   - Include all necessary imports
   - Show complete cell definitions
   - Explain reactivity flow between cells
   - Consider error handling and edge cases

4. **Apply Best Practices**
   - Use forms for user-submitted workflows
   - Cache expensive pure functions with `@mo.cache`
   - Use lazy loading for heavy components
   - Validate inputs with form validators

## Core Concepts Quick Reference

### Reactivity Rule

> When a cell runs, marimo automatically runs all cells that reference its defined variables.

This applies to:
- Code edits
- UI element interactions (when element is assigned to global variable)
- Variable deletions

### Cell Structure

```python
@app.cell
def cell_name(mo, input_var):  # refs = inputs
    result = process(input_var)
    mo.md(f"Result: {result}")
    return (result,)  # defs = outputs
```

### Key Constraints

1. **Single definition rule** - each variable defined by exactly one cell
2. **No mutation tracking** - `list.append()`, `obj.attr = val` not tracked
3. **Static analysis** - avoid `exec()`, `eval()` for predictable behavior

## Common Tasks You Can Help With

- **Creating UI** - "How do I make a slider that filters data?"
- **Layout** - "How do I create a dashboard with sidebar?"
- **Forms** - "How do I validate user input before processing?"
- **Charts** - "How do I make a chart where I can select data points?"
- **State** - "How do I synchronize multiple UI elements?"
- **Performance** - "How do I cache expensive computations?"
- **Data** - "How do I create an interactive data explorer?"
- **AI Integration** - "How do I add a chatbot to my notebook?"
- **Deployment** - "How do I deploy this as a web app?"

## UI Components Quick Reference

### Input Elements

```python
# Basic inputs
slider = mo.ui.slider(1, 100, value=50)
text = mo.ui.text(placeholder="Enter name")
dropdown = mo.ui.dropdown(["A", "B", "C"])
checkbox = mo.ui.checkbox(label="Enable")
button = mo.ui.button(label="Click", on_click=lambda v: v + 1)

# Numeric
number = mo.ui.number(start=0, stop=100, step=1)
range_slider = mo.ui.range_slider(0, 100)

# Selection
radio = mo.ui.radio(["Option 1", "Option 2"])
multiselect = mo.ui.multiselect(["A", "B", "C"])

# Date/Time
date = mo.ui.date()
datetime = mo.ui.datetime()

# Files
file = mo.ui.file(filetypes=[".csv", ".json"])

# Advanced
table = mo.ui.table(df, selection="multi")
code_editor = mo.ui.code_editor(language="python")
chat = mo.ui.chat(mo.ai.llm.openai("gpt-4o"))
```

### Composite Elements

```python
# Array - dynamic list
sliders = mo.ui.array([mo.ui.slider(0, 10) for _ in range(5)])

# Dictionary - named elements
controls = mo.ui.dictionary({"x": slider, "y": text})

# Batch - custom layout
form_content = mo.md("""
    Name: {name}
    Email: {email}
""").batch(name=mo.ui.text(), email=mo.ui.text(kind="email"))

# Form - require submission
form = form_content.form(
    submit_button_label="Submit",
    validate=lambda v: "Name required" if not v["name"] else None
)

# Tabs
tabs = mo.ui.tabs({"Tab 1": content1, "Tab 2": content2})
```

### Layout

```python
# Horizontal/Vertical stacks
mo.hstack([a, b, c], justify="space-between", gap=1.0)
mo.vstack([a, b, c], align="stretch", gap=0.5)

# Collapsible sections
mo.accordion({"Section 1": content1, "Section 2": content2})

# Alerts
mo.callout(mo.md("**Warning!**"), kind="warn")

# Sidebar
mo.sidebar([nav_links, settings])

# Deferred rendering
mo.lazy(expensive_component)
```

### Charts (Interactive)

```python
# Altair - returns selected data
chart = mo.ui.altair_chart(alt_chart, chart_selection="interval")
selected_df = chart.value

# Plotly - returns selection info
plot = mo.ui.plotly(fig)
selected_indices = plot.indices

# Matplotlib - pan/zoom
mo.mpl.interactive(plt.gcf())
```

## Common Patterns

### Gated Computation

```python
# Cell 1: Run button
button = mo.ui.run_button(label="Run Analysis")

# Cell 2: Gated by button
mo.stop(not button.value, mo.md("Click button to run"))
result = expensive_analysis()
result
```

### Form Workflow

```python
# Cell 1: Define form
form = mo.md("""
    **Configuration**
    Model: {model}
    Iterations: {iterations}
""").batch(
    model=mo.ui.dropdown(["gpt-4", "claude-3"]),
    iterations=mo.ui.slider(1, 100, value=10)
).form(
    validate=lambda v: "Select a model" if not v["model"] else None
)

# Cell 2: Use form values (only runs after submit)
mo.stop(form.value is None, form)
result = run_model(form.value["model"], form.value["iterations"])
result
```

### Dynamic Filtering

```python
# Cell 1: Filter controls
category = mo.ui.dropdown(df["category"].unique().tolist())
min_value = mo.ui.slider(
    df["value"].min(),
    df["value"].max(),
    label="Minimum Value"
)
mo.hstack([category, min_value])

# Cell 2: Filtered data (auto-updates)
filtered = df[
    (df["category"] == category.value) &
    (df["value"] >= min_value.value)
]
mo.ui.table(filtered)
```

### Synchronized Elements

```python
# Cell 1: Shared state
get_val, set_val = mo.state(50)

# Cell 2: Slider synced to state
slider = mo.ui.slider(0, 100, value=get_val(), on_change=set_val)

# Cell 3: Number input synced to same state
number = mo.ui.number(start=0, stop=100, value=get_val(), on_change=set_val)

# Both elements stay synchronized
mo.hstack([slider, number])
```

### Dashboard Layout

```python
mo.vstack([
    mo.md("# Dashboard"),
    mo.hstack([
        mo.vstack([
            mo.md("### Controls"),
            date_picker,
            category_filter,
            refresh_button
        ]),
        mo.vstack([
            mo.md("### Main View"),
            summary_stats,
            main_chart
        ])
    ], widths=[1, 3]),
    mo.accordion({
        "Data Table": mo.ui.table(data),
        "Export": mo.download(data.to_csv(), "data.csv")
    })
])
```

### Caching Expensive Computations

```python
@mo.cache
def compute_embeddings(texts: list[str]) -> np.ndarray:
    # Only computed once per unique input
    return model.encode(texts)

# Subsequent calls with same args return cached result
embeddings = compute_embeddings(documents)
```

### AI Chatbot

```python
chat = mo.ui.chat(
    mo.ai.llm.openai(
        "gpt-4o",
        system_message="You are a helpful data analyst.",
    ),
    prompts=["Analyze the data", "Create a visualization"],
    show_configuration_controls=True
)
chat
```

### Table Selection Workflow

```python
# Cell 1: Interactive table
table = mo.ui.table(df, selection="multi", page_size=20)
table

# Cell 2: React to selection
selected = table.value
if len(selected) > 0:
    mo.vstack([
        mo.md(f"**Selected {len(selected)} rows**"),
        mo.ui.altair_chart(
            alt.Chart(selected).mark_bar().encode(x="category", y="count()")
        )
    ])
else:
    mo.md("*Select rows to see analysis*")
```

## Control Flow Reference

| Function | Purpose | Example |
|----------|---------|---------|
| `mo.stop(cond, out)` | Halt if condition true | `mo.stop(form.value is None, form)` |
| `mo.state(val)` | Mutable reactive state | `get, set = mo.state(0)` |
| `@mo.cache` | Cache function results | `@mo.cache def fn(x): ...` |
| `@mo.persistent_cache` | Cache to disk | `@mo.persistent_cache def fn(x): ...` |
| `mo.lazy(obj)` | Defer rendering | `mo.lazy(heavy_chart)` |

## SQL Support

```python
# Query dataframes by variable name
result = mo.sql(f"SELECT * FROM df WHERE value > {threshold.value}")

# Query files directly
result = mo.sql(f"SELECT * FROM read_csv('data.csv') LIMIT 100")

# Dynamic queries
selected_cols = mo.ui.multiselect(df.columns.tolist())
result = mo.sql(f"SELECT {', '.join(selected_cols.value)} FROM df")
```

## CLI Commands Reference

```bash
# Edit notebook
marimo edit notebook.py

# Run as app
marimo run notebook.py --port 8080

# Create new notebook
marimo new
marimo new "Create a data dashboard"  # AI-generated

# Export
marimo export html notebook.py -o out.html
marimo export html-wasm notebook.py -o dir/  # Browser-runnable

# Convert from Jupyter
marimo convert notebook.ipynb -o notebook.py

# Check syntax
marimo check notebook.py --fix
```

## Deployment Options

### As Web App
```bash
marimo run notebook.py --host 0.0.0.0 --port 8080
```

### As WASM (Browser-Only)
```bash
marimo export html-wasm notebook.py -o output/ --mode run
# Deploy output/ to any static host (GitHub Pages, Netlify, etc.)
```

### Embedded in FastAPI
```python
from fastapi import FastAPI
from marimo import create_asgi_app

app = FastAPI()
marimo_app = create_asgi_app("notebook.py")
app.mount("/dashboard", marimo_app)
```

## Troubleshooting Guide

### Issue: UI element not reactive
**Solution:**
- Ensure element is assigned to a global variable
- Check that the variable is referenced in dependent cells
- Verify you're reading `.value`, not the element itself

### Issue: Cell not re-running when expected
**Solution:**
- Check variable dependencies are correct
- Ensure no circular dependencies
- Variables must be defined in exactly one cell
- Remember: mutations are not tracked

### Issue: Form value is always None
**Solution:**
- Form value is None until submitted
- Use `mo.stop()` to gate computation on form submission
- Check validation function isn't blocking submission

### Issue: Performance is slow
**Solution:**
- Use `@mo.cache` for expensive pure functions
- Use `mo.lazy()` for heavy components
- Enable lazy runtime mode in settings
- Use pagination for large tables

### Issue: Chart selections not working
**Solution:**
- Use `mo.ui.altair_chart()` or `mo.ui.plotly()`
- Ensure chart has selection parameters enabled
- Access selected data via `.value` property

## Best Practices Checklist

### Do
- [ ] Assign UI elements to global variables
- [ ] Use `mo.stop()` to gate expensive computation
- [ ] Use `@mo.cache` for expensive pure functions
- [ ] Use forms for user-submitted workflows
- [ ] Use lazy loading for heavy components
- [ ] Return cell outputs as tuples
- [ ] Keep cells focused on single responsibilities

### Don't
- [ ] Use `mo.state()` when standard reactivity suffices
- [ ] Mutate objects and expect tracking
- [ ] Use dynamic code generation (`exec`, `eval`)
- [ ] Define same variable in multiple cells
- [ ] Store secrets in notebook code
- [ ] Forget to handle loading/error states

## Next Steps

When you're ready, tell me:
- What kind of notebook are you building? (data exploration, interactive app, report)
- What specific feature or problem are you working on?
- What data or APIs are you working with?

I'll provide specific guidance following marimo's reactive patterns and best practices.

## Resources

- **Documentation:** https://docs.marimo.io/
- **GitHub:** https://github.com/marimo-team/marimo
- **Tutorials:** `marimo tutorial intro|dataflow|ui|markdown|plots|sql|layout`
- **Local Reference:** `/home/user/hackathon/marimo-llms.txt`


## KCG Summary


> Source: `docs/data_engineering/marimo/KCG_SUMMARY.md`

# marimo — KCG Summary

## What It Is
marimo is a reactive Python notebook framework (alternative to Jupyter) with Git-friendly .py file storage, deterministic execution, and built-in UI components. This directory contains the full marimo framework source with 40+ example notebooks covering UI elements, SQL integration, AI/LLM chat, control flow, markdown, layouts, testing, cloud deployment, and third-party integrations (HuggingFace, MotherDuck embeddings, Sage).

## Why This Matters for Kings' College Galway
marimo is the primary notebook/dashboard tool for the oideachais education data platform. The SQL notebooks demonstrate how to build reactive dashboards over DuckDB/MotherDuck curriculum data, the AI examples show how to embed LLM-powered chat into educational analytics, and the framework integration examples (FastAPI, Flask) inform how the Kings' College web frontend (TanStack Start) can embed marimo notebooks as interactive data exploration tools for teachers and students.

## Key Patterns Preserved
38 .md files remain, including:
- `README.md` — Overview of all marimo examples
- `marimo/README.md` — Full marimo framework README with architecture overview
- `marimo/SECURITY.md` — Security policy
- `marimo/README_Chinese.md`, `README_Japanese.md`, `README_Spanish.md`, `README_Traditional_Chinese.md` — Internationalized docs
- `ai/README.md`, `ai/chat/README.md`, `ai/tools/README.md` — AI/LLM integration patterns
- `sql/README.md`, `sql/misc/README.md` — SQL notebook patterns
- `cloud/README.md`, `cloud/modal/README.md`, `cloudflare/README.md` — Cloud deployment patterns
- `frameworks/README.md` + 4 framework-specific READMEs (FastAPI, Flask, FastHTML)
- `control_flow/README.md`, `layouts/README.md`, `markdown/README.md`, `misc/README.md`, `testing/README.md`, `ui/README.md`
- `third_party/README.md` + HuggingFace, MotherDuck, Sage integration READMEs

## Source Files
Full source removed (2026-06-06). Available at https://github.com/marimo-team/marimo

## What Was Removed
Python notebooks (.py), TypeScript/CSS source, JSON/YAML configs, HTML templates, Docker files, shell scripts, test snapshots, SVG images, lock files, .gitignore files


## Cloudflare Deployment


> Source: `docs/data_engineering/marimo/marimo_cloudflare.md`

# Building an Interactive Learning Platform for Irish Mathematics

A hybrid architecture combining browser-based notebooks, edge orchestration, and remote development environments can deliver the flexibility needed for Leaving Certificate mathematics and computer science education. **Marimo's WebAssembly export enables instant, zero-installation interactivity** for lightweight exercises, while **Cloudflare Durable Objects provide globally-distributed session state**, and **Coder workspaces deliver full development environments** for advanced coursework—all orchestrated through a **TanStack Start frontend** deployed at the edge.

## Marimo WASM delivers instant interactivity with key constraints

Marimo notebooks run entirely in-browser via Pyodide, eliminating server infrastructure for basic exercises. The architecture consists of a Python kernel running in a WebWorker, a TypeScript frontend issuing commands, and an RPC bridge replacing traditional server communication. For Leaving Certificate mathematics, all essential packages are fully supported: **NumPy, SciPy, SymPy, Matplotlib**, and pandas work out of the box with automatic installation when imported.

Three embedding approaches serve different needs. **iframe embedding** with `sandbox="allow-scripts allow-same-origin"` provides the simplest integration while enabling localStorage persistence for student progress. **Marimo Islands** embed individual reactive cells directly into lesson pages—ideal for interactive tutorials where explanations and computations interweave. The **marimo-snippets NPM package** converts static code examples into live notebooks, perfect for documentation sites.

Technical constraints shape where WASM fits in the architecture:

- **Memory ceiling of 2GB** limits dataset sizes and complex simulations
- **Single-threaded execution** means no parallel processing (though adequate for educational workloads)
- **Persistent storage relies on localStorage** when embedding with `allow-same-origin`; without server integration, progress saving is limited to browser storage or manual export
- **Initial load times of several seconds** occur as Pyodide downloads (~tens of MB for the scientific stack)
- **Chrome delivers best performance** and compatibility for WASM execution

For an Irish educational context, marimo handles bilingual content naturally—markdown cells support Irish language text, LaTeX renders mathematical notation in either language, and UI elements can be labeled bilingually through standard internationalization patterns.

## Cloudflare Durable Objects enable stateful edge coordination

Durable Objects solve the critical challenge of maintaining user progress and coordinating sessions across a globally-distributed platform. Each DO combines compute with **strongly-consistent storage** (now up to 10GB via SQLite backend), with single-threaded execution guaranteeing serialized access—essential for preventing race conditions in progress tracking.

For WebSocket connections powering terminal sessions or collaborative features, the **WebSocket Hibernation API** dramatically reduces costs. Without hibernation, maintaining 100 WebSocket connections with periodic messages costs approximately **$139/month**; with hibernation, the same workload drops to roughly **$10/month**. The DO hibernates while connections remain live on Cloudflare's network, only waking to process messages:

```javascript
export class StudentSessionDO extends DurableObject {
  async fetch(request) {
    const [client, server] = Object.values(new WebSocketPair());
    this.ctx.acceptWebSocket(server);
    server.serializeAttachment({ studentId: "123", lessonId: "calculus-01" });
    return new Response(null, { status: 101, webSocket: client });
  }

  async webSocketMessage(ws, message) {
    const { studentId } = ws.deserializeAttachment();
    // Process terminal input, update progress
  }
}
```

**Orchestrating Coder workspaces from Workers** requires a hybrid pattern. Enable Smart Placement to run Workers geographically closer to your Coder infrastructure, reducing round-trip latency for API calls. Workers handle authentication, rate limiting, and session routing at the edge, then proxy workspace creation and terminal connections to self-hosted Coder servers. Authentication tokens flow through Workers as intermediaries—the Worker validates the student's JWT, then issues requests to Coder's API with service credentials stored as secrets.

Rate limiting for educational platforms works best with **per-user Durable Objects** rather than global limiters (which create bottlenecks). Each student's rate limit state lives in their session DO, enabling fair resource allocation without single-point contention.

## Coder workspaces provide full development environments

For advanced coursework requiring persistent file systems, IDE integration, or complex dependencies, Coder delivers enterprise-grade cloud development environments. The architecture separates **coderd** (control plane managing workspace lifecycle) from **provisionerd** (executing Terraform to create infrastructure) and the **Coder Agent** (running inside workspaces providing SSH, port forwarding, and health checks).

Workspace templates use Terraform, enabling precise control over educational environments:

```hcl
resource "coder_agent" "main" {
  os   = "linux"
  arch = "amd64"
  startup_script = <<-EOF
    pip install numpy scipy sympy matplotlib jupyter
    # Pre-configure Irish language locales
    sudo locale-gen ga_IE.UTF-8
  EOF
}

module "jupyter" {
  source   = "registry.coder.com/modules/jupyter/coder"
  agent_id = coder_agent.main.id
}
```

**Coder's REST API enables complete programmatic control**—create workspaces on-demand when students begin advanced labs, configure per-course quotas, and monitor usage. The `/workspaces/{id}/watch` endpoint provides real-time status updates via Server-Sent Events, enabling the frontend to show workspace readiness.

Compared to iximiuz Labs' Firecracker approach, Coder trades **sub-second boot times (~125ms for Firecracker) for richer features**: native VS Code and JetBrains integration, built-in persistent volumes, and Terraform's infrastructure flexibility. For educational use where workspaces run for hours and IDE experience matters, Coder's tradeoffs favor developer productivity over cold-start speed.

## TanStack Start orchestrates the frontend at the edge

TanStack Start, now in Release Candidate stage with official Cloudflare Workers support, provides the frontend framework. Its **client-first architecture with full-document SSR** suits educational platforms with heavy interactivity—quizzes, simulations, and embedded notebooks benefit from client-side execution, while course listings and marketing pages leverage server rendering for SEO.

Cloudflare deployment uses the new Vite plugin approach:

```typescript
// vite.config.ts
import { cloudflare } from '@cloudflare/vite-plugin'
import { tanstackStart } from '@tanstack/react-start/plugin/vite'

export default defineConfig({
  plugins: [
    cloudflare({ viteEnvironment: { name: 'ssr' } }),
    tanstackStart(),
  ],
})
```

**Server functions bridge edge and origin** seamlessly. Create authenticated endpoints that validate student sessions, query progress from Durable Objects, or proxy requests to Coder:

```typescript
export const createWorkspace = createServerFn({ method: 'POST' })
  .inputValidator(z.object({ templateId: z.string(), courseId: z.string() }))
  .handler(async ({ data }) => {
    const coderResponse = await fetch(`${env.CODER_URL}/api/v2/workspaces`, {
      headers: { 'Coder-Session-Token': env.CODER_TOKEN },
      body: JSON.stringify({ template_id: data.templateId })
    });
    return coderResponse.json();
  });
```

For bilingual Irish/English content, TanStack Router's type-safe search parameters elegantly handle language selection: `?lang=ga` persists through navigation, enabling deep-linkable bilingual states. Course content can load from language-specific files based on this parameter.

## Translating iximiuz Labs patterns to Cloudflare architecture

iximiuz Labs' Foreman/Conductor/Bender architecture offers valuable patterns adaptable to this hybrid approach. Their **separation of concerns** maps directly:

| iximiuz Component | Cloudflare Equivalent | Function |
|-------------------|----------------------|----------|
| Foreman | Cloudflare Workers + D1/KV | Orchestration, auth, content management |
| Conductor | Durable Objects (WebSocket) | Terminal sessions, real-time communication |
| Bender | Coder API | Workspace provisioning and management |
| Examiner | Custom agent in Coder workspace | Solution checking, task verification |

The **DAG-based task execution** for automatic solution checking translates well. Define exercise verification as YAML task graphs, execute them via a lightweight daemon inside Coder workspaces, and report completion through WebSocket to Durable Objects. gRPC provides reliable state synchronization between verification agents and the coordination layer—more robust than polling.

**Warm pools** apply differently: rather than pre-spawning Firecracker VMs, maintain pre-warmed Coder workspace images with all dependencies installed. Coder's template caching and prebuilt images achieve similar faster-startup goals.

## Recommended hybrid architecture

The optimal architecture layers browser, edge, and origin:

```
┌─────────────────── Browser Layer ───────────────────┐
│  TanStack Start SPA        Marimo WASM Notebooks   │
│  (Interactive UI)          (Lightweight exercises)  │
└───────────────────────────┬─────────────────────────┘
                            │
┌─────────────── Cloudflare Edge Layer ───────────────┐
│  Workers (API Gateway)    Durable Objects           │
│  - Auth/JWT validation    - User progress (SQLite)  │
│  - Rate limiting          - WebSocket sessions      │
│  - Coder orchestration    - Notebook state sync     │
│                                                     │
│  KV (Content cache)       D1 (Course metadata)     │
└───────────────────────────┬─────────────────────────┘
                            │ Smart Placement
┌─────────────── Self-Hosted Origin ──────────────────┐
│  Coder Control Plane      PostgreSQL                │
│  - Workspace lifecycle    - User data               │
│  - Template management    - Progress persistence    │
│                                                     │
│  Coder Workers (Kubernetes/Docker)                  │
│  - Student workspaces with Python/math tools        │
│  - JupyterLab, VS Code integration                 │
│  - Solution verification agents                     │
└─────────────────────────────────────────────────────┘
```

**Content routing by complexity**: Leaving Certificate Paper 1 (algebra, functions, calculus) works beautifully in Marimo WASM—students manipulate equations, visualize graphs, and solve problems without any server infrastructure. Paper 2 (geometry, statistics, probability) similarly fits the in-browser model. Computer science coursework requiring file persistence, package installation beyond Pyodide's capabilities, or full IDE features escalates to Coder workspaces.

## Answering key technical questions

**Marimo WASM constraints**: The 2GB memory limit and single-threaded execution suffice for educational mathematics—even intensive symbolic computation in SymPy runs comfortably. State persistence requires localStorage (limited to ~5MB per origin) or implementing custom sync to your backend via `fetch()` calls from notebook code. Packages with complex native dependencies unavailable in Pyodide (like TensorFlow) won't work, but the core scientific Python stack is complete.

**Durable Objects and WebSockets**: DO's Hibernation API handles terminal session multiplexing efficiently. Each student session gets its own DO with hibernating WebSocket connections; the 2KB `serializeAttachment` limit stores session metadata, while the SQLite backend stores progress data. For collaborative features (shared notebooks, study groups), create per-room DOs that broadcast messages to all connected participants.

**Workers proxying Coder**: Effective but requires careful timeout handling—workspace creation can take 30-60 seconds, exceeding Workers' default CPU limits. Use Workers to initiate workspace creation and return immediately with a tracking ID, then have clients poll a separate status endpoint or receive updates via WebSocket from a Durable Object monitoring the Coder API.

**Authentication patterns**: Implement OAuth (Google, GitHub, or Irish educational SSO) at the Workers layer. After authentication, issue short-lived JWTs validated at the edge. For Coder access, Workers exchange user JWTs for Coder API tokens stored as secrets, never exposing Coder credentials to clients.

**Bilingual content in notebooks**: Marimo markdown cells render both English and Irish text natively. For dynamic language switching, use `mo.ui.dropdown` to select language, then conditionally display content:

```python
lang = mo.ui.dropdown(["English", "Gaeilge"], value="English")
content = {"English": "Solve for x:", "Gaeilge": "Réitigh do x:"}
mo.md(content[lang.value])
```

## Implementation priorities for the Irish Leaving Certificate

Start with **Marimo WASM for immediate impact**—no infrastructure required. Export notebooks covering key syllabus topics (quadratics, trigonometry, differentiation) and host on Cloudflare Pages. This validates content approaches and gathers user feedback before investing in Coder infrastructure.

**Phase two adds progress tracking** via Durable Objects. Each student's DO stores completed exercises, quiz scores, and checkpoint states. The SQLite backend handles complex queries like "show all students struggling with integration" for teacher dashboards.

**Phase three introduces Coder workspaces** for computer science components—Python programming, data structures, and computational problem-solving requiring persistent environments.

Throughout, the TanStack Start frontend unifies the experience, embedding Marimo iframes for interactive content, managing authentication, and routing students between browser-based exercises and full development environments based on lesson requirements. The architecture scales from a single developer serving hundreds of students to institutional deployments serving thousands, with costs dominated by Coder infrastructure rather than edge compute.

> Source: `docs/data_engineering/marimo/cloudflare/README.md`

# Marimo Notebook example

Example of deploying marimo in cloudflare.

```
pnpm run deploy
```


## AI Integration Patterns


> Source: `docs/data_engineering/marimo/ai/README.md`

# AI 🤖

These examples showcase a few simple applications of AI.

- 💬 [`chat/`](chat/): creating chatbots with marimo, using [`mo.ui.chat`](https://docs.marimo.io/api/inputs/chat.html#marimo.ui.chat)
- 🛢️ [`data/`](data/): making data labeling and model comparison tools
- 🛠 [`tools/`](tools/): interacting with external functions and services with function calling, returning rich responses
- 🍿 [`misc/`](misc/): miscellaneous AI examples

> [!TIP]
> Submit a
> [pull request](https://github.com/marimo-team/marimo/pulls) to add an example!

## Running examples

The requirements of each notebook are serialized in them as a top-level
comment. Here are the steps to open an example notebook:

1. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
2. Open an example with `uvx marimo edit --sandbox <notebook-url>`

> [!TIP]
> The [`--sandbox` flag](https://docs.marimo.io/guides/editor_features/package_management.html) opens the notebook in an isolated virtual environment,
> automatically installing the notebook's dependencies 📦

You can also open notebooks without `uv`, in which case you'll need to
manually [install marimo](https://docs.marimo.io/getting_started/index.html#installation)
first. Then run `marimo edit <notebook-url>`; however, you'll also need to
install the requirements yourself.


> Source: `docs/data_engineering/marimo/ai/chat/README.md`

# Chat 💬

These examples show how to make chatbots with marimo, using [`mo.ui.chat`](https://docs.marimo.io/api/inputs/chat.html#marimo.ui.chat).

- `custom.py` shows how to make a custom chatbot.
- `streaming_custom.py` shows how to make a custom chatbot with streaming responses (delta-based).
- `openai_example.py` shows how to make a chatbot powered by OpenAI models (streaming by default).
- `anthropic_example.py` shows how to make a chatbot powered by Anthropic models (streaming by default).
- `gemini.py` shows how to make a chatbot powered by Google models like Gemini (streaming by default).
- `groq_example.py` shows how to make a chatbot powered by Groq models (streaming by default).
- `mlx_chat.py` shows a simple chatbot using local on-device models with Apple's [MLX](https://github.com/ml-explore/mlx), a machine learning framework from Apple that is similar to JAX and PyTorch. This specific example uses the [mlx-lm](https://github.com/ml-explore/mlx-examples/tree/main/llms) library. Note that Apple Silicon chips are required for using MLX.
- `llm_datasette.py` shows how to make a chatbot powered by Simon W's LLM library.
- `dagger_code_interpreter.py` shows how to make a basic code-interpreter chatbot powered by Dagger containers.
- `recipe_bot.py` shows how to make a chatbot that can parse recipes from images.
- `simplemind_example.py` shows how to integrate [simplemind](https://github.com/kennethreitz/simplemind).
- `generative_ui.py` shows how to make a chatbot that can generate UI code.

## Streaming Responses

All built-in models (OpenAI, Anthropic, Google, Groq, Bedrock) stream responses using delta-based streaming. If a model doesn't support streaming, it will automatically fall back to non-streaming mode.

For custom models, create an async generator function that yields delta chunks (new content only).

See `streaming_custom.py` for a complete example of custom streaming.

Chatbot's in marimo are _reactive_: when the chatbot responds with a message,
all other cells referencing the chatbot are automatically run or marked
stale, with the chatbot's response stored in the object's `value` attribute.
You can use this to make notebooks that respond to the chatbot's response
in arbitrary ways. For example, you can make agentic notebooks!

Once you understand the basics, for a more interesting example, check out
[our notebook that lets you talk to any GitHub repo](../../third_party/sage/),
powered by [storia-ai/sage](https://github.com/storia-ai/sage). This example demonstrates advanced usage
of `ui.chat`, using `langchain` to construct a RAG-powered chatbot, served by
an async generator callback function.

## Running examples

The requirements of each notebook are serialized in them as a top-level
comment. Here are the steps to open an example notebook:

1. [Install marimo](https://docs.marimo.io/getting_started/index.html#installation)
2. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
3. Open an example with `marimo edit --sandbox <notebook.py>`.

> [!TIP]
> The [`--sandbox` flag](https://docs.marimo.io/guides/editor_features/package_management.html) opens the notebook in an isolated virtual environment,
> automatically installing the notebook's dependencies 📦

You can also open notebooks without `uv`, with just `marimo edit <notebook.py>`;
however, you'll need to install the requirements yourself.


> Source: `docs/data_engineering/marimo/ai/tools/README.md`

# AI tool use 🛠

These are examples of using AI that interact with external functions and
services.

> [!TIP]
> Submit a
> [pull request](https://github.com/marimo-team/marimo/pulls) to add an example!

## Running examples

The requirements of each notebook are serialized in them as a top-level
comment. Here are the steps to open an example notebook:

1. [Install marimo](https://docs.marimo.io/getting_started/index.html#installation)
2. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
3. Open an example with `marimo edit --sandbox <notebook.py>`.

> [!TIP]
> The [`--sandbox` flag](https://docs.marimo.io/guides/editor_features/package_management.html) opens the notebook in an isolated virtual environment,
> automatically installing the notebook's dependencies 📦

You can also open notebooks without `uv`, with just `marimo edit <notebook.py>`;
however, you'll need to install the requirements yourself.


## Cloud & Modal Deployment


> Source: `docs/data_engineering/marimo/cloud/README.md`

# Cloud ☁️

These examples show how to use various cloud provider APIs.

> [!TIP]
> Submit a
> [pull request](https://github.com/marimo-team/marimo/pulls) to add an example!

## Running examples

The requirements of each notebook are serialized in them as a top-level
comment. Here are the steps to open an example notebook:

1. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
2. Open an example with `uvx marimo edit --sandbox <notebook-url>`

> [!TIP]
> The [`--sandbox` flag](https://docs.marimo.io/guides/editor_features/package_management.html) opens the notebook in an isolated virtual environment,
> automatically installing the notebook's dependencies 📦

You can also open notebooks without `uv`, in which case you'll need to
manually [install marimo](https://docs.marimo.io/getting_started/index.html#installation)
first. Then run `marimo edit <notebook-url>`; however, you'll also need to
install the requirements yourself.


> Source: `docs/data_engineering/marimo/cloud/modal/README.md`

# Running marimo on Modal

This folder contains examples of how to run marimo notebooks on
[Modal](https://modal.com/), making it easy to get access to cloud GPUs. To get
started, first create a modal account and follow their onboarding. You'll also
need to install the [uv package manager](https://docs.astral.sh/uv/).

## Editable notebooks
[modal_edit.py](modal_edit.py) has an example of how to spin up an editable
marimo notebook that runs on a Modal container. Run with

```bash
uvx -p 3.12 modal run modal_edit.py
```

You can configure your GPU selection by editing `modal_edit`.

## Run as apps

[modal_app.py](modal_app.py) has an example of how to deploy a read-only marimo
notebook as an app on Modal. Run with

```bash
uvx -p 3.12 \
  --with modal \
  --with marimo \
  modal serve modal_app.py
```


## Framework Integrations


> Source: `docs/data_engineering/marimo/frameworks/README.md`

# Frameworks 🧩

These examples show how to use marimo with various web/ASGI frameworks, such as FastAPI, Flask, and FastHTML.

> [!TIP]
> Submit a
> [pull request](https://github.com/marimo-team/marimo/pulls) to add an example!

## Running examples

Each example includes a `README.md` file with instructions for running it.


> Source: `docs/data_engineering/marimo/frameworks/fastapi-endpoint/README.md`

# FastAPI + marimo, as an API endpoint

This is a simple example of how to use FastAPI with marimo. This example turns marimo notebooks into an API endpoint, which can be embedded in any FastAPI app.

- Turning functions defined in a notebook into an API endpoint
- Overriding global variables and returning cell outputs

## Running the app

1. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
2. Run the app with `uv run --no-project main.py`
3. Then run `curl http://localhost:8000/greet?name=coder`


> Source: `docs/data_engineering/marimo/frameworks/fastapi/README.md`

# FastAPI + marimo

This is a simple example of how to use FastAPI with marimo. This example programmatically creates multiple marimo apps from a directory, and then serves them as a single FastAPI app.

This example includes:

- Authentication
- Serving multiple marimo apps from a directory
- A home page listing all the apps
- Loading environment variables from a `.env` file
- Basic logging

## Running the app

1. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
2. Run the app with `uv run --no-project main.py`


> Source: `docs/data_engineering/marimo/frameworks/flask/README.md`

# Flask + marimo

This is a simple example of how to use Flask with marimo. This example programmatically creates multiple marimo apps from a directory, and then serves them as a single Flask app.

This example includes:

- Authentication
- Serving multiple marimo apps from a directory
- A home page listing all the apps
- Loading environment variables from a `.env` file
- Basic logging

## Running the app

1. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
2. Run the app with `uv run --no-project main.py`

This will start the Flask development server.


> Source: `docs/data_engineering/marimo/frameworks/fasthtml/README.md`

# FastHTML + marimo

This is a simple example of how to use FastHTML with marimo. This example programmatically creates multiple marimo apps from a directory, and then serves them as a single FastHTML app.

## Running the app

1. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
2. Run the app with `uv run --no-project main.py`


## Data & SQL


> Source: `docs/data_engineering/marimo/sql/README.md`

# SQL 🛢️

These examples show how to use marimo's built-in support for SQL, which
is powered by [duckdb](https://duckdb.org/), a fast in-process
analytical database.

- `querying_dataframes.py` shows hows to query Pandas or Polars dataframes
- `paremetrizing_sql_queries.py` shows hows to parametrize queries with Python values
- `read_csv.py` shows hows to read CSV data into duckdb
- `read_json.py` shows hows to read JSON data into duckdb
- `read_parquet.py` shows hows to read parquet data into duckdb
- `connect_to_persistent_db.py` shows hows to connect to a duckdb persistent database
- `connect_to_sqlite.py` shows hows to connect to a SQLite database
- `connect_to_postgres.py` shows hows to connect to a PostgreSQL database
- `connect_to_motherduck.py` shows hows to connect to [motherduck](https://motherduck.com)
- `histograms.py` shows hows to plot histograms of a column's values
- [`misc/`](misc/) contains illustrative examples

> [!TIP]
> For a broad overview of using SQL in marimo, run `marimo tutorial sql` at the
> command-line.

Consult the [duckdb documentation](https://duckdb.org/docs/index) for a
comprehensive guide on duckdb.

## Running examples

The requirements of each notebook are serialized in them as a top-level
comment. Here are the steps to open an example notebook:

1. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
2. Open an example with `uvx marimo edit --sandbox <notebook-url>`

> [!TIP]
> The [`--sandbox` flag](https://docs.marimo.io/guides/editor_features/package_management.html) opens the notebook in an isolated virtual environment,
> automatically installing the notebook's dependencies 📦

You can also open notebooks without `uv`, in which case you'll need to
manually [install marimo](https://docs.marimo.io/getting_started/index.html#installation)
first. Then run `marimo edit <notebook-url>`; however, you'll also need to
install the requirements yourself.


> Source: `docs/data_engineering/marimo/sql/misc/README.md`

# Misc. SQL examples 🛢️

This folder contains illustrative examples of using SQL in marimo.

> [!TIP]
> For a broad overview of using SQL in marimo, run `marimo tutorial sql` at the
> command-line.

## Running examples

The requirements of each notebook are serialized in them as a top-level
comment. Here are the steps to open an example notebook:

1. [Install marimo](https://docs.marimo.io/getting_started/index.html#installation)
2. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
3. Open an example with `marimo edit --sandbox <notebook.py>`.

> [!TIP]
> The [`--sandbox` flag](https://docs.marimo.io/guides/editor_features/package_management.html) opens the notebook in an isolated virtual environment,
> automatically installing the notebook's dependencies 📦

You can also open notebooks without `uv`, with just `marimo edit <notebook.py>`;
however, you'll need to install the requirements yourself.


## Third-Party Integrations


> Source: `docs/data_engineering/marimo/third_party/README.md`

# Third-party 📦

These examples showcase how to use various third-party packages in marimo.

> [!TIP]
> Submit a
> [pull request](https://github.com/marimo-team/marimo/pulls) to add an example!

## Running examples

The requirements of each notebook are serialized in them as a top-level
comment. Here are the steps to open an example notebook:

1. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
2. Open an example with `uvx marimo edit --sandbox <notebook-url>`

> [!TIP]
> The [`--sandbox` flag](https://docs.marimo.io/guides/editor_features/package_management.html) opens the notebook in an isolated virtual environment,
> automatically installing the notebook's dependencies 📦

You can also open notebooks without `uv`, in which case you'll need to
manually [install marimo](https://docs.marimo.io/getting_started/index.html#installation)
first. Then run `marimo edit <notebook-url>`; however, you'll also need to
install the requirements yourself.


> Source: `docs/data_engineering/marimo/third_party/huggingface/README.md`

# HuggingFace 📦

These examples showcase how to use HuggingFace's models in marimo.

- You can find a list of these models [here](https://huggingface.co/models).
- These examples are easily deployable on [HuggingFace's Spaces](https://huggingface.co/new-space?template=marimo-team%2Fmarimo-app-template). Or check out our templates:
  - [Basic application template](https://huggingface.co/spaces/marimo-team/marimo-app-template/tree/main)
  - [Chatbot template](https://huggingface.co/spaces/marimo-team/marimo-chatbot-template/tree/main)
  - [Text-to-image template](https://huggingface.co/spaces/marimo-team/marimo-text-to-image-template/tree/main)

> [!TIP]
> Submit a
> [pull request](https://github.com/marimo-team/marimo/pulls) to add an example!

## Running examples

The requirements of each notebook are serialized in them as a top-level
comment. Here are the steps to open an example notebook:

1. [Install marimo](https://docs.marimo.io/getting_started/index.html#installation)
2. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
3. Open an example with `marimo edit --sandbox <notebook.py>`.

> [!TIP]
> The [`--sandbox` flag](https://docs.marimo.io/guides/editor_features/package_management.html) opens the notebook in an isolated virtual environment,
> automatically installing the notebook's dependencies 📦

You can also open notebooks without `uv`, with just `marimo edit <notebook.py>`;
however, you'll need to install the requirements yourself.


> Source: `docs/data_engineering/marimo/third_party/motherduck/embeddings/README.md`

# Explore embeddings with MotherDuck

This notebook explores embeddings with MotherDuck's embeddings API.


> Source: `docs/data_engineering/marimo/third_party/sage/README.md`

# Sage: chat with any codebase 🤖💬

This example shows how to create a notebook that lets you
_chat with any codebase_, using [Sage](https://github.com/storia-ai/sage)
from Storia AI. It uses [`mo.ui.chat`](https://docs.marimo.io/api/inputs/chat.html) with a custom chat function that
implements a RAG-powered search over any GitHub repository of your choosing.
The result is a chatbot that you can use to incrementally explore a codebase
and even its associated GitHub issues.

![sage-chat](continue_chatting_with_sage.png)


## Running the chat notebook


### Index a GitHub repo with sage

This notebook has its Python dependencies inlined in it, but you do need
to set up some non-Python dependencies before you can run it. To run locally,
follow these instructions. Get the full instructions at
[the sage repo](https://github.com/storia-ai/sage).


```bash
docker rm -f marqo
docker pull marqoai/marqo:latest
docker run --name marqo -it -p 8882:8882 marqoai/marqo:latest
```

Then install [Ollama](https://github.com/ollama/ollama) and run

```bash
ollama pull llama3.1
```

Next, run

```
pipx install git+https://github.com/Storia-AI/sage.git@main
```

and choose a GitHub repo to index with (eg)

```bash
export GITHUB_REPO=marimo-team/marimo
```

Finally run

```
sage-index $GITHUB_REPO
```

### Run the marimo notebook!

Open the marimo notebook with

```bash
marimo edit --sandbox chat_with_github.py -- $GITHUB_REPO
```

and start chatting with your repo!

You can also deploy this notebook as a web app, with

```bash
marimo run --sandbox chat_with_github.py -- $GITHUB_REPO
```


> [!TIP]
> The [`--sandbox` flag](https://docs.marimo.io/guides/editor_features/package_management.html) opens the notebook in an isolated virtual environment,
> automatically installing the notebook's dependencies 📦

You can also open the notebook without `uv`, with just `marimo edit
chat_with_github_repo.py`; however, you'll need to install the requirements
yourself.


## UI, Layouts & Control Flow


> Source: `docs/data_engineering/marimo/ui/README.md`

# UI 🖱️

These basic examples show how to use marimo's built-in UI elements.

> [!TIP]
> New to marimo? Run `marimo tutorial intro` and `marimo tutorial ui`
> at the command line first!

_Looking for examples on making chatbots? Check out the [`ai/chat`](../ai/chat)
examples folder_.

## Running examples

The requirements of each notebook are serialized in them as a top-level
comment. Here are the steps to open an example notebook:

1. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
2. Open an example with `uvx marimo edit --sandbox <notebook-url>`

> [!TIP]
> The [`--sandbox` flag](https://docs.marimo.io/guides/editor_features/package_management.html) opens the notebook in an isolated virtual environment,
> automatically installing the notebook's dependencies 📦

You can also open notebooks without `uv`, in which case you'll need to
manually [install marimo](https://docs.marimo.io/getting_started/index.html#installation)
first. Then run `marimo edit <notebook-url>`; however, you'll also need to
install the requirements yourself.


> Source: `docs/data_engineering/marimo/layouts/README.md`

# Layouts 📽️

These examples show how to use marimo's built-in features for laying out
notebooks in interesting ways, such as presenting notebooks as slides,
adding sidebars, and arranging cells into columns while editing.

> [!TIP]
> Submit a
> [pull request](https://github.com/marimo-team/marimo/pulls) to add an example!


## Running examples

The requirements of each notebook are serialized in them as a top-level
comment. Here are the steps to open an example notebook:

1. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
2. Open an example with `uvx marimo edit --sandbox <notebook-url>`

> [!TIP]
> The [`--sandbox` flag](https://docs.marimo.io/guides/editor_features/package_management.html) opens the notebook in an isolated virtual environment,
> automatically installing the notebook's dependencies 📦

You can also open notebooks without `uv`, in which case you'll need to
manually [install marimo](https://docs.marimo.io/getting_started/index.html#installation)
first. Then run `marimo edit <notebook-url>`; however, you'll also need to
install the requirements yourself.


> Source: `docs/data_engineering/marimo/control_flow/README.md`

# Control Flow

These basic examples show how to control execution of cells.

> [!TIP]
> New to marimo? Run `marimo tutorial intro` and `marimo tutorial dataflow`
> at the command line first!

_Looking for examples on making chatbots? Check out the [`ai/chat`](../ai/chat)
examples folder_.

## Running examples

The requirements of each notebook are serialized in them as a top-level
comment. Here are the steps to open an example notebook:

1. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
2. Open an example with `uvx marimo edit --sandbox <notebook-url>`

> [!TIP]
> The [`--sandbox` flag](https://docs.marimo.io/guides/editor_features/package_management.html) opens the notebook in an isolated virtual environment,
> automatically installing the notebook's dependencies 📦

You can also open notebooks without `uv`, in which case you'll need to
manually [install marimo](https://docs.marimo.io/getting_started/index.html#installation)
first. Then run `marimo edit <notebook-url>`; however, you'll also need to
install the requirements yourself.


## Testing & Markdown


> Source: `docs/data_engineering/marimo/testing/README.md`

# Testing 🧪

These basic examples show how to use test marimo notebooks.

## Testing with pytest

Run `pytest test_with_pytest.py`.

## Testing with doctests

See `running_doctests.py`


> Source: `docs/data_engineering/marimo/markdown/README.md`

# Markdown

These basic examples show how to use write markdown in marimo.

> [!TIP]
> New to marimo? Run `marimo tutorial intro` and `marimo tutorial markdown`
> at the command line first!

## Running examples

The requirements of each notebook are serialized in them as a top-level
comment. Here are the steps to open an example notebook:

1. [Install `uv`](https://github.com/astral-sh/uv/?tab=readme-ov-file#installation)
2. Open an example with `uvx marimo edit --sandbox <notebook-url>`

> [!TIP]
> The [`--sandbox` flag](https://docs.marimo.io/guides/editor_features/package_management.html) opens the notebook in an isolated virtual environment,
> automatically installing the notebook's dependencies 📦

You can also open notebooks without `uv`, in which case you'll need to
manually [install marimo](https://docs.marimo.io/getting_started/index.html#installation)
first. Then run `marimo edit <notebook-url>`; however, you'll also need to
install the requirements yourself.


## Original Sources

- `docs/data_engineering/marimo/ai/chat/README.md`
- `docs/data_engineering/marimo/ai/README.md`
- `docs/data_engineering/marimo/ai/tools/README.md`
- `docs/data_engineering/marimo/cloud/modal/README.md`
- `docs/data_engineering/marimo/cloud/README.md`
- `docs/data_engineering/marimo/cloudflare/README.md`
- `docs/data_engineering/marimo/control_flow/README.md`
- `docs/data_engineering/marimo/docs/marimo/.github/PULL_REQUEST_TEMPLATE.md`
- `docs/data_engineering/marimo/docs/marimo/scripts/README.md`
- `docs/data_engineering/marimo/docs/marimo/tests/_server/session/snapshots/README.md`
- `docs/data_engineering/marimo/docs/marimo/tests/_utils/snapshots/docstring_complex.md`
- `docs/data_engineering/marimo/docs/marimo/tests/_utils/snapshots/docstring_one_liner.md`
- `docs/data_engineering/marimo/docs/marimo/tests/_utils/snapshots/docstring_summary.md`
- `docs/data_engineering/marimo/frameworks/fastapi-endpoint/README.md`
- `docs/data_engineering/marimo/frameworks/fastapi-github/README.md`
- `docs/data_engineering/marimo/frameworks/fastapi/README.md`
- `docs/data_engineering/marimo/frameworks/fasthtml/README.md`
- `docs/data_engineering/marimo/frameworks/flask/README.md`
- `docs/data_engineering/marimo/frameworks/README.md`
- `docs/data_engineering/marimo/KCG_SUMMARY.md`
- `docs/data_engineering/marimo/layouts/README.md`
- `docs/data_engineering/marimo/marimo_cloudflare.md`
- `docs/data_engineering/marimo/marimo.md`
- `docs/data_engineering/marimo/marimo/.github/PULL_REQUEST_TEMPLATE.md`
- `docs/data_engineering/marimo/marimo/README_Chinese.md`
- `docs/data_engineering/marimo/marimo/README_Japanese.md`
- `docs/data_engineering/marimo/marimo/README_Spanish.md`
- `docs/data_engineering/marimo/marimo/README_Traditional_Chinese.md`
- `docs/data_engineering/marimo/marimo/README.md`
- `docs/data_engineering/marimo/marimo/SECURITY.md`
- `docs/data_engineering/marimo/markdown/README.md`
- `docs/data_engineering/marimo/misc/README.md`
- `docs/data_engineering/marimo/README.md`
- `docs/data_engineering/marimo/sql/misc/README.md`
- `docs/data_engineering/marimo/sql/README.md`
- `docs/data_engineering/marimo/testing/README.md`
- `docs/data_engineering/marimo/third_party/huggingface/README.md`
- `docs/data_engineering/marimo/third_party/motherduck/embeddings/README.md`
- `docs/data_engineering/marimo/third_party/README.md`
- `docs/data_engineering/marimo/third_party/sage/README.md`
- `docs/data_engineering/marimo/ui/README.md`

---
*Generated by MERGE_PLAN.md Phase 1 — 2026-06-06*
