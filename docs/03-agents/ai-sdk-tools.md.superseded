---
truth: partial
---

# ai sdk tools

> Auto-merged from subdirectory .md files on 2026-06-06

---


## File: docs/agents/pydantic_ai/AG-UI - Pydantic AI.md

---
title: "AG-UI - Pydantic AI"
source: "https://ai.pydantic.dev/ui/ag-ui/"
author:
published:
created: 2025-12-29
description: "GenAI Agent Framework, the Pydantic way"
tags:
  - "clippings"
---
[Skip to content](https://ai.pydantic.dev/ui/ag-ui/#agent-user-interaction-ag-ui-protocol)

The [Agent-User Interaction (AG-UI) Protocol](https://docs.ag-ui.com/introduction) is an open standard introduced by the [CopilotKit](https://webflow.copilotkit.ai/blog/introducing-ag-ui-the-protocol-where-agents-meet-users) team that standardises how frontend applications communicate with AI agents, with support for streaming, frontend tools, shared state, and custom events.

Note

The AG-UI integration was originally built by the team at [Rocket Science](https://www.rocketscience.gg/) and contributed in collaboration with the Pydantic AI and CopilotKit teams. Thanks Rocket Science!

## Installation

The only dependencies are:

- [ag-ui-protocol](https://docs.ag-ui.com/introduction): to provide the AG-UI types and encoder.
- [starlette](https://www.starlette.io/): to handle [ASGI](https://asgi.readthedocs.io/en/latest/) requests from a framework like FastAPI.

You can install Pydantic AI with the `ag-ui` extra to ensure you have all the required AG-UI dependencies:

```bash
pip install 'pydantic-ai-slim[ag-ui]'
```

```bash
uv add 'pydantic-ai-slim[ag-ui]'
```

To run the examples you'll also need:

- [uvicorn](https://www.uvicorn.org/) or another ASGI compatible server

```bash
pip install uvicorn
```

```bash
uv add uvicorn
```

## Usage

There are three ways to run a Pydantic AI agent based on AG-UI run input with streamed AG-UI events as output, from most to least flexible. If you're using a Starlette-based web framework like FastAPI, you'll typically want to use the second method.

1. The [`AGUIAdapter.run_stream()`](https://ai.pydantic.dev/api/ui/base/#pydantic_ai.ui.UIAdapter.run_stream "run_stream") method, when called on an [`AGUIAdapter`](https://ai.pydantic.dev/api/ui/ag_ui/#pydantic_ai.ui.ag_ui.AGUIAdapter "AGUIAdapter
	dataclass
	") instantiated with an agent and an AG-UI [`RunAgentInput`](https://docs.ag-ui.com/sdk/python/core/types#runagentinput) object, will run the agent and return a stream of AG-UI events. It also takes optional [`Agent.iter()`](https://ai.pydantic.dev/api/agent/#pydantic_ai.agent.Agent.iter "iter
	async
	") arguments including `deps`. Use this if you're using a web framework not based on Starlette (e.g. Django or Flask) or want to modify the input or output some way.
2. The [`AGUIAdapter.dispatch_request()`](https://ai.pydantic.dev/api/ui/base/#pydantic_ai.ui.UIAdapter.dispatch_request "dispatch_request
	async
	classmethod
	") class method takes an agent and a Starlette request (e.g. from FastAPI) coming from an AG-UI frontend, and returns a streaming Starlette response of AG-UI events that you can return directly from your endpoint. It also takes optional [`Agent.iter()`](https://ai.pydantic.dev/api/agent/#pydantic_ai.agent.Agent.iter "iter
	async
	") arguments including `deps`, that you can vary for each request (e.g. based on the authenticated user). This is a convenience method that combines [`AGUIAdapter.from_request()`](https://ai.pydantic.dev/api/ui/base/#pydantic_ai.ui.UIAdapter.from_request "from_request
	async
	classmethod
	"), [`AGUIAdapter.run_stream()`](https://ai.pydantic.dev/api/ui/base/#pydantic_ai.ui.UIAdapter.run_stream "run_stream"), and [`AGUIAdapter.streaming_response()`](https://ai.pydantic.dev/api/ui/base/#pydantic_ai.ui.UIAdapter.streaming_response "streaming_response").
3. [`AGUIApp`](https://ai.pydantic.dev/api/ui/ag_ui/#pydantic_ai.ui.ag_ui.app.AGUIApp "AGUIApp") represents an ASGI application that handles every AG-UI request by running the agent. It also takes optional [`Agent.iter()`](https://ai.pydantic.dev/api/agent/#pydantic_ai.agent.Agent.iter "iter
	async
	") arguments including `deps`, but these will be the same for each request, with the exception of the AG-UI state that's injected as described under [state management](https://ai.pydantic.dev/ui/ag-ui/#state-management). This ASGI app can be [mounted](https://fastapi.tiangolo.com/advanced/sub-applications/) at a given path in an existing FastAPI app.

### Handle run input and output directly

This example uses [`AGUIAdapter.run_stream()`](https://ai.pydantic.dev/api/ui/base/#pydantic_ai.ui.UIAdapter.run_stream "run_stream") and performs its own request parsing and response generation. This can be modified to work with any web framework.

```python
Learn about Gateway run_ag_ui.pyimport json
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response, StreamingResponse
from pydantic import ValidationError

from pydantic_ai import Agent
from pydantic_ai.ui import SSE_CONTENT_TYPE
from pydantic_ai.ui.ag_ui import AGUIAdapter

agent = Agent('gateway/openai:gpt-5', instructions='Be fun!')

app = FastAPI()

@app.post('/')
async def run_agent(request: Request) -> Response:
    accept = request.headers.get('accept', SSE_CONTENT_TYPE)
    try:
        run_input = AGUIAdapter.build_run_input(await request.body())  # 
    except ValidationError as e:
        return Response(
            content=json.dumps(e.json()),
            media_type='application/json',
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    adapter = AGUIAdapter(agent=agent, run_input=run_input, accept=accept)
    event_stream = adapter.run_stream() # 

    sse_event_stream = adapter.encode_stream(event_stream)
    return StreamingResponse(sse_event_stream, media_type=accept) # AGUIAdapter.encode_stream() encodes the stream of AG-UI events as strings according to the accept header value. You can also use AGUIAdapter.streaming_response() to generate a streaming response directly from the AG-UI event stream returned by run_stream().
```

1. [`AGUIAdapter.build_run_input()`](https://ai.pydantic.dev/api/ui/ag_ui/#pydantic_ai.ui.ag_ui.AGUIAdapter.build_run_input "build_run_input
	classmethod
	") takes the request body as bytes and returns an AG-UI [`RunAgentInput`](https://docs.ag-ui.com/sdk/python/core/types#runagentinput) object. You can also use the [`AGUIAdapter.from_request()`](https://ai.pydantic.dev/api/ui/base/#pydantic_ai.ui.UIAdapter.from_request "from_request
	async
	classmethod
	") class method to build an adapter directly from a request.
2. [`AGUIAdapter.run_stream()`](https://ai.pydantic.dev/api/ui/base/#pydantic_ai.ui.UIAdapter.run_stream "run_stream") runs the agent and returns a stream of AG-UI events. It supports the same optional arguments as [`Agent.run_stream_events()`](https://ai.pydantic.dev/agents/#running-agents), including `deps`. You can also use [`AGUIAdapter.run_stream_native()`](https://ai.pydantic.dev/api/ui/base/#pydantic_ai.ui.UIAdapter.run_stream_native "run_stream_native") to run the agent and return a stream of Pydantic AI events instead, which can then be transformed into AG-UI events using [`AGUIAdapter.transform_stream()`](https://ai.pydantic.dev/api/ui/base/#pydantic_ai.ui.UIAdapter.transform_stream "transform_stream").
3. [`AGUIAdapter.encode_stream()`](https://ai.pydantic.dev/api/ui/base/#pydantic_ai.ui.UIAdapter.encode_stream "encode_stream") encodes the stream of AG-UI events as strings according to the accept header value. You can also use [`AGUIAdapter.streaming_response()`](https://ai.pydantic.dev/api/ui/base/#pydantic_ai.ui.UIAdapter.streaming_response "streaming_response") to generate a streaming response directly from the AG-UI event stream returned by `run_stream()`.

Since `app` is an ASGI application, it can be used with any ASGI server:

```shell
uvicorn run_ag_ui:app
```

This will expose the agent as an AG-UI server, and your frontend can start sending requests to it.

### Handle a Starlette request

This example uses [`AGUIAdapter.dispatch_request()`](https://ai.pydantic.dev/api/ui/base/#pydantic_ai.ui.UIAdapter.dispatch_request "dispatch_request
async
classmethod
") to directly handle a FastAPI request and return a response. Something analogous to this will work with any Starlette-based web framework.

Since `app` is an ASGI application, it can be used with any ASGI server:

```shell
uvicorn handle_ag_ui_request:app
```

This will expose the agent as an AG-UI server, and your frontend can start sending requests to it.

### Stand-alone ASGI app

This example uses [`AGUIApp`](https://ai.pydantic.dev/api/ui/ag_ui/#pydantic_ai.ui.ag_ui.app.AGUIApp "AGUIApp") to turn the agent into a stand-alone ASGI application:

```python
Learn about Gateway ag_ui_app.pyfrom pydantic_ai import Agent
from pydantic_ai.ui.ag_ui.app import AGUIApp

agent = Agent('gateway/openai:gpt-5', instructions='Be fun!')
app = AGUIApp(agent)
```

```python
ag_ui_app.pyfrom pydantic_ai import Agent
from pydantic_ai.ui.ag_ui.app import AGUIApp

agent = Agent('openai:gpt-5', instructions='Be fun!')
app = AGUIApp(agent)
```

Since `app` is an ASGI application, it can be used with any ASGI server:

```shell
uvicorn ag_ui_app:app
```

This will expose the agent as an AG-UI server, and your frontend can start sending requests to it.

## Design

The Pydantic AI AG-UI integration supports all features of the spec:

- [Events](https://docs.ag-ui.com/concepts/events)
- [Messages](https://docs.ag-ui.com/concepts/messages)
- [State Management](https://docs.ag-ui.com/concepts/state)
- [Tools](https://docs.ag-ui.com/concepts/tools)

The integration receives messages in the form of a [`RunAgentInput`](https://docs.ag-ui.com/sdk/python/core/types#runagentinput) object that describes the details of the requested agent run including message history, state, and available tools.

These are converted to Pydantic AI types and passed to the agent's run method. Events from the agent, including tool calls, are converted to AG-UI events and streamed back to the caller as Server-Sent Events (SSE).

A user request may require multiple round trips between client UI and Pydantic AI server, depending on the tools and events needed.

## Features

### State management

The integration provides full support for [AG-UI state management](https://docs.ag-ui.com/concepts/state), which enables real-time synchronization between agents and frontend applications.

In the example below we have document state which is shared between the UI and server using the [`StateDeps`](https://ai.pydantic.dev/api/ag_ui/#pydantic_ai.ag_ui.StateDeps "StateDeps
dataclass
") [dependencies type](https://ai.pydantic.dev/dependencies/) that can be used to automatically validate state contained in [`RunAgentInput.state`](https://docs.ag-ui.com/sdk/js/core/types#runagentinput) using a Pydantic `BaseModel` specified as a generic parameter.

Custom dependencies type with AG-UI state

If you want to use your own dependencies type to hold AG-UI state as well as other things, it needs to implements the [`StateHandler`](https://ai.pydantic.dev/api/ag_ui/#pydantic_ai.ag_ui.StateHandler "StateHandler") protocol, meaning it needs to be a [dataclass](https://docs.python.org/3/library/dataclasses.html) with a non-optional `state` field. This lets Pydantic AI ensure that state is properly isolated between requests by building a new dependencies object each time.

If the `state` field's type is a Pydantic `BaseModel` subclass, the raw state dictionary on the request is automatically validated. If not, you can validate the raw value yourself in your dependencies dataclass's `__post_init__` method.

If AG-UI state is provided but your dependencies do not implement [`StateHandler`](https://ai.pydantic.dev/api/ag_ui/#pydantic_ai.ag_ui.StateHandler "StateHandler"), Pydantic AI will emit a warning and ignore the state. Use [`StateDeps`](https://ai.pydantic.dev/api/ag_ui/#pydantic_ai.ag_ui.StateDeps "StateDeps
dataclass
") or a custom [`StateHandler`](https://ai.pydantic.dev/api/ag_ui/#pydantic_ai.ag_ui.StateHandler "StateHandler") implementation to receive and validate the incoming state.

```python
Learn about Gateway ag_ui_state.pyfrom pydantic import BaseModel

from pydantic_ai import Agent
from pydantic_ai.ui import StateDeps
from pydantic_ai.ui.ag_ui.app import AGUIApp

class DocumentState(BaseModel):
    """State for the document being written."""

    document: str = ''

agent = Agent(
    'gateway/openai:gpt-5',
    instructions='Be fun!',
    deps_type=StateDeps[DocumentState],
)
app = AGUIApp(agent, deps=StateDeps(DocumentState()))
```

```python
ag_ui_state.pyfrom pydantic import BaseModel

from pydantic_ai import Agent
from pydantic_ai.ui import StateDeps
from pydantic_ai.ui.ag_ui.app import AGUIApp

class DocumentState(BaseModel):
    """State for the document being written."""

    document: str = ''

agent = Agent(
    'openai:gpt-5',
    instructions='Be fun!',
    deps_type=StateDeps[DocumentState],
)
app = AGUIApp(agent, deps=StateDeps(DocumentState()))
```

Since `app` is an ASGI application, it can be used with any ASGI server:

```bash
uvicorn ag_ui_state:app --host 0.0.0.0 --port 9000
```

### Tools

AG-UI frontend tools are seamlessly provided to the Pydantic AI agent, enabling rich user experiences with frontend user interfaces.

### Events

Pydantic AI tools can send [AG-UI events](https://docs.ag-ui.com/concepts/events) simply by returning a [`ToolReturn`](https://ai.pydantic.dev/tools-advanced/#advanced-tool-returns) object with a [`BaseEvent`](https://docs.ag-ui.com/sdk/python/core/events#baseevent) (or a list of events) as `metadata`, which allows for custom events and state updates.

```python
Learn about Gateway ag_ui_tool_events.pyfrom ag_ui.core import CustomEvent, EventType, StateSnapshotEvent
from pydantic import BaseModel

from pydantic_ai import Agent, RunContext, ToolReturn
from pydantic_ai.ui import StateDeps
from pydantic_ai.ui.ag_ui.app import AGUIApp

class DocumentState(BaseModel):
    """State for the document being written."""

    document: str = ''

agent = Agent(
    'gateway/openai:gpt-5',
    instructions='Be fun!',
    deps_type=StateDeps[DocumentState],
)
app = AGUIApp(agent, deps=StateDeps(DocumentState()))

@agent.tool
async def update_state(ctx: RunContext[StateDeps[DocumentState]]) -> ToolReturn:
    return ToolReturn(
        return_value='State updated',
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=ctx.deps.state,
            ),
        ],
    )

@agent.tool_plain
async def custom_events() -> ToolReturn:
    return ToolReturn(
        return_value='Count events sent',
        metadata=[
            CustomEvent(
                type=EventType.CUSTOM,
                name='count',
                value=1,
            ),
            CustomEvent(
                type=EventType.CUSTOM,
                name='count',
                value=2,
            ),
        ]
    )
```

```python
ag_ui_tool_events.pyfrom ag_ui.core import CustomEvent, EventType, StateSnapshotEvent
from pydantic import BaseModel

from pydantic_ai import Agent, RunContext, ToolReturn
from pydantic_ai.ui import StateDeps
from pydantic_ai.ui.ag_ui.app import AGUIApp

class DocumentState(BaseModel):
    """State for the document being written."""

    document: str = ''

agent = Agent(
    'openai:gpt-5',
    instructions='Be fun!',
    deps_type=StateDeps[DocumentState],
)
app = AGUIApp(agent, deps=StateDeps(DocumentState()))

@agent.tool
async def update_state(ctx: RunContext[StateDeps[DocumentState]]) -> ToolReturn:
    return ToolReturn(
        return_value='State updated',
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=ctx.deps.state,
            ),
        ],
    )

@agent.tool_plain
async def custom_events() -> ToolReturn:
    return ToolReturn(
        return_value='Count events sent',
        metadata=[
            CustomEvent(
                type=EventType.CUSTOM,
                name='count',
                value=1,
            ),
            CustomEvent(
                type=EventType.CUSTOM,
                name='count',
                value=2,
            ),
        ]
    )
```

Since `app` is an ASGI application, it can be used with any ASGI server:

```bash
uvicorn ag_ui_tool_events:app --host 0.0.0.0 --port 9000
```

## Examples

For more examples of how to use [`AGUIApp`](https://ai.pydantic.dev/api/ui/ag_ui/#pydantic_ai.ui.ag_ui.app.AGUIApp "AGUIApp") see [`pydantic_ai_examples.ag_ui`](https://github.com/pydantic/pydantic-ai/tree/main/examples/pydantic_ai_examples/ag_ui), which includes a server for use with the [AG-UI Dojo](https://docs.ag-ui.com/tutorials/debugging#the-ag-ui-dojo).
---


## File: docs/agents/pydantic_ai/dbos/README.md

# Demo of the Pydantic Stack

---


## File: docs/agents/pydantic_ai/KCG_SUMMARY.md

# Pydantic AI — KCG Summary

## What It Is
Documentation clippings and patterns covering the **Pydantic AI stack**: Pydantic AI Gateway (unified multi-provider LLM access with built-in observability and failover), Agent-User Interaction (AG-UI) protocol integration for React frontends, MCP instrumentation via Pydantic Logfire, and DBOS durable execution integration. Also includes a DBOS integration demo showing how Pydantic AI agents compose with durable backends.

## Why This Matters for Kings' College Galway
The Pydantic AI Gateway offers a unified API layer for the multiple LLM providers used across Cianfhoghlaim (OpenCode, Hugging Face, Gemini), with built-in observability via OpenTelemetry that integrates with the existing Langfuse tracing infrastructure. The AG-UI protocol documentation provides the integration pattern for connecting the CopilotKit-powered frontend to agent backends using the same open standard the project already targets. The MCP + Logfire instrumentation guide shows how to add distributed tracing to the filesystem MCP server and future curriculum tool servers.

## Key Patterns Preserved
- `Pydantic AI Gateway - Pydantic AI.md` — Comprehensive guide to the Pydantic AI Gateway: setup, BYOK, inference purchasing, OpenTelemetry, failover, provider configuration
- `AG-UI - Pydantic AI.md` — AG-UI protocol integration guide: installation, streaming, frontend tools, shared state, custom events, CopilotKit compatibility
- `MCP - Pydantic Logfire Documentation.md` — MCP SDK instrumentation guide: client/server-side tracing, distributed traces, Logfire integration
- `dbos/README.md` — Demo of the Pydantic stack with DBOS durable execution

## Source Files
Full source removed (2026-06-06). Content originally clipped from:
- Pydantic AI docs: https://ai.pydantic.dev/
- Pydantic Logfire docs: https://logfire.pydantic.dev/
- AG-UI protocol: https://docs.ag-ui.com/

## What Was Removed
All non-markdown files were already absent (this subdir contained only 4 `.md` files and no source code).

---


## File: docs/agents/pydantic_ai/MCP - Pydantic Logfire Documentation.md

---
title: "MCP - Pydantic Logfire Documentation"
source: "https://logfire.pydantic.dev/docs/integrations/llms/mcp/"
author:
published:
created: 2025-12-29
description: "Pydantic Logfire Documentation"
tags:
  - "clippings"
---
[Skip to content](https://logfire.pydantic.dev/docs/integrations/llms/mcp/#model-context-protocol-mcp)

## Model Context Protocol (MCP)

**Logfire** supports instrumenting the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) with the [`logfire.instrument_mcp()`](https://logfire.pydantic.dev/docs/reference/api/logfire/#logfire.Logfire.instrument_mcp) method. This works on both the client and server side. If possible, calling this in both the client and server processes is recommended for nice distributed traces.

Below is a simple example. For the client, we use [Pydantic AI](https://ai.pydantic.dev/mcp/client/) (though any MCP client will work) and OpenAI. To use a different LLM provider instead of OpenAI, replace `openai:gpt-4o` in the client script with a different model name supported by Pydantic AI.

First, install the required dependencies:

```bash
pip install mcp 'pydantic-ai-slim[openai]'
```

Next, run the server script below:

```python
server.pyfrom mcp.server.fastmcp import FastMCP

import logfire

logfire.configure(service_name='server')
logfire.instrument_mcp()

app = FastMCP()

@app.tool()
def add(a: int, b: int) -> int:
    logfire.info(f'Calculating {a} + {b}')
    return a + b

app.run(transport='streamable-http')
```

Then run this client script in another terminal:

```python
agent.pyfrom pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP

import logfire

logfire.configure(service_name='agent')
logfire.instrument_pydantic_ai()  
logfire.instrument_mcp()

server = MCPServerStreamableHTTP('http://localhost:8000/mcp')
agent = Agent('openai:gpt-4o', toolsets=[server])
result = agent.run_sync('What is 7 plus 5?')
print(result.output)
```

You should see a trace like this in Logfire:

[![Logfire MCP Trace](https://logfire.pydantic.dev/docs/images/logfire-screenshot-mcp.png)](https://logfire.pydantic.dev/docs/images/logfire-screenshot-mcp.png)
---


## File: docs/agents/pydantic_ai/Pydantic AI Gateway - Pydantic AI.md

---
title: "Pydantic AI Gateway - Pydantic AI"
source: "https://ai.pydantic.dev/gateway/"
author:
published:
created: 2025-12-29
description: "GenAI Agent Framework, the Pydantic way"
tags:
  - "clippings"
---
[Skip to content](https://ai.pydantic.dev/gateway/#pydantic-ai-gateway)

## Pydantic AI Gateway

**[Pydantic AI Gateway](https://pydantic.dev/ai-gateway)** is a unified interface for accessing multiple AI providers with a single key. Features include built-in OpenTelemetry observability, real-time cost monitoring, failover management, and native integration with the other tools in the [Pydantic stack](https://pydantic.dev/).

Free while in Beta

The Pydantic AI Gateway is currently in Beta. You can bring your own key (BYOK) or buy inference through the Gateway (we will eat the card fee for now).

Sign up at [gateway.pydantic.dev](https://gateway.pydantic.dev/).

Questions?

For questions and feedback, contact us on [Slack](https://logfire.pydantic.dev/docs/join-slack/).

## Documentation Integration

To help you get started with [Pydantic AI Gateway](https://gateway.pydantic.dev/), some code examples on the Pydantic AI documentation include a "Via Pydantic AI Gateway" tab, alongside a "Direct to Provider API" tab with the standard Pydantic AI model string. The main difference between them is that when using Gateway, model strings use the `gateway/` prefix.

## Key features

- **API key management**: access multiple LLM providers with a single Gateway key.
- **Cost Limits**: set spending limits at project, user, and API key levels with daily, weekly, and monthly caps.
- **BYOK and managed providers:** Bring your own API keys (BYOK) from LLM providers, or pay for inference directly through the platform.
- **Multi-provider support:** Access models from OpenAI, Anthropic, Google Vertex, Groq, and AWS Bedrock. *More providers coming soon*.
- **Backend observability:** Log every request through [Pydantic Logfire](https://pydantic.dev/logfire) or any OpenTelemetry backend (*coming soon*).
- **Zero translation**: Unlike traditional AI gateways that translate everything to one common schema, **Pydantic AI Gateway** allows requests to flow through directly in each provider's native format. This gives you immediate access to the new model features as soon as they are released.
- **Open source with self-hosting**: Pydantic AI Gateway core is [open source](https://github.com/pydantic/pydantic-ai-gateway/) (under [AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.en.html)), allowing self-hosting with file-based configuration, instead of using the managed service.
- **Enterprise ready**: Includes SSO (with OIDC support), granular permissions, and flexible deployment options. Deploy to your Cloudflare account, or run on-premises with our [consulting support](https://pydantic.dev/contact).
```python
hello_world.pyfrom pydantic_ai import Agent

agent = Agent('gateway/openai:gpt-5')

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
"""
The first known use of "hello, world" was in a 1974 textbook about the C programming language.
"""
```

## Quick Start

This section contains instructions on how to set up your account and run your app with Pydantic AI Gateway credentials.

### Create an account

Using your GitHub or Google account, sign in at [gateway.pydantic.dev](https://gateway.pydantic.dev/). Choose a name for your organization (or accept the default). You will automatically be assigned the Admin role.

A default project will be created for you. You can choose to use it, or create a new one on the [Projects](https://gateway.pydantic.dev/admin/projects) page.

### Add Providers

There are two ways to use Providers in the Pydantic AI Gateway: you can bring your own key (BYOK) or buy inference through the platform.

#### Bringing your own API key (BYOK)

On the [Providers](https://gateway.pydantic.dev/admin/providers) page, fill in the form to add a provider. Paste your API key into the form under Credentials, and make sure to **select the Project that will be associated to this provider**. It is possible to add multiple keys from the same provider.

#### Use Built-in Providers

Go to the [Billing page](https://gateway.pydantic.dev/admin/billing), add a payment method, and purchase $15 in credits to activate built-in providers. This gives you single-key access to all available models from OpenAI, Anthropic, Google Vertex, AWS Bedrock, and Groq.

### Grant access to your team

On the [Users](https://gateway.pydantic.dev/admin/users) page, create an invitation and share the URL with your team to allow them to access the project.

### Create Gateway project keys

On the Keys page, Admins can create project keys which are not affected by spending limits. Users can only create personal keys, that will inherit spending caps from both User and Project levels, whichever is more restrictive.

## Usage

After setting up your account with the instructions above, you will be able to make an AI model request with the Pydantic AI Gateway. The code snippets below show how you can use Pydantic AI Gateway with different frameworks and SDKs. You can add `gateway/` as prefix on every known provider that

To use different models, change the model string `gateway/<api_format>:<model_name>` to other models offered by the supported providers.

Examples of providers and models that can be used are:

| **Provider** | **API Format** | **Example Model** |
| --- | --- | --- |
| OpenAI | `openai` | `gateway/openai:gpt-5` |
| Anthropic | `anthropic` | `gateway/anthropic:claude-sonnet-4-5` |
| Google Vertex | `google-vertex` | `gateway/google-vertex:gemini-2.5-flash` |
| Groq | `groq` | `gateway/groq:openai/gpt-oss-120b` |
| AWS Bedrock | `bedrock` | `gateway/bedrock:amazon.nova-micro-v1:0` |

### Pydantic AI

Before you start, make sure you are on version 1.16 or later of `pydantic-ai`. To update to the latest version run:

```bash
uv sync -P pydantic-ai
```

```bash
pip install -U pydantic-ai
```

Set the `PYDANTIC_AI_GATEWAY_API_KEY` environment variable to your Gateway API key:

```bash
export PYDANTIC_AI_GATEWAY_API_KEY="paig_<example_key>"
```

You can access multiple models with the same API key, as shown in the code snippet below.

```python
hello_world.pyfrom pydantic_ai import Agent

agent = Agent('gateway/openai:gpt-5')

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
"""
The first known use of "hello, world" was in a 1974 textbook about the C programming language.
"""
```

Pass your API key directly using the [`gateway_provider`](https://ai.pydantic.dev/api/providers/#pydantic_ai.providers.gateway.gateway_provider):

```python
passing_api_key.pyfrom pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.gateway import gateway_provider

provider = gateway_provider('openai', api_key='paig_<example_key>')
model = OpenAIChatModel('gpt-5', provider=provider)
agent = Agent(model)

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
"""
The first known use of "hello, world" was in a 1974 textbook about the C programming language.
"""
```

To use an alternate provider or routing group, you can specify it in the route parameter:

```python
routing_via_provider.pyfrom pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.gateway import gateway_provider

provider = gateway_provider(
    'openai',
    api_key='paig_<example_key>',
    route='builtin-openai'
)
model = OpenAIChatModel('gpt-5', provider=provider)
agent = Agent(model)

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
"""
The first known use of "hello, world" was in a 1974 textbook about the C programming language.
"""
```

### Claude Code

Before you start, log out of Claude Code using `/logout`.

Set your gateway credentials as environment variables:

```bash
export ANTHROPIC_BASE_URL="https://gateway.pydantic.dev/proxy/anthropic"
export ANTHROPIC_AUTH_TOKEN="YOUR_PYDANTIC_AI_GATEWAY_API_KEY"
```

Replace `YOUR_PYDANTIC_AI_GATEWAY_API_KEY` with the API key from the Keys page.

Launch Claude Code by typing `claude`. All requests will now route through the Pydantic AI Gateway.

### SDKs

#### OpenAI SDK

```python
openai_sdk.pyimport openai

client = openai.Client(
    base_url='https://gateway.pydantic.dev/proxy/chat/',
    api_key='paig_...',
)

response = client.chat.completions.create(
    model='gpt-5',
    messages=[{'role': 'user', 'content': 'Hello world'}],
)
print(response.choices[0].message.content)
#> Hello user
```

#### Anthropic SDK

```python
anthropic_sdk.pyimport anthropic

client = anthropic.Anthropic(
    base_url='https://gateway.pydantic.dev/proxy/anthropic/',
    auth_token='paig_...',
)

response = client.messages.create(
    max_tokens=1000,
    model='claude-sonnet-4-5',
    messages=[{'role': 'user', 'content': 'Hello world'}],
)
print(response.content[0].text)
#> Hello user
```

## Troubleshooting

### Unable to calculate spend

The gateway needs to know the cost of the request in order to provide insights about the spend, and to enforce spending limits. If it's unable to calculate the cost, it will return a 400 error with the message "Unable to calculate spend".

When [configuring a provider](https://gateway.pydantic.dev/admin/providers/new), you need to decide if you want the gateway to block the API key if it's unable to calculate the cost. If you choose to block the API key, any further requests using that API key will fail.

We are actively working on supporting more providers, and models. If you have a specific provider that you would like to see supported, please let us know on [Slack](https://logfire.pydantic.dev/docs/join-slack/) or [open an issue on `genai-prices`](https://github.com/pydantic/genai-prices/issues/new).
---


## File: docs/agents/smolagents/firecrawl-deepresearch/docs/blog-post.md

# Multi-Agent Deep Research with Smolagents + Firecrawl

Think of this as the written version of the video: a friendly walkthrough of how to wire up a deep‑research pipeline that runs on open models, uses Firecrawl to search and scrape, and leans on smolagents for clean orchestration. Grab a coffee—let’s build it together.

![Open Deep Research Workflow](open-deep-research-workflow-diagram.png)

## What We’re Building 
1) You type a question in the CLI.
2) A planner LLM drafts a thorough research map.
3) A splitter LLM turns that map into bite‑sized, non‑overlapping subtasks (JSON).
4) A coordinator agent spins up one sub-agent per subtask; every sub-agent can search & scrape the web through Firecrawl’s MCP toolkit.
5) The coordinator stitches every mini-report into one polished markdown file: `research_result.md`.

Everything below points to code in this repo so you can connect the dots as you read.

## Quick Setup (so you can follow along)
- Python 3.11
- Env vars: `HF_TOKEN` (Hugging Face Inference) and `FIRECRAWL_API_KEY` (for MCP tools).
- Install deps: `uv sync` (or `pip install -e .`).
- Run the pipeline: `uv run main.py`, then enter any research question.

## Step 1: Draft a Research Plan (`planner.py`)
We start by asking an open model to write the plan for us. It streams tokens, so you watch it think. But that is not necessary. You can just remove the `stream=True` flag and return the full completion if you want.

Also, feel free to check the `prompts.py` file to see the system instructions for the planner.

```python
# planner.py
from huggingface_hub import InferenceClient
from prompts import PLANNER_SYSTEM_INSTRUCTIONS

def generate_research_plan(user_query: str) -> str:
    MODEL_ID = "moonshotai/Kimi-K2-Thinking"
    PROVIDER = "auto"

    planner_client = InferenceClient(
        api_key=os.environ["HF_TOKEN"],
        bill_to="huggingface",
        provider=PROVIDER,
    )

    completion = planner_client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": user_query},
        ],
        stream=True,
    )
    # stream chunks into a string and return
```

Why start with a planner? It keeps the later agents on the same page and forces the model to expose its assumptions (regions, time spans, variables, outputs) up front.

## Step 2: Split the Plan into Focused Subtasks (`task_splitter.py`)
Now we ask another model to turn that plan into structured JSON. Pydantic provides the schema, and Hugging Face’s `response_format` makes the LLM obey it.

In this example, I omit the `Field` descriptions for conciseness. It is a good practice to include them in production code to make the JSON schema self-documenting. The agent also sees the descriptions when it is reasoning about the subtasks.

```python
# task_splitter.py (core bits)
class Subtask(BaseModel):
    id: str
    title: str
    description: str

class SubtaskList(BaseModel):
    subtasks: List[Subtask]

TASK_SPLITTER_JSON_SCHEMA = {
    "name": "subtaskList",
    "schema": SubtaskList.model_json_schema(),
    "strict": True,
}

completion = client.chat.completions.create(
    model=MODEL_ID,
    messages=[
        {"role": "system", "content": TASK_SPLITTER_SYSTEM_INSTRUCTIONS},
        {"role": "user", "content": research_plan},
    ],
    response_format={
        "type": "json_schema",
        "json_schema": TASK_SPLITTER_JSON_SCHEMA,
    }
)

subtasks = json.loads(completion.choices[0].message.content)["subtasks"]
```

The payoff: each sub-agent gets a crisp mission like “Temperature data collection” or “Historical climate drivers,” so they don’t step on each other.

## Step 3: Coordinator + Sub-Agents Share Firecrawl Tools (`coordinator.py`)
Here’s where it gets fun. We reuse Firecrawl’s MCP server so we don’t have to hand-code search or scraping tools—the agents inherit them automatically.

You can also create your own research tools if you want to have full control over the search and scraping logic. But the team at Firecrawl already build a great set of tools that you can use out of the box. Check out the [Firecrawl MCP documentation](https://docs.firecrawl.dev/mcp-server) for more details.

```python
FIRECRAWL_API_KEY = os.environ["FIRECRAWL_API_KEY"]
MCP_URL = f"https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/v2/mcp"

with MCPClient({"url": MCP_URL, "transport": "streamable-http"}) as mcp_tools:

    @tool
    def initialize_subagent(subtask_id: str, subtask_title: str, subtask_description: str) -> str:
        subagent = ToolCallingAgent(
            tools=mcp_tools,            # Firecrawl search/scrape
            model=subagent_model,
            add_base_tools=False,
            name=f"subagent_{subtask_id}",
        )

        subagent_prompt = SUBAGENT_PROMPT_TEMPLATE.format(
            user_query=user_query,
            research_plan=research_plan,
            subtask_id=subtask_id,
            subtask_title=subtask_title,
            subtask_description=subtask_description,
        )
        return subagent.run(subagent_prompt)
```

- Sub-agents all use the same prompt template from `prompts.py`, so their reports share structure (summary, analysis, bullets, sources).
- Models: coordinator and sub-agents default to `MiniMaxAI/MiniMax-M1-80k` via Novita. Swap `COORDINATOR_MODEL_ID` / `SUBAGENT_MODEL_ID` to try other long-context models.

### Coordinator Orchestration
The coordinator’s only “tool” is the ability to spawn sub-agents. It loops through the JSON subtasks, calls the tool once per subtask, waits, then merges the incoming markdown. Tekan look at the `COORDINATOR_PROMPT_TEMPLATE` in `prompts.py` to see how it works.

```python
coordinator = ToolCallingAgent(
    tools=[initialize_subagent],
    model=coordinator_model,
    add_base_tools=False,
    name="coordinator_agent",
)

coordinator_prompt = COORDINATOR_PROMPT_TEMPLATE.format(
    user_query=user_query,
    research_plan=research_plan,
    subtasks_json=json.dumps(subtasks, indent=2, ensure_ascii=False),
)

final_report = coordinator.run(coordinator_prompt)
```

The prompt literally says: “Call `initialize_subagent` for every subtask, then synthesize everything into one polished report.” No hidden magic—just tools + prompt discipline.

## Centralized Prompt Templates (`prompts.py`)
All the instructions live in one file so you can tweak the voice or structure in a single place and instantly affect every agent.

- `PLANNER_SYSTEM_INSTRUCTIONS`: tells the planner to output a detailed, first-person plan with explicit dimensions and expected format.
- `TASK_SPLITTER_SYSTEM_INSTRUCTIONS`: teaches the splitter to return 3–8 non-overlapping subtasks and to respect the JSON schema.
- `SUBAGENT_PROMPT_TEMPLATE`: shared by every sub-agent; we `.format` in the global query, full plan, and each task’s id/title/description so the only thing that changes is the task payload.
- `COORDINATOR_PROMPT_TEMPLATE`: guides orchestration—loop over subtasks, call the tool exactly once each, then produce a single markdown report with bibliography and open questions.

Why centralize? Because when you decide “let’s add stricter citation rules” or “make the summaries shorter,” you touch one file and the whole system listens. It’s also great for A/B testing—drop in an alternate template and toggle it with an env var or flag.

## Step 4: The Tiny CLI (`main.py`)
`main.py` is intentionally bare-bones: load env vars, ask for a question, run the pipeline, write `research_result.md`, and tell you where it went. That’s it.

```python
def main():
    load_dotenv()
    user_query = input("Enter your research query: ")
    result = run_deep_research(user_query)
    with open("research_result.md", "w") as f:
        f.write(result)
    print("Research result saved to research_result.md")
```

### Run the whole thing
Hit Enter, and logs start flying: first the planner, then the splitter, then a flurry of Firecrawl searches/scrapes as sub-agents work in parallel. Depending on your models and the scope, expect a few minutes.

## Run It Yourself (end-to-end)
1) Export keys: `export HF_TOKEN=...` and `export FIRECRAWL_API_KEY=...`.
2) Install: `uv sync`.
3) Start: `uv run main.py` and enter something ambitious (e.g., “How will offshore wind build-out affect New Jersey coastal grids by 2030?”).
4) Watch the console as agents spawn and call Firecrawl.
5) Open `research_result.md` to read the stitched report.

## Customize Without Breaking the Flow
- **Models:** Swap `MODEL_ID` constants in `planner.py`, `task_splitter.py`, and `coordinator.py`. Favor big context windows for coordinator/sub-agents.
- **Prompts:** Edit `prompts.py` to change tone, add citation rules, or enforce tables/charts.
- **Tools:** Firecrawl MCP already exposes search/scrape/map. Add your own `@tool` functions next to `initialize_subagent` if you need domain APIs.
- **Guardrails:** Add a “human approves plan” step, or cap the number of subtasks before spawning agents.

You now have a minimal—but inspectable—deep-research system that matches the video tutorial. Tinker with prompts, swap models, or bolt on new tools; the architecture is small enough that every change is easy to reason about.

---


## File: docs/agents/smolagents/firecrawl-deepresearch/README.md

# Firecrawl + Smolagents Deep Research (Multi‑Agent)

Deep‑research system that takes a user query, plans the work, splits it into focused subtasks, and orchestrates specialized sub‑agents to investigate each part. A coordinator agent synthesizes all findings into a single, well‑structured report.

The workflow mirrors the diagram you attached: generate plan → split into tasks → coordinator spawns sub‑agents → sub‑agents research → coordinator aggregates → final result.

## Links
- [YouTube video tutorial](https://www.youtube.com/watch?v=vHBRmXpDIFY)
- [Written version of the tutorial](https://alejandro-ao.com/posts/agents/multi-agent-deep-research/)

## Highlights
- Built on `smolagents` (by Hugging Face) for agent orchestration and tool calling.
- All LLM calls run via Hugging Face Inference Providers using open models.
- Uses Firecrawl MCP tools for web research and retrieval.
- Produces a consolidated markdown report saved to `research_result.md`.

## How It Works
- Plan generation: `planner.py:5` creates a high‑level research plan using an HF Inference model.
- Task splitting: `task_splitter.py:35` turns the plan into clear, non‑overlapping subtasks (JSON schema enforced).
- Coordinator: `coordinator.py:15` orchestrates the workflow and exposes the tool `initialize_subagent(...)` to spawn focused sub‑agents with shared MCP tools.
- Sub‑agents: created inside `coordinator.py:46`, each runs a targeted prompt and returns a markdown report.
- Synthesis: the coordinator gathers all sub‑agent outputs and creates the final report.

![Open Deep Research Workflow Diagram](docs/open-deep-research-workflow-diagram.png)

## Models & Providers
- Models are configured in code and executed via Hugging Face Inference Providers.
- Defaults demonstrate open‑model usage (e.g., `deepseek-ai/*`) and can be changed by editing the `MODEL_ID` constants:
  - Planner: `planner.py:6`
  - Task splitter: `task_splitter.py:37`
  - Coordinator/Sub‑agents: `coordinator.py:12` and `coordinator.py:13`
- Pick any open model available through HF providers (examples: `deepseek-ai/DeepSeek-R1`, `Qwen/Qwen2.5-32B-Instruct`, `tiiuae/falcon-40b-instruct`).

## Firecrawl MCP Tools
- Configured in `coordinator.py:8`–`coordinator.py:9` and shared with all agents via `MCPClient`.
- Provide powerful search, crawl, and retrieval capabilities used during sub‑agent research.

## Setup
- Requirements: Python `3.11` (`.python-version`), internet access, Hugging Face account for tokens.
- Recommended (uv):
  - `uv sync` to create `.venv` and install deps from `pyproject.toml`
  - For editable install: `uv pip install -e .`
- Fallback (pip): `pip install -e .`

## Configuration
- Environment variables (load via `.env` or your shell):
  - `HF_TOKEN`: Hugging Face token used by all LLM calls (`planner.py:14`, `task_splitter.py:45`, `coordinator.py:31` and `coordinator.py:37`).
  - `FIRECRAWL_API_KEY`: API key for Firecrawl MCP (`coordinator.py:8`).
- Model selection: edit `MODEL_ID` and provider values in the files listed under “Models & Providers” to choose the open models you prefer.

## Run
- `uv run main.py`
- Enter your query when prompted. The final consolidated report is written to `research_result.md`.

## Workflow Diagram
- The full workflow operates exactly as in the attached diagram: plan → tasks → coordinator → parallel sub‑agents → coordinator synthesis → final result. The coordinator and sub‑agents run on open HF‑hosted models via Inference Providers, and the agent framework is `smolagents` (HF).

## File Map
- `main.py`: CLI entry point that runs the pipeline and writes the final report.
- `coordinator.py`: coordinator agent, sub‑agent tool, and MCP integration.
- `planner.py`: research plan generation with HF Inference.
- `task_splitter.py`: JSON‑schema‑validated task decomposition.
- `prompts.py`: prompt templates for planner, splitter, sub‑agents, and coordinator.

## Notes
- All agents share the same MCP toolset, ensuring consistent access to Firecrawl capabilities.
- Swap model IDs to any open model available via HF providers to match your cost/quality constraints.

---


## File: docs/agents/smolagents/KCG_SUMMARY.md

# Smolagents — KCG Summary

## What It Is
A **multi-agent deep research system** built on HuggingFace's `smolagents` framework with Firecrawl MCP tools for web retrieval. The workflow follows a plan → split → coordinate → research → synthesize pattern: a planner generates a research strategy, a task splitter decomposes it into subtasks, a coordinator spawns specialized sub-agents, and the coordinator synthesizes all findings into a consolidated markdown report. All LLM calls use Hugging Face Inference Providers with open models.

## Why This Matters for Kings' College Galway
The plan-and-orchestrate pattern directly maps to the kind of multi-source curriculum research needed for the oideachais platform — generating a comprehensive Leaving Cert study guide by splitting research across subjects (Irish, English, Maths, etc.) and having specialized sub-agents investigate each topic independently before synthesis. The Firecrawl MCP integration demonstrates how to wire web search/retrieval into agent tool-calling, which is the exact pattern needed for the examinations.ie and curriculum.ie scraping pipelines. Using Hugging Face's open-model inference aligns with the project's commitment to open-source AI models for Irish language education.

## Key Patterns Preserved
- `firecrawl-deepresearch/README.md` — Complete multi-agent deep research workflow: planner, task splitter, coordinator, sub-agents, synthesis, models and providers, how to run
- `firecrawl-deepresearch/docs/blog-post.md` — Written tutorial (from alejandro-ao.com) explaining the multi-agent architecture in depth

## Source Files
Full source removed (2026-06-06), available at:
- Tutorial: https://alejandro-ao.com/posts/agents/multi-agent-deep-research/
- Smolagents: https://github.com/huggingface/smolagents

## What Was Removed
Python source (`.py` — planner, task_splitter, coordinator), license files, `.gitignore`, images (`.png`), and all non-markdown assets.

---


## Original Sources

- `docs/agents/pydantic_ai/AG-UI - Pydantic AI.md`
- `docs/agents/pydantic_ai/dbos/README.md`
- `docs/agents/pydantic_ai/KCG_SUMMARY.md`
- `docs/agents/pydantic_ai/MCP - Pydantic Logfire Documentation.md`
- `docs/agents/pydantic_ai/Pydantic AI Gateway - Pydantic AI.md`
- `docs/agents/smolagents/firecrawl-deepresearch/docs/blog-post.md`
- `docs/agents/smolagents/firecrawl-deepresearch/README.md`
- `docs/agents/smolagents/KCG_SUMMARY.md`
