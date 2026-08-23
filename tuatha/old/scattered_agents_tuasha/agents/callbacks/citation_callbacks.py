"""
Citation callbacks for Tuath Celtic Educational Game Agent.

Collects sources from grounding metadata and formats citations
for mythology, curriculum, and educational content.
"""
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from google.adk.agents.callback_context import CallbackContext
    from google.genai import types as genai_types

logger = logging.getLogger(__name__)


def collect_celtic_sources_callback(callback_context: CallbackContext) -> None:
    """
    Collect and organize educational sources from agent events.

    Extracts web source details (URLs, titles) and associated text segments
    with confidence scores from grounding metadata. Aggregates into state
    for use by the citation replacement callback.

    Sources are classified by type:
    - mythology: Celtic myths and legends
    - curriculum: NCCA, SQA, Qualifications Wales content
    - folklore: Traditional stories and customs
    - language: Grammar, vocabulary, pronunciation

    Args:
        callback_context: Context providing access to session events and state.
    """
    session = callback_context._invocation_context.session
    url_to_short_id = callback_context.state.get("url_to_short_id", {})
    sources = callback_context.state.get("sources", {})
    id_counter = len(url_to_short_id) + 1

    for event in session.events:
        if not (event.grounding_metadata and event.grounding_metadata.grounding_chunks):
            continue

        chunks_info = {}
        for idx, chunk in enumerate(event.grounding_metadata.grounding_chunks):
            if not chunk.web:
                continue

            url = chunk.web.uri
            title = (
                chunk.web.title
                if chunk.web.title != chunk.web.domain
                else chunk.web.domain
            )

            # Enhance title for Celtic/educational sources
            title = _enhance_tuath_source_title(url, title)

            if url not in url_to_short_id:
                short_id = f"tuath-{id_counter}"
                url_to_short_id[url] = short_id
                sources[short_id] = {
                    "short_id": short_id,
                    "title": title,
                    "url": url,
                    "domain": chunk.web.domain,
                    "source_type": _classify_tuath_source(url),
                    "supported_claims": [],
                }
                id_counter += 1

            chunks_info[idx] = url_to_short_id[url]

        # Collect supported claims with confidence scores
        if event.grounding_metadata.grounding_supports:
            for support in event.grounding_metadata.grounding_supports:
                confidence_scores = support.confidence_scores or []
                chunk_indices = support.grounding_chunk_indices or []

                for i, chunk_idx in enumerate(chunk_indices):
                    if chunk_idx in chunks_info:
                        short_id = chunks_info[chunk_idx]
                        confidence = (
                            confidence_scores[i] if i < len(confidence_scores) else 0.5
                        )
                        text_segment = support.segment.text if support.segment else ""
                        sources[short_id]["supported_claims"].append(
                            {
                                "text_segment": text_segment,
                                "confidence": confidence,
                            }
                        )

    callback_context.state["url_to_short_id"] = url_to_short_id
    callback_context.state["sources"] = sources


def citation_replacement_callback(
    callback_context: CallbackContext,
) -> genai_types.Content:
    """
    Replace citation tags with Markdown-formatted links.

    Processes 'final_cited_report' from context state, converting tags like
    `<cite source="tuath-N"/>` into hyperlinks using source information.
    Adds a sources section for educational reference.

    Args:
        callback_context: Contains the report and source information.

    Returns:
        The processed report with Markdown citation links.
    """
    from google.genai import types as genai_types

    final_report = callback_context.state.get("final_cited_report", "")
    sources = callback_context.state.get("sources", {})

    def tag_replacer(match: re.Match) -> str:
        short_id = match.group(1)
        if not (source_info := sources.get(short_id)):
            logger.warning(f"Invalid citation tag found and removed: {match.group(0)}")
            return ""
        display_text = source_info.get("title", source_info.get("domain", short_id))
        return f" [{display_text}]({source_info['url']})"

    processed_report = re.sub(
        r'<cite\s+source\s*=\s*["\']?\s*(tuath-\d+)\s*["\']?\s*/>',
        tag_replacer,
        final_report,
    )

    # Fix spacing around punctuation
    processed_report = re.sub(r"\s+([.,;:!?])", r"\1", processed_report)
    processed_report = re.sub(r"\]\s*\(", r"](", processed_report)

    # Add sources section organized by type
    if sources:
        sources_section = _format_sources_section(sources)
        processed_report += sources_section

    return genai_types.Content(
        parts=[genai_types.Part(text=processed_report)],
        role="model",
    )


def _format_sources_section(sources: dict) -> str:
    """Format sources into organized sections by type."""
    # Group sources by type
    by_type: dict[str, list] = {}
    for _short_id, info in sources.items():
        source_type = info.get("source_type", "reference")
        if source_type not in by_type:
            by_type[source_type] = []
        by_type[source_type].append(info)

    # Type display names
    type_names = {
        "mythology": "Mythology & Legends",
        "curriculum": "Curriculum Resources",
        "folklore": "Folklore & Traditions",
        "language": "Language Resources",
        "dictionary": "Dictionaries",
        "academic": "Academic Sources",
        "reference": "General References",
    }

    section = "\n\n---\n\n## Sources\n\n"
    for source_type, items in sorted(by_type.items()):
        type_display = type_names.get(source_type, source_type.title())
        section += f"### {type_display}\n\n"
        for info in items:
            section += f"- [{info['title']}]({info['url']})\n"
        section += "\n"

    return section


def _enhance_tuath_source_title(url: str, title: str) -> str:
    """Enhance source title for known Celtic and educational resources."""
    tuath_sources = {
        # Celtic language resources
        "duchas.ie": "Dúchas - National Folklore Collection",
        "logainm.ie": "Logainm - Placenames Database",
        "teanglann.ie": "Teanglann - Irish Dictionary",
        "focloir.ie": "Foclóir.ie - Dictionary",
        "dil.ie": "eDIL - Dictionary of Irish",
        # Curriculum authorities
        "curriculumonline.ie": "NCCA - Irish Curriculum",
        "ncca.ie": "NCCA - National Council for Curriculum",
        "sqa.org.uk": "SQA - Scottish Qualifications Authority",
        "qualificationswales.org": "Qualifications Wales",
        # Mythology resources
        "maryjones.us/ctexts": "Celtic Literature Collective",
        "sacred-texts.com/neu/celt": "Sacred Texts - Celtic",
        "storiesofold.com": "Stories of Old - Celtic Mythology",
        # Educational resources
        "gaelscoileanna.ie": "Gaelscoileanna - Irish Language Schools",
        "cogg.ie": "COGG - Irish Language Education",
    }

    for domain, enhanced_title in tuath_sources.items():
        if domain in url:
            return enhanced_title

    return title


def _classify_tuath_source(url: str) -> str:
    """Classify the type of educational source for Tuath."""
    source_types = {
        # Mythology sources
        "maryjones.us": "mythology",
        "sacred-texts.com": "mythology",
        "storiesofold.com": "mythology",
        "mythopedia.com": "mythology",
        # Folklore sources
        "duchas.ie": "folklore",
        # Curriculum sources
        "curriculumonline.ie": "curriculum",
        "ncca.ie": "curriculum",
        "sqa.org.uk": "curriculum",
        "qualificationswales.org": "curriculum",
        # Language/dictionary sources
        "teanglann.ie": "dictionary",
        "focloir.ie": "dictionary",
        "dil.ie": "dictionary",
        "logainm.ie": "language",
        # Academic sources
        "arxiv.org": "academic",
        "jstor.org": "academic",
        "academia.edu": "academic",
    }

    for domain, source_type in source_types.items():
        if domain in url:
            return source_type

    return "reference"
