"""
AG-UI Middleware for Oideachais.

Provides event translation and streaming support for AG-UI protocol integration.
Based on patterns from taighde/web/ag-ui/adk-middleware.
"""

from .event_translator import AgentEvent, EventTranslator, translate_agent_events
from .session_manager import Message, Session, SessionManager
from .streaming import (
    AGUIMessage,
    AGUIRequest,
    AGUIStateRequest,
    AGUIStreamingAgent,
    add_agui_endpoint,
    create_agui_app,
    encode_sse_event,
)

__all__ = [
    # Streaming agent
    "AGUIMessage",
    "AGUIRequest",
    "AGUIStateRequest",
    "AGUIStreamingAgent",
    # Event translation
    "AgentEvent",
    "EventTranslator",
    # Session management
    "Message",
    "Session",
    "SessionManager",
    "add_agui_endpoint",
    "create_agui_app",
    "encode_sse_event",
    "translate_agent_events",
]
