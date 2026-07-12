// BAML schema: Gemini Corpus Topic Profile Extraction
//
// Used for the non-legal/medical Gemini corpora (politics, culture,
// technology, other). Each corpus has a profile class with corpus-
// specific fields, but the 4 shared classes below are reused across
// the 4 corpora.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

enum PoliticalTopic {
  GOVERNANCE
  ELECTIONS
  POLICY
  PARTIES
  INTERNATIONAL_RELATIONS
  JUDICIAL
  ACTIVISM
  OTHER
}

class PoliticalTopicProfile {
  document_id string
  topic PoliticalTopic
  jurisdiction string
  key_entities string[]               @description("parties, politicians, organisations")
  policy_positions string[]
  timeline_events TimelineEvent[]
  source_pdf string
}

enum CultureTopic {
  HERITAGE
  LANGUAGE
  ARTS
  LITERATURE
  MUSIC
  GAELIC_CULTURE
  INDIGENOUS_RIGHTS
  OTHER
}

class CultureTopicProfile {
  document_id string
  topic CultureTopic
  key_figures string[]
  cultural_entities string[]
  timeline_events TimelineEvent[]
  source_pdf string
}

enum TechTopic {
  AI_ML
  DATA_PRIVACY
  CYBERSECURITY
  SOFTWARE
  HARDWARE
  STANDARDS
  REGULATION
  OTHER
}

class TechTopicProfile {
  document_id string
  topic TechTopic
  technical_entities string[]         @description("frameworks, libraries, protocols")
  standards_referenced string[]
  timeline_events TimelineEvent[]
  source_pdf string
}
