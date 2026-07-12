## ADDED Requirements

### Requirement: Portal marimo cross-reference

The system SHALL cross-reference the `portal-cloudflare-r2` marimo
notebook deployment in
`openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md`
R15 so that future agents looking up the canonical marimo-on-Cloudflare
pattern find both the mission-control and the study-plan examples.

#### Scenario: An agent searches for the canonical marimo pattern

- **WHEN** the agent opens `openspec/specs/official-media-marimo/spec.md`
- **THEN** the `## See also` section MUST link to the leaving-cert-portal
  R15 requirement (marimo notebook deployed to Cloudflare)
