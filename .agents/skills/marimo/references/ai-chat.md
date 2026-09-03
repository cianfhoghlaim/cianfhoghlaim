# Marimo AI Chat (`mo.ui.chat` patterns)

The canonical "AI chat inside a marimo notebook" pattern.
Works with any OpenAI-compatible API (OpenAI, Z.ai, vLLM,
llama.cpp, Ollama) plus Pydantic AI / Agno / Google ADK.

## Pattern 1: Simple OpenAI chat

```python
import os
import marimo as mo


@app.cell
def _():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        mo.stop(not api_key, mo.md("Set OPENAI_API_KEY to use the chat."))
    return (api_key,)


@app.cell
def _():
    chat = mo.ui.chat(
        mo.ai.llm.openai(
            model="gpt-4o-mini",
            system_message="You are a curriculum assistant for the NCCA.",
        ),
        max_messages=20,
    )
    chat
    return (chat,)


@app.cell
def _():
    chat = _
    if chat.value:
        last = chat.value[-1]
        mo.md(f"**You:** {last.content}")
    return
```

## Pattern 2: Chat with attachments (image / PDF)

```python
@app.cell
def _():
    chat = mo.ui.chat(
        mo.ai.llm.openai(
            model="gpt-4o",  # vision-capable
            system_message="You are a receipt extractor.",
        ),
        allow_attachments=["image/png", "image/jpeg", "application/pdf"],
        max_messages=20,
    )
    chat
    return (chat,)


@app.cell
def _():
    chat = _
    if chat.value:
        for msg in chat.value[-3:]:
            mo.md(f"**{msg.role}:** {msg.content}")
            if msg.attachments:
                for att in msg.attachments:
                    mo.image(att.data)
    return
```

## Pattern 3: Pydantic AI chat

```python
from pydantic_ai import Agent
from pydantic_ai.ui.ag_ui import AGUIAdapter


@app.cell
def _():
    agent = Agent(
        model="openai:gpt-4o-mini",
        system_prompt="You are a curriculum assistant.",
    )
    adapter = AGUIAdapter(agent)
    return (adapter,)


@app.cell
def _():
    adapter = _
    chat = mo.ui.chat(adapter.as_starlette_app(), max_messages=20)
    chat
    return (chat,)
```

## Pattern 4: Agno team chat

```python
from agno.team import Team
from agno.models.openai.like import OpenAILike


@app.cell
def _():
    model = OpenAILike(
        id="glm-4.6",
        base_url="https://api.z.ai/v1",
        api_key=os.environ["Z_AI_API_KEY"],
    )
    team = Team(
        name="team",
        mode="coordinate",
        members=[curriculum_agent, translation_agent],
        model=model,
    )
    return (team,)


@app.cell
def _():
    team = _
    chat = mo.ui.chat(team.as_ag_ui(), max_messages=20)
    chat
    return (chat,)
```

## Pattern 5: Streaming with `mo.status.spinner`

```python
@app.cell
def _():
    with mo.status.spinner(title="Waiting for the LLM..."):
        chat = mo.ui.chat(
            mo.ai.llm.openai(model="gpt-4o-mini"),
            max_messages=20,
        )
    chat
    return (chat,)
```

## Pattern 6: Chat history persistence (Postgres)

```python
import psycopg2


@app.setup
def setup_history():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    return (conn,)


@app.cell
def _():
    conn = _
    chat = mo.ui.chat(
        mo.ai.llm.openai(model="gpt-4o-mini"),
        history_table="chat_history",  # marimo persists to this table
    )
    chat
    return (chat,)
```

## KCG conventions

- All marimo AI chats MUST have an `OPENAI_API_KEY` (or
  `Z_AI_API_KEY`) gate at the top (use `mo.stop(not key, ...)`)
- Multimodal chats use `gpt-4o` (vision-capable)
- Text-only chats use `gpt-4o-mini` (cost-effective)
- Z.ai GLM-4.6 via `OpenAILike` is the cost-effective
  alternative for non-stakes chats
- The `max_messages` parameter limits context window
  (default 20 is a good starting point)

## Resources

- Marimo AI: <https://docs.marimo.io/ai/>
- OpenAI: <https://platform.openai.com/docs>
- Z.ai: <https://docs.z.ai/>
- Pydantic AI: <https://ai.pydantic.dev/>
- Agno: <https://docs.agno.com/>
