""// BAML Test block for the meaisinfhoghlaim v5 24-model OCR registry.
//
// Per the meaisinfhoghlaim v5 umbrella spec + the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.
//
// This BAML Test block validates the 24-model v4 registry structure.
// It exercises the canonical get_optimal_for_m4 + select_ocr_backend
// entry points per the v4 platform convention.

function GetOptimalForM4() -> OCRModelV4 {
  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function SelectOCRBackend(pdf_path: string) -> OCRBackendV4 {
  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

class OCRModelV4 {
  key string
  name string
  backend string
  unsloth_id string?
  mlx_id string?
  upstream_id string
  capabilities string[]
  m4_max_48gb_fit bool
  available bool
}

class OCRBackendV4 {
  pdf_path string
  selected_model string
  selected_backend string
}

test GetOptimalForM4 {
  functions [GetOptimalForM4]
  args {
  }
}

test SelectOCRBackend {
  functions [SelectOCRBackend]
  args {
    pdf_path "s3://garage/cianfhoghlaim/ireland/sample.pdf"
  }
}
"""
