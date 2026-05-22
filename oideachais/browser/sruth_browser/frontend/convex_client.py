"""Python client for Convex real-time backend.

Provides:
- Thread and message persistence
- Real-time event publishing
- Subscription management
- Workflow invocation
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from typing import Any, Callable
from uuid import uuid4

import httpx
import structlog

from ..config import BrowserConfig, get_config

logger = structlog.get_logger()


@dataclass
class ConvexMessage:
    """Represents a message in a Convex thread."""

    id: str
    thread_id: str
    role: str  # user, assistant, tool
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    timestamp: float = field(default_factory=lambda: datetime.utcnow().timestamp())
    metadata: dict[str, Any] | None = None


@dataclass
class ConvexThread:
    """Represents a Convex thread."""

    id: str
    user_id: str
    session_id: str
    status: str = "running"  # running, completed, failed
    metadata: dict[str, Any] | None = None
    created_at: float = field(default_factory=lambda: datetime.utcnow().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.utcnow().timestamp())


class ConvexClient:
    """HTTP client for Convex backend.

    Handles all communication with the self-hosted Convex server
    for persistent thread/message storage and real-time sync.
    """

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._client: httpx.AsyncClient | None = None
        self._local_threads: dict[str, ConvexThread] = {}
        self._local_messages: dict[str, list[ConvexMessage]] = {}

    @property
    def base_url(self) -> str:
        """Get Convex API base URL."""
        return self.config.convex_url.rstrip("/")

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        """Check if Convex backend is healthy."""
        try:
            response = await self.client.get(f"{self.base_url}/version")
            return response.status_code == 200
        except Exception as e:
            logger.warning("convex_health_check_failed", error=str(e))
            return False

    # =========================================================================
    # Thread Operations
    # =========================================================================

    async def create_thread(
        self,
        user_id: str,
        session_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> ConvexThread:
        """Create a new thread.

        Args:
            user_id: User identifier
            session_id: Browser session ID
            metadata: Optional thread metadata

        Returns:
            Created thread
        """
        thread = ConvexThread(
            id=f"thread_{uuid4().hex[:12]}",
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
        )

        try:
            response = await self.client.post(
                f"{self.base_url}/api/mutation",
                json={
                    "path": "threads:create",
                    "args": {
                        "userId": user_id,
                        "sessionId": session_id,
                        "status": thread.status,
                        "metadata": metadata,
                    },
                },
            )
            response.raise_for_status()
            result = response.json()

            # Update thread ID from Convex
            if result.get("value"):
                thread.id = result["value"]

            logger.info("thread_created", thread_id=thread.id, user_id=user_id)

        except Exception as e:
            logger.warning("convex_create_failed", error=str(e))
            # Fall back to local storage

        # Store locally
        self._local_threads[thread.id] = thread
        self._local_messages[thread.id] = []

        return thread

    async def get_thread(self, thread_id: str) -> ConvexThread | None:
        """Get a thread by ID.

        Args:
            thread_id: Thread ID

        Returns:
            Thread if found, None otherwise
        """
        # Check local cache first
        if thread_id in self._local_threads:
            return self._local_threads[thread_id]

        try:
            response = await self.client.post(
                f"{self.base_url}/api/query",
                json={
                    "path": "threads:get",
                    "args": {"threadId": thread_id},
                },
            )
            response.raise_for_status()
            result = response.json()

            if result.get("value"):
                data = result["value"]
                thread = ConvexThread(
                    id=data["_id"],
                    user_id=data["userId"],
                    session_id=data["sessionId"],
                    status=data["status"],
                    metadata=data.get("metadata"),
                    created_at=data.get("_creationTime", datetime.utcnow().timestamp()),
                )
                self._local_threads[thread.id] = thread
                return thread

        except Exception as e:
            logger.warning("convex_get_thread_failed", error=str(e))

        return None

    async def update_thread_status(
        self,
        thread_id: str,
        status: str,
    ) -> bool:
        """Update thread status.

        Args:
            thread_id: Thread ID
            status: New status (running, completed, failed)

        Returns:
            True if updated successfully
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/mutation",
                json={
                    "path": "threads:updateStatus",
                    "args": {
                        "threadId": thread_id,
                        "status": status,
                    },
                },
            )
            response.raise_for_status()

            # Update local cache
            if thread_id in self._local_threads:
                self._local_threads[thread_id].status = status
                self._local_threads[thread_id].updated_at = datetime.utcnow().timestamp()

            logger.info("thread_status_updated", thread_id=thread_id, status=status)
            return True

        except Exception as e:
            logger.warning("convex_update_status_failed", error=str(e))
            return False

    async def list_threads(
        self,
        user_id: str,
        limit: int = 50,
    ) -> list[ConvexThread]:
        """List threads for a user.

        Args:
            user_id: User identifier
            limit: Maximum threads to return

        Returns:
            List of threads
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/query",
                json={
                    "path": "threads:listByUser",
                    "args": {"userId": user_id, "limit": limit},
                },
            )
            response.raise_for_status()
            result = response.json()

            threads = []
            for data in result.get("value", []):
                thread = ConvexThread(
                    id=data["_id"],
                    user_id=data["userId"],
                    session_id=data["sessionId"],
                    status=data["status"],
                    metadata=data.get("metadata"),
                )
                threads.append(thread)
                self._local_threads[thread.id] = thread

            return threads

        except Exception as e:
            logger.warning("convex_list_threads_failed", error=str(e))
            # Return cached threads
            return [
                t for t in self._local_threads.values()
                if t.user_id == user_id
            ][:limit]

    # =========================================================================
    # Message Operations
    # =========================================================================

    async def add_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        tool_calls: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ConvexMessage:
        """Add a message to a thread.

        Args:
            thread_id: Thread ID
            role: Message role (user, assistant, tool)
            content: Message content
            tool_calls: Optional tool call details
            metadata: Optional message metadata

        Returns:
            Created message
        """
        message = ConvexMessage(
            id=f"msg_{uuid4().hex[:12]}",
            thread_id=thread_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            metadata=metadata,
        )

        try:
            response = await self.client.post(
                f"{self.base_url}/api/mutation",
                json={
                    "path": "messages:add",
                    "args": {
                        "threadId": thread_id,
                        "role": role,
                        "content": content,
                        "toolCalls": tool_calls,
                        "timestamp": message.timestamp,
                    },
                },
            )
            response.raise_for_status()
            result = response.json()

            if result.get("value"):
                message.id = result["value"]

            logger.debug("message_added", message_id=message.id, thread_id=thread_id)

        except Exception as e:
            logger.warning("convex_add_message_failed", error=str(e))

        # Store locally
        if thread_id not in self._local_messages:
            self._local_messages[thread_id] = []
        self._local_messages[thread_id].append(message)

        return message

    async def get_messages(
        self,
        thread_id: str,
        limit: int = 100,
    ) -> list[ConvexMessage]:
        """Get messages for a thread.

        Args:
            thread_id: Thread ID
            limit: Maximum messages to return

        Returns:
            List of messages
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/query",
                json={
                    "path": "messages:listByThread",
                    "args": {"threadId": thread_id, "limit": limit},
                },
            )
            response.raise_for_status()
            result = response.json()

            messages = []
            for data in result.get("value", []):
                msg = ConvexMessage(
                    id=data["_id"],
                    thread_id=thread_id,
                    role=data["role"],
                    content=data["content"],
                    tool_calls=data.get("toolCalls"),
                    timestamp=data.get("timestamp", 0),
                )
                messages.append(msg)

            # Update local cache
            self._local_messages[thread_id] = messages

            return messages

        except Exception as e:
            logger.warning("convex_get_messages_failed", error=str(e))
            return self._local_messages.get(thread_id, [])[:limit]

    # =========================================================================
    # Event Publishing
    # =========================================================================

    async def publish_event(
        self,
        thread_id: str,
        event_type: str,
        data: dict[str, Any],
    ) -> bool:
        """Publish an event to a thread.

        Events are used for real-time UI updates.

        Args:
            thread_id: Thread ID
            event_type: Event type (e.g., "TOOL_CALL_START", "TEXT_DELTA")
            data: Event data

        Returns:
            True if published successfully
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/mutation",
                json={
                    "path": "events:publish",
                    "args": {
                        "threadId": thread_id,
                        "eventType": event_type,
                        "data": data,
                        "timestamp": datetime.utcnow().timestamp(),
                    },
                },
            )
            response.raise_for_status()
            logger.debug("event_published", thread_id=thread_id, event_type=event_type)
            return True

        except Exception as e:
            logger.warning("convex_publish_event_failed", error=str(e))
            return False

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def start_workflow(
        self,
        workflow_name: str,
        args: dict[str, Any],
    ) -> str | None:
        """Start a Convex workflow.

        Args:
            workflow_name: Name of the workflow
            args: Workflow arguments

        Returns:
            Workflow ID if started successfully
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/mutation",
                json={
                    "path": f"workflows:{workflow_name}:start",
                    "args": args,
                },
            )
            response.raise_for_status()
            result = response.json()
            return result.get("value")

        except Exception as e:
            logger.error("convex_start_workflow_failed", workflow=workflow_name, error=str(e))
            return None

    async def get_workflow_status(
        self,
        workflow_id: str,
    ) -> dict[str, Any] | None:
        """Get workflow status.

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow status or None
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/query",
                json={
                    "path": "workflows:getStatus",
                    "args": {"workflowId": workflow_id},
                },
            )
            response.raise_for_status()
            return response.json().get("value")

        except Exception as e:
            logger.warning("convex_get_workflow_status_failed", error=str(e))
            return None


class ConvexEventBridge:
    """Bridge between browser agent events and Convex.

    Listens to agent events and publishes them to Convex
    for real-time UI sync.
    """

    def __init__(self, client: ConvexClient):
        self.client = client
        self._active_thread: str | None = None

    def set_active_thread(self, thread_id: str) -> None:
        """Set the active thread for event publishing."""
        self._active_thread = thread_id

    async def on_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Handle an agent event and publish to Convex."""
        if not self._active_thread:
            return

        await self.client.publish_event(
            thread_id=self._active_thread,
            event_type=event_type,
            data=data,
        )

        # Also add as message for important events
        if event_type in ["TEXT_COMPLETE", "TOOL_RESULT", "RUN_ERROR"]:
            role = "assistant" if event_type == "TEXT_COMPLETE" else "tool"
            content = data.get("content", data.get("result", str(data)))

            await self.client.add_message(
                thread_id=self._active_thread,
                role=role,
                content=content if isinstance(content, str) else json.dumps(content),
                tool_calls=data.get("tool_calls"),
            )


# Global client instance
_client: ConvexClient | None = None


@lru_cache
def get_convex_client() -> ConvexClient:
    """Get the global Convex client instance."""
    global _client
    if _client is None:
        _client = ConvexClient()
    return _client


async def init_convex() -> ConvexClient:
    """Initialize and return the Convex client."""
    client = get_convex_client()
    healthy = await client.health_check()

    if healthy:
        logger.info("convex_initialized", url=client.base_url)
    else:
        logger.warning("convex_unavailable", url=client.base_url)

    return client
