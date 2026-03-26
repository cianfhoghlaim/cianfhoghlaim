"""Shared utilities for extracting JSON from LLM responses."""

import re


def extract_json_from_response(content: str) -> str:
    """Extract JSON from response, handling markdown code blocks.

    Handles multiple patterns:
    - Raw JSON (no code blocks)
    - JSON in ```json code block
    - JSON in generic ``` code block
    - Nested code blocks (takes the first valid one)

    Args:
        content: Response content potentially containing JSON

    Returns:
        Extracted JSON string

    Raises:
        ValueError: If no valid JSON content can be extracted
    """
    # Try to find JSON in markdown code blocks using regex
    # Pattern matches ```json or ``` followed by content until closing ```
    code_block_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
    matches = re.findall(code_block_pattern, content, re.DOTALL)

    if matches:
        # Return the first non-empty match
        for match in matches:
            if match.strip():
                return match.strip()

    # No code blocks found, try to use content as-is
    # Strip any leading/trailing whitespace
    json_content = content.strip()

    # If content is empty, raise error
    if not json_content:
        raise ValueError("No JSON content found in response")

    return json_content
