"""
Root Agent for Crypteolas - GitHub Intelligence + DeFi Analytics.

Orchestrates specialist agents for crypto research queries.
"""

import datetime
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner

from ..config import config


# Lazy initialization to avoid import cycles
_root_agent: LlmAgent | None = None
_runner: InMemoryRunner | None = None


def _get_sub_agents() -> list:
    """Lazy load sub-agents to avoid circular imports."""
    from .protocol_research import protocol_research_agent
    from .code_analysis import code_analysis_agent
    from .defi_analytics import defi_analytics_agent
    from .documentation_agent import documentation_agent
    return [
        protocol_research_agent,
        code_analysis_agent,
        defi_analytics_agent,
        documentation_agent,
    ]


def get_root_agent() -> LlmAgent:
    """Get or create the root agent."""
    global _root_agent
    if _root_agent is None:
        _root_agent = LlmAgent(
            name="crypteolas_agent",
            model=config.orchestrator_model,
            description="Main assistant for crypto protocol research and DeFi analytics.",
            instruction=f"""
    You are Crypteolas, an expert AI assistant for cryptocurrency and DeFi research.
    You help developers, researchers, and analysts understand:

    - Protocol architectures and code
    - DeFi metrics and analytics
    - Security audits and vulnerabilities
    - Market data and trends
    - Documentation and technical specs

    **YOUR ROLE:**
    Route queries to the appropriate specialist agent and synthesize responses.

    **SPECIALIST AGENTS:**

    1. **protocol_research_agent**
       - Deep research on DeFi protocols
       - Protocol comparison and analysis
       - Tokenomics investigation
       - Use for: "Research Uniswap v4...", "Compare Aave and Compound...", "What is the architecture of..."

    2. **code_analysis_agent**
       - GitHub repository analysis
       - Code search and understanding
       - Dependency analysis
       - Use for: "Find code that...", "How is X implemented...", "Analyze the codebase of..."

    3. **defi_analytics_agent**
       - TVL and yield analysis
       - Market metrics and trends
       - Protocol performance
       - Use for: "What is the TVL of...", "Compare yields...", "Show funding rates..."

    4. **documentation_agent**
       - Protocol documentation search
       - Whitepaper analysis
       - Audit report queries
       - Use for: "What does the docs say about...", "Find audit findings for...", "Explain from whitepaper..."

    **CAPABILITIES:**
    - Semantic code search across repositories
    - Protocol documentation RAG
    - Real-time DeFi metrics
    - Temporal knowledge graph for protocol evolution
    - Security vulnerability analysis

    **DATA SOURCES:**
    - GitHub (repos, issues, PRs, commits)
    - DeFiLlama (TVL, yields, protocols)
    - CoinGecko (prices, market data)
    - Binance (funding rates, derivatives)
    - Protocol documentation (via Firecrawl)
    - Audit reports

    **RESPONSE APPROACH:**
    1. Identify the query type (research/code/analytics/docs)
    2. Clarify scope if ambiguous (which protocols, time range)
    3. Delegate to appropriate specialist
    4. Synthesize findings with context
    5. Cite sources and data freshness

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    Always note when data may be outdated or when real-time data is unavailable.
    Be clear about confidence levels and limitations.
    """,
            sub_agents=_get_sub_agents(),
            output_key="response",
        )
    return _root_agent


# Backwards-compatible module-level reference
@property
def root_agent() -> LlmAgent:
    return get_root_agent()


class App:
    """Simple app wrapper using InMemoryRunner."""

    def __init__(self, name: str = "crypteolas"):
        self.name = name
        self._runner: InMemoryRunner | None = None

    def _get_runner(self) -> InMemoryRunner:
        if self._runner is None:
            self._runner = InMemoryRunner(agent=get_root_agent(), app_name=self.name)
        return self._runner

    async def run_async(self, message: str) -> dict[str, Any]:
        """Run the agent with a message and return the response."""
        runner = self._get_runner()
        # Create a session and run
        session = await runner.session_service.create_session(
            app_name=self.name,
            user_id="user",
        )

        result = None
        async for event in runner.run_async(
            user_id="user",
            session_id=session.id,
            new_message=message,
        ):
            # Collect the final response
            if hasattr(event, "content"):
                result = event.content

        return {"response": result or ""}


# Create the app instance
app = App(name="crypteolas")


# Query classifier for routing
def classify_query(query: str) -> str:
    """Classify query to determine best agent."""
    query_lower = query.lower()

    # Code keywords
    if any(
        kw in query_lower
        for kw in [
            "code",
            "implementation",
            "function",
            "contract",
            "solidity",
            "repository",
            "github",
            "codebase",
            "source",
            "commit",
            "pr",
            "pull request",
        ]
    ):
        return "code"

    # Analytics keywords
    if any(
        kw in query_lower
        for kw in [
            "tvl",
            "yield",
            "apy",
            "price",
            "volume",
            "liquidity",
            "funding",
            "rate",
            "market cap",
            "analytics",
            "metrics",
            "trend",
            "chart",
        ]
    ):
        return "analytics"

    # Documentation keywords
    if any(
        kw in query_lower
        for kw in [
            "docs",
            "documentation",
            "whitepaper",
            "audit",
            "specification",
            "api",
            "guide",
            "tutorial",
            "explain",
        ]
    ):
        return "documentation"

    # Default to research
    return "research"


# Export for use as library
__all__ = [
    "get_root_agent",
    "app",
    "classify_query",
    "App",
]
