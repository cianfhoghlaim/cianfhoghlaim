"""Form automation tools."""

from typing import Any

from google.adk.tools import FunctionTool

from ..backends.router import get_router
from ..core.types import BrowserOperation


async def fill_form(
    url: str | None = None,
    fields: dict[str, str] | None = None,
    form_goal: str | None = None,
) -> dict:
    """Fill a form with specified field values.

    Can use either explicit field mappings or a natural language goal.

    Args:
        url: URL containing the form (optional if already navigated)
        fields: Dictionary mapping field identifiers to values
        form_goal: Natural language description of form filling goal

    Returns:
        Form fill result
    """
    router = get_router()

    if not fields and not form_goal:
        return {
            "success": False,
            "error": "Either fields or form_goal must be provided",
        }

    async def _fill(backend):
        # Navigate if URL provided
        if url:
            nav_result = await backend.navigate(url)
            if not nav_result.success:
                return {
                    "success": False,
                    "error": f"Navigation failed: {nav_result.error}",
                }

        # Fill form
        if fields:
            result = await backend.fill_form(fields)
        else:
            # For natural language goals, use Skyvern-style task
            # This converts the goal to field interactions
            result = await backend.interact(
                action=f"Fill the form: {form_goal}",
            )

        return {
            "success": result.success,
            "action": "fill_form",
            "fields_filled": len(fields) if fields else None,
            "goal": form_goal,
            "error": result.error,
        }

    return await router.execute_with_fallback(BrowserOperation.FORM, _fill)


async def submit_form(
    submit_selector: str | None = None,
    submit_text: str = "Submit",
    wait_for_navigation: bool = True,
) -> dict:
    """Submit a form by clicking the submit button.

    Args:
        submit_selector: CSS selector for submit button
        submit_text: Text of submit button (used if selector not provided)
        wait_for_navigation: Wait for page navigation after submit

    Returns:
        Submit result
    """
    router = get_router()

    async def _submit(backend):
        if submit_selector:
            result = await backend.interact(
                action="click",
                selector=submit_selector,
            )
        else:
            result = await backend.interact(
                action=f"click the '{submit_text}' button",
            )

        return {
            "success": result.success,
            "action": "submit",
            "selector": submit_selector,
            "text": submit_text,
            "error": result.error,
        }

    return await router.execute_with_fallback(BrowserOperation.FORM, _submit)


async def fill_and_submit(
    url: str,
    fields: dict[str, str],
    submit_selector: str | None = None,
    submit_text: str = "Submit",
) -> dict:
    """Fill a form and submit it in one operation.

    Args:
        url: URL containing the form
        fields: Field values to fill
        submit_selector: Submit button selector
        submit_text: Submit button text

    Returns:
        Combined fill and submit result
    """
    # Fill the form
    fill_result = await fill_form(url=url, fields=fields)

    if not fill_result.get("success"):
        return fill_result

    # Submit
    submit_result = await submit_form(
        submit_selector=submit_selector,
        submit_text=submit_text,
    )

    return {
        "success": submit_result.get("success"),
        "fill_result": fill_result,
        "submit_result": submit_result,
        "error": submit_result.get("error"),
    }


# Create ADK tools
fill_tool = FunctionTool(fill_form)
submit_tool = FunctionTool(submit_form)
fill_submit_tool = FunctionTool(fill_and_submit)
