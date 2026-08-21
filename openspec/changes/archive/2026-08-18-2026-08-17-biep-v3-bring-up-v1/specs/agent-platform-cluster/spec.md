# agent-platform-cluster

## ADDED Requirements

### Requirement: CopilotKit actions-stubbed lint invariant

The system SHALL fail `mise run lint:copilotkit-actions-stubbed` if
any action function in `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts`
returns the literal string `"TBD"` (the 12-of-14 stub class per the
`agentic-frontend-frameworks` spec).

The reason: per the `2026-08-10-copilotkit-action-wiring-v1` change
proposal, 12 of 14 CopilotKit actions return placeholder data. The
`leaving-cert.cianfhoghlaim.ie` chat UX is degraded. Closing this
gap requires (a) wiring real handlers (5 new files in
`apps/api/src/copilotkit/handlers/{syllabus,marking,ocr,learning_outcome,student_progress}.ts`)
and (b) a lint gate that prevents re-introduction of the stub
pattern.

This requirement adds the lint gate (the action wiring itself is
archived as part of Mega-1 Phase 4).

#### Scenario: Developer adds a new stub action

- **WHEN** a developer adds:
  ```typescript
  appRuntimeClient.actions.lookupFoo = async (): Promise<FooResult> => {
    return { result: "TBD", };  // placeholder
  };
  ```
- **THEN** `mise run lint:copilotkit-actions-stubbed` exits 1 with
  `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts:<line>: stub action detected — wire to a real handler`

#### Scenario: Real action passes the lint

- **WHEN** the action returns real data from a BAML call, DuckLake
  query, or Convex lookup
- **THEN** the lint exits 0

#### Scenario: Test fixture with stub action is exempt

- **GIVEN** `actions.test.ts` contains stub actions for unit tests
- **WHEN** the lint runs
- **THEN** it exits 0 (the `.test.ts` filename matches the test
  exemption pattern)