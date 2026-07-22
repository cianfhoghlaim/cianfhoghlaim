# Cargo Crate Registry - Forgejo

Host private Rust crates on `git.cianfhoghlaim.ie`.

## Registry URL

```
https://git.cianfhoghlaim.ie/api/packages/{owner}/cargo
```

Replace `{owner}` with your Forgejo username or organization name.

## Authentication

### Create Access Token

1. Go to https://git.cianfhoghlaim.ie/user/settings/applications
2. Generate token with `write:package` scope
3. Save the token securely

### Configure Cargo

Add to `~/.cargo/config.toml`:

```toml
[registries.cianfhoghlaim]
index = "sparse+https://git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/cargo/"

[net]
git-fetch-with-cli = true
```

Add credentials to `~/.cargo/credentials.toml`:

```toml
[registries.cianfhoghlaim]
token = "Bearer your_token_here"
```

## Publishing Crates

### Configure Crate

In `Cargo.toml`:

```toml
[package]
name = "cianfhoghlaim-shared"
version = "0.1.0"
edition = "2021"
publish = ["cianfhoghlaim"]

[dependencies]
```

### Publish Command

```bash
cargo publish --registry cianfhoghlaim
```

## Installing Crates

### From Registry

In `Cargo.toml`:

```toml
[dependencies]
cianfhoghlaim-shared = { version = "0.1.0", registry = "cianfhoghlaim" }
```

### Using Cargo Add

```bash
cargo add cianfhoghlaim-shared --registry cianfhoghlaim
```

## Package Naming Convention

For Cianfhoghlaim crates:

- `cianfhoghlaim-shared` - Shared Rust utilities
- `cianfhoghlaim-parser` - Document parsing
- `cianfhoghlaim-embeddings` - Embedding utilities

## Example Cargo.toml

```toml
[package]
name = "cianfhoghlaim-parser"
version = "0.1.0"
edition = "2021"
description = "Document parsing utilities for Cianfhoghlaim"
license = "MIT"
publish = ["cianfhoghlaim"]

[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1", features = ["full"] }

[dev-dependencies]
pretty_assertions = "1.4"
```

## Workspace Configuration

For monorepo with multiple crates:

```toml
# Cargo.toml (workspace root)
[workspace]
members = ["crates/*"]
resolver = "2"

[workspace.package]
edition = "2021"
publish = ["cianfhoghlaim"]

[workspace.dependencies]
serde = { version = "1.0", features = ["derive"] }
```

Each crate inherits:

```toml
# crates/parser/Cargo.toml
[package]
name = "cianfhoghlaim-parser"
version = "0.1.0"
edition.workspace = true
publish.workspace = true
```

## Troubleshooting

### 401 Unauthorized

- Verify token format: `Bearer {token}`
- Check token has `write:package` scope
- Ensure credentials.toml permissions are restricted

### Crate Not Found

- Verify registry name matches config
- Check crate was published successfully
- Run `cargo update` to refresh index

### SSL Certificate Errors

Add to config.toml:

```toml
[http]
check-revoke = false
```
