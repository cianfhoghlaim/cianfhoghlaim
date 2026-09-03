# Spec delta: `stacks-sync-loop`

This delta is part of the openspec change
`2026-08-15-stacks-sync-loop-v1`. The 6 ADDED Requirements below already
exist in the canonical `stacks-sync-loop` spec from the parallel-session
work. This delta adds ONE new requirement: the Tailscale/Cloudflare
integration check.

## ADDED Requirements

> Note: The 6 base requirements (Layer 1 sync:stacks-drift, Layer 2
> sync:stacks-ccc, Layer 3 sync:stacks-cognee, Layer 4 sync:stacks-validate,
> Layer 5 sync:stacks-health, Layer 6 sync:stacks orchestrator) were already
> added to the canonical spec by the parallel-session work. This delta
> focuses only on the additional Tailscale/Cloudflare integration.

### Requirement: sync:stacks also validates Tailscale + Cloudflare sidecar consistency

The system SHALL extend `sync:stacks-validate` to also verify that
every stack with `network_mode: host` or `internal: true` has a
matching Tailscale ACL entry at `bonneagar/tailscale/acl-{host}.json`
+ a Cloudflare tunnel route at `bonneagar/cloudflare/tunnel-routes/`.

#### Scenario: stack with internal: true has a missing Tailscale ACL

- **GIVEN** `bonneagar/stacks/agent-os/compose.yaml` has `internal: true`
- **WHEN** `mise run sync:stacks-validate` is invoked
- **THEN** the task SHALL check for `bonneagar/tailscale/acl-bunchloch.json`
- **AND** the task SHALL fail if the ACL doesn't reference the stack's
  5 service ports + the 2 outbound credentials paths
- **AND** the report SHALL list the missing ACL entries

#### Scenario: All stacks have complete Tailscale + Cloudflare integration

- **GIVEN** all 89 stacks have `internal: true` or `network_mode: host`
- **WHEN** `mise run sync:stacks-validate` is invoked
- **THEN** the task SHALL verify each stack has a matching Tailscale ACL
  + Cloudflare tunnel route
- **AND** the task SHALL exit 0 if all stacks are consistent
- **AND** the task SHALL exit 1 if any stack is missing the integration
