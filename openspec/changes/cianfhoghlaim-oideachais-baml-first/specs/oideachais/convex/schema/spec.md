# Spec Delta — Convex Schema (5 tables, chat persistence)

## ADDED Requirements

### Requirement: Convex Schema
The system SHALL provide 5 Convex tables in `oideachais/web/convex/schema.ts` for chat persistence, practice attempts, PDF annotations, classmate shares, and extraction budget tracking.

#### Scenario: subject_sessions Table
- **GIVEN** the `subject_sessions` Convex table
- **WHEN** a chat session is created
- **THEN** a row is inserted with: `{stage: string, subject: string, user_id: string, agno_session_id: string, message_count: int, last_active_at: timestamp}`
- **AND** the `agno_session_id` is reused for subsequent messages

#### Scenario: practice_attempts Table
- **GIVEN** the `practice_attempts` Convex table
- **WHEN** a student submits an essay via `<SCPracticeEssayEditor>`
- **THEN** a row is inserted with: `{stage: "senior_cycle", subject: string, question_id: string, essay: string, score: float, rubric_fingerprint: string, trace_id: string}`
- **AND** the `trace_id` links back to the Langfuse trace

#### Scenario: annotations Table
- **GIVEN** the `annotations` Convex table
- **WHEN** a user highlights text in a PDF viewer
- **THEN** a row is inserted with: `{stage: string, document_url: string, range_start: int, range_end: int, note: string, author_id: string, visibility: "private" | "public"}`
- **AND** the highlight is rendered inline on the PDF

#### Scenario: classmate_shares Table
- **GIVEN** the `classmate_shares` Convex table
- **WHEN** a user shares a chat session via `<ShareButton>`
- **THEN** a row is inserted with: `{stage: string, session_id: string, owner_id: string, share_token: string, visibility: "public" | "link-only"}`
- **AND** the share link `/en/shared/$share_token` opens a read-only chat replay

#### Scenario: extraction_budget Table
- **GIVEN** the `extraction_budget` Convex table
- **WHEN** a user opens a past paper and the SPA calls `baml.lazyExtract`
- **THEN** the budget row is incremented: `{session_id: string, papers_extracted: int, tokens_consumed: int, reset_at: timestamp}`
- **AND** if `papers_extracted > 5`, the request is rejected with a "come back tomorrow" message

### Requirement: Convex Functions
The system SHALL provide 4 Convex function files in `oideachais/web/convex/`.

#### Scenario: Convex Query Functions
- **GIVEN** the Convex functions
- **WHEN** the SPA calls them
- **THEN** the functions include:
  - `getSubjectSession(stage, subject, user_id)` returns the most recent session
  - `listPracticeAttempts(subject, user_id)` returns the user's essays
  - `listAnnotations(document_url)` returns the highlights for a document
  - `getClassmateShare(share_token)` returns the shared session (read-only)

#### Scenario: Convex Mutation Functions
- **GIVEN** the Convex functions
- **WHEN** the SPA calls them
- **THEN** the functions include:
  - `createSubjectSession(stage, subject, user_id, agno_session_id)`
  - `updateSubjectSession(session_id, message_count, last_active_at)`
  - `recordPracticeAttempt(stage, subject, question_id, essay, score, rubric_fingerprint, trace_id)`
  - `addAnnotation(stage, document_url, range_start, range_end, note, author_id, visibility)`
  - `shareClassmateSession(session_id, owner_id, visibility)` — returns the share_token
  - `incrementExtractionBudget(session_id, papers_extracted, tokens_consumed)`
