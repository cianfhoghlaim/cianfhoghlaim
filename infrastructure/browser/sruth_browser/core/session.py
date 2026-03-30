"""Browser session management with state persistence."""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Any

import structlog

from ..config import BrowserConfig, get_config
from ..exceptions import SessionError
from ..browser_types import BackendType, SessionState

logger = structlog.get_logger()


class BrowserSession:
    """Manages a single browser session with state migration support."""

    def __init__(
        self,
        session_id: str | None = None,
        backend: BackendType = BackendType.CDP_LOCAL,
        config: BrowserConfig | None = None,
    ):
        self.session_id = session_id or str(uuid.uuid4())
        self.backend = backend
        self.config = config or get_config()
        self._state = SessionState(session_id=self.session_id, backend=backend)
        self._lock = asyncio.Lock()
        self._cdp_connection: Any = None
        self._browserbase_session: Any = None

    @property
    def state(self) -> SessionState:
        """Get current session state."""
        return self._state

    async def initialize(self) -> None:
        """Initialize the browser session on the configured backend."""
        async with self._lock:
            logger.info(
                "initializing_session",
                session_id=self.session_id,
                backend=self.backend.value,
            )

            if self.backend == BackendType.CDP_LOCAL:
                await self._init_cdp_session()
            elif self.backend == BackendType.BROWSERBASE_MCP:
                await self._init_browserbase_session()
            elif self.backend == BackendType.SKYVERN_LOCAL:
                # Skyvern manages its own browser sessions
                pass
            elif self.backend == BackendType.CRAWL4AI_LOCAL:
                # Crawl4AI is stateless per request
                pass

            self._state.last_activity = datetime.utcnow()

    async def _init_cdp_session(self) -> None:
        """Initialize CDP connection to browser-grid."""
        try:
            from playwright.async_api import async_playwright

            playwright = await async_playwright().start()
            browser = await playwright.chromium.connect_over_cdp(self.config.cdp_url)
            context = await browser.new_context(
                viewport=self._state.viewport,
                user_agent=self._state.user_agent,
            )
            self._cdp_connection = {
                "playwright": playwright,
                "browser": browser,
                "context": context,
                "page": await context.new_page(),
            }
        except Exception as e:
            raise SessionError(self.session_id, f"CDP init failed: {e}") from e

    async def _init_browserbase_session(self) -> None:
        """Initialize Browserbase session via MCP."""
        if not self.config.has_browserbase:
            raise SessionError(self.session_id, "Browserbase not configured")

        # Session creation handled by MCP tool calls
        self._browserbase_session = {"active": True}

    async def navigate(self, url: str) -> None:
        """Navigate to URL and update state."""
        async with self._lock:
            if self.backend == BackendType.CDP_LOCAL and self._cdp_connection:
                page = self._cdp_connection["page"]
                await page.goto(url, timeout=int(self.config.navigation_timeout * 1000))
                self._state.url = page.url

            self._state.last_activity = datetime.utcnow()

    async def get_cookies(self) -> list[dict[str, Any]]:
        """Get all cookies from current session."""
        if self.backend == BackendType.CDP_LOCAL and self._cdp_connection:
            context = self._cdp_connection["context"]
            return await context.cookies()
        return self._state.cookies

    async def set_cookies(self, cookies: list[dict[str, Any]]) -> None:
        """Set cookies in current session."""
        async with self._lock:
            if self.backend == BackendType.CDP_LOCAL and self._cdp_connection:
                context = self._cdp_connection["context"]
                await context.add_cookies(cookies)
            self._state.cookies = cookies

    async def export_state(self) -> SessionState:
        """Export full session state for migration."""
        async with self._lock:
            if self.backend == BackendType.CDP_LOCAL and self._cdp_connection:
                context = self._cdp_connection["context"]
                page = self._cdp_connection["page"]

                self._state.cookies = await context.cookies()
                self._state.url = page.url

                # Export storage
                try:
                    self._state.local_storage = await page.evaluate(
                        "() => Object.fromEntries(Object.entries(localStorage))"
                    )
                    self._state.session_storage = await page.evaluate(
                        "() => Object.fromEntries(Object.entries(sessionStorage))"
                    )
                except Exception:
                    pass  # Storage access may fail for some pages

            return self._state

    async def import_state(self, state: SessionState) -> None:
        """Import session state from another session."""
        async with self._lock:
            old_id = self._state.session_id
            self._state = state.model_copy(update={"session_id": old_id})

            if self.backend == BackendType.CDP_LOCAL and self._cdp_connection:
                context = self._cdp_connection["context"]
                page = self._cdp_connection["page"]

                # Import cookies
                if state.cookies:
                    await context.add_cookies(state.cookies)

                # Navigate to URL
                if state.url:
                    await page.goto(state.url)

                # Import storage
                if state.local_storage:
                    for key, value in state.local_storage.items():
                        await page.evaluate(
                            f"localStorage.setItem({key!r}, {value!r})"
                        )
                if state.session_storage:
                    for key, value in state.session_storage.items():
                        await page.evaluate(
                            f"sessionStorage.setItem({key!r}, {value!r})"
                        )

    async def close(self) -> None:
        """Close the session and release resources."""
        async with self._lock:
            logger.info("closing_session", session_id=self.session_id)

            if self._cdp_connection:
                try:
                    await self._cdp_connection["browser"].close()
                    await self._cdp_connection["playwright"].stop()
                except Exception as e:
                    logger.warning("cdp_close_error", error=str(e))
                self._cdp_connection = None

            if self._browserbase_session:
                # Browserbase session cleanup via MCP
                self._browserbase_session = None


class SessionManager:
    """Manages multiple browser sessions with lifecycle handling."""

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._sessions: dict[str, BrowserSession] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the session manager."""
        if self.config.enable_session_persistence:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self) -> None:
        """Stop the session manager and close all sessions."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        async with self._lock:
            for session in list(self._sessions.values()):
                await session.close()
            self._sessions.clear()

    async def create_session(
        self,
        backend: BackendType = BackendType.CDP_LOCAL,
        session_id: str | None = None,
    ) -> BrowserSession:
        """Create a new browser session."""
        session = BrowserSession(
            session_id=session_id,
            backend=backend,
            config=self.config,
        )
        await session.initialize()

        async with self._lock:
            self._sessions[session.session_id] = session

        logger.info(
            "session_created",
            session_id=session.session_id,
            backend=backend.value,
        )
        return session

    async def get_session(self, session_id: str) -> BrowserSession | None:
        """Get an existing session by ID."""
        return self._sessions.get(session_id)

    async def migrate_session(
        self,
        session_id: str,
        target_backend: BackendType,
    ) -> BrowserSession:
        """Migrate a session to a different backend, preserving state."""
        async with self._lock:
            old_session = self._sessions.get(session_id)
            if not old_session:
                raise SessionError(session_id, "Session not found")

            # Export state from old session
            state = await old_session.export_state()

            # Create new session on target backend
            new_session = BrowserSession(
                session_id=session_id,
                backend=target_backend,
                config=self.config,
            )
            await new_session.initialize()
            await new_session.import_state(state)

            # Close old session
            await old_session.close()

            # Replace in registry
            self._sessions[session_id] = new_session

        logger.info(
            "session_migrated",
            session_id=session_id,
            from_backend=old_session.backend.value,
            to_backend=target_backend.value,
        )
        return new_session

    async def close_session(self, session_id: str) -> None:
        """Close and remove a session."""
        async with self._lock:
            session = self._sessions.pop(session_id, None)
            if session:
                await session.close()

    async def _cleanup_loop(self) -> None:
        """Periodically clean up stale sessions."""
        while True:
            await asyncio.sleep(60)  # Check every minute

            async with self._lock:
                now = datetime.utcnow()
                stale_threshold = timedelta(minutes=30)

                stale_ids = [
                    sid
                    for sid, session in self._sessions.items()
                    if now - session.state.last_activity > stale_threshold
                ]

                for sid in stale_ids:
                    session = self._sessions.pop(sid, None)
                    if session:
                        await session.close()
                        logger.info("session_cleaned_up", session_id=sid)
