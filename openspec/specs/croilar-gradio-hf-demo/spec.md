# croilar-gradio-hf-demo Specification

## Purpose
TBD - created by archiving change croilar-hf-build-small-2026-demo. Update Purpose after archive.
## Requirements
### Requirement: Space 1 "An Scrúdú" — Oideachais North-Star Demo
The system SHALL publish a Gradio Space under `build-small-hackathon/an-scrudai` that demonstrates the oideachais quadrant's typed-data pipeline for 33 Leaving Cert subjects across 17 years of exam papers and marking schemes.

#### Scenario: Subject syllabus heatmap renders
- **WHEN** a visitor opens the Space and selects "Mathematics Higher Level" from the 33-subject dropdown
- **THEN** the NCCA syllabus heatmap SHALL render with one row per syllabus topic, columns for years 2017–2025, and colour-coded cell values representing the topic's weightPct × question frequency
- **AND** the BAML function `ExtractLeavingCertSyllabus` from `oideachais/data_platform/baml_src/leaving_cert_syllabus_extraction.baml` SHALL be the data source
- **AND** the headline counter SHALL show "33 subjects × 17 years × 1 typed pipeline"

#### Scenario: New papers detected feed
- **WHEN** a new exam paper PDF arrives in the Dagster ingestion queue (modelled by the `exam_materials_assets.py:101-107` DynamicPartitionsDefinition sensor)
- **THEN** a live badge SHALL appear in the Gradio sidebar within 30 seconds showing the new subject/year/level that just arrived
- **AND** the badge SHALL be clickable to jump to the heatmap filtered by the new paper

### Requirement: Space 2 "Meaisín Cliste" — Meaisínfhoghlaim 3-Theme Demo
The system SHALL publish a Gradio Space under `build-small-hackathon/meaisin-cliste` that demonstrates the meaisínfhoghlaim quadrant as three themes side-by-side (Foclóir na Sé Náisiún, Scoil ar an Léarscáil, Curaclam Trasteorann), covering 7 Celtic nations.

#### Scenario: Foclóir cognate ripple across 7 nations
- **WHEN** a visitor types an English word (e.g. "house") into the Foclóir tab
- **THEN** a 7-row cognate table SHALL render with `teach` (Irish), `taigh` (Scottish Gaelic), `tŷ` (Welsh), `thie` (Manx), `chi` (Cornish), `ti` (Breton — marked "in progress"), sourced from `oideachais/samplaí/cognates.yaml`
- **AND** the right panel SHALL display an H3 hex map of the British Isles with each language community's geographic density, computed from the oideachais DLT geospatial sources

#### Scenario: 12-agent curriculum Q&A in EN/GA
- **WHEN** a visitor types "How is calculus introduced in Year 11?" in the Curaclam Trasteorann tab
- **THEN** 12 BAML agents (one per Celtic nation × per subject band: STEM, languages, arts, social) SHALL vote on the answer via the BAML `CompareCurricula` function from `tuatha/baml_src/celtic_curriculum.baml:188-214`
- **AND** the headlining number SHALL show the RAGAS agentic-vs-baseline delta (65.2% → 87.9% per `meaisínfhoghlaim/evaluation/ragas_pipeline.py:737-738`)
- **AND** each agent's response SHALL be labelled with its provenance jurisdiction (NCCA / SQA / WJEC / CCEA / DESC IoM / Cornwall / Breton)

### Requirement: Space 3 "Cianfhoghlaim" — Tuatha British Isles RPG Demo
The system SHALL publish a Gradio Space under `build-small-hackathon/cianfhoghlaim` that demonstrates the tuatha quadrant as a Hades-style RPG on a navigable British Isles map called **Tuatha**, with 6 NPCs drawn from 6 specific Wikipedia articles.

#### Scenario: Walk-the-Isles NPC chain
- **WHEN** a visitor opens the Space
- **THEN** a Babylon.js WebGPU scene SHALL load showing 7 nations (RoI, NI, Wales, Isle of Man, Scotland, Cornwall, English backdrop) with 4 diegetic mythology zones (Tuatha Dé Danann centred, Ulster, Fenian, Mabinogion)
- **AND** 6 NPCs SHALL be placed at fixed locations, each extracted from a specific Wikipedia source: Uí Liatháin lord (Loughcrew, `ga:Uí_Liatháin`), Brec/Óengus (Rathmore, `en:The_Expulsion_of_the_Déisi`), Manannán mac Lir (Isle of Man, `en:Manannán_mac_Lir`), Rhiannon (Dyfed, `en:Rhiannon`), Dian Cécht (Leinster, `en:Dian_Cecht`), Cian (Loughcrew, `en:Cian`)
- **AND** the BAML `GenerateNPCDialogue` from `tuatha/baml_src/mythology_extraction.baml:189-219` SHALL drive the level-gated dialogue trees

#### Scenario: Manannán's Ferryman's Trial
- **WHEN** the player approaches the Manannán mac Lir NPC and initiates the quest
- **THEN** 3 riddles SHALL be generated via the new BAML `EvaluateRiddleResponse` (modelled on `MarkingPoint` from `docs/03-agents/baml-extraction.md:462-469`)
- **AND** correct answers SHALL grant passage to the Isle of Man zone and mint a (local Anvil) Anam SBT via the CuchulainnNFT.sol 5-element system from `tuatha/apps/crypteolas_demo/anam-contracts/src/CuchulainnNFT.sol`

### Requirement: Space 4 "Anam: Tuatha na nGaelscoil" — Croílár 5-Element Connective-Tissue Demo
The system SHALL publish a Gradio Space under `build-small-hackathon/anam-tuatha-na-ngaelscoil` that demonstrates the croílár quadrant as the 5-element connective tissue integrating Spaces 1, 2, and 3, with 7 features (Tine / Uisce / Talamh / Aer / Anam / Mac Léinn / Fiosraigh) one per element.

#### Scenario: 5-element navigate
- **WHEN** a visitor opens the Space
- **THEN** a 5-tab Gradio Blocks SHALL render labelled Talamh, Uisce, Tine, Aer, Anam (with a 6th Mac Léinn tab spanning all elements and a 7th Fiosraigh tab for the classroom-to-MMO bridge)
- **AND** each tab's headline SHALL cite the corresponding element's symbol + School-subject mapping per `docs/bunchloch/tuatha/learn-to-earn-model.md:224-233`:
  - Talamh: "Lia Fáil" (Earth) → Geography, Agricultural Science, History
  - Uisce: "Cauldron of the Dagda" (Water) → Biology, Chemistry, Home Economics
  - Tine: "Spear of Lugh" (Fire) → Physics, Maths, Applied Maths
  - Aer: "Sword of Nuada" (Air) → English, Irish, Philosophy
  - Anam: "Anam" (Spirit) → meta-layer, all subjects

#### Scenario: Tine OCR-to-typed pipeline end-to-end
- **WHEN** a visitor uploads a scanned Leaving Cert exam paper (JPG/PNG/PDF) to the Tine tab
- **THEN** the 10-model OCR race from `meaisínfhoghlaim/ocr/model_registry.py:330-543` SHALL run in parallel via the `BAML_HACKATHON_PRIMARY` / `_FALLBACK_1` / `_FALLBACK_2` client chain (Qwen2.5-7B → Llama-3.1-8B → Gemma-2-9b-it)
- **AND** the `gaelic_metrics.py:195-242` evaluation (fada accuracy, tironian et recall, punctum delens precision) SHALL rank the models
- **AND** the winner's output SHALL flow into the BAML `ExtractPastPaper` from `oideachais/data_platform/baml_src/leaving_cert_past_paper_extraction.baml:30-54` to produce typed, searchable markdown
- **AND** the typed output SHALL be stored in the Space 1 ingestion queue for the An Scrúdú heatmap

