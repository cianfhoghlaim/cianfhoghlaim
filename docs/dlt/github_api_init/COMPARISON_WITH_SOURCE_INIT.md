# github_api_init vs. github_source_init: Detailed Comparison

## Side-by-Side Architecture

### 1. APPROACH

| Aspect | github_api_init (REST API) | github_source_init (Verified Source) |
|--------|---------------------------|--------------------------------------|
| **Paradigm** | Declarative (Configuration) | Imperative (Code-driven) |
| **Primary Artifact** | `github-docs.yaml` | `__init__.py` |
| **Framework** | `rest_api_resources()` | `@dlt.source` decorator + custom logic |
| **Pagination** | Automatic via config | Manual with helper functions |
| **Customization** | YAML editing | Python coding |
| **Entry Point** | `github_pipeline.py` template | Imported as `dlt_github` module |

### 2. DEPENDENCIES & SETUP

| Aspect | github_api_init | github_source_init |
|--------|-----------------|-------------------|
| **Requirements** | `dlt[duckdb]>=1.18.2` | (uses built-in dlt sources) |
| **Dependencies** | Minimal | Imports helpers, queries, settings modules |
| **Module Structure** | Single pipeline file | Package with submodules |
| **Configuration** | `github-docs.yaml` + `.dlt/` | Built-in verified source |

### 3. CONFIGURATION FILES

#### github_api_init
```
.dlt/
├── config.toml           # Runtime settings (logging, telemetry)
├── secrets.toml          # Template: access_token placeholder
└── .sources              # Source versioning metadata
github-docs.yaml          # ALL endpoints defined here
github_pipeline.py        # Minimal template code
dlt.yaml                  # Empty project config
requirements.txt          # Just dlt[duckdb]
```

#### github_source_init
```
.dlt/
├── config.toml           # Runtime settings
└── secrets.toml          # Template: access_token placeholder
__init__.py               # github_reactions() and github_repo_events() sources
helpers.py                # get_reactions_data(), get_rest_pages(), get_stargazers()
queries.py                # GraphQL queries for reactions source
settings.py               # Configuration constants
README.md                 # Usage documentation
(no github-docs.yaml)     # Endpoints defined in Python code/decorators
```

### 4. ENDPOINT DISCOVERY

#### github_api_init
```yaml
# All endpoints visible in one YAML file
resources:
  - name: issues
    endpoint:
      path: /repos/{owner}/{repo}/issues
      method: GET
      data_selector: 
      params: {}
  
  - name: pull_requests
    endpoint:
      path: /repos/{owner}/{repo}/pulls
      method: GET
```

**Advantages:**
- Single source of truth
- Easy to see all available endpoints
- Non-developers can read/understand structure
- Ideal for OpenAPI spec conversion
- Easy for AI/code generation

#### github_source_init
```python
@dlt.source
def github_reactions(owner: str, name: str, access_token: str = dlt.secrets.value):
    """GraphQL-based issues and PR reactions"""
    return (
        dlt.resource(
            get_reactions_data("issues", ...),
            name="issues",
            write_disposition="replace",
        ),
        ...
    )

@dlt.source
def github_repo_events(owner: str, name: str, access_token: Optional[str] = None):
    """REST events with incremental loading"""
    @dlt.resource(primary_key="id", table_name=lambda i: i["type"])
    def repo_events(
        last_created_at: dlt.sources.incremental[str] = ...
    ) -> Iterator[TDataItems]:
        ...
```

**Advantages:**
- Can use different APIs (GraphQL vs REST)
- Separate sources for different use cases
- Complex incremental logic possible
- Table naming functions
- Custom event dispatching
- Verified/maintained by dlt team

### 5. PAGINATION HANDLING

#### github_api_init (Page-based Example)
```yaml
client:
  paginator:
    type: page
    page_size_param: per_page
    default_page_size: 30
```
**How it works:** Framework automatically handles page iteration based on config.

#### github_source_init (Manual Example)
```python
def repo_events(...) -> Iterator[TDataItems]:
    repos_path = f"/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(name)}/events"
    
    for page in get_rest_pages(access_token, repos_path + "?per_page=100"):
        yield page
        
        if last_created_at.start_out_of_range:
            print(f"Overlap with previous run created at {last_created_at.initial_value}")
            break
```
**How it works:** Helper function manages pagination, developer controls flow.

### 6. AUTHENTICATION PATTERNS

#### github_api_init
```yaml
client:
  auth:
    type: apikey
    location: header
    header_name: Authorization
```
```python
@dlt.source
def github_source(access_token=dlt.secrets.value):
    config: RESTAPIConfig = {
        "client": {
            "auth": {
                "type": "apikey",
                "api_key": access_token,
                "location": "header",
                "header_name": "Authorization"
            }
        }
    }
```

#### github_source_init
```python
@dlt.source
def github_reactions(
    owner: str,
    name: str,
    access_token: str = dlt.secrets.value,
    ...
):
    # Token used in rest_pages helper
    for page in get_rest_pages(access_token, repos_path):
        yield page
```

### 7. INCREMENTAL LOADING

#### github_api_init (Config-based)
```yaml
resources:
  - name: some_resource
    endpoint:
      path: /repos/{owner}/{repo}/endpoint
      incremental:
        cursor_path: updated_at
        start_param: since
        initial_value: "2023-01-01T00:00:00Z"
```
**Framework automatically manages state.**

#### github_source_init (Code-based)
```python
@dlt.resource(primary_key="id", table_name=lambda i: i["type"])
def repo_events(
    last_created_at: dlt.sources.incremental[str] = dlt.sources.incremental(
        "created_at", 
        initial_value="1970-01-01T00:00:00Z", 
        last_value_func=max
    ),
) -> Iterator[TDataItems]:
    # Developer manages when to stop based on start_out_of_range
    if last_created_at.start_out_of_range:
        break
```
**Developer has full control.**

### 8. WRITE DISPOSITION & SCHEMA

#### github_api_init (Implicit)
```yaml
# Default behavior from resource_defaults if specified
# Or framework defaults (usually append)
resources:
  - name: issues
    endpoint:
      path: /repos/{owner}/{repo}/issues
      # write_disposition and primary_key handled by framework
```

#### github_source_init (Explicit)
```python
dlt.resource(
    get_reactions_data("issues", ...),
    name="issues",
    write_disposition="replace",  # Explicit
    primary_key="id",              # Explicit
)
```

### 9. DATA EXTRACTION

#### github_api_init
```yaml
resources:
  - name: issues
    endpoint:
      path: /repos/{owner}/{repo}/issues
      data_selector:  # JSONPath to extract actual data
      # If empty, assumes response is array or has default extraction
```
**Declarative, handled by framework.**

#### github_source_init
```python
def get_reactions_data(resource_type, ...):
    # Manual extraction of data from response
    # Custom processing before yielding
```
**Imperative, full developer control.**

### 10. TABLE GENERATION

#### github_api_init
**Tables created from resources array:**
- One table per resource: `issues`, `pull_requests`, `commits`, etc.
- Naming derived from resource name

#### github_source_init
**Tables created from decorators & return values:**
```python
@dlt.source
def github_reactions(...):
    return (
        dlt.resource(..., name="issues", ...),
        dlt.resource(..., name="pull_requests", ...),
    )

@dlt.source
def github_repo_events(...):
    @dlt.resource(table_name=lambda i: i["type"])
    def repo_events(...):
        # Dynamic table naming: one table per event type
        yield page
```
**Can have dynamic table naming based on data.**

## When to Use Each

### Use github_api_init When:
1. **Simple REST API** with no specialized logic
2. **Learning dlt** for the first time
3. **OpenAPI spec available** for conversion
4. **Multiple similar endpoints** with same pagination
5. **Team includes non-Python developers**
6. **Rapid prototyping** needed
7. **AI/LLM-driven development** where config is easier to generate
8. **MCP integration** where YAML is more portable
9. **Low customization needs**

### Use github_source_init When:
1. **Complex APIs** needing special handling
2. **Multiple protocols** (GraphQL + REST)
3. **Advanced incremental** with custom logic
4. **Dynamic table routing** based on data
5. **Official source** to be included in dlt library
6. **Specialized authentication** flows
7. **Complex data transformations**
8. **Existing verified source** to build from
9. **High customization** needs

## Endpoints Coverage Comparison

### github_api_init
**32 REST endpoints defined in github-docs.yaml:**
- Organization/user operations
- Repository metadata
- Issues & tracking
- Pull requests
- Commits & code
- Releases & deployments
- Events & activity
- Projects
- CI/CD workflows

### github_source_init
**2 specialized sources:**
1. `github_reactions` - GraphQL-based issues and PRs with reactions
2. `github_repo_events` - REST events with incremental loading
3. `github_stargazers` - Stargazers with dates (GraphQL)

**Intentionally limited** to high-value, complex data patterns.

## Code Generation Potential

### github_api_init
**Can be auto-generated from:**
- OpenAPI/Swagger specs
- Airbyte YAML definitions
- API documentation
- LLM-driven analysis

**Example:** AI system reads GitHub API docs → generates github-docs.yaml → pipeline works

### github_source_init
**Cannot be auto-generated** (requires domain expertise):
- Complex algorithms
- Custom transformations
- Multi-source joins
- Specialized incremental logic

**Example:** Human expert designs optimized source → tested by dlt team → included in library

## Example: Loading Issues

### github_api_init
```python
from dlt.sources.rest_api import rest_api_resources, RESTAPIConfig

@dlt.source
def github_source(access_token=dlt.secrets.value):
    config = {
        "client": {"base_url": "https://api.github.com"},
        "resources": [
            {
                "name": "issues",
                "endpoint": {
                    "path": "/repos/{owner}/{repo}/issues",
                    "method": "GET"
                }
            }
        ]
    }
    yield from rest_api_resources(config)

pipeline = dlt.pipeline("github_pipeline", destination="duckdb", dataset_name="github")
pipeline.run(github_source(token))
```
**Simple, direct, one file.**

### github_source_init
```python
from dlt_github import github_reactions

pipeline = dlt.pipeline("github_pipeline", destination="duckdb", dataset_name="github")
pipeline.run(github_reactions("owner", "repo", access_token=token))
```
**Import pre-built source.**

Or use helper functions:
```python
from dlt_github.helpers import get_reactions_data

# Custom logic wrapping the helper
```
**Compose from modules.**

## Summary Table

| Feature | github_api_init | github_source_init |
|---------|-----------------|-------------------|
| **Learning Curve** | Easy (YAML) | Moderate (Python + dlt) |
| **Speed to Build** | Very Fast (1 hour) | Slow (days/weeks) |
| **Flexibility** | Medium (config limits) | High (code freedom) |
| **Maintainability** | Good (configuration) | Good (code patterns) |
| **Scalability** | Good (many endpoints) | Excellent (specialized) |
| **Documentation** | Auto-generated possible | Manual required |
| **Testing** | Schema-based | Unit + integration |
| **Production Ready** | Yes (after testing) | Yes (if verified) |
| **AI-Friendly** | Excellent (YAML gen) | Difficult (code gen) |
| **MCP Compatible** | Excellent | Moderate |

## Conclusion

**github_api_init** = The future of API data loading: configuration-driven, AI-friendly, maintainable
**github_source_init** = The optimized past: hand-crafted, specialized, library-quality

Both are valid approaches for different scenarios in the dlt ecosystem.
