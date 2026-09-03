# `croilar-persona-registry` capability spec — NEW

The type-safe persona configuration system that defines each public identity in the Croílár platform.

## ADDED Requirements

### Requirement: Persona Schema
The system SHALL define a Zod-validated TypeScript schema for persona configuration.

#### Scenario: Schema validates correctly
- **WHEN** a persona config file in `personas/<id>.ts` is loaded
- **THEN** the config SHALL be validated against the `Persona` Zod schema
- **AND** invalid configs SHALL produce a compile-time TypeScript error

#### Scenario: Required fields present
- **WHEN** the schema is checked
- **THEN** every persona SHALL have `id`, `slug`, `i18n` (en + ga), `theme` (mode + accent + palette), `routes` (non-empty array with per-route `path`, `label`, `icon`, `loader`), `dataSources` (non-empty array), `featureFlags` (cv, data, identity, contact booleans), `dagsterAssetGroup`, and `bamlSchemas`

### Requirement: Persona Registry
The system SHALL maintain a lookup table mapping persona slugs to full persona configs.

#### Scenario: Registry resolves persona
- **WHEN** `getPersona("aleyum")` is called
- **THEN** the full Aleyum persona config is returned

#### Scenario: Unknown persona returns undefined
- **WHEN** `getPersona("nonexistent")` is called
- **THEN** `undefined` is returned and the router SHALL render a 404

### Requirement: New Persona Addition
The system SHALL support adding a persona by creating one file and registering it.

#### Scenario: Adding a third persona
- **WHEN** a new file `personas/<new-id>.ts` is created using `definePersona({...})`
- **AND** the new persona is added to `_registry.ts`
- **THEN** `bun run typecheck` SHALL pass
- **AND** the new persona SHALL receive its own routes, theme, i18n bundle, and data sources

### Requirement: Theme Token Generation
The system SHALL derive CSS custom properties from each persona's theme config.

#### Scenario: Theme tokens resolved
- **WHEN** the aleyum persona is loaded
- **THEN** `resolveThemeTokens("aleyum")` SHALL return `{ "--color-accent": "oklch(0.74 0.18 285)", "--color-scheme": "dark", ... }`
- **AND** these tokens SHALL be applied to `document.documentElement` via `__root.tsx`
