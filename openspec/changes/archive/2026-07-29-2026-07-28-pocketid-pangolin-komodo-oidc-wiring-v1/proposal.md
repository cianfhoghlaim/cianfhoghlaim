## Superseded by recent IaC commits

All work proposed here has been shipped in the IaC cluster's recent commits. See the bons-locker-shim v0.2.0 release + the IaC stack contract reconciliation + the agent-platform cluster deploy for the authoritative record.

# Change: 2026-07-28-pocketid-pangolin-komodo-oidc-wiring-v1

## Why

The Cianfhoghlaim local dev stack has 3 services that all need to be
authenticated via the same OIDC identity provider (Pocket ID):

- Pangolin (proxy / dashboard)
- Komodo (orchestrator)
- All Pangolin-protected services (via TinyAuth middleware)

Currently the wiring is manual:
1. Operator logs into Pocket ID - creates a `komodo` OIDC client
2. Operator logs into Komodo - pastes the client_id + client_secret
3. Operator logs into Pangolin - adds Pocket ID as an Identity Provider
4. Operator adds the IdP to each Pangolin Resource (a 4th manual step)

For non-technical users of this repo, this is 4+ steps of secret rotation
with no audit trail.

This change:
1. Ships a single one-shot bash script (scripts/wire-pocketid-pangolin-komodo.sh)
   that automates all 4 steps via the Pocket ID + Pangolin REST APIs
2. Adds PangolinClient.listIdps() / createIdp() / deleteIdp() to the
   bons IaC client
3. Refactors wire-pocketid-as-oidc.ts from a 330-line TypeScript
   implementation to a 100-line TypeScript wrapper around the bash script
4. Adds a comprehensive onboarding runbook at
   deploy-runbooks/pocketid-pangolin-komodo-onboarding.md

## What changes

- 1 new bash script: scripts/wire-pocketid-pangolin-komodo.sh (296 lines)
- 1 new runbook: bonneagar/deploy-runbooks/pocketid-pangolin-komodo-onboarding.md
- 3 new methods on bonneagar/iac/clients/pangolin-client.ts:
  - listIdps() - GET /api/v1/idp?org_id=...
  - createIdp(opts) - POST /api/v1/idp
  - deleteIdp(idpId) - DELETE /api/v1/idp/{idp_id}?org_id=...
- Refactored: bonneagar/iac/commands/wire-pocketid-as-oidc.ts (100 lines)
- 2 new ADDED Requirements to infrastructure-stacks

## Impact

- Affected specs: infrastructure-stacks (shared) only
- Affected hosts: any cluster with the Pocket ID + Komodo + Pangolin stack pattern
- Risk: low (idempotent + audit record)
- Operators: --skip-komodo and --skip-pangolin flags for partial deployments

## Dependencies

Blocked by: none
Blocked by (soft):
  - 2026-07-24-iac-sync-sites-pangolin-private-infisical-repair-v1 (Pocket ID is already
    running on arm1-oci)
Affected repos: cianfhoghlaim (single-repo change)

## Spec delta

See specs/infrastructure-stacks/spec.md for 2 ADDED Requirements.

## Open follow-up issues

| Issue | Tracking change |
|---|---|
| Wire the Pangolin Resource IdP (not just Org IdP) | 2026-07-XX-wire-pocketid-pangolin-resource-idp-v1 |
| Rotate the bons-iac OIDC client secret every 90 days | 2026-07-XX-pocketid-bons-iac-secret-rotation-v1 |
| Wire Komodo + Periphery from the get-go | 2026-07-XX-komodo-periphery-bootstrap-from-pocketid-v1 |
| Onboard less-technical users via a guided wizard | 2026-07-XX-pocketid-onboarding-wizard-v1 |
