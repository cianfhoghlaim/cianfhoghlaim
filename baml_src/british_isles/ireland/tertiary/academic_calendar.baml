// BAML Schema for UoG Academic Calendar events.
//
// Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.
//
// Migrated from
// kings_college_galway/baml_src/uog/processing/academic_calendar.baml
// (retired per the umbrella change).

class AcademicCalendarEvent {
  date_iso string @description("ISO-8601 date of the event, e.g. '2025-09-08'")
  event_name_english string @description("Event name in English, e.g. 'Start of Teaching - Semester 1'")
  event_name_irish string? @description("Event name in Irish, e.g. 'Tús na Teagaisc - Seimeastar 1'")
  category "teaching" | "exam" | "registration" | "graduation" | "holiday" | "ceremony" | "other"
  academic_year string @description("Academic year, e.g. '2025/26'")
  source_url string @description("Canonical URL of the calendar page")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Extraction confidence 0.0-1.0")
}

function ExtractAcademicCalendarEvent(input: string) -> AcademicCalendarEvent {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting University of Galway academic calendar
    events from the public calendar page at
    https://www.universityofgalway.ie/academic-calendar/.

    Extract: date_iso, event_name_english + irish, category,
    academic_year.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractAcademicCalendarBulk(input: string) -> AcademicCalendarEvent[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting every University of Galway academic
    calendar event from the calendar page. Return one
    AcademicCalendarEvent per event.

    {{ ctx.output_format }}
    {{ input }}
  "#
}
