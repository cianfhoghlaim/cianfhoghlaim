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
function ExtractMythologicalCharacter(
  text: string,
  tradition: CelticTradition
) -> MythologicalCharacter {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#

}

// Extract story structure
function ExtractMythologicalStory(
  text: string
) -> MythologicalStory {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#

}

// Extract location lore
function ExtractMythologicalLocation(
  text: string,
  tradition: CelticTradition
) -> MythologicalLocation {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
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
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
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

function ExtractFolkloreElements(
  text: string
) -> FolkloreElement[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

// ============================================================================
// NPC dialogue generation for the Cianfhoghlaim RPG
// Promoted from spaces/_common/baml/hackathon_schemas.baml (2026-06-24).
// Used by:
//   - spaces/cianfhoghlaim/dialogue.py (the Cianfhoghlaim RPG Space)
//   - tuatha/agents/agno/npc_dialogue_team.py (the 4-agent formative team)
// ============================================================================

class NpcDialogue {
  speaker string
  nation_code string  // "IE" | "NI" | "WLS" | "IM" | "SCT" | "universal"
  era string  // e.g. "Iron Age", "Early Medieval", "Fictional"
  utterance_en string
  utterance_ga string
  scholarly_footnote_en string
  scholarly_footnote_ga string
  emotional_tone string  // "wry" | "wounded" | "curious" | "defiant" | "gentle"
  asks_player_about string  // prompt for the player's next turn
}

class NpcDialogueExchange {
  npc_name string
  npc_title string
  turn_index int
  dialogue NpcDialogue
  quest_offered string?
  artifact_granted string?
}

function GenerateNpcDialogue(
  npc_name: string,
  npc_title: string,
  nation_code: string,
  era: string,
  player_utterance: string,
  conversation_history: string,
  // formatted as "Speaker: text"
  scholarly_source: string
) -> NpcDialogueExchange {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
