// Nigerian federal extraction BAML schema.

class NigerianFederalCurriculumSpec {
  url string
  country string @description("Country code (nga)")
  federal_institution string @description("nuc | jamb | nabteb | nbc | federal_ministry_of_education | ...")
  language string @description("en | ha | yo | ig | pcm")
  title string
  degree_type string? @description("bachelor | master | doctorate | diploma | certificate")
  course_list string[]?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractNigerianFederalCurriculumSpec(
  federal_institution: string,
  language: string,
  text: string
) -> NigerianFederalCurriculumSpec {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
