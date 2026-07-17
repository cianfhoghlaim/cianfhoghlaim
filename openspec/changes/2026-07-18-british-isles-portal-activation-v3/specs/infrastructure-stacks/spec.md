## ADDED Requirements

### Requirement: portal-cloudflare-r2 stack entry

The system SHALL add a new stack at `bonneagar/stacks/portal-cloudflare-r2/`
following the 6-file GOLD_STANDARD pattern (compose.yaml + wrangler.jsonc +
Dockerfile + README.md + docs/STACK.md + Pangolin route).

The stack SHALL host:
- 1 Cloudflare R2 bucket (`cianfhoghlaim-pdfs`)
- 1 Cloudflare Pages project (`portal`)
- 1 Pangolin resource binding (`portal.cianfhoghlaim.ie` → Cloudflare tunnel)
- 1 Locket sidecar (secret injection from Infisical `dev-baile`)
- 1 Cloudflare Tunnel sidecar

**No Cloudflare Worker is required.** Signed URLs are issued from the
existing `hono-api` service (which already has S3 credentials via the
Garage S3 backend). This keeps the project on the Cloudflare free tier
with **no Workers Paid subscription required**.

Free-tier limits SHALL be called out in the README (10 GB storage + 1M
Class A ops/mo).

#### Scenario: Operator reads the stack README

- **WHEN** the operator opens `bonneagar/stacks/portal-cloudflare-r2/README.md`
- **THEN** they see the 6-file pattern + the free-tier limits
- **AND** the document notes that signed URLs are issued from Hono (no Workers Paid required)
- **AND** the stack is `bun run iac:plan --stack portal-cloudflare-r2`-able

#### Scenario: Stack deploys end-to-end

- **GIVEN** the operator runs `bun run iac:deploy --stack portal-cloudflare-r2`
- **WHEN** the deploy completes
- **THEN** `portal.cianfhoghlaim.ie` resolves to the leaving-cert app
- **AND** PDF assets download via Hono-issued signed R2 URLs (15-min TTL)

### Requirement: Pocket ID SSO as the single OIDC provider

The system SHALL use Pocket ID OIDC as the single SSO provider
across all 5 canonical surfaces + the central portal. The 5 OIDC
audiences SHALL be:

| Audience | Surface |
|---|---|
| `convex_backend` | Convex (all surfaces) |
| `croilar_web` | `croilar-web` |
| `croilar_portal` | `croilar-portal` |
| `leaving_cert_portal` | `cianfhoghlaim-leaving-cert` (5th surface) |
| `portal` | `portal.cianfhoghlaim.ie` (central portal entry) |

The Pocket ID instance SHALL live on `arm1-oci`.

#### Scenario: An operator adds a new OIDC audience

- **GIVEN** the operator wants to add a 6th audience for a future surface
- **WHEN** they edit `bonneagar/iac/pocketid/audiences.yaml`
- **THEN** the Pocket ID instance picks up the change via resource-sync
- **AND** the new audience appears in the JWKS at `/.well-known/jwks.json`

### Requirement: Sequential domain-by-domain migration as architectural principle

The system SHALL document the sequential domain-by-domain migration
principle (no big-bang cutovers) as a core IaC architectural rule.
The pattern is operationalized by the feature-flag rollout documented
in
`openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md`
R25.

#### Scenario: A new stack is deployed

- **GIVEN** the operator wants to deploy the `portal-cloudflare-r2` stack
- **WHEN** they run `bun run iac:deploy --stack portal-cloudflare-r2`
- **THEN** the rollout is gated by the `portal_rollout` feature flag
- **AND** the rollout proceeds 10% → 50% → 100% over 7 days
- **AND** any error rate spike triggers automatic rollback
