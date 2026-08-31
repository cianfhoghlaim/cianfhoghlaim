## MODIFIED Requirements

### Requirement: 14 NCCA + NCCA-adjacent subject coverage (was: 8 NCCA)

The standalone `tuatha/` repo SHALL cover exactly **14**
subjects: the 8 NCCA Leaving Certificate subjects
(Mathematics + Applied Mathematics + Chemistry + Geography +
History + English + Gaeilge + Computer Science) + the 6
NCCA-adjacent subjects (Accounting + Biology + Business +
French + Irish (T2) + Physics) added in the
`2026-08-26-tuatha-subject-expansion-to-14-v1` change.

> **Note**: this MODIFIES the canonical
> `cianfhoghlaim-educational-mmo` spec's "8 NCCA subjects"
> requirement. The 8 NCCA subjects remain the canonical NCCA
> set; the 6 NCCA-adjacent subjects are an extension the
> standalone tuatha repo ships (per the user's "all subjects"
> directive of 2026-08-26).

#### Scenario: Each subject has a complete per-subject stack

- **GIVEN** the post-expansion `tuatha/` repo
- **WHEN** the agent verifies the subject coverage
- **THEN** each of the 14 subjects SHALL have:
  - 1 `tuatha/subjects/<subject>.py` ADK LlmAgent
  - 5 `tuatha/tools/<subject>_<tool>.py` per-subject tools
  - 1 `tuatha/baml/qpack_<subject>.baml` BAML contract
  - 1 `tuatha/dlt/{syllabus,past_paper,marking_scheme,formative_item,response_score}/<subject>.py` DLT source
  - 1 `tuatha/web/apps/tuatha-ui/src/routes/realm/<subject>.tsx` PixiJS realm route
  - 1 `tuatha/web/packages/realm-canvas/src/subjects/<subject>.ts` sprite bank

#### Scenario: The 14 SUBJECT_WIRING_REGISTRY entries dispatch the 14 ROUTING_KEYWORDS buckets

- **GIVEN** the post-expansion `tuatha/routing.py`
- **WHEN** the agent invokes `route_message()` with a
  keyword from any of the 14 `ROUTING_KEYWORDS` buckets
  (math / appm / chem / geog / hist / engl / gael / comp +
  acct / biol / bus / fren / iris / phys)
- **THEN** the dispatch SHALL return the correct module_slug
- **AND** `route_message_to_wire()` SHALL return the
  canonical `SubjectAgentWiring` for the matching subject
