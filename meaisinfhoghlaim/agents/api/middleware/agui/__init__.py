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
    # Event translation
    "AgentEvent",
    "EventTranslator",
    "translate_agent_events",
    # Session management
    "Message",
    "Session",
    "SessionManager",
    # Streaming agent
    "AGUIMessage",
    "AGUIRequest",
    "AGUIStateRequest",
    "AGUIStreamingAgent",
    "add_agui_endpoint",
    "create_agui_app",
    "encode_sse_event",
]
