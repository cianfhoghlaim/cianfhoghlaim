"""
Citation callbacks for Celtic Education Research Agent.

Collects sources from grounding metadata and formats citations.
"""
from __future__ import annotations

import logging
import re

from google.adk.agents.callback_context import CallbackContext
from google.genai import types as genai_types


def collect_celtic_sources_callback(callback_context: CallbackContext) -> None:
    """
    Collect and organize research sources from agent events.

    Extracts web source details (URLs, titles) and associated text segments
    with confidence scores from grounding metadata. Aggregates into state
    for use by the citation replacement callback.

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

            # Enhance title for Celtic sources
            title = enhance_celtic_source_title(url, title)

            if url not in url_to_short_id:
                short_id = f"src-{id_counter}"
                url_to_short_id[url] = short_id
                sources[short_id] = {
                    "short_id": short_id,
                    "title": title,
                    "url": url,
                    "domain": chunk.web.domain,
                    "source_type": classify_celtic_source(url),
                    "supported_claims": [],
                }
                id_counter += 1

            chunks_info[idx] = url_to_short_id[url]

        # Collect supported claims
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
    `<cite source="src-N"/>` into hyperlinks using source information.

    Args:
        callback_context: Contains the report and source information.

    Returns:
        The processed report with Markdown citation links.
    """
    final_report = callback_context.state.get("final_cited_report", "")
    sources = callback_context.state.get("sources", {})

    def tag_replacer(match: re.Match) -> str:
        short_id = match.group(1)
        if not (source_info := sources.get(short_id)):
            logging.warning(f"Invalid citation tag found and removed: {match.group(0)}")
            return ""
        display_text = source_info.get("title", source_info.get("domain", short_id))
        return f" [{display_text}]({source_info['url']})"

    processed_report = re.sub(
        r'<cite\s+source\s*=\s*["\']?\s*(src-\d+)\s*["\']?\s*/>',
        tag_replacer,
        final_report,
    )

    # Fix spacing around punctuation
    processed_report = re.sub(r"\s+([.,;:!?])", r"\1", processed_report)
    processed_report = re.sub(r"\]\s*\(", r"](", processed_report)

    # Add sources summary if there are sources
    if sources:
        sources_section = "\n\n---\n\n## Sources\n\n"
        for _short_id, info in sorted(sources.items()):
            source_type = info.get("source_type", "")
            type_badge = f" [{source_type}]" if source_type else ""
            sources_section += f"- [{info['title']}]({info['url']}){type_badge}\n"
        processed_report += sources_section

    return genai_types.Content(
        parts=[genai_types.Part(text=processed_report)],
        role="model",
    )


def enhance_celtic_source_title(url: str, title: str) -> str:
    """Enhance source title for known Celtic resources."""
    celtic_sources = {
        "duchas.ie": "Duchas - National Folklore Collection",
        "logainm.ie": "Logainm - Placenames Database",
        "tearma.ie": "Tearma - Terminology Database",
        "ainm.ie": "Ainm - Biographical Database",
        "teanglann.ie": "Teanglann - Irish Dictionary",
        "focloir.ie": "Focloir.ie - Dictionary",
        "canuint.ie": "Canuint - Irish Dialects",
        "gaois.ie": "GAOIS Research Group",
        "dil.ie": "eDIL - Dictionary of Irish",
        "dasg.ac.uk": "DASG - Scottish Gaelic Archive",
        "corpas.ie": "Corpas na Gaeilge",
    }

    for domain, enhanced_title in celtic_sources.items():
        if domain in url:
            return enhanced_title

    return title


def classify_celtic_source(url: str) -> str:
    """Classify the type of Celtic language source."""
    source_types = {
        "duchas.ie": "folklore",
        "logainm.ie": "placenames",
        "tearma.ie": "terminology",
        "ainm.ie": "biography",
        "teanglann.ie": "dictionary",
        "canuint.ie": "pronunciation",
        "gaois.ie": "research",
        "dil.ie": "historical-dictionary",
        "universaldependencies.org": "treebank",
        "arxiv.org": "academic",
        "aclanthology.org": "academic",
    }

    for domain, source_type in source_types.items():
        if domain in url:
            return source_type

    return ""


# --- British Isles Education Callbacks ---


def collect_education_sources_callback(callback_context: CallbackContext) -> None:
    """
    Collect web sources for British Isles education research.

    Extracts URLs and titles from grounding metadata for cross-nation
    education research (England, Scotland, Wales, NI, Ireland).
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

            # Enhance title for education sources
            title = enhance_education_source_title(url, title)

            if url not in url_to_short_id:
                short_id = f"src-{id_counter}"
                url_to_short_id[url] = short_id
                sources[short_id] = {
                    "short_id": short_id,
                    "title": title,
                    "url": url,
                    "domain": chunk.web.domain,
                    "source_type": classify_education_source(url),
                    "supported_claims": [],
                }
                id_counter += 1
            chunks_info[idx] = url_to_short_id[url]

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


def format_education_citations_callback(
    callback_context: CallbackContext,
) -> genai_types.Content:
    """
    Replace citation tags with Markdown links for education research.

    Processes 'final_report' from state and converts citation tags.
    """
    final_report = callback_context.state.get("final_report", "")
    sources = callback_context.state.get("sources", {})

    def tag_replacer(match: re.Match) -> str:
        short_id = match.group(1)
        if not (source_info := sources.get(short_id)):
            return ""
        display_text = source_info.get("title", source_info.get("domain", short_id))
        return f" [{display_text}]({source_info['url']})"

    processed_report = re.sub(
        r'<cite\s+source\s*=\s*["\']?\s*(src-\d+)\s*["\']?\s*/>',
        tag_replacer,
        final_report,
    )
    processed_report = re.sub(r"\s+([.,;:])", r"\1", processed_report)
    callback_context.state["final_report_with_citations"] = processed_report

    return genai_types.Content(parts=[genai_types.Part(text=processed_report)])


def enhance_education_source_title(url: str, title: str) -> str:
    """Enhance source title for known education resources."""
    education_sources = {
        "gov.uk/government/organisations/department-for-education": "DfE - England",
        "explore-education-statistics.service.gov.uk": "DfE Explore Statistics",
        "gov.scot": "Scottish Government",
        "education.gov.scot": "Education Scotland",
        "sqa.org.uk": "SQA - Scottish Qualifications",
        "gov.wales": "Welsh Government",
        "statswales.gov.wales": "StatsWales",
        "estyn.gov.wales": "Estyn - Welsh Inspectorate",
        "qualificationswales.org": "Qualifications Wales",
        "nisra.gov.uk": "NISRA - NI Statistics",
        "education-ni.gov.uk": "Department of Education NI",
        "etini.gov.uk": "ETI - NI Inspectorate",
        "gov.ie/en/organisation/department-of-education": "Department of Education Ireland",
        "ncca.ie": "NCCA - Curriculum Ireland",
        "examinations.ie": "SEC - State Examinations",
        "cso.ie": "CSO - Central Statistics Office",
        "ofsted.gov.uk": "Ofsted - England Inspectorate",
    }

    for domain, enhanced_title in education_sources.items():
        if domain in url:
            return enhanced_title

    # Official-media bucket — added by the official-media-pipeline change
    # (Phase 6). Recognises the 4 intelligence agencies so the citation
    # pipeline surfaces them with the canonical title.
    official_media_sources = {
        "mi5.gov.uk": "MI5 - Security Service",
        "sis.gov.uk": "MI6 - Secret Intelligence Service",
        "gchq.gov.uk": "GCHQ - Government Communications HQ",
        "hmgcc.gov.uk": "HMGCC - His Majesty's Government Communications Centre",
    }
    for domain, enhanced_title in official_media_sources.items():
        if domain in url:
            return enhanced_title

    return title


def classify_education_source(url: str) -> str:
    """Classify the type of education source by nation."""
    source_types = {
        # England
        "gov.uk": "england-government",
        "ofsted.gov.uk": "england-inspectorate",
        # Scotland
        "gov.scot": "scotland-government",
        "education.gov.scot": "scotland-curriculum",
        "sqa.org.uk": "scotland-qualifications",
        # Wales
        "gov.wales": "wales-government",
        "statswales": "wales-statistics",
        "estyn.gov.wales": "wales-inspectorate",
        # Northern Ireland
        "nisra.gov.uk": "ni-statistics",
        "education-ni.gov.uk": "ni-education",
        "etini.gov.uk": "ni-inspectorate",
        # Ireland
        "gov.ie": "ireland-government",
        "ncca.ie": "ireland-curriculum",
        "examinations.ie": "ireland-exams",
        "cso.ie": "ireland-statistics",
    }

    for domain, source_type in source_types.items():
        if domain in url:
            return source_type

    return ""
