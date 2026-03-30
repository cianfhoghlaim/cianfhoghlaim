# ChunkHound Code Search Capability

## Overview

Semantic code search with MVCC support, multi-language parsing, and MCP integration for AI-assisted development.

| Feature | Description |
|---------|-------------|
| Semantic Search | Vector similarity via LanceDB |
| Multi-Language | 29 languages via Tree-sitter |
| MVCC Safety | Multi-process coordination |
| MCP Server | AI agent integration |

## Requirements

### Requirement: Codebase Indexing

The system SHALL index codebases for semantic search with MVCC-safe storage.

#### Scenario: Index Repository
- **GIVEN** repository path and config
- **WHEN** indexing is executed
- **THEN** code chunks are embedded and stored in LanceDB

#### Scenario: Incremental Update
- **GIVEN** existing index and changed files
- **WHEN** index is updated
- **THEN** only changed chunks are reprocessed

### Requirement: Semantic Search

The system SHALL search code semantically using natural language queries.

#### Scenario: Natural Language Query
- **GIVEN** natural language query
- **WHEN** `search_semantic` is executed
- **THEN** relevant code chunks are returned with context

#### Scenario: Regex Search
- **GIVEN** regex pattern
- **WHEN** `search_regex` is executed
- **THEN** matching files and locations are returned

### Requirement: Multi-Language Support

The system SHALL parse multiple programming languages using cAST algorithm.

#### Scenario: Parse TypeScript
- **GIVEN** TypeScript source files
- **WHEN** parsed
- **THEN** functions, classes, and interfaces are extracted

#### Scenario: Parse Python
- **GIVEN** Python source files
- **WHEN** parsed
- **THEN** functions, classes, and modules are extracted

### Requirement: MCP Server

The system SHALL provide MCP server for AI agent integration.

#### Scenario: Stdio Mode
- **GIVEN** `chunkhound mcp stdio` is running
- **WHEN** AI agent connects
- **THEN** search and explore tools are available

#### Scenario: HTTP Mode
- **GIVEN** `chunkhound mcp http --port 5173` is running
- **WHEN** AI agent connects via SSE
- **THEN** remote search is available

### Requirement: Multi-Hop Analysis

The system SHALL support deep code exploration.

#### Scenario: Code Research
- **GIVEN** research question
- **WHEN** `code_research` is executed
- **THEN** multi-hop analysis traces code paths

## Supported Languages

TypeScript, JavaScript, Python, Go, Rust, Java, Kotlin, Ruby, C, C++, C#, Dart, Haskell, Groovy, HCL, Bash, JSON, Markdown, and 10+ more.

## API Reference (MCP Tools)

| Tool | Parameters | Description |
|------|------------|-------------|
| `search_semantic` | query, limit | Vector similarity search |
| `search_regex` | pattern, limit | Regex pattern matching |
| `get_file_chunks` | filePath | Retrieve indexed chunks |
| `list_files` | pattern | Codebase navigation |
| `code_research` | question | Deep multi-hop analysis |

## Configuration

```json
{
  "include": ["**/*.ts", "**/*.py"],
  "exclude": ["node_modules", ".git"],
  "embedding": {
    "provider": "openai",
    "model": "text-embedding-3-large"
  }
}
```

## Implementation References

| Component | Path |
|-----------|------|
| Python Module | `bonneagar/dagger/chunkhound/` |
| Config | `.chunkhound.json` |

## Constraints

- **LanceDB:** MVCC-safe with automatic conflict resolution
- **Embedding Batching:** Minimum 100 texts per API call
- **MCP Stdout:** No logging allowed (JSON-RPC protocol)
