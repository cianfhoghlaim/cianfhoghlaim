# PyPI Package Registry - Forgejo

Host private Python packages on `git.cianfhoghlaim.ie`.

## Registry URL

```
https://git.cianfhoghlaim.ie/api/packages/{owner}/pypi/simple
```

Replace `{owner}` with your Forgejo username or organization name.

## Authentication

### Create Access Token

1. Go to https://git.cianfhoghlaim.ie/user/settings/applications
2. Generate token with `write:package` scope
3. Save the token securely

### Configure uv (Recommended)

Add to your project's `pyproject.toml`:

```toml
[[tool.uv.index]]
name = "cianfhoghlaim"
url = "https://git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/pypi/simple"
```

For authentication, set environment variable:

```bash
export UV_INDEX_CIANFHOGHLAIM_PASSWORD="your_token_here"
```

Or add to `~/.config/uv/uv.toml`:

```toml
[[index]]
name = "cianfhoghlaim"
url = "https://git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/pypi/simple"
username = "your_username"
password = "your_token"
```

### Configure pip

Add to `~/.pip/pip.conf`:

```ini
[global]
extra-index-url = https://{username}:{token}@git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/pypi/simple
```

### Configure twine for Publishing

Add to `~/.pypirc`:

```ini
[distutils]
index-servers =
    cianfhoghlaim

[cianfhoghlaim]
repository = https://git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/pypi
username = your_username
password = your_token
```

## Publishing Packages

### Using uv (Recommended)

```bash
# Build the package
uv build

# Publish to Forgejo
uv publish --index cianfhoghlaim
```

### Using twine

```bash
# Build the package
python -m build

# Upload to Forgejo
twine upload --repository cianfhoghlaim dist/*
```

## Installing Packages

### Using uv

```bash
# Install from private registry (searches both PyPI and Forgejo)
uv pip install cianfhoghlaim-shared

# Install from specific index
uv pip install cianfhoghlaim-shared --index cianfhoghlaim
```

### Using pip

```bash
pip install --extra-index-url https://git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/pypi/simple cianfhoghlaim-shared
```

## Package Naming Convention

For Cianfhoghlaim packages, use the `cianfhoghlaim-` prefix:

- `cianfhoghlaim-shared` - Shared utilities
- `cianfhoghlaim-oideachais` - Education pipeline
- `cianfhoghlaim-tuath` - Game/narrative system
- `cianfhoghlaim-crypteolas` - Crypto intelligence

## Example pyproject.toml

```toml
[project]
name = "cianfhoghlaim-shared"
version = "0.1.0"
description = "Shared utilities for Cianfhoghlaim projects"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[[tool.uv.index]]
name = "cianfhoghlaim"
url = "https://git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/pypi/simple"
```

## Troubleshooting

### 401 Unauthorized

- Verify token has `write:package` scope
- Check token hasn't expired
- Ensure correct username/token in config

### Package Not Found

- Ensure package was published successfully
- Check package name matches exactly (case-sensitive)
- Verify you're using correct owner in URL
