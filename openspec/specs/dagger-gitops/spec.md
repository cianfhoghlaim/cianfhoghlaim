# GitOps Pipeline Capability

## Overview

8-step GitOps pipeline orchestration connecting Forgejo and Komodo for automated infrastructure deployment.

| Feature | Description |
|---------|-------------|
| User Management | Create renovate-bot user with scoped tokens |
| Webhook Configuration | Forgejo to Komodo event triggers |
| Runner Registration | Actions runner deployment |
| Resource Sync | Git-to-infrastructure synchronization |

## Requirements

### Requirement: Complete GitOps Setup

The system SHALL orchestrate the full GitOps pipeline setup in 8 steps.

#### Scenario: Full Setup
- **GIVEN** Forgejo and Komodo credentials
- **WHEN** `setupComplete()` is executed
- **THEN** all 8 steps complete:
  1. Create renovate-bot user
  2. Generate access token
  3. Set RENOVATE_TOKEN secret
  4. Configure webhooks
  5. Create Git Provider in Komodo
  6. Deploy forgejo-runner stack
  7. Sync resources
  8. Verify functionality

### Requirement: Partial Setup

The system SHALL support partial pipeline execution for independent setup of components.

#### Scenario: Forgejo-Only Setup
- **GIVEN** Forgejo credentials
- **WHEN** `setupForgejo()` is executed
- **THEN** steps 1-4 complete (user, token, secret, webhook)

#### Scenario: Komodo-Only Setup
- **GIVEN** Komodo credentials and Forgejo token
- **WHEN** `setupKomodo()` is executed
- **THEN** steps 5-7 complete (provider, deploy, sync)

### Requirement: Pipeline Verification

The system SHALL verify GitOps pipeline functionality with comprehensive health checks.

#### Scenario: Health Verification
- **GIVEN** Forgejo and Komodo credentials
- **WHEN** `verify()` is executed
- **THEN** 8 health checks run:
  - Forgejo API health
  - Forgejo Admin Token validity
  - Komodo API health
  - Komodo Version
  - Forgejo Runners online
  - Forgejo Webhooks configured
  - RENOVATE_TOKEN secret exists
  - Komodo Stacks accessible

### Requirement: Runner Registration

The system SHALL register Forgejo runners with appropriate labels.

#### Scenario: Register Runner
- **GIVEN** Forgejo credentials and runner name
- **WHEN** `registerRunner()` is executed
- **THEN** runner is registered with ubuntu-latest label

## API Reference

| Function | Parameters | Returns |
|----------|------------|---------|
| `setupComplete()` | forgejoUrl, forgejoAdminToken, komodoUrl, komodoApiKey, komodoApiSecret, webhookSecret, renovatePassword | string |
| `setupForgejo()` | forgejoUrl, forgejoAdminToken, webhookSecret, renovatePassword | string |
| `setupKomodo()` | komodoUrl, komodoApiKey, komodoApiSecret, forgejoToken | string |
| `verify()` | forgejoUrl, forgejoAdminToken, komodoUrl, komodoApiKey, komodoApiSecret | string |
| `registerRunner()` | forgejoUrl, forgejoAdminToken, runnerName | string |

## Implementation References

| Component | Path |
|-----------|------|
| Main Module | `bonneagar/dagger/src/gitops.ts` |
| Forgejo Client | `bonneagar/dagger/src/forgejo.ts` |
| Komodo Client | `bonneagar/dagger/src/komodo.ts` |

## Related Specs

- [dagger-forgejo](../dagger-forgejo/spec.md) - Forgejo API automation
- [dagger-komodo](../dagger-komodo/spec.md) - Komodo SDK wrapper
- [infrastructure-stacks](../infrastructure-stacks/spec.md) - Deployed stacks
