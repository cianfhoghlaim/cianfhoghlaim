## ADDED Requirements

### Requirement: Cloud Run deployment — serving layer only (Rule 6 mandate)

The system SHALL deploy the 13 ADK agents + the TanStack Start web app to
Google Cloud Run as 2 independent services:

1. `biiep-agents` — the ADK agent runtime (Python service)
2. `biiep-web` — the TanStack Start web app (Node.js service)

Both services MUST scale to zero (`min-instances=0`) to stay under the
$150 credit budget. The Cloud Run serving layer is the ONLY new GCP
surface — all other infra (Cognee, LanceDB, litellm, llama-swap,
unsloth-serve, OCR router, Langfuse, ChangeDetection.io) stays on
bunchloch.

#### Scenario: Both services live on Cloud Run

- **WHEN** the operator runs `gcloud run services list --project=biiep-hackathon-2026-08`
- **THEN** the output MUST list both `biiep-agents` and `biiep-web`
- **AND** each service MUST have a public URL `<service>-<hash>.run.app`

### Requirement: Vertex AI Gemini 3.5 Flash integration

The system SHALL integrate Gemini 3.5 Flash via Vertex AI as the primary
LLM for the Cloud Run serving layer ONLY. The integration MUST use the
official `google-cloud-aiplatform` SDK (Python) and `@google-cloud/vertexai`
(TS).

The model MUST be `gemini-3.5-flash` (the cost-saving tip from the Resources page).

The litellm gateway on the dev (local) side handles local inference;
the Vertex AI endpoint handles production (Cloud Run) inference. The
agent-client.ts in the web app switches between the two.

#### Scenario: Gemma fails → Cloud Gemini fallback works

- **WHEN** the local Gemma client is unreachable (offline mode)
- **THEN** the cloud serving layer SHALL serve the request via Vertex AI
- **AND** the response MUST be returned within ≤3 seconds

### Requirement: Secret Manager (replaces Locket/Infisical)

The system SHALL use Google Cloud Secret Manager to store all secrets
(database URLs, API keys, etc.). The previous Locket sidecar pattern
(from the main repo) MUST NOT be deployed to Cloud Run.

Required secrets:

- `VERTEX_AI_API_KEY` — Vertex AI authentication
- `FIRESTORE_PROJECT_ID` — Firestore project ID

#### Scenario: Secret Manager replaces Locket

- **WHEN** the operator runs `gcloud secrets list --project=biiep-hackathon-2026-08`
- **THEN** the output MUST list all required secrets
- **AND** NO `.env` file MUST exist in the worktree (the Infisical pattern is replaced)

### Requirement: Firestore (Memory Bank) on the serving layer

The system SHALL use Firestore (Native mode) as the **Memory Bank** primitive
for the Collaborative Partner track. This is the ONLY new Firestore use
on Cloud Run. The existing Cognee stack handles the production structured
knowledge; Firestore handles the cross-instance persistence.

The data model MUST include:

- `sessions/{session_id}` — conversation history
- `users/{user_id}` — user preferences
- `progress/{user_id}/{jurisdiction}/{level}/{subject}` — syllabus progress
- `feedback/{user_id}/{timestamp}` — user feedback for adaptive learning

#### Scenario: Memory persists across Cloud Run instances

- **WHEN** user A sends a message in `biiep-agents-v1` instance
- **AND** the next message is routed to `biiep-agents-v2` instance
- **THEN** the v2 instance MUST see the previous conversation history
- **AND** the response MUST adapt to the user's previous context

### Requirement: Identity-Aware Proxy (replaces Pangolin)

The system SHALL use Identity-Aware Proxy (IAP) to authenticate the
public-facing Cloud Run URLs. The previous Pangolin tunnel pattern
(from the main repo) MUST NOT be deployed.

#### Scenario: IAP blocks unauthenticated requests

- **WHEN** an unauthenticated request hits `biiep-web-<hash>.run.app/admin`
- **THEN** IAP MUST return a 401 Unauthorized
- **AND** the request MUST be logged to Cloud Logging

### Requirement: Cost guardrails (stay under $150)

The system SHALL stay under the $150 credit budget. Required guardrails:

- Cloud Run `min-instances=0` for both services
- Firestore Native mode (no enterprise edition)
- Cloud Storage 5GB cap
- Vertex AI `gemini-3.5-flash` (NOT `gemini-3.5-pro`)
- Cloud Billing alert at $50 + $100 + $150 thresholds
- Estimated total cost: **$15** (well under $150, since most work uses the existing local litellm + llama-swap + unsloth-serve + OCR router)

#### Scenario: Daily cost stays under $3

- **WHEN** the operator runs `gcloud billing accounts list --project=biiep-hackathon-2026-08`
- **THEN** the daily cost MUST be ≤ $3
- **AND** the cumulative cost over 10 days MUST be ≤ $30 (well under $150)
