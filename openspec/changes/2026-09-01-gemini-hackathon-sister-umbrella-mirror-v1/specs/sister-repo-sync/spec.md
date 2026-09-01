## ADDED Requirements

### Requirement: The gemini_hackathon sister-repo umbrella mirror SHALL be tracked

The cianfhoghlaim monorepo SHALL maintain a
`gemini-hackathon-sister-umbrella-mirror-v1` openspec change
at
`openspec/changes/2026-09-01-gemini-hackathon-sister-umbrella-mirror-v1/`
that tracks the gemini_hackathon-side backlogs (the
`2026-08-24-gemini-hackathon-public-v1/` public showcase
contract + `2026-08-25-per-subnation-user-context/` per-UK-
jurisdiction user context) + the per-PR reciprocal mirror
contract + the per-quadrant DuckLake `metadata_schema`
(`oideachais` quadrant) + the per-sister Langfuse project
mapping (`gemini-hackathon-dev` + `gemini-hackathon-prod`).

The mirror SHALL reference the
[`2026-08-26-empower-gemini-hackathon-v1/`](../2026-08-26-empower-gemini-hackathon-v1/)
umbrella which is the canonical showcase umbrella, and the
new
[`2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/`](../2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/)
Phase 1 umbrella which integrates the gemini_hackathon
learnings back into cianfhoghlaim.

#### Scenario: The gemini_hackathon mirror change is in the active openspec list

- **WHEN** the operator runs `uv run openspec list | grep gemini-hackathon-sister-umbrella-mirror`
- **THEN** the mirror change SHALL appear in the active list
- **AND** the mirror's `proposal.md` SHALL carry the 4 metadata fields
- **AND** `uv run openspec validate 2026-09-01-gemini-hackathon-sister-umbrella-mirror-v1 --strict` SHALL exit 0