# spacetimedb-typescript-sdk — KCG Summary

## What It Is
The `@clockworklabs/spacetimedb-sdk` TypeScript SDK for SpacetimeDB — the official client library for connecting browser/Node.js applications to a SpacetimeDB server. Handles WebSocket connection management, table subscription, reducer invocation, and auto-generated type bindings from the SpacetimeDB module schema.

## Why This Matters for Kings' College Galway
The `sruth/tuatha/` educational MMO uses this SDK to connect the Babylon.js frontend in `sruth/tuatha/ui` to the SpacetimeDB game server. Student positions, chat messages, quiz answers, and quest state all flow through this SDK's subscription/reducer model. The quickstart-chat example directly informs our multiplayer classroom text-chat implementation.

## Key Patterns Preserved
- **README.md** — SDK overview with GitHub source link
- **DEVELOP.md** — Development setup and contribution guide
- **packages/sdk/README.md** — Core SDK package documentation
- **packages/sdk/CHANGELOG.md** — SDK version history
- **packages/test-app/README.md** — Integration test application
- **examples/quickstart-chat/README.md** — Full-stack chat example (React + Vite + SpacetimeDB)
- **.changeset/README.md** — Changeset-based versioning workflow

## Source Files
Full source code removed (2026-06-06). The 139 deleted files include TypeScript source (`*.ts`, `*.tsx`), build config (`tsconfig.json`, `tsup.config.ts`, `vite.config.ts`, `vitest.config.ts`), package manifests (`package.json`, `pnpm-lock.yaml`), React components (`App.tsx`, CSS files), test files, SVG assets, and the `LICENSE` file. Available at <https://github.com/clockworklabs/SpacetimeDB> (under `sdks/typescript/packages/sdk`).

## What Was Removed
- TypeScript/JavaScript: `*.ts`, `*.tsx`, `*.js`, `*.jsx`
- Build config: `tsconfig.json`, `tsup.config.ts`, `vite.config.ts`, `vitest.config.ts`, `eslint.config.js`
- Package manifests: `package.json`, `pnpm-lock.yaml`
- Assets: `*.svg`, `*.css`
- Repo config: `.gitignore`, `.npmignore`, `.gitattributes`, `.prettierignore`
- License file
