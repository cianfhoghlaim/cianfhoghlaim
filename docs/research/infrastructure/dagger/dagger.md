# Dagger CI/CD

Containerized CI/CD pipelines for the cianfhoghlaim monorepo.

## Overview

Dagger provides portable, reproducible CI/CD that runs anywhere:

- **Containerized** - Every step runs in a container
- **Cacheable** - Automatic caching of build artifacts
- **Polyglot** - TypeScript SDK with Python and Rust modules
- **Local/Remote** - Same pipeline runs locally and in CI

## Location

```
bonneagar/dagger/
├── dagger.json          # Dagger module configuration (v0.18.0)
├── package.json
└── src/
    ├── index.ts         # Infrastructure (Ansible, Docker Compose, 1Password)
    ├── ci.ts            # CI orchestration (polyglot)
    ├── python.ts        # Python CI (pytest, pyright, ruff, dagster)
    ├── typescript.ts    # TypeScript CI (bun, tsc, eslint, docusaurus)
    ├── rust.ts          # Rust CI (cargo, clippy, fmt)
    └── cloudflare.ts    # Cloudflare deployment (Pages, Workers)
```

## Usage

### Run Full CI

```bash
# Full polyglot CI (Python + TypeScript + Rust)
dagger call -m bonneagar/dagger ci --source .

# Or via mise
mise run dagger:ci
```

### Test Python Projects

```bash
# Test all Python projects
dagger call -m bonneagar/dagger test-python --source .

# Test specific project
dagger call -m bonneagar/dagger python test \
  --source . \
  --project sruth/oideachas
```

### Test TypeScript

```bash
# Run TypeScript checks
dagger call -m bonneagar/dagger test-typescript --source .

# Build all TypeScript
dagger call -m bonneagar/dagger typescript build --source .
```

### Test Rust

```bash
# Run Rust checks (clippy, fmt, test)
dagger call -m bonneagar/dagger test-rust --source .

# Build release binary
dagger call -m bonneagar/dagger rust build-release \
  --source . \
  --project bonneagar/locket
```

### Deploy to Cloudflare

```bash
# Deploy docs to Cloudflare Pages
dagger call -m bonneagar/dagger deploy-cloudflare \
  --source . \
  --api-token env:CLOUDFLARE_API_TOKEN \
  --account-id $CLOUDFLARE_ACCOUNT_ID
```

### Build All

```bash
# Build everything (TS + Rust + Docs)
dagger call -m bonneagar/dagger build-all --source .
```

## Module Structure

### Bonneagar Class (index.ts)

Main entry point exposing all pipeline functions:

```typescript
@object()
class Bonneagar {
  @func()
  async ci(source: Directory): Promise<string> {
    // Run all checks
  }

  @func()
  async testPython(source: Directory, project: string): Promise<string> {
    // Run pytest + pyright
  }
}
```

### Python Module (python.ts)

```typescript
export async function testPython(
  client: Client,
  source: Directory,
  project: string
): Promise<Container> {
  return client
    .container()
    .from("ghcr.io/astral-sh/uv:python3.12-bookworm")
    .withDirectory("/src", source)
    .withWorkdir(`/src/${project}`)
    .withExec(["uv", "sync"])
    .withExec(["uv", "run", "pytest"])
    .withExec(["uv", "run", "pyright"]);
}
```

## CI Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Python    │     │ TypeScript  │     │    Rust     │
│   pytest    │     │   bun build │     │ cargo test  │
│   pyright   │     │   tsc check │     │   clippy    │
│   ruff      │     │   eslint    │     │   fmt       │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Deploy    │
                    │  Cloudflare │
                    └─────────────┘
```

## Module Functions

### CI Module (ci.ts)

| Function | Description |
|----------|-------------|
| `ci` | Full polyglot CI (Python + TS + Rust) |
| `testPython` | Test all Python projects |
| `testTypescript` | Test TypeScript projects |
| `testRust` | Test Rust projects |
| `buildAll` | Build all projects |
| `deployCloudflare` | Deploy docs to Cloudflare Pages |

### Python Module (python.ts)

| Function | Description |
|----------|-------------|
| `test` | Run pytest |
| `typecheck` | Run pyright |
| `lint` | Run ruff check |
| `format` | Run ruff format |
| `testDagster` | Test Dagster assets |
| `check` | All Python checks |

### TypeScript Module (typescript.ts)

| Function | Description |
|----------|-------------|
| `typecheck` | Run tsc --noEmit |
| `lint` | Run eslint |
| `build` | Build all packages |
| `buildDocs` | Build Docusaurus |
| `buildApp` | Build specific app |

### Rust Module (rust.ts)

| Function | Description |
|----------|-------------|
| `build` | cargo build |
| `test` | cargo test |
| `clippy` | cargo clippy |
| `fmtCheck` | cargo fmt --check |
| `buildRelease` | Build release binary |

### Cloudflare Module (cloudflare.ts)

| Function | Description |
|----------|-------------|
| `deployPages` | Deploy to Pages |
| `deployDocs` | Build and deploy docs |
| `deployWorker` | Deploy Worker |
| `listProjects` | List Pages projects |

## Related

- [Pulumi](./pulumi) - Infrastructure as Code
- [Komodo](./komodo) - Container orchestration
- [Infrastructure Overview](./overview)
