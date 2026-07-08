// BAML schema: Cross-subject Topic Extraction (BIEP v1 — the cross-subject
// competency backbone)
//
// Used by the LC6 Dagster assets to extract the canonical
// cross-subject topic key from each BAML SyllabusDocument. The
// resulting CrossSubjectTopic rows are the input to:
//   - the 7 v1 CocoIndex Apps (one per subject + government_circulars)
//   - the cross_subject_competency LanceDB table
//   - the 4 MotherDuck Dives (topic_frequency_per_year_per_subject, etc.)
//
// Per openspec/changes/2026-07-06-british-isles-education-pipeline-v1/ and
// the canonical spec at openspec/specs/british-isles-education-pipeline/spec.md.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

// ============================================================================
// Enums
// ============================================================================

enum SubjectArea {
  MATHEMATICS
  CHEMISTRY
  GEOGRAPHY
  GAEILGE
  ENGLISH
  COMPUTER_SCIENCE
  CROSS_SUBJECT
  GENERAL
}

// 6 NCCA Key Competencies (the Brown Ajah theming backbone — see
// `docs/BROWN_AJAH_THEMING.md` for the 3 Trí Dé Dána mappings).
enum NCCAKeyCompetency {
  INFORMATION_PROCESSING
  COMMUNICATING
  WORKING_WITH_OTHERS
  PERSONAL_EFFECTIVENESS
  CRITICAL_CREATIVE_THINKING
}

// 4 LC levels + JC placeholder
enum LCLevel {
  JC       @description("Junior Cycle")
  LC_FDN   @description("Leaving Certificate Foundation Level")
  LC_OL    @description("Leaving Certificate Ordinary Level")
  LC_HL    @description("Leaving Certificate Higher Level")
}

// ============================================================================
// Core value types
// ============================================================================

class CrossSubjectTopic {
  // The canonical topic key (deterministic; e.g. "MATH-ALGEBRA-LC_HL-2026")
  topic_id: string
  subject: SubjectArea
  topic_label_en: string
  topic_label_ga: string?     @description("Irish label; null if EN-only")
  level: LCLevel
  ncca_lo_code: string?       @description("e.g. 'LC-MATHS-LO-2.4' or null")
  key_competencies: NCCAKeyCompetency[]

  // Cross-subject links (the competency backbone)
  related_subjects: SubjectArea[]  @description("Subjects whose syllabi mention this topic")
  related_topic_ids: string[]      @description("Cross-subject topic IDs that this topic bridges to")

  // Provenance
  source_pdf: string
  source_page: int
  extraction_confidence: float   @description("0.0-1.0")
  extracted_at: string           @description("ISO 8601 datetime")
}

class CrossSubjectTopicSet {
  subject: SubjectArea
  level: LCLevel
  language: string               @description("en or ga")
  topics: CrossSubjectTopic[]
  total_topics: int
  cross_subject_bridges: int     @description("Count of topics linked to >=1 other subject")
}

// ============================================================================
// BAML functions
// ============================================================================

function ExtractCrossSubjectTopics(
  subject: SubjectArea,
  level: LCLevel,
  language: string,
  pdf_text: string,
  source_pdf: string,
) -> CrossSubjectTopicSet {
  client ExtractEn
  prompt #"
    You are the BIEP v1 cross-subject topic extractor. Given the
    following NCCA Leaving Certificate {{ subject }} syllabus text at
    level {{ level }} (language: {{ language }}), extract the
    canonical cross-subject topics.

    Source PDF: {{ source_pdf }}

    PDF text (first 12,000 chars):
    ---
    {{ pdf_text }}
    ---

    Return a CrossSubjectTopicSet with:
      - subject, level, language
      - topics: list of CrossSubjectTopic
        (each with topic_id="{subject}-{topic-slug}-{level}",
         subject, topic_label_en, topic_label_ga, level,
         ncca_lo_code, key_competencies, related_subjects,
         related_topic_ids, source_pdf, source_page,
         extraction_confidence 0.0-1.0, extracted_at=ISO datetime)
      - total_topics: integer
      - cross_subject_bridges: count of topics that link to >=1
        other SubjectArea

    Identify cross-subject links (e.g. a Mathematics "Statistics" topic
    that bridges to "Geography — Data Analysis", a Chemistry
    "Acids/Bases" topic that bridges to "Biology — pH Balance"). Be
    CONSERVATIVE — only mark related_subjects when the connection is
    explicit in the syllabus text, not inferred.

    Preserve BILINGUAL nature: every CrossSubjectTopic should have
    BOTH topic_label_en and topic_label_ga (topic_label_ga may be null
    for EN-only syllabi).

    {{ ctx.output_format }}
  "#
}

function LinkTopicToCompetency(
  topic: CrossSubjectTopic,
  competency: NCCAKeyCompetency,
) -> CrossSubjectTopic {
  client ExtractEn
  prompt #"
    Validate that the given NCCA Key Competency ({{ competency }}) is
    correctly associated with the following cross-subject topic.

    Topic:
    {{ topic }}

    If the association is valid, return the topic unchanged. If the
    competency is mis-assigned, REMOVE it from
    topic.key_competencies and set
    topic.extraction_confidence = max(0, topic.extraction_confidence - 0.2).

    Always return a CrossSubjectTopic.

    {{ ctx.output_format }}
  "#
}
