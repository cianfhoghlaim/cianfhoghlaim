"""
Citation callbacks for Crypteolas DeFi/GitHub Intelligence Agent.

Collects sources from grounding metadata and formats citations
for protocol documentation, audit reports, and GitHub references.
"""
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from google.adk.agents.callback_context import CallbackContext
    from google.genai import types as genai_types

logger = logging.getLogger(__name__)


def collect_crypto_sources_callback(callback_context: "CallbackContext") -> None:
    """
    Collect and organize crypto/DeFi sources from agent events.

    Extracts web source details (URLs, titles) and associated text segments
    with confidence scores from grounding metadata. Aggregates into state
    for use by the citation replacement callback.

    Sources are classified by type:
    - protocol: DeFi protocol documentation
    - audit: Security audit reports
    - github: GitHub repositories and code
    - analytics: On-chain analytics platforms
    - news: Crypto news and research

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

            # Enhance title for crypto/DeFi sources
            title = _enhance_crypto_source_title(url, title)

            if url not in url_to_short_id:
                short_id = f"crypto-{id_counter}"
                url_to_short_id[url] = short_id
                sources[short_id] = {
                    "short_id": short_id,
                    "title": title,
                    "url": url,
                    "domain": chunk.web.domain,
                    "source_type": _classify_crypto_source(url),
                    "risk_level": _assess_source_risk(url),
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
    callback_context: "CallbackContext",
) -> "genai_types.Content":
    """
    Replace citation tags with Markdown-formatted links.

    Processes 'final_cited_report' from context state, converting tags like
    `<cite source="crypto-N"/>` into hyperlinks using source information.
    Adds a sources section organized by type and risk level.

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
        r'<cite\s+source\s*=\s*["\']?\s*(crypto-\d+)\s*["\']?\s*/>',
        tag_replacer,
        final_report,
    )

    # Fix spacing around punctuation
    processed_report = re.sub(r"\s+([.,;:!?])", r"\1", processed_report)
    processed_report = re.sub(r"\]\s*\(", r"](", processed_report)

    # Add sources section organized by type with risk indicators
    if sources:
        sources_section = _format_crypto_sources_section(sources)
        processed_report += sources_section

    return genai_types.Content(
        parts=[genai_types.Part(text=processed_report)],
        role="model",
    )


def _format_crypto_sources_section(sources: dict) -> str:
    """Format sources into organized sections by type with risk indicators."""
    # Group sources by type
    by_type: dict[str, list] = {}
    for short_id, info in sources.items():
        source_type = info.get("source_type", "reference")
        if source_type not in by_type:
            by_type[source_type] = []
        by_type[source_type].append(info)

    # Type display names and emojis
    type_info = {
        "protocol": ("Protocol Documentation", "📄"),
        "audit": ("Security Audits", "🔒"),
        "github": ("GitHub Repositories", "💻"),
        "analytics": ("On-Chain Analytics", "📊"),
        "news": ("News & Research", "📰"),
        "governance": ("Governance", "🏛️"),
        "reference": ("General References", "📚"),
    }

    # Risk level indicators
    risk_emoji = {
        "verified": "✅",
        "moderate": "⚠️",
        "unverified": "❓",
    }

    section = "\n\n---\n\n## Sources\n\n"
    for source_type, items in sorted(by_type.items()):
        display_name, emoji = type_info.get(source_type, (source_type.title(), "📌"))
        section += f"### {emoji} {display_name}\n\n"
        for info in items:
            risk = info.get("risk_level", "unverified")
            risk_indicator = risk_emoji.get(risk, "")
            section += f"- {risk_indicator} [{info['title']}]({info['url']})\n"
        section += "\n"

    return section


def _enhance_crypto_source_title(url: str, title: str) -> str:
    """Enhance source title for known crypto/DeFi resources."""
    crypto_sources = {
        # Protocol docs
        "docs.aave.com": "Aave Documentation",
        "docs.uniswap.org": "Uniswap Documentation",
        "docs.curve.fi": "Curve Finance Documentation",
        "docs.lido.fi": "Lido Documentation",
        "docs.compound.finance": "Compound Documentation",
        "docs.makerdao.com": "MakerDAO Documentation",
        # Analytics platforms
        "defillama.com": "DefiLlama - DeFi Analytics",
        "dune.com": "Dune Analytics",
        "etherscan.io": "Etherscan",
        "arbiscan.io": "Arbiscan",
        "polygonscan.com": "Polygonscan",
        "basescan.org": "Basescan",
        # Audit firms
        "code4rena.com": "Code4rena - Audit Platform",
        "sherlock.xyz": "Sherlock - Audit Protocol",
        "consensys.io/diligence": "ConsenSys Diligence",
        "openzeppelin.com/security-audits": "OpenZeppelin Audits",
        "trailofbits.com": "Trail of Bits",
        "quantstamp.com": "Quantstamp",
        # GitHub
        "github.com/aave": "Aave GitHub",
        "github.com/Uniswap": "Uniswap GitHub",
        "github.com/curvefi": "Curve Finance GitHub",
        "github.com/lidofinance": "Lido GitHub",
        # News/Research
        "theblock.co": "The Block",
        "messari.io": "Messari Research",
        "coindesk.com": "CoinDesk",
        "cointelegraph.com": "Cointelegraph",
    }

    for domain, enhanced_title in crypto_sources.items():
        if domain in url:
            return enhanced_title

    # Handle generic GitHub repos
    if "github.com" in url:
        parts = url.split("github.com/")
        if len(parts) > 1:
            repo_path = parts[1].split("/")[:2]
            if len(repo_path) >= 2:
                return f"GitHub: {repo_path[0]}/{repo_path[1]}"

    return title


def _classify_crypto_source(url: str) -> str:
    """Classify the type of crypto/DeFi source."""
    source_types = {
        # Protocol documentation
        "docs.aave.com": "protocol",
        "docs.uniswap.org": "protocol",
        "docs.curve.fi": "protocol",
        "docs.lido.fi": "protocol",
        "docs.compound.finance": "protocol",
        "docs.makerdao.com": "protocol",
        # Analytics
        "defillama.com": "analytics",
        "dune.com": "analytics",
        "etherscan.io": "analytics",
        "arbiscan.io": "analytics",
        "polygonscan.com": "analytics",
        # Audits
        "code4rena.com": "audit",
        "sherlock.xyz": "audit",
        "consensys.io/diligence": "audit",
        "openzeppelin.com/security-audits": "audit",
        "trailofbits.com": "audit",
        "quantstamp.com": "audit",
        # GitHub
        "github.com": "github",
        # Governance
        "snapshot.org": "governance",
        "tally.xyz": "governance",
        # News
        "theblock.co": "news",
        "messari.io": "news",
        "coindesk.com": "news",
        "cointelegraph.com": "news",
    }

    for domain, source_type in source_types.items():
        if domain in url:
            return source_type

    return "reference"


def _assess_source_risk(url: str) -> str:
    """Assess the trust/verification level of a source."""
    # Highly trusted sources
    verified_domains = [
        "docs.aave.com",
        "docs.uniswap.org",
        "docs.curve.fi",
        "docs.lido.fi",
        "etherscan.io",
        "defillama.com",
        "code4rena.com",
        "openzeppelin.com",
        "consensys.io",
        "github.com/aave",
        "github.com/Uniswap",
        "github.com/curvefi",
        "github.com/OpenZeppelin",
    ]

    # Moderately trusted
    moderate_domains = [
        "github.com",
        "dune.com",
        "messari.io",
        "theblock.co",
        "sherlock.xyz",
    ]

    for domain in verified_domains:
        if domain in url:
            return "verified"

    for domain in moderate_domains:
        if domain in url:
            return "moderate"

    return "unverified"
