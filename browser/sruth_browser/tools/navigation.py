"""Navigation tools for browser automation."""

from google.adk.tools import FunctionTool

from ..backends.router import get_router
from ..core.types import BrowserOperation


async def navigate(
    url: str,
    wait_until: str = "load",
    timeout: float | None = None,
) -> dict:
    """Navigate to a URL.

    Args:
        url: Target URL
        wait_until: Wait condition (load, domcontentloaded, networkidle)
        timeout: Navigation timeout in seconds

    Returns:
        Navigation result with final URL and title
    """
    router = get_router()

    async def _navigate(backend):
        result = await backend.navigate(url, wait_until=wait_until, timeout=timeout)
        return {
            "success": result.success,
            "url": result.url,
            "title": result.title,
            "status_code": result.status_code,
            "backend": result.backend_used.value,
            "latency_ms": result.latency_ms,
            "error": result.error,
        }

    return await router.execute_with_fallback(BrowserOperation.NAVIGATE, _navigate)


async def go_back() -> dict:
    """Navigate back in browser history.

    Returns:
        Navigation result
    """
    router = get_router()

    async def _back(backend):
        # Use CDP-level navigation
        result = await backend.interact("back")
        return {
            "success": result.success,
            "action": "back",
            "error": result.error,
        }

    return await router.execute_with_fallback(BrowserOperation.NAVIGATE, _back)


async def go_forward() -> dict:
    """Navigate forward in browser history.

    Returns:
        Navigation result
    """
    router = get_router()

    async def _forward(backend):
        result = await backend.interact("forward")
        return {
            "success": result.success,
            "action": "forward",
            "error": result.error,
        }

    return await router.execute_with_fallback(BrowserOperation.NAVIGATE, _forward)


async def reload(ignore_cache: bool = False) -> dict:
    """Reload the current page.

    Args:
        ignore_cache: Whether to bypass cache

    Returns:
        Reload result
    """
    router = get_router()

    async def _reload(backend):
        result = await backend.interact("reload")
        return {
            "success": result.success,
            "action": "reload",
            "ignore_cache": ignore_cache,
            "error": result.error,
        }

    return await router.execute_with_fallback(BrowserOperation.NAVIGATE, _reload)


async def click_coordinates(
    x: int,
    y: int,
    button: str = "left",
    click_count: int = 1,
) -> dict:
    """Click at specific pixel coordinates.

    This is the fallback for visual healing when CSS selectors fail.
    After using GLM-4.6v to find element coordinates, call this to click.

    Args:
        x: X coordinate in pixels
        y: Y coordinate in pixels
        button: Mouse button (left, right, middle)
        click_count: Number of clicks (1 for single, 2 for double)

    Returns:
        Click result with success status

    Example:
        # After visual healing found coordinates
        result = await click_coordinates(450, 300)
    """
    router = get_router()

    async def _click(backend):
        if hasattr(backend, "click_coordinates"):
            result = await backend.click_coordinates(x, y, button=button, click_count=click_count)
            return {
                "success": result.success,
                "action": f"click_coordinates({x}, {y})",
                "coordinates": {"x": x, "y": y},
                "button": button,
                "click_count": click_count,
                "backend": result.backend_used.value,
                "latency_ms": result.latency_ms,
                "error": result.error,
            }
        else:
            return {
                "success": False,
                "action": f"click_coordinates({x}, {y})",
                "error": f"Backend {backend.backend_type.value} does not support coordinate clicks",
            }

    return await router.execute_with_fallback(BrowserOperation.INTERACT, _click)


async def scroll_to_coordinates(
    x: int,
    y: int,
) -> dict:
    """Scroll to specific coordinates.

    Args:
        x: Target X scroll position
        y: Target Y scroll position

    Returns:
        Scroll result
    """
    router = get_router()

    async def _scroll(backend):
        result = await backend.interact(f"scroll_to({x}, {y})")
        return {
            "success": result.success,
            "action": f"scroll_to({x}, {y})",
            "coordinates": {"x": x, "y": y},
            "error": result.error,
        }

    return await router.execute_with_fallback(BrowserOperation.INTERACT, _scroll)


async def hover_coordinates(
    x: int,
    y: int,
) -> dict:
    """Hover at specific coordinates.

    Useful for triggering hover states without needing a selector.

    Args:
        x: X coordinate in pixels
        y: Y coordinate in pixels

    Returns:
        Hover result
    """
    router = get_router()

    async def _hover(backend):
        if hasattr(backend, "hover_coordinates"):
            result = await backend.hover_coordinates(x, y)
            return {
                "success": result.success,
                "action": f"hover_coordinates({x}, {y})",
                "coordinates": {"x": x, "y": y},
                "error": result.error,
            }
        else:
            return {
                "success": False,
                "action": f"hover_coordinates({x}, {y})",
                "error": f"Backend {backend.backend_type.value} does not support coordinate hover",
            }

    return await router.execute_with_fallback(BrowserOperation.INTERACT, _hover)


# Create ADK tools
navigate_tool = FunctionTool(navigate)
back_tool = FunctionTool(go_back)
forward_tool = FunctionTool(go_forward)
reload_tool = FunctionTool(reload)
click_coords_tool = FunctionTool(click_coordinates)
scroll_coords_tool = FunctionTool(scroll_to_coordinates)
hover_coords_tool = FunctionTool(hover_coordinates)
