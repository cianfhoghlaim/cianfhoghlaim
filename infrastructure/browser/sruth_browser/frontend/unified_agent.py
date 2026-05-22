"""Unified browser agent for all frontend protocols."""

import asyncio
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

import structlog

from ..agents import root_agent
from ..backends import BackendRouter, get_router
from ..config import BrowserConfig, get_config
from .event_bus import AgentEvent, EventBus, EventType

logger = structlog.get_logger()


class UnifiedBrowserAgent:
    """Unified browser agent supporting multiple frontend protocols.

    Wraps the ADK browser agent and provides protocol-agnostic
    event streaming for TanStack AI, MCP-UI, and AG-UI.
    """

    def __init__(
        self,
        config: BrowserConfig | None = None,
        router: BackendRouter | None = None,
    ):
        self.config = config or get_config()
        self.router = router or get_router()
        self.event_bus = EventBus()
        self._active_runs: dict[str, asyncio.Task] = {}

    async def run(
        self,
        message: str,
        thread_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Run the agent with a message and return the result.

        Args:
            message: User message
            thread_id: Optional thread ID for conversation continuity
            context: Optional additional context

        Returns:
            Agent response text
        """
        run_id = str(uuid4())
        thread_id = thread_id or str(uuid4())

        await self.event_bus.emit_run_started(run_id, thread_id)

        try:
            # Run the ADK agent
            # Note: This is a simplified version. Full ADK integration
            # would use the App.stream() method for proper event handling.

            result = await self._execute_agent(message, context)

            await self.event_bus.emit_text_complete(run_id, result)
            await self.event_bus.emit_run_finished(run_id, result)

            return result

        except Exception as e:
            logger.error("agent_run_error", run_id=run_id, error=str(e))
            await self.event_bus.emit_error(run_id, str(e))
            raise

    async def stream(
        self,
        message: str,
        thread_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> AsyncIterator[AgentEvent]:
        """Stream agent responses as events.

        Args:
            message: User message
            thread_id: Optional thread ID
            context: Optional additional context

        Yields:
            Agent events
        """
        run_id = str(uuid4())
        thread_id = thread_id or str(uuid4())

        # Start streaming
        async def _run():
            await self.run(message, thread_id, context)

        task = asyncio.create_task(_run())
        self._active_runs[run_id] = task

        try:
            async for event in self.event_bus.stream(run_id):
                yield event
        finally:
            if run_id in self._active_runs:
                del self._active_runs[run_id]

    async def _execute_agent(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Execute the ADK agent.

        This is a simplified implementation. Full integration would use:
        - google.adk.apps.App for session management
        - Proper event streaming from ADK
        - State persistence
        """
        # Parse intent from message
        intent = self._parse_intent(message)

        if intent == "extract":
            # Quick extraction
            from ..agents.gatherer import extract_page
            url = self._extract_url(message)
            if url:
                result = await extract_page(url)
                return self._format_result(result)

        elif intent == "research":
            # Deep research
            from ..agents.gatherer import deep_research
            topic = message.replace("research", "").strip()
            result = await deep_research(topic)
            return self._format_result(result)

        elif intent == "navigate":
            # Navigation
            from ..agents.hunter import navigate_to_goal
            url = self._extract_url(message)
            if url:
                result = await navigate_to_goal(url, goal="Navigate to page")
                return self._format_result(result)

        elif intent == "screenshot":
            # Screenshot
            url = self._extract_url(message)
            if url:
                async def _screenshot(backend):
                    return await backend.screenshot(url=url)
                result = await self.router.execute_with_fallback(
                    "screenshot",
                    _screenshot,
                )
                if result.success:
                    return f"Screenshot captured successfully. Image size: {result.width}x{result.height}"
                return f"Screenshot failed: {result.error}"

        # Default: try extraction
        url = self._extract_url(message)
        if url:
            from ..agents.gatherer import extract_page
            result = await extract_page(url)
            return self._format_result(result)

        return f"I understand you want to: {message}. Please provide a URL or more specific instructions."

    def _parse_intent(self, message: str) -> str:
        """Parse user intent from message."""
        message_lower = message.lower()

        if any(w in message_lower for w in ["research", "find out", "learn about"]):
            return "research"
        if any(w in message_lower for w in ["screenshot", "capture", "image of"]):
            return "screenshot"
        if any(w in message_lower for w in ["go to", "navigate", "open"]):
            return "navigate"
        if any(w in message_lower for w in ["extract", "scrape", "get content", "fetch"]):
            return "extract"

        return "unknown"

    def _extract_url(self, message: str) -> str | None:
        """Extract URL from message."""
        import re
        url_pattern = r'https?://[^\s<>"\'{}|\\^`\[\]]+'
        match = re.search(url_pattern, message)
        return match.group(0) if match else None

    def _format_result(self, result: dict) -> str:
        """Format result dictionary as readable text."""
        if not result.get("success"):
            return f"Operation failed: {result.get('error', 'Unknown error')}"

        content = result.get("content", {})

        if "markdown" in content:
            return content["markdown"]

        if "extracted" in content:
            import json
            return json.dumps(content["extracted"], indent=2)

        if "data" in result:
            import json
            return json.dumps(result["data"], indent=2)

        return f"Operation completed successfully. Backend: {result.get('backend', 'unknown')}"

    async def cancel_run(self, run_id: str) -> bool:
        """Cancel an active run."""
        if run_id in self._active_runs:
            self._active_runs[run_id].cancel()
            del self._active_runs[run_id]
            return True
        return False

    def get_active_runs(self) -> list[str]:
        """Get list of active run IDs."""
        return list(self._active_runs.keys())


# Global instance
_agent: UnifiedBrowserAgent | None = None


def get_browser_agent() -> UnifiedBrowserAgent:
    """Get the global browser agent instance."""
    global _agent
    if _agent is None:
        _agent = UnifiedBrowserAgent()
    return _agent
