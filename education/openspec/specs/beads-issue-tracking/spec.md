# Beads Issue Tracking Capability

## Overview

Distributed issue tracker designed for AI agent workflows with CLI-first interface and Git-native storage.

| Feature | Description |
|---------|-------------|
| Git-Native | Issues stored in `.beads/issues.jsonl` |
| Conflict-Free | Automatic JSONL merge resolution |
| CLI-First | `bd` command for all operations |
| MCP Integration | AI agent access via MCP server |

## Requirements

### Requirement: Issue Creation

The system SHALL create and manage issues with unique identifiers.

#### Scenario: Create Issue
- **GIVEN** issue title and optional type
- **WHEN** `bd create "title"` is executed
- **THEN** issue is created with unique ID (e.g., cf-a1b2c3)

#### Scenario: Create Epic
- **GIVEN** epic title
- **WHEN** `bd create --type=epic "title"` is executed
- **THEN** epic is created with child issue support

### Requirement: Issue Status Tracking

The system SHALL track issue status through lifecycle states.

#### Scenario: Update Status
- **GIVEN** issue ID and new status
- **WHEN** `bd update <id> --status <status>` is executed
- **THEN** status changes (open, in_progress, blocked, closed)

### Requirement: Git Synchronization

The system SHALL synchronize issues with Git repository.

#### Scenario: Sync Issues
- **WHEN** `bd sync` is executed
- **THEN** issues sync with remote repository

#### Scenario: Auto-Sync
- **GIVEN** auto_sync is enabled in config
- **WHEN** sync_interval elapses
- **THEN** issues sync automatically

### Requirement: Dependency Management

The system SHALL track issue dependencies.

#### Scenario: Add Dependency
- **GIVEN** issue ID and dependency ID
- **WHEN** dependency is added
- **THEN** relationship types are tracked (blocks, related, parent-child, discovered-from)

### Requirement: MCP Integration

The system SHALL provide MCP server for AI agent access.

#### Scenario: MCP Tools
- **GIVEN** MCP server is running (`beads-mcp` in .mcp.json)
- **WHEN** AI agent connects
- **THEN** issue CRUD operations are available

## Storage

```
.beads/
├── config.yaml      # Configuration (prefix, auto_sync, agent)
├── issues.jsonl     # Issue database
└── .gitignore       # Git ignore patterns
```

## API Reference (CLI)

| Command | Parameters | Description |
|---------|------------|-------------|
| `bd create` | title, --type | Create issue |
| `bd list` | --status, --type | List issues |
| `bd show` | id | Show issue details |
| `bd update` | id, --status, --title | Update issue |
| `bd sync` | - | Sync with Git |
| `bd comment` | id, message | Add comment |

## Implementation References

| Component | Path |
|-----------|------|
| Go Module | `bonneagar/dagger/beads/` |
| Config | `.beads/config.yaml` |

## Related Specs

- [dagger-gitops](../dagger-gitops/spec.md) - GitOps integration
