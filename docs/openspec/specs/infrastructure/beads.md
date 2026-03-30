# Beads Issue Tracker

## Overview
Beads (`bd`) is an issue tracker designed for AI-supervised coding workflows. It serves as the primary task management system for the Cianfhoghlaim project, replacing external tools and Markdown TODO lists.

## Core Capabilities
- **Issue Tracking**: Manage bugs, features, tasks, epics, and chores.
- **Dependency Management**: Track blocking relationships and hierarchical structures (epics/tasks).
- **Auto-Sync**: Automatically synchronizes database state with JSONL files for git version control.
- **Agent Integration**: Optimized for AI agents with JSON output, ready work queues, and context minimization.
- **MCP Server**: Provides Model Context Protocol integration for clients like Claude Desktop.

## Usage
- **CLI**: Primary interface (`bd`) for creation, updates, and queries.
- **MCP**: `beads-mcp` for integration with AI assistants.
- **Git Hooks**: Ensures synchronization between local DB and git.

## Key Constraints
- All work items MUST be tracked in Beads.
- Agents MUST check `bd ready` before starting new tasks.
- Issues discovered during work MUST be linked via `discovered-from`.
