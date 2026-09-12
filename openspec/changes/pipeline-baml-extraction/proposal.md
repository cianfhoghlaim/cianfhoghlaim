## Why

The BAML extraction completion
(`2026-08-10-baml-extraction-completion-v1`) and CopilotKit action
wiring (`2026-08-10-copilotkit-action-wiring-v1`) changes share the
extraction→action contract that powers every agent. Bundling them
records that BAML completion is incomplete without the action
surface it feeds.

## What Changes

- Cross-batch BAML completion + CopilotKit action contract: the
  extraction completion depends on the action wiring shipping
  first (no point having extracted BAML output with no caller).
- Records the dependency order in `design.md`.

## Capabilities

(none added; pure bundling)

## Impact

- **Affected changes**: 2 bundled
- **Affected code**: none — this change is metadata-only