"""Agent definitions for crypteolas."""

# Lazy imports to avoid circular dependencies at module load time
__all__ = ["adk", "tools", "agno", "hitl", "callbacks"]


def __getattr__(name: str):
    """Lazy import submodules."""
    if name == "adk":
        from . import adk
        return adk
    elif name == "tools":
        from . import tools
        return tools
    elif name == "agno":
        from . import agno
        return agno
    elif name == "hitl":
        from . import hitl
        return hitl
    elif name == "callbacks":
        from . import callbacks
        return callbacks
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
