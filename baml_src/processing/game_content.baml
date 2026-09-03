// Game Content Generation Schemas
// Generate quests, NPCs, and game world content for Tuath

enum QuestType {
  LANGUAGE_LEARNING @description("Vocabulary and grammar quests")
  CULTURAL_EXPLORATION @description("Visit locations, learn customs")
  MYTHOLOGY_DISCOVERY @description("Uncover legends and lore")
  CONVERSATION_PRACTICE @description("NPC dialogue practice")
  TRANSLATION_CHALLENGE @description("Translate text or speech")
  COLLECTION @description("Gather items with Celtic names")
}

enum QuestDifficulty {
  BEGINNER @description("Levels 1-5, basic vocabulary")
  ELEMENTARY @description("Levels 6-10, simple sentences")
  INTERMEDIATE @description("Levels 11-15, conversations")
  ADVANCED @description("Levels 16-20, complex grammar")
  MASTER @description("Levels 21+, fluent usage")
}

enum GameZoneType {
  TUTORIAL
  GAELTACHT
  GAIDHEALTACHD
  WELSH_SPEAKING
  MYTHOLOGICAL
  OTHERWORLD
}

class Quest {
  id string
  title string @description("Quest title in English")
  native_title string @description("Title in Celtic language")

  quest_type QuestType
  difficulty QuestDifficulty
  level_requirement int
  target_language CelticLanguage

  description string @description("Player-facing description")
  backstory string @description("Lore context")

  objectives QuestObjective[]
  rewards QuestReward[]
  learning_outcomes string[] @description("Educational goals")

  zone string @description("Game zone")
  npcs_involved string[]
  estimated_time_minutes int
}

class QuestObjective {
  id string
  description string
  objective_type string @description("talk, collect, translate, explore, etc.")

  celtic_content CelticContent? @description("Language learning content")
  hints QuestHint[]
  completion_criteria string
  xp_value int
}

class CelticContent {
  primary_text string @description("Celtic text to learn/use")
  translation string
  pronunciation string?
  grammar_note string?
  vocabulary string[] @description("New words introduced")
}

class QuestHint {
  level int @description("1=subtle, 4=explicit")
  hint_text string
  celtic_phrase string?
  translation string?
}

class QuestReward {
  reward_type string @description("xp, item, achievement, vocabulary")
  value int?
  item_name string?
  celtic_name string?
}

// Generate quest from curriculum
function GenerateLanguageQuest(
  learning_outcome: LearningOutcome,
  language: CelticLanguage,
  zone: string,
  difficulty: QuestDifficulty
) -> Quest {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured game content from a game design document.

    Source type: markdown game design document

    Extract:
    - game_title: the title of the game
    - mechanics: list of game mechanics with descriptions
    - levels: list of levels with difficulty + learning objectives
    - subject_focus: the canonical subject slug (chemistry, mathematics, etc.)
    - age_range: the target age range (e.g. '12-15')

    

    The game content is used by the Túatha educational MMO. The age_range + subject_focus drive the cohort matching.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Generate mythology-based quest
function GenerateMythologyQuest(
  story: MythologicalStory,
  character: MythologicalCharacter?,
  language: CelticLanguage,
  difficulty: QuestDifficulty
) -> Quest {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured game content from a game design document.

    Source type: markdown game design document

    Extract:
    - game_title: the title of the game
    - mechanics: list of game mechanics with descriptions
    - levels: list of levels with difficulty + learning objectives
    - subject_focus: the canonical subject slug (chemistry, mathematics, etc.)
    - age_range: the target age range (e.g. '12-15')

    

    The game content is used by the Túatha educational MMO. The age_range + subject_focus drive the cohort matching.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// NPC Generation
class NPC {
  id string
  name string
  native_name string @description("Name in Celtic language")

  character_type string @description("villager, scholar, warrior, druid, etc.")
  mythological_basis string? @description("If based on mythology")

  appearance string
  personality string[]
  voice_style string @description("How they speak")

  home_zone string
  languages string[] @description("Languages they speak")
  fluency_level string @description("native, fluent, learning")

  dialogue_topics string[]
  quests_given string[]
  teaching_specialty string? @description("What they can teach")

  greetings NPCGreeting[]
  idle_lines string[] @description("Ambient dialogue")
}

class NPCGreeting {
  celtic_text string
  english_translation string
  context string @description("When to use")
  tone string
}

function GenerateNPC(
  zone: string,
  role: string,
  language: CelticLanguage,
  mythological_inspiration: MythologicalCharacter?
) -> NPC {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured game content from a game design document.

    Source type: markdown game design document

    Extract:
    - game_title: the title of the game
    - mechanics: list of game mechanics with descriptions
    - levels: list of levels with difficulty + learning objectives
    - subject_focus: the canonical subject slug (chemistry, mathematics, etc.)
    - age_range: the target age range (e.g. '12-15')

    

    The game content is used by the Túatha educational MMO. The age_range + subject_focus drive the cohort matching.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// World Building
class GameLocation {
  id string
  name string
  native_name string

  zone_type GameZoneType
  parent_zone string?

  description string @description("Atmospheric description")
  history string @description("Lore background")

  languages_spoken CelticLanguage[]
  level_range int[] @description("[min, max] level")

  features LocationFeature[]
  npcs string[] @description("NPC IDs in location")
  quests_available string[]

  ambient_sounds string[]
  weather_patterns string[]
  time_of_day_effects string[]
}

class LocationFeature {
  name string
  native_name string
  feature_type string @description("landmark, shop, shrine, etc.")
  description string
  interaction string? @description("What players can do")
  educational_content string? @description("What players learn")
}

function GenerateGameLocation(
  zone: string,
  real_world_basis: string?,
  mythology_connection: MythologicalLocation?,
  language: CelticLanguage
) -> GameLocation {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured game content from a game design document.

    Source type: markdown game design document

    Extract:
    - game_title: the title of the game
    - mechanics: list of game mechanics with descriptions
    - levels: list of levels with difficulty + learning objectives
    - subject_focus: the canonical subject slug (chemistry, mathematics, etc.)
    - age_range: the target age range (e.g. '12-15')

    

    The game content is used by the Túatha educational MMO. The age_range + subject_focus drive the cohort matching.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Item Generation
class GameItem {
  id string
  name string
  native_name string

  item_type string @description("weapon, armor, consumable, quest_item, etc.")
  rarity string @description("common, uncommon, rare, legendary, mythic")

  description string
  lore string @description("Item backstory")
  mythological_connection string?

  celtic_inscription string? @description("Text on item")
  inscription_translation string?

  stats map<string, int>?
  abilities string[]
  quest_required string?
}

function GenerateGameItem(
  item_type: string,
  rarity: string,
  mythology_inspiration: string?,
  language: CelticLanguage
) -> GameItem {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured game content from a game design document.

    Source type: markdown game design document

    Extract:
    - game_title: the title of the game
    - mechanics: list of game mechanics with descriptions
    - levels: list of levels with difficulty + learning objectives
    - subject_focus: the canonical subject slug (chemistry, mathematics, etc.)
    - age_range: the target age range (e.g. '12-15')

    

    The game content is used by the Túatha educational MMO. The age_range + subject_focus drive the cohort matching.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
