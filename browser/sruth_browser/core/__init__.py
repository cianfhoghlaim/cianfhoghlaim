"""Browser core infrastructure - LLM routing, durable execution, sessions.

Components:
- LLMRouter: Multi-provider LLM fallback with circuit breaker
- RestatePlugin: Durable execution for multi-step agent pipelines
- SessionManager: Browser session state management with migration support
"""

from .llm_router import (
    LLMProvider,
    LLMResponse,
    LLMRouter,
    ProviderHealth,
    get_llm_router,
)
from .restate import (
    Awakeable,
    AwakeableManager,
    RestateClient,
    RestateContext,
    RestatePlugin,
    RestateSessionService,
    get_restate_plugin,
    init_restate,
)
from .session import (
    BrowserSession,
    SessionManager,
)

__all__ = [
    # LLM Router
    "LLMProvider",
    "LLMResponse",
    "LLMRouter",
    "ProviderHealth",
    "get_llm_router",
    # Restate
    "Awakeable",
    "AwakeableManager",
    "RestateClient",
    "RestateContext",
    "RestatePlugin",
    "RestateSessionService",
    "get_restate_plugin",
    "init_restate",
    # Session
    "BrowserSession",
    "SessionManager",
]
