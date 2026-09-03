"""
MCP Server implementation for Tuath Celtic Education.

Provides tools for:
- Curriculum search and learning outcomes (consuming from oideachais)
- Celtic mythology exploration
- FIBO educational asset generation

NOTE: Curriculum data is consumed from oideachais (the authoritative source)
rather than maintaining duplicate ingestion pipelines.
"""

import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent, Tool

from ..tools.curriculum_search import (
    OIDEACHAIS_LANCEDB_PATH,
)
from ..tools.curriculum_search import (
    get_learning_outcomes as _get_learning_outcomes,
)

# Import actual tool implementations
from ..tools.curriculum_search import (
    search_curriculum as _search_curriculum,
)
from ..tools.mythology_query import (
    get_character_lore as _get_character_lore,
)
from ..tools.mythology_query import (
    get_location_lore as _get_location_lore,
)
from ..tools.mythology_query import (
    search_mythology as _search_mythology,
)

# =============================================================================
# MCP Server Setup
# =============================================================================

server = Server("tuath-education")


# =============================================================================
# Tool Definitions
# =============================================================================

TOOLS = [
    # Curriculum Tools
    Tool(
        name="search_curriculum",
        description="Search Celtic curriculum content (NCCA Irish, SQA Scottish Gaelic, WJEC Welsh)",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
                "subject": {
                    "type": "string",
                    "enum": ["irish", "geography", "history", "mathematics", "science"],
                    "description": "Subject area filter",
                },
                "level": {
                    "type": "string",
                    "enum": ["primary", "junior_cycle", "senior_cycle"],
                    "description": "Education level",
                },
                "language": {
                    "type": "string",
                    "enum": ["en", "ga", "cy", "gd"],
                    "description": "Content language (en=English, ga=Irish, cy=Welsh, gd=Scottish Gaelic)",
                    "default": "en",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 10)",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="get_learning_outcomes",
        description="Get learning outcomes for a curriculum strand or topic",
        inputSchema={
            "type": "object",
            "properties": {
                "strand": {
                    "type": "string",
                    "description": "Curriculum strand (e.g., 'Number', 'Oral Language', 'Living Things')",
                },
                "subject": {
                    "type": "string",
                    "description": "Subject area",
                },
                "level": {
                    "type": "string",
                    "enum": ["primary", "junior_cycle", "senior_cycle"],
                    "description": "Education level",
                },
            },
            "required": ["strand"],
        },
    ),
    Tool(
        name="get_exam_papers",
        description="Search historical exam papers from SEC (Ireland), SQA (Scotland)",
        inputSchema={
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "Subject name",
                },
                "year": {
                    "type": "integer",
                    "description": "Exam year (e.g., 2023)",
                },
                "level": {
                    "type": "string",
                    "enum": ["ordinary", "higher", "foundation"],
                    "description": "Exam level",
                },
            },
            "required": ["subject"],
        },
    ),
    # Mythology Tools
    Tool(
        name="search_mythology",
        description="Search Celtic mythology and folklore (Irish, Welsh, Scottish)",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
                "tradition": {
                    "type": "string",
                    "enum": ["irish", "welsh", "scottish", "manx", "all"],
                    "description": "Celtic tradition to search",
                    "default": "all",
                },
                "category": {
                    "type": "string",
                    "enum": ["characters", "places", "stories", "creatures", "all"],
                    "description": "Content category",
                    "default": "all",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="get_character_lore",
        description="Get detailed lore for a mythological character",
        inputSchema={
            "type": "object",
            "properties": {
                "character_name": {
                    "type": "string",
                    "description": "Character name (e.g., 'Cú Chulainn', 'Fionn mac Cumhaill')",
                },
                "include_relationships": {
                    "type": "boolean",
                    "description": "Include character relationships",
                    "default": True,
                },
                "include_stories": {
                    "type": "boolean",
                    "description": "Include associated stories",
                    "default": True,
                },
            },
            "required": ["character_name"],
        },
    ),
    Tool(
        name="get_place_lore",
        description="Get mythological lore for a place",
        inputSchema={
            "type": "object",
            "properties": {
                "place_name": {
                    "type": "string",
                    "description": "Place name (e.g., 'Tír na nÓg', 'Emain Macha')",
                },
            },
            "required": ["place_name"],
        },
    ),
    # FIBO Generation Tools
    Tool(
        name="generate_fibo_image",
        description="Generate an educational image using the FIBO framework",
        inputSchema={
            "type": "object",
            "properties": {
                "concept": {
                    "type": "string",
                    "description": "Educational concept to visualize",
                },
                "subject": {
                    "type": "string",
                    "enum": ["chemistry", "biology", "physics", "geography", "history", "irish"],
                    "description": "Subject area",
                },
                "diagram_type": {
                    "type": "string",
                    "enum": ["molecular", "process_flow", "cell_diagram", "force_diagram", "map", "timeline"],
                    "description": "Type of diagram to generate",
                },
                "style": {
                    "type": "string",
                    "enum": ["digital_illustration", "photograph", "sketch", "infographic"],
                    "description": "Visual style",
                    "default": "digital_illustration",
                },
            },
            "required": ["concept", "subject"],
        },
    ),
    Tool(
        name="validate_asset",
        description="Validate a generated educational asset against curriculum requirements",
        inputSchema={
            "type": "object",
            "properties": {
                "asset_id": {
                    "type": "string",
                    "description": "ID of the generated asset",
                },
                "concept_title": {
                    "type": "string",
                    "description": "Title of the concept being validated",
                },
            },
            "required": ["asset_id"],
        },
    ),
    Tool(
        name="list_generated_assets",
        description="List generated educational assets",
        inputSchema={
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "Filter by subject",
                },
                "status": {
                    "type": "string",
                    "enum": ["draft", "validated", "approved", "rejected"],
                    "description": "Filter by status",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results",
                    "default": 20,
                },
            },
        },
    ),
    # Geospatial Tools
    Tool(
        name="search_gaeltacht",
        description="Search Gaeltacht regions and Irish-speaking areas",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Place name or search query",
                },
                "region": {
                    "type": "string",
                    "enum": ["connacht", "munster", "ulster", "all"],
                    "description": "Region filter",
                    "default": "all",
                },
            },
        },
    ),
]


# =============================================================================
# Tool Implementations
# =============================================================================


async def search_curriculum_impl(
    query: str,
    subject: str | None = None,
    level: str | None = None,
    language: str = "en",
    limit: int = 10,
) -> str:
    """Search curriculum content from oideachais LanceDB."""
    try:
        results = await _search_curriculum(
            query=query,
            subject=subject,
            level=level,
            language=language,
            limit=limit,
        )

        if not results.results:
            return f"""No curriculum results found for "{query}".

Filters applied:
- Subject: {subject or 'all'}
- Level: {level or 'all'}
- Language: {language}

Data source: oideachais LanceDB at {OIDEACHAIS_LANCEDB_PATH}
"""

        output = [f'Curriculum search results for "{query}" ({results.total} found):\n']
        for i, r in enumerate(results.results, 1):
            output.append(f"{i}. [{r.subject} - {r.level}] {r.title}")
            output.append(f"   Nation: {r.nation} | Language: {r.language}")
            if r.content:
                content_preview = r.content[:150] + "..." if len(r.content) > 150 else r.content
                output.append(f"   {content_preview}")
            output.append("")

        output.append("Data source: oideachais (via shared LanceDB)")
        return "\n".join(output)

    except Exception as e:
        return f"Error searching curriculum: {e}"


async def get_learning_outcomes_impl(
    strand: str,
    subject: str | None = None,
    level: str | None = None,
) -> str:
    """Get learning outcomes from sruth.oideachais."""
    try:
        outcomes = await _get_learning_outcomes(
            topic=strand,
            nation=None,
            level=level,
        )

        if not outcomes:
            return f"""No learning outcomes found for "{strand}".

Filters: level={level or 'all'}, subject={subject or 'all'}
"""

        output = [f'Learning Outcomes for "{strand}":\n']
        for i, outcome in enumerate(outcomes, 1):
            output.append(f"{i}. {outcome.description}")
            output.append(f"   Subject: {outcome.subject} | Level: {outcome.level} | Nation: {outcome.nation}")
            if outcome.prerequisites:
                output.append(f"   Prerequisites: {', '.join(outcome.prerequisites)}")
            output.append("")

        return "\n".join(output)

    except Exception as e:
        return f"Error getting learning outcomes: {e}"


async def search_mythology_impl(
    query: str,
    tradition: str = "all",
    category: str = "all",
    limit: int = 10,
) -> str:
    """Search Celtic mythology content."""
    try:
        trad = None if tradition == "all" else tradition
        results = await _search_mythology(
            query=query,
            tradition=trad,
            limit=limit,
        )

        if not results.results:
            return f"""No mythology results found for "{query}".

Tradition filter: {tradition}
Category filter: {category}
"""

        output = [f'Mythology search results for "{query}" ({results.total} found):\n']
        for i, r in enumerate(results.results, 1):
            output.append(f"{i}. {r.title} ({r.tradition.title()} - {r.cycle})")
            if r.characters:
                output.append(f"   Characters: {', '.join(r.characters[:5])}")
            if r.content:
                content_preview = r.content[:150] + "..." if len(r.content) > 150 else r.content
                output.append(f"   {content_preview}")
            output.append("")

        return "\n".join(output)

    except Exception as e:
        return f"Error searching mythology: {e}"


async def get_character_lore_impl(
    character_name: str,
    include_relationships: bool = True,
    include_stories: bool = True,
) -> str:
    """Get detailed character lore."""
    try:
        lore_list = await _get_character_lore(character_name)

        if not lore_list:
            return f"No lore found for character: {character_name}"

        output = []
        for lore in lore_list:
            output.append(f"# {lore.name}")
            output.append(f"\n**Tradition:** {lore.tradition.title()}")
            output.append(f"**Cycle:** {lore.cycle}")
            if lore.titles:
                output.append(f"**Titles:** {', '.join(lore.titles)}")
            output.append(f"\n## Description\n{lore.description}")

            if include_relationships and lore.relationships:
                output.append("\n## Relationships")
                for rel, name in lore.relationships.items():
                    output.append(f"- {rel.title()}: {name}")

            if include_stories and lore.stories:
                output.append("\n## Associated Stories")
                for story in lore.stories:
                    output.append(f"- {story}")

            if lore.celtic_names:
                output.append("\n## Celtic Names")
                for lang, name in lore.celtic_names.items():
                    lang_full = {"ga": "Irish", "gd": "Scottish Gaelic", "cy": "Welsh"}.get(lang, lang)
                    output.append(f"- {lang_full}: {name}")

            output.append("\n---\n")

        return "\n".join(output)

    except Exception as e:
        return f"Error getting character lore: {e}"


async def get_place_lore_impl(place_name: str) -> str:
    """Get lore for a mythological place."""
    try:
        locations = await _get_location_lore(place_name)

        if not locations:
            return f"No lore found for location: {place_name}"

        output = []
        for loc in locations:
            output.append(f"# {loc.name}")
            output.append(f"\n**Tradition:** {loc.tradition.title()}")
            output.append(f"\n## Description\n{loc.description}")
            output.append(f"\n## Significance\n{loc.significance}")

            if loc.associated_characters:
                output.append("\n## Associated Characters")
                for char in loc.associated_characters:
                    output.append(f"- {char}")

            if loc.events:
                output.append("\n## Notable Events")
                for event in loc.events:
                    output.append(f"- {event}")

            if loc.celtic_names:
                output.append("\n## Celtic Names")
                for lang, name in loc.celtic_names.items():
                    lang_full = {"ga": "Irish", "gd": "Scottish Gaelic", "cy": "Welsh"}.get(lang, lang)
                    output.append(f"- {lang_full}: {name}")

            output.append("\n---\n")

        return "\n".join(output)

    except Exception as e:
        return f"Error getting location lore: {e}"


def generate_fibo_image_impl(
    concept: str,
    subject: str,
    diagram_type: str | None = None,
    style: str = "digital_illustration",
) -> str:
    """Generate educational image using FIBO framework."""
    # FIBO asset generation would use LiteLLM for image generation
    asset_id = f"fibo_{concept.lower().replace(' ', '_')}_{subject}_001"

    return f"""FIBO Image Generation Request:

Concept: {concept}
Subject: {subject}
Diagram Type: {diagram_type or 'auto-detected'}
Style: {style}

Status: Queued for generation
Asset ID: {asset_id}

To generate:
1. Prompt will be constructed from concept and subject
2. Image will be generated via LiteLLM (Flux, DALL-E, or similar)
3. VLM validation will check curriculum alignment
4. Asset will be stored in LanceDB with embeddings

Note: Full LiteLLM integration pending. Run `dagster asset materialize fibo_generation` to process queue.
"""


def validate_asset_impl(asset_id: str, concept_title: str | None = None) -> str:
    """Validate generated asset against curriculum requirements."""
    return f"""Asset Validation: {asset_id}

Validation Checks:
- Scientific Accuracy: Pending VLM review
- Educational Clarity: Pending VLM review
- Curriculum Alignment: Pending curriculum match

Status: PENDING
Next Steps:
1. Run VLM validation pipeline
2. Match against curriculum learning outcomes
3. Generate accessibility metadata

Note: VLM validation integration pending. Use `/api/fibo/validate` endpoint when available.
"""


# =============================================================================
# MCP Handlers
# =============================================================================


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    try:
        if name == "search_curriculum":
            result = await search_curriculum_impl(
                query=arguments["query"],
                subject=arguments.get("subject"),
                level=arguments.get("level"),
                language=arguments.get("language", "en"),
                limit=arguments.get("limit", 10),
            )
        elif name == "get_learning_outcomes":
            result = await get_learning_outcomes_impl(
                strand=arguments["strand"],
                subject=arguments.get("subject"),
                level=arguments.get("level"),
            )
        elif name == "search_mythology":
            result = await search_mythology_impl(
                query=arguments["query"],
                tradition=arguments.get("tradition", "all"),
                category=arguments.get("category", "all"),
                limit=arguments.get("limit", 10),
            )
        elif name == "get_character_lore":
            result = await get_character_lore_impl(
                character_name=arguments["character_name"],
                include_relationships=arguments.get("include_relationships", True),
                include_stories=arguments.get("include_stories", True),
            )
        elif name == "get_place_lore":
            result = await get_place_lore_impl(arguments["place_name"])
        elif name == "generate_fibo_image":
            result = generate_fibo_image_impl(
                concept=arguments["concept"],
                subject=arguments["subject"],
                diagram_type=arguments.get("diagram_type"),
                style=arguments.get("style", "digital_illustration"),
            )
        elif name == "validate_asset":
            result = validate_asset_impl(
                asset_id=arguments["asset_id"],
                concept_title=arguments.get("concept_title"),
            )
        elif name == "list_generated_assets":
            result = "Generated assets listing: Pending LanceDB integration."
        elif name == "get_exam_papers":
            result = f"Exam papers for {arguments['subject']}: Pending SEC/SQA integration."
        elif name == "search_gaeltacht":
            result = f"Gaeltacht search for '{arguments.get('query', '')}': Pending GeoJSON integration."
        else:
            result = f"Unknown tool: {name}"

        return CallToolResult(
            content=[TextContent(type="text", text=result)],
            isError=False,
        )

    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {e}")],
            isError=True,
        )


# =============================================================================
# Server Factory
# =============================================================================


def create_mcp_server() -> Server:
    """Create and return the MCP server instance."""
    return server


async def run_server():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


# =============================================================================
# Entry Point
# =============================================================================


if __name__ == "__main__":
    asyncio.run(run_server())
