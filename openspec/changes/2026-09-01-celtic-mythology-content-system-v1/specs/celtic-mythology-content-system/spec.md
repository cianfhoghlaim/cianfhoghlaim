## ADDED Requirements

### Requirement: BAML SSOT for 8 Celtic mythology functions

The system SHALL provide BAML functions in `baml/celtic/mythology.baml`
that extract: `ExtractCelticDeity`, `ExtractGeis`, `ExtractOghamInscription`,
`ExtractHeroCycle`, `ExtractPentElementalAffinity`, `ExtractMythologyQuest`,
`BuildGameAssetFromLO`, `ComposeMythologyNarrative`. No Pydantic / Zod
duplicate classes SHALL exist; Pydantic + Zod are codegen only.

#### Scenario: ExtractCelticDeity succeeds
- **WHEN** the user invokes `ExtractCelticDeity` on the raw text "Brigid, daughter of the Dagda, patroness of poetry, smithing, and healing in Irish mythology"
- **THEN** the function returns a `CelticDeity` Pydantic model with `nation="irish"`, `name="Brigid"`, `father="the Dagda"`, `domains=["poetry","smithing","healing"]`, `pantheon="tuatha_de_danann"`, `element="fire"`

#### Scenario: ExtractGeis returns boons and banes
- **WHEN** the user invokes `ExtractGeis` on the Cúchulainn text "He must never eat the flesh of a dog, nor refuse a meal offered to him"
- **THEN** the function returns a `Geis` Pydantic model with `subject="Cúchulainn"`, `boons=["never refuse a meal"]`, `banes=["never eat dog flesh"]`, `consequence="death by betrayal"`

#### Scenario: ExtractOghamInscription recognises aicme
- **WHEN** the user invokes `ExtractOghamInscription` on the text "B L N F S — the Ogham inscription B L N F S (Beith, Luis, Nion, Fear, Saille) belongs to the Aicme Beith"
- **THEN** the function returns an `OghamInscription` Pydantic model with `letters=["B","L","N","F","S"]`, `aicme="beith"`, `translation="(lineage marker)"`, `stone_id="CISP-CW-001"`

#### Scenario: ExtractHeroCycle covers Cúchulainn
- **WHEN** the user invokes `ExtractHeroCycle` on the Cúchulainn text "Sétanta, son of Sualtam, slew the hound of Culann and became Cúchulainn"
- **THEN** the function returns a `HeroCycle` Pydantic model with `birth_name="Sétanta"`, `name="Cúchulainn"`, `cycle="ulster"`, `weapon="Gáe Bolg"`, `origin="the boy corps of Emain Macha"`

### Requirement: BAML SSOT for 6 Irish dynastic history functions

The system SHALL provide BAML functions in `baml/celtic/irish_history.baml`
that extract: `ExtractIrishDynasty` (Tuatha Dé Danann, Uí Liatháin, Déisí,
Aileach, Uí Néill, Eóganachta), `ExtractProvincialKingdom`, `ExtractTimelineEvent`,
`ExtractHighKing`, `ExtractFomoriansBattle`, `ExtractNormanImpact`.

#### Scenario: ExtractIrishDynasty covers the 6 mandated families
- **WHEN** the user invokes `ExtractIrishDynasty` over a corpus of 1,000 history texts
- **THEN** the function SHALL successfully extract at least one record for each of the 6 mandated families: Tuatha Dé Danann, Uí Liatháin, Déisí, Aileach, Uí Néill, Eóganachta

#### Scenario: ExtractProvincialKingdom returns 4 provinces
- **WHEN** the user invokes `ExtractProvincialKingdom` on "The Kingdom of Osraige bordered Leinster and Munster"
- **THEN** the function returns a `ProvincialKingdom` Pydantic model with `name="Osraige"`, `borders=["Leinster","Munster"]`, `period="5th-12th c."`

#### Scenario: ExtractTimelineEvent anchors chronology
- **WHEN** the user invokes `ExtractTimelineEvent` on "The Battle of Clontarf took place in 1014 AD between the forces of Brian Boru and a coalition of Norse and Leinster rebels"
- **THEN** the function returns a `TimelineEvent` Pydantic model with `year=1014`, `event="Battle of Clontarf"`, `actors=["Brian Boru", "Norse", "Leinster"]`, `outcome="Brian Boru killed; Norse power broken"`

#### Scenario: ExtractHighKing identifies the High King of Ireland
- **WHEN** the user invokes `ExtractHighKing` on "Niall Caille, of the Uí Néill, was High King of Ireland from 833 to 846 AD"
- **THEN** the function returns a `HighKing` Pydantic model with `name="Niall Caille"`, `dynasty="Uí Néill"`, `start_year=833`, `end_year=846`, `province="Midhe"`

### Requirement: Geography curriculum binding for 4 syllabuses

The system SHALL map the Leaving Certificate Geography (5 core + 4
elective units), English A-Level Geography (7 topics), Scottish CfE
Higher Geography (5 areas), and Welsh WJEC Geography (3 themes) to the
BIEP v3 `lessonObjective` table via 4 BAML functions in
`baml/celtic/geography_curriculum.baml`.

#### Scenario: LC Geography unit 1.1 mapped
- **WHEN** the user invokes `ExtractLCGeographyOutcome` on "LC Geography Core Unit 1.1: The Earth's surface — plate tectonics"
- **THEN** the function returns a `GeographyOutcome` Pydantic model with `syllabus="lc_geography"`, `unit="1.1"`, `topic="plate_tectonics"`, `learning_objective_id="LCGEO-1.1-PT"`

#### Scenario: A-Level Geography topic 2.3 mapped
- **WHEN** the user invokes `ExtractALevelGeographyTopic` on "A-Level Geography Topic 2.3: Globalisation — its impacts on people, places and environments"
- **THEN** the function returns a `GeographyOutcome` Pydantic model with `syllabus="a_level_geography"`, `topic="globalisation"`, `learning_objective_id="ALGEO-2.3-GLB"`

#### Scenario: CfE Geography Area 4 mapped
- **WHEN** the user invokes `ExtractCfEGeographyArea` on "CfE Higher Geography Area 4: Population Geography"
- **THEN** the function returns a `GeographyOutcome` Pydantic model with `syllabus="cfe_higher_geography"`, `area="population"`, `learning_objective_id="CFEHG-4-POP"`

### Requirement: Interactive British Isles map with 4-level drill-down

The system SHALL provide a marimo + Altair visualisation in
`notebooks/32_british_isles_map.py` that supports drill-down through
4 levels: subnation (6 nations) → subprovince (provinces / regions /
counties groups) → subcounty (counties / council areas / principal
areas) → settlement (towns / villages / parishes). The map SHALL be
built on TopoJSON + Altair + ibis + DuckDB (DuckLake-backed).

#### Scenario: Drill from Ireland → Munster → Cork → Cobh
- **WHEN** the user clicks on Ireland in the subnation map
- **THEN** the map transitions to subprovince view showing the 4 provinces
- **WHEN** the user clicks on Munster
- **THEN** the map transitions to subcounty view showing the 6 Munster counties
- **WHEN** the user clicks on Cork
- **THEN** the map transitions to settlement view showing the 12 main Cork settlements

#### Scenario: GeoAI op renders within the map
- **WHEN** the user invokes `hotspot` on the Cork settlement layer
- **THEN** the map overlays a Getis-Ord Gi* heatmap highlighting statistically significant spatial clusters

#### Scenario: Map renders all 6 nations
- **WHEN** the user opens the British Isles map at the subnation level
- **THEN** the map SHALL display all 6 nations: Ireland, Scotland, Wales, England, Isle of Man, Cornwall

### Requirement: GeoAI + DuckDB / ibis / DuckLake spatial analysis

The system SHALL provide `notebooks/_shared/geoai.py` with 12 standard
GeoAI operations (buffer / intersect / distance / centroid / area /
simplify / union / dissolve / convex_hull / voronoi / kriging / hotspot)
operating on ibis tables backed by DuckDB queries against DuckLake.

#### Scenario: Buffer op on a settlement
- **WHEN** the user invokes `geo.buffer(settlements_table, radius_m=5000)`
- **THEN** the function returns an ibis table with a new `buffer_geom` column containing the 5km buffers around each settlement

#### Scenario: Intersect op on two layers
- **WHEN** the user invokes `geo.intersect(coalitions_layer, cisp_stones_layer)`
- **THEN** the function returns an ibis table with the intersection geometries

#### Scenario: Kriging op on rainfall data
- **WHEN** the user invokes `geo.kriging(met_office_rainfall_table, x="lon", y="lat", value="mm_hr")`
- **THEN** the function returns a GeoTIFF with interpolated rainfall surface

### Requirement: Celtic Mythology Agent with 8 tools

The system SHALL provide `agents/meaisinfhoghlaim/educational/celtic_mythology_agent.py`
as an ADK agent exposing 8 tools. The agent SHALL be registered in
`agents/agent_registry.py:AGENT_REGISTRY` with `framework="adk"`,
`litellm_routing_key="mythology"`.

#### Scenario: Mythology agent queries a deity
- **WHEN** the user invokes `celtic_mythology_agent` with the query "Who is Manannán mac Lir?"
- **THEN** the agent returns a `CelticDeity` Pydantic model with `nation="irish"`, `name="Manannán mac Lir"`, `domains=["sea","travel","trade"]`, `pantheon="tuatha_de_danann"`, `element="water"`

#### Scenario: Mythology agent queries a hero cycle
- **WHEN** the user invokes `celtic_mythology_agent` with the query "Tell me about Cúchulainn"
- **THEN** the agent returns a `HeroCycle` Pydantic model

### Requirement: Irish History Agent with 6 tools

The system SHALL provide `agents/meaisinfhoghlaim/educational/irish_history_agent.py`
as an ADK agent exposing 6 tools for the 6 Irish dynastic families.
The agent SHALL be registered in `agents/agent_registry.py:AGENT_REGISTRY`.

#### Scenario: Uí Liatháin dynasty query
- **WHEN** the user invokes `irish_history_agent` with "Tell me about Uí Liatháin"
- **THEN** the agent returns an `IrishDynasty` Pydantic model with `family="Uí Liatháin"`, `province="Munster"`, `period="4th-12th c."`, `territory="modern Co. Cork"`

#### Scenario: Aileach dynasty query
- **WHEN** the user invokes `irish_history_agent` with "Tell me about Aileach"
- **THEN** the agent returns an `IrishDynasty` Pydantic model with `family="Aileach"`, `province="Ulster"`, `period="5th-12th c."`, `territory="modern Co. Donegal"`, `capital="Grianan of Aileach"`

### Requirement: Educational Geography Agent with 10 tools

The system SHALL provide `agents/meaisinfhoghlaim/educational/educational_geography_agent.py`
as an ADK agent exposing 10 tools for the 4 syllabuses (LC + A-Level +
CfE + WJEC) + GeoAI ops + map rendering.

#### Scenario: LC Geography Core Unit 1.1 query
- **WHEN** the user invokes `educational_geography_agent` with "LC Geography Core Unit 1.1 learning outcomes"
- **THEN** the agent returns the 7 learning outcomes for the unit, cross-referenced to the BIEP v3 lessonObjective table

#### Scenario: GeoAI buffer op via agent
- **WHEN** the user invokes `educational_geography_agent` with "buffer the Cork settlements by 5km"
- **THEN** the agent invokes `geo.buffer` and returns the buffer geometries

### Requirement: CocoIndex v1 embedding for mythology + Irish history

The system SHALL provide 2 CocoIndex v1 Apps
(`cocoindex_flows/biep_parity/mythology_embedding.py`,
`cocoindex_flows/biep_parity/irish_history_embedding.py`) conforming to R1-R4.

#### Scenario: Both Apps materialise via mise run biep:v3:mythology
- **WHEN** the user invokes `mise run biep:v3:mythology`
- **THEN** the mythology + irish_history CocoIndex Apps SHALL successfully materialise ≥1,000 rows each to DuckLake