# dlt github_api_init Directory Analysis

## Overview
The `github_api_init` directory represents dlt's **REST API-first approach** to creating API sources. This is distinct from the `github_source_init` (verified source) approach and demonstrates dlt's best practices for building declarative, configuration-driven API connectors using the REST API framework.

## Directory Structure

```
github_api_init/
├── .dlt/                          # dlt configuration directory
│   ├── config.toml               # Runtime configuration
│   ├── secrets.toml              # API credentials (templated)
│   └── .sources                  # Source tracking metadata
├── github-docs.yaml              # REST API endpoint definitions (KEY)
├── github_pipeline.py            # Pipeline entry point (minimal template)
├── requirements.txt              # Python dependencies
├── dlt.yaml                      # Empty dlt project config
├── .gitignore                    # Standard dlt gitignore
├── CLAUDE.md                     # AI coding guidelines for REST APIs
└── AGENT.md                      # (same as CLAUDE.md)
```

## Key Files Explanation

### 1. github-docs.yaml - The Core API Specification

This file is the **central artifact** that declares all GitHub API endpoints in a declarative YAML format. It follows a structured pattern:

#### Structure:

```yaml
# Source Metadata
source_name: github
version: 1.8.30
authentication_required: true
api_types_available:
  - REST

# Client Configuration (Global)
client:
  base_url: https://api.github.com
  auth:
    type: apikey
    location: header
    header_name: Authorization
  headers:
    Accept: application/vnd.github.v3+json
  paginator:
    type: page
    page_size_param: per_page
    default_page_size: 30

# Resources (Endpoint Definitions)
resources:
  - name: assignees
    endpoint:
      path: /repos/{owner}/{repo}/assignees
      method: GET
      data_selector: 
      params: {}
  
  # ... 32 more endpoints ...

# Auth Details for Validation
auth_info:
  mentioned_objects:
    - PersonalAccessToken
    - OAuthApp

# Error Handling Reference
errors:
  - REQUEST_LIMIT_EXCEEDED: Throttle API calls or reduce frequency
  - 401 Unauthorized: Recheck OAuth scopes or token expiration
  - 404 Not Found: Validate repository or organization names
```

#### Endpoints Defined (32 total):

**Organization/User Level:**
- `organizations` - GET /user/orgs
- `users` - GET /users
- `teams` - GET /orgs/{org}/teams
- `repositories` - GET /users/{username}/repos

**Repository Metadata:**
- `assignees` - GET /repos/{owner}/{repo}/assignees
- `branches` - GET /repos/{owner}/{repo}/branches
- `collaborator` - GET /repos/{owner}/{repo}/collaborators
- `issue_labels` - GET /repos/{owner}/{repo}/labels
- `tags` - GET /repos/{owner}/{repo}/tags
- `workflows` - GET /repos/{owner}/{repo}/actions/workflows

**Issues & Tracking:**
- `issues` - GET /repos/{owner}/{repo}/issues
- `issue_events` - GET /repos/{owner}/{repo}/issues/events
- `issue_milestones` - GET /repos/{owner}/{repo}/milestones
- `comments` - GET /repos/{owner}/{repo}/issues/comments
- `issue_comment_reactions` - GET /repos/{owner}/{repo}/issues/comments/{comment_id}/reactions
- `issue_reactions` - GET /repos/{owner}/{repo}/issues/{issue_number}/reactions

**Pull Requests:**
- `pull_requests` - GET /repos/{owner}/{repo}/pulls
- `pull_request_commits` - GET /repos/{owner}/{repo}/pulls/{pull_number}/commits
- `pull_request_stats` - GET /repos/{owner}/{repo}/pulls/{pull_number}/stats
- `review_comments` - GET /repos/{owner}/{repo}/pulls/{pull_number}/comments
- `pull_request_comment_reactions` - GET /repos/{owner}/{repo}/pulls/{pull_number}/comments/{comment_id}/reactions
- `reviews` - GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews

**Commits & Code:**
- `commits` - GET /repos/{owner}/{repo}/commits
- `commit_comments` - GET /repos/{owner}/{repo}/commits/{commit_sha}/comments
- `commit_comment_reactions` - GET /repos/{owner}/{repo}/comments/{comment_id}/reactions

**Releases & Deployments:**
- `releases` - GET /repos/{owner}/{repo}/releases
- `deployments` - GET /repos/{owner}/{repo}/deployments

**Events & Activity:**
- `events` - GET /repos/{owner}/{repo}/events
- `stargazers` - GET /repos/{owner}/{repo}/stargazers

**Projects:**
- `projects` - GET /repos/{owner}/{repo}/projects
- `project_columns` - GET /projects/{project_id}/columns
- `project_cards` - GET /projects/{project_id}/cards

**CI/CD:**
- `workflow_runs` - GET /repos/{owner}/{repo}/actions/runs
- `workflow_jobs` - GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs

### 2. github_pipeline.py - Template Pipeline Implementation

This is a **minimal template** showing the dlt pattern:

```python
import dlt
from dlt.sources.rest_api import (
    RESTAPIConfig,
    rest_api_resources,
)

@dlt.source
def github_source(access_token=dlt.secrets.value):
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://example.com/v1/",
            "auth": {
                "type": "bearer",
                "token": access_token,
            },
        },
        "resources": [
            # TODO: add resource definitions here
        ],
    }

    yield from rest_api_resources(config)

def get_data() -> None:
    pipeline = dlt.pipeline(
        pipeline_name='github_pipeline',
        destination='duckdb',
        dataset_name='github_data',
    )

    access_token = "my_access_token"
    load_info = pipeline.run(github_source(access_token))
    print(load_info)

if __name__ == "__main__":
    get_data()
```

**Key Patterns:**
- Uses `@dlt.source` decorator for dependency injection
- Uses `rest_api_resources()` to process config
- Passes secrets via function parameters
- Returns generator from decorator
- DuckDB as default destination

### 3. .dlt/ Configuration Files

#### .dlt/config.toml
```toml
[runtime]
log_level="WARNING"
dlthub_telemetry = true
```

**Purpose:** Runtime configuration for dlt behavior (logging, telemetry).

#### .dlt/secrets.toml
```toml
access_token = "access_token"        # Root level

[sources.github]
access_token = "<configure me>"      # Source-specific
```

**Purpose:** Credentials management with templated placeholders.

#### .dlt/.sources
YAML file tracking source metadata and integrity:
- Engine version
- Git commit SHAs
- File checksums
- dlt version constraints

**Purpose:** Source versioning and state management in dlt registry.

### 4. requirements.txt
```
dlt[duckdb]>=1.18.2
```

Minimal dependencies: dlt with DuckDB adapter.

### 5. CLAUDE.md - AI Coding Guidelines

Comprehensive guidance for AI assistants including:
- Prerequisites for writing REST API sources
- Authentication methods (API Key, Bearer, OAuth2, Basic)
- Pagination types (json_link, header_link, offset, page_number, cursor, single_page)
- Data selection with `data_selector` (JSONPath extraction)
- Incremental loading configuration
- Parameter extraction guide from API docs
- Verification checklist
- dlt REST API pagination configuration details

## Architectural Differences: API Init vs. Source Init

### github_api_init (REST API Approach)
- **Configuration-driven:** YAML file defines endpoints
- **Declarative:** Uses `RESTAPIConfig` dictionary
- **Minimal code:** Rest API framework handles all plumbing
- **Generated:** Created by `dlt init` command
- **Use case:** Any REST API without specialized logic
- **Flexibility:** Easy to add/remove endpoints by modifying YAML
- **Pagination:** Handled transparently via config
- **Best for:** Quick API source generation, MCP integration, OpenAPI-driven development

### github_source_init (Verified Source)
- **Code-driven:** Python functions with custom logic
- **Imperative:** Uses decorators and generators
- **Advanced features:** GraphQL support, complex incremental logic
- **Maintained:** Official dlt library sources
- **Use case:** Complex APIs needing custom handling
- **Flexibility:** Full Python power for edge cases
- **Pagination:** Manual with helper functions
- **Best for:** Production sources, complex APIs, official library contributions

## Best Practices Reflected

### 1. Configuration Over Code
```yaml
# Clean, readable endpoint definition
- name: issues
  endpoint:
    path: /repos/{owner}/{repo}/issues
    method: GET
    data_selector: 
    params: {}
```

### 2. Authentication Security
- Credentials never hardcoded
- Uses `dlt.secrets` pattern
- Separate secrets.toml template
- Secure credential injection via decorators

### 3. Pagination Standardization
```yaml
paginator:
  type: page
  page_size_param: per_page
  default_page_size: 30
```
Single paginator config handles all endpoints using same strategy.

### 4. Data Extraction
`data_selector` field uses JSONPath to unwrap nested responses - transparent to user.

### 5. State Management
`.dlt/.sources` tracks versions, checksums, git history for reproducibility.

### 6. Documentation
Every file has clear purpose:
- CLAUDE.md/AGENT.md: AI coding rules
- github-docs.yaml: API specification
- requirements.txt: Dependencies
- .dlt/config.toml: Runtime settings
- .dlt/secrets.toml: Credentials template

## Key REST API Framework Features

### Configuration Structure
```python
RESTAPIConfig = {
    "client": {           # Global HTTP client settings
        "base_url": "...",
        "auth": {...},
        "headers": {...},
        "paginator": {...}
    },
    "resource_defaults": {  # Apply to all resources
        "primary_key": "id",
        "write_disposition": "merge",
        "endpoint": {"params": {...}}
    },
    "resources": [        # Individual endpoint definitions
        {
            "name": "resource_name",
            "endpoint": {
                "path": "/endpoint",
                "method": "GET",
                "data_selector": "...",
                "params": {...},
                "paginator": {...},  # Override client paginator
                "incremental": {...}
            }
        }
    ]
}
```

### Pagination Types by Strategy

| Type | Use Case | Config Key |
|------|----------|-----------|
| `json_link` | Response contains next URL | `next_url_path` |
| `header_link` | Link header contains next URL | `links_next_key` |
| `offset` | Query params: offset + limit | `offset_param`, `limit_param` |
| `page_number` | Query params: page + limit | `page_param`, `limit_param` |
| `cursor` | Response contains cursor token | `cursor_path`, `cursor_param` |
| `single_page` | No pagination | (none) |

## How to Use This Template

1. **Start with github-docs.yaml** - Extract endpoints from API docs
2. **Configure client settings** - Base URL, auth type, headers, paginator
3. **Define resources** - One per endpoint with path, method, params, data_selector
4. **Add to github_pipeline.py** - Reference github-docs.yaml in config
5. **Set secrets** - Fill .dlt/secrets.toml with actual credentials
6. **Run** - Execute pipeline.run(github_source(token))

## Relationship to OpenAPI/Swagger

The github-docs.yaml structure mirrors OpenAPI concepts:
- `client.base_url` = OpenAPI server URL
- `client.auth` = OpenAPI securitySchemes
- `resources[].endpoint.path` = OpenAPI paths
- `resources[].endpoint.method` = OpenAPI operations
- `resources[].endpoint.params` = OpenAPI parameters
- Pagination = OpenAPI extension patterns

This enables **automatic source generation** from OpenAPI specs.

## Integration Points

### With dlt CLI
```bash
dlt init github duckdb  # Creates this structure
```

### With MCP (Model Context Protocol)
The github-docs.yaml format is suitable for MCP AI-to-AI communication.

### With Dagster
Outputs can be wrapped as Dagster assets for orchestration.

### With LLMs/AI
Configuration-driven approach enables AI to read/modify APIs without code generation.

## Summary

`github_api_init` represents dlt's **best practice for REST API sources**: 
- Declarative endpoint specification
- Security by design
- Minimal code boilerplate
- Framework handles pagination/errors
- Ready for production use
- AI-friendly configuration format
