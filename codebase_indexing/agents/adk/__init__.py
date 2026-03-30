"""
Crypteolas ADK (Agent Developer Kit) Agents.

Google ADK-based agents for crypto protocol research and analysis:
- root_agent: Coordinator agent for routing queries
- protocol_research: Protocol analysis and research
- code_analysis: Semantic code search and pattern detection
- architecture_agent: Repository architecture and dependency analysis
- defi_analytics: DeFi metrics and protocol analysis
- documentation_agent: Documentation generation
"""

__all__ = [
    "get_root_agent",
    "app",
    "protocol_research_agent",
    "code_analysis_agent",
    "architecture_agent",
    "defi_analytics_agent",
    "documentation_agent",
]


def __getattr__(name: str):
    """Lazy import agents to avoid circular dependencies."""
    if name == "get_root_agent":
        from .root_agent import get_root_agent
        return get_root_agent
    elif name == "app":
        from .root_agent import app
        return app
    elif name == "root_agent":
        # Backwards compatibility - return the get function
        from .root_agent import get_root_agent
        return get_root_agent()
    elif name == "protocol_research_agent":
        from .protocol_research import protocol_research_agent
        return protocol_research_agent
    elif name == "code_analysis_agent":
        from .code_analysis import code_analysis_agent
        return code_analysis_agent
    elif name == "architecture_agent":
        from .architecture_agent import architecture_agent
        return architecture_agent
    elif name == "defi_analytics_agent":
        from .defi_analytics import defi_analytics_agent
        return defi_analytics_agent
    elif name == "documentation_agent":
        from .documentation_agent import documentation_agent
        return documentation_agent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
