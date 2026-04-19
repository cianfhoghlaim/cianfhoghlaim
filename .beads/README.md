# Beads - AI-Native Issue Tracking

Welcome to Beads! This repository uses **Beads** for issue tracking - a modern, AI-native tool designed to live directly in your codebase alongside your code.

## What is Beads?

Beads is issue tracking that lives in your repo, making it perfect for AI coding agents and developers who want their issues close to their code. No web UI required - everything works through the CLI and integrates seamlessly with git.

**Learn more:** [github.com/steveyegge/beads](https://github.com/steveyegge/beads)

## Quick Start

### Essential Commands

```bash
# Create new issues
bd create "Add user authentication"

# View all issues
bd list

# View issue details
bd show <issue-id>

# Update issue status
bd update <issue-id> --status in_progress
bd update <issue-id> --status done

# Sync with git remote
bd sync
```

### Working with Issues

Issues in Beads are:
- **Git-native**: Stored in `.beads/issues.jsonl` and synced like code
- **AI-friendly**: CLI-first design works perfectly with AI coding agents
- **Branch-aware**: Issues can follow your branch workflow
- **Always in sync**: Auto-syncs with your commits

## Why Beads?

✨ **AI-Native Design**
- Built specifically for AI-assisted development workflows
- CLI-first interface works seamlessly with AI coding agents
- No context switching to web UIs

🚀 **Developer Focused**
- Issues live in your repo, right next to your code
- Works offline, syncs when you push
- Fast, lightweight, and stays out of your way

🔧 **Git Integration**
- Automatic sync with git commits
- Branch-aware issue tracking
- Intelligent JSONL merge resolution

## Get Started with Beads

Try Beads in your own projects:

```bash
# Install Beads
curl -sSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash

# Initialize in your repo
bd init

# Create your first issue
bd create "Try out Beads"
```

## Using Beads with AI Agents (Gemini CLI, Copilot, Roo Code)

Beads is designed to be the central nervous system for AI-assisted development in this repository.

### For Gemini CLI & Roo Code
1. **MCP & Tools Setup**: Ensure your agent has access to terminal execution. For Roo Code, verify `.roo/mcp.json` is active.
2. **Task Discovery**: Begin sessions by running `bd list` or `bd ready` to find open issues.
3. **Session Management**: Always run `bd update <id> --status in_progress` when starting a task.
4. **Handoff Protocol**: Before concluding a session, you MUST follow the instructions in the `AGENTS.md` file located at the repository root. This includes running `bd sync` and pushing changes to ensure work isn't stranded locally.

### For GitHub Copilot
1. **Agent Skills Integration**: We leverage the Agent Skills standard (`.skills/`). You can instruct Copilot to "use the beads skill" or reference specific instructions in `.skills/` to teach Copilot how to interact with the `bd` CLI during a chat session.
2. **Commit Generation**: Copilot can read the `.beads/issues.jsonl` file to understand the current context and generate highly accurate commit messages based on the active issue.

## Learn More

- **Documentation**: [github.com/steveyegge/beads/docs](https://github.com/steveyegge/beads/tree/main/docs)
- **Quick Start Guide**: Run `bd quickstart`
- **Examples**: [github.com/steveyegge/beads/examples](https://github.com/steveyegge/beads/tree/main/examples)

---

*Beads: Issue tracking that moves at the speed of thought* ⚡
