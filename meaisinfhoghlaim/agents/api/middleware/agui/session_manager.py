"""
AG-UI Session Manager.

Manages conversation sessions for the AG-UI protocol, including:
- Session creation and lookup by thread_id
- Session state management
- Message history tracking
- Session cleanup and timeout handling
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """A message in the conversation history."""

    id: str
    role: str  # user, assistant, system, tool
    content: str
    timestamp: float = field(default_factory=time.time)
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None


@dataclass
class Session:
    """A conversation session."""

    session_id: str
    thread_id: str
    user_id: str
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    state: dict[str, Any] = field(default_factory=dict)
    messages: list[Message] = field(default_factory=list)
    processed_message_ids: set[str] = field(default_factory=set)
    pending_tool_calls: list[str] = field(default_factory=list)


class SessionManager:
    """Manages conversation sessions with singleton pattern.

    Thread-safe session management with automatic cleanup of stale sessions.
    Supports session persistence and state management for AG-UI workflows.

    Usage:
        manager = SessionManager.get_instance()
        session = await manager.get_or_create_session(thread_id, user_id)
    """

    _instance: SessionManager | None = None
    _lock = asyncio.Lock()

    def __init__(
        self,
        session_timeout_seconds: int = 1200,  # 20 minutes
        cleanup_interval_seconds: int = 300,  # 5 minutes
        max_sessions_per_user: int | None = None,
    ):
        self._sessions: dict[str, Session] = {}
        self._thread_to_session: dict[str, str] = {}  # thread_id -> session_id
        self._user_sessions: dict[str, set[str]] = defaultdict(set)  # user_id -> session_ids

        self._session_timeout = session_timeout_seconds
        self._cleanup_interval = cleanup_interval_seconds
        self._max_sessions_per_user = max_sessions_per_user

        self._cleanup_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    @classmethod
    async def get_instance(
        cls,
        session_timeout_seconds: int = 1200,
        cleanup_interval_seconds: int = 300,
        **kwargs,
    ) -> SessionManager:
        """Get or create the singleton instance."""
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls(
                    session_timeout_seconds=session_timeout_seconds,
                    cleanup_interval_seconds=cleanup_interval_seconds,
                    **kwargs,
                )
                # Start cleanup task
                cls._instance._start_cleanup_task()
            return cls._instance

    def _start_cleanup_task(self):
        """Start background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self):
        """Background loop to clean up expired sessions."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")

    async def _cleanup_expired_sessions(self):
        """Remove sessions that have exceeded the timeout."""
        now = time.time()
        expired = []

        async with self._lock:
            for session_id, session in self._sessions.items():
                if now - session.last_activity > self._session_timeout:
                    expired.append(session_id)

            for session_id in expired:
                session = self._sessions.pop(session_id, None)
                if session:
                    self._thread_to_session.pop(session.thread_id, None)
                    if session.user_id in self._user_sessions:
                        self._user_sessions[session.user_id].discard(session_id)

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")

    async def stop_cleanup_task(self):
        """Stop the background cleanup task."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def get_or_create_session(
        self,
        thread_id: str,
        user_id: str,
        initial_state: dict[str, Any] | None = None,
    ) -> tuple[Session, str]:
        """Get an existing session or create a new one.

        Args:
            thread_id: AG-UI thread ID (client-provided)
            user_id: User identifier
            initial_state: Initial state for new sessions

        Returns:
            Tuple of (Session, session_id)
        """
        async with self._lock:
            # Check if session exists for this thread
            if thread_id in self._thread_to_session:
                session_id = self._thread_to_session[thread_id]
                session = self._sessions.get(session_id)
                if session:
                    session.last_activity = time.time()
                    return session, session_id

            # Check max sessions per user
            if self._max_sessions_per_user:
                user_session_count = len(self._user_sessions.get(user_id, set()))
                if user_session_count >= self._max_sessions_per_user:
                    # Remove oldest session
                    await self._remove_oldest_user_session(user_id)

            # Create new session
            session_id = str(uuid.uuid4())
            session = Session(
                session_id=session_id,
                thread_id=thread_id,
                user_id=user_id,
                state=initial_state.copy() if initial_state else {},
            )

            self._sessions[session_id] = session
            self._thread_to_session[thread_id] = session_id
            self._user_sessions[user_id].add(session_id)

            logger.debug(f"Created session {session_id} for thread {thread_id}")
            return session, session_id

    async def _remove_oldest_user_session(self, user_id: str):
        """Remove the oldest session for a user."""
        user_sessions = self._user_sessions.get(user_id, set())
        if not user_sessions:
            return

        oldest_session = None
        oldest_time = float("inf")

        for session_id in user_sessions:
            session = self._sessions.get(session_id)
            if session and session.last_activity < oldest_time:
                oldest_time = session.last_activity
                oldest_session = session

        if oldest_session:
            await self._delete_session(oldest_session.session_id)

    async def _delete_session(self, session_id: str):
        """Delete a session by ID."""
        session = self._sessions.pop(session_id, None)
        if session:
            self._thread_to_session.pop(session.thread_id, None)
            self._user_sessions[session.user_id].discard(session_id)

    async def get_session(
        self,
        session_id: str,
        user_id: str | None = None,
    ) -> Session | None:
        """Get a session by ID.

        Args:
            session_id: Session ID
            user_id: Optional user ID for validation

        Returns:
            Session or None if not found
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                if user_id and session.user_id != user_id:
                    return None
                session.last_activity = time.time()
                return session
            return None

    async def get_session_by_thread_id(
        self,
        thread_id: str,
        user_id: str | None = None,
    ) -> Session | None:
        """Get a session by thread ID.

        Args:
            thread_id: AG-UI thread ID
            user_id: Optional user ID for validation

        Returns:
            Session or None if not found
        """
        async with self._lock:
            session_id = self._thread_to_session.get(thread_id)
            if not session_id:
                return None

            session = self._sessions.get(session_id)
            if session:
                if user_id and session.user_id != user_id:
                    return None
                session.last_activity = time.time()
                return session
            return None

    async def update_session_state(
        self,
        session_id: str,
        state: dict[str, Any],
    ) -> bool:
        """Update session state.

        Args:
            session_id: Session ID
            state: State to merge with existing state

        Returns:
            True if successful
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            session.state.update(state)
            session.last_activity = time.time()
            return True

    async def set_state_value(
        self,
        session_id: str,
        key: str,
        value: Any,
    ) -> bool:
        """Set a single state value.

        Args:
            session_id: Session ID
            key: State key
            value: Value to set

        Returns:
            True if successful
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            session.state[key] = value
            session.last_activity = time.time()
            return True

    async def get_state_value(
        self,
        session_id: str,
        key: str,
        default: Any = None,
    ) -> Any:
        """Get a single state value.

        Args:
            session_id: Session ID
            key: State key
            default: Default value if not found

        Returns:
            State value or default
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return default

            return session.state.get(key, default)

    async def get_session_state(
        self,
        session_id: str,
    ) -> dict[str, Any] | None:
        """Get full session state.

        Args:
            session_id: Session ID

        Returns:
            Session state or None if not found
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None

            return session.state.copy()

    async def add_message(
        self,
        session_id: str,
        message: Message,
    ) -> bool:
        """Add a message to the session history.

        Args:
            session_id: Session ID
            message: Message to add

        Returns:
            True if successful
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            session.messages.append(message)
            session.processed_message_ids.add(message.id)
            session.last_activity = time.time()
            return True

    async def get_messages(
        self,
        session_id: str,
    ) -> list[Message]:
        """Get all messages for a session.

        Args:
            session_id: Session ID

        Returns:
            List of messages
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return []

            return list(session.messages)

    def mark_messages_processed(
        self,
        thread_id: str,
        message_ids: list[str],
    ):
        """Mark messages as processed (synchronous for performance).

        Args:
            thread_id: AG-UI thread ID
            message_ids: List of message IDs to mark
        """
        session_id = self._thread_to_session.get(thread_id)
        if not session_id:
            return

        session = self._sessions.get(session_id)
        if session:
            session.processed_message_ids.update(message_ids)

    def get_processed_message_ids(self, thread_id: str) -> set[str]:
        """Get set of processed message IDs for a thread.

        Args:
            thread_id: AG-UI thread ID

        Returns:
            Set of processed message IDs
        """
        session_id = self._thread_to_session.get(thread_id)
        if not session_id:
            return set()

        session = self._sessions.get(session_id)
        if session:
            return session.processed_message_ids.copy()
        return set()

    async def add_pending_tool_call(
        self,
        session_id: str,
        tool_call_id: str,
    ) -> bool:
        """Add a pending tool call to track.

        Args:
            session_id: Session ID
            tool_call_id: Tool call ID

        Returns:
            True if successful
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            if tool_call_id not in session.pending_tool_calls:
                session.pending_tool_calls.append(tool_call_id)
            return True

    async def remove_pending_tool_call(
        self,
        session_id: str,
        tool_call_id: str,
    ) -> bool:
        """Remove a pending tool call.

        Args:
            session_id: Session ID
            tool_call_id: Tool call ID

        Returns:
            True if successful
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            if tool_call_id in session.pending_tool_calls:
                session.pending_tool_calls.remove(tool_call_id)
            return True

    async def has_pending_tool_calls(self, session_id: str) -> bool:
        """Check if session has pending tool calls.

        Args:
            session_id: Session ID

        Returns:
            True if there are pending tool calls
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            return len(session.pending_tool_calls) > 0
