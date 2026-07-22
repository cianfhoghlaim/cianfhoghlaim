// Tearma.ie - National Terminology Database for Irish
// BAML schema for structured extraction from Tearma API responses
// https://www.tearma.ie - Bilingual English-Irish terminology
// December 2024

// ============================================================================
// TERMINOLOGY DOMAIN ENUMS
// ============================================================================

// Subject domains/areas covered by Tearma.ie
enum TerminologyDomain {
  LAW @alias("Law - Dlí")
  MED @alias("Medicine - Leigheas")
  IT @alias("Information Technology - Teicneolaíocht Faisnéise")
  EDU @alias("Education - Oideachas")
  ENV @alias("Environment - Comhshaol")
  FIN @alias("Finance - Airgeadas")
  SCI @alias("Science - Eolaíocht")
  BIO @alias("Biology - Bitheolaíocht")
  CHEM @alias("Chemistry - Ceimic")
  PHYS @alias("Physics - Fisic")
  MATH @alias("Mathematics - Matamaitic")
  ENG @alias("Engineering - Innealtóireacht")
  ARCH @alias("Architecture - Ailtireacht")
  ART @alias("Art - Ealaín")
  MUS @alias("Music - Ceol")
  LIT @alias("Literature - Litríocht")
  HIST @alias("History - Stair")
  GEO @alias("Geography - Tíreolaíocht")
  LING @alias("Linguistics - Teangeolaíocht")
  POL @alias("Politics - Polaitíocht")
  ECON @alias("Economics - Eacnamaíocht")
  SOC @alias("Sociology - Socheolaíocht")
  PSYCH @alias("Psychology - Síceolaíocht")
  ADMIN @alias("Public Administration - Riarachán Poiblí")
  AGRI @alias("Agriculture - Talmhaíocht")
  SPORT @alias("Sport - Spórt")
  TRANS @alias("Transport - Iompar")
  CONSTR @alias("Construction - Tógáil")
  COMM @alias("Commerce - Tráchtáil")
  MIL @alias("Military - Míleata")
  RELIG @alias("Religion - Reiligiún")
  GEN @alias("General - Ginearálta")
}

// Irish noun gender
enum IrishGender {
  M @alias("Masculine - Firinscneach")
  F @alias("Feminine - Baininscneach")
}

// Irish noun declension class
enum IrishDeclension {
  D1 @alias("First Declension - An Chéad Díochlaonadh")
  D2 @alias("Second Declension - An Dara Díochlaonadh")
  D3 @alias("Third Declension - An Tríú Díochlaonadh")
  D4 @alias("Fourth Declension - An Ceathrú Díochlaonadh")
  D5 @alias("Fifth Declension - An Cúigiú Díochlaonadh")
  IRR @alias("Irregular - Neamhrialta")
}

// Part of speech
enum PartOfSpeech {
  NOUN @alias("Noun - Ainmfhocal")
  VERB @alias("Verb - Briathar")
  ADJ @alias("Adjective - Aidiacht")
  ADV @alias("Adverb - Dobhriathar")
  PREP @alias("Preposition - Réamhfhocal")
  CONJ @alias("Conjunction - Cónasc")
  PRON @alias("Pronoun - Forainm")
  ART @alias("Article - Alt")
  INTERJ @alias("Interjection - Intriacht")
  PHRASE @alias("Phrase - Frása")
  ABBR @alias("Abbreviation - Giorrúchán")
}

// Term status in Tearma
enum TermStatus {
  APPROVED @alias("Approved - Ceadaithe")
  PENDING @alias("Pending review - Ar feitheamh")
  DEPRECATED @alias("Deprecated - Seanchéasta")
  PROPOSED @alias("Proposed - Molta")
}

// Source/authority for terminology
enum TerminologySource {
  COGG @alias("An Coiste Téarmaíochta - Terminology Committee")
  FIONTAR @alias("Fiontar & Scoil na Gaeilge DCU")
  IATE @alias("IATE - EU terminology database")
  FGB @alias("Foclóir Gaeilge-Béarla - Ó Dónaill")
  EID @alias("English-Irish Dictionary - de Bhaldraithe")
  DINEEN @alias("Foclóir Gaedhilge agus Béarla - Dinneen")
  NCCA @alias("National Council for Curriculum and Assessment")
  CUSTOM @alias("User-submitted - Úsáideoir")
}

// ============================================================================
// CORE TERMINOLOGY STRUCTURES
// ============================================================================

// Irish grammatical information for a noun
class IrishNounGrammar {
  gender IrishGender @description("Noun gender: masculine or feminine")
  declension IrishDeclension? @description("Declension class (1-5 or irregular)")
  genitive_singular string? @description("Genitive singular form (tuiseal ginideach uatha)")
  nominative_plural string? @description("Nominative plural form (tuiseal ainmneach iolra)")
  genitive_plural string? @description("Genitive plural form (tuiseal ginideach iolra)")
  verbal_noun bool @description("Whether this is a verbal noun (ainm briathartha)")
}

// Irish grammatical information for a verb
class IrishVerbGrammar {
  verbal_noun string? @description("Verbal noun form (ainm briathartha)")
  verbal_adjective string? @description("Verbal adjective form (aidiacht bhriathartha)")
  conjugation int? @description("Verb conjugation class (1 or 2)")
  irregular bool @description("Whether the verb is irregular")
  autonomous_form string? @description("Autonomous/impersonal form (an fhoirm shaorbhriathartha)")
}

// Irish grammatical information for an adjective
class IrishAdjectiveGrammar {
  comparative string? @description("Comparative form (breischéim)")
  superlative string? @description("Superlative form (sárchéim)")
  genitive_singular_masc string? @description("Genitive singular with masculine noun")
  genitive_singular_fem string? @description("Genitive singular with feminine noun")
  plural string? @description("Plural form")
}

// Combined grammar information
class IrishGrammar {
  part_of_speech PartOfSpeech @description("Part of speech")
  noun_grammar IrishNounGrammar? @description("Noun-specific grammar if applicable")
  verb_grammar IrishVerbGrammar? @description("Verb-specific grammar if applicable")
  adjective_grammar IrishAdjectiveGrammar? @description("Adjective-specific grammar if applicable")
  notes string? @description("Additional grammatical notes")
  @@stream.done
}

// Term in a single language
class TermText {
  text string @description("The term text")
  language string @description("Language code: ga (Irish) or en (English)")
  is_preferred bool @description("Whether this is the preferred/recommended term")
  variants string[]? @description("Alternative forms or spellings")
  abbreviation string? @description("Standard abbreviation if any")
  pronunciation string? @description("IPA pronunciation guide")
}

// Usage example showing term in context
class UsageExample {
  text_ga string @description("Example sentence in Irish")
  text_en string @description("Example sentence in English")
  source string? @description("Source of the example")
  domain TerminologyDomain? @description("Domain context for the example")
}

// Definition of a term
class TermDefinition {
  text string @description("Definition text")
  language string @description("Language of definition: ga or en")
  source TerminologySource? @description("Source of definition")
}

// Cross-reference to related term
class TermRelation {
  related_term_id int @description("ID of related term")
  relation_type string @description("Relationship type: synonym, antonym, broader, narrower, related")
  term_text string? @description("The related term text for reference")
}

// ============================================================================
// MAIN TERM RECORD
// ============================================================================

// Full terminology record from Tearma.ie
class TearmaTerm {
  // Identification
  id int @description("Unique term identifier in Tearma database")
  
  // Terms in both languages
  term_ga TermText @description("Irish term")
  term_en TermText @description("English term")
  
  // Grammar (primarily for Irish)
  grammar IrishGrammar? @description("Grammatical information for Irish term")
  
  // Classification
  domains TerminologyDomain[] @description("Subject domains this term belongs to")
  status TermStatus @description("Approval status of the term")
  
  // Definitions
  definition_ga TermDefinition? @description("Definition in Irish")
  definition_en TermDefinition? @description("Definition in English")
  
  // Usage and context
  examples UsageExample[]? @description("Usage examples in context")
  context_notes string? @description("Notes on usage context or register")
  
  // Related terms
  synonyms TermRelation[]? @description("Synonymous terms")
  antonyms TermRelation[]? @description("Antonymous terms")
  broader_terms TermRelation[]? @description("Broader/hypernym terms")
  narrower_terms TermRelation[]? @description("Narrower/hyponym terms")
  related_terms TermRelation[]? @description("Other related terms")
  
  // Source and authority
  source TerminologySource @description("Primary source/authority")
  source_reference string? @description("Specific reference (e.g., page number)")
  
  // Metadata
  created_at string? @description("ISO datetime when term was added")
  modified_at string? @description("ISO datetime when term was last modified")
  approved_by string? @description("Authority that approved the term")
}

// Search result from Tearma API
class TearmaSearchResult {
  terms TearmaTerm[] @description("Terms matching the search query")
  total_count int @description("Total number of matching terms")
  page int @description("Current page number")
  per_page int @description("Results per page")
  has_more bool @description("Whether more pages are available")
  query string @description("Original search query")
  search_language string @description("Language searched: ga, en, or both")
}

// Domain-specific term list
class TearmaDomainTerms {
  domain TerminologyDomain @description("The domain")
  domain_name_ga string @description("Domain name in Irish")
  domain_name_en string @description("Domain name in English")
  term_count int @description("Number of terms in this domain")
  terms TearmaTerm[] @description("Terms in this domain")
  @@stream.done
}

// ============================================================================
// SPECIALIZED STRUCTURES
// ============================================================================

// Educational term (subset for NCCA curriculum)
class EducationalTerm {
  term_id int @description("Tearma ID")
  term_ga string @description("Irish term")
  term_en string @description("English term")
  subject string @description("School subject this term relates to")
  level string? @description("Education level: primary, junior_cycle, senior_cycle")
  curriculum_code string? @description("NCCA curriculum reference code")
  definition_ga string? @description("Short definition in Irish")
  definition_en string? @description("Short definition in English")
  @@stream.done
}

// Legal term (subset for law domain)
class LegalTerm {
  term_id int @description("Tearma ID")
  term_ga string @description("Irish legal term")
  term_en string @description("English legal term")
  legal_area string? @description("Area of law: constitutional, criminal, civil, etc.")
  legislation_reference string? @description("Reference to relevant legislation")
  definition string @description("Legal definition")
  notes string? @description("Usage notes for legal context")
}

// IT/Computing term
class ITTerm {
  term_id int @description("Tearma ID")
  term_ga string @description("Irish IT term")
  term_en string @description("English IT term")
  category string? @description("IT category: hardware, software, networking, etc.")
  definition string @description("Technical definition")
  microsoft_term bool @description("Whether aligned with Microsoft terminology")
  apple_term bool @description("Whether aligned with Apple terminology")
}

// ============================================================================
// EXTRACTION FUNCTIONS
// ============================================================================

// Parse Tearma API JSON response for a single term
function ParseTearmaTerm(
  json_response: string
) -> TearmaTerm {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Parse Tearma search results
function ParseTearmaSearchResults(
  json_response: string
) -> TearmaSearchResult {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Extract domain-specific terminology
function ExtractDomainTerminology(
  json_response: string,
  target_domain: TerminologyDomain
) -> TearmaDomainTerms {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Extract educational terminology for curriculum alignment
function ExtractEducationalTerms(
  json_response: string,
  subject: string,
  level: string
) -> EducationalTerm[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Extract Irish grammar information from term
function ExtractIrishGrammar(
  term_text: string,
  context: string
) -> IrishGrammar {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Generate bilingual term card for vocabulary learning
function GenerateTermCard(
  term: TearmaTerm
) -> string {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Link term to Logainm placenames (for geographic terminology)
function LinkTermToPlacenames(
  term: TearmaTerm,
  placename_contexts: string[]
) -> int[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Translate term between English and Irish with full context
function TranslateTerm(
  source_text: string,
  source_language: string,
  domain_context: TerminologyDomain?
) -> TearmaTerm {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// ============================================================================
// INTEGRATION WITH OTHER GAOIS RESOURCES
// ============================================================================

// Link Tearma term to Dúchas folklore references
class TearmaFolkloreLink {
  term_id int @description("Tearma term ID")
  term_ga string @description("Irish term")
  term_en string @description("English term")
  duchas_references DuchasFolkloreReference[] @description("Folklore collection references")
}

// Reference to folklore material using the term
class DuchasFolkloreReference {
  collection string @description("CBÉS, CBÉ, CBÉG, or CBÉD")
  volume_id int? @description("Volume ID if applicable")
  item_id int? @description("Item ID if applicable")
  context string @description("Context in which term appears")
  historical_form string? @description("Historical/dialectal form of the term")
}

// Find folklore uses of a term
function FindFolkloreUsage(
  term: TearmaTerm,
  duchas_search_results: string
) -> TearmaFolkloreLink {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Combined lookup across Tearma and Logainm
class BilingualPlaceTerm {
  tearma_id int? @description("Tearma ID if term exists")
  logainm_glossary_id int? @description("Logainm glossary ID if a placename element")
  term_ga string @description("Irish term/element")
  term_en string @description("English meaning")
  is_placename_element bool @description("Whether commonly found in placenames")
  example_places string[]? @description("Example placenames using this element")
  definition string? @description("Combined definition")
}

// Cross-reference term with placename elements
function CrossReferencePlacenameElement(
  term_text: string,
  tearma_data: string,
  logainm_glossary: string
) -> BilingualPlaceTerm {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
