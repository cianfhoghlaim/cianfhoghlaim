"""
Spatial query tools for Tuath.

Query Celtic language regions, Gaeltacht boundaries,
and geospatial context for the game world.
"""

from typing import Any

from pydantic import BaseModel


class CelticRegion(BaseModel):
    """A Celtic language region."""

    id: str
    name: str
    native_name: str
    language: str
    language_name: str
    country: str
    region_type: str  # gaeltacht, gàidhealtachd, welsh_speaking
    speakers: int | None = None
    speaker_percentage: float | None = None
    description: str
    notable_places: list[str]
    game_zone: str | None = None


class GaeltachtInfo(BaseModel):
    """Detailed info about a Gaeltacht area."""

    id: str
    name: str
    native_name: str
    county: str
    population: int | None = None
    irish_speakers: int | None = None
    area_km2: float | None = None
    description: str
    dialects: list[str]
    notable_features: list[str]
    quests_available: list[str]
    npcs: list[str]


class RegionQueryResult(BaseModel):
    """Result from region query."""

    regions: list[CelticRegion]
    total: int
    query_type: str


async def query_celtic_regions(
    language: str | None = None,
    country: str | None = None,
    region_type: str | None = None,
    near_coordinates: tuple[float, float] | None = None,
    radius_km: float = 50.0,
) -> RegionQueryResult:
    """
    Query Celtic language regions.

    Args:
        language: Filter by language code (ga, gd, cy)
        country: Filter by country (ireland, scotland, wales)
        region_type: Filter by region type
        near_coordinates: Find regions near (lat, lon)
        radius_km: Radius for coordinate search

    Returns:
        RegionQueryResult with matching regions
    """
    results = []

    for region_id, region in CELTIC_REGIONS.items():
        # Apply filters
        if language and region["language"] != language:
            continue
        if country and region["country"] != country:
            continue
        if region_type and region["region_type"] != region_type:
            continue

        results.append(
            CelticRegion(
                id=region_id,
                name=region["name"],
                native_name=region["native_name"],
                language=region["language"],
                language_name=region["language_name"],
                country=region["country"],
                region_type=region["region_type"],
                speakers=region.get("speakers"),
                speaker_percentage=region.get("speaker_percentage"),
                description=region["description"],
                notable_places=region.get("notable_places", []),
                game_zone=region.get("game_zone"),
            )
        )

    return RegionQueryResult(
        regions=results,
        total=len(results),
        query_type="filter",
    )


async def get_gaeltacht_info(
    gaeltacht_id: str | None = None,
    name: str | None = None,
) -> GaeltachtInfo | list[GaeltachtInfo]:
    """
    Get detailed Gaeltacht information.

    Args:
        gaeltacht_id: Specific Gaeltacht ID
        name: Search by name (partial match)

    Returns:
        GaeltachtInfo or list of matches
    """
    if gaeltacht_id and gaeltacht_id in GAELTACHT_AREAS:
        area = GAELTACHT_AREAS[gaeltacht_id]
        return GaeltachtInfo(
            id=gaeltacht_id,
            name=area["name"],
            native_name=area["native_name"],
            county=area["county"],
            population=area.get("population"),
            irish_speakers=area.get("irish_speakers"),
            area_km2=area.get("area_km2"),
            description=area["description"],
            dialects=area.get("dialects", []),
            notable_features=area.get("notable_features", []),
            quests_available=area.get("quests", []),
            npcs=area.get("npcs", []),
        )

    # Search by name
    if name:
        name_lower = name.lower()
        matches = []
        for gid, area in GAELTACHT_AREAS.items():
            if (
                name_lower in area["name"].lower()
                or name_lower in area["native_name"].lower()
            ):
                matches.append(
                    GaeltachtInfo(
                        id=gid,
                        name=area["name"],
                        native_name=area["native_name"],
                        county=area["county"],
                        population=area.get("population"),
                        irish_speakers=area.get("irish_speakers"),
                        area_km2=area.get("area_km2"),
                        description=area["description"],
                        dialects=area.get("dialects", []),
                        notable_features=area.get("notable_features", []),
                        quests_available=area.get("quests", []),
                        npcs=area.get("npcs", []),
                    )
                )
        return matches

    # Return all if no filter
    return [
        GaeltachtInfo(
            id=gid,
            name=area["name"],
            native_name=area["native_name"],
            county=area["county"],
            population=area.get("population"),
            irish_speakers=area.get("irish_speakers"),
            area_km2=area.get("area_km2"),
            description=area["description"],
            dialects=area.get("dialects", []),
            notable_features=area.get("notable_features", []),
            quests_available=area.get("quests", []),
            npcs=area.get("npcs", []),
        )
        for gid, area in GAELTACHT_AREAS.items()
    ]


# Celtic language regions
CELTIC_REGIONS = {
    # Irish Gaeltacht
    "connemara": {
        "name": "Connemara",
        "native_name": "Conamara",
        "language": "ga",
        "language_name": "Irish",
        "country": "ireland",
        "region_type": "gaeltacht",
        "speakers": 20000,
        "speaker_percentage": 61.0,
        "description": "Largest Gaeltacht in Galway, known for its rugged landscapes and strong Irish traditions.",
        "notable_places": ["Spiddal", "Carraroe", "Carna", "Roundstone"],
        "game_zone": "conamara_realm",
    },
    "donegal": {
        "name": "Donegal Gaeltacht",
        "native_name": "Gaeltacht Dhún na nGall",
        "language": "ga",
        "language_name": "Irish",
        "country": "ireland",
        "region_type": "gaeltacht",
        "speakers": 24000,
        "speaker_percentage": 68.0,
        "description": "Northwestern Gaeltacht with distinctive Ulster Irish dialect.",
        "notable_places": ["Gweedore", "Gaoth Dobhair", "Arranmore Island"],
        "game_zone": "ulster_highlands",
    },
    "kerry": {
        "name": "Kerry Gaeltacht",
        "native_name": "Gaeltacht Chiarraí",
        "language": "ga",
        "language_name": "Irish",
        "country": "ireland",
        "region_type": "gaeltacht",
        "speakers": 10000,
        "speaker_percentage": 50.0,
        "description": "Munster Gaeltacht on the Dingle Peninsula and Iveragh.",
        "notable_places": ["Dingle", "Ballyferriter", "Ventry"],
        "game_zone": "munster_coast",
    },
    "aran_islands": {
        "name": "Aran Islands",
        "native_name": "Oileáin Árann",
        "language": "ga",
        "language_name": "Irish",
        "country": "ireland",
        "region_type": "gaeltacht",
        "speakers": 1200,
        "speaker_percentage": 85.0,
        "description": "Three islands in Galway Bay with ancient Celtic heritage.",
        "notable_places": ["Inis Mór", "Inis Meáin", "Inis Oírr", "Dún Aonghasa"],
        "game_zone": "aran_isles",
    },

    # Scottish Gàidhealtachd
    "western_isles": {
        "name": "Western Isles",
        "native_name": "Na h-Eileanan Siar",
        "language": "gd",
        "language_name": "Scottish Gaelic",
        "country": "scotland",
        "region_type": "gàidhealtachd",
        "speakers": 15000,
        "speaker_percentage": 52.0,
        "description": "Outer Hebrides with the highest concentration of Gaelic speakers.",
        "notable_places": ["Stornoway", "Lewis", "Harris", "Barra"],
        "game_zone": "hebridean_realm",
    },
    "skye": {
        "name": "Isle of Skye",
        "native_name": "An t-Eilean Sgitheanach",
        "language": "gd",
        "language_name": "Scottish Gaelic",
        "country": "scotland",
        "region_type": "gàidhealtachd",
        "speakers": 2500,
        "speaker_percentage": 25.0,
        "description": "Legendary island with Gaelic heritage and dramatic landscapes.",
        "notable_places": ["Portree", "Dunvegan", "Sleat", "Trotternish"],
        "game_zone": "skye_highlands",
    },

    # Welsh-speaking areas
    "gwynedd": {
        "name": "Gwynedd",
        "native_name": "Gwynedd",
        "language": "cy",
        "language_name": "Welsh",
        "country": "wales",
        "region_type": "welsh_speaking",
        "speakers": 77000,
        "speaker_percentage": 65.0,
        "description": "Heartland of Welsh language in northwest Wales.",
        "notable_places": ["Caernarfon", "Bangor", "Porthmadog", "Dolgellau"],
        "game_zone": "gwynedd_kingdom",
    },
    "ynys_mon": {
        "name": "Anglesey",
        "native_name": "Ynys Môn",
        "language": "cy",
        "language_name": "Welsh",
        "country": "wales",
        "region_type": "welsh_speaking",
        "speakers": 38000,
        "speaker_percentage": 57.0,
        "description": "Island with strong Welsh traditions and druidic heritage.",
        "notable_places": ["Holyhead", "Beaumaris", "Llanfairpwll"],
        "game_zone": "druid_isle",
    },
    "ceredigion": {
        "name": "Ceredigion",
        "native_name": "Ceredigion",
        "language": "cy",
        "language_name": "Welsh",
        "country": "wales",
        "region_type": "welsh_speaking",
        "speakers": 47000,
        "speaker_percentage": 47.0,
        "description": "West Wales coastal region with Welsh university town.",
        "notable_places": ["Aberystwyth", "Cardigan", "Lampeter"],
        "game_zone": "west_wales",
    },
}

# Detailed Gaeltacht information
GAELTACHT_AREAS = {
    "conamara": {
        "name": "Connemara",
        "native_name": "Conamara",
        "county": "Galway",
        "population": 33000,
        "irish_speakers": 20000,
        "area_km2": 1200,
        "description": "Wild Atlantic landscape with bogs, lakes, and the Twelve Bens mountains. Strongest Irish-speaking community.",
        "dialects": ["Connacht Irish"],
        "notable_features": [
            "Twelve Bens mountains",
            "Connemara ponies",
            "Traditional currach boats",
            "Seaweed harvesting",
        ],
        "quests": ["gaeltacht_journey", "connemara_bard", "atlantic_fishing"],
        "npcs": ["Séamas the Fisherman", "Bríd the Weaver", "Peadar the Storyteller"],
    },
    "gaoth_dobhair": {
        "name": "Gweedore",
        "native_name": "Gaoth Dobhair",
        "county": "Donegal",
        "population": 4000,
        "irish_speakers": 3000,
        "area_km2": 150,
        "description": "Coastal community in northwest Donegal with distinctive Ulster Irish.",
        "dialects": ["Ulster Irish"],
        "notable_features": [
            "Mount Errigal",
            "Bloody Foreland",
            "Tory Island nearby",
            "Traditional music scene",
        ],
        "quests": ["ulster_legends", "tory_island_voyage", "errigal_ascent"],
        "npcs": ["Máire the Musician", "Dónall the Boatman"],
    },
    "corca_dhuibhne": {
        "name": "Corca Dhuibhne",
        "native_name": "Corca Dhuibhne",
        "county": "Kerry",
        "population": 10000,
        "irish_speakers": 6000,
        "area_km2": 400,
        "description": "Dingle Peninsula Gaeltacht with rich archaeological heritage.",
        "dialects": ["Munster Irish"],
        "notable_features": [
            "Blasket Islands",
            "Gallarus Oratory",
            "Mount Brandon",
            "Beehive huts",
        ],
        "quests": ["blasket_memories", "brandon_pilgrimage", "munster_poetry"],
        "npcs": ["Tomás the Elder", "Siobhán of the Islands"],
    },
    "aran": {
        "name": "Aran Islands",
        "native_name": "Oileáin Árann",
        "county": "Galway",
        "population": 1200,
        "irish_speakers": 1000,
        "area_km2": 46,
        "description": "Three limestone islands with prehistoric forts and monastic sites.",
        "dialects": ["Connacht Irish"],
        "notable_features": [
            "Dún Aonghasa fort",
            "Aran sweaters",
            "Currach boats",
            "Stone walls",
        ],
        "quests": ["dun_aonghasa_mystery", "island_traditions", "aran_craft"],
        "npcs": ["Liam the Knitter", "Colm the Fort Keeper"],
    },
}


# Game zone mappings
GAME_ZONES = {
    "tutorial_zone": {
        "name": "The Village of Beginnings",
        "native_name": "Sráidbhaile na Tosaithe",
        "type": "tutorial",
        "languages": ["ga", "en"],
        "level_range": (1, 5),
    },
    "conamara_realm": {
        "name": "Realm of Connemara",
        "native_name": "Ríocht Chonamara",
        "type": "gaeltacht",
        "languages": ["ga"],
        "level_range": (5, 15),
    },
    "ulster_highlands": {
        "name": "Ulster Highlands",
        "native_name": "Ardchríocha Uladh",
        "type": "gaeltacht",
        "languages": ["ga"],
        "level_range": (10, 20),
    },
    "munster_coast": {
        "name": "Munster Coast",
        "native_name": "Cósta na Mumhan",
        "type": "gaeltacht",
        "languages": ["ga"],
        "level_range": (8, 18),
    },
    "aran_isles": {
        "name": "Islands of Aran",
        "native_name": "Oileáin Árann",
        "type": "gaeltacht",
        "languages": ["ga"],
        "level_range": (12, 22),
    },
    "hebridean_realm": {
        "name": "Hebridean Realm",
        "native_name": "Rìoghachd nan Eilean",
        "type": "gàidhealtachd",
        "languages": ["gd"],
        "level_range": (15, 25),
    },
    "skye_highlands": {
        "name": "Skye Highlands",
        "native_name": "Gàidhealtachd an Eilein Sgitheanaich",
        "type": "gàidhealtachd",
        "languages": ["gd"],
        "level_range": (18, 28),
    },
    "gwynedd_kingdom": {
        "name": "Kingdom of Gwynedd",
        "native_name": "Teyrnas Gwynedd",
        "type": "welsh_speaking",
        "languages": ["cy"],
        "level_range": (15, 25),
    },
    "druid_isle": {
        "name": "Druid's Isle",
        "native_name": "Ynys y Derwyddon",
        "type": "welsh_speaking",
        "languages": ["cy"],
        "level_range": (20, 30),
    },
    "otherworld": {
        "name": "The Otherworld",
        "native_name": "An Saol Eile / Annwfn",
        "type": "mythological",
        "languages": ["ga", "gd", "cy"],
        "level_range": (25, 40),
    },
}
