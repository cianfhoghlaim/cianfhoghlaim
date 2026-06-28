"""
CopilotKit/AG-UI Agent Routes with Full AG-UI Protocol.

Server-Sent Events (SSE) streaming for AI agent interactions.
Implements complete 17-event AG-UI protocol for CopilotKit integration.
Integrates with Celtic tutor and mythology narrator agents.

AG-UI Protocol Events (17 total):
- Lifecycle: RUN_STARTED, RUN_FINISHED, RUN_ERROR, STEP_STARTED, STEP_FINISHED
- Messages: TEXT_MESSAGE_START, TEXT_MESSAGE_CONTENT, TEXT_MESSAGE_END
- Tools: TOOL_CALL_START, TOOL_CALL_ARGS, TOOL_CALL_END, TOOL_RESULT
- State: STATE_SNAPSHOT, STATE_DELTA, MESSAGES_SNAPSHOT
- Special: RAW, CUSTOM
"""

import asyncio
import json
import time
import uuid
from collections.abc import AsyncGenerator
from enum import StrEnum

from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..ag_ui_protocol import (
    AGUIEventEmitter,
    GameProgressState,
)
from .auth import get_session_from_header
from .payments import check_payment_or_free, create_402_response

# Import orchestrator for actual LLM-powered responses
try:
    from ...agents.orchestrator import TuathAgentOrchestrator, get_orchestrator

    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    get_orchestrator = None
    TuathAgentOrchestrator = None

router = APIRouter()


class AgentType(StrEnum):
    """Available agent types."""
    CELTIC_TUTOR = "celtic_tutor"
    QUEST_GUIDE = "quest_guide"
    MYTHOLOGY_NARRATOR = "mythology_narrator"
    RESEARCH_ASSISTANT = "research_assistant"


class A2UIEventType(StrEnum):
    """Legacy A2UI Protocol event types (deprecated - use AGUIEventType)."""
    LIFECYCLE_START = "lifecycle.start"
    LIFECYCLE_COMPLETE = "lifecycle.complete"
    LIFECYCLE_ERROR = "lifecycle.error"
    STATE_SNAPSHOT = "state.snapshot"
    STATE_DELTA = "state.delta"
    TOOL_CALL_START = "tool.call.start"
    TOOL_CALL_RESULT = "tool.call.result"
    RENDER_COMPONENT = "render.component"
    MESSAGE_DELTA = "message.delta"
    MESSAGE_COMPLETE = "message.complete"


# Game progress state for tracking player progression
_game_states: dict[str, GameProgressState] = {}


class AgentState(BaseModel):
    """Agent state for A2UI protocol."""
    agent_type: AgentType
    conversation_id: str
    language: str = "ga"
    language_level: str = "beginner"
    current_quest: str | None = None
    current_zone: str | None = None
    vocabulary_learned: list[str] = Field(default_factory=list)
    xp_earned: int = 0
    tools_available: list[str] = Field(default_factory=list)


class RenderComponent(BaseModel):
    """A2UI render component specification."""
    component: str  # Component name (VocabularyCard, QuestProgress, etc.)
    props: dict = Field(default_factory=dict)
    slot: str = "main"  # UI slot (main, sidebar, overlay)


class ToolCall(BaseModel):
    """Tool call specification."""
    tool_name: str
    tool_id: str
    parameters: dict = Field(default_factory=dict)


class AgentMessage(BaseModel):
    """Message to the agent."""

    content: str
    language: str = "en"  # Target Celtic language (ga, gd, cy) or en
    context: dict | None = None


class AgentEvent(BaseModel):
    """SSE event from agent."""

    event: str
    data: dict


class ConversationContext(BaseModel):
    """Conversation context for agent."""

    player_id: str | None = None
    current_zone: str | None = None
    current_quest: str | None = None
    language_level: str = "beginner"
    preferred_language: str = "ga"


# In-memory conversation storage
_conversations: dict[str, list[dict]] = {}
_agent_states: dict[str, AgentState] = {}


@router.post("/agent")
async def agent_endpoint(
    request: Request,
    x_session_id: str | None = Header(None),
    x_payment_id: str | None = Header(None),
):
    """
    Main agent endpoint with SSE streaming.

    Supports AG-UI protocol for CopilotKit integration.
    """
    # Check payment or free usage
    if not check_payment_or_free(x_session_id, "chat_message", x_payment_id):
        return create_402_response("chat_message")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON body",
        )

    messages = body.get("messages", [])
    context = body.get("context", {})
    conversation_id = body.get("conversation_id", str(uuid.uuid4()))

    # Get session info
    session = get_session_from_header(x_session_id) if x_session_id else None
    player_id = session.get("player_id") if session else None

    # Check if orchestrator is available for LLM-powered responses
    use_orchestrator = body.get("use_llm", False) and ORCHESTRATOR_AVAILABLE

    if use_orchestrator:
        return StreamingResponse(
            generate_orchestrator_response(messages, context, conversation_id, player_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    return StreamingResponse(
        generate_agent_response(messages, context, conversation_id, player_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/agent/llm")
async def agent_llm_endpoint(
    request: Request,
    x_session_id: str | None = Header(None),
    x_payment_id: str | None = Header(None),
):
    """
    LLM-powered agent endpoint with SSE streaming.

    Uses the TuathAgentOrchestrator for actual LLM calls via ADK.
    Falls back to template responses if ADK is unavailable.
    """
    if not check_payment_or_free(x_session_id, "chat_message", x_payment_id):
        return create_402_response("chat_message")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON body",
        )

    messages = body.get("messages", [])
    context = body.get("context", {})
    conversation_id = body.get("conversation_id", str(uuid.uuid4()))

    session = get_session_from_header(x_session_id) if x_session_id else None
    player_id = session.get("player_id") if session else None

    return StreamingResponse(
        generate_orchestrator_response(messages, context, conversation_id, player_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def generate_orchestrator_response(
    messages: list[dict],
    context: dict,
    conversation_id: str,
    player_id: str | None,
) -> AsyncGenerator[str]:
    """Generate LLM-powered responses using the TuathAgentOrchestrator.

    Streams AG-UI protocol events from actual ADK agent execution.
    """
    # Get the last user message
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break

    # Build game state context
    game_state = {
        "player_id": player_id,
        "current_quest": context.get("current_quest"),
        "current_zone": context.get("current_zone"),
        "language_level": context.get("language_level", "beginner"),
        "preferred_language": context.get("preferred_language", "ga"),
    }

    if ORCHESTRATOR_AVAILABLE and get_orchestrator:
        orchestrator = get_orchestrator()

        # Stream events from orchestrator
        async for event in orchestrator.process_request(
            message=user_message,
            thread_id=conversation_id,
            context=context,
            game_state=game_state,
        ):
            # Convert orchestrator events to SSE format
            yield f"data: {json.dumps(event)}\n\n"
    else:
        # Fallback to template response
        async for sse_event in generate_agent_response(
            messages, context, conversation_id, player_id
        ):
            yield sse_event


async def generate_agent_response(
    messages: list[dict],
    context: dict,
    conversation_id: str,
    player_id: str | None,
) -> AsyncGenerator[str]:
    """Generate AG-UI protocol SSE events for agent response.

    Uses the full 17-event AG-UI protocol for CopilotKit integration.
    """
    start_time = time.time()

    # Initialize AG-UI event emitter
    emitter = AGUIEventEmitter(
        run_id=str(uuid.uuid4()),
        thread_id=conversation_id,
    )

    # Initialize game progress state
    if conversation_id not in _game_states:
        _game_states[conversation_id] = GameProgressState()
    game_state = _game_states[conversation_id]

    # Store conversation
    if conversation_id not in _conversations:
        _conversations[conversation_id] = []
    _conversations[conversation_id].extend(messages)

    # Get the last user message
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break

    # Determine which agent to use based on context and message
    agent_type = classify_message(user_message, context)

    # Initialize or get agent state
    agent_state = _agent_states.get(conversation_id, AgentState(
        agent_type=AgentType(agent_type),
        conversation_id=conversation_id,
        language=context.get("preferred_language", "ga"),
        language_level=context.get("language_level", "beginner"),
        current_quest=context.get("current_quest"),
        current_zone=context.get("current_zone"),
        tools_available=["curriculum_search", "mythology_query", "translation"],
    ))
    _agent_states[conversation_id] = agent_state

    # AG-UI: RUN_STARTED event
    yield emitter.run_started(
        agent_name=agent_type,
        input_message=user_message,
        metadata={
            "language": agent_state.language,
            "language_level": agent_state.language_level,
            "player_id": player_id,
        },
    ).to_sse()

    # AG-UI: STATE_SNAPSHOT event with full agent and game state
    yield emitter.state_snapshot(
        state={
            "agent": agent_state.model_dump(),
            "game": game_state.to_dict(),
        }
    ).to_sse()

    # AG-UI: STEP_STARTED for tool execution
    step_start = emitter.step_started(step_name="tool_execution", step_type="tool")
    yield step_start.to_sse()
    tool_step_start = time.time()

    # AG-UI: Tool calls based on agent type
    if agent_type == "celtic_tutor":
        # TOOL_CALL_START
        yield emitter.tool_call_start("curriculum_search").to_sse()

        # TOOL_CALL_ARGS
        yield emitter.tool_call_args(
            args={"query": user_message, "language": agent_state.language}
        ).to_sse()

        await asyncio.sleep(0.1)  # Simulate tool execution

        # TOOL_CALL_END
        yield emitter.tool_call_end("curriculum_search").to_sse()

        # TOOL_RESULT
        yield emitter.tool_result(
            tool_name="curriculum_search",
            result={"found": True, "topics": ["greetings", "grammar", "vocabulary"]},
            duration_ms=int((time.time() - tool_step_start) * 1000),
        ).to_sse()

    elif agent_type == "mythology_narrator":
        yield emitter.tool_call_start("mythology_query").to_sse()
        yield emitter.tool_call_args(
            args={"query": user_message, "tradition": "irish"}
        ).to_sse()
        await asyncio.sleep(0.1)
        yield emitter.tool_call_end("mythology_query").to_sse()
        yield emitter.tool_result(
            tool_name="mythology_query",
            result={"found": True, "entities": ["Tuatha Dé Danann", "Lugh"]},
            duration_ms=int((time.time() - tool_step_start) * 1000),
        ).to_sse()

    elif agent_type == "quest_guide":
        yield emitter.tool_call_start("quest_lookup").to_sse()
        yield emitter.tool_call_args(
            args={"quest_id": context.get("current_quest", "tutorial")}
        ).to_sse()
        await asyncio.sleep(0.1)
        yield emitter.tool_call_end("quest_lookup").to_sse()
        yield emitter.tool_result(
            tool_name="quest_lookup",
            result={"quest": "First Words", "step": 1, "total_steps": 5},
            duration_ms=int((time.time() - tool_step_start) * 1000),
        ).to_sse()

    # AG-UI: STEP_FINISHED for tool execution
    yield emitter.step_finished(
        step_id=step_start.step_id,
        step_name="tool_execution",
        duration_ms=int((time.time() - tool_step_start) * 1000),
    ).to_sse()

    # AG-UI: Custom event for A2UI render components (game-specific)
    render_components = get_render_components(agent_type, context, user_message)
    for component in render_components:
        yield emitter.custom(
            event_name="render_component",
            payload={
                "component": component.component,
                "props": component.props,
                "slot": component.slot,
            },
        ).to_sse()

    # Generate response based on agent type
    response_content = await generate_response_content(
        agent_type, user_message, context, player_id
    )

    # AG-UI: TEXT_MESSAGE_START
    yield emitter.text_message_start(role="assistant").to_sse()

    # AG-UI: TEXT_MESSAGE_CONTENT (streaming chunks)
    for chunk in chunk_response(response_content):
        yield emitter.text_message_content(delta=chunk).to_sse()
        await asyncio.sleep(0.02)

    # AG-UI: TEXT_MESSAGE_END
    yield emitter.text_message_end().to_sse()

    # Update game state based on response
    new_vocab = extract_vocabulary(response_content, agent_state.language)
    for word in new_vocab[:3]:
        delta = game_state.update_from_event({
            "type": "vocabulary_learned",
            "word": word,
            "xp": 5,
        })
        if delta:
            yield emitter.state_delta(delta=delta, operation="merge").to_sse()

    # Update agent state
    agent_state.xp_earned += 10
    if new_vocab:
        agent_state.vocabulary_learned.extend(new_vocab[:3])

    # AG-UI: STATE_DELTA for updated state
    yield emitter.state_delta(
        delta={
            "xp_earned": agent_state.xp_earned,
            "vocabulary_learned": new_vocab[:3] if new_vocab else [],
            "game": game_state.to_dict(),
        },
        operation="merge",
    ).to_sse()

    # AG-UI: MESSAGES_SNAPSHOT with conversation history
    yield emitter.messages_snapshot(
        messages=_conversations.get(conversation_id, [])[-10:]  # Last 10 messages
    ).to_sse()

    # Calculate total duration
    duration_ms = int((time.time() - start_time) * 1000)

    # AG-UI: RUN_FINISHED event
    yield emitter.run_finished(
        output=response_content[:100] + "..." if len(response_content) > 100 else response_content,
        duration_ms=duration_ms,
        token_usage={"input": len(user_message.split()), "output": len(response_content.split())},
    ).to_sse()


def get_render_components(
    agent_type: str,
    context: dict,
    message: str
) -> list[RenderComponent]:
    """Get A2UI render components based on agent type."""
    components = []

    if agent_type == "celtic_tutor":
        # Vocabulary flashcard component
        components.append(RenderComponent(
            component="VocabularyCard",
            props={
                "language": context.get("preferred_language", "ga"),
                "level": context.get("language_level", "beginner"),
                "topic": "greetings",
            },
            slot="sidebar",
        ))

        # Grammar explainer component
        components.append(RenderComponent(
            component="GrammarExplainer",
            props={
                "language": context.get("preferred_language", "ga"),
                "topic": "word_order",
            },
            slot="main",
        ))

    elif agent_type == "quest_guide":
        # Quest progress component
        components.append(RenderComponent(
            component="QuestProgress",
            props={
                "quest_id": context.get("current_quest", "tutorial_greetings"),
                "current_step": 1,
                "total_steps": 5,
            },
            slot="sidebar",
        ))

        # Map marker component
        components.append(RenderComponent(
            component="MapMarker",
            props={
                "zone": context.get("current_zone", "village_center"),
                "target": "village_elder",
            },
            slot="overlay",
        ))

    elif agent_type == "mythology_narrator":
        # Character card component
        components.append(RenderComponent(
            component="CharacterCard",
            props={
                "character": "lugh",
                "tradition": "irish_mythology",
                "show_relationships": True,
            },
            slot="sidebar",
        ))

        # Story timeline component
        components.append(RenderComponent(
            component="StoryTimeline",
            props={
                "cycle": "mythological_cycle",
                "highlight": "four_treasures",
            },
            slot="main",
        ))

    return components


def extract_vocabulary(content: str, language: str) -> list[str]:
    """Extract vocabulary words from response content."""
    # Simple extraction of Irish words from the response
    irish_words = []

    # Common vocabulary patterns
    vocab_patterns = {
        "ga": [
            "Dia duit", "Slán", "Go raibh maith agat", "Fáilte",
            "Tuatha Dé Danann", "Tír na nÓg", "Fianna",
        ],
        "cy": ["Bore da", "Nos da", "Diolch", "Croeso"],
        "gd": ["Madainn mhath", "Oidhche mhath", "Tapadh leat"],
    }

    patterns = vocab_patterns.get(language, vocab_patterns["ga"])
    for word in patterns:
        if word.lower() in content.lower():
            irish_words.append(word)

    return irish_words


def format_a2ui_event(event_type: A2UIEventType, data: dict) -> str:
    """Format data as A2UI SSE event."""
    return f"event: {event_type.value}\ndata: {json.dumps(data)}\n\n"


def classify_message(message: str, context: dict) -> str:
    """Classify message to determine appropriate agent."""
    message_lower = message.lower()

    # Language learning keywords
    if any(kw in message_lower for kw in [
        "translate", "how do you say", "what does", "mean",
        "grammar", "vocabulary", "word", "phrase", "learn",
        "gaeilge", "gàidhlig", "cymraeg", "pronunciation"
    ]):
        return "celtic_tutor"

    # Quest keywords
    if any(kw in message_lower for kw in [
        "quest", "mission", "objective", "complete", "find",
        "where", "how do i", "next step", "hint", "help me", "stuck"
    ]):
        return "quest_guide"

    # Mythology keywords
    if any(kw in message_lower for kw in [
        "story", "legend", "myth", "who is", "tell me about",
        "lore", "character", "hero", "god", "goddess",
        "tuatha", "fianna", "mabinogion", "cú chulainn"
    ]):
        return "mythology_narrator"

    # Default to research
    return "research_assistant"


async def generate_response_content(
    agent_type: str,
    message: str,
    context: dict,
    player_id: str | None,
) -> str:
    """Generate response content based on agent type."""

    # Get language preference
    target_language = context.get("preferred_language", "ga")
    language_level = context.get("language_level", "beginner")

    if agent_type == "celtic_tutor":
        return generate_tutor_response(message, target_language, language_level)
    elif agent_type == "quest_guide":
        return generate_quest_response(message, context, player_id)
    elif agent_type == "mythology_narrator":
        return generate_mythology_response(message, target_language)
    else:
        return generate_research_response(message, target_language)


def generate_tutor_response(
    message: str,
    target_language: str,
    level: str,
) -> str:
    """Generate Celtic tutor response."""
    language_names = {
        "ga": ("Irish", "Gaeilge"),
        "gd": ("Scottish Gaelic", "Gàidhlig"),
        "cy": ("Welsh", "Cymraeg"),
    }

    lang_en, lang_native = language_names.get(target_language, ("Irish", "Gaeilge"))

    # Simple response generation (would use ADK agent in production)
    response = f"""## {lang_native} Learning

I'll help you learn {lang_en}!

### Common Greetings

| {lang_en} | English | Pronunciation |
|-----------|---------|---------------|
| Dia duit | Hello | DEE-ah gwit |
| Slán | Goodbye | slawn |
| Go raibh maith agat | Thank you | guh rev mah ah-gut |

### Grammar Note
In {lang_en}, the word order is Verb-Subject-Object (VSO), different from English!

**Example:**
- *Tá mé go maith* (I am well)
- Literally: "Is me good"

### Practice
Try saying: "Dia duit! Conas atá tú?" (Hello! How are you?)

Go n-éirí leat! (Good luck!)
"""
    return response


def generate_quest_response(
    message: str,
    context: dict,
    player_id: str | None,
) -> str:
    """Generate quest guide response."""
    context.get("current_quest", "tutorial_greetings")

    response = """## Quest Guidance

**Current Quest:** First Words
**Objective:** Learn basic greetings in Irish

### Current Objective
Talk to the village elder near the standing stones.

### Hint Level 1
Look for an elder wearing green near the central fire. The standing stones mark the village center.

### Learning Connection
This quest teaches you basic Irish greetings, connecting to Primary Irish curriculum outcomes L1-3 (oral communication).

### Key Vocabulary
- **Dia duit** (DEE-ah gwit) - Hello
- **Fáilte** (FAWL-che) - Welcome
- **Sráidbhaile** (STRAWJ-val-eh) - Village

Lean ar aghaidh! (Keep going!)
"""
    return response


def generate_mythology_response(
    message: str,
    target_language: str,
) -> str:
    """Generate mythology narrator response."""
    response = """## The Tuatha Dé Danann

*The mist parts to reveal ancient wisdom...*

**Lugh Lámhfhada** speaks:

> "A chara, welcome to the lands of the Tuatha Dé Danann. We are the divine race who came from the northern islands, bringing with us four great treasures."

### The Four Treasures

1. **Lia Fáil** - The Stone of Destiny (screams for the true king)
2. **Claíomh Solais** - The Sword of Light (Nuada's invincible blade)
3. **Sleá Bua** - The Spear of Victory (Lugh's unstoppable weapon)
4. **Coire Dagda** - The Cauldron of Plenty (never empties)

### Celtic Terms

| Irish | Meaning |
|-------|---------|
| Tuatha Dé Danann | Peoples of the goddess Danu |
| Lámhfhada | Long-arm (of the long arm) |
| Samildánach | Many-skilled |

*"Learn our stories, young one, and carry the wisdom of ages..."*
"""
    return response


def generate_research_response(
    message: str,
    target_language: str,
) -> str:
    """Generate research assistant response."""
    response = """## Celtic Language Research

### Language Family Overview

The Celtic languages form a branch of Indo-European, divided into two groups:

**Goidelic (Q-Celtic):**
- Irish (Gaeilge) - ~1.7 million speakers
- Scottish Gaelic (Gàidhlig) - ~57,000 speakers
- Manx (Gaelg) - revived language

**Brythonic (P-Celtic):**
- Welsh (Cymraeg) - ~560,000 speakers
- Breton (Brezhoneg) - ~200,000 speakers
- Cornish (Kernewek) - revived language

### Key Linguistic Features

1. **Initial Consonant Mutations** - Consonants change based on grammatical context
2. **VSO Word Order** - Verb comes first
3. **Inflected Prepositions** - Prepositions conjugate like verbs
4. **Two Types of "to be"** - Copula vs. substantive verb

### Comparative Example

| English | Irish | Welsh | Scottish Gaelic |
|---------|-------|-------|-----------------|
| head | ceann | pen | ceann |
| four | ceathair | pedwar | ceithir |

The P-Celtic/Q-Celtic split shows in "four" - *kʷ* became *p* in Brythonic but *k* in Goidelic.
"""
    return response


def chunk_response(content: str, chunk_size: int = 20) -> list[str]:
    """Split response into chunks for streaming."""
    words = content.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= chunk_size:
            chunks.append(" ".join(current_chunk) + " ")
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def format_sse_event(event_type: str, data: dict) -> str:
    """Format data as SSE event."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    x_session_id: str | None = Header(None),
):
    """Get conversation history."""
    if conversation_id not in _conversations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return {
        "conversation_id": conversation_id,
        "messages": _conversations[conversation_id],
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    x_session_id: str | None = Header(None),
):
    """Delete a conversation."""
    _conversations.pop(conversation_id, None)

    return {"success": True}


@router.get("/state/{conversation_id}")
async def get_agent_state(
    conversation_id: str,
    x_session_id: str | None = Header(None),
):
    """Get agent state for a conversation (A2UI protocol)."""
    if conversation_id not in _agent_states:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent state not found",
        )

    return {
        "conversation_id": conversation_id,
        "state": _agent_states[conversation_id].model_dump(),
    }


@router.post("/state/{conversation_id}")
async def update_agent_state(
    conversation_id: str,
    request: Request,
    x_session_id: str | None = Header(None),
):
    """Update agent state (A2UI protocol)."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON body",
        )

    if conversation_id not in _agent_states:
        # Create new state
        _agent_states[conversation_id] = AgentState(
            agent_type=AgentType(body.get("agent_type", "celtic_tutor")),
            conversation_id=conversation_id,
            language=body.get("language", "ga"),
            language_level=body.get("language_level", "beginner"),
        )

    # Update existing state with provided fields
    state = _agent_states[conversation_id]
    for key, value in body.items():
        if hasattr(state, key) and key not in ["agent_type", "conversation_id"]:
            setattr(state, key, value)

    return {
        "success": True,
        "state": state.model_dump(),
    }


@router.get("/agents")
async def list_agents():
    """List available agents and their capabilities."""
    return {
        "agents": [
            {
                "type": "celtic_tutor",
                "name": "Celtic Tutor",
                "description": "Language learning assistant for Irish, Welsh, and Scottish Gaelic",
                "capabilities": ["vocabulary", "grammar", "pronunciation", "translation"],
                "tools": ["curriculum_search", "translation", "pronunciation_guide"],
            },
            {
                "type": "quest_guide",
                "name": "Quest Guide",
                "description": "Helps with game quests and objectives",
                "capabilities": ["quest_hints", "navigation", "progress_tracking"],
                "tools": ["quest_lookup", "map_marker", "objective_tracker"],
            },
            {
                "type": "mythology_narrator",
                "name": "Mythology Narrator",
                "description": "Tells Celtic myths and legends",
                "capabilities": ["storytelling", "character_lore", "history"],
                "tools": ["mythology_query", "character_lookup", "story_search"],
            },
            {
                "type": "research_assistant",
                "name": "Research Assistant",
                "description": "General research on Celtic languages and culture",
                "capabilities": ["research", "comparison", "etymology"],
                "tools": ["knowledge_search", "curriculum_search", "web_search"],
            },
        ],
        "supported_languages": [
            {"code": "ga", "name": "Irish", "native": "Gaeilge"},
            {"code": "cy", "name": "Welsh", "native": "Cymraeg"},
            {"code": "gd", "name": "Scottish Gaelic", "native": "Gàidhlig"},
        ],
    }
