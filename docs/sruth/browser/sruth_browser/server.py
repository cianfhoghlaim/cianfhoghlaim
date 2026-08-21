"""Unified server for browser agent stack.

Provides endpoints for:
- POST /chat    - TanStack AI SSE stream
- POST /agui    - AG-UI 17-event SSE
- POST /mcp     - MCP-UI JSON-RPC
- GET  /health  - Health check
"""

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from .backends.router import get_router
from .backends.selfhosted import (
    CDPBackend,
    Crawl4AIBackend,
    SkyvernBackend,
    StagehandBackend,
)
from .backends.paid import BrowserbaseBackend, FirecrawlBackend
from .core.config import get_config
from .frontend.adapters import AGUIAdapter, MCPUIAdapter, TanStackAdapter
from .frontend.unified_agent import get_browser_agent

logger = structlog.get_logger()


# Request models
class ChatRequest(BaseModel):
    """TanStack AI chat request."""

    messages: list[dict[str, Any]] | None = None
    message: str | None = None
    context: dict[str, Any] | None = None
    thread_id: str | None = None


class AGUIRequest(BaseModel):
    """AG-UI request."""

    messages: list[dict[str, Any]]
    threadId: str | None = None
    context: dict[str, Any] | None = None


class MCPRequest(BaseModel):
    """MCP-UI JSON-RPC request."""

    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any] | None = None
    id: str | int | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("starting_browser_agent_server")

    # Initialize backends
    config = get_config()
    router = get_router()

    # Register self-hosted backends
    try:
        cdp = CDPBackend(config)
        await cdp.initialize()
        router.register_backend(cdp)
    except Exception as e:
        logger.warning("cdp_init_failed", error=str(e))

    try:
        crawl4ai = Crawl4AIBackend(config)
        await crawl4ai.initialize()
        router.register_backend(crawl4ai)
    except Exception as e:
        logger.warning("crawl4ai_init_failed", error=str(e))

    try:
        skyvern = SkyvernBackend(config)
        await skyvern.initialize()
        router.register_backend(skyvern)
    except Exception as e:
        logger.warning("skyvern_init_failed", error=str(e))

    try:
        stagehand = StagehandBackend(config)
        await stagehand.initialize()
        router.register_backend(stagehand)
    except Exception as e:
        logger.warning("stagehand_init_failed", error=str(e))

    # Register paid backends if configured
    if config.has_firecrawl:
        try:
            firecrawl = FirecrawlBackend(config)
            await firecrawl.initialize()
            router.register_backend(firecrawl)
        except Exception as e:
            logger.warning("firecrawl_init_failed", error=str(e))

    if config.has_browserbase:
        try:
            browserbase = BrowserbaseBackend(config)
            await browserbase.initialize()
            router.register_backend(browserbase)
        except Exception as e:
            logger.warning("browserbase_init_failed", error=str(e))

    logger.info("browser_agent_server_started")

    yield

    logger.info("shutting_down_browser_agent_server")


def create_app() -> FastAPI:
    """Create the FastAPI application."""
    config = get_config()

    app = FastAPI(
        title="Browser Agent Stack",
        description="Self-hosted browser automation with ADK + Agno and paid fallback",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        router = get_router()
        health_status = router.get_all_health()

        return {
            "status": "healthy",
            "backends": [
                {
                    "name": h.backend.value,
                    "state": h.state.value,
                    "available": h.is_available,
                    "success_count": h.success_count,
                    "failure_count": h.failure_count,
                }
                for h in health_status
            ],
        }

    @app.post("/chat")
    async def chat(request: ChatRequest):
        """TanStack AI chat endpoint (SSE stream)."""
        agent = get_browser_agent()

        # Parse message
        message, context = TanStackAdapter.parse_request(request.model_dump())

        if not message:
            raise HTTPException(400, "No message provided")

        async def stream():
            async for event in agent.stream(message, request.thread_id, context):
                yield TanStackAdapter.format_event(event)

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    @app.post("/agui")
    async def agui(request: AGUIRequest):
        """AG-UI endpoint (17-event SSE stream)."""
        agent = get_browser_agent()

        # Parse message
        message, thread_id, context = AGUIAdapter.parse_request(request.model_dump())

        if not message:
            raise HTTPException(400, "No message provided")

        async def stream():
            async for event in agent.stream(message, thread_id or request.threadId, context):
                async for sse in AGUIAdapter.stream_response(iter([event])):
                    yield sse

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @app.get("/agui/info")
    async def agui_info():
        """AG-UI capabilities endpoint."""
        return AGUIAdapter.format_capabilities()

    @app.post("/mcp")
    async def mcp(request: MCPRequest):
        """MCP-UI JSON-RPC endpoint."""
        method, params, request_id = MCPUIAdapter.parse_request(request.model_dump())

        try:
            if method == "initialize":
                return MCPUIAdapter.format_response(
                    {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                            "resources": {},
                        },
                        "serverInfo": {
                            "name": "browser-agent",
                            "version": "0.1.0",
                        },
                    },
                    request_id,
                )

            elif method == "tools/list":
                return MCPUIAdapter.format_response(
                    {"tools": MCPUIAdapter.list_tools()},
                    request_id,
                )

            elif method == "resources/list":
                return MCPUIAdapter.format_response(
                    {"resources": MCPUIAdapter.list_resources()},
                    request_id,
                )

            elif method == "tools/call":
                tool_name = params.get("name") if isinstance(params, dict) else ""
                tool_args = params.get("arguments", {}) if isinstance(params, dict) else {}

                result = await _execute_tool(tool_name, tool_args)

                return MCPUIAdapter.format_response(
                    {"content": [{"type": "text", "text": json.dumps(result)}]},
                    request_id,
                )

            elif method == "resources/read":
                uri = params.get("uri") if isinstance(params, dict) else ""
                content = await _read_resource(uri)

                return MCPUIAdapter.format_response(
                    {"contents": [content]},
                    request_id,
                )

            elif method == "chat":
                agent = get_browser_agent()
                message = params if isinstance(params, str) else params.get("message", "")
                result = await agent.run(message)

                return MCPUIAdapter.format_response(
                    {"content": result},
                    request_id,
                )

            else:
                return MCPUIAdapter.format_error(
                    f"Unknown method: {method}",
                    -32601,
                    request_id,
                )

        except Exception as e:
            logger.error("mcp_error", method=method, error=str(e))
            return MCPUIAdapter.format_error(str(e), -32603, request_id)

    return app


async def _execute_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Execute an MCP tool."""
    from .tools import extraction, navigation, research, screenshot

    if name == "browser_extract":
        return await extraction.extract_page(
            args.get("url", ""),
            formats=args.get("formats", ["markdown"]),
        )

    elif name == "browser_navigate":
        return await navigation.navigate(args.get("url", ""))

    elif name == "browser_screenshot":
        return await screenshot.capture_screenshot(
            url=args.get("url"),
            full_page=args.get("fullPage", False),
        )

    elif name == "browser_research":
        return await research.deep_research(
            args.get("topic", ""),
            max_sources=args.get("maxSources", 15),
        )

    else:
        return {"error": f"Unknown tool: {name}"}


async def _read_resource(uri: str) -> dict[str, Any]:
    """Read an MCP resource."""
    if uri == "browser://health":
        router = get_router()
        health = router.get_all_health()
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps([h.model_dump() for h in health], default=str),
        }

    elif uri == "browser://history":
        agent = get_browser_agent()
        history = agent.event_bus.get_history()
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps([e.model_dump() for e in history[-100:]], default=str),
        }

    else:
        return {
            "uri": uri,
            "mimeType": "text/plain",
            "text": f"Unknown resource: {uri}",
        }


# Create default app
app = create_app()


def run_server():
    """Run the server."""
    import uvicorn

    config = get_config()
    uvicorn.run(
        "sruth_browser.server:app",
        host=config.server_host,
        port=config.server_port,
        reload=True,
    )


if __name__ == "__main__":
    run_server()
