# drift-remediation

## MODIFIED Requirements

### Requirement: The registry audit covers all hardcoded-model surfaces

The system SHALL include `meaisinfhoghlaim/` in the `_AUDIT_DIRS` list
of `scripts/registry_audit.py`. The audit's purpose is to catch
hardcoded model strings; the gap means the hardcoded defaults in
`meaisinfhoghlaim/models/routing.py` are invisible to the gate.

The previous requirement's reference to "4 hardcoded defaults in
`meaisinfhoghlaim/process/llm_router.py`" is **stale** — those defaults
were migrated to `model_for(...)` lookups by the
`2026-07-30-drift-remediation-everything-bagel-v1` change (commits
verified during the `2026-08-17-hygiene-drift-cleanup-v1` ccc audit;
`llm_router.py:315,332,350,365` all call `model_for(...)` correctly).

The remaining gap was `meaisinfhoghlaim/models/routing.py:58-79,97`:
~15 hardcoded model strings (`uccix-mistral-24b`, `gemma-4-26B-A4B`,
`molmo2-8b`) in the per-`(source_group, language)` routing table. These
were also migrated as part of `2026-08-17-hygiene-drift-cleanup-v1`
(P3.1 + P3.3 tasks). The routing table now references 4 canonical
constants (`DEFAULT_TEXT_MODEL`, `IRISH_TEXT_MODEL`,
`DIAGRAM_OCR_MODEL`, `DEFAULT_OCR_MODEL`) that all resolve via
`model_for(...)`.

The regression gate that enforces this going forward is
`tests/test_routing_model_registry.py`, which fails if any entry in
`ROUTING_TABLE` uses a model string that is NOT one of the 4 canonical
constants.

#### Scenario: A hardcoded model is added to meaisinfhoghlaim/models/routing.py

- **GIVEN** a developer adds a new entry to `ROUTING_TABLE` with
  `model="qwen3-vl-30b-a3b"` (a raw string, not a constant)
- **WHEN** `mise run lint:registry` runs
- **THEN** the audit MUST detect the new hardcoded string (because
  `meaisinfhoghlaim/` is in `_AUDIT_DIRS` per the
  `2026-07-30-drift-remediation-everything-bagel-v1` change)
- **AND** `pytest tests/test_routing_model_registry.py` MUST fail with
  a finding like `routing_table[(new_source, 'en')] uses an unknown model string 'qwen3-vl-30b-a3b'; expected one of the 4 canonical constants`

#### Scenario: The 4 canonical constants resolve via model_for()

- **WHEN** `meaisinfhoghlaim.models.routing` is imported
- **THEN** all 4 constants (`DEFAULT_TEXT_MODEL`, `IRISH_TEXT_MODEL`,
  `DIAGRAM_OCR_MODEL`, `DEFAULT_OCR_MODEL`) MUST resolve to the same
  strings that `model_for("text_llm", "default")`,
  `model_for("text_llm", "irish", language="ga")`,
  `model_for("ocr_vision", "specialist")`, and
  `model_for("ocr_vision", "default")` return
- **AND** `tests/test_routing_model_registry.py` MUST pass all 12
  assertions