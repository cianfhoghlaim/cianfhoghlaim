"""
AG-UI Curriculum Agent FastAPI Endpoint.

Provides the SSE streaming endpoint for the curriculum assistant.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the AG-UI ADK middleware
try:
    from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
    HAS_AG_UI_ADK = True
except ImportError:
    HAS_AG_UI_ADK = False
    print("Warning: ag_ui_adk not installed, using fallback")

from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai import types as genai_types

from ..adk.config import config, CURRICULUM_FRAMEWORKS
from ..tools.curriculum_search import (
    search_curriculum,
    find_similar_content,
    compare_curricula,
    get_learning_outcomes,
)


# --- Agent Tools ---
async def search_curriculum_hybrid(
    query: str,
    nations: list[str] | None = None,
    levels: list[str] | None = None,
    subjects: list[str] | None = None,
    limit: int = 20,
) -> dict:
    """
    Search curriculum content with hybrid vector + keyword matching.

    Args:
        query: Search query text
        nations: Filter by nations (ireland, england, scotland, wales, northern_ireland)
        levels: Filter by education levels
        subjects: Filter by subjects
        limit: Max results to return

    Returns:
        Search results with STATE_SNAPSHOT event
    """
    results = await search_curriculum(
        query=query,
        nations=nations,
        levels=levels,
        subjects=subjects,
        limit=limit,
    )

    return {
        "results": results,
        "query": query,
        "count": len(results),
    }


async def compare_curricula_cross_nation(
    subject: str,
    nations: list[str],
    level: str | None = None,
) -> dict:
    """
    Compare curriculum coverage across nations.

    Args:
        subject: Subject to compare (e.g., Mathematics, Science)
        nations: List of nations to compare
        level: Optional education level filter

    Returns:
        Comparison table with alignment scores
    """
    comparison = await compare_curricula(
        subject=subject,
        nations=nations,
        level=level,
    )

    return comparison


async def request_translation_approval(
    source_text: str,
    source_language: str,
    target_language: str,
    domain: str = "curriculum",
) -> dict:
    """
    Request human-in-the-loop approval for Celtic language translation.

    This is a long-running tool that pauses agent execution until
    the user approves or rejects the translation.

    Args:
        source_text: Text to translate
        source_language: Source language code (en)
        target_language: Target language code (ga, cy, gd, gv)
        domain: Translation domain for terminology

    Returns:
        Translation request details for HITL approval
    """
    import uuid

    # Placeholder translation - would call actual translation service
    translated_text = f"[Translation of '{source_text[:50]}...' to {target_language}]"
    confidence = 0.85

    return {
        "translation_id": str(uuid.uuid4()),
        "source_language": source_language,
        "target_language": target_language,
        "source_text": source_text,
        "translated_text": translated_text,
        "domain": domain,
        "confidence": confidence,
        "needs_review": confidence < 0.9,
        "requires_approval": True,
    }


# --- Agent Definition ---
import datetime

CURRICULUM_AGENT_INSTRUCTION = f"""
You are a curriculum assistant for the Celtic Education Platform.

**YOUR CAPABILITIES:**
1. Search curriculum content across 5 nations (Ireland, England, Scotland, Wales, NI)
2. Compare learning outcomes and topics across nations
3. Find equivalent content in different curricula
4. Support Celtic language translations (Irish, Welsh, Scottish Gaelic)

**TOOLS:**
- `search_curriculum_hybrid`: Find curriculum content by topic, nation, level
- `compare_curricula_cross_nation`: Compare a subject across nations
- `request_translation_approval`: Request translation for Celtic languages

**CURRICULUM FRAMEWORKS:**
{CURRICULUM_FRAMEWORKS}

**AGE/STAGE REFERENCE:**
| Age | Ireland | England | Scotland | Wales | NI |
|-----|---------|---------|----------|-------|-----|
| 12-15 | Junior Cycle | KS3/4 | Third/Fourth | KS3/4 | KS3/4 |
| 15-16 | Junior Cert | GCSE | National 5 | GCSE | GCSE |
| 16-18 | Senior Cycle | A-Level | Higher | A-Level | A-Level |

**RESPONSE FORMAT:**
- Start with a brief answer to the user's question
- Reference specific curriculum outcomes by code when possible
- Highlight Celtic language provisions when relevant
- Note cross-nation equivalencies

Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
"""

# Create the ADK agent
curriculum_llm_agent = LlmAgent(
    name="curriculum_assistant",
    model=config.model_name,
    description="Pan-Celtic curriculum assistant with cross-nation comparison capabilities.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction=CURRICULUM_AGENT_INSTRUCTION,
    tools=[
        search_curriculum_hybrid,
        compare_curricula_cross_nation,
        request_translation_approval,
    ],
    output_key="curriculum_response",
)


def create_curriculum_app() -> FastAPI:
    """Create FastAPI app with AG-UI curriculum endpoint."""
    app = FastAPI(
        title="Celtic Curriculum AG-UI Agent",
        description="Pan-Celtic curriculum comparison and search agent",
        version="1.0.0",
    )

    # Add CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if HAS_AG_UI_ADK:
        # Create AG-UI ADK agent wrapper
        adk_agent = ADKAgent(
            adk_agent=curriculum_llm_agent,
            app_name="cianfhoghlaim_curriculum",
            user_id="demo_user",
            session_timeout_seconds=3600,
            use_in_memory_services=True,
            emit_messages_snapshot=True,
        )

        # Add the AG-UI endpoint
        add_adk_fastapi_endpoint(app, adk_agent, path="/api/agent")
    else:
        # Fallback simple endpoint
        from fastapi import Request
        from fastapi.responses import StreamingResponse
        import json
        import asyncio

        @app.post("/api/agent")
        async def agent_endpoint(request: Request):
            """Fallback AG-UI endpoint without full middleware."""
            body = await request.json()

            async def event_stream():
                # Emit RUN_STARTED
                yield f"event: RUN_STARTED\n"
                yield f"data: {json.dumps({'run_id': body.get('run_id', 'fallback')})}\n\n"

                # Emit simple response
                yield f"event: TEXT_MESSAGE_START\n"
                yield f"data: {json.dumps({'message_id': 'msg_1'})}\n\n"

                response = "I'm the Celtic Curriculum Assistant. I can help you search and compare curricula across Ireland, England, Scotland, Wales, and Northern Ireland. Ask me about specific subjects, levels, or topics!"

                for chunk in [response[i:i+50] for i in range(0, len(response), 50)]:
                    yield f"event: TEXT_MESSAGE_CONTENT\n"
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                    await asyncio.sleep(0.05)

                yield f"event: TEXT_MESSAGE_END\n"
                yield f"data: {json.dumps({})}\n\n"

                yield f"event: RUN_FINISHED\n"
                yield f"data: {json.dumps({'status': 'success'})}\n\n"

            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )

    @app.get("/health")
    async def health():
        return {"status": "healthy", "ag_ui_adk": HAS_AG_UI_ADK}

    return app


# Create the app instance
app = create_curriculum_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "curriculum_endpoint:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
