"""Cost-based backend router with circuit breaker pattern.

High-level helpers for the author-archive-v1 pipeline:
- pre_research() - Firecrawl /agent with credit budget guard
- map_site() - sitemap discovery, prefers free
- visual_ground() - find element on screenshot, prefers free
- screenshot() - take a screenshot, prefers free
"""

import asyncio
import time
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from typing import Any, TypeVar

import structlog

from ..config import BrowserConfig, get_config
from ..credit_budget import BudgetExhaustedError, CreditBudget, get_budget
from ..exceptions import (
    BackendError,
    CircuitOpenError,
    FallbackExhaustedError,
    NoBackendError,
)
from ..browser_types import (
    BACKEND_COST,
    BACKEND_PRIORITY,
    BackendHealth,
    BackendType,
    BrowserOperation,
    CircuitState,
    ResearchResult,
    ScreenshotResult,
    VisualGroundingResult,
)
from .base import BrowserBackend, ResearchCapableBackend

logger = structlog.get_logger()
T = TypeVar("T")


class CircuitBreaker:
    def __init__(self, backend, failure_threshold=3, recovery_timeout=30.0, half_open_requests=1):
        self.backend = backend
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure = None
        self._last_success = None
        self._last_error = None
        self._half_open_count = 0
        self._lock = asyncio.Lock()
        self._latencies = []

    @property
    def health(self):
        avg = sum(self._latencies) / len(self._latencies) if self._latencies else None
        return BackendHealth(
            backend=self.backend,
            state=self._state,
            failure_count=self._failure_count,
            success_count=self._success_count,
            last_failure=self._last_failure,
            last_success=self._last_success,
            last_error=self._last_error,
            latency_ms=avg,
        )

    async def can_execute(self):
        async with self._lock:
            if self._state == CircuitState.CLOSED:
                return True
            if self._state == CircuitState.OPEN:
                if self._last_failure:
                    elapsed = datetime.utcnow() - self._last_failure
                    if elapsed >= timedelta(seconds=self.recovery_timeout):
                        self._state = CircuitState.HALF_OPEN
                        self._half_open_count = 0
                        return True
                return False
            if self._state == CircuitState.HALF_OPEN:
                return self._half_open_count < self.half_open_requests
            return False

    async def record_success(self, latency_ms):
        async with self._lock:
            self._success_count += 1
            self._last_success = datetime.utcnow()
            self._latencies.append(latency_ms)
            if len(self._latencies) > 100:
                self._latencies = self._latencies[-100:]
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_count += 1
                if self._half_open_count >= self.half_open_requests:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0

    async def record_failure(self, error):
        async with self._lock:
            self._failure_count += 1
            self._last_failure = datetime.utcnow()
            self._last_error = error
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
            elif self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN

    def time_until_recovery(self):
        if self._state != CircuitState.OPEN or not self._last_failure:
            return 0.0
        elapsed = (datetime.utcnow() - self._last_failure).total_seconds()
        return max(0.0, self.recovery_timeout - elapsed)


class BackendRouter:
    def __init__(self, config=None):
        self.config = config or get_config()
        self._backends = {}
        self._circuits = {}
        self._lock = asyncio.Lock()
        for bt in BackendType:
            self._circuits[bt] = CircuitBreaker(
                backend=bt,
                failure_threshold=self.config.circuit_failure_threshold,
                recovery_timeout=self.config.circuit_recovery_timeout,
                half_open_requests=self.config.circuit_half_open_requests,
            )

    def register_backend(self, backend):
        self._backends[backend.backend_type] = backend

    def get_backend(self, backend_type):
        return self._backends.get(backend_type)

    def get_health(self, backend_type):
        return self._circuits[backend_type].health

    def get_all_health(self):
        return [c.health for c in self._circuits.values()]

    async def select_backend(self, operation, exclude=None):
        exclude = exclude or []
        priority_order = BACKEND_PRIORITY.get(operation, list(BackendType))
        if self.config.fallback_strategy == "cost":
            priority_order = sorted(priority_order, key=lambda b: BACKEND_COST.get(b, 999))
        for bt in priority_order:
            if bt in exclude:
                continue
            if bt not in self._backends:
                continue
            if await self._circuits[bt].can_execute():
                return bt
        return None

    async def execute_with_fallback(self, operation, func, max_attempts=3):
        backends_tried = []
        for _ in range(max_attempts):
            bt = await self.select_backend(operation, exclude=backends_tried)
            if bt is None:
                if not backends_tried:
                    raise FallbackExhaustedError(operation.value, backends_tried)
                break
            backends_tried.append(bt)
            backend = self._backends[bt]
            circuit = self._circuits[bt]
            start = time.perf_counter()
            try:
                result = await func(backend)
                await circuit.record_success((time.perf_counter() - start) * 1000)
                return result
            except BackendError as e:
                await circuit.record_failure(str(e))
                if not e.retryable or not self.config.fallback_enabled:
                    raise
            except Exception as e:
                await circuit.record_failure(str(e))
                if not self.config.fallback_enabled:
                    raise BackendError(str(e), bt) from e
        raise FallbackExhaustedError(operation.value, backends_tried)

    async def execute_on_backend(self, backend_type, func):
        if backend_type not in self._backends:
            raise KeyError(f"Backend {backend_type.value} not registered")
        circuit = self._circuits[backend_type]
        if not await circuit.can_execute():
            raise CircuitOpenError(backend_type, circuit.time_until_recovery())
        backend = self._backends[backend_type]
        start = time.perf_counter()
        try:
            result = await func(backend)
            await circuit.record_success((time.perf_counter() - start) * 1000)
            return result
        except Exception as e:
            await circuit.record_failure(str(e))
            raise

    @property
    def budget(self) -> CreditBudget:
        return get_budget()

    @property
    def _budget(self) -> CreditBudget:
        return get_budget()

    def credit_summary(self):
        return self.budget.get_summary()

    async def pre_research(self, url, goal, *, budget_hint=2, prefer_free=False, timeout=None):
        budget = self.budget
        if prefer_free:
            return await self._free_pre_research(url, goal, timeout=timeout)
        if not budget.has(budget_hint):
            return await self._free_pre_research(url, goal, timeout=timeout)
        bt = await self.select_backend(BrowserOperation.RESEARCH)
        if bt is None:
            return await self._free_pre_research(url, goal, timeout=timeout)
        backend = self._backends[bt]
        if not isinstance(backend, ResearchCapableBackend):
            return await self._free_pre_research(url, goal, timeout=timeout)
        circuit = self._circuits[bt]
        if not await circuit.can_execute():
            return await self._free_pre_research(url, goal, timeout=timeout)
        start = time.perf_counter()
        try:
            payload = await backend.research(query=goal, max_urls=15, timeout=timeout)
            await circuit.record_success((time.perf_counter() - start) * 1000)
        except Exception:
            await circuit.record_failure("research failed")
            return await self._free_pre_research(url, goal, timeout=timeout)
        try:
            budget.charge(cost=budget_hint, backend=bt.value, purpose="pre_research", url=url)
        except BudgetExhaustedError:
            pass
        return ResearchResult(
            success=bool(payload.get("success")),
            query=goal,
            sources=payload.get("sources", []),
            content=payload.get("content", ""),
            backend_used=bt,
            latency_ms=payload.get("latency_ms", 0),
            urls_visited=payload.get("urls_visited", 0),
            tokens_used=payload.get("tokens_used"),
            error=payload.get("error"),
            metadata={
                "credits_spent_this_call": budget_hint,
                "raw_backend_payload": payload,
            },
        )

    async def _free_pre_research(self, url, goal, *, timeout=None):
        bt = await self.select_backend(BrowserOperation.MAP_SITE)
        if bt is None:
            raise NoBackendError(BrowserOperation.MAP_SITE.value)
        backend = self._backends[bt]
        start = time.perf_counter()
        urls = []
        sample = ""
        try:
            mf = getattr(backend, "map_site", None)
            if mf is not None:
                urls = await mf(url, limit=100)
        except Exception:
            pass
        if urls:
            try:
                from ..browser_types import ExtractionFormat
                sf = getattr(backend, "extract", None) or getattr(backend, "scrape", None)
                if sf is not None:
                    r = await sf(urls[0], formats=[ExtractionFormat.MARKDOWN], timeout=timeout)
                    if r.success:
                        sample = r.content.get("markdown", "")
            except Exception:
                pass
        return ResearchResult(
            success=bool(urls),
            query=goal,
            sources=[{"url": u} for u in urls[:50]],
            content=sample,
            backend_used=bt,
            latency_ms=(time.perf_counter() - start) * 1000,
            urls_visited=len(urls),
            metadata={"fallback": "free_pre_research", "sitemap_size": len(urls)},
        )

    async def map_site(self, url, *, prefer_free=True, search=None, limit=100, timeout=None):
        if prefer_free:
            free = [b for b in BACKEND_PRIORITY.get(BrowserOperation.MAP_SITE, []) if BACKEND_COST.get(b, 999) == 0]
            bt = None
            for c in free:
                if c in self._backends and await self._circuits[c].can_execute():
                    bt = c
                    break
        else:
            bt = await self.select_backend(BrowserOperation.MAP_SITE)
        if bt is None:
            raise NoBackendError(BrowserOperation.MAP_SITE.value)
        backend = self._backends[bt]
        mf = getattr(backend, "map_site", None)
        if mf is None:
            raise BackendError(f"Backend {bt.value} has no map_site", bt, retryable=False)
        try:
            return await mf(url, search=search, limit=limit)
        except Exception as e:
            await self._circuits[bt].record_failure(str(e))
            raise

    async def visual_ground(self, *, image_data, query, image_format="png", prefer_free=True, timeout=None):
        if prefer_free:
            free = [b for b in BACKEND_PRIORITY.get(BrowserOperation.VISUAL_GROUNDING, []) if BACKEND_COST.get(b, 999) == 0]
            bt = None
            for c in free:
                if c in self._backends and await self._circuits[c].can_execute():
                    bt = c
                    break
        else:
            bt = await self.select_backend(BrowserOperation.VISUAL_GROUNDING)
        if bt is None:
            raise NoBackendError(BrowserOperation.VISUAL_GROUNDING.value)
        backend = self._backends[bt]
        start = time.perf_counter()
        try:
            if bt == BackendType.ZAI_VISION:
                gf = getattr(backend, "visual_grounding", None) or getattr(backend, "visual_ground", None)
                if gf is None:
                    raise BackendError(f"Backend {bt.value} has no visual_grounding", bt, retryable=False)
                result = await gf(image_data=image_data, query=query, image_format=image_format, timeout=timeout)
            else:
                of = getattr(backend, "observe", None)
                if of is None:
                    raise BackendError(f"Backend {bt.value} has no observe", bt, retryable=False)
                obs = await of(query, timeout=timeout)
                first = obs[0] if obs else {}
                result = VisualGroundingResult(
                    success=bool(obs),
                    prompt=query,
                    bounding_box=first.get("bounding_box") or first.get("bbox"),
                    confidence=first.get("confidence"),
                    backend_used=bt,
                    latency_ms=(time.perf_counter() - start) * 1000,
                    metadata={"observations": obs},
                )
            await self._circuits[bt].record_success((time.perf_counter() - start) * 1000)
            return result
        except Exception as e:
            await self._circuits[bt].record_failure(str(e))
            raise

    async def screenshot(self, url, *, prefer_free=True, full_page=False, timeout=None):
        if prefer_free:
            free = [b for b in BACKEND_PRIORITY.get(BrowserOperation.SCREENSHOT, []) if BACKEND_COST.get(b, 999) == 0]
            bt = None
            for c in free:
                if c in self._backends and await self._circuits[c].can_execute():
                    bt = c
                    break
        else:
            bt = await self.select_backend(BrowserOperation.SCREENSHOT)
        if bt is None:
            raise NoBackendError(BrowserOperation.SCREENSHOT.value)
        backend = self._backends[bt]
        sf = getattr(backend, "screenshot", None)
        if sf is None:
            raise BackendError(f"Backend {bt.value} has no screenshot", bt, retryable=False)
        start = time.perf_counter()
        try:
            result = await sf(url=url, full_page=full_page, timeout=timeout)
            await self._circuits[bt].record_success((time.perf_counter() - start) * 1000)
            return result
        except Exception as e:
            await self._circuits[bt].record_failure(str(e))
            raise


_router = None
def get_router():
    global _router
    if _router is None:
        _router = BackendRouter()
    return _router
