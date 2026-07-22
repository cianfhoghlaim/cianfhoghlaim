// oideachais/baml_src/site_analysis.baml
//
// Phase 8 of the openspec change `lateralise-british-isles-domains`.
// BAML classes for firecrawl/browserbase-driven site analysis records.
//
// One `SiteAnalysis` row is written per public source in
// `oideachais/sources.yaml`. The row is consumed by:
//   * `oideachais.site_analysis.extractor` (firecrawl MCP)
//   * `oideachais.dagster_defs.assets.site_analysis.extract` (Dagster asset)
//   * `oideachais.cocoindex_flows.site_analysis_embedding` (LanceDB embed)
//   * `oideachais.cognee_integration.site_analysis_cognify` (Cognee graph)

class SoftwareFingerprint {
  cms string?            @description("Detected CMS (e.g. WordPress, Drupal, Joomla).")
  waf string?            @description("Web application firewall in front of the site.")
  captcha string?        @description("Captcha provider if any.")
  analytics string[]     @description("Analytics / tracking scripts detected.")
  framework_headers string[] @description("HTTP framework headers (e.g. X-Powered-By).")
  fonts string[]         @description("Distinct web fonts referenced in the site.")
}

class LayoutFingerprint {
  main_content_xpath string?  @description("XPath of the main content node on a sample page.")
  sticky_nav bool              @description("Whether a sticky / fixed-position navigation bar is present.")
  cookie_banner bool           @description("Whether a cookie consent banner is present on the home page.")
  form_regions string[]        @description("CSS selectors for form regions (search, login, etc.).")
  pagination_pattern string?   @description("Detected pagination pattern: link, button, infinite-scroll, none.")
}

class PageDescription {
  url string
  h1 string?
  h2_hierarchy string[]
  summary string              @description("LLM-generated one-paragraph summary of the page.")
  links string[]
  attachments string[]        @description("List of downloadable attachments (PDF / DOCX / etc.)")
}

class SiteAnalysis {
  source_id string           @description("sources.yaml id, e.g. ni.education.ccea.")
  captured_at string         @description("ISO-8601 UTC timestamp of the capture.")
  url string                 @description("Root URL of the source.")
  software SoftwareFingerprint
  layout LayoutFingerprint
  pages_sampled int
  pages PageDescription[]
  screenshot_path string?    @description("Garage S3 path of the full-page screenshot.")
  compliance_notes string?   @description("Optional free-text compliance / accessibility observations.")
}
