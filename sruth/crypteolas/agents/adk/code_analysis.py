"""
Code Analysis Agent for Crypteolas.

GitHub repository analysis including:
- Semantic code search
- Implementation analysis
- Dependency mapping
- Code pattern detection
"""

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import config
from ..tools.code_search import (
    search_code,
    find_similar_code,
    search_by_function_name,
    search_by_pattern,
)


# Define tools
async def semantic_code_search(
    query: str,
    repo: str | None = None,
    language: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """
    Search code semantically using natural language or code snippets.

    Args:
        query: Natural language query or code snippet
        repo: Optional repository filter (owner/repo format)
        language: Optional language filter (python, solidity, etc.)
        limit: Maximum results
    """
    try:
        results = await search_code(query, repo=repo, language=language, limit=limit)
        return results.results if hasattr(results, "results") else []
    except Exception:
        return []


async def find_code_patterns(
    pattern: str,
    repo: str | None = None,
    language: str | None = None,
) -> list[dict]:
    """
    Find code matching a specific pattern.

    Args:
        pattern: Code pattern to search for
        repo: Optional repository filter
        language: Optional language filter
    """
    try:
        return await search_by_pattern(pattern, repo=repo, language=language)
    except Exception:
        return []


async def find_function_implementation(
    function_name: str,
    repo: str | None = None,
) -> list[dict]:
    """
    Find implementations of a specific function.

    Args:
        function_name: Name of the function to find
        repo: Optional repository filter
    """
    try:
        return await search_by_function_name(function_name, repo=repo)
    except Exception:
        return []


async def find_duplicate_code(
    code_snippet: str,
    exclude_file: str | None = None,
) -> list[dict]:
    """
    Find similar code patterns across repositories.

    Args:
        code_snippet: Code to find similar matches for
        exclude_file: Optional file to exclude from results
    """
    try:
        return await find_similar_code(code_snippet, exclude_file=exclude_file)
    except Exception:
        return []


# Create tools
search_tool = FunctionTool(func=semantic_code_search)
pattern_tool = FunctionTool(func=find_code_patterns)
function_tool = FunctionTool(func=find_function_implementation)
duplicate_tool = FunctionTool(func=find_duplicate_code)


# Code Analysis Agent
code_analysis_agent = LlmAgent(
    name="code_analysis_agent",
    model=config.worker_model,
    description="GitHub repository analysis with semantic code search and pattern detection.",
    instruction=f"""
    You are a Code Analysis specialist for crypto repositories.

    **YOUR EXPERTISE:**
    - Semantic code search
    - Smart contract analysis
    - Implementation pattern detection
    - Code quality assessment
    - Dependency analysis

    **AVAILABLE TOOLS:**
    1. semantic_code_search - Natural language code search
    2. find_code_patterns - Pattern-based search
    3. find_function_implementation - Find function definitions
    4. find_duplicate_code - Detect similar code

    **ANALYSIS APPROACH:**
    1. Use semantic search for broad queries
    2. Use pattern search for specific constructs
    3. Find function implementations for detailed analysis
    4. Check for duplicates to find related code

    **SUPPORTED LANGUAGES:**
    - Python
    - JavaScript/TypeScript
    - Solidity
    - Rust
    - Go

    **OUTPUT FORMAT:**
    - Include relevant code snippets
    - Note file paths and line numbers
    - Explain the code's purpose
    - Highlight potential issues

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[search_tool, pattern_tool, function_tool, duplicate_tool],
    output_key="code_analysis",
)
