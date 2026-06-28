"""Z.AI vision and MCP tools for browser agent."""

from typing import Any

import structlog

from ..backends.paid.zai_backend import ZAIVisionBackend
from ..backends.paid.zai_mcp_client import get_zai_mcp_client
from ..config import get_config
from ..browser_types import BackendType, VisionAnalysisResult, VisualGroundingResult

logger = structlog.get_logger()

_zai_backend: ZAIVisionBackend | None = None


async def _get_zai_backend() -> ZAIVisionBackend:
    """Get or create Z.AI backend singleton."""
    global _zai_backend
    if _zai_backend is None:
        config = get_config()
        _zai_backend = ZAIVisionBackend(config)
        await _zai_backend.initialize()
    return _zai_backend


async def visual_grounding(
    image_source: str,
    prompt: str,
    *,
    timeout: float | None = None,
) -> VisualGroundingResult:
    """Find element coordinates in an image using GLM-4.6v visual grounding.

    This is the core function for the visual healing workflow. When a CSS
    selector fails, capture a screenshot and use this to find the element
    by visual description.

    Args:
        image_source: Path to image file, URL, or base64 data
        prompt: Description of element to find (e.g., "Find the login button")
        timeout: Optional timeout in seconds

    Returns:
        VisualGroundingResult with coordinates {x, y} normalized to [0, 1]
        or bounding_box [xmin, ymin, xmax, ymax] normalized to [0, 1000]

    Example:
        result = await visual_grounding(
            "/tmp/screenshot.png",
            "Find the 'Submit' button"
        )
        if result.success:
            # Convert normalized coords to pixel coords
            x = result.coordinates["x"] * viewport_width
            y = result.coordinates["y"] * viewport_height
            await page.mouse.click(x, y)
    """
    backend = await _get_zai_backend()
    return await backend.visual_grounding(image_source, prompt, timeout=timeout)


async def analyze_vision(
    image_source: str,
    prompt: str,
    analysis_type: str = "general",
    *,
    timeout: float | None = None,
) -> VisionAnalysisResult:
    """Analyze an image using GLM-4.6v.

    Args:
        image_source: Path to image, URL, or base64 data
        prompt: What to analyze
        analysis_type: Type of analysis
            - general: General image understanding
            - ui_to_artifact: Convert UI to code/specs
            - ocr: Extract text
            - error_diagnosis: Analyze error screenshots
            - diagram: Understand technical diagrams
            - chart: Analyze data visualizations
        timeout: Optional timeout

    Returns:
        VisionAnalysisResult with analysis content
    """
    backend = await _get_zai_backend()
    return await backend.analyze_vision(
        image_source, prompt, analysis_type, timeout=timeout
    )


async def compare_ui_images(
    expected_image: str,
    actual_image: str,
    prompt: str | None = None,
    *,
    timeout: float | None = None,
) -> VisionAnalysisResult:
    """Compare expected vs actual UI screenshots.

    Useful for visual regression testing and design QA.

    Args:
        expected_image: Path/URL to expected/reference design
        actual_image: Path/URL to actual implementation
        prompt: Custom comparison instructions
        timeout: Optional timeout

    Returns:
        VisionAnalysisResult with detailed diff report
    """
    backend = await _get_zai_backend()
    return await backend.compare_images(
        expected_image, actual_image, prompt, timeout=timeout
    )


async def ui_to_code(
    image_source: str,
    framework: str = "react",
    style_system: str = "tailwind",
) -> dict[str, Any]:
    """Convert UI screenshot to frontend code.

    Args:
        image_source: Path/URL to UI screenshot
        framework: Target framework (react, vue, svelte, html)
        style_system: CSS approach (tailwind, css, styled-components)

    Returns:
        Dict with generated code and metadata
    """
    client = await get_zai_mcp_client()
    return await client.ui_to_artifact(
        image_source,
        f"Generate {framework} code using {style_system} for this UI",
        output_type="code",
    )


async def ui_to_prompt(
    image_source: str,
) -> dict[str, Any]:
    """Generate AI prompt to recreate this UI.

    Useful for creating prompts for other AI image/UI generators.

    Args:
        image_source: Path/URL to UI screenshot

    Returns:
        Dict with generated prompt
    """
    client = await get_zai_mcp_client()
    return await client.ui_to_artifact(
        image_source,
        "Generate a detailed prompt that could recreate this UI design",
        output_type="prompt",
    )


async def ui_to_spec(
    image_source: str,
) -> dict[str, Any]:
    """Extract design specification from UI screenshot.

    Returns design tokens like colors, fonts, spacing.

    Args:
        image_source: Path/URL to UI screenshot

    Returns:
        Dict with design specification
    """
    client = await get_zai_mcp_client()
    return await client.ui_to_artifact(
        image_source,
        "Extract design specifications: colors, typography, spacing, components",
        output_type="spec",
    )


async def extract_text_ocr(
    image_source: str,
    language_hint: str | None = None,
) -> dict[str, Any]:
    """Extract text from image using OCR.

    Args:
        image_source: Path/URL to image
        language_hint: Programming language hint for code extraction

    Returns:
        Dict with extracted text
    """
    client = await get_zai_mcp_client()
    return await client.extract_text_from_screenshot(
        image_source,
        "Extract all text from this image, preserving formatting",
        programming_language=language_hint,
    )


async def diagnose_error(
    image_source: str,
    context: str | None = None,
) -> dict[str, Any]:
    """Diagnose error from screenshot with suggested fixes.

    Args:
        image_source: Path/URL to error screenshot
        context: When the error occurred (e.g., "during npm install")

    Returns:
        Dict with diagnosis and suggested solutions
    """
    client = await get_zai_mcp_client()
    return await client.diagnose_error_screenshot(
        image_source,
        "Diagnose this error and provide actionable solutions",
        context=context,
    )


async def understand_diagram(
    image_source: str,
    prompt: str,
    diagram_type: str | None = None,
) -> dict[str, Any]:
    """Analyze technical diagram.

    Args:
        image_source: Path/URL to diagram
        prompt: What to understand
        diagram_type: Type hint (architecture, flowchart, uml, er-diagram)

    Returns:
        Dict with diagram analysis
    """
    client = await get_zai_mcp_client()
    return await client.understand_technical_diagram(
        image_source, prompt, diagram_type=diagram_type
    )


async def analyze_chart(
    image_source: str,
    focus: str | None = None,
) -> dict[str, Any]:
    """Analyze data visualization.

    Args:
        image_source: Path/URL to chart/graph
        focus: Analysis focus (trends, anomalies, comparisons)

    Returns:
        Dict with chart insights
    """
    client = await get_zai_mcp_client()
    return await client.analyze_data_visualization(
        image_source,
        "Extract key insights and trends from this visualization",
        analysis_focus=focus,
    )


async def ui_diff(
    expected_image: str,
    actual_image: str,
) -> dict[str, Any]:
    """Compare expected vs actual UI for QA.

    Args:
        expected_image: Path/URL to expected design
        actual_image: Path/URL to actual implementation

    Returns:
        Dict with detailed difference report
    """
    client = await get_zai_mcp_client()
    return await client.ui_diff_check(expected_image, actual_image)


async def analyze_video(
    video_source: str,
    prompt: str,
) -> dict[str, Any]:
    """Analyze video content.

    Args:
        video_source: Path/URL to video (MP4, MOV, M4V, max 8MB)
        prompt: What to analyze

    Returns:
        Dict with video analysis
    """
    client = await get_zai_mcp_client()
    return await client.analyze_video(video_source, prompt)


async def web_search_prime(
    query: str,
    limit: int = 10,
) -> dict[str, Any]:
    """Search the web using Z.AI webSearchPrime.

    Higher quality search results than standard web search.

    Args:
        query: Search query
        limit: Maximum results

    Returns:
        Dict with search results
    """
    client = await get_zai_mcp_client()
    return await client.web_search(query, limit=limit)


async def web_reader(
    url: str,
    format: str = "markdown",
) -> dict[str, Any]:
    """Read webpage content using Z.AI webReader.

    Args:
        url: URL to read
        format: Output format (markdown, html, text)

    Returns:
        Dict with page content
    """
    client = await get_zai_mcp_client()
    return await client.web_read(url, extract_format=format)


async def search_github_docs(
    repo_url: str,
    query: str,
    limit: int = 10,
) -> dict[str, Any]:
    """Search documentation in a GitHub repository.

    Args:
        repo_url: GitHub repository URL
        query: Search query
        limit: Maximum results

    Returns:
        Dict with matching documentation
    """
    client = await get_zai_mcp_client()
    return await client.search_repo_docs(repo_url, query, limit=limit)


async def get_github_repo_structure(
    repo_url: str,
) -> dict[str, Any]:
    """Get structure of a GitHub repository.

    Args:
        repo_url: GitHub repository URL

    Returns:
        Dict with repository structure
    """
    client = await get_zai_mcp_client()
    return await client.get_repo_structure(repo_url)


async def read_github_file(
    repo_url: str,
    file_path: str,
) -> dict[str, Any]:
    """Read a file from GitHub repository.

    Args:
        repo_url: GitHub repository URL
        file_path: Path to file in repository

    Returns:
        Dict with file content
    """
    client = await get_zai_mcp_client()
    return await client.read_repo_file(repo_url, file_path)
