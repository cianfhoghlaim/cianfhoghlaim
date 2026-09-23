"""uoa_portal — Google ADK 5-stage SequentialAgent for the authenticated
University of Galway portal pipeline (regexam.nuigalway.ie + Canvas).

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

The 5-stage pipeline mirrors the BIEP v3 5-phase pattern:

  1. auth        — resolve the user's M365 session; emit
                   `adk_request_credential` if no cookies exist
  2. browse      — drive the Patchright browser to navigate + screenshot
  3. vision      — interpret the screenshot via Gemini 2.5 Pro vision
  4. download    — stream the selected files to Lakehouse (MotherDuck)
  5. embed       — embed the extracted text into LanceDB per CocoIndex

Sub-agents cover 5 specialist workflows (mirrors the SU root's
sub_agents pattern):
  - regexam_past_papers   — regexam.nuigalway.ie past paper scraper
  - canvas_modules         — Canvas course material downloader
  - module_subset_picker   — the "which subset?" interactive agent
  - vision_interpreter     — Gemini 2.5 Pro vision-language interpreter
  - lakehouse_uploader     — MotherDuck + LanceDB uploader

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# BAML client (graceful degradation)
try:
    from baml_client import b  # type: ignore[import-not-found]

    _BAML_AVAILABLE = True
except Exception:
    _BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]


# LiteLLM routing (per the KCG minimax 7-tier alias pattern)
try:
    from google.adk.models.lite_llm import LiteLlm  # type: ignore[import-not-found]

    _LITELLM_AVAILABLE = True
except Exception:
    _LITELLM_AVAILABLE = False
    LiteLlm = None  # type: ignore[assignment]


def _get_llm() -> Any:
    """Resolve the KCG `minimax` 7-tier LiteLLM alias."""
    if not _LITELLM_AVAILABLE:
        return "gemini-2.5-flash"
    return LiteLlm(  # type: ignore[call-arg]
        model="minimax",
        api_base=os.getenv("LITELLM_API_BASE", "https://litellm.cianfhoghlaim.ie"),
    )


def _get_vision_llm() -> str:
    """Resolve the vision-language model (Gemini 2.5 Pro direct)."""
    return "gemini-2.5-pro"


# Lazy imports to avoid hard ADK dependency
def _build_root_agent() -> Any:
    from google.adk.agents import SequentialAgent

    from .tools.uoa_browse import uoa_browse_and_select_tool
    from .tools.uoa_vision import uoa_vision_interpret_tool
    from .tools.stream_to_lakehouse import stream_to_lakehouse_tool
    from .tools.baml_extract_uoa_portal import baml_extract_uoa_portal_tool
    from .tools.cocoindex_upsert import cocoindex_upsert_tool

    return SequentialAgent(
        name="uoa_portal_pipeline",
        sub_agents=[
            _build_auth_agent(),
            _build_browse_agent(),
            _build_vision_agent(),
            _build_download_agent(),
            _build_embed_agent(),
        ],
    )


def _build_auth_agent() -> Any:
    from google.adk.agents import LlmAgent

    return LlmAgent(
        name="auth",
        model=_get_llm(),
        description="Resolves the user's M365 session for regexam.nuigalway.ie + Canvas.",
        instruction="""
You are the auth sub-agent of the UoA portal pipeline. Resolve the
user's M365 session by checking
`/stedding/user_profiles/<user_id>/{regexam,canvas}/cookies.json`.

If no cookies exist, emit `adk_request_credential` for the
`OpenIdConnectWithConfig` scheme:
- authorization_endpoint: https://login.microsoftonline.com/common/oauth2/v2.0/authorize
- token_endpoint:        https://login.microsoftonline.com/common/oauth2/v2.0/token
- scopes:                 ["openid", "User.Read", "Files.Read"]

Otherwise, surface the existing cookie path.
""",
    )


def _build_browse_agent() -> Any:
    from google.adk.agents import LlmAgent

    return LlmAgent(
        name="browse",
        model=_get_llm(),
        description="Drives the Patchright browser to navigate + screenshot.",
        instruction="""
You are the browse sub-agent. Use the `uoa_browse_and_select` tool to
navigate the UoG portal pages (regexam.nuigalway.ie or
canvas.universityofgalway.ie), take a screenshot, and return the
screenshot + the page URL.

For regexam: navigate the cascading dropdowns (faculty → department
→ programme → module → year → paper type) + extract the PDF link.

For Canvas: navigate the per-module Files page + list the available
files.

If the user has provided a module subset (e.g. "CS203, MA101"), pass
that to the tool; otherwise emit `uoa_request_subset` to ask the user
which subset they want.
""",
    )


def _build_vision_agent() -> Any:
    from google.adk.agents import LlmAgent

    return LlmAgent(
        name="vision",
        model=_get_vision_llm(),
        description="Interprets screenshots via Gemini 2.5 Pro vision.",
        instruction="""
You are the vision sub-agent. Use the `uoa_vision_interpret` tool to
send the screenshot to Gemini 2.5 Pro for interpretation. The
interpretation extracts:
- module_code (e.g. 'CS203')
- paper_year (e.g. 2024)
- file_type (pdf/docx/pptx/mp4)
- title
- selection_question (the "which subset?" prompt for the user)

Return a structured interpretation as JSON.
""",
    )


def _build_download_agent() -> Any:
    from google.adk.agents import LlmAgent

    return LlmAgent(
        name="download",
        model=_get_llm(),
        description="Streams the selected files to Lakehouse + extracts via BAML.",
        instruction="""
You are the download sub-agent. Use the `stream_to_lakehouse` tool to
download the selected file to /stedding/user_profiles/<user_id>/downloads/
+ upload to the `cianfhoghlaim.tertiary.uog.user_<user_id>_<service>` table
in MotherDuck. Then use the `baml_extract_uoa_portal` tool to extract
the structured content via the UoAPortalContent BAML class.
""",
    )


def _build_embed_agent() -> Any:
    from google.adk.agents import LlmAgent

    return LlmAgent(
        name="embed",
        model=_get_llm(),
        description="Embeds the extracted text into LanceDB per CocoIndex.",
        instruction="""
You are the embed sub-agent. Use the `cocoindex_upsert` tool to embed
the extracted text via BAAI/bge-m3 (1024-d multilingual) + write to
the `uog_user_<user_id>_<service>_chunks` LanceDB table.
""",
    )


def build_root_agent() -> Any:
    """Public entrypoint — returns the 5-stage SequentialAgent."""
    return _build_root_agent()


uoa_portal_pipeline = build_root_agent()

__all__ = [
    "build_root_agent",
    "uoa_portal_pipeline",
]
