// =============================================================================
// Curriculum Relationship Functions (split from curriculum_extraction.baml)
// Cross-stage relationship extraction functions for the 5-stage cognify pass.
// =============================================================================

function ExtractLearningOutcomeRelationships(source_outcome: LearningOutcome,
  target_outcomes: LearningOutcome[],
  subject_context: string) -> RelationshipExtractionResult {
  client Claude
  prompt #"You are an expert curriculum analyst specializing in Irish education.

Analyze relationships between learning outcomes in {{ subject_context }}.

SOURCE LEARNING OUTCOME:
- Code: {{ source_outcome.code }}
- Description (EN): {{ source_outcome.description_en }}
{% if source_outcome.description_ga %}- Description (GA): {{ source_outcome.description_ga }}{% endif %}
- Subject: {{ source_outcome.subject }}
- Level: {{ source_outcome.level }}
- Difficulty: {{ source_outcome.difficulty }}
{% if source_outcome.strand %}- Strand: {{ source_outcome.strand }}{% endif %}
{% if source_outcome.strand_unit %}- Unit: {{ source_outcome.strand_unit }}{% endif %}
- Key Skills: {{ source_outcome.key_skills }}

POTENTIAL TARGET OUTCOMES:
{% for target in target_outcomes %}
- {{ target.code }}: {{ target.description_en }}
  Level: {{ target.level }}, Difficulty: {{ target.difficulty }}
{% endfor %}

For each meaningful relationship found, identify:
- Edge type (PREREQUISITE_FOR, BUILDS_ON, ASSESSES, RELATED_TO, PART_OF, ENABLES, CONTRASTS_WITH)
- Confidence score (0.0-1.0)
- Brief rationale (1-2 sentences citing the source outcome's code)
- Any Irish-language curriculum terminology (use bilingual labels)

The relationships should form a directed graph that captures prerequisite chains, skill dependencies, and conceptual connections across the Irish curriculum. Cite specific learning outcome codes in rationales.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SOURCE: {{ source_outcome.code }}
    CONTEXT: {{ subject_context }}
"#
}


function ExtractSkillsFromOutcome(outcome: LearningOutcome,
  curriculum_context: string) -> SkillExtractionResult {
  client Claude
  prompt #"You are an expert Irish education curriculum analyst.

Extract the key skills, competencies, and learning dimensions embedded in a single learning outcome from the Irish curriculum.

CURRICULUM CONTEXT:
{{ curriculum_context }}

LEARNING OUTCOME:
- Code: {{ outcome.code }}
- Description (EN): {{ outcome.description_en }}
{% if outcome.description_ga %}- Description (GA): {{ outcome.description_ga }}{% endif %}
- Subject: {{ outcome.subject }}
- Level: {{ outcome.level }}

For each skill extracted, identify:
- The skill name (use canonical Irish education terminology)
- The skill category (Cognitive, Creative, Communication, Physical, Personal, Social, Numeracy, Literacy, Digital)
- A proficiency level indicator
- Specific evidence from the outcome description that demonstrates this skill

Use bilingual labels (English and Irish) for skill names where the Irish curriculum has a specific term.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    OUTCOME: {{ outcome.code }}
    CONTEXT: {{ curriculum_context }}
"#
}


function ExtractCurriculumFromDocument(document_text: string,
  subject: string,
  level: EducationLevel) -> ExtractedCurriculumDocument {
  client Claude
  prompt #"You are an expert curriculum document parser specializing in the Irish education system.

Parse a curriculum specification document and extract its complete structure.

SUBJECT: {{ subject }}
LEVEL: {{ level }}

DOCUMENT TEXT:
{{ document_text }}

Extract:
1. Document metadata (title, year, cycle, language, URL, document_type)
2. Aims and objectives (with both English and Irish versions where available)
3. Strands with their codes, titles (EN/GA), and descriptions
4. Strand units within each strand
5. Learning outcomes grouped by strand, with full bilingual text
6. Key skills, cross-curricular themes, and assessment approaches mentioned
7. Any explicit references to related NCCA publications

For bilingual content, extract both English (description_en) and Irish (description_ga) variants. If Irish is not present, leave description_ga as null.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    SUBJECT: {{ subject }}
    LEVEL: {{ level }}
"#
}


function IdentifyPrerequisiteChain(target_outcome: LearningOutcome,
  available_outcomes: LearningOutcome[],
  max_depth: int) -> LearningOutcome[] {
  client Claude
  prompt #"You are an expert at identifying prerequisite learning outcome chains in the Irish education curriculum.

TARGET OUTCOME:
- Code: {{ target_outcome.code }}
- Description: {{ target_outcome.description_en }}
- Level: {{ target_outcome.level }}, Subject: {{ target_outcome.subject }}

AVAILABLE OUTCOMES (the full corpus you can choose from):
{% for available in available_outcomes %}
- {{ available.code }}: {{ available.description_en }} (Level: {{ available.level }})
{% endfor %}

Identify the prerequisite chain (up to {{ max_depth }} levels deep) by selecting the outcomes that a student must master BEFORE attempting the target outcome.

Prerequisites should:
- Be at a LOWER difficulty level or earlier in the learning progression
- Be from the same subject or directly cross-curricular foundation subjects
- Be necessary (not merely helpful) for understanding the target
- Be ordered from most fundamental to most advanced

Return the chain in dependency order (foundational first).

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    TARGET: {{ target_outcome.code }}
    DEPTH: {{ max_depth }}
"#
}