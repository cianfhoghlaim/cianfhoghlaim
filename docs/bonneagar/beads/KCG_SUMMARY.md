# Beads — KCG Summary

## What It Is
Beads is an open-source issue tracking and project management CLI tool by Steve Yegge. It stores issues as JSONL files in a `.beads/` directory, enabling Git-based issue management with branching, merging, and offline-first workflows.

## Why This Matters for Kings' College Galway
The project uses Beads for local issue tracking alongside Forgejo Issues. The JSONL format integrates with Git workflows — issues are version-controlled alongside code. This is useful for tracking documentation consolidation tasks, infrastructure bugs, and pipeline improvement items that don't need to be in the shared Forgejo instance.

## Key Patterns
- **Git-native issues**: `.beads/beads.jsonl` stored in the repo; issues are commits
- **Offline-first**: All issue operations work without network access
- **CLI-driven**: `bd list`, `bd show`, `bd comment` — no web UI required
- **Deduplication**: Built-in duplicate detection and merging

## Source Files
Full Go source code removed (2026-06-05). Available at <https://github.com/steveyegge/beads>.
