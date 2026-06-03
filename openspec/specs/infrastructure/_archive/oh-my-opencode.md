# Oh My OpenCode

## Overview
Oh My OpenCode is an agent harness and orchestration framework for OpenCode. It enhances the capabilities of AI agents by providing specialized sub-agents, improved tools, and context management.

## Core Capabilities
- **Agent Orchestration**: Manages specialized agents (Sisyphus, Oracle, Librarian, etc.) for complex tasks.
- **Tool Enhancement**: Provides LSP integration, AST-based search/replace, and documentation lookups.
- **Context Management**: Auto-injects project context (AGENTS.md) and manages token usage.
- **Compatibility**: Offers a Claude Code compatibility layer for seamless integration.

## Usage
- **Plugin**: Integrated into OpenCode via configuration.
- **Commands**: Slash commands and automated hooks.

## Key Constraints
- Configuration via `oh-my-opencode.json`.
- Respects project-specific rules in `.claude/rules/`.
