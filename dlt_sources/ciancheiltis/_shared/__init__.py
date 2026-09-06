"""Shared helpers for all six ciancheiltis phases.

Implements:

- `language_detector.detect_languages(body: str) -> dict[str, float]` —
  content-based lingua-py detection on the first 5 KB; never trust
  `metadata["language"]`.
- `opaque_url_scanner.scan(base_url) -> list[str]` — discovers
  numeric/slug-only URLs that hide their language pair (the
  `legislation.gov.uk/uksi/2007/1484/made` pattern).
- `gov_wales_waf_bypass.fetch(url, *, client) -> PageFetch` —
  gov.wales CloudFront + WAF + CAPTCHA fallback (Firecrawl interact
  with profile + hwb.gov.wales mirror).
- `bilingual_page_validator.is_same_article(url_a, url_b) -> bool` —
  structural check that two URLs are the same article in different
  languages.
"""
