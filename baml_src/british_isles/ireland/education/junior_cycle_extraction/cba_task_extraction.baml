// BAML Schema for NCCA Junior Cycle Classroom-Based Assessment (CBA) extraction.
//
// Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

class CbaTask {
  cba_id string                   @description("e.g. 'cba-english-jc1-2026'")
  subject_slug string
  cba_type string                 @description("e.g. 'written_task', 'practical_investigation', 'oral_present'")
  title_en string
  title_ga string?
  brief_text_en string            @description("Full CBA brief text")
  learning_outcomes_assessed string[]
  duration_hours int              @description("Suggested student time on the CBA")
  assessment_criteria string[]    @description("e.g. ['originality', 'research', 'communication']")
  marking_scheme_rubric string[]  @description("Level descriptors per assessment criterion")
  exemplar_work_url string?       @description("URL to NCCA exemplar student work")
  source_url string
  scraped_at string
}

function ExtractCbaTask(input: string, cba_id: string) -> CbaTask {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting NCCA Junior Cycle Classroom-Based
    Assessment (CBA) task details.

    For CBA {{ cba_id }}, extract the full task: subject, type, title,
    brief text, learning outcomes assessed, suggested duration,
    assessment criteria, marking scheme rubric, exemplar work URL.

    {{ ctx.output_format }}
    {{ input }}
  "#
}
