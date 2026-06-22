"""
Agent Routes for Crypteolas API.

Provides AG-UI SSE streaming endpoint for CopilotKit integration.
"""

import json
from typing import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import structlog

from agents.adk.root_agent import app as agent_app  # type: ignore

logger = structlog.get_logger()

router = APIRouter()


async def generate_sse_events(
    request_body: dict,
) -> AsyncGenerator[dict, None]:
    """
    Generate SSE events from agent execution.

    Implements AG-UI protocol for CopilotKit.
    """
    try:
        # Extract messages from request
        messages = request_body.get("messages", [])
        if not messages:
            yield {"event": "error", "data": json.dumps({"error": "No messages provided"})}
            return

        # Get the latest user message
        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        if not user_message:
            yield {"event": "error", "data": json.dumps({"error": "No user message found"})}
            return

        logger.info("Processing agent request", message=user_message[:100])

        # Send start event
        yield {
            "event": "start",
            "data": json.dumps({"type": "start"}),
        }

        # Execute agent
        try:
            # Run the agent with the user message
            result = await agent_app.run_async(user_message)

            # Stream the response
            response_text = result.get("response", "") if isinstance(result, dict) else str(result)

            # Send text delta events
            yield {
                "event": "textDelta",
                "data": json.dumps({
                    "type": "textDelta",
                    "delta": response_text,
                }),
            }

        except Exception as e:
            logger.error("Agent execution error", error=str(e))
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }
            return

        # Send done event
        yield {
            "event": "done",
            "data": json.dumps({"type": "done"}),
        }

    except Exception as e:
        logger.error("SSE generation error", error=str(e))
        yield {
            "event": "error",
            "data": json.dumps({"error": str(e)}),
        }


@router.post("/sse")
async def agent_sse(request: Request):
    """
    AG-UI SSE streaming endpoint.

    Implements Server-Sent Events for CopilotKit integration.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    return EventSourceResponse(
        generate_sse_events(body),
        media_type="text/event-stream",
    )


@router.post("/chat")
async def agent_chat(request: Request):
    """
    Non-streaming chat endpoint.

    Returns complete response in JSON format.
    """
    try:
        body = await request.json()
        messages = body.get("messages", [])

        # Get the latest user message
        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        if not user_message:
            return {"error": "No user message found"}

        # Execute agent
        result = await agent_app.run_async(user_message)

        return {
            "response": result.get("response", "") if isinstance(result, dict) else str(result),
            "status": "success",
        }

    except Exception as e:
        logger.error("Chat error", error=str(e))
        return {"error": str(e), "status": "error"}
