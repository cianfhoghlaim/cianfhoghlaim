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
) -> Quest {
  client CelticContentFallback
  prompt #"
    Generate an immersive language learning quest for the Tuath Celtic MMO.

    Learning Outcome: {{ learning_outcome.description }}
    Target Language: {{ language }}
    Game Zone: {{ zone }}
    Difficulty: {{ difficulty }}

    Create a quest that:
    - Teaches the learning outcome through gameplay
    - Uses authentic Celtic language appropriate to difficulty
    - Integrates with Celtic mythology and culture
    - Has 3-5 meaningful objectives
    - Provides graduated hints (4 levels)
    - Includes vocabulary and grammar notes

    For BEGINNER: Simple greetings, basic nouns
    For INTERMEDIATE: Sentences, verb conjugations
    For ADVANCED: Complex grammar, idioms, literature

    {{ ctx.output_format }}
  "#
}

// Generate mythology-based quest
function GenerateMythologyQuest(
  story: MythologicalStory,
  character: MythologicalCharacter?,
  language: CelticLanguage,
  difficulty: QuestDifficulty
) -> Quest {
  client Claude
  prompt #"
    Generate a mythology-based quest inspired by this Celtic story.

    Story: {{ story.title }}
    Summary: {{ story.summary }}
    Themes: {{ story.themes }}
    {% if character %}
    Character: {{ character.name }} - {{ character.description }}
    {% endif %}

    Target Language: {{ language }}
    Difficulty: {{ difficulty }}

    Create a quest that:
    - Retells or explores the mythological story
    - Teaches Celtic language through the narrative
    - Features authentic mythological characters
    - Connects to real Celtic learning outcomes
    - Creates an immersive experience

    {{ ctx.output_format }}
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
) -> NPC {
  client CelticContentFallback
  prompt #"
    Generate an NPC for the Tuath Celtic MMO.

    Game Zone: {{ zone }}
    Role: {{ role }}
    Primary Language: {{ language }}
    {% if mythological_inspiration %}
    Mythological Inspiration: {{ mythological_inspiration.name }}
    Character Type: {{ mythological_inspiration.character_type }}
    Traits: {{ mythological_inspiration.personality }}
    {% endif %}

    Create an NPC that:
    - Fits the Celtic cultural context of the zone
    - Speaks authentically in the target language
    - Can teach or guide players in language learning
    - Has memorable personality and appearance
    - Includes multiple greeting variations

    {{ ctx.output_format }}
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
) -> GameLocation {
  client Claude
  prompt #"
    Generate a game location for the Tuath Celtic MMO.

    Zone: {{ zone }}
    {% if real_world_basis %}Real World Basis: {{ real_world_basis }}{% endif %}
    {% if mythology_connection %}
    Mythology Connection: {{ mythology_connection.name }}
    Description: {{ mythology_connection.description }}
    Significance: {{ mythology_connection.significance }}
    {% endif %}
    Primary Language: {{ language }}

    Create a location that:
    - Authentically represents Celtic culture
    - Provides language learning opportunities
    - Has rich atmospheric description
    - Includes interactive features
    - Connects to mythology where appropriate

    {{ ctx.output_format }}
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
) -> GameItem {
  client FastExtraction
  prompt #"
    Generate a game item for the Tuath Celtic MMO.

    Item Type: {{ item_type }}
    Rarity: {{ rarity }}
    {% if mythology_inspiration %}Mythology Inspiration: {{ mythology_inspiration }}{% endif %}
    Language for names: {{ language }}

    Create an item with:
    - Authentic Celtic name and English equivalent
    - Lore connecting to Celtic mythology
    - Celtic inscription if appropriate
    - Stats fitting the rarity level

    {{ ctx.output_format }}
  "#
}
