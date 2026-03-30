"""Evaluator Agent - Quality validation and fallback escalation.

The Evaluator is the quality control phase in the browsing pipeline.
It validates extraction results and triggers fallbacks when needed:
- Schema validation (BAML)
- Content quality assessment
- Fallback escalation to paid services
- Visual healing (selector failure recovery via GLM-4.6v)
- Result aggregation
"""

import structlog
from typing import Any, Literal

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

from ..backends import get_router
from ..config import get_config
from ..exceptions import FallbackExhaustedError
from ..browser_types import BackendType, BrowserOperation

logger = structlog.get_logger()


class QualityAssessment(BaseModel):
    """Model for quality assessment result."""

    grade: Literal["pass", "fail"] = Field(
        description="Pass if quality is acceptable, fail if retry needed"
    )
    score: float = Field(
        ge=0, le=1,
        description="Quality score between 0 and 1"
    )
    issues: list[str] = Field(
        default_factory=list,
        description="List of quality issues found"
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Suggestions for improvement"
    )
    should_fallback: bool = Field(
        default=False,
        description="Whether to escalate to paid fallback"
    )


class ValidationResult(BaseModel):
    """Model for schema validation result."""

    valid: bool = Field(description="Whether data matches schema")
    errors: list[str] = Field(
        default_factory=list,
        description="Validation errors found"
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description="Required fields that are missing"
    )


class VisualHealingResult(BaseModel):
    """Result of visual healing workflow."""

    success: bool = Field(description="Whether element was found")
    coordinates: dict[str, float] | None = Field(
        default=None,
        description="Click coordinates {x, y} as fractions of viewport"
    )
    pixel_coords: dict[str, int] | None = Field(
        default=None,
        description="Click coordinates in pixels"
    )
    method: str = Field(
        default="visual_grounding",
        description="Method used to find element"
    )
    error: str | None = Field(default=None, description="Error if failed")


async def visual_healing(
    screenshot_path: str,
    element_description: str,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    failed_selector: str | None = None,
) -> dict:
    """Recover from selector failure using visual grounding.

    When a CSS selector fails, this workflow:
    1. Takes the provided screenshot
    2. Sends to GLM-4.6v with element description
    3. Returns click coordinates

    Args:
        screenshot_path: Path to screenshot (captured after selector failed)
        element_description: Description of element to find
            e.g., "the blue 'Login' button", "the search input field"
        viewport_width: Browser viewport width
        viewport_height: Browser viewport height
        failed_selector: The selector that failed (for logging)

    Returns:
        VisualHealingResult with coordinates if found

    Example:
        result = await visual_healing(
            "/tmp/page_screenshot.png",
            "the 'Submit' button at the bottom of the form",
            viewport_width=1920,
            viewport_height=1080
        )
        if result["success"]:
            await page.mouse.click(
                result["pixel_coords"]["x"],
                result["pixel_coords"]["y"]
            )
    """
    config = get_config()

    if not config.enable_visual_healing:
        return {
            "success": False,
            "coordinates": None,
            "pixel_coords": None,
            "method": "visual_grounding",
            "error": "Visual healing is disabled in config",
        }

    if not config.has_zai:
        return {
            "success": False,
            "coordinates": None,
            "pixel_coords": None,
            "method": "visual_grounding",
            "error": "Z.AI API key not configured for visual healing",
        }

    try:
        from ..tools import visual_grounding

        logger.info(
            "visual_healing_attempt",
            element=element_description,
            failed_selector=failed_selector,
        )

        prompt = f"Find the center coordinates of: {element_description}"
        result = await visual_grounding(screenshot_path, prompt)

        if result.success and result.coordinates:
            x_frac = result.coordinates["x"]
            y_frac = result.coordinates["y"]

            pixel_x = int(x_frac * viewport_width)
            pixel_y = int(y_frac * viewport_height)

            logger.info(
                "visual_healing_success",
                element=element_description,
                coordinates=result.coordinates,
                pixel_coords={"x": pixel_x, "y": pixel_y},
            )

            return {
                "success": True,
                "coordinates": result.coordinates,
                "pixel_coords": {"x": pixel_x, "y": pixel_y},
                "method": "visual_grounding",
                "error": None,
            }

        logger.warning(
            "visual_healing_failed",
            element=element_description,
            error=result.error,
        )

        return {
            "success": False,
            "coordinates": None,
            "pixel_coords": None,
            "method": "visual_grounding",
            "error": result.error or "Could not locate element visually",
        }

    except Exception as e:
        logger.error("visual_healing_error", error=str(e))
        return {
            "success": False,
            "coordinates": None,
            "pixel_coords": None,
            "method": "visual_grounding",
            "error": str(e),
        }


async def heal_and_click(
    screenshot_path: str,
    element_description: str,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
) -> dict:
    """Visual healing + click execution helper.

    Combines visual healing with CDP click execution.
    Use this when you have a description but no selector.

    Args:
        screenshot_path: Path to screenshot
        element_description: Description of element to click
        viewport_width: Viewport width
        viewport_height: Viewport height

    Returns:
        Result with success status and click details
    """
    healing_result = await visual_healing(
        screenshot_path,
        element_description,
        viewport_width,
        viewport_height,
    )

    if not healing_result["success"]:
        return {
            "success": False,
            "error": healing_result["error"],
            "healing_result": healing_result,
        }

    try:
        router = get_router()
        cdp_backend = router.get_backend(BackendType.CDP_LOCAL)

        if cdp_backend and hasattr(cdp_backend, "click_coordinates"):
            click_result = await cdp_backend.click_coordinates(
                healing_result["pixel_coords"]["x"],
                healing_result["pixel_coords"]["y"],
            )
            return {
                "success": click_result.success,
                "coordinates": healing_result["coordinates"],
                "pixel_coords": healing_result["pixel_coords"],
                "click_result": click_result,
            }
        else:
            return {
                "success": True,
                "coordinates": healing_result["coordinates"],
                "pixel_coords": healing_result["pixel_coords"],
                "note": "CDP click_coordinates not available, use pixel_coords manually",
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Click failed: {e}",
            "coordinates": healing_result["coordinates"],
            "pixel_coords": healing_result["pixel_coords"],
        }


async def validate_schema(
    data: dict,
    schema_name: str,
) -> dict:
    """Validate extracted data against a BAML schema.

    Args:
        data: Extracted data to validate
        schema_name: Name of BAML schema to use

    Returns:
        Validation result with errors if any
    """
    # TODO: Integrate with actual BAML validation
    # For now, do basic structure validation
    errors = []
    missing = []

    if not data:
        return {
            "valid": False,
            "errors": ["Data is empty"],
            "missing_fields": [],
        }

    # Check for common required fields based on schema name
    schema_requirements = {
        "CurriculumSpecification": ["title", "subject", "level", "source_url"],
        "ExamPaper": ["title", "subject", "year", "questions"],
        "TeachingResource": ["title", "resource_type", "source_url"],
        "TermEntry": ["term", "domain"],
    }

    required = schema_requirements.get(schema_name, [])
    for field in required:
        if field not in data or data.get(field) is None:
            missing.append(field)

    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "missing_fields": missing,
    }


async def assess_quality(
    content: dict,
    expected_type: str = "general",
    min_length: int = 100,
) -> dict:
    """Assess the quality of extracted content.

    Args:
        content: Extracted content to assess
        expected_type: Type of content (article, curriculum, exam, etc.)
        min_length: Minimum expected content length

    Returns:
        Quality assessment with score and issues
    """
    issues = []
    score = 1.0

    # Check if content exists
    if not content:
        return {
            "grade": "fail",
            "score": 0.0,
            "issues": ["No content extracted"],
            "suggestions": ["Try different extraction format or backend"],
            "should_fallback": True,
        }

    # Check content length
    text_content = ""
    if "markdown" in content:
        text_content = content["markdown"]
    elif "text" in content:
        text_content = content["text"]
    elif "html" in content:
        text_content = content["html"]

    if len(text_content) < min_length:
        issues.append(f"Content too short ({len(text_content)} < {min_length} chars)")
        score -= 0.3

    # Check for error indicators
    error_phrases = [
        "access denied",
        "403 forbidden",
        "404 not found",
        "captcha",
        "please enable javascript",
        "blocked",
    ]
    text_lower = text_content.lower()
    for phrase in error_phrases:
        if phrase in text_lower:
            issues.append(f"Possible access issue: '{phrase}' found in content")
            score -= 0.4

    # Check for extracted structured data
    if "extracted" in content:
        extracted = content["extracted"]
        if not extracted or (isinstance(extracted, dict) and len(extracted) == 0):
            issues.append("Structured extraction returned empty")
            score -= 0.2

    # Determine grade
    grade = "pass" if score >= 0.6 else "fail"
    should_fallback = score < 0.4

    suggestions = []
    if should_fallback:
        suggestions.append("Consider using paid fallback (Firecrawl/Browserbase)")
    if "access denied" in str(issues).lower():
        suggestions.append("Try Stagehand for interactive bypass")

    return {
        "grade": grade,
        "score": max(0.0, score),
        "issues": issues,
        "suggestions": suggestions,
        "should_fallback": should_fallback,
    }


async def escalate_to_fallback(
    operation: str,
    url: str,
    reason: str,
) -> dict:
    """Escalate operation to paid fallback service.

    Args:
        operation: Operation type (extract, navigate, interact)
        url: Target URL
        reason: Reason for escalation

    Returns:
        Fallback result
    """
    router = get_router()

    # Map operation string to enum
    op_map = {
        "extract": BrowserOperation.EXTRACT,
        "scrape": BrowserOperation.SCRAPE,
        "navigate": BrowserOperation.NAVIGATE,
        "interact": BrowserOperation.INTERACT,
        "research": BrowserOperation.RESEARCH,
    }
    browser_op = op_map.get(operation.lower(), BrowserOperation.SCRAPE)

    # Force use of paid backends
    paid_backends = [BackendType.FIRECRAWL_MCP, BackendType.BROWSERBASE_MCP]

    for backend_type in paid_backends:
        backend = router.get_backend(backend_type)
        if not backend:
            continue

        try:
            if browser_op == BrowserOperation.EXTRACT:
                result = await backend.extract(url)
                if result.success:
                    return {
                        "success": True,
                        "backend": backend_type.value,
                        "content": result.content,
                    }
            elif browser_op == BrowserOperation.NAVIGATE:
                result = await backend.navigate(url)
                if result.success:
                    return {
                        "success": True,
                        "backend": backend_type.value,
                        "url": result.url,
                    }
        except Exception as e:
            continue

    return {
        "success": False,
        "error": "All fallback backends exhausted",
        "tried": [b.value for b in paid_backends],
    }


async def aggregate_results(
    results: list[dict],
    dedup_key: str | None = None,
) -> dict:
    """Aggregate multiple extraction results.

    Args:
        results: List of extraction results
        dedup_key: Optional key to deduplicate by

    Returns:
        Aggregated results
    """
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]

    # Deduplicate if key provided
    if dedup_key and successful:
        seen = set()
        deduped = []
        for r in successful:
            key_value = r.get(dedup_key) or r.get("content", {}).get(dedup_key)
            if key_value and key_value not in seen:
                seen.add(key_value)
                deduped.append(r)
            elif not key_value:
                deduped.append(r)
        successful = deduped

    return {
        "success": len(successful) > 0,
        "total": len(results),
        "successful_count": len(successful),
        "failed_count": len(failed),
        "successful_results": successful,
        "failed_results": failed,
        "deduplicated": dedup_key is not None,
    }


# Create function tools for ADK
validate_tool = FunctionTool(validate_schema)
quality_tool = FunctionTool(assess_quality)
fallback_tool = FunctionTool(escalate_to_fallback)
aggregate_tool = FunctionTool(aggregate_results)
visual_healing_tool = FunctionTool(visual_healing)
heal_click_tool = FunctionTool(heal_and_click)

# Evaluator Agent Definition
evaluator_agent = LlmAgent(
    name="evaluator",
    model="gemini-2.0-flash",
    description="""Quality control agent for extraction validation and recovery.

    Capabilities:
    - Validate data against BAML schemas
    - Assess content quality and completeness
    - Escalate to paid fallbacks when needed
    - Visual healing for selector failures (GLM-4.6v)
    - Aggregate and deduplicate results

    Use this agent when:
    - Extraction quality needs verification
    - Schema validation is required
    - Fallback decision needs to be made
    - CSS selectors fail and visual recovery is needed
    - Results need aggregation
    """,
    instruction="""You are the Evaluator agent, responsible for quality control and recovery.

    Your role in the pipeline:
    1. Receive extraction results from Gatherer
    2. Validate against expected schemas
    3. Assess content quality and completeness
    4. Decide if fallback is needed
    5. Use visual healing when selectors fail
    6. Aggregate final results

    Guidelines:
    - Always validate structured data against schema
    - Check for access issues (captcha, blocked, etc.)
    - Escalate to fallback if score < 0.4
    - Use visual_healing when CSS selectors fail
    - Aggregate and deduplicate when multiple sources

    Visual Healing Workflow:
    When an interaction fails due to selector not found:
    1. Capture screenshot of current page state
    2. Call visual_healing with element description
    3. If coordinates returned, use heal_and_click to click
    4. This uses GLM-4.6v vision model for grounding

    Quality indicators:
    - Content length (too short = incomplete)
    - Error phrases (access denied, captcha)
    - Missing required fields
    - Empty structured extractions
    """,
    tools=[
        validate_tool,
        quality_tool,
        fallback_tool,
        aggregate_tool,
        visual_healing_tool,
        heal_click_tool,
    ],
    output_key="evaluator_result",
    output_schema=QualityAssessment,
)
