"""
Geospatial API Routes.

Celtic language region data and Gaeltacht information.
"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

router = APIRouter()


class CelticRegion(BaseModel):
    """A Celtic language region."""

    id: str
    name: str
    native_name: str
    language: str
    language_name: str
    country: str
    region_type: str
    speakers: int | None = None
    speaker_percentage: float | None = None
    description: str
    notable_places: list[str]
    game_zone: str | None = None
    coordinates: dict | None = None


class GaeltachtArea(BaseModel):
    """Detailed Gaeltacht area information."""

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
    quests: list[str]
    npcs: list[str]
    coordinates: dict | None = None


@router.get("/regions")
async def get_celtic_regions(
    language: str | None = Query(None, description="Filter by language (ga, gd, cy)"),
    country: str | None = Query(None, description="Filter by country (ireland, scotland, wales)"),
    region_type: str | None = Query(None, description="Filter by type"),
):
    """Get Celtic language regions."""
    regions = [
        # Irish Gaeltacht regions
        CelticRegion(
            id="connemara",
            name="Connemara",
            native_name="Conamara",
            language="ga",
            language_name="Irish",
            country="ireland",
            region_type="gaeltacht",
            speakers=20000,
            speaker_percentage=61.0,
            description="Largest Gaeltacht in Galway, known for rugged landscapes and strong Irish traditions.",
            notable_places=["Spiddal", "Carraroe", "Carna", "Roundstone"],
            game_zone="conamara_realm",
            coordinates={"lat": 53.4, "lon": -9.8},
        ),
        CelticRegion(
            id="donegal",
            name="Donegal Gaeltacht",
            native_name="Gaeltacht Dhún na nGall",
            language="ga",
            language_name="Irish",
            country="ireland",
            region_type="gaeltacht",
            speakers=24000,
            speaker_percentage=68.0,
            description="Northwestern Gaeltacht with distinctive Ulster Irish dialect.",
            notable_places=["Gweedore", "Gaoth Dobhair", "Arranmore Island"],
            game_zone="ulster_highlands",
            coordinates={"lat": 55.0, "lon": -8.3},
        ),
        CelticRegion(
            id="kerry",
            name="Kerry Gaeltacht",
            native_name="Gaeltacht Chiarraí",
            language="ga",
            language_name="Irish",
            country="ireland",
            region_type="gaeltacht",
            speakers=10000,
            speaker_percentage=50.0,
            description="Munster Gaeltacht on the Dingle Peninsula.",
            notable_places=["Dingle", "Ballyferriter", "Ventry"],
            game_zone="munster_coast",
            coordinates={"lat": 52.1, "lon": -10.3},
        ),
        CelticRegion(
            id="aran_islands",
            name="Aran Islands",
            native_name="Oileáin Árann",
            language="ga",
            language_name="Irish",
            country="ireland",
            region_type="gaeltacht",
            speakers=1200,
            speaker_percentage=85.0,
            description="Three islands in Galway Bay with ancient Celtic heritage.",
            notable_places=["Inis Mór", "Inis Meáin", "Inis Oírr", "Dún Aonghasa"],
            game_zone="aran_isles",
            coordinates={"lat": 53.1, "lon": -9.7},
        ),
        # Scottish Gàidhealtachd
        CelticRegion(
            id="western_isles",
            name="Western Isles",
            native_name="Na h-Eileanan Siar",
            language="gd",
            language_name="Scottish Gaelic",
            country="scotland",
            region_type="gàidhealtachd",
            speakers=15000,
            speaker_percentage=52.0,
            description="Outer Hebrides with highest concentration of Gaelic speakers.",
            notable_places=["Stornoway", "Lewis", "Harris", "Barra"],
            game_zone="hebridean_realm",
            coordinates={"lat": 58.2, "lon": -6.8},
        ),
        CelticRegion(
            id="skye",
            name="Isle of Skye",
            native_name="An t-Eilean Sgitheanach",
            language="gd",
            language_name="Scottish Gaelic",
            country="scotland",
            region_type="gàidhealtachd",
            speakers=2500,
            speaker_percentage=25.0,
            description="Legendary island with Gaelic heritage and dramatic landscapes.",
            notable_places=["Portree", "Dunvegan", "Sleat", "Trotternish"],
            game_zone="skye_highlands",
            coordinates={"lat": 57.3, "lon": -6.2},
        ),
        # Welsh-speaking areas
        CelticRegion(
            id="gwynedd",
            name="Gwynedd",
            native_name="Gwynedd",
            language="cy",
            language_name="Welsh",
            country="wales",
            region_type="welsh_speaking",
            speakers=77000,
            speaker_percentage=65.0,
            description="Heartland of Welsh language in northwest Wales.",
            notable_places=["Caernarfon", "Bangor", "Porthmadog", "Dolgellau"],
            game_zone="gwynedd_kingdom",
            coordinates={"lat": 52.9, "lon": -4.1},
        ),
        CelticRegion(
            id="ynys_mon",
            name="Anglesey",
            native_name="Ynys Môn",
            language="cy",
            language_name="Welsh",
            country="wales",
            region_type="welsh_speaking",
            speakers=38000,
            speaker_percentage=57.0,
            description="Island with strong Welsh traditions and druidic heritage.",
            notable_places=["Holyhead", "Beaumaris", "Llanfairpwll"],
            game_zone="druid_isle",
            coordinates={"lat": 53.3, "lon": -4.3},
        ),
    ]

    # Apply filters
    if language:
        regions = [r for r in regions if r.language == language]
    if country:
        regions = [r for r in regions if r.country == country]
    if region_type:
        regions = [r for r in regions if r.region_type == region_type]

    return {
        "regions": regions,
        "total": len(regions),
    }


@router.get("/regions/{region_id}")
async def get_region(region_id: str):
    """Get a specific Celtic region."""
    regions = await get_celtic_regions()
    for region in regions["regions"]:
        if region.id == region_id:
            return region

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Region '{region_id}' not found",
    )


@router.get("/gaeltacht")
async def get_gaeltacht_areas():
    """Get detailed Gaeltacht area information."""
    areas = [
        GaeltachtArea(
            id="conamara",
            name="Connemara",
            native_name="Conamara",
            county="Galway",
            population=33000,
            irish_speakers=20000,
            area_km2=1200,
            description="Wild Atlantic landscape with bogs, lakes, and the Twelve Bens mountains.",
            dialects=["Connacht Irish"],
            notable_features=[
                "Twelve Bens mountains",
                "Connemara ponies",
                "Traditional currach boats",
            ],
            quests=["gaeltacht_journey", "connemara_bard", "atlantic_fishing"],
            npcs=["Séamas the Fisherman", "Bríd the Weaver", "Peadar the Storyteller"],
            coordinates={"lat": 53.4, "lon": -9.8},
        ),
        GaeltachtArea(
            id="gaoth_dobhair",
            name="Gweedore",
            native_name="Gaoth Dobhair",
            county="Donegal",
            population=4000,
            irish_speakers=3000,
            area_km2=150,
            description="Coastal community in northwest Donegal with distinctive Ulster Irish.",
            dialects=["Ulster Irish"],
            notable_features=["Mount Errigal", "Bloody Foreland", "Tory Island nearby"],
            quests=["ulster_legends", "tory_island_voyage", "errigal_ascent"],
            npcs=["Máire the Musician", "Dónall the Boatman"],
            coordinates={"lat": 55.05, "lon": -8.3},
        ),
        GaeltachtArea(
            id="corca_dhuibhne",
            name="Corca Dhuibhne",
            native_name="Corca Dhuibhne",
            county="Kerry",
            population=10000,
            irish_speakers=6000,
            area_km2=400,
            description="Dingle Peninsula Gaeltacht with rich archaeological heritage.",
            dialects=["Munster Irish"],
            notable_features=["Blasket Islands", "Gallarus Oratory", "Mount Brandon"],
            quests=["blasket_memories", "brandon_pilgrimage", "munster_poetry"],
            npcs=["Tomás the Elder", "Siobhán of the Islands"],
            coordinates={"lat": 52.15, "lon": -10.35},
        ),
        GaeltachtArea(
            id="aran",
            name="Aran Islands",
            native_name="Oileáin Árann",
            county="Galway",
            population=1200,
            irish_speakers=1000,
            area_km2=46,
            description="Three limestone islands with prehistoric forts and monastic sites.",
            dialects=["Connacht Irish"],
            notable_features=["Dún Aonghasa fort", "Aran sweaters", "Currach boats"],
            quests=["dun_aonghasa_mystery", "island_traditions", "aran_craft"],
            npcs=["Liam the Knitter", "Colm the Fort Keeper"],
            coordinates={"lat": 53.1, "lon": -9.7},
        ),
    ]

    return {
        "gaeltacht_areas": areas,
        "total": len(areas),
    }


@router.get("/gaeltacht/{area_id}")
async def get_gaeltacht_area(area_id: str):
    """Get a specific Gaeltacht area."""
    areas = await get_gaeltacht_areas()
    for area in areas["gaeltacht_areas"]:
        if area.id == area_id:
            return area

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Gaeltacht area '{area_id}' not found",
    )


@router.get("/game-zones")
async def get_game_zones():
    """Get game world zones mapped to Celtic regions."""
    return {
        "zones": [
            {
                "id": "tutorial_zone",
                "name": "The Village of Beginnings",
                "native_name": "Sráidbhaile na Tosaithe",
                "type": "tutorial",
                "languages": ["ga", "en"],
                "level_range": [1, 5],
                "based_on": None,
            },
            {
                "id": "conamara_realm",
                "name": "Realm of Connemara",
                "native_name": "Ríocht Chonamara",
                "type": "gaeltacht",
                "languages": ["ga"],
                "level_range": [5, 15],
                "based_on": "connemara",
            },
            {
                "id": "ulster_highlands",
                "name": "Ulster Highlands",
                "native_name": "Ardchríocha Uladh",
                "type": "gaeltacht",
                "languages": ["ga"],
                "level_range": [10, 20],
                "based_on": "donegal",
            },
            {
                "id": "munster_coast",
                "name": "Munster Coast",
                "native_name": "Cósta na Mumhan",
                "type": "gaeltacht",
                "languages": ["ga"],
                "level_range": [8, 18],
                "based_on": "kerry",
            },
            {
                "id": "aran_isles",
                "name": "Islands of Aran",
                "native_name": "Oileáin Árann",
                "type": "gaeltacht",
                "languages": ["ga"],
                "level_range": [12, 22],
                "based_on": "aran_islands",
            },
            {
                "id": "hebridean_realm",
                "name": "Hebridean Realm",
                "native_name": "Rìoghachd nan Eilean",
                "type": "gàidhealtachd",
                "languages": ["gd"],
                "level_range": [15, 25],
                "based_on": "western_isles",
            },
            {
                "id": "skye_highlands",
                "name": "Skye Highlands",
                "native_name": "Gàidhealtachd an Eilein Sgitheanaich",
                "type": "gàidhealtachd",
                "languages": ["gd"],
                "level_range": [18, 28],
                "based_on": "skye",
            },
            {
                "id": "gwynedd_kingdom",
                "name": "Kingdom of Gwynedd",
                "native_name": "Teyrnas Gwynedd",
                "type": "welsh_speaking",
                "languages": ["cy"],
                "level_range": [15, 25],
                "based_on": "gwynedd",
            },
            {
                "id": "druid_isle",
                "name": "Druid's Isle",
                "native_name": "Ynys y Derwyddon",
                "type": "welsh_speaking",
                "languages": ["cy"],
                "level_range": [20, 30],
                "based_on": "ynys_mon",
            },
            {
                "id": "otherworld",
                "name": "The Otherworld",
                "native_name": "An Saol Eile / Annwfn",
                "type": "mythological",
                "languages": ["ga", "gd", "cy"],
                "level_range": [25, 40],
                "based_on": None,
            },
        ],
    }


@router.get("/dialects")
async def get_celtic_dialects():
    """Get information about Celtic language dialects."""
    return {
        "dialects": {
            "irish": [
                {
                    "id": "connacht",
                    "name": "Connacht Irish",
                    "native_name": "Gaeilge Chonnacht",
                    "regions": ["Connemara", "Aran Islands", "Mayo"],
                    "features": ["Strong stress on first syllable", "Preservation of verbal noun"],
                },
                {
                    "id": "munster",
                    "name": "Munster Irish",
                    "native_name": "Gaeilge na Mumhan",
                    "regions": ["Kerry", "Cork", "Waterford"],
                    "features": ["Stress on long syllables", "Distinctive intonation"],
                },
                {
                    "id": "ulster",
                    "name": "Ulster Irish",
                    "native_name": "Gaeilge Uladh",
                    "regions": ["Donegal", "Tyrone (historical)"],
                    "features": ["Scottish Gaelic influence", "Archaic vocabulary"],
                },
            ],
            "scottish_gaelic": [
                {
                    "id": "lewis",
                    "name": "Lewis Gaelic",
                    "native_name": "Gàidhlig Leòdhais",
                    "regions": ["Lewis", "Harris"],
                    "features": ["Conservative pronunciation", "Strong community"],
                },
                {
                    "id": "skye",
                    "name": "Skye Gaelic",
                    "native_name": "Gàidhlig an Eilein Sgitheanaich",
                    "regions": ["Skye", "Lochalsh"],
                    "features": ["Mainland influence", "Tourism impact"],
                },
            ],
            "welsh": [
                {
                    "id": "north",
                    "name": "Northern Welsh",
                    "native_name": "Cymraeg y Gogledd",
                    "regions": ["Gwynedd", "Anglesey"],
                    "features": ["Traditional forms", "Strong community"],
                },
                {
                    "id": "south",
                    "name": "Southern Welsh",
                    "native_name": "Cymraeg y De",
                    "regions": ["Carmarthen", "Swansea area"],
                    "features": ["Urban influence", "English borrowings"],
                },
            ],
        },
    }
