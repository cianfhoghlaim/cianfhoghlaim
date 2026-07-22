// Canonical BAML: Circular Extraction (DoE circulars + marking schemes)
//
// Promoted from spaces/_common/baml/hackathon_schemas.baml (2026-06-24).
// Used by:
//   - spaces/an_scrudu/ (the An Scrúdú Space)
//   - oideachais/dlt_sources/domains/education/ie/leaving_cert.py (the canonical DLT source)
//
// Uses the canonical LitellmClient (routes through http://litellm:4000/v1).
// Replaces the spaces-only BAML_HACKATHON_CHAINED client.

class CircularReference {
  circular_number int
  issued_year int
  issuing_body string  // e.g. "Department of Education and Skills"
  title_en string
  title_ga string?
  subject string  // e.g. "Chemistry", "Irish", "Mathematics"
  level string    // e.g. "Leaving Certificate", "Junior Certificate"
}

class TopicDistribution {
  topic_code string  // e.g. "CH1", "IR1" — section code in the circular
  topic_label string
  marking_points int
  paper_section string  // e.g. "Section A", "Section B"
}

class MarkingSchemeSummary {
  total_marking_points int
  topics TopicDistribution[]
  estimated_paper_duration_min int
  has_orale bool  // Irish oral component?
  has_coursework bool
}

class CircularExtraction {
  circular CircularReference
  scheme MarkingSchemeSummary
  raw_text_excerpt string
  extraction_confidence float  // 0.0 - 1.0
  @@stream.done
}

function ExtractCircularMeta(
  pdf_text: string,
  filename: string,
) -> CircularExtraction {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
