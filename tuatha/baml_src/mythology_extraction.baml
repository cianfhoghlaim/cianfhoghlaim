// Mythology Extraction Schemas
// Extract structured data from Celtic mythology and folklore sources

enum CelticTradition {
  IRISH
  WELSH
  SCOTTISH
  MANX
  BRETON
  CORNISH
  PAN_CELTIC
}

enum MythologicalCycle {
  TUATHA_DE_DANANN @description("Irish divine race")
  FIANNA @description("Irish warrior band")
  ULSTER @description("Ulster Cycle, Cú Chulainn")
  KINGS @description("Irish historical kings")
  MABINOGION @description("Welsh Four Branches")
  ARTHURIAN @description("King Arthur legends")
  FOLK @description("Folk tales and legends")
}

enum CharacterType {
  DEITY
  HERO
  MORTAL
  CREATURE
  DRUID
  BARD
  KING
  QUEEN
  WARRIOR
  GIANT
  FAIRY
}

class MythologicalCharacter {
  name string @description("Primary name")
  native_names NameVariant[] @description("Names in Celtic languages")
  aliases string[] @description("Other known names")
  character_type CharacterType
  tradition CelticTradition
  cycle MythologicalCycle?

  titles string[] @description("Epithets and titles")
  description string @description("Character summary")
  personality string[] @description("Key traits")
  abilities string[] @description("Powers and skills")

  relationships CharacterRelationship[]
  key_stories string[] @description("Stories featuring this character")
  symbols string[] @description("Associated symbols")
  sacred_items string[] @description("Magical items")

  modern_relevance string? @description("Contemporary significance")
  game_role string? @description("Role in Tuath game")
}

class NameVariant {
  language CelticLanguage
  name string
  pronunciation string?
  meaning string?
}

class CharacterRelationship {
  related_character string @description("Name of related character")
  relationship_type string @description("parent, child, spouse, rival, etc.")
  story_context string? @description("How they relate in stories")
}

class MythologicalLocation {
  name string
  native_names NameVariant[]
  tradition CelticTradition
  location_type string @description("realm, fortress, lake, mountain, etc.")

  description string
  significance string @description("Why this place matters")
  associated_characters string[]
  key_events string[]

  real_world_location string? @description("Modern location if known")
  game_zone string? @description("Zone in Tuath game")
}

class MythologicalStory {
  title string
  native_title string?
  tradition CelticTradition
  cycle MythologicalCycle

  summary string @description("Brief plot summary")
  themes string[] @description("Major themes")
  moral string? @description("Lesson or message")

  main_characters string[]
  locations string[]
  key_events StoryEvent[]

  source_texts string[] @description("Original manuscript sources")
  educational_value string @description("Learning opportunities")
}

class StoryEvent {
  description string
  characters_involved string[]
  location string?
  significance string
  celtic_terms CelticTerm[]
}

class CelticTerm {
  term string @description("Word in Celtic language")
  language CelticLanguage
  translation string
  context string @description("How used in story")
}

// Extract character from mythology text
function ExtractMythologicalCharacter(text: string, tradition: CelticTradition) -> MythologicalCharacter {
  client CelticContentFallback
  prompt #"
    Extract a detailed mythological character profile from this Celtic text.

    Tradition: {{ tradition }}

    Text:
    {{ text }}

    Capture all names, relationships, and story appearances.
    Include Celtic language terms with accurate spelling.

    {{ ctx.output_format }}
  "#
}

// Extract story structure
function ExtractMythologicalStory(text: string) -> MythologicalStory {
  client Claude
  prompt #"
    Extract the structure and content of this Celtic mythological story.

    Text:
    {{ text }}

    Identify the tradition, cycle, key characters, and themes.
    Note Celtic terms and their meanings.
    Assess educational value for language learners.

    {{ ctx.output_format }}
  "#
}

// Extract location lore
function ExtractMythologicalLocation(text: string, tradition: CelticTradition) -> MythologicalLocation {
  client FastExtraction
  prompt #"
    Extract mythological location information from this Celtic text.

    Tradition: {{ tradition }}

    Text:
    {{ text }}

    Identify names in Celtic languages, significance, and associated stories.

    {{ ctx.output_format }}
  "#
}

// Generate NPC dialogue from character
class NPCDialogue {
  character_name string
  context string @description("Situation in game")
  dialogue_lines DialogueLine[]
  teaching_moment string? @description("Educational opportunity")
}

class DialogueLine {
  speaker string
  celtic_text string @description("Dialogue in Celtic language")
  english_translation string
  tone string @description("friendly, mysterious, warning, etc.")
  gesture string? @description("Character action")
}

function GenerateNPCDialogue(
  character: MythologicalCharacter,
  context: string,
  player_level: int,
  target_language: CelticLanguage
) -> NPCDialogue {
  client CelticContentFallback
  prompt #"
    Generate immersive NPC dialogue for this Celtic mythological character.

    Character: {{ character.name }}
    Character Type: {{ character.character_type }}
    Tradition: {{ character.tradition }}
    Key Traits: {{ character.personality }}

    Game Context: {{ context }}
    Player Level: {{ player_level }}
    Target Language: {{ target_language }}

    Create authentic dialogue that:
    - Reflects the character's mythology and personality
    - Uses appropriate Celtic language for the player's level
    - Includes educational language learning moments
    - Maintains immersive storytelling

    For lower levels (1-5), use simple phrases with translations.
    For higher levels (15+), use more complex language with less translation.

    {{ ctx.output_format }}
  "#
}

// Extract folklore for NPC behavior
class FolkloreElement {
  name string
  tradition CelticTradition
  element_type string @description("superstition, custom, belief, etc.")
  description string
  celtic_term string?
  game_application string @description("How to use in game")
}

function ExtractFolkloreElements(text: string) -> FolkloreElement[] {
  client FastExtraction
  prompt #"
    Extract folklore elements from this Celtic text that could enhance game immersion.

    Text:
    {{ text }}

    Identify customs, superstitions, beliefs, and traditions.
    Suggest how each could be incorporated into the game.

    {{ ctx.output_format }}
  "#
}
