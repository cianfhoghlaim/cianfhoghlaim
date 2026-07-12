"""Screenshot tools for visual capture and analysis."""

from typing import Literal

from google.adk.tools import FunctionTool

from ..backends.router import get_router
from ..core.types import BrowserOperation


async def capture_screenshot(
    url: str | None = None,
    full_page: bool = False,
    selector: str | None = None,
    format: Literal["png", "jpeg", "webp"] = "png",
) -> dict:
    """Capture a screenshot of a page or element.

    Args:
        url: URL to screenshot (optional if already navigated)
        full_page: Capture full scrollable page
        selector: CSS selector for specific element
        format: Image format (png, jpeg, webp)

    Returns:
        Screenshot result with base64 image data
    """
    router = get_router()

    async def _screenshot(backend):
        result = await backend.screenshot(
            url=url,
            full_page=full_page,
            selector=selector,
        )
        return {
            "success": result.success,
            "url": result.url,
            "image_data": result.image_data,
            "format": result.format,
            "width": result.width,
            "height": result.height,
            "backend": result.backend_used.value,
            "latency_ms": result.latency_ms,
            "error": result.error,
        }

    return await router.execute_with_fallback(BrowserOperation.SCREENSHOT, _screenshot)


async def analyze_screenshot(
    url: str,
    prompt: str,
    full_page: bool = False,
) -> dict:
    """Capture and analyze a screenshot using vision AI.

    Uses Z.AI or similar vision model to analyze page content.

    Args:
        url: URL to screenshot and analyze
        prompt: Analysis prompt (what to look for)
        full_page: Capture full scrollable page

    Returns:
        Analysis result with insights
    """
    # First capture screenshot
    screenshot_result = await capture_screenshot(
        url=url,
        full_page=full_page,
    )

    if not screenshot_result.get("success"):
        return {
            "success": False,
            "url": url,
            "error": screenshot_result.get("error", "Screenshot failed"),
        }

    # For now, return the screenshot
    # TODO: Integrate with Z.AI vision MCP for analysis
    return {
        "success": True,
        "url": url,
        "screenshot": screenshot_result.get("image_data"),
        "analysis": "Vision analysis not yet integrated",
        "prompt": prompt,
    }


# Create ADK tools
screenshot_tool = FunctionTool(capture_screenshot)
analyze_tool = FunctionTool(analyze_screenshot)
