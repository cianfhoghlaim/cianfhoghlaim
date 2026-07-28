# Change: 2026-07-28-pocketid-komodo-periphery-onboarding-v1

## Why

The Pocket ID + Komodo + Pangolin wiring flow has 5 manual steps that
non-technical operators struggle with. The wire-pocketid-pangolin-komodo.sh
script (from the 2026-07-28 change) covers 3 of them (Pocket ID OIDC client,
Komodo OIDC config, Pangolin IdP). This change adds the missing 2:

  1. Bound each Pangolin Resource (site) to the PocketID IdP (the "4th
     manual step" — was missing)
  2. Komodo + Periphery bootstrap from the get-go (the "5th step" —
     auto-derives Periphery's API key from Pocket ID, self-registers
     Periphery with Pangolin, configures the wire between them)

Plus 2 operator-supporting scripts:

  - onboard-pocketid.sh: a guided TUI/CLI wizard for non-technical users
    that asks 3 questions (Pocket ID admin key, Pangolin API key, Komodo
    password) + validates + persists to .env + optionally runs the wire
    script. This is the "I just want it to work" path.
  - rotate-pocketid-secrets.sh: a 90-day cron job for OIDC client secret
    rotation. Pocket ID rotates secrets on every fetch, so we can't
    store them. This script runs the rotation at 3am on the 1st of every
    3rd month.

## What changes

- 4 new scripts in `scripts/`:
  - `onboard-pocketid.sh` (231 lines): guided TUI/CLI wizard
  - `wire-pocketid-resource-idp.sh` (124 lines): bind PocketID IdP to
    all/specific Pangolin Resources
  - `bootstrap-komodo-periphery.sh` (197 lines): auto-derive Periphery
    API key from Pocket ID, self-register Periphery, wire Komodo
  - `rotate-pocketid-secrets.sh` (113 lines): 90-day cron job for
    OIDC client secret rotation

- 2 ADDED Requirements to `infrastructure-stacks`:
  - "PocketID IdP MUST be bound to every Pangolin Resource (4th manual
    step) — wired by wire-pocketid-resource-idp.sh"
  - "Komodo + Periphery MUST be self-configured from the get-go (5th
    manual step) — wired by bootstrap-komodo-periphery.sh"

## Impact

- **Affected specs:** `infrastructure-stacks` (shared) only
- **Affected hosts:** any cluster with Pocket ID + Komodo + Pangolin
- **Risk:** low (all scripts are idempotent + write audit records)
- **Operators:** the 4 scripts + the 90-day cron make the cluster
  self-managing. Non-technical users can run the wizard once + forget.

## Dependencies

- `Blocked by: 2026-07-28-pocketid-pangolin-komodo-oidc-wiring-v1`
  (the wire script that creates the Pocket ID OIDC client + Pangolin IdP)
- `Affected repos: cianfhoghlaim (single-repo change)`

## How the 5 steps are now fully automatable

| Step | Script | Result |
|---|---|---|
| 1. Pocket ID OIDC client for Komodo | `wire-pocketid-pangolin-komodo.sh` | client_id + secret in .env + local Infisical |
| 2. Komodo OIDC config | `wire-pocketid-pangolin-komodo.sh` | Komodo auth via PocketID passkey |
| 3. Pangolin IdP for PocketID | `wire-pocketid-pangolin-komodo.sh` | Pangolin dashboard sees PocketID IdP |
| 4. Bind PocketID IdP to Resources | `wire-pocketid-resource-idp.sh` | Every Resource (mlflow, langfuse, etc.) can auth via PocketID |
| 5. Komodo+Periphery bootstrap | `bootstrap-komodo-periphery.sh` | Periphery self-registers with Pangolin, Komodo gets Periphery wire |

Plus:
| Operator workflow | Script | Result |
|---|---|---|
| Non-technical onboarding | `onboard-pocketid.sh` | Guided TUI asks 3 questions, validates, persists to .env, optionally runs the wire script |
| 90-day rotation | `rotate-pocketid-secrets.sh` (cron) | Fetches fresh secret, mints fresh Pangolin API key, updates .env |

## Spec delta

See `specs/infrastructure-stacks/spec.md` for 2 ADDED Requirements.

## Open follow-up issues

- [ ] Add a wire-pocketid-pangolin-resource-idp.sh --komodo flag to also
  bind PocketID to a Komodo Resource (not just Pangolin)
- [ ] Add per-Periphery onboarding token (right now bootstrap uses Pocket ID
  but the Komodo side needs a separate API key)
- [ ] Add a guard for "Pangolin Resource already has PocketID bound" to
  prevent duplicate IdP bindings
- [ ] Add monitoring/alerting for failed rotations (pagerduty/webhook)
