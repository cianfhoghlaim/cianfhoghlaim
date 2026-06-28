"""Unified frontend adapters for browser agent stack.

Supports three protocols:
- TanStack AI: SSE streaming at /chat
- MCP-UI: JSON-RPC at /mcp
- AG-UI: 17-event SSE at /agui

Real-time persistence via Convex:
- Thread/message history
- Event streaming
- Workflow tracking
"""

from .adapters import AGUIAdapter, MCPUIAdapter, TanStackAdapter
from .convex_client import (
    ConvexClient,
    ConvexEventBridge,
    ConvexMessage,
    ConvexThread,
    get_convex_client,
    init_convex,
)
from .event_bus import AgentEvent, EventBus, EventType
from .unified_agent import UnifiedBrowserAgent, get_browser_agent

__all__ = [
    # Unified agent
    "UnifiedBrowserAgent",
    "get_browser_agent",
    # Event bus
    "EventBus",
    "EventType",
    "AgentEvent",
    # Protocol adapters
    "TanStackAdapter",
    "MCPUIAdapter",
    "AGUIAdapter",
    # Convex real-time
    "ConvexClient",
    "ConvexThread",
    "ConvexMessage",
    "ConvexEventBridge",
    "get_convex_client",
    "init_convex",
]
