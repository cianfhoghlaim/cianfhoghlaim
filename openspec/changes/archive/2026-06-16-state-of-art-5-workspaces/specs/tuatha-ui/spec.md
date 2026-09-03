# Spec Delta: tuatha-ui

## ADDED Requirements

### Requirement: SpacetimeDB Real-Time Multiplayer
The game route SHALL connect to a SpacetimeDB subscription:
- `routes/game.tsx` SHALL use `@spacetimedb/sdk` to subscribe to a `tuath-game` SpacetimeDB module
- Module SHALL track player positions, quests, and chat in real-time
- Babylon.js scene SHALL react to SpacetimeDB row updates (player movement, zone transitions)

#### Scenario: Two players in the same zone
- **WHEN** Player A moves in Babylon.js
- **THEN** position update is committed to SpacetimeDB
- **AND** Player B's Babylon scene receives the update via subscription
- **AND** Player B sees Player A's avatar move

### Requirement: SIWE Authentication via Better Auth
The auth system SHALL support Sign-In With Ethereum:
- `useSiweAuth()` hook SHALL call Better Auth's `siwe` plugin on the `sruth/croilar/hono-api` oIDC issuer
- `SIWEConnect.tsx` SHALL render the wallet connect flow (MetaMask, WalletConnect, Coinbase)
- Auth state SHALL persist across page reloads via JWT cookie

#### Scenario: Wallet sign-in
- **WHEN** user clicks "Connect Wallet" and signs the SIWE challenge
- **THEN** Better Auth creates/updates the user account linked to the Ethereum address
- **AND** JWT is set as a httpOnly cookie
- **AND** user is redirected to the game zone

### Requirement: x402 Paywall
The payment system SHALL enforce x402 payment for premium content:
- `X402Paywall.tsx` SHALL call the x402 middleware on Hono API
- Requests SHALL include a `Payment` header with the signed payment
- Server SHALL validate the payment amount and recipient before serving premium content

#### Scenario: Unlock premium zone
- **WHEN** user attempts to access a premium zone
- **THEN** server returns `402 Payment Required` with payment details
- **AND** `X402Paywall.tsx` prompts user to sign the payment
- **AND** on successful payment, user gains access to the zone

### Requirement: Mythology Server Functions with Graphiti Backend
The mythology page SHALL query a Graphiti knowledge graph:
- `server/mythology.ts` SHALL call the Graphiti MCP server for entity relationships
- Results SHALL be rendered as A2UI cards using `A2UIComponents.tsx`
- Search SHALL support fuzzy matching on character names, cycles, and traditions

#### Scenario: Search for Cú Chulainn
- **WHEN** user searches "Cú Chulainn" on the mythology page
- **THEN** server function queries Graphiti for entities matching the name
- **AND** returns related characters, stories, and cycles
- **AND** A2UI cards render with Celtic-themed styling

### Requirement: Curriculum Server Functions with LanceDB
The learn route SHALL query a LanceDB vector store for educational content, returning results with topic, subject, stage, and difficulty metadata, while tracking user progress through topics in the learning path.

#### Scenario: Search for Leaving Cert Irish grammar
- **WHEN** user searches "aidiacht shealbhach" on the learn page
- **THEN** server function vector-searches LanceDB for related curriculum content
- **AND** returns results ranked by semantic similarity
- **AND** each result includes stage (junior_cycle/senior_cycle), subject (gaeilge), and difficulty level

### Requirement: MapLibre Celtic Language Map
The map route SHALL render an interactive MapLibre map displaying the 6 Celtic nations with language region boundaries, speaker counts, and language details on hover using `react-map-gl/maplibre`.

#### Scenario: Map loads with Celtic regions
- **WHEN** user navigates to `/map`
- **THEN** MapLibre renders a map centered on the British Isles
- **AND** 6 Celtic regions are highlighted: Ireland, Scotland, Isle of Man, Wales, Cornwall, Brittany
- **AND** hovering a region shows speaker count and language name (Gaeilge, Gàidhlig, Gaelg, Cymraeg, Kernewek, Brezhoneg)

### Requirement: Crypteolas Federated Learning Demo
The learn/irish route SHALL integrate the crypteolas federated learning demo module, displaying training progress and model accuracy metrics from the `sruth/crypteolas/apps/crypteolas_demo` module via a TanStack Start server function.

#### Scenario: Federated training session
- **WHEN** user opens the learn/irish page
- **THEN** server function initializes a crypteolas federated learning session
- **AND** the page displays current model accuracy and rounds completed
- **AND** the user can opt-in to contribute their local data to the global model

## MODIFIED Requirements

### Requirement: game.tsx Import (fix broken module path)
The `routes/game.tsx` file SHALL import the Babylon.js game client from the correct workspace reference path (`@tuath/game-client` or inline initialization) instead of the broken relative path `../../game/client/src` which is unreachable from the `sruth/tuatha/ui` workspace.

#### Scenario: Game route renders Babylon.js canvas
- **WHEN** user navigates to `/game`
- **THEN** the game route imports the Babylon.js engine from the workspace
- **AND** a WebGL canvas renders the Celtic MMO world
- **AND** the TypeScript compiler does not report module-not-found errors

### Requirement: root Config (remove Vinxi dual-config)
The `sruth/tuatha/ui` package SHALL use a single TanStack Start native `vite.config.ts` as its sole build configuration, with the `app.config.ts` file deleted and `package.json` scripts updated from `vinxi dev/build/start` to TanStack Start CLI commands.

#### Scenario: Dev server starts with TanStack Start
- **WHEN** developer runs `bun run dev` in sruth/tuatha/ui
- **THEN** TanStack Start dev server starts on the configured port
- **AND** file-based routes under `src/routes/` are discovered and served
- **AND** no Vinxi-related errors appear in the console
- **AND** `app.config.ts` no longer exists in the project root

## REMOVED Requirements

### Requirement: Vinxi Runtime (`vinxi` dependency)
**Reason**: TanStack Start v2.140+ is now native (no longer Vinxi-based).
**Migration**: Remove `vinxi` from dependencies; remove `vinxi.config.ts` if present; verify no `vinxi/types` imports remain.
