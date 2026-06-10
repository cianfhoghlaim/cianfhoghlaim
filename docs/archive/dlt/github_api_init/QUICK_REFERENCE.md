# github_api_init: Quick Reference Guide

## File Manifest

| File | Purpose | Key Content |
|------|---------|------------|
| `github-docs.yaml` | API specification | 32 GitHub REST endpoints in declarative YAML format |
| `github_pipeline.py` | Entry point | Minimal template showing dlt pattern |
| `.dlt/config.toml` | Runtime config | Logging level, telemetry settings |
| `.dlt/secrets.toml` | Credentials | Template for GitHub API token |
| `.dlt/.sources` | Version tracking | Engine version, git SHAs, checksums |
| `requirements.txt` | Dependencies | `dlt[duckdb]>=1.18.2` |
| `dlt.yaml` | Project config | Empty project marker |
| `CLAUDE.md` / `AGENT.md` | AI guidelines | Comprehensive REST API coding rules |

## Configuration Structure (YAML)

```yaml
source_name: github
version: 1.8.30
authentication_required: true

# Global HTTP client settings
client:
  base_url: https://api.github.com
  auth:
    type: apikey
    location: header
    header_name: Authorization
  headers:
    Accept: application/vnd.github.v3+json
  paginator:
    type: page                  # page, offset, cursor, json_link, header_link, single_page
    page_size_param: per_page
    default_page_size: 30

# Individual endpoints
resources:
  - name: resource_name
    endpoint:
      path: /path/{param1}/{param2}
      method: GET
      data_selector: results   # JSONPath to extract data
      params:
        filter_param: value
      paginator:               # Override client paginator if needed
        type: cursor
        cursor_path: pagination.next
        cursor_param: after
      incremental:             # For incremental loading
        cursor_path: updated_at
        start_param: since
        initial_value: "2023-01-01T00:00:00Z"

# Reference sections
auth_info:
  mentioned_objects:
    - PersonalAccessToken
    - OAuthApp

errors:
  - 401 Unauthorized: Recheck auth
  - 404 Not Found: Validate parameters
```

## Pagination Types Quick Reference

```yaml
# Page-based (like GitHub uses)
paginator:
  type: page
  page_param: page
  limit_param: per_page
  total_path: total_pages

# Offset-based
paginator:
  type: offset
  offset_param: offset
  limit_param: limit
  total_path: total

# Cursor-based
paginator:
  type: cursor
  cursor_path: pagination.next_cursor
  cursor_param: after

# Link header-based (GitHub alternative)
paginator:
  type: header_link
  links_next_key: next

# Response contains next URL
paginator:
  type: json_link
  next_url_path: links.next

# No pagination
paginator:
  type: single_page
```

## Authentication Types

```yaml
# API Key in header
auth:
  type: apikey
  name: X-API-Key
  api_key: ...              # from dlt.secrets
  location: header

# API Key in query
auth:
  type: apikey
  name: api_token
  api_key: ...
  location: query

# Bearer token
auth:
  type: bearer
  token: ...                # from dlt.secrets

# Basic auth
auth:
  type: basic
  username: ...
  password: ...

# OAuth2
auth:
  type: oauth2
  token_url: https://auth.example.com/token
  client_id: ...
  client_secret: ...
  scopes:
    - read
    - write
```

## Data Selector (JSONPath) Examples

```yaml
# Flat response array
data_selector: .              # or leave empty

# Nested in data field
data_selector: data

# Nested deeper
data_selector: data.results

# Nested with wildcard
data_selector: data.*

# Multiple levels
data_selector: response.payload.items

# Selecting specific fields
data_selector: data.{id,name,created_at}
```

## Pipeline Execution Pattern

```python
import dlt
from dlt.sources.rest_api import rest_api_resources, RESTAPIConfig

@dlt.source
def my_api_source(api_token=dlt.secrets.value):
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.example.com",
            "auth": {
                "type": "bearer",
                "token": api_token,
            }
        },
        "resources": [
            # Add resource definitions here
        ]
    }
    
    yield from rest_api_resources(config)

# Run the pipeline
pipeline = dlt.pipeline(
    pipeline_name='my_pipeline',
    destination='duckdb',
    dataset_name='my_data',
    progress="log"
)

# Load data
load_info = pipeline.run(my_api_source())
print(load_info)
```

## Secrets Configuration

`.dlt/secrets.toml`:
```toml
# Root level (used as default)
access_token = "your_actual_token_here"

# Source-specific
[sources.github]
access_token = "your_token"

# Per-resource credentials (advanced)
[sources.resource_name]
api_key = "key_value"
api_secret = "secret_value"
```

Reference in Python:
```python
@dlt.source
def source_func(token=dlt.secrets.value):
    # Token automatically injected from secrets.toml

@dlt.source
def source_func(token=dlt.secrets["my_api_token"]):
    # Specific named secret

@dlt.source
def source_func(token=dlt.secrets["sources.github"]["access_token"]):
    # Source-specific secret
```

## 32 GitHub API Endpoints Included

### Organization/User (4)
- organizations, users, teams, repositories

### Repository Metadata (6)
- assignees, branches, collaborator, issue_labels, tags, workflows

### Issues (6)
- issues, issue_events, issue_milestones, comments, issue_comment_reactions, issue_reactions

### Pull Requests (6)
- pull_requests, pull_request_commits, pull_request_stats, review_comments, pull_request_comment_reactions, reviews

### Commits (3)
- commits, commit_comments, commit_comment_reactions

### Releases & Deployments (2)
- releases, deployments

### Events & Activity (2)
- events, stargazers

### Projects (3)
- projects, project_columns, project_cards

### CI/CD (2)
- workflow_runs, workflow_jobs

## Incremental Loading Setup

For timestamp-based incremental:
```yaml
resources:
  - name: issues
    endpoint:
      path: /repos/{owner}/{repo}/issues
      params:
        since: "{incremental.start_value}"
      incremental:
        cursor_path: updated_at      # Field to track state
        start_param: since           # Query param name
        initial_value: "2023-01-01T00:00:00Z"
```

For ID-based incremental:
```yaml
resources:
  - name: items
    endpoint:
      path: /items
      params:
        min_id: "{incremental.start_value}"
      incremental:
        cursor_path: id              # Track item IDs
        start_param: min_id
        initial_value: 0
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check token in secrets.toml, verify scopes |
| 404 Not Found | Validate path parameters ({owner}, {repo}, etc.) |
| Empty data | Check data_selector JSONPath, verify API response |
| Pagination not working | Verify paginator type matches API behavior |
| Rate limit exceeded | Reduce page_size or add delays (dlt handles with retries) |
| Incremental not tracking | Ensure cursor_path matches response field names |

## Best Practices

1. **Start with github-docs.yaml** - Define all endpoints there
2. **Use data_selector** - Unwrap nested response data declaratively
3. **Respect rate limits** - Configure appropriate page_size
4. **Secure secrets** - Never hardcode tokens, always use .dlt/secrets.toml
5. **Test incrementally** - Start with small date ranges
6. **Document parameters** - Add comments to complex endpoint configs
7. **Validate JSONPath** - Test data_selector with sample responses
8. **Plan primary keys** - Know which fields uniquely identify records
9. **Consider write disposition** - Replace vs. Append vs. Merge
10. **Monitor schema changes** - API changes may require config updates

## Resource Defaults Example

```yaml
resource_defaults:
  primary_key: id                    # Default primary key
  write_disposition: merge           # Default write mode
  endpoint:
    params:
      limit: 100                    # Default page size
      
resources:
  - name: resource_using_defaults
    endpoint:
      path: /path
      # Inherits primary_key, write_disposition, params.limit from defaults
  
  - name: resource_override_primary_key
    endpoint:
      path: /path2
      # Can override: specify own primary_key in resource if needed
```

## Integration with Rest of Stack

### With dlt CLI
```bash
dlt init github duckdb           # Creates this structure
dlt run github_pipeline.py       # Executes the pipeline
dlt pipeline github show         # Inspect loaded data
```

### With Destinations
```python
pipeline = dlt.pipeline(
    pipeline_name='github',
    destination='duckdb',        # Can be postgres, bigquery, snowflake, etc.
    dataset_name='github_data'
)
```

### With Orchestration (Dagster example)
```python
from dagster import asset

@asset
def github_issues(context) -> None:
    pipeline = dlt.pipeline(...)
    pipeline.run(github_source(token))
```

## Files to Modify for Custom API

1. **github-docs.yaml** - Replace GitHub endpoints with your API's endpoints
2. **requirements.txt** - Keep as-is or add dlt extras for your destination
3. **dlt.yaml** - Rename pipeline/source names if desired
4. **.dlt/secrets.toml** - Replace with your API credentials
5. **github_pipeline.py** - Update source function name and config loading
6. **CLAUDE.md** - Reference as guide when building config

## Verification Checklist

Before running:
- [ ] Base URL is correct
- [ ] Authentication type and location verified
- [ ] All endpoint paths checked against API docs
- [ ] Data selector JSONPath tested with sample responses
- [ ] Pagination type matches API behavior
- [ ] Secrets configured in .dlt/secrets.toml
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] API token/credentials set and not expired
- [ ] Rate limits understood and page_size configured appropriately
- [ ] Output destination (duckdb) is available/writable

## Resources

- **dlt Documentation:** https://dlthub.com/docs
- **REST API Source Guide:** https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api
- **GitHub API Docs:** https://docs.github.com/en/rest
- **CLAUDE.md in this directory:** Comprehensive AI coding guidelines
