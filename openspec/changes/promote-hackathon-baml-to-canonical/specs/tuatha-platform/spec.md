## ADDED Requirements

### Requirement: Cross-nation Celtic curriculum comparison

The tuatha quadrant MUST provide a `CompareCelticNations` BAML function (in `tuatha/baml_src/celtic_curriculum.baml`) that returns a `CrossNationComparison` (with `CurriculumMapping` per nation) for a given topic across the 5 Celtic-nation curricula (IE, NI, WLS, IM, SCT). The function MUST use the canonical `LitellmClient`.

#### Scenario: Agent compares atomic structure across nations

- **WHEN** an agent has a topic query (e.g. "atomic structure") and calls `CompareCelticNations(topic_query=..., scope=["IE", "NI", "WLS", "IM", "SCT"])`
- **THEN** the function returns a `CrossNationComparison` with one `CurriculumMapping` per nation, a `shared_year_levels` list, and a `notes` string

### Requirement: Bilingual EN+GA formative exit cards

The tuatha quadrant MUST provide a `GenerateExitCardQuestions` BAML function (in `tuatha/baml_src/player_assessment.baml`) that returns a bilingual (EN + Gaeilge) `ExitCardSet` (with `ExitCardQuestion[]`) for a 3-minute end-of-lesson check for understanding. The function MUST use the canonical `LitellmClient`.

#### Scenario: Agent generates 6 exit-card questions

- **WHEN** an agent calls `GenerateExitCardQuestions(lesson_topic=..., subject=..., level=..., num_questions=6, curriculum_extract=...)`
- **THEN** the function returns a 6-question `ExitCardSet` with mixed question types (multiple_choice, short_answer, numeric), bilingual prompts + explanations, and a balanced Bloom distribution
- **AND** each question has a `marking_point_ref` linking back to a topic_code from the supplied `CircularExtraction`

### Requirement: NPC dialogue generation for the Cianfhoghlaim RPG

The tuatha quadrant MUST provide a `GenerateNpcDialogue` BAML function (in `tuatha/baml_src/mythology_extraction.baml`) that returns an `NpcDialogueExchange` (with `NpcDialogue`) for one of the 6 Celtic NPCs in the Cianfhoghlaim RPG. The function MUST use the canonical `LitellmClient`.

#### Scenario: Agent role-plays an NPC

- **WHEN** an agent has an NPC name, title, nation_code, era, the player's utterance, the conversation history, and the cached Wikipedia source
- **THEN** the function returns an `NpcDialogueExchange` with `utterance_en`, `utterance_ga`, scholarly footnotes, an `emotional_tone`, an `asks_player_about` prompt, and (optionally) a `quest_offered` and `artifact_granted`
- **AND** the response stays in character, is grounded in the source material, mixes in 1 Irish phrase per 3 turns, and is under 3 sentences per turn
