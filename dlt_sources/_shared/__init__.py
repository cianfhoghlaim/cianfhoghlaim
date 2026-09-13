"""Shared DLT sources used across multiple jurisdictions.

Per the openspec change
`2026-09-06-adk-gemini-deep-research-control-plane-v1`, this sub-package
holds cross-jurisdiction DLT sources that wrap external APIs.
"""

from .gemini_deep_research import gemini_deep_research_source

__all__ = ["gemini_deep_research_source"]
