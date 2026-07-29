# Spec delta: `multimodal-code-and-media-intel`

This delta is part of the openspec change
`2026-07-14-multimodal-code-and-media-intel-v1`. The 4 ADDED
Requirements below already exist in the canonical `multimodal-code-and-media-intel`
spec from the parallel-session work. This change is now **deferred**
(per the proposal.md header note + the centralized-model-schema-registry
Phase 7 deferral). This delta adds ONE new requirement reflecting
the deferral state.

## ADDED Requirements

### Requirement: Multimodal rollout is deferred until CocoIndex factory dedup pattern lands

The system SHALL defer the multimodal CocoIndex rollout (4 streams:
youtube_kg, package_changelog, codebase_git_history, repo_arch_docs)
until the CocoIndex factory dedup pattern (centralized-model-schema-registry
Phase 7) lands. The 10 tasks already shipped (Phase 0 codeolas primitives +
Phase 1.1-1.5 partial youtube_kg) remain in place; the 40 remaining tasks
are tracked under this deferred requirement.

#### Scenario: operator checks the multimodal deferral state

- **WHEN** the operator runs `openspec list` and finds
  `multimodal-code-and-media-intel` archived
- **THEN** the canonical spec at `openspec/specs/multimodal-code-and-media-intel/spec.md`
  SHALL show this deferral requirement
- **AND** the 4 base requirements (5 v1 Apps + OCR/VLM registry + WhisperX + 7+5 cognify)
  SHALL remain in the canonical spec
