# @cianfhoghlaim/contracts — shared TS types + Zod schemas

Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1**
openspec change. The canonical shared types for the Cianfhoghlaim
platform.

## What's included

- **BIEP axis** — `BIEP_SUBJECTS` (15 subjects), `SubjectSchema` (Zod enum)
- **Jurisdiction schemas** — `BRITISH_ISLES_JURISDICTIONS`,
  `COMMONWEALTH_JURISDICTIONS`, `EUROPEAN_NATIONS_JURISDICTIONS`,
  `JurisdictionSchema`
- **Tertiary institution schemas** — `TERTIARY_INSTITUTIONS` (UoG +
  NUI federation + british_isles_tertiary), `TertiaryInstitutionSchema`
- **Pipeline event schema** — `PipelineEventSchema` (the AG-UI
  SSE envelope shape, with 12 event types: RUN_STARTED, RUN_FINISHED,
  STEP_STARTED, STEP_FINISHED, TEXT_MESSAGE_START, TEXT_MESSAGE_CONTENT,
  TEXT_MESSAGE_END, TOOL_CALL_START, TOOL_CALL_ARGS, TOOL_CALL_END,
  TOOL_CALL_RESULT, STATE_DELTA, MESSAGES_SNAPSHOT)
- **Source kind + destination schemas** — `SourceKindSchema` (the 8
  pipeline kinds: syllabus, exam_papers, personal_archive,
  official_docs, comics, crypto, pdf, media), `DestinationSchema`
  (the 15 destination names from Wave 4)

## Setup

```bash
bun add @cianfhoghlaim/contracts
```

## Usage

```ts
import {
  BIEP_SUBJECTS,
  SubjectSchema,
  JurisdictionSchema,
  PipelineEventSchema,
  type PipelineEvent,
} from "@cianfhoghlaim/contracts";

// Validate a subject
const result = SubjectSchema.safeParse("mathematics");
if (result.success) {
  console.log("Valid subject:", result.data);
}

// Validate a pipeline event from AG-UI
const event: PipelineEvent = PipelineEventSchema.parse({
  event_type: "TEXT_MESSAGE_CONTENT",
  run_id: "run-123",
  thread_id: "thread-456",
  timestamp: new Date().toISOString(),
});
```
