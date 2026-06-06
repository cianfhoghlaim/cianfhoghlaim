# Spec Delta — TanStack Start Migration (file-based routes, SSR)

## MODIFIED Requirements

### Requirement: Web Framework (TanStack Start)

The system SHALL run the `oideachais/web/apps/web` on real **TanStack Start** with file-based routes, server functions, and SSR streaming. The current Vite SPA is replaced.

#### Scenario: File-Based Route Tree
- **GIVEN** `oideachais/web/apps/web/src/routes/`
- **WHEN** the directory is listed
- **THEN** it contains a `__root.tsx` plus file-based routes:
  - `__root.tsx` (the root layout with `<TranslationToggle>`, `<OideachasChat>`, header, footer)
  - `index.tsx` (5 stage cards)
  - `(en)/` and `(ga)/` route groups
  - Within each: `stages/{aistear,primary,junior_cycle,senior_cycle,tertiary}.tsx`, `subjects/$slug.tsx`, `courses/$courseCode.tsx`, `past-papers/$subject.tsx`, `marking-schemes/$subject.tsx`, `examiner-reports/$subject.tsx`, `practice/$subject.tsx`, `points-calculator.tsx`, `matriculation-auditor.tsx`, `about.tsx`, `chat.tsx`

#### Scenario: TanStack Start Configuration
- **GIVEN** `oideachais/web/app.config.ts`
- **WHEN** the file is read
- **THEN** it uses `defineConfig` from `@tanstack/react-start` and the `vinxi` framework
- **AND** the old Vite-only plugin list is replaced with `tsconfigPaths()`, `tailwindcss()`, `@tanstack/router-plugin()`
- **AND** the dev server runs `bun run --bun vite dev --host 0.0.0.0 --port 3001`

#### Scenario: Server Function for SSR
- **GIVEN** the `/en/stages/senior_cycle.tsx` route
- **WHEN** the page is server-rendered
- **THEN** the loader calls a `createServerFn` that fetches `subjects.lc_subjects.json` server-side
- **AND** the rendered HTML is streamed to the browser with React Suspense for slow-loading sections
- **AND** the client hydrates with the same `OideachasChat` panel

#### Scenario: Migration Preserves Functionality
- **GIVEN** the existing 7 routes (`index`, `exams`, `marking-schemes`, `syllabus`, `dives`, `lakehouse`, `runs`)
- **WHEN** the migration completes
- **THEN** the 4 routes `exams`, `marking-schemes`, `syllabus`, `dives` are removed (replaced by `subjects/$slug.tsx` with the dynamic data-driven view)
- **AND** the 3 ops routes `index`, `lakehouse`, `runs` are kept as file-based routes (no functional change, just file-based)
- **AND** the Vite proxy to `http://localhost:8787` for `/api` and `/rpc` is preserved
- **AND** the `vite.config.ts` plugins are updated to include `@tanstack/router-plugin` for the file-based route generation

#### Scenario: Old tsconfig References Removed
- **GIVEN** the root `oideachais/web/tsconfig.json` and `app.config.ts`
- **WHEN** they are inspected
- **THEN** the stale `include: ["app", "src", "vite.config.ts", "app.config.ts"]` and `paths: { "@/*": ["./app/*"] }` references (pointing at a non-existent `./app/`) are removed
- **AND** the `app.config.ts` no longer references `vinxi.config.ts` (which never existed)

## ADDED Requirements

### Requirement: TanStack Start Dependencies
The system SHALL declare the TanStack Start dependencies in `oideachais/web/package.json`.

#### Scenario: Required Dependencies
- **GIVEN** `oideachais/web/package.json`
- **WHEN** the dependencies are listed
- **THEN** `@tanstack/react-start` and `@tanstack/router-plugin` are present (currently installed but unused)
- **AND** `vinxi` is added as a devDependency
- **AND** no new runtime dependencies are added beyond the file-based router (TanStack Router is already there)
