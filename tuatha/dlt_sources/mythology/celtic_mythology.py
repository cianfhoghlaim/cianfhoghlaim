"""
DLT source for Celtic mythology content.

Crawls and structures mythology from various sources:
- Irish: Tuatha Dé Danann, Fionn mac Cumhaill, Ulster Cycle
- Welsh: Mabinogion, Welsh gods
- Scottish: Highland folklore, Gaelic legends
- Manx: Manannán mac Lir, island legends

Sources:
- Wikipedia (celtic mythology categories)
- Sacred Texts Archive
- Mary Jones Celtic Encyclopedia
- CELT (Corpus of Electronic Texts)
"""

import os
from datetime import datetime, timezone
from typing import Any, Iterator

import dlt


# Known mythology URLs and categories
MYTHOLOGY_SOURCES = {
    "irish": {
        "cycles": [
            "Mythological_Cycle",
            "Ulster_Cycle",
            "Fenian_Cycle",
            "Historical_Cycle",
        ],
        "deities": [
            "Tuatha_Dé_Danann",
            "Dagda",
            "Brigid",
            "Lugh",
            "Danu_(Irish_goddess)",
            "Morrígan",
            "Manannán_mac_Lir",
            "Aengus",
            "Nuada",
            "Goibniu",
        ],
        "heroes": [
            "Cú_Chulainn",
            "Fionn_mac_Cumhaill",
            "Oisín",
            "Diarmuid_Ua_Duibhne",
            "Deirdre",
            "Medb",
        ],
        "locations": [
            "Tír_na_nÓg",
            "Otherworld_(Celtic_mythology)",
            "Emain_Macha",
            "Tara_(Ireland)",
            "Brú_na_Bóinne",
        ],
    },
    "welsh": {
        "mabinogion": [
            "Mabinogion",
            "Four_Branches_of_the_Mabinogi",
            "Pwyll_Pendefig_Dyfed",
            "Branwen_ferch_Llŷr",
            "Manawydan_fab_Llŷr",
            "Math_fab_Mathonwy",
        ],
        "deities": [
            "Arawn",
            "Rhiannon",
            "Bran_the_Blessed",
            "Lleu_Llaw_Gyffes",
            "Gwydion",
            "Don_(Welsh_mythology)",
        ],
        "arthurian": [
            "Arthurian_legend",
            "Culhwch_and_Olwen",
        ],
    },
    "scottish": {
        "legends": [
            "Scottish_mythology",
            "Scottish_folklore",
            "Cailleach",
            "Blue_Men_of_the_Minch",
            "Each-uisge",
            "Selkie",
        ],
    },
    "manx": {
        "legends": [
            "Manx_folklore",
            "Buggane",
            "Moddey_Dhoo",
        ],
    },
}


def _crawl_wikipedia_mythology(
    tradition: str = "irish",
    category: str | None = None,
    max_pages: int = 50,
) -> Iterator[dict[str, Any]]:
    """Crawl Wikipedia for Celtic mythology articles."""
    try:
        from firecrawl import FirecrawlApp
    except ImportError:
        yield {
            "url": "https://en.wikipedia.org",
            "status": "firecrawl_not_installed",
            "tradition": tradition,
            "source": "wikipedia",
            "crawled_at": datetime.now(timezone.utc).isoformat(),
        }
        return

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        yield {
            "url": "https://en.wikipedia.org",
            "status": "no_api_key",
            "tradition": tradition,
            "source": "wikipedia",
            "crawled_at": datetime.now(timezone.utc).isoformat(),
        }
        return

    app = FirecrawlApp(api_key=api_key)

    # Get articles for this tradition
    tradition_sources = MYTHOLOGY_SOURCES.get(tradition, {})
    if category and category in tradition_sources:
        articles = tradition_sources[category]
    else:
        # Combine all categories for the tradition
        articles = []
        for cat_articles in tradition_sources.values():
            articles.extend(cat_articles)

    # Limit articles
    articles = articles[:max_pages]

    for article in articles:
        url = f"https://en.wikipedia.org/wiki/{article}"
        try:
            result = app.scrape_url(
                url,
                params={
                    "formats": ["markdown"],
                    "onlyMainContent": True,
                },
            )

            if result:
                metadata = result.get("metadata", {})
                yield {
                    "url": url,
                    "article_id": article,
                    "title": metadata.get("title", article.replace("_", " ")),
                    "description": metadata.get("description"),
                    "markdown": result.get("markdown"),
                    "tradition": tradition,
                    "category": category,
                    "source": "wikipedia",
                    "crawled_at": datetime.now(timezone.utc).isoformat(),
                    "status": "success",
                }
        except Exception as e:
            yield {
                "url": url,
                "article_id": article,
                "error": str(e),
                "tradition": tradition,
                "source": "wikipedia",
                "crawled_at": datetime.now(timezone.utc).isoformat(),
                "status": "error",
            }


def _crawl_celt_corpus(max_pages: int = 50) -> Iterator[dict[str, Any]]:
    """Crawl CELT (Corpus of Electronic Texts) for Irish mythology."""
    try:
        from firecrawl import FirecrawlApp
    except ImportError:
        return

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        return

    app = FirecrawlApp(api_key=api_key)

    # CELT mythology sections
    celt_sections = [
        "/published/T300000/",  # Mythological texts
        "/published/T300001/",  # Saga texts
    ]

    try:
        result = app.crawl_url(
            "https://celt.ucc.ie",
            params={
                "limit": max_pages,
                "maxDepth": 2,
                "includePaths": celt_sections,
                "scrapeOptions": {
                    "formats": ["markdown"],
                },
            },
            poll_interval=5,
        )

        for page in result.get("data", []):
            metadata = page.get("metadata", {})
            yield {
                "url": metadata.get("sourceURL"),
                "title": metadata.get("title"),
                "markdown": page.get("markdown"),
                "tradition": "irish",
                "source": "celt",
                "content_type": "primary_text",
                "crawled_at": datetime.now(timezone.utc).isoformat(),
                "status": "success",
            }
    except Exception:
        pass


def _generate_mythology_entities() -> Iterator[dict[str, Any]]:
    """Generate structured mythology entities for the game."""
    # Pre-defined entities with game-relevant attributes
    entities = [
        # Irish Deities
        {
            "id": "dagda",
            "name": "The Dagda",
            "name_ga": "An Dagda",
            "tradition": "irish",
            "entity_type": "deity",
            "attributes": ["strength", "wisdom", "abundance"],
            "artifacts": ["Cauldron of Plenty", "Club of Dagda", "Uaithne (harp)"],
            "domains": ["earth", "fertility", "magic"],
            "description": "Father god of the Tuatha Dé Danann, wielder of a magic club and owner of an inexhaustible cauldron.",
        },
        {
            "id": "brigid",
            "name": "Brigid",
            "name_ga": "Bríd",
            "tradition": "irish",
            "entity_type": "deity",
            "attributes": ["healing", "poetry", "smithcraft"],
            "domains": ["fire", "hearth", "spring"],
            "description": "Triple goddess of healing, poetry, and smithcraft. Associated with Imbolc.",
        },
        {
            "id": "lugh",
            "name": "Lugh",
            "name_ga": "Lugh Lámhfhada",
            "tradition": "irish",
            "entity_type": "deity",
            "attributes": ["skill", "light", "crafts"],
            "artifacts": ["Spear of Lugh", "Sling of Lugh"],
            "domains": ["sun", "skills", "oaths"],
            "description": "God of many skills, master craftsman and warrior. Associated with Lughnasadh.",
        },
        {
            "id": "morrigan",
            "name": "The Morrígan",
            "name_ga": "An Mórrígan",
            "tradition": "irish",
            "entity_type": "deity",
            "attributes": ["war", "fate", "prophecy"],
            "domains": ["battle", "sovereignty", "death"],
            "description": "Phantom queen, goddess of war and fate. Often appears as a crow.",
        },
        # Irish Heroes
        {
            "id": "cu_chulainn",
            "name": "Cú Chulainn",
            "name_ga": "Cú Chulainn",
            "tradition": "irish",
            "entity_type": "hero",
            "cycle": "Ulster Cycle",
            "attributes": ["strength", "battle_fury", "honor"],
            "artifacts": ["Gáe Bulg"],
            "description": "Hound of Ulster, greatest warrior of the Red Branch. Son of Lugh.",
        },
        {
            "id": "fionn",
            "name": "Fionn mac Cumhaill",
            "name_ga": "Fionn mac Cumhaill",
            "tradition": "irish",
            "entity_type": "hero",
            "cycle": "Fenian Cycle",
            "attributes": ["wisdom", "leadership", "hunting"],
            "artifacts": ["Salmon of Knowledge"],
            "description": "Leader of the Fianna, gained wisdom from the Salmon of Knowledge.",
        },
        # Welsh Deities
        {
            "id": "rhiannon",
            "name": "Rhiannon",
            "name_cy": "Rhiannon",
            "tradition": "welsh",
            "entity_type": "deity",
            "attributes": ["horses", "sovereignty", "otherworld"],
            "domains": ["moon", "horses", "magic"],
            "description": "Great Queen of the Otherworld, associated with horses and birds.",
        },
        {
            "id": "bran",
            "name": "Brân the Blessed",
            "name_cy": "Bendigeidfran",
            "tradition": "welsh",
            "entity_type": "deity",
            "attributes": ["protection", "hospitality", "prophecy"],
            "artifacts": ["Cauldron of Rebirth"],
            "description": "Giant king of Britain, his severed head protected the island.",
        },
        # Locations
        {
            "id": "tir_na_nog",
            "name": "Tír na nÓg",
            "name_ga": "Tír na nÓg",
            "tradition": "irish",
            "entity_type": "location",
            "location_type": "otherworld",
            "attributes": ["eternal_youth", "beauty", "timelessness"],
            "description": "Land of Eternal Youth, realm of the Tuatha Dé Danann beyond the western sea.",
        },
        {
            "id": "annwn",
            "name": "Annwn",
            "name_cy": "Annwn",
            "tradition": "welsh",
            "entity_type": "location",
            "location_type": "otherworld",
            "attributes": ["cauldron", "hunting", "magic"],
            "description": "Welsh Otherworld, realm of Arawn the death god.",
        },
    ]

    for entity in entities:
        entity["source"] = "structured"
        entity["generated_at"] = datetime.now(timezone.utc).isoformat()
        yield entity


@dlt.source(name="celtic_mythology")
def celtic_mythology_source(
    traditions: list[str] | None = None,
    max_pages_per_tradition: int = 50,
    include_celt: bool = True,
    include_entities: bool = True,
):
    """
    DLT source for Celtic mythology content.

    Args:
        traditions: List of traditions to include (irish, welsh, scottish, manx)
        max_pages_per_tradition: Maximum pages to crawl per tradition
        include_celt: Whether to include CELT corpus texts
        include_entities: Whether to include pre-structured game entities

    Returns:
        DLT source with mythology_articles, celt_texts, and mythology_entities
    """
    if traditions is None:
        traditions = ["irish", "welsh", "scottish", "manx"]

    @dlt.resource(
        name="mythology_articles",
        write_disposition="merge",
        primary_key=["url"],
    )
    def mythology_articles():
        """Wikipedia mythology articles."""
        for tradition in traditions:
            yield from _crawl_wikipedia_mythology(
                tradition=tradition,
                max_pages=max_pages_per_tradition,
            )

    @dlt.resource(
        name="celt_texts",
        write_disposition="merge",
        primary_key=["url"],
    )
    def celt_texts():
        """CELT primary source texts."""
        if include_celt:
            yield from _crawl_celt_corpus(max_pages=max_pages_per_tradition)

    @dlt.resource(
        name="mythology_entities",
        write_disposition="merge",
        primary_key=["id"],
    )
    def mythology_entities():
        """Structured mythology entities for game integration."""
        if include_entities:
            yield from _generate_mythology_entities()

    return mythology_articles, celt_texts, mythology_entities
