## ADDED Requirements

### Requirement: cianfhoghlaim MUST carry `baml_src/_shared/provider_router.py`

The cianfhoghlaim repo SHALL carry the canonical shared provider
router module at `baml_src/_shared/provider_router.py` (wholesale
copy of `cianchosaint/baml_src/_shared/provider_router.py`) plus
the cianfhoghlaim-local extensions for the 6 hackathon HF
Inference backends + the 9 M3 chokepoint aliases.

#### Scenario: Wholesale copy lands

- **WHEN** a sister-repo sync agent runs the wholesale-copy
  contract from `cianchosaint-handoff-v1/proposal.md` §Shared-1
- **THEN** the file MUST exist at the canonical path
- **AND** MUST export the same `Provider`, `ProviderRouter`,
  `resolve()`, and `route_call()` API as the cianchosaint origin
- **AND** MUST be importable via `from baml_src._shared.provider_router import ProviderRouter`
