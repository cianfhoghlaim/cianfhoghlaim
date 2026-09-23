// BAML Schema for UoG Governance Minutes (University Council + Academic Council).
//
// Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.
//
// Migrated from
// kings_college_galway/baml_src/uog/processing/governance_minute.baml
// (retired per the umbrella change).

class GovernanceMinute {
  meeting_date_iso string @description("ISO-8601 date of the meeting, e.g. '2025-10-15'")
  body "university_council" | "academic_council" | "faculty_board" | "other"
  agenda_items string[] @description("The agenda items discussed, in order")
  decisions string[] @description("Concrete decisions made at the meeting")
  policy_changes string[] @description("Policy changes (e.g. new regulations, new fees)")
  attendees string[] @description("Names of attendees")
  source_url string @description("Canonical URL of the minutes PDF or HTML")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Extraction confidence 0.0-1.0")
}

function ExtractGovernanceMinute(input: string) -> GovernanceMinute {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting University of Galway governance
    minutes (University Council + Academic Council).

    Extract: meeting_date_iso, body, agenda_items[], decisions[],
    policy_changes[], attendees[].

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractGovernanceMinuteBulk(input: string) -> GovernanceMinute[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting every University of Galway governance
    minute from the page. Return one GovernanceMinute per meeting.

    {{ ctx.output_format }}
    {{ input }}
  "#
}
