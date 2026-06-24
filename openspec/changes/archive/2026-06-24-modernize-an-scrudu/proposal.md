## Why

`spaces/an_scrudu/` (An Scrúdú, the past-paper heatmap) was the
canonical Space 1 of the 2026-06 hackathon. Since then:

- The BAML `ExtractCircularMeta` function has been promoted to
  `oideachais/baml_src/circular_extraction.baml` (the canonical
  location, with the canonical `LitellmClient`).
- The 3-tier HF Inference fallback chain in
  `spaces/_common/baml_client.py` has been replaced with the
  canonical KCG LiteLLM gateway (the HF chain is now the
  offline-mode fallback only).
- The canonical oideachais quadrant has a 5-stage leabharlann
  pipeline (BAML → CocoIndex v1 → Cognee → Graphiti → LanceDB)
  that the Space should consume.

The Space's `extraction.py` still uses the hand-rolled
`chat_complete_json` call (which now goes through the LiteLLM
gateway per A2, but the response is not validated against a
schema) and the flat `dataclass` (which is brittle when the
LLM returns the nested BAML shape).

This change modernizes the Space:

1. Add Pydantic v2 schemas that mirror the canonical
   `oideachais/baml_src/circular_extraction.baml` (the
   CircularReference + TopicDistribution + MarkingSchemeSummary
   + CircularExtraction classes).
2. Update `_validate_and_coerce` to validate the LLM response
   against the Pydantic schema (accepts both the nested BAML
   shape and the flat legacy shape).
3. Update the prompt to request the nested BAML shape (matches
   the canonical BAML function).
4. Add `pydantic>=2.5` to `requirements.txt`.

The Space is now schema-validated, uses the canonical BAML
shape, and falls back to the regex-based offline mode only
when both the LiteLLM gateway AND the HF Inference chain
fail.

## What changes

- `spaces/an_scrudu/extraction.py` — add the 4 Pydantic models
  (PCircularReference, PTopicDistribution, PMarkingSchemeSummary,
  PCircularExtraction) + update `_validate_and_coerce` to use them
- `spaces/an_scrudu/extraction.py` — update the prompt template to
  request the nested BAML shape
- `spaces/an_scrudu/requirements.txt` — add `pydantic>=2.5`
- 1 MODIFIED Requirement to the `oideachais-pipeline` spec
  (the Space consumes the canonical lakehouse pipeline)
- 1 MODIFIED Requirement to the `spaces-cicd-pipeline` spec
  (the modernization is the C1 instance of the spec)

## Out of scope

- Switching to the real BAML compiler (would require
  `baml-cli generate` in the Space; the Pydantic mirror gives
  80% of the benefits without the BAML toolchain dep)
- The actual `oideachais/dlt_sources/domains/education/ie/leaving_cert.py`
  DLT source integration (a separate change)
- The marimo heatmap replacement (covered in the
  `marimo/SKILL.md` skill; not in this change)
