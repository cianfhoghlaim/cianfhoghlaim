"""Entity and Relationship Extraction.

Defines data models and functions for extracting entities and relationships
from documents using LLMs.

Reference: docs_to_knowledge_graph example from CocoIndex
"""

from dataclasses import dataclass, field
from typing import Any
import json


@dataclass
class DocumentSummary:
    """Summary of a document."""
    title: str
    summary: str


@dataclass
class Relationship:
    """A relationship triple (subject-predicate-object).

    Represents an RDF-style relationship extracted from text.
    Both subject and object should be nouns/concepts, not verbs.
    """
    subject: str  # e.g., "CocoIndex"
    predicate: str  # e.g., "supports"
    object: str  # e.g., "Incremental Processing"

    def to_dict(self) -> dict[str, str]:
        return {
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
        }


@dataclass
class EntityMention:
    """An entity mention linking a document to an entity."""
    entity: str
    filename: str
    id: str | None = None


@dataclass
class ExtractionResult:
    """Result of entity/relationship extraction."""
    summary: DocumentSummary
    relationships: list[Relationship]
    entities: set[str] = field(default_factory=set)

    def __post_init__(self):
        # Extract unique entities from relationships
        for rel in self.relationships:
            self.entities.add(rel.subject)
            self.entities.add(rel.object)


def extract_entities_and_relationships(
    content: str,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini",
) -> ExtractionResult:
    """Extract entities and relationships from document content.

    Uses an LLM to identify entities (concepts, people, technologies)
    and relationships between them.

    Args:
        content: Document content to analyze
        llm_provider: LLM provider ("openai", "ollama", etc.)
        model: Model name

    Returns:
        ExtractionResult with summary, relationships, and entities
    """
    # Try to use OpenAI for extraction
    try:
        import openai
        return _extract_with_openai(content, model)
    except ImportError:
        pass

    # Fallback to simple extraction
    return _extract_simple(content)


def _extract_with_openai(content: str, model: str = "gpt-4o-mini") -> ExtractionResult:
    """Extract using OpenAI API."""
    import os
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("LLM_API_KEY", os.environ.get("OPENAI_API_KEY")))

    # Extract summary
    summary_response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a document summarizer. Extract a title and brief summary."
            },
            {
                "role": "user",
                "content": f"Summarize this document:\n\n{content[:4000]}"
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    try:
        summary_data = json.loads(summary_response.choices[0].message.content)
        summary = DocumentSummary(
            title=summary_data.get("title", "Untitled"),
            summary=summary_data.get("summary", ""),
        )
    except (json.JSONDecodeError, KeyError):
        summary = DocumentSummary(title="Untitled", summary="")

    # Extract relationships
    rel_response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": """You are a knowledge graph extractor. Extract relationships from the document.
Return a JSON object with a "relationships" array. Each relationship should have:
- "subject": A noun/concept (e.g., "Python", "DLT", "REST API")
- "predicate": A verb phrase (e.g., "supports", "uses", "integrates with")
- "object": A noun/concept

Focus on technical concepts, tools, and their relationships. Ignore examples and code snippets.
Return at most 10 relationships."""
            },
            {
                "role": "user",
                "content": f"Extract relationships from:\n\n{content[:4000]}"
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    relationships = []
    try:
        rel_data = json.loads(rel_response.choices[0].message.content)
        for rel in rel_data.get("relationships", []):
            relationships.append(Relationship(
                subject=rel.get("subject", ""),
                predicate=rel.get("predicate", ""),
                object=rel.get("object", ""),
            ))
    except (json.JSONDecodeError, KeyError):
        pass

    return ExtractionResult(summary=summary, relationships=relationships)


def _extract_simple(content: str) -> ExtractionResult:
    """Simple extraction without LLM.

    Uses basic heuristics to extract potential entities.
    """
    import re

    # Extract title from first heading or first line
    lines = content.split("\n")
    title = "Untitled"
    for line in lines[:10]:
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            break
        elif line.strip():
            title = line.strip()[:100]
            break

    # Simple summary: first paragraph
    summary = ""
    for line in lines:
        if line.strip() and not line.startswith("#"):
            summary = line.strip()[:500]
            break

    # Extract potential entities (capitalized words, code identifiers)
    entity_pattern = r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b'
    potential_entities = set(re.findall(entity_pattern, content))

    # Filter common words
    common_words = {"The", "This", "That", "These", "Those", "When", "Where", "How", "What", "Why"}
    entities = potential_entities - common_words

    # Create simple relationships (entity -> "mentioned in" -> title)
    relationships = [
        Relationship(subject=entity, predicate="mentioned in", object=title)
        for entity in list(entities)[:10]
    ]

    return ExtractionResult(
        summary=DocumentSummary(title=title, summary=summary),
        relationships=relationships,
    )


def extract_from_github_issue(issue: dict[str, Any]) -> ExtractionResult:
    """Extract entities from a GitHub issue.

    Args:
        issue: GitHub issue data from API

    Returns:
        ExtractionResult
    """
    title = issue.get("title", "")
    body = issue.get("body", "") or ""
    labels = [l.get("name", "") for l in issue.get("labels", [])]

    content = f"# {title}\n\nLabels: {', '.join(labels)}\n\n{body}"

    return extract_entities_and_relationships(content)


def extract_from_pull_request(pr: dict[str, Any]) -> ExtractionResult:
    """Extract entities from a GitHub pull request.

    Args:
        pr: GitHub PR data from API

    Returns:
        ExtractionResult
    """
    title = pr.get("title", "")
    body = pr.get("body", "") or ""

    content = f"# {title}\n\n{body}"

    return extract_entities_and_relationships(content)
