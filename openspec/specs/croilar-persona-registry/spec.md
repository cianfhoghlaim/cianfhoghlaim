# `croilar-persona-registry` capability spec

The type-safe persona configuration system that defines each public identity in the Croílár platform.

## Requirements

### Requirement: Persona Schema
The system SHALL define a Zod-validated TypeScript schema for persona configuration.

#### Scenario: Schema validates correctly
- **WHEN** a persona config file in `personas/<id>.ts` is loaded
- **THEN** the config SHALL be validated against the `Persona` Zod schema
- **AND** invalid configs SHALL produce a compile-time TypeScript error

### Requirement: Persona Registry
The system SHALL maintain a lookup table mapping persona slugs to full persona configs.

#### Scenario: Registry resolves persona
- **WHEN** `getPersona("aleyum")` is called
- **THEN** the full Aleyum persona config is returned

### Requirement: New Persona Addition
The system SHALL support adding a persona by creating one file and registering it.

#### Scenario: Adding a third persona
- **WHEN** a new file `personas/<new-id>.ts` is created using `definePersona({...})`
- **AND** the new persona is added to `_registry.ts`
- **THEN** `bun run typecheck` SHALL pass
