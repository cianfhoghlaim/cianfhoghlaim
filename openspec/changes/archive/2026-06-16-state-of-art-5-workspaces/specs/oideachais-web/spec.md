# Spec Delta: oideachais-web

## ADDED Requirements

### Requirement: AG-UI Streaming CopilotKit Runtime
The oideachais-web API server SHALL provide a CopilotKit AG-UI streaming runtime that:
- Reads/writes `subject_sessions` from the Convex table indexed by `user_id` + `stage` + `language`
- Streams AG-UI events via `http-sse` transport
- Supports bilingual routing via `?language=en|ga` query parameter
- Enforces extraction budget via `extraction_budget` Convex table (5 papers/day/session)

#### Scenario: Bilingual chat session
- **WHEN** user initiates chat with `?language=ga&stage=junior_cycle&subject=gaeilge`
- **THEN** runtime creates/loads `subject_sessions` row indexed by `(user_id, 'junior_cycle')`
- **AND** streams AG-UI events in Irish language

### Requirement: TanStack DB Practice Attempts Cache
The web app SHALL provide a `@tanstack/db` collection for `practice_attempts` that:
- Synchronizes with the Convex `practice_attempts` table via oRPC
- Supports optimistic mutations for essay submission
- Invalidates on new practice attempt record

#### Scenario: Optimistic essay submit
- **WHEN** user submits an essay for a practice question
- **THEN** DB collection optimistically inserts the attempt
- **AND** oRPC mutation writes to Convex `practice_attempts`
- **AND** DB syncs back the server-assigned `_id` and `trace_id`

### Requirement: Better Auth Protected Procedures
The oRPC server SHALL provide true auth protection:
- `protectedProcedure` SHALL call `auth.api.getSession()` against the oIDC issuer
- `publicProcedure` SHALL remain unauthenticated
- Auth state SHALL be shared between Hono API server and TanStack Start SSR

#### Scenario: Authenticated request
- **WHEN** user makes an RPC call with a valid Better Auth session cookie
- **THEN** `protectedProcedure` extracts user from session and passes to handler
- **AND** handler receives `ctx.session.user`

#### Scenario: Unauthenticated request
- **WHEN** user makes an RPC call without a valid session
- **THEN** `protectedProcedure` throws `UNAUTHORIZED` error

### Requirement: BAML Extraction Pipeline with Langfuse Tracing
The oRPC server SHALL provide a `baml.extract` procedure that:
- Accepts a `stage`, `subject`, and `session_id`
- Runs `curriculum_extraction.baml` against the staging store
- Emits a Langfuse trace per extraction
- Enforces `extraction_budget` (5 papers/day/session)

#### Scenario: Budget-exceeded extraction
- **WHEN** user has already extracted 5 papers in this session's 24h window
- **THEN** procedure returns HTTP 429 with remaining reset time
- **AND** no BAML call is made

### Requirement: MotherDuck Dive Embed
The lakehouse route SHALL render a MotherDuck Dive embed via:
- oRPC `motherduck.embedSession` procedure (already implemented)
- React `<MotherDuckDive>` component using the returned session token

#### Scenario: Dive loads
- **WHEN** authenticated user navigates to `/lakehouse`
- **THEN** MotherDuck Dive embed session is requested via oRPC
- **AND** Dive renders in an iframe

### Requirement: Effect-TS Convex Client
The Convex client layer SHALL be wrapped in Effect-TS for testability, replacing direct `ConvexReactClient` usage with Effect-based services that return `Effect<A, E, R>` types and support mock injection for unit tests.

#### Scenario: Effect-based Convex query
- **WHEN** a component calls a Convex query through the Effect-TS layer
- **THEN** the query returns `Effect<Data, ConvexError, never>`
- **AND** the component can use `Effect.runPromise` or TanStack Query integration
- **AND** in tests, a mock Convex service can be injected via Effect's Layer system

### Requirement: Bilingual Route Loaders
Each bilingual route (`en/` and `ga/`) SHALL provide a TanStack Start `loader()` that:
- Fetches from the correct Convex `subject_sessions` row keyed by `language` index
- Passes preloaded data to route component via `Route.useLoaderData()`

#### Scenario: Irish route load
- **WHEN** user navigates to `/ga/céimeanna/ardteist`
- **THEN** loader fetches `subject_sessions` where `language === 'ga'`
- **AND** component renders with server-loaded data

### Requirement: Langfuse Tracing on All oRPC Procedures
All oRPC procedures SHALL emit a Langfuse trace via a `withLangfuse` middleware on the `o` builder, with each trace including procedure name, duration, status, and error details if the call fails.

#### Scenario: Traced oRPC call
- **WHEN** any oRPC procedure is invoked
- **THEN** a Langfuse trace is created with the procedure name as the trace name
- **AND** the trace includes `input` and `output` as trace metadata
- **AND** if the procedure throws, the error is recorded in the trace with stack trace

## MODIFIED Requirements

### Requirement: ProtectedProcedure (previously always-throwing stub)
The `protectedProcedure` oRPC middleware SHALL call `auth.api.getSession()` against the oIDC issuer to validate the session cookie, passing the authenticated user to the handler's context on success instead of throwing UNAUTHORIZED for all callers.

#### Scenario: Authenticated request with valid session
- **WHEN** user makes an RPC call with a valid Better Auth session cookie
- **THEN** `protectedProcedure` calls `auth.api.getSession()` which returns a valid session
- **AND** handler receives `ctx.session.user` with id, name, email, and emailVerified fields

#### Scenario: Unauthenticated request
- **WHEN** user makes an RPC call without a session cookie
- **THEN** `protectedProcedure` throws `ORPCError("UNAUTHORIZED")`

### Requirement: root `app.config.ts` (previously Vinxi hybrid)
The root `app.config.ts` SHALL be replaced by a TanStack Start native `vite.config.ts` at project root that uses `@tanstack/react-start/plugin/vite` and `@vitejs/plugin-react`, removing all Vinxi 0.4 router references and `vinxi/types/client` TypeScript types.

#### Scenario: Dev server starts with TanStack Start native
- **WHEN** developer runs `bun run dev` in sruth/oideachais/web
- **THEN** TanStack Start dev server starts on port 3001
- **AND** file-based routes under `apps/web/src/app/routes/` are discovered
- **AND** SSR streaming works with React Suspense
- **AND** no Vinxi warnings appear in console

## REMOVED Requirements

### Requirement: Vinxi Router `sruth/oideachais/web/src/` (empty directory)
**Reason**: Vinxi 0.4 legacy; TanStack Start is now native.
**Migration**: None — directory was empty.
