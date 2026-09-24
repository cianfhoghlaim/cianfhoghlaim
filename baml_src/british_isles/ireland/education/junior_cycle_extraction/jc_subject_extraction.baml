// BAML Schema for NCCA Junior Cycle Subject Specification extraction.
//
// Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
// Fills the previously-empty baml_src/.../junior_cycle_extraction/ dir.

class JcSubjectSpec {
  subject_slug string            @description("e.g. 'english', 'mathematics'")
  subject_code string            @description("e.g. 'EN', 'MA'")
  title_en string
  title_ga string?
  level string                    @description("'common', 'higher', 'ordinary'")
  strands string[]                @description("Subject strands per NCCA spec")
  learning_outcomes string[]      @description("Per-strand learning outcomes")
  assessment_methods string[]     @description("e.g. ['CBA 1', 'CBA 2', 'Assessment Task']")
  prerequisites string[]?
  duration_hours int?
  source_url string
  scraped_at string
  confidence float
}

function ExtractJcSubjectSpec(input: string, subject_slug: string) -> JcSubjectSpec {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting NCCA Junior Cycle subject
    specifications from curriculumonline.ie.

    For subject {{ subject_slug }}, extract the full specification:
    code, title (EN + GA), level, strands, learning outcomes,
    assessment methods, prerequisites, duration hours.

    {{ ctx.output_format }}
    {{ input }}
  "#
}
