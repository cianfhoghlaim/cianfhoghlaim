# Locket

Secrets management with 1Password integration for infrastructure and applications.

## Overview

Locket provides secure secret distribution:

- **1Password Connect** - Fetch secrets from 1Password vaults
- **Environment Injection** - Inject secrets as environment variables
- **Rotation Support** - Automatic secret rotation
- **Rust CLI** - Fast, secure CLI tool

## Location

```
bonneagar/locket/
├── Cargo.toml           # Rust workspace
├── src/
│   ├── main.rs          # CLI entry point
│   ├── onepassword.rs   # 1Password Connect client
│   ├── inject.rs        # Environment injection
│   └── rotate.rs        # Secret rotation
└── xtask/               # Build tasks
```

## Installation

```bash
# Build from source
cd bonneagar/locket
cargo build --release

# Or install globally
cargo install --path .
```

## Usage

### Fetch Secrets

```bash
# Fetch a single secret
locket get vault/item/field

# Fetch and inject as environment
locket inject --vault production -- ./my-app
```

### Environment Files

Generate `.env` files from 1Password:

```bash
# Generate .env from vault
locket env generate --vault production --output .env.production
```

### Docker Integration

```yaml
# docker-compose.yml
services:
  app:
    image: myapp:latest
    environment:
      - DATABASE_URL=op://vault/database/url
    entrypoint: ["locket", "inject", "--", "/app/start.sh"]
```

## Configuration

### 1Password Connect

Set up 1Password Connect server:

```yaml
# docker-compose.yml
services:
  op-connect-api:
    image: 1password/connect-api:latest
    ports:
      - "8080:8080"
    volumes:
      - ./1password-credentials.json:/home/opuser/.op/1password-credentials.json

  op-connect-sync:
    image: 1password/connect-sync:latest
    volumes:
      - ./1password-credentials.json:/home/opuser/.op/1password-credentials.json
      - op-data:/home/opuser/.op/data
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OP_CONNECT_HOST` | 1Password Connect server URL |
| `OP_CONNECT_TOKEN` | API token for Connect |

## Secret Reference Syntax

```
op://vault-name/item-name/field-name
```

Examples:
- `op://production/database/password`
- `op://development/api-keys/openai`

## Integration with Dagger

```typescript
// In Dagger pipeline
const secrets = await client
  .container()
  .from("rust:latest")
  .withExec(["cargo", "install", "--path", "bonneagar/locket"])
  .withEnvVariable("OP_CONNECT_HOST", process.env.OP_CONNECT_HOST!)
  .withSecretVariable("OP_CONNECT_TOKEN", opToken)
  .withExec(["locket", "env", "generate", "--output", ".env"]);
```

## Related

- [Pangolin](./pangolin) - VPN access
- [Komodo](./komodo) - Deployment management
- [Infrastructure Overview](./overview)
