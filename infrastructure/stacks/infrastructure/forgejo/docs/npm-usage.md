# npm Package Registry - Forgejo

Host private npm packages on `git.cianfhoghlaim.ie`.

## Registry URL

```
https://git.cianfhoghlaim.ie/api/packages/{owner}/npm
```

Replace `{owner}` with your Forgejo username or organization name.

## Authentication

### Create Access Token

1. Go to https://git.cianfhoghlaim.ie/user/settings/applications
2. Generate token with `write:package` scope
3. Save the token securely

### Configure npm

Add to `.npmrc` in project root or `~/.npmrc`:

```ini
@cianfhoghlaim:registry=https://git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/npm/
//git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/npm/:_authToken=${FORGEJO_NPM_TOKEN}
```

Set environment variable:

```bash
export FORGEJO_NPM_TOKEN="your_token_here"
```

### Configure pnpm

Add to `.npmrc`:

```ini
@cianfhoghlaim:registry=https://git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/npm/
//git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/npm/:_authToken=${FORGEJO_NPM_TOKEN}
```

### Configure bun

Bun reads from `.npmrc` automatically. Same configuration as npm.

## Publishing Packages

### Package Naming

Use scoped packages with `@cianfhoghlaim/` prefix:

```json
{
  "name": "@cianfhoghlaim/shared",
  "version": "0.1.0"
}
```

### Publish Command

```bash
# Using npm
npm publish

# Using pnpm
pnpm publish --no-git-checks

# Using bun
bun publish
```

## Installing Packages

```bash
# npm
npm install @cianfhoghlaim/shared

# pnpm
pnpm add @cianfhoghlaim/shared

# bun
bun add @cianfhoghlaim/shared
```

## Package Naming Convention

For Cianfhoghlaim packages:

- `@cianfhoghlaim/shared` - Shared UI components
- `@cianfhoghlaim/portal-ui` - Portal frontend components
- `@cianfhoghlaim/types` - TypeScript type definitions

## Example package.json

```json
{
  "name": "@cianfhoghlaim/shared",
  "version": "0.1.0",
  "description": "Shared frontend components for Cianfhoghlaim",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": ["dist"],
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "prepublishOnly": "pnpm build"
  },
  "publishConfig": {
    "registry": "https://git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/npm/"
  }
}
```

## Monorepo Configuration (Turborepo/pnpm)

In workspace `pnpm-workspace.yaml`:

```yaml
packages:
  - "packages/*"
```

In root `.npmrc`:

```ini
@cianfhoghlaim:registry=https://git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/npm/
//git.cianfhoghlaim.ie/api/packages/cianfhoghlaim/npm/:_authToken=${FORGEJO_NPM_TOKEN}
```

## Troubleshooting

### 401 Unauthorized

- Verify token has `write:package` scope
- Check `FORGEJO_NPM_TOKEN` is set
- Ensure `.npmrc` syntax is correct

### Package Not Found

- Check scoped package name is correct
- Verify registry URL includes owner
- Ensure package was published successfully
