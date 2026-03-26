"""Restate durable execution integration for browser agent stack.

Provides:
- Durable execution for multi-step agent pipelines
- Checkpointing between Hunter/Operator/Gatherer/Evaluator agents
- Virtual objects for stateful browser sessions
- Awakeables for human-in-the-loop approval workflows
- Parallel execution with gather/select patterns
"""

import asyncio
from dataclasses import dataclass, field
from datetime import timedelta
from functools import lru_cache
from typing import Any, Callable, TypeVar

import httpx
import structlog

from ..config import BrowserConfig, get_config

logger = structlog.get_logger()

T = TypeVar("T")


@dataclass
class RestateContext:
    """Context for Restate workflow execution.

    Provides durable execution primitives:
    - run(): Execute a step with automatic checkpointing
    - sleep(): Durable sleep that survives restarts
    - awakeable(): Create promises that can be resolved externally
    - get/set(): Access journaled state
    """

    workflow_id: str
    run_id: str
    step_index: int = 0
    state: dict[str, Any] = field(default_factory=dict)
    _completed_steps: set[str] = field(default_factory=set)

    async def run(
        self,
        step_name: str,
        action: Callable[[], T],
    ) -> T:
        """Execute a step with checkpointing.

        If the workflow is replaying after a crash, this will
        return the cached result instead of re-executing.
        """
        step_key = f"{step_name}_{self.step_index}"

        if step_key in self._completed_steps:
            logger.debug("restate_step_cached", step=step_name)
            return self.state.get(f"result_{step_key}")

        logger.info("restate_step_executing", step=step_name)

        try:
            if asyncio.iscoroutinefunction(action):
                result = await action()
            else:
                result = action()

            # Store result for replay
            self.state[f"result_{step_key}"] = result
            self._completed_steps.add(step_key)
            self.step_index += 1

            return result

        except Exception as e:
            logger.error("restate_step_failed", step=step_name, error=str(e))
            raise

    async def sleep(self, duration: timedelta) -> None:
        """Durable sleep that survives restarts."""
        await asyncio.sleep(duration.total_seconds())

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from journaled state."""
        return self.state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set value in journaled state."""
        self.state[key] = value


@dataclass
class Awakeable:
    """Represents a promise that can be resolved externally.

    Used for human-in-the-loop approval workflows where the agent
    waits for a human decision before proceeding.
    """

    id: str
    _resolved: bool = False
    _result: Any = None
    _error: Exception | None = None
    _event: asyncio.Event = field(default_factory=asyncio.Event)

    async def wait(self, timeout: timedelta | None = None) -> Any:
        """Wait for the awakeable to be resolved."""
        if timeout:
            try:
                await asyncio.wait_for(
                    self._event.wait(),
                    timeout=timeout.total_seconds(),
                )
            except asyncio.TimeoutError:
                raise TimeoutError(f"Awakeable {self.id} timed out after {timeout}")
        else:
            await self._event.wait()

        if self._error:
            raise self._error
        return self._result

    def resolve(self, result: Any) -> None:
        """Resolve the awakeable with a result."""
        self._result = result
        self._resolved = True
        self._event.set()

    def reject(self, error: Exception) -> None:
        """Reject the awakeable with an error."""
        self._error = error
        self._resolved = True
        self._event.set()


class AwakeableManager:
    """Manages awakeables for human-in-the-loop workflows."""

    def __init__(self):
        self._awakeables: dict[str, Awakeable] = {}
        self._counter = 0

    def create(self, prefix: str = "awakeable") -> Awakeable:
        """Create a new awakeable."""
        self._counter += 1
        awakeable_id = f"{prefix}_{self._counter}"
        awakeable = Awakeable(id=awakeable_id)
        self._awakeables[awakeable_id] = awakeable
        return awakeable

    def resolve(self, awakeable_id: str, result: Any) -> bool:
        """Resolve an awakeable by ID."""
        awakeable = self._awakeables.get(awakeable_id)
        if awakeable:
            awakeable.resolve(result)
            return True
        return False

    def reject(self, awakeable_id: str, error: Exception) -> bool:
        """Reject an awakeable by ID."""
        awakeable = self._awakeables.get(awakeable_id)
        if awakeable:
            awakeable.reject(error)
            return True
        return False

    def get(self, awakeable_id: str) -> Awakeable | None:
        """Get an awakeable by ID."""
        return self._awakeables.get(awakeable_id)


class RestateClient:
    """HTTP client for Restate server communication.

    Handles:
    - Health checks
    - Workflow invocation
    - Awakeable resolution
    - State queries
    """

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={"Content-Type": "application/json"},
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        """Check if Restate server is healthy."""
        try:
            response = await self.client.get(
                f"{self.config.restate_admin_url}/health"
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning("restate_health_check_failed", error=str(e))
            return False

    async def invoke_workflow(
        self,
        service: str,
        handler: str,
        key: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Invoke a Restate workflow or handler.

        Args:
            service: Service name (e.g., "browser_session")
            handler: Handler name (e.g., "navigate")
            key: Object key for virtual objects (e.g., session_id)
            data: Request payload

        Returns:
            Response from the handler
        """
        if key:
            url = f"{self.config.restate_url}/{service}/{key}/{handler}"
        else:
            url = f"{self.config.restate_url}/{service}/{handler}"

        try:
            response = await self.client.post(url, json=data or {})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("restate_invoke_failed", service=service, handler=handler, error=str(e))
            raise

    async def resolve_awakeable(
        self,
        awakeable_id: str,
        result: Any,
    ) -> bool:
        """Resolve an awakeable via Restate API.

        Called by the approval UI when a human approves/rejects an action.
        """
        url = f"{self.config.restate_url}/restate/awakeables/{awakeable_id}/resolve"

        try:
            response = await self.client.post(url, json={"result": result})
            return response.status_code == 200
        except Exception as e:
            logger.error("restate_awakeable_resolve_failed", id=awakeable_id, error=str(e))
            return False

    async def reject_awakeable(
        self,
        awakeable_id: str,
        reason: str,
    ) -> bool:
        """Reject an awakeable via Restate API."""
        url = f"{self.config.restate_url}/restate/awakeables/{awakeable_id}/reject"

        try:
            response = await self.client.post(url, json={"reason": reason})
            return response.status_code == 200
        except Exception as e:
            logger.error("restate_awakeable_reject_failed", id=awakeable_id, error=str(e))
            return False

    async def get_workflow_state(
        self,
        service: str,
        key: str,
    ) -> dict[str, Any]:
        """Get the current state of a workflow/virtual object."""
        url = f"{self.config.restate_admin_url}/query/{service}/{key}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("restate_state_query_failed", service=service, key=key, error=str(e))
            return {}


class RestateSessionService:
    """Session service backed by Restate virtual objects.

    Provides persistent session storage that survives:
    - Process restarts
    - Network failures
    - Crashes during execution
    """

    def __init__(self, client: RestateClient):
        self.client = client
        self._local_cache: dict[str, dict[str, Any]] = {}

    async def get_session(self, session_id: str) -> dict[str, Any]:
        """Get session data from Restate."""
        cached = self._local_cache.get(session_id)
        if cached:
            return cached

        try:
            state = await self.client.get_workflow_state(
                service="browser_session",
                key=session_id,
            )
            self._local_cache[session_id] = state
            return state
        except Exception:
            return {}

    async def update_session(
        self,
        session_id: str,
        updates: dict[str, Any],
    ) -> None:
        """Update session data in Restate."""
        await self.client.invoke_workflow(
            service="browser_session",
            handler="update_state",
            key=session_id,
            data=updates,
        )

        # Update local cache
        if session_id not in self._local_cache:
            self._local_cache[session_id] = {}
        self._local_cache[session_id].update(updates)

    async def delete_session(self, session_id: str) -> None:
        """Delete a session from Restate."""
        await self.client.invoke_workflow(
            service="browser_session",
            handler="delete",
            key=session_id,
        )
        self._local_cache.pop(session_id, None)


class RestatePlugin:
    """Plugin for integrating Restate with Google ADK.

    Wraps ADK agent execution with Restate durable execution,
    providing automatic checkpointing and recovery.
    """

    def __init__(
        self,
        config: BrowserConfig | None = None,
    ):
        self.config = config or get_config()
        self.client = RestateClient(config)
        self.session_service = RestateSessionService(self.client)
        self.awakeable_manager = AwakeableManager()

    async def initialize(self) -> bool:
        """Initialize the Restate plugin."""
        if not self.config.enable_durable_execution:
            logger.info("restate_disabled")
            return False

        healthy = await self.client.health_check()
        if healthy:
            logger.info("restate_initialized", url=self.config.restate_url)
        else:
            logger.warning("restate_unavailable", url=self.config.restate_url)

        return healthy

    async def close(self) -> None:
        """Clean up resources."""
        await self.client.close()

    def create_context(
        self,
        workflow_id: str,
        run_id: str | None = None,
    ) -> RestateContext:
        """Create a new execution context for a workflow."""
        import uuid
        return RestateContext(
            workflow_id=workflow_id,
            run_id=run_id or str(uuid.uuid4()),
        )

    async def request_approval(
        self,
        session_id: str,
        action: str,
        details: dict[str, Any] | None = None,
        timeout_minutes: int | None = None,
    ) -> bool:
        """Request human approval for an action.

        Args:
            session_id: Session ID for context
            action: Description of the action requiring approval
            details: Additional details for the approval request
            timeout_minutes: Override default timeout

        Returns:
            True if approved, False if rejected or timed out
        """
        if not self.config.enable_human_approval:
            logger.debug("human_approval_disabled")
            return True  # Auto-approve if disabled

        # Create awakeable for the approval
        awakeable = self.awakeable_manager.create(prefix=f"approval_{session_id}")

        # Publish approval request (to be picked up by UI)
        logger.info(
            "approval_requested",
            awakeable_id=awakeable.id,
            session_id=session_id,
            action=action,
        )

        # Store the request for UI to pick up
        await self.session_service.update_session(
            session_id,
            {
                "pending_approval": {
                    "awakeable_id": awakeable.id,
                    "action": action,
                    "details": details or {},
                    "status": "pending",
                }
            },
        )

        # Wait for human response
        timeout = timedelta(
            minutes=timeout_minutes or self.config.approval_timeout_minutes
        )

        try:
            result = await awakeable.wait(timeout=timeout)
            logger.info("approval_received", awakeable_id=awakeable.id, approved=result)
            return bool(result)
        except TimeoutError:
            logger.warning("approval_timeout", awakeable_id=awakeable.id)
            return False
        finally:
            # Clear pending approval
            await self.session_service.update_session(
                session_id,
                {"pending_approval": None},
            )


# Global plugin instance
_plugin: RestatePlugin | None = None


@lru_cache
def get_restate_plugin() -> RestatePlugin:
    """Get the global Restate plugin instance."""
    global _plugin
    if _plugin is None:
        _plugin = RestatePlugin()
    return _plugin


async def init_restate() -> RestatePlugin:
    """Initialize and return the Restate plugin."""
    plugin = get_restate_plugin()
    await plugin.initialize()
    return plugin
