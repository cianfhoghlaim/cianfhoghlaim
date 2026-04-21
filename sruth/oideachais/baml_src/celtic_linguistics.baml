// Celtic Linguistics - Core Enums and Classes
// Type-safe linguistic extraction for Celtic languages
// December 2024

// ============================================================================
// LANGUAGE ENUMS
// ============================================================================

// Celtic and related languages
enum CelticLanguage {
  GA @alias("Irish (Modern)")
  GD @alias("Scottish Gaelic")
  CY @alias("Welsh")
  BR @alias("Breton")
  GV @alias("Manx")
  KW @alias("Cornish")
  SGA @alias("Old Irish")
  MGA @alias("Middle Irish")
  OW @alias("Old Welsh")
  EN @alias("English")
}

// Language family branches
enum CelticBranch {
  GOIDELIC @alias("Goidelic (Irish, Scottish Gaelic, Manx)")
  BRYTHONIC @alias("Brythonic (Welsh, Breton, Cornish)")
  PROTO_CELTIC @alias("Proto-Celtic (reconstructed)")
}

// Irish dialect regions
enum IrishDialect {
  MUNSTER @alias("Gaeilge na Mumhan - Kerry, Cork, Waterford")
  CONNACHT @alias("Gaeilge Chonnacht - Galway, Mayo, Roscommon")
  ULSTER @alias("Gaeilge Uladh - Donegal")
  STANDARD @alias("An Caighdeán Oifigiúil")
}

// ============================================================================
// PARTS OF SPEECH
// ============================================================================

// Universal POS tags with Celtic-specific annotations
enum PartOfSpeech {
  NOUN @alias("Noun - Ainmfhocal")
  VERB @alias("Verb - Briathar")
  ADJ @alias("Adjective - Aidiacht")
  ADV @alias("Adverb - Dobhriathar")
  ADP @alias("Adposition (Preposition) - Réamhfhocal")
  DET @alias("Determiner (Article) - Alt")
  PRON @alias("Pronoun - Forainm")
  CCONJ @alias("Coordinating Conjunction - Cónasc comhordaithe")
  SCONJ @alias("Subordinating Conjunction - Cónasc fo-ordaithe")
  PART @alias("Particle - Mír")
  INTJ @alias("Interjection - Intriacht")
  NUM @alias("Numeral - Uimhir")
  PROPN @alias("Proper Noun - Ainm dilis")
  PUNCT @alias("Punctuation")
  SYM @alias("Symbol")
  X @alias("Other")
}

// ============================================================================
// GRAMMATICAL FEATURES
// ============================================================================

// Grammatical gender
enum GrammaticalGender {
  MASC @alias("Masculine - Firinscneach")
  FEM @alias("Feminine - Baininscneach")
  NEUT @alias("Neuter (historical)")
}

// Grammatical case
enum GrammaticalCase {
  NOM @alias("Nominative - Ainmneach")
  GEN @alias("Genitive - Ginideach")
  DAT @alias("Dative - Tabharthach (archaic)")
  VOC @alias("Vocative - Gairmeach")
  ACC @alias("Accusative (historical)")
}

// Grammatical number
enum GrammaticalNumber {
  SING @alias("Singular - Uatha")
  PLUR @alias("Plural - Iolra")
  DUAL @alias("Dual (historical)")
}

// Verb tense
enum VerbTense {
  PRES @alias("Present - Aimsir Láithreach")
  PAST @alias("Past - Aimsir Chaite")
  FUT @alias("Future - Aimsir Fháistineach")
  COND @alias("Conditional - Modh Coinníollach")
  HAB @alias("Past Habitual - Aimsir Ghnáthchaite")
}

// Verb mood
enum VerbMood {
  IND @alias("Indicative - Modh Táscach")
  SUB @alias("Subjunctive - Modh Foshuiteach")
  IMP @alias("Imperative - Modh Ordaitheach")
}

// ============================================================================
// INITIAL MUTATIONS
// ============================================================================

// Celtic initial mutation types
enum MutationType {
  // Irish mutations
  LEN @alias("Lenition (Séimhiú)")
  ECL @alias("Eclipsis (Urú)")
  HPREF @alias("H-prothesis (h-prefix)")
  TPREF @alias("T-prefix")

  // Welsh mutations
  SOFT @alias("Soft Mutation (Treiglad Meddal)")
  NASAL @alias("Nasal Mutation (Treiglad Trwynol)")
  ASP @alias("Aspirate Mutation (Treiglad Llaes)")

  NONE @alias("No mutation")
}

// Initial mutation details
class InitialMutation {
  type MutationType @description("Type of mutation applied")
  original_initial string @description("Original initial consonant/vowel")
  mutated_form string @description("Form after mutation")
  trigger string? @description("What triggered the mutation")
  language CelticLanguage @description("Language context")
}

// ============================================================================
// MORPHOLOGICAL FEATURES
// ============================================================================

// Complete morphological feature bundle
class MorphologicalFeatures {
  gender GrammaticalGender? @description("Grammatical gender")
  number GrammaticalNumber? @description("Singular/plural")
  case_ GrammaticalCase? @alias("case") @description("Grammatical case")
  person int? @description("1st, 2nd, or 3rd person")
  tense VerbTense? @description("Verb tense")
  mood VerbMood? @description("Verb mood")
  voice string? @description("Active, Passive, Autonomous")
  aspect string? @description("Perfective, Imperfective")
  polarity string? @description("Positive or Negative")
  mutation MutationType? @description("Initial mutation if any")
}

// ============================================================================
// LINGUISTIC TOKEN
// ============================================================================

// A fully annotated linguistic token
class LinguisticToken {
  surface_form string @description("Word as it appears in text")
  lemma string @description("Dictionary form / base form")
  language CelticLanguage @description("Language of the token")
  pos PartOfSpeech @description("Part of speech tag")
  features MorphologicalFeatures? @description("Morphological features")
  mutation InitialMutation? @description("Initial mutation if present")
  gloss string? @description("English translation/gloss")
}

// ============================================================================
// EXTRACTION FUNCTIONS
// ============================================================================

// Extract morphological features from a Celtic word in context
function ExtractMorphology(
  word string @description("The word to analyze"),
  context string @description("Sentence or phrase containing the word"),
  language CelticLanguage @description("Celtic language of the word")
) -> LinguisticToken {
  client Claude
  prompt #"
    Analyze the following Celtic word and extract its morphological features.

    Word: {{ word }}
    Context: {{ context }}
    Language: {{ language }}

    Provide:
    1. The lemma (dictionary form)
    2. Part of speech
    3. Grammatical features (gender, number, case, etc.)
    4. Any initial mutation present
    5. English gloss

    {{ ctx.output_format }}
  "#
}

// Analyze a complete sentence for linguistic annotation
function AnalyzeSentence(
  sentence string @description("Celtic language sentence"),
  language CelticLanguage @description("Language of the sentence")
) -> LinguisticToken[] {
  client Claude
  prompt #"
    Analyze this {{ language }} sentence and annotate each token.

    Sentence: {{ sentence }}

    For each word, provide:
    - Surface form (as written)
    - Lemma (dictionary form)
    - Part of speech
    - Morphological features
    - Initial mutation if any

    Note Celtic-specific features like:
    - Initial mutations (lenition, eclipsis, etc.)
    - Synthetic verb forms with fused pronouns
    - Case marking on nouns

    {{ ctx.output_format }}
  "#
}

// Identify the dialect of Irish text
function IdentifyDialect(
  text string @description("Irish language text sample")
) -> IrishDialect {
  client ClaudeHaiku
  prompt #"
    Analyze this Irish text and identify which dialect it represents.

    Text: {{ text }}

    Look for dialect markers like:
    - Munster: 'do' for past tense, '-ínn' verbal noun endings
    - Connacht: 'a' for verbal nouns, different vowel quality
    - Ulster: 'chan' for negation, 'cha/chan' patterns
    - Standard: Official spelling and grammar

    {{ ctx.output_format }}
  "#
}
