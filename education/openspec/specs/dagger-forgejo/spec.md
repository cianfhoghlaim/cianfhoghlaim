# Forgejo API Automation Capability

## Overview

Programmatic access to Forgejo REST API for user management, repository management, webhooks, Actions secrets, and runner registration.

| Feature | Description |
|---------|-------------|
| User Management | Create users, generate tokens |
| Repository | Collaborator permissions |
| Webhooks | Event-based triggers |
| Actions | Secrets and runner management |

## Requirements

### Requirement: User Management

The system SHALL manage Forgejo users programmatically.

#### Scenario: Create User
- **GIVEN** username, email, and password
- **WHEN** `createUser()` is executed
- **THEN** user is created in Forgejo

#### Scenario: Create Access Token
- **GIVEN** username, token name, and scopes
- **WHEN** `createAccessToken()` is executed
- **THEN** token is created with specified permissions

### Requirement: Repository Management

The system SHALL manage repository collaborators.

#### Scenario: Add Collaborator
- **GIVEN** owner, repo, username, and permission
- **WHEN** `addCollaborator()` is executed
- **THEN** user is added with specified permission

### Requirement: Webhook Configuration

The system SHALL manage repository webhooks.

#### Scenario: Create Webhook
- **GIVEN** owner, repo, target URL, secret, and events
- **WHEN** `createWebhook()` is executed
- **THEN** webhook is configured for specified events

#### Scenario: List Webhooks
- **GIVEN** owner and repo
- **WHEN** `listWebhooks()` is executed
- **THEN** all webhooks are returned

### Requirement: Actions Secrets

The system SHALL manage GitHub Actions secrets.

#### Scenario: Set Secret
- **GIVEN** owner, repo, secret name, and value
- **WHEN** `setActionsSecret()` is executed
- **THEN** secret is stored encrypted

### Requirement: Runner Management

The system SHALL manage Forgejo runners.

#### Scenario: Get Registration Token
- **WHEN** `getRunnerRegistrationToken()` is executed
- **THEN** admin registration token is returned

#### Scenario: Register Runner
- **GIVEN** runner name, labels, and registration token
- **WHEN** `registerRunner()` is executed
- **THEN** runner container is configured

## API Reference

| Function | Parameters | Returns |
|----------|------------|---------|
| `createUser()` | username, email, password, mustChangePassword | string |
| `createAccessToken()` | username, tokenName, scopes[] | string |
| `addCollaborator()` | owner, repo, username, permission | string |
| `createWebhook()` | owner, repo, targetUrl, webhookSecret, events[], branchFilter | string |
| `listWebhooks()` | owner, repo | string |
| `setActionsSecret()` | owner, repo, secretName, secretValue | string |
| `listActionsSecrets()` | owner, repo | string |
| `getRunnerRegistrationToken()` | - | string |
| `listRunners()` | - | string |
| `registerRunner()` | runnerName, labels[], registrationToken | Container |
| `health()` | - | string |
| `getCurrentUser()` | - | string |

## Implementation References

| Component | Path |
|-----------|------|
| Main Module | `bonneagar/dagger/src/forgejo.ts` |

## Related Specs

- [dagger-gitops](../dagger-gitops/spec.md) - GitOps pipeline
