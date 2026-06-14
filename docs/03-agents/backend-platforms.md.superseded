---
truth: partial
---

# uackend platforms

> Auto-merged from subdirectory .md files on 2026-06-06

---


## File: docs/agents/convex/AI Agent.md

---
title: "AI Agent"
source: "https://www.convex.dev/components/agent?utm_source=yt-convex&utm_medium=video&dub_id=6fmqcDQgcYvkahij"
author:
  - "[[Convex]]"
published:
created: 2025-12-29
description: "Agents organize your AI workflows into units, with message history and vector search built in."
tags:
  - "clippings"
---
[Back to Components](https://www.convex.dev/components) ![AI Agent hero image](https://www.convex.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fagent.d9d5c243.png&w=1536&q=75)

```bash
npm install @convex-dev/agent
```

AI Agents, built on Convex.[Check out the docs here](https://docs.convex.dev/agents).

The Agent component is a core building block for building AI agents. It manages threads and messages, around which you Agents can cooperate in static or dynamic workflows.

- [Agents](https://docs.convex.dev/agents/agent-usage) provide an abstraction for using LLMs to represent units of use-case-specific prompting with associated models, prompts,[Tool Calls](https://docs.convex.dev/agents/tools), and behavior in relation to other Agents, functions, APIs, and more.
- [Threads](https://docs.convex.dev/agents/threads) persist [messages](https://docs.convex.dev/agents/messages) and can be shared by multiple users and agents (including [human agents](https://docs.convex.dev/agents/human-agents)).
- Streaming text and objects using deltas over websockets so all clients stay in sync efficiently, without http streaming. Enables streaming from async functions.
- [Conversation context](https://docs.convex.dev/agents/context) is automatically included in each LLM call, including built-in hybrid vector/text search for messages in the thread and opt-in search for messages from other threads (for the same specified user).
- [RAG](https://docs.convex.dev/agents/rag) techniques are supported for prompt augmentation from other sources, either up front in the prompt or as tool calls. Integrates with the [RAG Component](https://www.convex.dev/components/rag), or DIY.
- [Workflows](https://docs.convex.dev/agents/workflows) allow building multi-step operations that can span agents, users, durably and reliably.
- [Files](https://docs.convex.dev/agents/files) are supported in thread history with automatic saving to [file storage](https://docs.convex.dev/file-storage) and ref-counting.
- [Debugging](https://docs.convex.dev/agents/debugging) is enabled by callbacks, the [agent playground](https://docs.convex.dev/agents/playground) where you can inspect all metadata and iterate on prompts and context settings, and inspection in the dashboard.
- [Usage tracking](https://docs.convex.dev/agents/usage-tracking) is easy to set up, enabling usage attribution per-provider, per-model, per-user, per-agent, for billing & more.
- [Rate limiting](https://docs.convex.dev/agents/rate-limiting), powered by the [Rate Limiter Component](https://www.convex.dev/components/rate-limiter), helps control the rate at which users can interact with agents and keep you from exceeding your LLM provider's limits.

[Read the associated Stack post here](https://stack.convex.dev/ai-agents).

[![Powerful AI Apps Made Easy with the Agent Component](https://thumbs.video-to-markdown.com/b323ac24.jpg)](https://youtu.be/tUKMPUlOCHY) **Read the [docs](https://docs.convex.dev/agents) for more details.**

Play with the example:

```ts
git clone https://github.com/get-convex/agent.git
cd agent
npm run setup
npm run dev
```

Found a bug? Feature request?[File it here](https://github.com/get-convex/agent/issues).

Get your app up and running in minutes

[Start building](https://www.convex.dev/start)
---


## File: docs/agents/convex/Convex MCP Server _ Convex Developer Hub.md

---
title: "Convex MCP Server | Convex Developer Hub"
source: "https://docs.convex.dev/ai/convex-mcp-server"
author:
published:
created: 2025-12-29
description: "Convex MCP server"
tags:
  - "clippings"
---
The Convex [Model Context Protocol](https://docs.cursor.com/context/model-context-protocol) (MCP) server provides several tools that allow AI agents to interact with your Convex deployment.

## Setup

Add the following command to your MCP servers configuration:

`npx -y convex@latest mcp start`

For Cursor you can use this quick link to install:

or see editor specific instructions:

- [Cursor](https://docs.convex.dev/ai/using-cursor#setup-the-convex-mcp-server)
- [Windsurf](https://docs.convex.dev/ai/using-windsurf#setup-the-convex-mcp-server)
- [VS Code](https://docs.convex.dev/ai/using-github-copilot#setup-the-convex-mcp-server)
- Claude Code: add the MCP server and test with
	```bash
	claude mcp add-json convex '{"type":"stdio","command":"npx","args":["convex","mcp","start"]}'
	claude mcp get convex
	```

## Available Tools

### Deployment Tools

- **`status`**: Queries available deployments and returns a deployment selector that can be used with other tools. This is typically the first tool you'll use to find your Convex deployment.

### Table Tools

- **`tables`**: Lists all tables in a deployment along with their:
	- Declared schemas (if present)
	- Inferred schemas (automatically tracked by Convex)
	- Table names and metadata
- **`data`**: Allows pagination through documents in a specified table.
- **`runOneoffQuery`**: Enables writing and executing sandboxed JavaScript queries against your deployment's data. These queries are read-only and cannot modify the database.

### Function Tools

- **`functionSpec`**: Provides metadata about all deployed functions, including:
	- Function types
	- Visibility settings
	- Interface specifications
- **`run`**: Executes deployed Convex functions with provided arguments.
- **`logs`**: Fetches a chunk of recent function execution log entries, similar to `npx convex logs` but as structured objects.

### Environment Variable Tools

- **`envList`**: Lists all environment variables for a deployment
- **`envGet`**: Retrieves the value of a specific environment variable
- **`envSet`**: Sets a new environment variable or updates an existing one
- **`envRemove`**: Removes an environment variable from the deployment

[Read more about how to use the Convex MCP Server](https://stack.convex.dev/convex-mcp-server)
---


## File: docs/agents/durable/dbos/dbos-node-starter/README.md

# Welcome to DBOS!

This is a template app built with DBOS and Koa.

## Running Locally

First, install the application dependencies.

```shell
npm install
```

Next, we need to setup a Postgres database.
DBOS stores application execution history in Postgres.

If you have a Postgres database, you can set the `DBOS_SYSTEM_DATABASE_URL` environment variable to the connection string for that database.
You can set this environment variable directly or you can put it in an `.env` file in the root of this project.
The template app includes an `.env.example` file with a dummy connection string you can use as a reference.

If you don't have a Postgres server, you can start one locally using Docker.
The DBOS SDK includes a utility to start and stop a local Postgres Docker container.

```shell
npx dbos postgres start
npx dbos postgres stop
```

> Note, DBOS will automatically connect to Postgres running on localhost if `DBOS_SYSTEM_DATABASE_URL` is not specified.
> If you use a local Postgres Docker container, you do not need to set the `DBOS_SYSTEM_DATABASE_URL` environment variable.

Once you have a setup or configured a Postgres database for DBOS, you can launch the application.

```shell
npm run launch
```

Alternatively, you can run the application with [`nodemon`](https://nodemon.io/)
to enable automatic restart when the application changes.

```shell
npm run dev
```

Once the app is running, visit [`http://localhost:3000`](http://localhost:3000) to see your app.
Then, edit `src/main.ts` to start building!

---


## File: docs/agents/durable/dbos/dbos-node-toolbox/README.md

# DBOS Toolbox

This app contains example code for many DBOS features, including workflows, steps, queues, scheduled workflows, and transactions.
You can use it as a template when starting a new DBOS app&mdash;start by editing `src/main.ts`.

To learn more about how to program with DBOS, check out the [DBOS programming guide](https://docs.dbos.dev/typescript/programming-guide).

## Running Locally

First, install the application dependencies.

```shell
npm install
```

Next, we need to setup a Postgres database.
DBOS stores application execution history in Postgres.
Additionally, the toolbox app uses a Knex.js based DBOS Data Source, which stores data in a separate database.
While these databases can be deployed to separate Postgres servers, we will deploy to a single server for simplicity.

If you have a Postgres database, you can set the `DBOS_DATABASE_URL` environment variable to the connection string for that database.
You can set this environment variable directly or you can put it in an `.env` file in the root of this project.
The template app includes an `.env.example` file with a dummy connection string you can use as a reference.

> Note, this demo uses `DBOS_DATABASE_URL` so that it can also be deployed to DBOS Cloud.
> If you are running DBOS locally, you can use whatever mechanism you wish to manage database connection information.

If you don't have a Postgres server, you can start one locally using Docker.
The DBOS SDK includes a utility to start and stop a local Postgres Docker container.

```shell
npx dbos postgres start
npx dbos postgres stop
```

> Note, this demo app is configured to automatically connect to Postgres running on localhost if `DBOS_DATABASE_URL` is not specified.
> If you use a local Postgres Docker container, you do not need to set the `DBOS_DATABASE_URL` environment variable.

Once you have a setup or configured a Postgres database for DBOS, you need to configure the application database.
This demo app includes script file to create the database and run the Knex.js migrations required by the application.
You can run this script via the `db:setup` npm script.

```shell
npm run db:setup
```

Once you have configured the application database, you can launch the application.
The launch script has a pre-step to build the app automatically.

```shell
npm run launch
```

Alternatively, you can run the application with [`nodemon`](https://nodemon.io/)
to enable automatic restart when the application changes.

```shell
npm run dev
```

Once the app is running, visit [`http://localhost:3000`](http://localhost:3000) to see the app in action.
You can edit the code in `src/main.ts` to start building.

---


## File: docs/agents/durable/dbos/dbos-toolbox/README.md

# DBOS Toolbox

This app contains example code for many DBOS features, including workflows, steps, queues, scheduled workflows, and transactions.
You can use it as a template when starting a new DBOS app&mdash;start by editing `main.py`.

To learn more about how to program with DBOS, check out the [DBOS programming guide](https://docs.dbos.dev/python/programming-guide).

## Setup

1. Install dependencies and activate your virtual environment

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install dbos
```

2. Start your app:

```shell
python3 main.py
```

Visit [`http://localhost:8000`](http://localhost:8000) to see your app!

---


## File: docs/agents/durable/dbos/document-detective/README.md

# Document Detective

In this example, we'll use DBOS to build a reliable and scalable data processing pipeline. We'll show how DBOS can help you horizontally scale an application to process many items concurrently and seamlessly recover from failures. Specifically, we'll build a pipeline that indexes PDF documents for RAG, though you can use a similar design pattern to build almost any data pipeline.

## Creating an OpenAI Account

To run this app, you need an OpenAI developer account.
Obtain an API key [here](https://platform.openai.com/api-keys) and set up a payment method for your account [here](https://platform.openai.com/account/billing/overview).
Make sure you have some credits (~$1) to use it.

Set your API key as an environment variable:

```shell
export OPENAI_API_KEY=<your_openai_key>
```

## Setup

1. Install dependencies:

```shell
uv sync
```

2. Start Postgres in a local Docker container:

```bash
uv run dbos postgres start
```

Set the `DBOS_SYSTEM_DATABASE_URL` environment variable to connect to this database:

```shell
export DBOS_SYSTEM_DATABASE_URL="postgresql+psycopg://postgres:dbos@localhost:5432/document_detective"
```

If you already use Postgres, you can set the `DBOS_SYSTEM_DATABASE_URL` environment variable to your own connection string.

3. Set up the Postgres vector store for LlamaIndex (requires pgvector):

```shell
uv run python3 setup_llamaindex.py
```

4. Start your app!

```shell
uv run python3 -m document_detective.main
```

Visit [`http://localhost:8000`](http://localhost:8000) to see your chat agent!


### Indexing Documents

To index a batch of PDF documents, send a list of their URLs in a POST request to the `/index` endpoint.

For example, try this cURL command to index Apple's SEC 10-K filings for 2020-2024:

```shell
curl -X POST "http://localhost:8000/index" \
     -H "Content-Type: application/json" \
     -d '{"urls": [
        "https://dbos-hackathon.s3.us-east-1.amazonaws.com/apple-filings/apple-10k-2020.pdf",
        "https://dbos-hackathon.s3.us-east-1.amazonaws.com/apple-filings/apple-10k-2021.pdf",
        "https://dbos-hackathon.s3.us-east-1.amazonaws.com/apple-filings/apple-10k-2022.pdf",
        "https://dbos-hackathon.s3.us-east-1.amazonaws.com/apple-filings/apple-10k-2023.pdf",
        "https://dbos-hackathon.s3.us-east-1.amazonaws.com/apple-filings/apple-10k-2024.pdf"
]}'
```
---


## File: docs/agents/durable/dbos/hacker-news-agent/frontend/README.md

# Deep Research Agent - Frontend

A React-based UI for the Deep Research Agent that allows you to launch AI agents and monitor their progress.

## Features

- Launch new research agents with custom topics
- View all active and completed agents
- Real-time status updates (polls every 3 seconds)
- Display detailed agent information including:
  - Agent ID and creation time
  - Research topic
  - Iteration count
  - Status (running, success, error)
  - Generated reports

## Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Backend Setup

Make sure the backend API is running before using the frontend:

```bash
# From the project root
uv run python -m hacker_news_agent.main
```

The backend should be running on `http://localhost:8000`

## Usage

1. Enter a research topic in the input field
2. Click "Launch Agent" to start a new research agent
3. View the list of agents below with their current status
4. The list automatically refreshes every 3 seconds to show updates

## Tech Stack

- React 18
- TypeScript
- Vite
- CSS3

## API Endpoints

The frontend connects to these backend endpoints:

- `POST /agents` - Start a new research agent
- `GET /agents` - List all agents with their statuses

---


## File: docs/agents/durable/dbos/hacker-news-agent/README.md

# Hacker News Research Agent

An autonomous research agent for searching Hacker News built with DBOS.
You can find a detailed walkthrough [here](https://docs.dbos.dev/python/examples/hacker-news-agent).

<img width="1202" height="1298" alt="513013609-738119e9-4253-4230-94bb-554888658563" src="https://github.com/user-attachments/assets/4d1d1b61-084b-48ba-a826-f53372ab8768" />


## Setup

1. Install dependencies:

```bash
uv sync
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

3. Run the launch script to start the React frontend and agentic backend.
The app is available at http://localhost:5173/.

```bash
./launch_app.sh
```

---


## File: docs/agents/durable/dbos/queue-worker/README.md

# DBOS Queue Worker

This example demonstrates how to build DBOS workflows in their own "queue worker" service and enqueue and manage them from other services.

## Setup

1. Install dependencies:

```shell
uv sync
```

2. Start both services in this example: a FastAPI web server (`server.py`) and a DBOS worker (`worker.py`):

```shell
./launch_app.sh
```

Visit [`http://localhost:8000`](http://localhost:8000) to see your app!


---


## File: docs/agents/durable/dbos/reliable-refunds-langchain/README.md

# Reliable Customer Service Agent Powered by DBOS and LangGraph

This is an AI agent built with DBOS and LangGraph, demonstrating human-in-the-loop pattern with LLM interactions.

You can chat with this LLM-powered AI agent to:
-  Check the status of your purchase order.
- Request a refund for your order.

The agent is a stateful graph constructed with LangGraph. The architecture diagram is shown below:

![LangGraph diagram](architect.png)

The `tools` include two DBOS decorated functions: a database transaction function to retrieve order status, and a refund workflow to process refund requests.

## Asynchronous Human-in-the-Loop Processing

What makes this agent unique is its ability to leverage DBOS for asynchronous human-in-the-loop processing. This is typically challenging to write, but DBOS makes it simple and reliable.

If an order exceeds a certain cost threshold, the refund request will be escalated for manual review. In this case, the refund workflow contains the following step:
- An email is sent to an admin for approval.
- The refund workflow **pauses** until a human decision is made.
- Based on the response, the workflow either proceeds with the refund or rejects the request.
as an email to the admin for a manual review.

The tool invokes the refund workflow to execute asynchronously and returns back to the chatbot as soon as the workflow is started, so the chatbot is not blocked by the potentially long review period.

This demonstrates how **DBOS simplifies complex workflows**, making it easier to integrate human decision-making into automated processes.

## Creating an OpenAI Account

To run this app, you need an OpenAI developer account.
Obtain an API key [here](https://platform.openai.com/api-keys) and set up a payment method for your account [here](https://platform.openai.com/account/billing/overview).
This bot uses `gpt-3.5-turbo` for text generation.
Make sure you have some credits (~$1) to use it.

Set your API key as an environment variable:

```shell
export OPENAI_API_KEY=<your_openai_key>
```

## Setting Up SendGrid

This app uses [SendGrid](https://sendgrid.com/en-us) to send emails.
Create a SendGrid account, verify an email for sending, and generate an API key.
Then set the API key and sender email as environment variables:

```shell
export SENDGRID_API_KEY=<your key>
export SENDGRID_FROM_EMAIL=<your email>
export ADMIN_EMAIL=<your email>
```

### Deploying to the Cloud

To serverlessly deploy this app to DBOS Cloud, first install the DBOS Cloud CLI (requires Node):

```shell
npm i -g @dbos-inc/dbos-cloud
```

Then, run this command to deploy your app:

```shell
dbos-cloud app deploy
```

This command outputs a URL&mdash;visit it to see your chatbot!
You can also visit the [DBOS Cloud Console](https://console.dbos.dev/login-redirect) to see your app's status and logs.

### Running Locally

First create a virtual environment and install dependencies:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


Then start your app in the virtual environment:

```shell
dbos migrate
dbos start
```

Visit [`http://localhost:8000`](http://localhost:8000) to see your customer service chatbot!
---


## File: docs/agents/durable/dbos/s3mirror/README.md

# s3mirror

DBOS powered utility for performant, durable and observable transfers between S3 buckets.

Created in collaboration with Bristol Myers Squibb. Read our joint manuscript here:
https://www.biorxiv.org/content/10.1101/2025.06.13.657723v1

## Running the app on your system

Clone this repo.

### 1. Set up Env
Easiest to use venv to create an environment just for the app
```bash
cd s3mirror
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Optional: Set up Postgres

By default, the app will use SQLite. To use Postgres instead, set the variable `DBOS_SYSTEM_DATABASE_URL` appropriately. See https://docs.dbos.dev/python/programming-guide

### 3. Start the App
Export the AWS credentials and launch like so

```bash
export AWS_ACCESS_KEY_ID="YOURKEY..."
export AWS_SECRET_ACCESS_KEY="YourSecretKey..."
export AWS_DEFAULT_REGION="us-east-1" #substitute for your case
dbos start
```

### 4. Run a Transfer
In the file `start_transfer_example.py` replace `YOUR_BUCKET_HERE` with the bucket to write to (using the creds exported above). The file is configured to read from the public Google Genomics bucket, so you don't need to change `src_` values for a test. 

Then run
```bash
cd s3mirror
source s3sync/.venv/bin/activate # if needed
python3 start_transfer_example.py
```
It will emit a transfer_id. You can send a GET request to 
```
http://0.0.0.0:8000/transfer_status/TRANSFER_ID
```
To track the transfer.

### 5. Notes
The transfer will proceed durably. If you `CTRL+C` the app and restart, it will resume where it left off - downloading only files that have not finished. The status of all past transfers is also stored durably. The `transfer_status` page continues to work as long as Postgres retains data about that specific transfer.

The `rate` field output by transfer_status is in GB/s. 

To cancel a transfer, sent an empty POST request to `/cancel/TRANSFER_ID`

The script `clear_dst.sh` cleans a bucket. Edit it to add your bucket name instead of `YOUR_BUCKET_HERE`. Use it carefully as it deletes all the data in the specified path.

## Running in DBOS Cloud

If you haven't already, sign up at https://console.dbos.dev

### 1. Install the DBOS Cloud CLI

```bash
# Install Node 22
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm

nvm install 22
nvm use 22

# Install dbos-cloud
npm i -g @dbos-inc/dbos-cloud@latest
```

### 2. Log in from the App Directory

```bash
cd s3mirror
dbos-cloud login
```
Follow the instructions

### 3. Deploy App

The AWS keys are passed to the app at deploy time. Like so:

```bash
dbos-cloud app register -d your-database-name
dbos-cloud app env create -s AWS_ACCESS_KEY_ID -v "YOURKEY..."
dbos-cloud app env create -s AWS_SECRET_ACCESS_KEY -v "AWS_SECRET_ACCESS_KEY"
dbos-cloud app env create -s AWS_DEFAULT_REGION -v "us-east-1" #substitute for your case
dbos-cloud app deploy
```

This starts a Postgres server for you in the cloud, uploads your app and returns a URL. You can now use this URL as the base in `start_transfer_example.py` to start transfers.

### 4. Cloud Notes

You can use the [Dashboard](https://docs.dbos.dev/cloud-tutorials/monitoring-dashboard) to view app logs. 

You can upgrade to DBOS Pro at https://console.dbos.dev. This will make transfers auto-scale to multiple workers and increase speed by over 4x. You can further tune the performance by starting a [linking a larger Postgres database](https://docs.dbos.dev/production/dbos-cloud/cloud-cli#dbos-cloud-db-link) and increasing your [per-vm RAM](https://docs.dbos.dev/production/dbos-cloud/cloud-cli#dbos-cloud-db-link).

For more, see https://docs.dbos.dev/

---


## File: docs/agents/durable/dbos/widget-store/README.md

# Widget Store

This app uses DBOS to build an online storefront that's resilient to any failure.
You can interrupt it at any time (we even provide a crash button to facilitate experimentation) and it will recover from exactly where it left off.

## Setup

1. Install dependencies and activate your virtual environment

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install dbos
```

2. Start Postgres in a local Docker container:

```bash
dbos postgres start
```

Set the `DBOS_DATABASE_URL` environment variable to connect to this database:

```shell
export DBOS_DATABASE_URL="postgresql+psycopg://postgres:dbos@localhost:5432/widget_store"
```

If you already use Postgres, you can set the `DBOS_DATABASE_URL` environment variable to your own connection string.

3. Run database migrations:

```shell
dbos migrate
```

4. Start your app:

```shell
python3 -m widget_store.main
```

Visit [`http://localhost:8000`](http://localhost:8000) to see your app!
---


## File: docs/agents/durable/KCG_SUMMARY.md

# Durable — KCG Summary

## What It Is
Collection of production-grade examples for **durable execution and orchestration** using two complementary platforms: **Restate** (durable agent workflows with crash-safe LLM calls, idempotent retries, human-in-the-loop, stateful virtual objects, multi-agent RPC) and **DBOS** (durable backend OS with built-in workflow reliability). Both solve the same core problem — keeping long-running agentic workflows alive across crashes, restarts, and waiting periods without bespoke state machinery.

## Why This Matters for Kings' College Galway
Durable execution patterns are critical for the oideachais education platform, where scraping pipelines, curriculum embedding jobs, and multi-agent orchestration run for minutes to hours. Restate's suspend/resume and human-in-the-loop primitives directly map to approval workflows for curriculum content QA. DBOS's transactional workflow model (guaranteed exactly-once execution) aligns with the data platform's need for reliable ingestion and transformation pipelines. The Vercel AI SDK and OpenAI Agents SDK integration examples provide reusable patterns for the TanStack Start frontend's agent backends.

## Key Patterns Preserved
- `restate/README.md` — Catalog of AI workflow examples: Vercel AI SDK, OpenAI Agents, A2A protocol, MCP, Python patterns, TypeScript patterns
- `restate/ai-examples/README.md` — Overview of agentic AI examples across SDKs
- `restate/ai-examples/a2a/README.md` — Agent-to-Agent protocol integration with Restate
- `restate/ai-examples/mcp/README.md` — Model Context Protocol tool servers with durable execution
- `restate/ai-examples/vercel-ai/template/README.md` — Minimal Vercel AI SDK + Restate template
- `restate/ai-examples/vercel-ai/template_nextjs/README.md` — Next.js frontend + Restate backend
- `restate/ai-examples/vercel-ai/tour-of-agents/README.md` — Multi-agent tour using Vercel AI SDK
- `restate/ai-examples/vercel-ai/examples/README.md` — Additional Vercel AI SDK examples
- `restate/ai-examples/openai-agents/template/README.md` — OpenAI Agents SDK + Restate template
- `restate/ai-examples/openai-agents/tour-of-agents/README.md` — Multi-agent tour using OpenAI Agents SDK
- `restate/ai-examples/python-patterns/README.md` — Python-only durable execution patterns (no SDK)
- `restate/mcp/README.md` — Restate MCP server example
- `restate/agent47/README.md` — Full-stack agent with UI, pubsub, and Restate backend
- `restate/agent47/packages/ui/README.md` — Agent47 React frontend
- `restate/agent47/packages/pubsub/README.md` — Agent47 pubsub messaging
- `restate/typescript-patterns/README.md` — TypeScript durable execution patterns
- `dbos/hacker-news-agent/README.md` — Autonomous research agent with React frontend and DBOS backend
- `dbos/hacker-news-agent/frontend/README.md` — Hacker News agent React frontend
- `dbos/widget-store/README.md` — E-commerce workflow with DBOS durable transactions
- `dbos/s3mirror/README.md` — S3 mirror agent with DBOS
- `dbos/dbos-toolbox/README.md` — DBOS Python toolbox utilities
- `dbos/reliable-refunds-langchain/README.md` — LangChain + DBOS for reliable payment workflows
- `dbos/dbos-node-toolbox/README.md` — DBOS Node.js toolbox utilities
- `dbos/dbos-node-starter/README.md` — DBOS Node.js starter template
- `dbos/queue-worker/README.md` — DBOS queue-based worker pattern
- `dbos/document-detective/README.md` — Document processing agent with DBOS

## Source Files
Full source removed (2026-06-06), available at:
- Restate: https://github.com/restatedev/examples
- DBOS: https://github.com/dbos-inc

## What Was Removed
TypeScript source (`.ts`, `.tsx`), Python source (`.py`), JSON configs (`package.json`, `tsconfig.json`, `pyproject.toml`), lock files, Dockerfiles, YAML configs, shell scripts, `.cursor/rules/`, `.claude/` files, images, SVGs, and all non-markdown assets.

---


## File: docs/agents/durable/restate/agent47/packages/pubsub/README.md


# Demo infra

This package contains non-restate imaginary code, that a cloud based coding agent would need.
It contains:
* a sandbox provisioning API (do not use in production!) 
* a websocket service to deliver messages to the UI.




---


## File: docs/agents/durable/restate/agent47/packages/ui/README.md

# UI

This is a demo UI, generated with v0.



---


## File: docs/agents/durable/restate/agent47/README.md

# Coding Agent

This repository contains a coding agent _demo_ built on [Restate.dev](https://restate.dev)
Key features:

* Conversation management — Maintains multi-turn context and session state so the agent can follow, clarify, and continue user interactions reliably.
* Orchestrated subagent execution — Coordinates and supervises subagents and workflows to break complex tasks into manageable jobs, with planning, retries, and interruption handling.
* Sandbox lifecycle and resource management — Provisions, locks, releases, and reclaims isolated execution sandboxes (with timeouts) so user code runs safely and reproducibly.

## How does this works

This section summarizes how the agent is structured and how requests flow through the system.

The system has three primary responsibilities:
- Orchestration: [agent.ts](packages/agent/src/agent.ts) receives user messages, maintains conversation state and session context, decides when to start/stop or interrupt workflows, and routes work to the executor.
- Workflow execution: [agent_executor.ts](packages/agent/src/agent_executor.ts) turns high‑level requests and context into stepwise plans (ToDos), runs sub‑workflows, manages retries and error handling, and reports progress back to the orchestrator.
- Sandbox management [sandbox.ts](packages/agent/src/sandbox.ts): provisions isolated runtimes, enforces timeouts and resource limits, and locks/releases sandboxes to ensure safe, reproducible execution.

Typical request lifecycle:

1. The orchestrator accepts a message and updates conversation context.
2. The executor generates a plan of concrete tasks based on the current context.
3. The executor executes each task, as a subagent workflow, while tools run inside sandboxes that the sandbox manager provisions and locks.
4. The orchestrator updates the session state, presents results to the user, and reclaims sandbox resources.

# Quick Start

* Start restate
```bash
docker run --net host restatedev/restate
```

* You would need the `OPENAI_API_KEY` in your env

```bash
export OPENAI_API_KEY=...
```

* Modal labs sandboxes

Make sure to expose the relevant env variables for modal, (i.e. `MODAL_PROFILE`) and then set the

* Start the services
```bash
pnpm install
pnpm build
pnpm start 
```

* Register the services with restate

Use the webui/cli or
```bash
curl http://localhost:9070/deployments --json '{ "uri" : "http://localhost:9080"}'
```

* Demo UI

[Agent UI](http://localhost:3000)


# Disclaimer

This demo is for illustrative purposes, it's purpose is to highlight the capabilities of the Restate.dev as a platform for AI applications.

---


## File: docs/agents/durable/restate/ai-examples/.tools/typescript_formatter/README.md

# TypeScript Examples formatter

Use this to format all typescript example files by running
`npm run format-all`

---


## File: docs/agents/durable/restate/ai-examples/a2a/README.md

# Resilient A2A Agents with Restate

These examples use [Restate](https://ai.restate.dev/) to implement the [Agent2Agent (A2A) protocol](https://github.com/google/A2A).

Restate acts as a scalable, resilient task orchestrator that speaks the A2A protocol and gives you:
- 🔁 **Automatic retries** - Handles LLM API downtime, timeouts, and infrastructure failures
- 🔄 **Smart recovery** - Preserves progress across failures without duplicating work
- ⏱️ **Persistent task handles** - Tracks progress across failures, time, and processes
- 🎮 **Task control** - Cancel tasks, query status, re-subscribe to ongoing tasks
- 🧠 **Idempotent submission** - Automatic deduplication based on task ID
- 🤖 **Agentic workflows** - Build resilient agents with human-in-the-loop and parallel tool execution
- 💾 **Durable state** - Maintain consistent agent state across infrastructure events
- 👀 **Full observability** - Line-by-line execution tracking with built-in audit trail
- ☁️️ **Easy to self-host** - or connect to Restate Cloud

<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/a2a/a2a.png" width="600px"/>

## Prerequisites
- Python 3.12 or higher
- [UV](https://docs.astral.sh/uv/)
- An [OpenAI API Key](https://platform.openai.com/docs/api-reference/authentication)
    ```shell
    echo "OPENAI_API_KEY=your_api_key_here" >> .env
    ```

## Running the example: multi-agent 

This example shows how to run multiple agents and use the A2A protocol to communicate with them.

<img src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/a2a/multi_agent.png" alt="Restate UI" width="600"/>

Make sure you have no other Restate server/services running. Then bring up the multi-agent example:

```shell
echo "OPENAI_API_KEY=your_api_key_here" >> .env
docker compose up
```

(It will take a while before all the services are up and running and you will see a few retries for the registration.)

Go to the Restate UI (`http://localhost:9070`). You see here the overview of the services that are running:

<img src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/a2a/multi_agent_overview.png" alt="Restate UI" width="1000"/>

To send messages to the host agent, click on it and then click on the "Playground" button. 

<img src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/a2a/multi_agent_chat.png" alt="Restate UI" width="1000"/>

The host agent will forward messages to the registered agents that it knows of, and it will use the A2A protocol to communicate with them.

You can also send messages with the A2A protocol directly to the agents, without going through the host agent:


### Weather Agent: Restate + OpenAI Agent SDK

You can either send a message to the weather agent using the A2A protocol:

```shell
curl localhost:8080/WeatherAgentA2AServer/process_request \
    --json '{
      "jsonrpc": "2.0",
      "id": 923043,
      "method":"tasks/send",
      "params": {
        "id": "3954039823504",
        "sessionId": "lw33sl5e-8966-6g6k-26ee-2d5e6w29ya3423",
        "message": {
          "role":"user",
          "parts": [{
            "type":"text",
            "text": "What is the weather in Detroit?"
          }]
        },
        "metadata": {}
      }
    }' | jq . 
```

### Reimbursement Agent: Restate + OpenAI Agent SDK

This is a stateful agent which runs long-running tasks and blocks on human approval if the amount is greater than 100 USD.

You talk to a dedicated reimbursement agent based on the session ID. 
If you provide the session ID, the agent will remember the conversation and the tasks you have sent to it.

To start a task that **will block on human approval**, run the following command:

```shell
curl localhost:8080/ReimbursementAgentA2AServer/process_request \
    --json '{
      "jsonrpc": "2.0",
      "id": 22323,
      "method":"tasks/send",
      "params": {
        "id": "lwp13w5e3sdf258t3wedsf13234",
        "sessionId": "lw33sl5e-8966-6g6k-26ee-2d5e6w29y3a3423",
        "message": {
          "role":"user",
          "parts": [{
            "type":"text",
            "text": "Reimburse my hotel for my business trip of 5 nights for 1200USD"
          }]
        },
        "metadata": {}
      }
    }' | jq . 
```

It will then return a response mentioning you need to provide a date. 

<details><summary>View output</summary>

```json
{
  "jsonrpc": "2.0",
  "id": 22323,
  "result": {
    "id": "lwp13w5e3sdf258t3wedsf13234",
    "sessionId": "lw33sl5e-8966-6g6k-26ee-2d5e6w29y3a3423",
    "status": {
      "state": "input-required",
      "message": {
        "role": "agent",
        "parts": [
          {
            "type": "text",
            "text": "MISSING_INFO: Could you please provide the date of the transaction for the hotel reimbursement?",
            "metadata": null
          }
        ],
        "metadata": null
      },
      "timestamp": "2025-06-18T08:56:41.037053"
    },
    "artifacts": null,
    "history": [
      {
        "role": "user",
        "parts": [
          {
            "type": "text",
            "text": "Reimburse my hotel for my business trip of 5 nights for 1200USD",
            "metadata": null
          }
        ],
        "metadata": null
      }
    ],
    "metadata": null
  },
  "error": null
}
```

</details>

You can then provide the date of the transaction by sending another request to the same stateful session (same task and session ID):

```shell
curl localhost:8080/ReimbursementAgentA2AServer/process_request \
    --json '{
      "jsonrpc": "2.0",
      "id": 22324,
      "method":"tasks/send",
      "params": {
        "id": "lwp13w5e3sdf258t3wedsf13234",
        "sessionId": "lw33sl5e-8966-6g6k-26ee-2d5e6w29y3a3423",
        "message": {
          "role":"user",
          "parts": [{
            "type":"text",
            "text": "The date of the transaction is 05/04/2025"
          }]
        },
        "metadata": {}
      }
    }' | jq . 
```

Possibly, the agent will ask for a final approval before it can proceed with the reimbursement. 
```shell
curl localhost:8080/ReimbursementAgentA2AServer/process_request \
    --json '{
      "jsonrpc": "2.0",
      "id": 22325,
      "method":"tasks/send",
      "params": {
        "id": "lwp13w5e3sdf258t3wedsf13234",
        "sessionId": "lw33sl5e-8966-6g6k-26ee-2d5e6w29y3a3423",
        "message": {
          "role":"user",
          "parts": [{
            "type":"text",
            "text": "The info looks good"
          }]
        },
        "metadata": {}
      }
    }' | jq . 
```

Once the agent has all the information, it will ask start the reimbursement process and will block until a human approves the request.

The logs of the agent service will print the curl command to approve the reimbursement and unblock the task.
Or you can leave the task blocked if you want to try out the get and cancel task commands below.

```text
... first part of logs ...
[2025-05-16 13:42:50,410] [310993] [INFO] - Agent session lwp13w5e3sdf258t3wesf13234 -   Starting iteration of agent loop with agent: ReimbursementAgent and tools/handoffs: ['create_request_form', 'reimburse', 'return_form']
[2025-05-16 13:42:50,410] [310993] [INFO] - Agent session lwp13w5e3sdf258t3wesf13234 -  Calling LLM
[2025-05-16 13:42:52,293] [310993] [INFO] - HTTP Request: POST https://api.openai.com/v1/responses "HTTP/1.1 200 OK"
[2025-05-16 13:42:52,303] [310993] [INFO] - Agent session lwp13w5e3sdf258t3wesf13234 -  Executing tool reimburse
================================================== 
 Requesting approval for request_id_1633297 
 Resolve via: 
curl localhost:8080/restate/awakeables/sign_1oqmHpDF_RJQBltjnf48zszmfmRr4w9izAAAAEQ/resolve --json '{"approved": true}' 
 ==================================================
```

Approve the reimbursement. 

You can have a look at the Restate UI at `http://localhost:9070/ui/invocations` to see the end-to-end flow:

<img src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/a2a/long-running-task.png" alt="Restate UI" width="1200"/>

We see how the A2A server called the task object. The task object then called the `invoke` method of the reimbursement agent, which then called the LLM to process the request.
We see how it waited for the human approval and then continued with the reimbursement process. 

Finally, it scheduled the payment task to execute at the end of the month.

**You can now also use the A2A protocol to query the task status and history, or cancel the task:**

#### Get the task

```shell
curl localhost:8080/ReimbursementAgentA2AServer/process_request \
    --json '{
      "jsonrpc": "2.0",
      "id": 2,
      "method":"tasks/get",
      "params": {
        "id": "lwp13w5e3sdf258t3wesf13234",
        "historyLength": 10,
        "metadata": {}
      }
    }' | jq . 
```

<details>
<summary>View output</summary>

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "id": "lwp13w5e3sdf258t3wesf13234",
    "sessionId": "lw33sl5e-8966-6g6k-26ee-2d5e6w29ya3423",
    "status": {
      "state": "submitted",
      "message": null,
      "timestamp": "2025-05-16T13:42:46.306507"
    },
    "artifacts": null,
    "history": [
      {
        "role": "user",
        "parts": [
          {
            "type": "text",
            "text": "Reimburse my hotel for my business trip of 5 nights for 1200USD of 05/04/2025",
            "metadata": null
          }
        ],
        "metadata": null
      }
    ],
    "metadata": null
  },
  "error": null
}
```

</details>

The Durable Task Object stores the Task data in Restate's embedded K/V store.
We can query the K/V store via the UI. Have a look at the task progress in the Restate UI at `http://localhost:9070/ui/state`:

<img src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/a2a/restate_ui_task_state.png" alt="Restate UI" width="1000"/>

#### Cancel a Task

For example, start a new reimbursement task and then cancel it:

```shell
curl localhost:8080/ReimbursementAgentA2AServer/process_request \
    --json '{
      "jsonrpc": "2.0",
      "id": 223235,
      "method":"tasks/send",
      "params": {
        "id": "lwp13w5e3sdf258t3wedsf13234",
        "sessionId": "lw33sl5e-8966-6g6k-26ee-2d5e6w29y3a34235",
        "message": {
          "role":"user",
          "parts": [{
            "type":"text",
            "text": "Reimburse my hotel for my business trip of 5 nights for 1200USD of 05/04/2025"
          }]
        },
        "metadata": {}
      }
    }' | jq . 
```

```shell
curl localhost:8080/ReimbursementAgentA2AServer/process_request \
    --json '{
      "jsonrpc": "2.0",
      "id": 3,
      "method":"tasks/cancel",
      "params": {
        "id": "lwp13w5e3sdf258t3wedsf13234",
        "metadata": {}
      }
    }' | jq . 
```

<details>
<summary>View output</summary>

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "id": "lwp13w5e3sdf258t3wesf13234",
    "sessionId": "lw33sl5e-8966-6g6k-26ee-2d5e6w29ya3423",
    "status": {
      "state": "canceled",
      "message": null,
      "timestamp": "2025-05-16T13:44:05.852323"
    },
    "artifacts": null,
    "history": [
      {
        "role": "user",
        "parts": [
          {
            "type": "text",
            "text": "Reimburse my hotel for my business trip of 5 nights for 1200USD of 05/04/2025",
            "metadata": null
          }
        ],
        "metadata": null
      }
    ],
    "metadata": null
  },
  "error": null
}
```

</details>

The UI also shows the task as canceled in the state tab and in the journal overview of the long-running task:

<img src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/a2a/cancel_journal.png" alt="Restate UI" width="1200"/>

This is implemented via Restate's [cancel task API](https://docs.restate.dev/develop/python/service-communication#cancel-an-invocation).

### Stopping the example

To bring the services down, run:

```shell
docker compose down
docker compose rm
```


## Running a single agent

You can also start a single agent together with Restate. 


For example, to run the weather agent:

```shell
uv run a2a/weather
```

[Start the Restate Server](https://docs.restate.dev/develop/local_dev) in a separate shell:
```shell
restate-server
```

Then register the service:

```shell
restate -y deployments register http://localhost:9081/restate/v1
```

Then send requests to the agent.

---


## File: docs/agents/durable/restate/ai-examples/mcp/README.md

# Resilient MCP Server with Restate

Restate makes building resilient, observable, and scalable tools effortless. Here's what it brings to the table:

- ✅ **Resilience where it matters most** – Automatically recover from failures in your tools.
- 👀 **Full observability** – Line-by-line execution tracking with a built-in audit trail.
- 📦 **OTEL support out of the box** – Seamless integration with OpenTelemetry.
- 🌍 **Deploy anywhere** – Whether it's AWS Lambda, CloudRun, Fly.io, Cloudflare, Kubernetes, or Deno Deploy.
- 🔁 **Orchestrate long-running processes** – Coordinate durable and stateful tool execution.
- ☁️ **Easy to self-host** – Or connect to [Restate Cloud](https://restate.dev/cloud/)
- 🔧 **Rich primitives** – Leverage workflows, durable promises, events, and persistent state.

---

## Example: Generate a greeting 

```ts
  tool(
  {
    description: "Greets a person with a song and dance",
    input: z.object({ name: z.string() }),
  },
  async (ctx, { name }) => {

    const urls = await ctx.run(
      "Obtain two Pre-signed URLs for a bucket",
      () => generatePresignedUrls()
    );

    const imageStep = ctx.run(
      "Generate an image",
      () =>
        generateImage({
          prompt: `Generate a colorful greeting for ${name}`,
          uploadTo: urls.imageUrl,
        }),
      {
        maxRetryAttempts: 3,
      }
    );

    const audioStep = ctx.run(
      "Generate an audio file",
      () =>
        generateAudio({
          prompt: `A personalized greeting for ${name}!`,
          uploadTo: urls.audioUrl,
        }),
      { maxRetryAttempts: 3 }
    );

    
    await all([imageStep, audioStep]);

    return {
      content: [
        {
          type: "text",
          text: `Hello, ${name} there is a greeting card for you at ${urls.imageUrl} and a song ${urls.audioUrl}}!`,
        },
      ],
    };
  }
);

```

## Running the example

1. Export your OpenAI or Anthrophic API key as an environment variable:
    ```shell
    export OPENAI_API_KEY=your_openai_api_key
    ```
2. [Start the Restate Server](https://docs.restate.dev/develop/local_dev) in a separate shell:
    ```shell
    restate-server
    ```
3. Start the tools services:
    ```shell
    cd tools
    npm install
    npm run app
    ```
4. Register the services (use `--force` if you already had another deployment registered at 9080): 
    ```shell
    restate -y deployments register localhost:9080
    ```
5. Build the MCP server:
    ```shell
    cd restate-mcp
    npm install
    npm run build
    ```

6. Configure Claude desktop
   
   Edit:
   * macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   * Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   
   ```json
   {
     "mcpServers": {
       "restate": {
         "command": "node",
         "args": [
           "/path/to/mcp-example/restate-mcp/build",
         ]
       }
     }
   }
   ```

7. Ask Claude to greet your favorite person

![Claude](image.png "The incremental counter")


---


## File: docs/agents/durable/restate/ai-examples/openai-agents/template/.claude/CLAUDE.md

# Restate Python SDK Rules

## Core Concepts

* Restate provides durable execution: code automatically stores completed steps and resumes from where it left off on failures
* All handlers receive a `Context`/`ObjectContext`/`WorkflowContext`/`ObjectSharedContext`/`WorkflowSharedContext` object as the first argument
* Handlers can take typed inputs and return typed outputs using Python type hints and Pydantic models

## Service Types

### Basic Services

```python {"CODE_LOAD::python/src/develop/my_service.py"}  theme={null}
import restate

my_service = restate.Service("MyService")


@my_service.handler("myHandler")
async def my_handler(ctx: restate.Context, greeting: str) -> str:
    return f"${greeting}!"


app = restate.app([my_service])
```

### Virtual Objects (Stateful, Key-Addressable)

```python {"CODE_LOAD::python/src/develop/my_virtual_object.py"}  theme={null}
import restate

my_object = restate.VirtualObject("MyVirtualObject")


@my_object.handler("myHandler")
async def my_handler(ctx: restate.ObjectContext, greeting: str) -> str:
    return f"${greeting} ${ctx.key()}!"


@my_object.handler(kind="shared")
async def my_concurrent_handler(ctx: restate.ObjectSharedContext, greeting: str) -> str:
    return f"${greeting} ${ctx.key()}!"


app = restate.app([my_object])
```

### Workflows

```python {"CODE_LOAD::python/src/develop/my_workflow.py"}  theme={null}
import restate

my_workflow = restate.Workflow("MyWorkflow")


@my_workflow.main()
async def run(ctx: restate.WorkflowContext, req: str) -> str:
    # ... implement workflow logic here ---
    return "success"


@my_workflow.handler()
async def interact_with_workflow(ctx: restate.WorkflowSharedContext, req: str):
    # ... implement interaction logic here ...
    return


app = restate.app([my_workflow])
```

## Context Operations

### State Management (Virtual Objects & Workflows only)

❌ Never use global variables - not durable, lost across replicas.
✅ Use `ctx.get()` and `ctx.set()` - durable and scoped to the object's key.

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#state"}  theme={null}
# Get state
count = await ctx.get("count", type_hint=int) or 0

# Set state
ctx.set("count", count + 1)

# Clear state
ctx.clear("count")
ctx.clear_all()

# Get all state keys
keys = ctx.state_keys()
```

### Service Communication

#### Request-Response

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#service_calls"}  theme={null}
# Call a Service
response = await ctx.service_call(my_handler, "Hi")

# Call a Virtual Object
response2 = await ctx.object_call(my_object_handler, key="object-key", arg="Hi")

# Call a Workflow
response3 = await ctx.workflow_call(run, "wf-id", arg="Hi")
```

#### One-Way Messages

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#sending_messages"}  theme={null}
ctx.service_send(my_handler, "Hi")
ctx.object_send(my_object_handler, key="object-key", arg="Hi")
ctx.workflow_send(run, "wf-id", arg="Hi")
```

#### Delayed Messages

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#delayed_messages"}  theme={null}
ctx.service_send(
    my_handler,
    "Hi",
    send_delay=timedelta(hours=5)
)
```

#### Generic Calls

Call a service without using the generated client, but just String names.

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#request_response_generic"}  theme={null}
response = await ctx.generic_call(
    "MyObject", "my_handler", key="Mary", arg=json.dumps("Hi").encode("utf-8")
)
```

#### With Idempotency Key

```python  theme={null}
response = await ctx.service_call(
    my_service.my_handler,
    "Hi",
    idempotency_key="my-key"
)
```

### Run Actions or Side Effects (Non-Deterministic Operations)

❌ Never call external APIs/DBs directly - will re-execute during replay, causing duplicates.
✅ Wrap in `ctx.run()` or `ctx.run_typed()` - Restate journals the result; runs only once.

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#durable_steps"}  theme={null}
# Wrap non-deterministic code in ctx.run
result = await ctx.run_typed("my-side-effect", call_external_api, query="weather", some_id="123")

# Or with typed version for better type safety
result = await ctx.run_typed("my-side-effect", call_external_api)
```

### Deterministic randoms and time

❌ Never use `random.random()` - non-deterministic and breaks replay logic.
✅ Use `ctx.random()` or `ctx.uuid4()` - Restate journals the result for deterministic replay.

❌ Never use `time.time()`, `datetime.now()` - returns different values during replay.
✅ Use `ctx.now()` - Restate records and replays the same timestamp.

### Durable Timers and Sleep

❌ Never use `asyncio.sleep()` or `time.sleep()` - not durable, lost on restarts.
✅ Use `ctx.sleep()` - durable timer that survives failures.

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#durable_timers"}  theme={null}
# Sleep
await ctx.sleep(timedelta(seconds=30))

# Schedule delayed call (different from sleep + send)
ctx.service_send(
    my_handler,
    "Hi",
    send_delay=timedelta(hours=5)
)
```

### Awakeables (External Events)

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#awakeables"}  theme={null}
# Create awakeable
awakeable_id, promise = ctx.awakeable(type_hint=str)

# Send ID to external system
await ctx.run_typed("request_human_review", request_human_review, name=name, awakeable_id=awakeable_id)

# Wait for result
review = await promise

# Resolve from another handler
ctx.resolve_awakeable(awakeable_id, "Looks good!")

# Reject from another handler
ctx.reject_awakeable(awakeable_id, "Cannot be reviewed")
```

### Durable Promises (Workflows only)

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#workflow_promises"}  theme={null}
# Wait for promise
review = await ctx.promise("review").value()

# Resolve promise
await ctx.promise("review").resolve("approval")
```

## Concurrency

Always use Restate combinators (`restate.gather`, `restate.select`) instead of Python's native `asyncio` methods - they journal execution order for deterministic replay.

### `restate.gather()` - Wait for All

Returns when all futures complete. Use to wait for multiple operations to finish.

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#gather"}  theme={null}
# ❌ BAD
results1 = await asyncio.gather(call1(), call2())

# ✅ GOOD
claude_call = ctx.service_call(ask_openai, "What is the weather?")
openai_call = ctx.service_call(ask_claude, "What is the weather?")
results2 = await restate.gather(claude_call, openai_call)
```

### `restate.select()` - Race Multiple Operations

Returns immediately when the first future completes. Use for timeouts and racing operations.

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#select"}  theme={null}
# ❌ BAD
result1 = await asyncio.wait([call1(), call2()], return_when=asyncio.FIRST_COMPLETED)

# ✅ GOOD
confirmation = ctx.awakeable(type_hint=str)
match await restate.select(
    confirmation=confirmation[1],
    timeout=ctx.sleep(timedelta(days=1))
):
    case ["confirmation", result]:
        print("Got confirmation:", result)
    case ["timeout", _]:
        raise restate.TerminalError("Timeout!")
```

### Invocation Management

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#cancel"}  theme={null}
# Send a request, get the invocation id
handle = ctx.service_send(
    my_handler, arg="Hi", idempotency_key="my-idempotency-key"
)
invocation_id = await handle.invocation_id()

# Now re-attach
result = await ctx.attach_invocation(invocation_id)

# Cancel invocation
ctx.cancel_invocation(invocation_id)
```

## Serialization

### Default (JSON)

By default, Python SDK uses built-in JSON support with type hints.

### Pydantic Models

For type safety and validation with Pydantic:

```python {"CODE_LOAD::python/src/develop/agentsmd/serialization.py#pydantic"}  theme={null}
import restate
from pydantic import BaseModel
from restate.serde import Serde


class Greeting(BaseModel):
    name: str

class GreetingResponse(BaseModel):
    result: str

greeter = restate.Service("Greeter")

@greeter.handler()
async def greet(ctx: restate.Context, greeting: Greeting) -> GreetingResponse:
    return GreetingResponse(result=f"You said hi to {greeting.name}!")
```

### Custom Serialization

```python {"CODE_LOAD::python/src/develop/agentsmd/serialization.py#custom"}  theme={null}
class MyData(typing.TypedDict):
    """Represents a response from the GPT model."""

    some_value: str
    my_number: int


class MySerde(Serde[MyData]):
    def deserialize(self, buf: bytes) -> typing.Optional[MyData]:
        if not buf:
            return None
        data = json.loads(buf)
        return MyData(some_value=data["some_value"], my_number=data["some_number"])

    def serialize(self, obj: typing.Optional[MyData]) -> bytes:
        if obj is None:
            return bytes()
        data = {"some_value": obj["some_value"], "some_number": obj["my_number"]}
        return bytes(json.dumps(data), "utf-8")

# For the input/output serialization of your handlers
@my_object.handler(input_serde=MySerde(), output_serde=MySerde())
async def my_handler(ctx: restate.ObjectContext, greeting: str) -> str:

    # To serialize state
    await ctx.get("my_state", serde=MySerde())
    ctx.set("my_state", MyData(some_value="Hi", my_number=15), serde=MySerde())

    # To serialize awakeable payloads
    ctx.awakeable(serde=MySerde())

    # etc.

    return "some-output"
```

## Error Handling

Restate retries failures indefinitely by default. For permanent business-logic failures (invalid input, declined payment), use TerminalError to stop retries immediately.

### Terminal Errors (No Retry)

```python {"CODE_LOAD::python/src/develop/agentsmd/error_handling.py#terminal"}  theme={null}
from restate import TerminalError

raise TerminalError("Invalid input - will not retry")
```

### Retryable Errors

```python  theme={null}
# Any other thrown error will be retried
raise Exception("Temporary failure - will retry")
```

## Testing

Install with `pip install restate_sdk[harness]`

```python {"CODE_LOAD::python/src/develop/agentsmd/testing.py#here"}  theme={null}
import restate

from src.develop.my_service import app

with restate.test_harness(app) as harness:
    restate_client = harness.ingress_client()
    print(restate_client.post("/greeter/greet", json="Alice").json())
```

---


## File: docs/agents/durable/restate/ai-examples/openai-agents/template/.cursor/rules/AGENTS.md

# Restate Python SDK Rules

## Core Concepts

* Restate provides durable execution: code automatically stores completed steps and resumes from where it left off on failures
* All handlers receive a `Context`/`ObjectContext`/`WorkflowContext`/`ObjectSharedContext`/`WorkflowSharedContext` object as the first argument
* Handlers can take typed inputs and return typed outputs using Python type hints and Pydantic models

## Service Types

### Basic Services

```python {"CODE_LOAD::python/src/develop/my_service.py"}  theme={null}
import restate

my_service = restate.Service("MyService")


@my_service.handler("myHandler")
async def my_handler(ctx: restate.Context, greeting: str) -> str:
    return f"${greeting}!"


app = restate.app([my_service])
```

### Virtual Objects (Stateful, Key-Addressable)

```python {"CODE_LOAD::python/src/develop/my_virtual_object.py"}  theme={null}
import restate

my_object = restate.VirtualObject("MyVirtualObject")


@my_object.handler("myHandler")
async def my_handler(ctx: restate.ObjectContext, greeting: str) -> str:
    return f"${greeting} ${ctx.key()}!"


@my_object.handler(kind="shared")
async def my_concurrent_handler(ctx: restate.ObjectSharedContext, greeting: str) -> str:
    return f"${greeting} ${ctx.key()}!"


app = restate.app([my_object])
```

### Workflows

```python {"CODE_LOAD::python/src/develop/my_workflow.py"}  theme={null}
import restate

my_workflow = restate.Workflow("MyWorkflow")


@my_workflow.main()
async def run(ctx: restate.WorkflowContext, req: str) -> str:
    # ... implement workflow logic here ---
    return "success"


@my_workflow.handler()
async def interact_with_workflow(ctx: restate.WorkflowSharedContext, req: str):
    # ... implement interaction logic here ...
    return


app = restate.app([my_workflow])
```

## Context Operations

### State Management (Virtual Objects & Workflows only)

❌ Never use global variables - not durable, lost across replicas.
✅ Use `ctx.get()` and `ctx.set()` - durable and scoped to the object's key.

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#state"}  theme={null}
# Get state
count = await ctx.get("count", type_hint=int) or 0

# Set state
ctx.set("count", count + 1)

# Clear state
ctx.clear("count")
ctx.clear_all()

# Get all state keys
keys = ctx.state_keys()
```

### Service Communication

#### Request-Response

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#service_calls"}  theme={null}
# Call a Service
response = await ctx.service_call(my_handler, "Hi")

# Call a Virtual Object
response2 = await ctx.object_call(my_object_handler, key="object-key", arg="Hi")

# Call a Workflow
response3 = await ctx.workflow_call(run, "wf-id", arg="Hi")
```

#### One-Way Messages

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#sending_messages"}  theme={null}
ctx.service_send(my_handler, "Hi")
ctx.object_send(my_object_handler, key="object-key", arg="Hi")
ctx.workflow_send(run, "wf-id", arg="Hi")
```

#### Delayed Messages

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#delayed_messages"}  theme={null}
ctx.service_send(
    my_handler,
    "Hi",
    send_delay=timedelta(hours=5)
)
```

#### Generic Calls

Call a service without using the generated client, but just String names.

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#request_response_generic"}  theme={null}
response = await ctx.generic_call(
    "MyObject", "my_handler", key="Mary", arg=json.dumps("Hi").encode("utf-8")
)
```

#### With Idempotency Key

```python  theme={null}
response = await ctx.service_call(
    my_service.my_handler,
    "Hi",
    idempotency_key="my-key"
)
```

### Run Actions or Side Effects (Non-Deterministic Operations)

❌ Never call external APIs/DBs directly - will re-execute during replay, causing duplicates.
✅ Wrap in `ctx.run()` or `ctx.run_typed()` - Restate journals the result; runs only once.

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#durable_steps"}  theme={null}
# Wrap non-deterministic code in ctx.run
result = await ctx.run_typed("my-side-effect", call_external_api, query="weather", some_id="123")

# Or with typed version for better type safety
result = await ctx.run_typed("my-side-effect", call_external_api)
```

### Deterministic randoms and time

❌ Never use `random.random()` - non-deterministic and breaks replay logic.
✅ Use `ctx.random()` or `ctx.uuid4()` - Restate journals the result for deterministic replay.

❌ Never use `time.time()`, `datetime.now()` - returns different values during replay.
✅ Use `ctx.now()` - Restate records and replays the same timestamp.

### Durable Timers and Sleep

❌ Never use `asyncio.sleep()` or `time.sleep()` - not durable, lost on restarts.
✅ Use `ctx.sleep()` - durable timer that survives failures.

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#durable_timers"}  theme={null}
# Sleep
await ctx.sleep(timedelta(seconds=30))

# Schedule delayed call (different from sleep + send)
ctx.service_send(
    my_handler,
    "Hi",
    send_delay=timedelta(hours=5)
)
```

### Awakeables (External Events)

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#awakeables"}  theme={null}
# Create awakeable
awakeable_id, promise = ctx.awakeable(type_hint=str)

# Send ID to external system
await ctx.run_typed("request_human_review", request_human_review, name=name, awakeable_id=awakeable_id)

# Wait for result
review = await promise

# Resolve from another handler
ctx.resolve_awakeable(awakeable_id, "Looks good!")

# Reject from another handler
ctx.reject_awakeable(awakeable_id, "Cannot be reviewed")
```

### Durable Promises (Workflows only)

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#workflow_promises"}  theme={null}
# Wait for promise
review = await ctx.promise("review").value()

# Resolve promise
await ctx.promise("review").resolve("approval")
```

## Concurrency

Always use Restate combinators (`restate.gather`, `restate.select`) instead of Python's native `asyncio` methods - they journal execution order for deterministic replay.

### `restate.gather()` - Wait for All

Returns when all futures complete. Use to wait for multiple operations to finish.

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#gather"}  theme={null}
# ❌ BAD
results1 = await asyncio.gather(call1(), call2())

# ✅ GOOD
claude_call = ctx.service_call(ask_openai, "What is the weather?")
openai_call = ctx.service_call(ask_claude, "What is the weather?")
results2 = await restate.gather(claude_call, openai_call)
```

### `restate.select()` - Race Multiple Operations

Returns immediately when the first future completes. Use for timeouts and racing operations.

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#select"}  theme={null}
# ❌ BAD
result1 = await asyncio.wait([call1(), call2()], return_when=asyncio.FIRST_COMPLETED)

# ✅ GOOD
confirmation = ctx.awakeable(type_hint=str)
match await restate.select(
    confirmation=confirmation[1],
    timeout=ctx.sleep(timedelta(days=1))
):
    case ["confirmation", result]:
        print("Got confirmation:", result)
    case ["timeout", _]:
        raise restate.TerminalError("Timeout!")
```

### Invocation Management

```python {"CODE_LOAD::python/src/develop/agentsmd/actions.py#cancel"}  theme={null}
# Send a request, get the invocation id
handle = ctx.service_send(
    my_handler, arg="Hi", idempotency_key="my-idempotency-key"
)
invocation_id = await handle.invocation_id()

# Now re-attach
result = await ctx.attach_invocation(invocation_id)

# Cancel invocation
ctx.cancel_invocation(invocation_id)
```

## Serialization

### Default (JSON)

By default, Python SDK uses built-in JSON support with type hints.

### Pydantic Models

For type safety and validation with Pydantic:

```python {"CODE_LOAD::python/src/develop/agentsmd/serialization.py#pydantic"}  theme={null}
import restate
from pydantic import BaseModel
from restate.serde import Serde


class Greeting(BaseModel):
    name: str

class GreetingResponse(BaseModel):
    result: str

greeter = restate.Service("Greeter")

@greeter.handler()
async def greet(ctx: restate.Context, greeting: Greeting) -> GreetingResponse:
    return GreetingResponse(result=f"You said hi to {greeting.name}!")
```

### Custom Serialization

```python {"CODE_LOAD::python/src/develop/agentsmd/serialization.py#custom"}  theme={null}
class MyData(typing.TypedDict):
    """Represents a response from the GPT model."""

    some_value: str
    my_number: int


class MySerde(Serde[MyData]):
    def deserialize(self, buf: bytes) -> typing.Optional[MyData]:
        if not buf:
            return None
        data = json.loads(buf)
        return MyData(some_value=data["some_value"], my_number=data["some_number"])

    def serialize(self, obj: typing.Optional[MyData]) -> bytes:
        if obj is None:
            return bytes()
        data = {"some_value": obj["some_value"], "some_number": obj["my_number"]}
        return bytes(json.dumps(data), "utf-8")

# For the input/output serialization of your handlers
@my_object.handler(input_serde=MySerde(), output_serde=MySerde())
async def my_handler(ctx: restate.ObjectContext, greeting: str) -> str:

    # To serialize state
    await ctx.get("my_state", serde=MySerde())
    ctx.set("my_state", MyData(some_value="Hi", my_number=15), serde=MySerde())

    # To serialize awakeable payloads
    ctx.awakeable(serde=MySerde())

    # etc.

    return "some-output"
```

## Error Handling

Restate retries failures indefinitely by default. For permanent business-logic failures (invalid input, declined payment), use TerminalError to stop retries immediately.

### Terminal Errors (No Retry)

```python {"CODE_LOAD::python/src/develop/agentsmd/error_handling.py#terminal"}  theme={null}
from restate import TerminalError

raise TerminalError("Invalid input - will not retry")
```

### Retryable Errors

```python  theme={null}
# Any other thrown error will be retried
raise Exception("Temporary failure - will retry")
```

## Testing

Install with `pip install restate_sdk[harness]`

```python {"CODE_LOAD::python/src/develop/agentsmd/testing.py#here"}  theme={null}
import restate

from src.develop.my_service import app

with restate.test_harness(app) as harness:
    restate_client = harness.ingress_client()
    print(restate_client.post("/greeter/greet", json="Alice").json())
```

---


## File: docs/agents/durable/restate/ai-examples/openai-agents/template/README.md

# Resilient agents with Restate + OpenAI Agents Python SDK
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](agent.py)

Use the OpenAI Agent SDK to implement your agent, and let Restate handle the persistence and resiliency of the agent's decisions and tool executions.

The example is an agent that can search for the weather in certain city.

<img src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/get-started-openai/invocation_ui.png" alt="Using Agent SDK - journal" width="1200px"/>

> Also check out the Tour of Agents with [the OpenAI Agents SDK + Restate](../tour-of-agents) 

## Running the example

1. Export your OpenAI or Anthrophic API key as an environment variable:
    ```shell
    export OPENAI_API_KEY=your_openai_api_key
    ```
2. [Start the Restate Server](https://docs.restate.dev/develop/local_dev) in a separate shell:
    ```shell
    restate-server
    ```
3. Start the services:
    ```shell
    uv run .
    ```
4. Register the services: 
    ```shell
    restate -y deployments register localhost:9080
    ```

5. Send requests to your agent:

    ```shell
    curl localhost:8080/agent/run --json '"What is the weather in Detroit?"'
    ```
    
    Returns: `The weather in Detroit is currently 22°C and sunny.`


Check the Restate UI (`http://localhost:9080`) to see the journals of your invocations (remove the filters).

<img src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/get-started-openai/detailed_invocation_ui.png" alt="Using Agent SDK - journal" width="1200px"/>

## Integrating Restate with the OpenAI Python Agent SDK

To make the agent resilient, we need to:
- Persist the results of LLM calls in Restate's journal by wrapping them in `ctx.run()`. This is handled by the `RestateModelProvider`.
- To persist the intermediate tool execution steps, we pass the Restate context along to the tools.

## Limitations
1. You cannot do parallel tool calls or any type of parallel execution if you integrate Restate with an Agent SDK. 
If you execute actions on the context in different tools in parallel, Restate will not be able to deterministically replay them because the order might be different during recovery and will crash. 
We are working on a solution to this, but for now, you can only use Restate with Agent SDKs for sequential tool calls.

2. Restate does not yet support streaming responses from the Vercel AI SDK.

---


## File: docs/agents/durable/restate/ai-examples/openai-agents/tour-of-agents/README.md

# Tour of AI Agents with Restate - Python OpenAI Agents SDK
Learn how to implement resilient agents with durable execution, human-in-the-loop, multi-agent communication, and parallel execution.

[Learn more](https://docs.restate.dev/tour/openai-agents)

To run:
```shell
uv run .
```
---


## File: docs/agents/durable/restate/ai-examples/python-patterns/README.md

# Patterns for building resilient LLM-based apps and agents with Restate

These patterns show how you can use Restate to harden LLM-based routing decisions and tool executions.

These small self-contained patterns can be mixed and matched to build more complex agents or workflows.

The patterns included here:
- [Chaining LLM calls](app/chaining.py): Build fault-tolerant processing pipelines where each step transforms the previous step's output.
- [Tool routing](app/routing_to_tool.py): Automatically route requests to tools based on LLM outputs.
- [Parallel tool execution](app/parallel_tools.py): Execute multiple tools in parallel with durable results that persist across failures.
- [Multi-agent routing](app/routing_to_agent.py): Route requests to specialized agents based on LLM outputs.
- [Remote agent routing](app/routing_to_remote_agent.py): Deploy/scale agents separately and route requests with resilient communication.
- [Parallel agent processing](app/parallel_agents.py): Run multiple, specialized agents in parallel and aggregate their results.
- [Racing agents](app/racing_agents.py): Race multiple agents and return the result from whichever completes first successfully.
- [Orchestrator-worker pattern](app/orchestrator_workers.py): Break down complex tasks into specialized subtasks and execute them in parallel.
- [Evaluator-optimizer pattern](app/evaluator_optimizer.py): Generate → Evaluate → Improve loop until quality criteria are met.
- [Human-in-the-loop pattern](app/human_in_the_loop.py): Implement resilient human approval steps that suspend execution until feedback is received.
- [Chat sessions](app/chat.py): Long-lived, stateful chat sessions that maintain conversation state across multiple requests.

## Why Restate?

The benefits of using Restate here are:
- 🔁 **Automatic retries** of failed tasks: LLM API down, timeouts, long-running tasks, infrastructure failures, etc. Restate guarantees all tasks run to completion exactly once.
- ✅ **Recovery of previous progress**: After a failure, Restate recovers the progress the execution did before the crash. 
It persists routing decisions, tool execution outcomes, and deterministically replays them after failures, as opposed to executing them again. 
- 🧠 **Exactly-once execution** - Automatic deduplication of requests and tool executions via idempotency keys.
- 💾 **Persistent memory** - Maintain session state across infrastructure events.
The state can be queried from the outside. Stateful sessions are long-lived and can be resumed at any time.
- 🎮 **Task control** - Cancel tasks, query status, re-subscribe to ongoing tasks, and track progress across failures, time, and processes.


## Running the examples

1. Export your OpenAI API key as an environment variable:
    ```shell
    export OPENAI_API_KEY=your_openai_api_key
    ```
2. [Start the Restate Server](https://docs.restate.dev/develop/local_dev) in a separate shell:
    ```shell
    restate-server
    ```
3. Start the services:
    ```shell
    uv run .
    ```
4. Register the services (use `--force` if you already had another deployment registered at 9080): 
    ```shell
    restate -y deployments register localhost:9080 --force
    ```

### Chaining LLM calls
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](app/chaining.py)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/prompt-chaining)

Build fault-tolerant processing pipelines where each step transforms the previous step's output.

In the UI (`http://localhost:9070`), click on the `process` handler of the `CallChainingService` to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/chaining_playground.png" alt="Chaining LLM calls - UI"/>

You see in the Invocations Tab of the UI how the LLM is called multiple times, and how the results are refined step by step:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/chaining.png" alt="Chaining LLM calls - UI"/>

### Tool routing
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](app/routing_to_tool.py)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/tools)

Automatically route requests to tools based on LLM outputs. The agent keeps calling the LLM and executing tools until a final answer is returned.

In the UI (`http://localhost:9070`), click on the `route` handler of the `ToolRouter` service to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/routing_local_tools_playground.png" alt="Dynamic routing LLM calls - UI"/>

In the UI, you can see how the LLM decides to forward the request to the technical support tools, and how the response is processed:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/routing_local_tools.png" alt="Dynamic routing based on LLM output - UI"/>

### Parallel tool execution
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](app/parallel_tools.py)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/parallelization)

Execute multiple tools in parallel with durable results that persist across failures.

In the UI (`http://localhost:9070`), click on the `run` handler of the `ParallelToolAgent` to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/parallel_tools_playground.png" alt="Parallel tool calls - UI"/>

You see in the UI how the different tools are executed in parallel:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/parallel_tools.png" alt="Parallel tool calls - UI"/>

Once all tools are done, the results are aggregated and returned to the client.

### Multi-agent routing
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](app/routing_to_agent.py)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/multi-agent)

Route requests to specialized agents based on LLM outputs. Routing decisions are persisted and can be retried.

In the UI (`http://localhost:9070`), click on the `answer` handler of the `AgentRouter` service to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/routing_local_agent_playground.png" alt="Multi-agent routing - UI"/>

In the UI, you can see how the LLM decides to forward the request to the specialized support agents, and how the response is processed:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/routing_local_agent.png" alt="Multi-agent routing - UI"/>

### Remote agent routing
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](app/routing_to_remote_agent.py)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/multi-agent)

Route requests to remote agents with resilient communication. 
Restate proxies requests to remote agents, persisting routing decisions and results. 
In case of failures, Restate retries failed executions.

In the UI (`http://localhost:9070`), click on the `answer` handler of the `RemoteAgentRouter` service to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/routing_remote_agent_playground.png" alt="Multi-agent routing - UI"/>

In the UI, you can see how the LLM decides to forward the request to the specialized support agents, and how the nested call is also shown in the UI:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/routing_remote_agent.png" alt="Multi-agent routing - UI"/>

### Parallel agent processing
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](app/parallel_agents.py)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/parallelization)

Run multiple, specialized agents in parallel and aggregate their results. If any agent fails, Restate retries only the failed agents while preserving completed results.

In the UI (`http://localhost:9070`), click on the `analyze` handler of the `ParallelAgentsService` to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/parallel_agents_playground.png" alt="Parallel agents - UI"/>

You see in the UI how the different agents are executed in parallel:
<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/parallel_agents.png" alt="Parallel agents - UI"/>

Once all agents are done, the results are aggregated and returned to the client.

### Racing agents
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](app/racing_agents.py)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/competitive-racing)

Execute multiple AI approaches or strategies simultaneously and return the result from whichever completes first successfully.

Restate turns Promises/Futures into durable, distributed constructs that persist across failures and process restarts.

In the UI (`http://localhost:9070`), click on the `run` handler of the `RacingAgent` service to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/typescript_patterns/doc/img/patterns/racing_playground.png" alt="Racing agents - UI"/>

You see in the UI how the different agents are executed in parallel and the first successful result is returned, while the other agents are cancelled:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/typescript_patterns/doc/img/patterns/racing.png" alt="Racing agents - UI"/>

### Human-in-the-loop pattern
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](app/human_in_the_loop.py)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/human-in-the-loop)

Implement resilient human approval steps that suspend execution until feedback is received. Durable promises survive crashes and can be recovered across process restarts.

In the UI (`http://localhost:9070`), click on the `moderate` handler of the `HumanInTheLoopService` to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/human-in-the-loop-playground.png" alt="Human-in-the-loop pattern - UI"/>

Test this out by killing the service halfway through or restarting the Restate Server. You will notice that Restate will still be able to resolve the promise and invoke the handler again.

Then use the **curl command printed in the service logs** to provide your feedback.

You can see how the feedback gets incorporated in the Invocations tab in the Restate UI (`http://localhost:9070`):

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/human-in-the-loop.png" alt="Human-in-the-loop pattern - UI"/>

### Chat sessions
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](app/chat.py)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/sessions-and-chat)

Long-lived, stateful chat sessions that maintain conversation state across multiple requests. Sessions survive failures and can be resumed at any time.

In the UI (`http://localhost:9070`), click on the `message` handler of the `Chat` service to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/chat-1.png" alt="Chat" width="900px"/>

You can then provide feedback on the response by sending new messages to the same session:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/chat-2.png" alt="Chat" width="900px"/>

In the invocations tab, you can see how the memory was loaded and stored in Restate:
<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/chat.png" alt="Chat - UI"/>

Go to the state tab of the UI to see the state of the chat session:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/chat-state.png" alt="Chat" width="900px"/>


### Orchestrator-worker pattern
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](app/orchestrator_workers.py)

Break down complex tasks into specialized subtasks and execute them in parallel. If any worker fails, Restate retries only that worker while preserving other completed work.

In the UI (`http://localhost:9070`), click on the `process` handler of the `Orchestrator` to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/orchestrator-playground.png" alt="Orchestrator LLM calls - UI"/>

In the UI, you can see how the LLM split the task in three parts and how each of the worker LLMs execute their tasks in parallel:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/orchestrator.png" alt="Orchestrator-worker pattern - UI"/>

### Evaluator-optimizer pattern
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](app/evaluator_optimizer.py)

Generate → Evaluate → Improve loop until quality criteria are met. Restate persists each iteration, resuming from the last completed step on failure.

In the UI (`http://localhost:9070`), click on the `run` handler of the `EvaluatorOptimizer` to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/evaluator-playground.png" alt="Evaluator-optimizer pattern - UI"/>

In the UI, you can see how the LLM generates a response, and how the evaluator LLM evaluates it and asks for improvements until the response is satisfactory:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/evaluator.png" alt="Evaluator-optimizer pattern - UI"/>

---


## File: docs/agents/durable/restate/ai-examples/README.md

<!-- markdown-link-check-disable -->
[![Documentation](https://img.shields.io/badge/doc-reference-blue)](https://docs.restate.dev)
[![Discord](https://img.shields.io/discord/1128210118216007792?logo=discord)](https://discord.gg/skW3AZ6uGd)
[![Slack](https://img.shields.io/badge/Slack-4A154B?logo=slack&logoColor=fff)](https://join.slack.com/t/restatecommunity/shared_invite/zt-2v9gl005c-WBpr167o5XJZI1l7HWKImA)
[![Twitter](https://img.shields.io/twitter/follow/restatedev.svg?style=social&label=Follow)](https://x.com/intent/follow?screen_name=restatedev)
<!-- markdown-link-check-enable -->

# Examples for AI workflows and Durable Agents

This repo contains a set of runnable examples of AI workflows and agents, using  **Durable Execution and Orchestration** via [Restate](https://restate.dev/) ([Github](https://github.com/restatedev/restate))

The goal is to show how you can easily add production-grade _resilience_, _state persistence_, _retries_, _suspend/resume_, _human-in-the-loop_, and _observability_ to agentic workflows. So you can ship agents that stay alive and consistent without sprinkling retry-code everywhere and without building heavyweight infra yourself.

The Restate approach works **independent of specific SDKs** but **integrates easily with popular SDKs**, like the [Vercel AI SDK](https://ai-sdk.dev/) or the [OpenAI Agent SDK](https://openai.github.io/openai-agents-python/). You can also use without and Agent SDK _(roll your own loop)_ or for more traditional workflows.


## Why Restate?
📄 For a gentle intro, read [the blog post "Durable Agents - Fault Tolerance across Frameworks and without Handcuffs"](https://restate.dev/blog/durable-ai-loops-fault-tolerance-across-frameworks-and-without-handcuffs/)


| Use Case                           | What it solves                                                                              |
|------------------------------------|---------------------------------------------------------------------------------------------|
| **Durable Execution**              | Crash-safe LLM/tool calls & idempotent retries—agents resume at the last successful step.   |
| **Detailed Observability**         | Auto-captured trace of every step, retry, and message for easy debugging and auditing.      |
| **Human-in-the-loop & long waits** | Suspend while waiting for user approval or slow jobs; pay for compute, not wall-clock time. |
| **Stateful sessions / memory**     | Virtual Objects keep multi-turn conversations and other state isolated and consistent.      |
| **Multi-agent orchestration**      | Reliable RPC, queuing, and scheduling between agents running in separate processes.         |


<img src="/doc/img/patterns/parallel_tools.png" alt="Restate UI - trace of agent with parallel tools" width="900px"/>
<br/>
<caption><em>Restate UI showing an agent execution with parallel tool calls</em></caption>


## Full Example Catalog

### Agent SDK Integrations  
| Integration | Example | Description | Code | Docs                                                 |
|-------------|---------|-------------|------|------------------------------------------------------|
| **Vercel AI SDK** | **Template** | A minimal example of how to use Restate with the Vercel AI SDK | [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](vercel-ai/template) | [📖](https://docs.restate.dev/ai-quickstart)         |
| | **Tour of Agents** | A step-by-step tutorial showing how to build resilient agents | [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](vercel-ai/tour-of-agents) | [📖](https://docs.restate.dev/tour/vercel-ai-agents) |
| | **Examples** | More advanced examples that can be deployed as a Next.js app on Vercel | [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](vercel-ai/examples) | -                                                    |
| **OpenAI Agents SDK** | **Template** | A minimal example of how to use Restate with the OpenAI Agents SDK | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](openai-agents/template) | [📖](https://docs.restate.dev/ai-quickstart)         |
| | **Tour of Agents** | A step-by-step tutorial showing how to build resilient agents | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](openai-agents/tour-of-agents) | [📖](https://docs.restate.dev/tour/openai-agents)    |

### Composable AI Patterns
| Pattern                | Description | Code | Docs |
|------------------------|-------------|------|------|
| **Chaining LLM calls** | Build fault-tolerant processing pipelines where each step transforms the previous step's output | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/chaining.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/chaining.ts) | [📖](https://docs.restate.dev/ai/patterns/prompt-chaining) |
| **Tool routing** | Automatically route requests to tools based on LLM outputs | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/routing_to_tool.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/routing-to-tools.ts) | [📖](https://docs.restate.dev/ai/patterns/tools) |
| **Parallel tool execution** | Execute multiple tools in parallel with durable results that persist across failures | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/parallel_tools.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/parallel-tools.ts) | [📖](https://docs.restate.dev/ai/patterns/parallelization) |
| **Multi-agent routing** | Route requests to specialized agents based on LLM outputs | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/routing_to_agent.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/routing-to-agent.ts) | [📖](https://docs.restate.dev/ai/patterns/multi-agent) |
| **Remote agent routing** | Deploy/scale agents separately and route requests with resilient communication | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/routing_to_remote_agent.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/routing-to-remote-agent.ts) | [📖](https://docs.restate.dev/ai/patterns/multi-agent) |
| **Parallel agent processing** | Run multiple, specialized agents in parallel and aggregate their results | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/parallel_agents.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/parallel-agents.ts) | [📖](https://docs.restate.dev/ai/patterns/parallelization) |
| **Racing agents** | Race multiple agents against each other and use the fastest response | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/racing_agents.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/racing-agents.ts) | [📖](https://docs.restate.dev/ai/patterns/competitive-racing) |
| **Human-in-the-loop pattern** | Implement resilient human approval steps that suspend execution until feedback is received | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/human_in_the_loop.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/human-in-the-loop.ts) | [📖](https://docs.restate.dev/ai/patterns/human-in-the-loop) |
| **Chat sessions** | Long-lived, stateful chat sessions that maintain conversation state across multiple requests | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/chat.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/chat.ts) | [📖](https://docs.restate.dev/ai/patterns/sessions-and-chat) |
| **Orchestrator-worker pattern** | Break down complex tasks into specialized subtasks and execute them in parallel | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/orchestrator_workers.py) | - |
| **Evaluator-optimizer pattern** | Generate → Evaluate → Improve loop until quality criteria are met | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/evaluator_optimizer.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/evaluator-optimizer.ts) | - |

### Other Examples
| Example                | Description | Code |
|------------------------|-------------|------|
| **MCP**                |  Using Restate for exposing tools and resilient orchestration of tool calls | [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](mcp) | 
| **A2A**                | Implement Google's Agent-to-Agent protocol with Restate as resilient, scalable task orchestrator | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](a2a) | 

Restate currently supports 6 languages:

[![TypeScript](https://skillicons.dev/icons?i=ts)](https://docs.restate.dev/develop/ts/overview)
[![Python](https://skillicons.dev/icons?i=python&theme=light)](https://docs.restate.dev/develop/python/overview)
[![Java](https://skillicons.dev/icons?i=java&theme=light)](https://docs.restate.dev/develop/java/overview)
[![Kotlin](https://skillicons.dev/icons?i=kotlin&theme=light)](https://docs.restate.dev/develop/java/overview)
[![Go](https://skillicons.dev/icons?i=go)](https://docs.restate.dev/develop/go/overview)
[![Rust](https://skillicons.dev/icons?i=rust&theme=light)](https://docs.rs/restate-sdk/latest/restate_sdk/)

The examples can be translated to any of the supported languages. 
Join our [Discord](https://discord.gg/skW3AZ6uGd)/[Slack](https://join.slack.com/t/restatecommunity/shared_invite/zt-2v9gl005c-WBpr167o5XJZI1l7HWKImA) to get help with translating an examples to your language of choice.

## Learn more
- [Documentation](https://docs.restate.dev/ai)
- [Examples on workflows, microservice orchestration, async tasks, event processing](https://github.com/restatedev/examples)
- [Restate Cloud](https://restate.dev/cloud/)
- [Discord](https://discord.gg/skW3AZ6uGd) / [Slack](https://join.slack.com/t/restatecommunity/shared_invite/zt-2v9gl005c-WBpr167o5XJZI1l7HWKImA)

## Acknowledgements

- The DIY patterns are largely based on Anthropic's [agents cookbook](https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents).
- Some of the A2A examples in this repo are based on the examples included in the [Google A2A repo](https://github.com/google/A2A/tree/main).

---


## File: docs/agents/durable/restate/ai-examples/vercel-ai/examples/README.md

# Restate and Vercel AI SDK examples

A set of examples illustrating how to use [Restate](https://restate.dev/) ([Github](https://github.com/restatedev/)) to add durable execution, state, and communication to agents built with the [Vercel AI SDK](https://ai-sdk.dev)

## Setting up an Environment

### Starting Restate Server

```shell
npx @restatedev/restate-server@latest
```

```bash

### Starting the Agents NextJS app

The project is a basic Next.js project, bootstrapped form the standard template.

```bash
npm run dev
```

The entry point is in the [restate/v1](app/restate/v1/[[...services]]/route.ts) route.

### Register the AI SDK agents at Restate

```shell
npx @restatedev/restate deployments register http://localhost:3000/restate/v1 --use-http1.1
```

Or use the UI on `localhost:9070` to register the services.

## An Example Walkthrough

Code: [multi_tool.ts](restate/services/multi_tool.ts)

This is inspired by this example: https://ai-sdk.dev/docs/foundations/agents#using-maxsteps 

The example is almost vanilla Vercel AI SDK code, with three small additions:

1. The AI agent function (`useToolsExample(...)`) is run as a Restate durable service handler.
   This gives the code durable retries and enables all further features.
   ```typescript
   export default restate.service({
     name: "tools",
     handlers: {
       message:
         // ...
         async (ctx: restate.Context, { prompt }) => {
           return await useToolsExample(ctx, prompt);
         }
     }
   });
   ```

2. We wrap the LLM model to make sure all inference steps are durable journaled:
   ```typescript
   const model = wrapLanguageModel({
     model: openai("gpt-4o-2024-08-06"),
     middleware: durableCalls(ctx, { maxRetryAttempts: 3 }),
   });
   ```

3. We wrap tool calls into durable steps (`ctx.run(...)`)
   ```typescript
   execute: async ({ expression }) => {
          return await ctx.run(
            `evaluating ${expression}`,
            async () => mathjs.evaluate(expression),
            { serde: superJson }
          );
        },
   ```

### Invoking

Invoke it via http:
```shell
curl localhost:8080/tools/message --json '{ "prompt": "A taxi driver earns $9461 per 1-hour of work. If he works 12 hours a day and in 1 hour he uses 12 liters of petrol with a price of $134 for 1 liter. How much money does he earn in one day?" }'
```

Or use the UI playground in the UI on `localhost:9070`
![Restate's UI Service Playground](doc/img/playground.png)


### Investigating the execution

Use the *Invocations* tab in the UI to see ongoing invocations. Adjust the filter below to also show finished (succeeded) invocations.

*NOTE: Retention of detailed timeline information is only available in the latest nightly build that can be run with the docker command above.*

![Restate's UI showing invocations](doc/img/invocations.png)

![Restate's UI showing an invocation timeline](doc/img/invocation_timeline.png)


## Other Examples

### Human approval

This example models a workflow that needs an approval.
It uses as tool with a durable promise for that.
The promise can be completed with a separate handler on the workflow.

Code: [human_approval.ts](./restate/services/human_approval.ts)

```typescript
// tool awaiting durable promise
riskAnalysis: tool({
  description: /* ... */
  inputSchema: z.object({ amount: z.number() }),
  execute: async ({ amount }) => {
    // send some how the request to the human evaluator.
    // A human evaluator will receive a notification with all the relevant details and on their own time (maybe days later)
    // respond with the decision.
    // ctx.run("notify a human", async () => sqs.sendMessage({ ... }))

    // and now we wait for the response
    return ctx.promise("approval");
  },
}),

// approval handler
approval: async (ctx: restate.WorkflowSharedContext, approval: string) => {
  ctx.promise("approval").resolve(approval);
}
```

The UI shows how the agentic workflow suspends when awaiting the durable promise.

![Screenshot of workflow awaiting approval promise](doc/img/human_approval_pending.png)

The approval promise can be completed via the UI as well, select the *approval* handler. Make sure you address the right workflow (use the same key as you used for kicking off the workflow).

![Screenshot of completed workflow](doc/img/human_approval_complete.png)



### Chat

This is an example of using virtual object state to remember the per-user chat history.
Virtual objects give us in addition guaranteed unique keys, guaranteed single writer concurrency, and state transactionality.

Code: [chat.ts](./restate/services/chat.ts)

```shell
# the object key is in the URL (malte / timer) and extracted to obtain locks,
# fetch state, and queue
curl localhost:8080/chat/malte/message --json '{ "message": "Hi, my name is Malte" }'
curl localhost:8080/chat/timer/message --json '{ "message": "Hi, my name is Timer" }'

curl localhost:8080/chat/malte/message --json '{ "message": "Who am I?" }' # => malte
curl localhost:8080/chat/timer/message --json '{ "message": "Who am I?" }' # => timer
```

You can explore the state of the Virtual Objects in the UI.

![Screenshot of state UI](doc/img/chat_state.png)


### Multi Agent

This example shows how to let one agent call another agent.
Code: [multi_agent.ts](./restate/services/multi_agent.ts)

We use Restate's durable RPC mechanism, which gives us reliable event-based RPC,
automatic idempotency, and suspends the calling agent while the callee agent is working. 

```typescript
riskAssessmentAgent: tool({
  // we make the other agent available as a tool here
  description:
    "A risk assessment agent that will determine the risk of a given loan request " +
    "It replies an object { risk } where risk is either 'high' or 'low'. " +
    "For example: { risk: 'high' } or { risk: 'low' }",
  inputSchema: LoanRequest,
  execute: async ({ amount, reason }) => {
    // call the risk assessment agent by making a durable call to the agent workflow
    const response = await ctx
      .workflowClient<RiskAssementAgent>({ name: "risk_assess" }, ctx.key)
      .run({ amount, reason });

    return response;
  },
})
```

When asking for a loan of 50000, the risk assessment agent will be called.

The UI shows how the calling agent is suspended, while the risk assessment agent is busy.
![Screenshot of the main loan agent awaiting the risk assessment agent](doc/img/multi_agent_pending.png)

After the risk assessment agent completes, the callee resumes the workflow.
![Screenshot of the main loan agent with the completed risk assessment agent](doc/img/multi_agent_complete.png)

## Remote LLM Calls

This example demonstrates how to extract the LLM calls into a separate restate service.
Code: [remote_llm.ts](./restate/services/remote_llm.ts)

We use restate's durable RPC, virtual objects for concurrency control, and the flexibility of deployment to separate the long running 
I/O bound services (wait for the LLM to respond).
For example, clustering these calls in a Fluid compute runtime, or even a standalone VM/pod/ECS container. 

Use the `remoteCalls` middleware instead:

```typescript
const model = wrapLanguageModel({
     model: openai("gpt-4o-mini"),
     middleware: remoteCalls(ctx, { maxRetryAttempts: 3, maxConcurrency: 10 }),
});
```

## Experiment - Persistent Result Event Stream

**Note:** This is an early experiment for now.

The [Multi Tool Agent Example](./restate/services/multi_agent.ts) publishes the intermediate
messages to a pubsub stream, which is implemented as a Restate Virtual Object (see [pubsub.ts](./restate/services/pubsub.ts)).

The pubsub stream is accessible via the [/pubsub/[topic]](app/pubsub/[topic]/route.ts) route.

The agent publishes messages via this hook:
```typescript
onStepFinish: async (step) => {
      publishMessage(ctx, "channel", {
        role: "system",
        content: step.text,
      });
    },
```

Below is a screenshot of a terminal with two concurrent stream subscribers receiving the intermediate step messages with the agent's reasoning.

![Screenshot of console showing PubSub Channel](doc/img/pubsubchannel.png)

---


## File: docs/agents/durable/restate/ai-examples/vercel-ai/template_nextjs/.claude/CLAUDE.md

# Restate TypeScript SDK Rules

## Core Concepts

* Restate provides durable execution: code automatically stores completed steps and resumes from where it left off on failures
* All handlers receive a `Context`/`ObjectContext`/`WorkflowContext`/`ObjectSharedContext`/`WorkflowSharedContext` object as the first argument
* Handlers can take one optional JSON-serializable input and must return a JSON-serializable output. Or specify the serializers.

## Service Types

### Basic Services

```ts {"CODE_LOAD::ts/src/develop/service.ts"}  theme={null}
import * as restate from "@restatedev/restate-sdk";

export const myService = restate.service({
  name: "MyService",
  handlers: {
    myHandler: async (ctx: restate.Context, greeting: string) => {
      return `${greeting}!`;
    },
  },
});

restate.serve({ services: [myService] });
```

### Virtual Objects (Stateful, Key-Addressable)

```ts {"CODE_LOAD::ts/src/develop/virtual_object.ts"}  theme={null}
import * as restate from "@restatedev/restate-sdk";

export const myObject = restate.object({
  name: "MyObject",
  handlers: {
    myHandler: async (ctx: restate.ObjectContext, greeting: string) => {
      return `${greeting} ${ctx.key}!`;
    },
    myConcurrentHandler: restate.handlers.object.shared(
      async (ctx: restate.ObjectSharedContext, greeting: string) => {
        return `${greeting} ${ctx.key}!`;
      }
    ),
  },
});

restate.serve({ services: [myObject] });
```

### Workflows

```ts {"CODE_LOAD::ts/src/develop/workflow.ts"}  theme={null}
import * as restate from "@restatedev/restate-sdk";

export const myWorkflow = restate.workflow({
  name: "MyWorkflow",
  handlers: {
    run: async (ctx: restate.WorkflowContext, req: string) => {
      // implement workflow logic here

      return "success";
    },

    interactWithWorkflow: async (ctx: restate.WorkflowSharedContext) => {
      // implement interaction logic here
      // e.g. resolve a promise that the workflow is waiting on
    },
  },
});

restate.serve({ services: [myWorkflow] });
```

## Context Operations

### State Management (Virtual Objects & Workflows only)

❌ Never use global variables - not durable, lost across replicas.
✅ Use `ctx.get()` and `ctx.set()` - durable and scoped to the object's key.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#state"}  theme={null}
// Get state
const count = (await ctx.get<number>("count")) ?? 0;

// Set state
ctx.set("count", count + 1);

// Clear state
ctx.clear("count");
ctx.clearAll();

// Get all state keys
const keys = await ctx.stateKeys();
```

### Service Communication

#### Request-Response

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#service_calls"}  theme={null}
// Call a Service
const response = await ctx.serviceClient(myService).myHandler("Hi");

// Call a Virtual Object
const response2 = await ctx.objectClient(myObject, "key").myHandler("Hi");

// Call a Workflow
const response3 = await ctx.workflowClient(myWorkflow, "wf-id").run("Hi");
```

#### One-Way Messages

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#sending_messages"}  theme={null}
ctx.serviceSendClient(myService).myHandler("Hi");
ctx.objectSendClient(myObject, "key").myHandler("Hi");
ctx.workflowSendClient(myWorkflow, "wf-id").run("Hi");
```

#### Delayed Messages

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#delayed_messages"}  theme={null}
ctx.serviceSendClient(myService).myHandler(
    "Hi",
    restate.rpc.sendOpts({ delay: { hours: 5 } })
);
```

#### Generic Calls

Call a service without using the generated client, but just String names.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#generic_call"}  theme={null}
const response = await ctx.genericCall({
  service: "MyObject",
  method: "myHandler",
  parameter: "Hi",
  key: "Mary", // drop this for Service calls
  inputSerde: restate.serde.json,
  outputSerde: restate.serde.json,
});
```

### Run Actions or Side Effects (Non-Deterministic Operations)

❌ Never call external APIs/DBs directly - will re-execute during replay, causing duplicates.
✅ Wrap in `ctx.run()` - Restate journals the result; runs only once.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#durable_steps"}  theme={null}
const result = await ctx.run("my-side-effect", async () => {
  return await callExternalAPI();
});
```

### Deterministic randoms and time

❌ Never use `Math.random()` - non-deterministic and breaks replay logic.
✅ Use `ctx.rand.random()` or `ctx.rand.uuidv4()` - Restate journals the result for deterministic replay.

❌ Never use Date.now(), new Date() - returns different values during replay.
✅ Use `await ctx.date.now();` - Restate records and replays the same timestamp.

### Durable Timers and Sleep

❌ Never use setTimeout() or sleep from other libraries - not durable, lost on restarts.
✅ Use ctx.sleep() - durable timer that survives failures.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#durable_timers"}  theme={null}
// Sleep
await ctx.sleep({ seconds: 30 });

// Schedule delayed call (different from sleep + send)
ctx.serviceSendClient(myService).myHandler(
    "Hi",
    restate.rpc.sendOpts({ delay: { hours: 5 } })
);
```

### Awakeables (External Events)

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#awakeables"}  theme={null}
// Create awakeable
const {id, promise} = ctx.awakeable<string>();

// Send ID to external system
await ctx.run(() => requestHumanReview(name, id));

// Wait for result
const review = await promise;

// Resolve from another handler
ctx.resolveAwakeable(id, "Looks good!");

// Reject from another handler
ctx.rejectAwakeable(id, "Cannot be reviewed");
```

### Durable Promises (Workflows only)

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#workflow_promises"}  theme={null}
// Wait for promise
const review = await ctx.promise<string>("review");

// Resolve promise
await ctx.promise<string>("review").resolve(review);
```

## Concurrency

Always use Restate combinators (`RestatePromise.all`, `RestatePromise.race`, `RestatePromise.any`, `RestatePromise.allSettled`) instead of JavaScript's native `Promise` methods - they journal execution order for deterministic replay.

### `RestatePromise.all()` - Wait for All

Returns when all futures complete. Use to wait for multiple operations to finish.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_all"}  theme={null}
// ❌ BAD
const results1 = await Promise.all([call1, call2]);

// ✅ GOOD
const claude = ctx.serviceClient(claudeAgent).ask("What is the weather?");
const openai = ctx.serviceClient(openAiAgent).ask("What is the weather?");
const results2 = await RestatePromise.all([claude, openai]);
```

### `RestatePromise.race()` - Race Multiple Operations

Returns immediately when the first future completes. Use for timeouts and racing operations.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_race"}  theme={null}
// ❌ BAD
const result1 = await Promise.race([call1, call2]);

// ✅ GOOD
const firstToComplete = await RestatePromise.race([
  ctx.sleep({ milliseconds: 100 }),
  ctx.serviceClient(myService).myHandler("Hi"),
]);
```

### RestatePromise.any() - First Successful Result

Returns the first successful result, ignoring rejections until all fail.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_any"}  theme={null}
// ❌ BAD - using Promise.any (not journaled)
const result1 = await Promise.any([call1, call2]);

// ✅ GOOD
const result2 = await RestatePromise.any([
  ctx.run(() => callLLM("gpt-4", prompt)),
  ctx.run(() => callLLM("claude", prompt))
]);
```

### `RestatePromise.allSettled()` - Wait for All (Success or Failure)

Returns results of all promises, whether they succeeded or failed.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_allsettled"}  theme={null}
// ❌ BAD
const results1 = await Promise.allSettled([call1, call2]);

// ✅ GOOD
const results2 = await RestatePromise.allSettled([
  ctx.serviceClient(service1).call(),
  ctx.serviceClient(service2).call()
]);

results2.forEach((result, i) => {
  if (result.status === "fulfilled") {
    console.log(`Call ${i} succeeded:`, result.value);
  } else {
    console.log(`Call ${i} failed:`, result.reason);
  }
});
```

### Invocation Management

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#cancel"}  theme={null}
const handle = ctx.serviceSendClient(myService).myHandler(
    "Hi",
    restate.rpc.sendOpts({ idempotencyKey: "my-key" })
);
const invocationId = await handle.invocationId;
const response = await ctx.attach(invocationId);

// Cancel invocation
ctx.cancel(invocationId);
```

## Serialization

### Default (JSON)

By default, TypeScript SDK uses built-in JSON support.

### Zod Schemas

For type safety and validation with Zod, install: `npm install @restatedev/restate-sdk-zod`

```typescript {"CODE_LOAD::ts/src/develop/serialization.ts#zod"}  theme={null}
import * as restate from "@restatedev/restate-sdk";
import { z } from "zod";
import { serde } from "@restatedev/restate-sdk-zod";

const Greeting = z.object({
  name: z.string(),
});

const GreetingResponse = z.object({
  result: z.string(),
});

const greeter = restate.service({
  name: "Greeter",
  handlers: {
    greet: restate.handlers.handler(
      { input: serde.zod(Greeting), output: serde.zod(GreetingResponse) },
      async (ctx: restate.Context, { name }) => {
        return { result: `You said hi to ${name}!` };
      }
    ),
  },
});
```

### Custom Serialization

```typescript {"CODE_LOAD::ts/src/develop/serialization.ts#service_definition"}  theme={null}
const myService = restate.service({
  name: "MyService",
  handlers: {
    myHandler: restate.handlers.handler(
      {
        // Set the input serde here
        input: restate.serde.binary,
        // Set the output serde here
        output: restate.serde.binary,
      },
      async (ctx: Context, data: Uint8Array): Promise<Uint8Array> => {
        // Process the request
        return data;
      }
    ),
  },
});
```

## Error Handling

Restate retries failures indefinitely by default. For permanent business-logic failures (invalid input, declined payment), use TerminalError to stop retries immediately.

### Terminal Errors (No Retry)

```typescript {"CODE_LOAD::ts/src/develop/error_handling.ts#terminal"}  theme={null}
throw new TerminalError("Something went wrong.", { errorCode: 500 });
```

### Retryable Errors

```typescript  theme={null}
// Any other thrown error will be retried
throw new Error("Temporary failure - will retry");
```

## Testing

```typescript {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-testing.test.ts"}  theme={null}
import { RestateTestEnvironment } from "@restatedev/restate-sdk-testcontainers";
import * as clients from "@restatedev/restate-sdk-clients";
import { describe, it, beforeAll, afterAll, expect } from "vitest";
import {greeter} from "./greeter-service";

describe("MyService", () => {
    let restateTestEnvironment: RestateTestEnvironment;
    let restateIngress: clients.Ingress;

    beforeAll(async () => {
        restateTestEnvironment = await RestateTestEnvironment.start({services: [greeter]});
        restateIngress = clients.connect({ url: restateTestEnvironment.baseUrl() });
    }, 20_000);

    afterAll(async () => {
        await restateTestEnvironment?.stop();
    });

    it("Can call methods", async () => {
        const client = restateIngress.objectClient(greeter, "myKey");
        await client.greet("Test!");
    });

    it("Can read/write state", async () => {
        const state = restateTestEnvironment.stateOf(greeter, "myKey");
        await state.set("count", 123);
        expect(await state.get("count")).toBe(123);
    });
});
```

## SDK Clients (External Invocations)

```typescript {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-clients.ts#here"}  theme={null}
const restateClient = clients.connect({url: "http://localhost:8080"});

// Request-response
const result = await restateClient
    .serviceClient<MyService>({name: "MyService"})
    .myHandler("Hi");

// One-way
await restateClient
    .serviceSendClient<MyService>({name: "MyService"})
    .myHandler("Hi");

// Delayed
await restateClient
    .serviceSendClient<MyService>({name: "MyService"})
    .myHandler("Hi", clients.rpc.sendOpts({delay: {seconds: 1}}));
```

---


## File: docs/agents/durable/restate/ai-examples/vercel-ai/template_nextjs/.cursor/rules/AGENTS.md

# Restate TypeScript SDK Rules

## Core Concepts

* Restate provides durable execution: code automatically stores completed steps and resumes from where it left off on failures
* All handlers receive a `Context`/`ObjectContext`/`WorkflowContext`/`ObjectSharedContext`/`WorkflowSharedContext` object as the first argument
* Handlers can take one optional JSON-serializable input and must return a JSON-serializable output. Or specify the serializers.

## Service Types

### Basic Services

```ts {"CODE_LOAD::ts/src/develop/service.ts"}  theme={null}
import * as restate from "@restatedev/restate-sdk";

export const myService = restate.service({
  name: "MyService",
  handlers: {
    myHandler: async (ctx: restate.Context, greeting: string) => {
      return `${greeting}!`;
    },
  },
});

restate.serve({ services: [myService] });
```

### Virtual Objects (Stateful, Key-Addressable)

```ts {"CODE_LOAD::ts/src/develop/virtual_object.ts"}  theme={null}
import * as restate from "@restatedev/restate-sdk";

export const myObject = restate.object({
  name: "MyObject",
  handlers: {
    myHandler: async (ctx: restate.ObjectContext, greeting: string) => {
      return `${greeting} ${ctx.key}!`;
    },
    myConcurrentHandler: restate.handlers.object.shared(
      async (ctx: restate.ObjectSharedContext, greeting: string) => {
        return `${greeting} ${ctx.key}!`;
      }
    ),
  },
});

restate.serve({ services: [myObject] });
```

### Workflows

```ts {"CODE_LOAD::ts/src/develop/workflow.ts"}  theme={null}
import * as restate from "@restatedev/restate-sdk";

export const myWorkflow = restate.workflow({
  name: "MyWorkflow",
  handlers: {
    run: async (ctx: restate.WorkflowContext, req: string) => {
      // implement workflow logic here

      return "success";
    },

    interactWithWorkflow: async (ctx: restate.WorkflowSharedContext) => {
      // implement interaction logic here
      // e.g. resolve a promise that the workflow is waiting on
    },
  },
});

restate.serve({ services: [myWorkflow] });
```

## Context Operations

### State Management (Virtual Objects & Workflows only)

❌ Never use global variables - not durable, lost across replicas.
✅ Use `ctx.get()` and `ctx.set()` - durable and scoped to the object's key.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#state"}  theme={null}
// Get state
const count = (await ctx.get<number>("count")) ?? 0;

// Set state
ctx.set("count", count + 1);

// Clear state
ctx.clear("count");
ctx.clearAll();

// Get all state keys
const keys = await ctx.stateKeys();
```

### Service Communication

#### Request-Response

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#service_calls"}  theme={null}
// Call a Service
const response = await ctx.serviceClient(myService).myHandler("Hi");

// Call a Virtual Object
const response2 = await ctx.objectClient(myObject, "key").myHandler("Hi");

// Call a Workflow
const response3 = await ctx.workflowClient(myWorkflow, "wf-id").run("Hi");
```

#### One-Way Messages

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#sending_messages"}  theme={null}
ctx.serviceSendClient(myService).myHandler("Hi");
ctx.objectSendClient(myObject, "key").myHandler("Hi");
ctx.workflowSendClient(myWorkflow, "wf-id").run("Hi");
```

#### Delayed Messages

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#delayed_messages"}  theme={null}
ctx.serviceSendClient(myService).myHandler(
    "Hi",
    restate.rpc.sendOpts({ delay: { hours: 5 } })
);
```

#### Generic Calls

Call a service without using the generated client, but just String names.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#generic_call"}  theme={null}
const response = await ctx.genericCall({
  service: "MyObject",
  method: "myHandler",
  parameter: "Hi",
  key: "Mary", // drop this for Service calls
  inputSerde: restate.serde.json,
  outputSerde: restate.serde.json,
});
```

### Run Actions or Side Effects (Non-Deterministic Operations)

❌ Never call external APIs/DBs directly - will re-execute during replay, causing duplicates.
✅ Wrap in `ctx.run()` - Restate journals the result; runs only once.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#durable_steps"}  theme={null}
const result = await ctx.run("my-side-effect", async () => {
  return await callExternalAPI();
});
```

### Deterministic randoms and time

❌ Never use `Math.random()` - non-deterministic and breaks replay logic.
✅ Use `ctx.rand.random()` or `ctx.rand.uuidv4()` - Restate journals the result for deterministic replay.

❌ Never use Date.now(), new Date() - returns different values during replay.
✅ Use `await ctx.date.now();` - Restate records and replays the same timestamp.

### Durable Timers and Sleep

❌ Never use setTimeout() or sleep from other libraries - not durable, lost on restarts.
✅ Use ctx.sleep() - durable timer that survives failures.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#durable_timers"}  theme={null}
// Sleep
await ctx.sleep({ seconds: 30 });

// Schedule delayed call (different from sleep + send)
ctx.serviceSendClient(myService).myHandler(
    "Hi",
    restate.rpc.sendOpts({ delay: { hours: 5 } })
);
```

### Awakeables (External Events)

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#awakeables"}  theme={null}
// Create awakeable
const {id, promise} = ctx.awakeable<string>();

// Send ID to external system
await ctx.run(() => requestHumanReview(name, id));

// Wait for result
const review = await promise;

// Resolve from another handler
ctx.resolveAwakeable(id, "Looks good!");

// Reject from another handler
ctx.rejectAwakeable(id, "Cannot be reviewed");
```

### Durable Promises (Workflows only)

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#workflow_promises"}  theme={null}
// Wait for promise
const review = await ctx.promise<string>("review");

// Resolve promise
await ctx.promise<string>("review").resolve(review);
```

## Concurrency

Always use Restate combinators (`RestatePromise.all`, `RestatePromise.race`, `RestatePromise.any`, `RestatePromise.allSettled`) instead of JavaScript's native `Promise` methods - they journal execution order for deterministic replay.

### `RestatePromise.all()` - Wait for All

Returns when all futures complete. Use to wait for multiple operations to finish.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_all"}  theme={null}
// ❌ BAD
const results1 = await Promise.all([call1, call2]);

// ✅ GOOD
const claude = ctx.serviceClient(claudeAgent).ask("What is the weather?");
const openai = ctx.serviceClient(openAiAgent).ask("What is the weather?");
const results2 = await RestatePromise.all([claude, openai]);
```

### `RestatePromise.race()` - Race Multiple Operations

Returns immediately when the first future completes. Use for timeouts and racing operations.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_race"}  theme={null}
// ❌ BAD
const result1 = await Promise.race([call1, call2]);

// ✅ GOOD
const firstToComplete = await RestatePromise.race([
  ctx.sleep({ milliseconds: 100 }),
  ctx.serviceClient(myService).myHandler("Hi"),
]);
```

### RestatePromise.any() - First Successful Result

Returns the first successful result, ignoring rejections until all fail.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_any"}  theme={null}
// ❌ BAD - using Promise.any (not journaled)
const result1 = await Promise.any([call1, call2]);

// ✅ GOOD
const result2 = await RestatePromise.any([
  ctx.run(() => callLLM("gpt-4", prompt)),
  ctx.run(() => callLLM("claude", prompt))
]);
```

### `RestatePromise.allSettled()` - Wait for All (Success or Failure)

Returns results of all promises, whether they succeeded or failed.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_allsettled"}  theme={null}
// ❌ BAD
const results1 = await Promise.allSettled([call1, call2]);

// ✅ GOOD
const results2 = await RestatePromise.allSettled([
  ctx.serviceClient(service1).call(),
  ctx.serviceClient(service2).call()
]);

results2.forEach((result, i) => {
  if (result.status === "fulfilled") {
    console.log(`Call ${i} succeeded:`, result.value);
  } else {
    console.log(`Call ${i} failed:`, result.reason);
  }
});
```

### Invocation Management

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#cancel"}  theme={null}
const handle = ctx.serviceSendClient(myService).myHandler(
    "Hi",
    restate.rpc.sendOpts({ idempotencyKey: "my-key" })
);
const invocationId = await handle.invocationId;
const response = await ctx.attach(invocationId);

// Cancel invocation
ctx.cancel(invocationId);
```

## Serialization

### Default (JSON)

By default, TypeScript SDK uses built-in JSON support.

### Zod Schemas

For type safety and validation with Zod, install: `npm install @restatedev/restate-sdk-zod`

```typescript {"CODE_LOAD::ts/src/develop/serialization.ts#zod"}  theme={null}
import * as restate from "@restatedev/restate-sdk";
import { z } from "zod";
import { serde } from "@restatedev/restate-sdk-zod";

const Greeting = z.object({
  name: z.string(),
});

const GreetingResponse = z.object({
  result: z.string(),
});

const greeter = restate.service({
  name: "Greeter",
  handlers: {
    greet: restate.handlers.handler(
      { input: serde.zod(Greeting), output: serde.zod(GreetingResponse) },
      async (ctx: restate.Context, { name }) => {
        return { result: `You said hi to ${name}!` };
      }
    ),
  },
});
```

### Custom Serialization

```typescript {"CODE_LOAD::ts/src/develop/serialization.ts#service_definition"}  theme={null}
const myService = restate.service({
  name: "MyService",
  handlers: {
    myHandler: restate.handlers.handler(
      {
        // Set the input serde here
        input: restate.serde.binary,
        // Set the output serde here
        output: restate.serde.binary,
      },
      async (ctx: Context, data: Uint8Array): Promise<Uint8Array> => {
        // Process the request
        return data;
      }
    ),
  },
});
```

## Error Handling

Restate retries failures indefinitely by default. For permanent business-logic failures (invalid input, declined payment), use TerminalError to stop retries immediately.

### Terminal Errors (No Retry)

```typescript {"CODE_LOAD::ts/src/develop/error_handling.ts#terminal"}  theme={null}
throw new TerminalError("Something went wrong.", { errorCode: 500 });
```

### Retryable Errors

```typescript  theme={null}
// Any other thrown error will be retried
throw new Error("Temporary failure - will retry");
```

## Testing

```typescript {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-testing.test.ts"}  theme={null}
import { RestateTestEnvironment } from "@restatedev/restate-sdk-testcontainers";
import * as clients from "@restatedev/restate-sdk-clients";
import { describe, it, beforeAll, afterAll, expect } from "vitest";
import {greeter} from "./greeter-service";

describe("MyService", () => {
    let restateTestEnvironment: RestateTestEnvironment;
    let restateIngress: clients.Ingress;

    beforeAll(async () => {
        restateTestEnvironment = await RestateTestEnvironment.start({services: [greeter]});
        restateIngress = clients.connect({ url: restateTestEnvironment.baseUrl() });
    }, 20_000);

    afterAll(async () => {
        await restateTestEnvironment?.stop();
    });

    it("Can call methods", async () => {
        const client = restateIngress.objectClient(greeter, "myKey");
        await client.greet("Test!");
    });

    it("Can read/write state", async () => {
        const state = restateTestEnvironment.stateOf(greeter, "myKey");
        await state.set("count", 123);
        expect(await state.get("count")).toBe(123);
    });
});
```

## SDK Clients (External Invocations)

```typescript {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-clients.ts#here"}  theme={null}
const restateClient = clients.connect({url: "http://localhost:8080"});

// Request-response
const result = await restateClient
    .serviceClient<MyService>({name: "MyService"})
    .myHandler("Hi");

// One-way
await restateClient
    .serviceSendClient<MyService>({name: "MyService"})
    .myHandler("Hi");

// Delayed
await restateClient
    .serviceSendClient<MyService>({name: "MyService"})
    .myHandler("Hi", clients.rpc.sendOpts({delay: {seconds: 1}}));
```

---


## File: docs/agents/durable/restate/ai-examples/vercel-ai/template_nextjs/README.md

# Restate + Vercel AI Example (for NextJS)

This is template of a simple agent, written with the Vercel AI SDK and using Restate for resilience and observability.
It set up as a NextJS app.

Use this template when deploying the agent as a NextJS app, for example on Vercel. For deployments on other stacks, use the standard template, which serves the agent services via HTTP/2 (fastest option) or runs on FaaS like AWS Lambda natively.  

## Running the template example

1. Install all dependencies
    ```shell
    npm install
    ```
2. Export your OpenAI key as an environment variable. If you want to use another model (e.g., Anthrophic Claude, Google Gemini) you need to change the dependencies in `package.json` and the model in `restate/services/agent.ts` accordingly:
    ```shell
    export OPENAI_API_KEY=your_openai_api_key
    ```
3. Start the nextjs app, which contains the agent code.
    ```shell
    npm run dev
    ```

4. [Start the Restate Server](https://docs.restate.dev/develop/local_dev) in a separate shell. The server is the durable orchstrator. It is queue, workflow engine, k/V store in one.
    ```shell
    npx @restatedev/restate-server@latest
    ```

5. Register the services, to let Restate Server know about the agent. The Server can now proxy invocations to the agent, adding durable execution that way. You can do this via the UI (by default at `http://localhost:9070`)
    ```shell
    npx @restatedev/restate deployments register -y --use-http1.1 http://localhost:3000/restate/v1
    ```

6. All should be ready. Now send a request to your agent. You can do that through the UI, or via HTTP. _(note that we target Restate Server's endpoint (8080) because the server proxies requests to the service, to make them durable.)_

    ```shell
    curl localhost:8080/agent/run --json '"What is the weather in Detroit?"'
    ```

   Returns: `The weather in Detroit is currently 22°C and sunny.`

Check the Restate UI (`localhost:9070`) to see the journals of your invocations.
---


## File: docs/agents/durable/restate/ai-examples/vercel-ai/template/.claude/CLAUDE.md

# Restate TypeScript SDK Rules

## Core Concepts

* Restate provides durable execution: code automatically stores completed steps and resumes from where it left off on failures
* All handlers receive a `Context`/`ObjectContext`/`WorkflowContext`/`ObjectSharedContext`/`WorkflowSharedContext` object as the first argument
* Handlers can take one optional JSON-serializable input and must return a JSON-serializable output. Or specify the serializers.

## Service Types

### Basic Services

```ts {"CODE_LOAD::ts/src/develop/service.ts"}  theme={null}
import * as restate from "@restatedev/restate-sdk";

export const myService = restate.service({
  name: "MyService",
  handlers: {
    myHandler: async (ctx: restate.Context, greeting: string) => {
      return `${greeting}!`;
    },
  },
});

restate.serve({ services: [myService] });
```

### Virtual Objects (Stateful, Key-Addressable)

```ts {"CODE_LOAD::ts/src/develop/virtual_object.ts"}  theme={null}
import * as restate from "@restatedev/restate-sdk";

export const myObject = restate.object({
  name: "MyObject",
  handlers: {
    myHandler: async (ctx: restate.ObjectContext, greeting: string) => {
      return `${greeting} ${ctx.key}!`;
    },
    myConcurrentHandler: restate.handlers.object.shared(
      async (ctx: restate.ObjectSharedContext, greeting: string) => {
        return `${greeting} ${ctx.key}!`;
      }
    ),
  },
});

restate.serve({ services: [myObject] });
```

### Workflows

```ts {"CODE_LOAD::ts/src/develop/workflow.ts"}  theme={null}
import * as restate from "@restatedev/restate-sdk";

export const myWorkflow = restate.workflow({
  name: "MyWorkflow",
  handlers: {
    run: async (ctx: restate.WorkflowContext, req: string) => {
      // implement workflow logic here

      return "success";
    },

    interactWithWorkflow: async (ctx: restate.WorkflowSharedContext) => {
      // implement interaction logic here
      // e.g. resolve a promise that the workflow is waiting on
    },
  },
});

restate.serve({ services: [myWorkflow] });
```

## Context Operations

### State Management (Virtual Objects & Workflows only)

❌ Never use global variables - not durable, lost across replicas.
✅ Use `ctx.get()` and `ctx.set()` - durable and scoped to the object's key.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#state"}  theme={null}
// Get state
const count = (await ctx.get<number>("count")) ?? 0;

// Set state
ctx.set("count", count + 1);

// Clear state
ctx.clear("count");
ctx.clearAll();

// Get all state keys
const keys = await ctx.stateKeys();
```

### Service Communication

#### Request-Response

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#service_calls"}  theme={null}
// Call a Service
const response = await ctx.serviceClient(myService).myHandler("Hi");

// Call a Virtual Object
const response2 = await ctx.objectClient(myObject, "key").myHandler("Hi");

// Call a Workflow
const response3 = await ctx.workflowClient(myWorkflow, "wf-id").run("Hi");
```

#### One-Way Messages

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#sending_messages"}  theme={null}
ctx.serviceSendClient(myService).myHandler("Hi");
ctx.objectSendClient(myObject, "key").myHandler("Hi");
ctx.workflowSendClient(myWorkflow, "wf-id").run("Hi");
```

#### Delayed Messages

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#delayed_messages"}  theme={null}
ctx.serviceSendClient(myService).myHandler(
    "Hi",
    restate.rpc.sendOpts({ delay: { hours: 5 } })
);
```

#### Generic Calls

Call a service without using the generated client, but just String names.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#generic_call"}  theme={null}
const response = await ctx.genericCall({
  service: "MyObject",
  method: "myHandler",
  parameter: "Hi",
  key: "Mary", // drop this for Service calls
  inputSerde: restate.serde.json,
  outputSerde: restate.serde.json,
});
```

### Run Actions or Side Effects (Non-Deterministic Operations)

❌ Never call external APIs/DBs directly - will re-execute during replay, causing duplicates.
✅ Wrap in `ctx.run()` - Restate journals the result; runs only once.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#durable_steps"}  theme={null}
const result = await ctx.run("my-side-effect", async () => {
  return await callExternalAPI();
});
```

### Deterministic randoms and time

❌ Never use `Math.random()` - non-deterministic and breaks replay logic.
✅ Use `ctx.rand.random()` or `ctx.rand.uuidv4()` - Restate journals the result for deterministic replay.

❌ Never use Date.now(), new Date() - returns different values during replay.
✅ Use `await ctx.date.now();` - Restate records and replays the same timestamp.

### Durable Timers and Sleep

❌ Never use setTimeout() or sleep from other libraries - not durable, lost on restarts.
✅ Use ctx.sleep() - durable timer that survives failures.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#durable_timers"}  theme={null}
// Sleep
await ctx.sleep({ seconds: 30 });

// Schedule delayed call (different from sleep + send)
ctx.serviceSendClient(myService).myHandler(
    "Hi",
    restate.rpc.sendOpts({ delay: { hours: 5 } })
);
```

### Awakeables (External Events)

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#awakeables"}  theme={null}
// Create awakeable
const {id, promise} = ctx.awakeable<string>();

// Send ID to external system
await ctx.run(() => requestHumanReview(name, id));

// Wait for result
const review = await promise;

// Resolve from another handler
ctx.resolveAwakeable(id, "Looks good!");

// Reject from another handler
ctx.rejectAwakeable(id, "Cannot be reviewed");
```

### Durable Promises (Workflows only)

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#workflow_promises"}  theme={null}
// Wait for promise
const review = await ctx.promise<string>("review");

// Resolve promise
await ctx.promise<string>("review").resolve(review);
```

## Concurrency

Always use Restate combinators (`RestatePromise.all`, `RestatePromise.race`, `RestatePromise.any`, `RestatePromise.allSettled`) instead of JavaScript's native `Promise` methods - they journal execution order for deterministic replay.

### `RestatePromise.all()` - Wait for All

Returns when all futures complete. Use to wait for multiple operations to finish.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_all"}  theme={null}
// ❌ BAD
const results1 = await Promise.all([call1, call2]);

// ✅ GOOD
const claude = ctx.serviceClient(claudeAgent).ask("What is the weather?");
const openai = ctx.serviceClient(openAiAgent).ask("What is the weather?");
const results2 = await RestatePromise.all([claude, openai]);
```

### `RestatePromise.race()` - Race Multiple Operations

Returns immediately when the first future completes. Use for timeouts and racing operations.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_race"}  theme={null}
// ❌ BAD
const result1 = await Promise.race([call1, call2]);

// ✅ GOOD
const firstToComplete = await RestatePromise.race([
  ctx.sleep({ milliseconds: 100 }),
  ctx.serviceClient(myService).myHandler("Hi"),
]);
```

### RestatePromise.any() - First Successful Result

Returns the first successful result, ignoring rejections until all fail.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_any"}  theme={null}
// ❌ BAD - using Promise.any (not journaled)
const result1 = await Promise.any([call1, call2]);

// ✅ GOOD
const result2 = await RestatePromise.any([
  ctx.run(() => callLLM("gpt-4", prompt)),
  ctx.run(() => callLLM("claude", prompt))
]);
```

### `RestatePromise.allSettled()` - Wait for All (Success or Failure)

Returns results of all promises, whether they succeeded or failed.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_allsettled"}  theme={null}
// ❌ BAD
const results1 = await Promise.allSettled([call1, call2]);

// ✅ GOOD
const results2 = await RestatePromise.allSettled([
  ctx.serviceClient(service1).call(),
  ctx.serviceClient(service2).call()
]);

results2.forEach((result, i) => {
  if (result.status === "fulfilled") {
    console.log(`Call ${i} succeeded:`, result.value);
  } else {
    console.log(`Call ${i} failed:`, result.reason);
  }
});
```

### Invocation Management

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#cancel"}  theme={null}
const handle = ctx.serviceSendClient(myService).myHandler(
    "Hi",
    restate.rpc.sendOpts({ idempotencyKey: "my-key" })
);
const invocationId = await handle.invocationId;
const response = await ctx.attach(invocationId);

// Cancel invocation
ctx.cancel(invocationId);
```

## Serialization

### Default (JSON)

By default, TypeScript SDK uses built-in JSON support.

### Zod Schemas

For type safety and validation with Zod, install: `npm install @restatedev/restate-sdk-zod`

```typescript {"CODE_LOAD::ts/src/develop/serialization.ts#zod"}  theme={null}
import * as restate from "@restatedev/restate-sdk";
import { z } from "zod";
import { serde } from "@restatedev/restate-sdk-zod";

const Greeting = z.object({
  name: z.string(),
});

const GreetingResponse = z.object({
  result: z.string(),
});

const greeter = restate.service({
  name: "Greeter",
  handlers: {
    greet: restate.handlers.handler(
      { input: serde.zod(Greeting), output: serde.zod(GreetingResponse) },
      async (ctx: restate.Context, { name }) => {
        return { result: `You said hi to ${name}!` };
      }
    ),
  },
});
```

### Custom Serialization

```typescript {"CODE_LOAD::ts/src/develop/serialization.ts#service_definition"}  theme={null}
const myService = restate.service({
  name: "MyService",
  handlers: {
    myHandler: restate.handlers.handler(
      {
        // Set the input serde here
        input: restate.serde.binary,
        // Set the output serde here
        output: restate.serde.binary,
      },
      async (ctx: Context, data: Uint8Array): Promise<Uint8Array> => {
        // Process the request
        return data;
      }
    ),
  },
});
```

## Error Handling

Restate retries failures indefinitely by default. For permanent business-logic failures (invalid input, declined payment), use TerminalError to stop retries immediately.

### Terminal Errors (No Retry)

```typescript {"CODE_LOAD::ts/src/develop/error_handling.ts#terminal"}  theme={null}
throw new TerminalError("Something went wrong.", { errorCode: 500 });
```

### Retryable Errors

```typescript  theme={null}
// Any other thrown error will be retried
throw new Error("Temporary failure - will retry");
```

## Testing

```typescript {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-testing.test.ts"}  theme={null}
import { RestateTestEnvironment } from "@restatedev/restate-sdk-testcontainers";
import * as clients from "@restatedev/restate-sdk-clients";
import { describe, it, beforeAll, afterAll, expect } from "vitest";
import {greeter} from "./greeter-service";

describe("MyService", () => {
    let restateTestEnvironment: RestateTestEnvironment;
    let restateIngress: clients.Ingress;

    beforeAll(async () => {
        restateTestEnvironment = await RestateTestEnvironment.start({services: [greeter]});
        restateIngress = clients.connect({ url: restateTestEnvironment.baseUrl() });
    }, 20_000);

    afterAll(async () => {
        await restateTestEnvironment?.stop();
    });

    it("Can call methods", async () => {
        const client = restateIngress.objectClient(greeter, "myKey");
        await client.greet("Test!");
    });

    it("Can read/write state", async () => {
        const state = restateTestEnvironment.stateOf(greeter, "myKey");
        await state.set("count", 123);
        expect(await state.get("count")).toBe(123);
    });
});
```

## SDK Clients (External Invocations)

```typescript {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-clients.ts#here"}  theme={null}
const restateClient = clients.connect({url: "http://localhost:8080"});

// Request-response
const result = await restateClient
    .serviceClient<MyService>({name: "MyService"})
    .myHandler("Hi");

// One-way
await restateClient
    .serviceSendClient<MyService>({name: "MyService"})
    .myHandler("Hi");

// Delayed
await restateClient
    .serviceSendClient<MyService>({name: "MyService"})
    .myHandler("Hi", clients.rpc.sendOpts({delay: {seconds: 1}}));
```

---


## File: docs/agents/durable/restate/ai-examples/vercel-ai/template/.cursor/rules/AGENTS.md

# Restate TypeScript SDK Rules

## Core Concepts

* Restate provides durable execution: code automatically stores completed steps and resumes from where it left off on failures
* All handlers receive a `Context`/`ObjectContext`/`WorkflowContext`/`ObjectSharedContext`/`WorkflowSharedContext` object as the first argument
* Handlers can take one optional JSON-serializable input and must return a JSON-serializable output. Or specify the serializers.

## Service Types

### Basic Services

```ts {"CODE_LOAD::ts/src/develop/service.ts"}  theme={null}
import * as restate from "@restatedev/restate-sdk";

export const myService = restate.service({
  name: "MyService",
  handlers: {
    myHandler: async (ctx: restate.Context, greeting: string) => {
      return `${greeting}!`;
    },
  },
});

restate.serve({ services: [myService] });
```

### Virtual Objects (Stateful, Key-Addressable)

```ts {"CODE_LOAD::ts/src/develop/virtual_object.ts"}  theme={null}
import * as restate from "@restatedev/restate-sdk";

export const myObject = restate.object({
  name: "MyObject",
  handlers: {
    myHandler: async (ctx: restate.ObjectContext, greeting: string) => {
      return `${greeting} ${ctx.key}!`;
    },
    myConcurrentHandler: restate.handlers.object.shared(
      async (ctx: restate.ObjectSharedContext, greeting: string) => {
        return `${greeting} ${ctx.key}!`;
      }
    ),
  },
});

restate.serve({ services: [myObject] });
```

### Workflows

```ts {"CODE_LOAD::ts/src/develop/workflow.ts"}  theme={null}
import * as restate from "@restatedev/restate-sdk";

export const myWorkflow = restate.workflow({
  name: "MyWorkflow",
  handlers: {
    run: async (ctx: restate.WorkflowContext, req: string) => {
      // implement workflow logic here

      return "success";
    },

    interactWithWorkflow: async (ctx: restate.WorkflowSharedContext) => {
      // implement interaction logic here
      // e.g. resolve a promise that the workflow is waiting on
    },
  },
});

restate.serve({ services: [myWorkflow] });
```

## Context Operations

### State Management (Virtual Objects & Workflows only)

❌ Never use global variables - not durable, lost across replicas.
✅ Use `ctx.get()` and `ctx.set()` - durable and scoped to the object's key.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#state"}  theme={null}
// Get state
const count = (await ctx.get<number>("count")) ?? 0;

// Set state
ctx.set("count", count + 1);

// Clear state
ctx.clear("count");
ctx.clearAll();

// Get all state keys
const keys = await ctx.stateKeys();
```

### Service Communication

#### Request-Response

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#service_calls"}  theme={null}
// Call a Service
const response = await ctx.serviceClient(myService).myHandler("Hi");

// Call a Virtual Object
const response2 = await ctx.objectClient(myObject, "key").myHandler("Hi");

// Call a Workflow
const response3 = await ctx.workflowClient(myWorkflow, "wf-id").run("Hi");
```

#### One-Way Messages

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#sending_messages"}  theme={null}
ctx.serviceSendClient(myService).myHandler("Hi");
ctx.objectSendClient(myObject, "key").myHandler("Hi");
ctx.workflowSendClient(myWorkflow, "wf-id").run("Hi");
```

#### Delayed Messages

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#delayed_messages"}  theme={null}
ctx.serviceSendClient(myService).myHandler(
    "Hi",
    restate.rpc.sendOpts({ delay: { hours: 5 } })
);
```

#### Generic Calls

Call a service without using the generated client, but just String names.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#generic_call"}  theme={null}
const response = await ctx.genericCall({
  service: "MyObject",
  method: "myHandler",
  parameter: "Hi",
  key: "Mary", // drop this for Service calls
  inputSerde: restate.serde.json,
  outputSerde: restate.serde.json,
});
```

### Run Actions or Side Effects (Non-Deterministic Operations)

❌ Never call external APIs/DBs directly - will re-execute during replay, causing duplicates.
✅ Wrap in `ctx.run()` - Restate journals the result; runs only once.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#durable_steps"}  theme={null}
const result = await ctx.run("my-side-effect", async () => {
  return await callExternalAPI();
});
```

### Deterministic randoms and time

❌ Never use `Math.random()` - non-deterministic and breaks replay logic.
✅ Use `ctx.rand.random()` or `ctx.rand.uuidv4()` - Restate journals the result for deterministic replay.

❌ Never use Date.now(), new Date() - returns different values during replay.
✅ Use `await ctx.date.now();` - Restate records and replays the same timestamp.

### Durable Timers and Sleep

❌ Never use setTimeout() or sleep from other libraries - not durable, lost on restarts.
✅ Use ctx.sleep() - durable timer that survives failures.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#durable_timers"}  theme={null}
// Sleep
await ctx.sleep({ seconds: 30 });

// Schedule delayed call (different from sleep + send)
ctx.serviceSendClient(myService).myHandler(
    "Hi",
    restate.rpc.sendOpts({ delay: { hours: 5 } })
);
```

### Awakeables (External Events)

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#awakeables"}  theme={null}
// Create awakeable
const {id, promise} = ctx.awakeable<string>();

// Send ID to external system
await ctx.run(() => requestHumanReview(name, id));

// Wait for result
const review = await promise;

// Resolve from another handler
ctx.resolveAwakeable(id, "Looks good!");

// Reject from another handler
ctx.rejectAwakeable(id, "Cannot be reviewed");
```

### Durable Promises (Workflows only)

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#workflow_promises"}  theme={null}
// Wait for promise
const review = await ctx.promise<string>("review");

// Resolve promise
await ctx.promise<string>("review").resolve(review);
```

## Concurrency

Always use Restate combinators (`RestatePromise.all`, `RestatePromise.race`, `RestatePromise.any`, `RestatePromise.allSettled`) instead of JavaScript's native `Promise` methods - they journal execution order for deterministic replay.

### `RestatePromise.all()` - Wait for All

Returns when all futures complete. Use to wait for multiple operations to finish.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_all"}  theme={null}
// ❌ BAD
const results1 = await Promise.all([call1, call2]);

// ✅ GOOD
const claude = ctx.serviceClient(claudeAgent).ask("What is the weather?");
const openai = ctx.serviceClient(openAiAgent).ask("What is the weather?");
const results2 = await RestatePromise.all([claude, openai]);
```

### `RestatePromise.race()` - Race Multiple Operations

Returns immediately when the first future completes. Use for timeouts and racing operations.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_race"}  theme={null}
// ❌ BAD
const result1 = await Promise.race([call1, call2]);

// ✅ GOOD
const firstToComplete = await RestatePromise.race([
  ctx.sleep({ milliseconds: 100 }),
  ctx.serviceClient(myService).myHandler("Hi"),
]);
```

### RestatePromise.any() - First Successful Result

Returns the first successful result, ignoring rejections until all fail.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_any"}  theme={null}
// ❌ BAD - using Promise.any (not journaled)
const result1 = await Promise.any([call1, call2]);

// ✅ GOOD
const result2 = await RestatePromise.any([
  ctx.run(() => callLLM("gpt-4", prompt)),
  ctx.run(() => callLLM("claude", prompt))
]);
```

### `RestatePromise.allSettled()` - Wait for All (Success or Failure)

Returns results of all promises, whether they succeeded or failed.

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#promise_allsettled"}  theme={null}
// ❌ BAD
const results1 = await Promise.allSettled([call1, call2]);

// ✅ GOOD
const results2 = await RestatePromise.allSettled([
  ctx.serviceClient(service1).call(),
  ctx.serviceClient(service2).call()
]);

results2.forEach((result, i) => {
  if (result.status === "fulfilled") {
    console.log(`Call ${i} succeeded:`, result.value);
  } else {
    console.log(`Call ${i} failed:`, result.reason);
  }
});
```

### Invocation Management

```ts {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-actions.ts#cancel"}  theme={null}
const handle = ctx.serviceSendClient(myService).myHandler(
    "Hi",
    restate.rpc.sendOpts({ idempotencyKey: "my-key" })
);
const invocationId = await handle.invocationId;
const response = await ctx.attach(invocationId);

// Cancel invocation
ctx.cancel(invocationId);
```

## Serialization

### Default (JSON)

By default, TypeScript SDK uses built-in JSON support.

### Zod Schemas

For type safety and validation with Zod, install: `npm install @restatedev/restate-sdk-zod`

```typescript {"CODE_LOAD::ts/src/develop/serialization.ts#zod"}  theme={null}
import * as restate from "@restatedev/restate-sdk";
import { z } from "zod";
import { serde } from "@restatedev/restate-sdk-zod";

const Greeting = z.object({
  name: z.string(),
});

const GreetingResponse = z.object({
  result: z.string(),
});

const greeter = restate.service({
  name: "Greeter",
  handlers: {
    greet: restate.handlers.handler(
      { input: serde.zod(Greeting), output: serde.zod(GreetingResponse) },
      async (ctx: restate.Context, { name }) => {
        return { result: `You said hi to ${name}!` };
      }
    ),
  },
});
```

### Custom Serialization

```typescript {"CODE_LOAD::ts/src/develop/serialization.ts#service_definition"}  theme={null}
const myService = restate.service({
  name: "MyService",
  handlers: {
    myHandler: restate.handlers.handler(
      {
        // Set the input serde here
        input: restate.serde.binary,
        // Set the output serde here
        output: restate.serde.binary,
      },
      async (ctx: Context, data: Uint8Array): Promise<Uint8Array> => {
        // Process the request
        return data;
      }
    ),
  },
});
```

## Error Handling

Restate retries failures indefinitely by default. For permanent business-logic failures (invalid input, declined payment), use TerminalError to stop retries immediately.

### Terminal Errors (No Retry)

```typescript {"CODE_LOAD::ts/src/develop/error_handling.ts#terminal"}  theme={null}
throw new TerminalError("Something went wrong.", { errorCode: 500 });
```

### Retryable Errors

```typescript  theme={null}
// Any other thrown error will be retried
throw new Error("Temporary failure - will retry");
```

## Testing

```typescript {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-testing.test.ts"}  theme={null}
import { RestateTestEnvironment } from "@restatedev/restate-sdk-testcontainers";
import * as clients from "@restatedev/restate-sdk-clients";
import { describe, it, beforeAll, afterAll, expect } from "vitest";
import {greeter} from "./greeter-service";

describe("MyService", () => {
    let restateTestEnvironment: RestateTestEnvironment;
    let restateIngress: clients.Ingress;

    beforeAll(async () => {
        restateTestEnvironment = await RestateTestEnvironment.start({services: [greeter]});
        restateIngress = clients.connect({ url: restateTestEnvironment.baseUrl() });
    }, 20_000);

    afterAll(async () => {
        await restateTestEnvironment?.stop();
    });

    it("Can call methods", async () => {
        const client = restateIngress.objectClient(greeter, "myKey");
        await client.greet("Test!");
    });

    it("Can read/write state", async () => {
        const state = restateTestEnvironment.stateOf(greeter, "myKey");
        await state.set("count", 123);
        expect(await state.get("count")).toBe(123);
    });
});
```

## SDK Clients (External Invocations)

```typescript {"CODE_LOAD::ts/src/develop/agentsmd/agentsmd-clients.ts#here"}  theme={null}
const restateClient = clients.connect({url: "http://localhost:8080"});

// Request-response
const result = await restateClient
    .serviceClient<MyService>({name: "MyService"})
    .myHandler("Hi");

// One-way
await restateClient
    .serviceSendClient<MyService>({name: "MyService"})
    .myHandler("Hi");

// Delayed
await restateClient
    .serviceSendClient<MyService>({name: "MyService"})
    .myHandler("Hi", clients.rpc.sendOpts({delay: {seconds: 1}}));
```

---


## File: docs/agents/durable/restate/ai-examples/vercel-ai/template/README.md

# Restate + Vercel AI Example (non-NextJS)

This is template of a simple agent written with the Vercel AI SDK and using Restate for resilience and observability.

This example is for deployments where the agent is served directly, and not as part of a NextJS app.
Use this template when deploying the agent on generic containers, FaaS (Lambda, Fly.io, etc.) or for simply experimenting locally.

## Running the template example

1. Export your OpenAI key as an environment variable. If you want to use another model (e.g., Anthrophic Claude, Google Gemini) you need to change the dependencies in `package.json` and the model in `src/app.ts` accordingly:
    ```shell
    export OPENAI_API_KEY=your_openai_api_key
    ```
2. [Start the Restate Server](https://docs.restate.dev/develop/local_dev) in a separate shell. The server is the durable orchstrator. It is queue, workflow engine, K/V store in one.
    ```shell
    npx @restatedev/restate-server@latest
    ```
3. Start the agent.
    ```shell
    npm install
    npm run dev
    ```
4. Register the services, to let Restate Server know about the agent. The Server can now proxy invocations to the agent, adding durable execution that way.
    ```shell
    npx @restatedev/restate -y deployments register localhost:9080
    ```

5. All should be ready. Now send a request to your agent. Note that we target Restate Server's endpoint (8080) because the server proxies requests to the service, to make them durable.

    ```shell
    curl localhost:8080/agent/run --json '"What is the weather in Detroit?"'
    ```

   Returns: `The weather in Detroit is currently 22°C and sunny.`

Check the Restate UI (`localhost:9080`) to see the journals of your invocations.

<img src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/get-started-vercel/journal_vercel.png" alt="Using Agent SDK - journal" width="1200px"/>
---


## File: docs/agents/durable/restate/ai-examples/vercel-ai/tour-of-agents/README.md

# Tour of AI Agents with Restate - Vercel AI SDK

Learn how to implement resilient agents with durable execution, human-in-the-loop, multi-agent communication, and parallel execution.

[Learn more](https://docs.restate.dev/tour/vercel-ai-agents)

To run:

```shell
npm install
npm run dev
```

---


## File: docs/agents/durable/restate/mcp/README.md

# Resilient MCP Server with Restate

Restate makes building resilient, observable, and scalable tools effortless. Here's what it brings to the table:

- ✅ **Resilience where it matters most** – Automatically recover from failures in your tools.
- 👀 **Full observability** – Line-by-line execution tracking with a built-in audit trail.
- 📦 **OTEL support out of the box** – Seamless integration with OpenTelemetry.
- 🌍 **Deploy anywhere** – Whether it's AWS Lambda, CloudRun, Fly.io, Cloudflare, Kubernetes, or Deno Deploy.
- 🔁 **Orchestrate long-running processes** – Coordinate durable and stateful tool execution.
- ☁️ **Easy to self-host** – Or connect to [Restate Cloud](https://restate.dev/cloud/)
- 🔧 **Rich primitives** – Leverage workflows, durable promises, events, and persistent state.

---

## Example: Generate a greeting 

```ts
  tool(
  {
    description: "Greets a person with a song and dance",
    input: z.object({ name: z.string() }),
  },
  async (ctx, { name }) => {

    const urls = await ctx.run(
      "Obtain two Pre-signed URLs for a bucket",
      () => generatePresignedUrls()
    );

    const imageStep = ctx.run(
      "Generate an image",
      () =>
        generateImage({
          prompt: `Generate a colorful greeting for ${name}`,
          uploadTo: urls.imageUrl,
        }),
      {
        maxRetryAttempts: 3,
      }
    );

    const audioStep = ctx.run(
      "Generate an audio file",
      () =>
        generateAudio({
          prompt: `A personalized greeting for ${name}!`,
          uploadTo: urls.audioUrl,
        }),
      { maxRetryAttempts: 3 }
    );

    
    await all([imageStep, audioStep]);

    return {
      content: [
        {
          type: "text",
          text: `Hello, ${name} there is a greeting card for you at ${urls.imageUrl} and a song ${urls.audioUrl}}!`,
        },
      ],
    };
  }
);

```

## Running the example

1. Export your OpenAI or Anthrophic API key as an environment variable:
    ```shell
    export OPENAI_API_KEY=your_openai_api_key
    ```
2. [Start the Restate Server](https://docs.restate.dev/develop/local_dev) in a separate shell:
    ```shell
    restate-server
    ```
3. Start the tools services:
    ```shell
    cd tools
    npm install
    npm run app
    ```
4. Register the services (use `--force` if you already had another deployment registered at 9080): 
    ```shell
    restate -y deployments register localhost:9080
    ```
5. Build the MCP server:
    ```shell
    cd restate-mcp
    npm install
    npm run build
    ```

6. Configure Claude desktop
   
   Edit:
   * macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   * Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   
   ```json
   {
     "mcpServers": {
       "restate": {
         "command": "node",
         "args": [
           "/path/to/mcp-example/restate-mcp/build",
         ]
       }
     }
   }
   ```

7. Ask Claude to greet your favorite person

![Claude](image.png "The incremental counter")


---


## File: docs/agents/durable/restate/README.md

<!-- markdown-link-check-disable -->
[![Documentation](https://img.shields.io/badge/doc-reference-blue)](https://docs.restate.dev)
[![Discord](https://img.shields.io/discord/1128210118216007792?logo=discord)](https://discord.gg/skW3AZ6uGd)
[![Slack](https://img.shields.io/badge/Slack-4A154B?logo=slack&logoColor=fff)](https://join.slack.com/t/restatecommunity/shared_invite/zt-2v9gl005c-WBpr167o5XJZI1l7HWKImA)
[![Twitter](https://img.shields.io/twitter/follow/restatedev.svg?style=social&label=Follow)](https://x.com/intent/follow?screen_name=restatedev)
<!-- markdown-link-check-enable -->

# Examples for AI workflows and Durable Agents

This repo contains a set of runnable examples of AI workflows and agents, using  **Durable Execution and Orchestration** via [Restate](https://restate.dev/) ([Github](https://github.com/restatedev/restate))

The goal is to show how you can easily add production-grade _resilience_, _state persistence_, _retries_, _suspend/resume_, _human-in-the-loop_, and _observability_ to agentic workflows. So you can ship agents that stay alive and consistent without sprinkling retry-code everywhere and without building heavyweight infra yourself.

The Restate approach works **independent of specific SDKs** but **integrates easily with popular SDKs**, like the [Vercel AI SDK](https://ai-sdk.dev/) or the [OpenAI Agent SDK](https://openai.github.io/openai-agents-python/). You can also use without and Agent SDK _(roll your own loop)_ or for more traditional workflows.


## Why Restate?
📄 For a gentle intro, read [the blog post "Durable Agents - Fault Tolerance across Frameworks and without Handcuffs"](https://restate.dev/blog/durable-ai-loops-fault-tolerance-across-frameworks-and-without-handcuffs/)


| Use Case                           | What it solves                                                                              |
|------------------------------------|---------------------------------------------------------------------------------------------|
| **Durable Execution**              | Crash-safe LLM/tool calls & idempotent retries—agents resume at the last successful step.   |
| **Detailed Observability**         | Auto-captured trace of every step, retry, and message for easy debugging and auditing.      |
| **Human-in-the-loop & long waits** | Suspend while waiting for user approval or slow jobs; pay for compute, not wall-clock time. |
| **Stateful sessions / memory**     | Virtual Objects keep multi-turn conversations and other state isolated and consistent.      |
| **Multi-agent orchestration**      | Reliable RPC, queuing, and scheduling between agents running in separate processes.         |


<img src="/doc/img/patterns/parallel_tools.png" alt="Restate UI - trace of agent with parallel tools" width="900px"/>
<br/>
<caption><em>Restate UI showing an agent execution with parallel tool calls</em></caption>


## Full Example Catalog

### Agent SDK Integrations  
| Integration | Example | Description | Code | Docs                                                 |
|-------------|---------|-------------|------|------------------------------------------------------|
| **Vercel AI SDK** | **Template** | A minimal example of how to use Restate with the Vercel AI SDK | [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](vercel-ai/template) | [📖](https://docs.restate.dev/ai-quickstart)         |
| | **Tour of Agents** | A step-by-step tutorial showing how to build resilient agents | [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](vercel-ai/tour-of-agents) | [📖](https://docs.restate.dev/tour/vercel-ai-agents) |
| | **Examples** | More advanced examples that can be deployed as a Next.js app on Vercel | [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](vercel-ai/examples) | -                                                    |
| **OpenAI Agents SDK** | **Template** | A minimal example of how to use Restate with the OpenAI Agents SDK | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](openai-agents/template) | [📖](https://docs.restate.dev/ai-quickstart)         |
| | **Tour of Agents** | A step-by-step tutorial showing how to build resilient agents | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](openai-agents/tour-of-agents) | [📖](https://docs.restate.dev/tour/openai-agents)    |

### Composable AI Patterns
| Pattern                | Description | Code | Docs |
|------------------------|-------------|------|------|
| **Chaining LLM calls** | Build fault-tolerant processing pipelines where each step transforms the previous step's output | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/chaining.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/chaining.ts) | [📖](https://docs.restate.dev/ai/patterns/prompt-chaining) |
| **Tool routing** | Automatically route requests to tools based on LLM outputs | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/routing_to_tool.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/routing-to-tools.ts) | [📖](https://docs.restate.dev/ai/patterns/tools) |
| **Parallel tool execution** | Execute multiple tools in parallel with durable results that persist across failures | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/parallel_tools.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/parallel-tools.ts) | [📖](https://docs.restate.dev/ai/patterns/parallelization) |
| **Multi-agent routing** | Route requests to specialized agents based on LLM outputs | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/routing_to_agent.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/routing-to-agent.ts) | [📖](https://docs.restate.dev/ai/patterns/multi-agent) |
| **Remote agent routing** | Deploy/scale agents separately and route requests with resilient communication | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/routing_to_remote_agent.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/routing-to-remote-agent.ts) | [📖](https://docs.restate.dev/ai/patterns/multi-agent) |
| **Parallel agent processing** | Run multiple, specialized agents in parallel and aggregate their results | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/parallel_agents.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/parallel-agents.ts) | [📖](https://docs.restate.dev/ai/patterns/parallelization) |
| **Racing agents** | Race multiple agents against each other and use the fastest response | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/racing_agents.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/racing-agents.ts) | [📖](https://docs.restate.dev/ai/patterns/competitive-racing) |
| **Human-in-the-loop pattern** | Implement resilient human approval steps that suspend execution until feedback is received | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/human_in_the_loop.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/human-in-the-loop.ts) | [📖](https://docs.restate.dev/ai/patterns/human-in-the-loop) |
| **Chat sessions** | Long-lived, stateful chat sessions that maintain conversation state across multiple requests | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/chat.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/chat.ts) | [📖](https://docs.restate.dev/ai/patterns/sessions-and-chat) |
| **Orchestrator-worker pattern** | Break down complex tasks into specialized subtasks and execute them in parallel | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/orchestrator_workers.py) | - |
| **Evaluator-optimizer pattern** | Generate → Evaluate → Improve loop until quality criteria are met | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](python-patterns/app/evaluator_optimizer.py) [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](typescript-patterns/src/evaluator-optimizer.ts) | - |

### Other Examples
| Example                | Description | Code |
|------------------------|-------------|------|
| **MCP**                |  Using Restate for exposing tools and resilient orchestration of tool calls | [<img src="https://skillicons.dev/icons?i=ts&theme=light" width="20" height="20">](mcp) | 
| **A2A**                | Implement Google's Agent-to-Agent protocol with Restate as resilient, scalable task orchestrator | [<img src="https://skillicons.dev/icons?i=python&theme=light" width="20" height="20">](a2a) | 

Restate currently supports 6 languages:

[![TypeScript](https://skillicons.dev/icons?i=ts)](https://docs.restate.dev/develop/ts/overview)
[![Python](https://skillicons.dev/icons?i=python&theme=light)](https://docs.restate.dev/develop/python/overview)
[![Java](https://skillicons.dev/icons?i=java&theme=light)](https://docs.restate.dev/develop/java/overview)
[![Kotlin](https://skillicons.dev/icons?i=kotlin&theme=light)](https://docs.restate.dev/develop/java/overview)
[![Go](https://skillicons.dev/icons?i=go)](https://docs.restate.dev/develop/go/overview)
[![Rust](https://skillicons.dev/icons?i=rust&theme=light)](https://docs.rs/restate-sdk/latest/restate_sdk/)

The examples can be translated to any of the supported languages. 
Join our [Discord](https://discord.gg/skW3AZ6uGd)/[Slack](https://join.slack.com/t/restatecommunity/shared_invite/zt-2v9gl005c-WBpr167o5XJZI1l7HWKImA) to get help with translating an examples to your language of choice.

## Learn more
- [Documentation](https://docs.restate.dev/ai)
- [Examples on workflows, microservice orchestration, async tasks, event processing](https://github.com/restatedev/examples)
- [Restate Cloud](https://restate.dev/cloud/)
- [Discord](https://discord.gg/skW3AZ6uGd) / [Slack](https://join.slack.com/t/restatecommunity/shared_invite/zt-2v9gl005c-WBpr167o5XJZI1l7HWKImA)

## Acknowledgements

- The DIY patterns are largely based on Anthropic's [agents cookbook](https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents).
- Some of the A2A examples in this repo are based on the examples included in the [Google A2A repo](https://github.com/google/A2A/tree/main).

---


## File: docs/agents/durable/restate/typescript-patterns/README.md

# Patterns for building resilient LLM-based apps and agents with Restate

These patterns show how you can use Restate to harden LLM-based routing decisions and tool executions.

These small self-contained patterns can be mixed and matched to build more complex agents or workflows.

The patterns included here:

- [Chaining LLM calls](src/chaining.ts): Build fault-tolerant processing pipelines where each step transforms the previous step's output.
- [Tool routing](src/routing-to-tools.ts): Automatically route requests to tools based on LLM outputs.
- [Parallel tool execution](src/parallel-tools.ts): Execute multiple tools in parallel with durable results that persist across failures.
- [Multi-agent routing](src/routing-to-agent.ts): Route requests to specialized agents based on LLM outputs.
- [Remote agent routing](src/routing-to-remote-agent.ts): Deploy/scale agents separately and route requests with resilient communication.
- [Parallel agent processing](src/parallel-agents.ts): Run multiple, specialized agents in parallel and aggregate their results.
- [Racing agents](src/racing-agents.ts): Race multiple agents and return the result from whichever completes first successfully.
- [Evaluator-optimizer pattern](src/evaluator-optimizer.ts): Generate → Evaluate → Improve loop until quality criteria are met.
- [Human-in-the-loop pattern](src/human-in-the-loop.ts): Implement resilient human approval steps that suspend execution until feedback is received.
- [Chat sessions](src/chat.ts): Long-lived, stateful chat sessions that maintain conversation state across multiple requests.

## Why Restate?

The benefits of using Restate here are:

- 🔁 **Automatic retries** of failed tasks: LLM API down, timeouts, long-running tasks, infrastructure failures, etc. Restate guarantees all tasks run to completion exactly once.
- ✅ **Recovery of previous progress**: After a failure, Restate recovers the progress the execution did before the crash.
  It persists routing decisions, tool execution outcomes, and deterministically replays them after failures, as opposed to executing them again.
- 🧠 **Exactly-once execution** - Automatic deduplication of requests and tool executions via idempotency keys.
- 💾 **Persistent memory** - Maintain session state across infrastructure events.
  The state can be queried from the outside. Stateful sessions are long-lived and can be resumed at any time.
- 🎮 **Task control** - Cancel tasks, query status, re-subscribe to ongoing tasks, and track progress across failures, time, and processes.

## Running the examples

1. Export your OpenAI API key as an environment variable:
   ```shell
   export OPENAI_API_KEY=your_openai_api_key
   ```
2. [Start the Restate Server](https://docs.restate.dev/develop/local_dev) in a separate shell:
   ```shell
   restate-server
   ```
3. Start the services:
   ```shell
   npm run dev
   ```
4. Register the services (use `--force` if you already had another deployment registered at 9080):
   ```shell
   restate -y deployments register localhost:9080 --force
   ```

### Chaining LLM calls

[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](src/chaining.ts)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/prompt-chaining)

Build fault-tolerant processing pipelines where each step transforms the previous step's output.

In the UI (`http://localhost:9070`), click on the `process` handler of the `CallChainingService` to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/chaining_playground.png" alt="Chaining LLM calls - UI"/>

You see in the Invocations Tab of the UI how the LLM is called multiple times, and how the results are refined step by step:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/chaining.png" alt="Chaining LLM calls - UI"/>

### Tool routing

[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](src/routing-to-tools.ts)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/tools)

Automatically route requests to tools based on LLM outputs. The agent keeps calling the LLM and executing tools until a final answer is returned.

In the UI (`http://localhost:9070`), click on the `route` handler of the `ToolRouter` service to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/routing_local_tools_playground.png" alt="Dynamic routing LLM calls - UI"/>

In the UI, you can see how the LLM decides to forward the request to the technical support tools, and how the response is processed:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/routing_local_tools.png" alt="Dynamic routing based on LLM output - UI"/>

### Parallel tool execution

[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](src/parallel-tools.ts)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/parallelization)

Execute multiple tools in parallel with durable results that persist across failures.

In the UI (`http://localhost:9070`), click on the `run` handler of the `ParallelToolAgent` to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/parallel_tools_playground.png" alt="Parallel tool calls - UI"/>

You see in the UI how the different tools are executed in parallel:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/parallel_tools.png" alt="Parallel tool calls - UI"/>

Once all tools are done, the results are aggregated and returned to the client.

### Multi-agent routing

[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](src/routing-to-agent.ts)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/multi-agent)

Route requests to specialized agents based on LLM outputs. Routing decisions are persisted and can be retried.

In the UI (`http://localhost:9070`), click on the `answer` handler of the `AgentRouter` service to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/routing_local_agent_playground.png" alt="Multi-agent routing - UI"/>

In the UI, you can see how the LLM decides to forward the request to the specialized support agents, and how the response is processed:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/routing_local_agent.png" alt="Multi-agent routing - UI"/>

### Remote agent routing

[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](src/routing-to-remote-agent.ts)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/multi-agent)

Route requests to remote agents with resilient communication.
Restate proxies requests to remote agents, persisting routing decisions and results.
In case of failures, Restate retries failed executions.

In the UI (`http://localhost:9070`), click on the `answer` handler of the `RemoteAgentRouter` service to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/routing_remote_agent_playground.png" alt="Multi-agent routing - UI"/>

In the UI, you can see how the LLM decides to forward the request to the specialized support agents, and how the nested call is also shown in the UI:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/routing_remote_agent.png" alt="Multi-agent routing - UI"/>

### Parallel agent processing

[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](src/parallel-agents.ts)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/parallelization)

Run multiple, specialized agents in parallel and aggregate their results. If any agent fails, Restate retries only the failed agents while preserving completed results.

In the UI (`http://localhost:9070`), click on the `analyze` handler of the `ParallelAgentsService` to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/parallel_agents_playground.png" alt="Parallel agents - UI"/>

You see in the UI how the different agents are executed in parallel:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/parallel_agents.png" alt="Parallel agents - UI"/>

Once all agents are done, the results are aggregated and returned to the client.

### Racing agents

[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](src/racing-agents.ts)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/competitive-racing)

Execute multiple AI approaches or strategies simultaneously and return the result from whichever completes first successfully.

Restate turns Promises/Futures into durable, distributed constructs that persist across failures and process restarts.

In the UI (`http://localhost:9070`), click on the `run` handler of the `RacingAgent` service to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/typescript_patterns/doc/img/patterns/racing_playground.png" alt="Racing agents - UI"/>

You see in the UI how the different agents are executed in parallel and the first successful result is returned, while the other agents are cancelled:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/typescript_patterns/doc/img/patterns/racing.png" alt="Racing agents - UI"/>

### Human-in-the-loop pattern

[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](src/human-in-the-loop.ts)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/human-in-the-loop)

Implement resilient human approval steps that suspend execution until feedback is received. Durable promises survive crashes and can be recovered across process restarts.

In the UI (`http://localhost:9070`), click on the `moderate` handler of the `HumanInTheLoopService` to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/human-in-the-loop-playground.png" alt="Human-in-the-loop pattern - UI"/>

Test this out by killing the service halfway through or restarting the Restate Server. You will notice that Restate will still be able to resolve the promise and invoke the handler again.

Then use the **curl command printed in the service logs** to provide your feedback.

You can see how the feedback gets incorporated in the Invocations tab in the Restate UI (`http://localhost:9070`):

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/human-in-the-loop.png" alt="Human-in-the-loop pattern - UI"/>

### Chat sessions

[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](src/chat.ts)
[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/read-guide.svg">](https://docs.restate.dev/ai/patterns/sessions-and-chat)

Long-lived, stateful chat sessions that maintain conversation state across multiple requests. Sessions survive failures and can be resumed at any time.

In the UI (`http://localhost:9070`), click on the `message` handler of the `Chat` service to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/chat-1.png" alt="Chat" width="900px"/>

You can then provide feedback on the response by sending new messages to the same session:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/chat-2.png" alt="Chat" width="900px"/>

In the invocations tab, you can see how the memory was loaded and stored in Restate:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/chat.png" alt="Chat - UI"/>

Go to the state tab of the UI to see the state of the chat session:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/chat-state.png" alt="Chat" width="900px"/>

### Evaluator-optimizer pattern

[<img src="https://raw.githubusercontent.com/restatedev/img/refs/heads/main/show-code.svg">](src/evaluator-optimizer.ts)

Generate → Evaluate → Improve loop until quality criteria are met. Restate persists each iteration, resuming from the last completed step on failure.

In the UI (`http://localhost:9070`), click on the `run` handler of the `EvaluatorOptimizer` to open the playground and send a default request:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/evaluator-playground.png" alt="Evaluator-optimizer pattern - UI"/>

In the UI, you can see how the LLM generates a response, and how the evaluator LLM evaluates it and asks for improvements until the response is satisfactory:

<img width="1200px" src="https://raw.githubusercontent.com/restatedev/ai-examples/refs/heads/main/doc/img/patterns/evaluator.png" alt="Evaluator-optimizer pattern - UI"/>

---


## Original Sources

- `docs/agents/convex/AI Agent.md`
- `docs/agents/convex/Convex MCP Server _ Convex Developer Hub.md`
- `docs/agents/durable/dbos/dbos-node-starter/README.md`
- `docs/agents/durable/dbos/dbos-node-toolbox/README.md`
- `docs/agents/durable/dbos/dbos-toolbox/README.md`
- `docs/agents/durable/dbos/document-detective/README.md`
- `docs/agents/durable/dbos/hacker-news-agent/frontend/README.md`
- `docs/agents/durable/dbos/hacker-news-agent/README.md`
- `docs/agents/durable/dbos/queue-worker/README.md`
- `docs/agents/durable/dbos/reliable-refunds-langchain/README.md`
- `docs/agents/durable/dbos/s3mirror/README.md`
- `docs/agents/durable/dbos/widget-store/README.md`
- `docs/agents/durable/KCG_SUMMARY.md`
- `docs/agents/durable/restate/agent47/packages/pubsub/README.md`
- `docs/agents/durable/restate/agent47/packages/ui/README.md`
- `docs/agents/durable/restate/agent47/README.md`
- `docs/agents/durable/restate/ai-examples/.tools/typescript_formatter/README.md`
- `docs/agents/durable/restate/ai-examples/a2a/README.md`
- `docs/agents/durable/restate/ai-examples/mcp/README.md`
- `docs/agents/durable/restate/ai-examples/openai-agents/template/.claude/CLAUDE.md`
- `docs/agents/durable/restate/ai-examples/openai-agents/template/.cursor/rules/AGENTS.md`
- `docs/agents/durable/restate/ai-examples/openai-agents/template/README.md`
- `docs/agents/durable/restate/ai-examples/openai-agents/tour-of-agents/README.md`
- `docs/agents/durable/restate/ai-examples/python-patterns/README.md`
- `docs/agents/durable/restate/ai-examples/README.md`
- `docs/agents/durable/restate/ai-examples/vercel-ai/examples/README.md`
- `docs/agents/durable/restate/ai-examples/vercel-ai/template_nextjs/.claude/CLAUDE.md`
- `docs/agents/durable/restate/ai-examples/vercel-ai/template_nextjs/.cursor/rules/AGENTS.md`
- `docs/agents/durable/restate/ai-examples/vercel-ai/template_nextjs/README.md`
- `docs/agents/durable/restate/ai-examples/vercel-ai/template/.claude/CLAUDE.md`
- `docs/agents/durable/restate/ai-examples/vercel-ai/template/.cursor/rules/AGENTS.md`
- `docs/agents/durable/restate/ai-examples/vercel-ai/template/README.md`
- `docs/agents/durable/restate/ai-examples/vercel-ai/tour-of-agents/README.md`
- `docs/agents/durable/restate/mcp/README.md`
- `docs/agents/durable/restate/README.md`
- `docs/agents/durable/restate/typescript-patterns/README.md`
