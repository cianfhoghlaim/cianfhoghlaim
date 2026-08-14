## MODIFIED Requirements

### Requirement: 2D TanStack Start game client

The system SHALL provide a TanStack Start 2D game client at
`cianfhoghlaim/web/apps/cianfhoghlaim-mmo/` on port 3080 with routes
for the 8 subject realms, the student badge wallet, a Digital Learning
Profile, the cross-subject mastery dashboard, the teacher view, and the
public Merkle anchor verification page. The client SHALL use BetterAuth
(email/password + SIWE wallet) for authentication, Convex for real-time
state, and CopilotKit AG-UI for streaming agent chat. The client SHALL
be bilingual EN + GA throughout. Subject realm pages SHALL render quest
content fetched from a real Convex query against generated content — no
hardcoded item counts or non-functional buttons. Every subject realm
SHALL render a real, working CopilotKit chat panel connected to that
subject's specialist agent — not placeholder text. When a badge is
issued during a chat session, the chat SHALL render the badge inline as
generative UI, using only the fields the backend actually returned.
**No Babylon.js, no SpacetimeDB.**

#### Scenario: Subject realm page renders real quest content

- **GIVEN** the user navigates to `/realm/mathematics`
- **WHEN** the page loads
- **THEN** the page displays the Mathematics realm header (bilingual)
- **AND** the page renders the quest pack fetched via
  `useQuery(api.questPacks.getBySubject, { subject: "mathematics" })`,
  not a hardcoded count, with a loading state while the query resolves
  and an explicit "not yet generated" state if none exists
- **AND** the "Start" control expands a real formative item from the
  fetched pack

#### Scenario: Subject realm chat streams and renders a badge

- **GIVEN** a student is chatting with `math_agent` in the Mathematics
  realm and completes a formative item scoring ≥80%
- **WHEN** the agent's response includes a call to the
  `renderBadgeCard` CopilotKit action with the real `SkillTreeBadge`
  fields `issue_badge()` returned
- **THEN** a badge card renders inline in the chat stream, showing the
  subject, competency code, key competencies, and score
- **AND** the rendered card never displays a badge the backend did not
  actually issue

#### Scenario: Student badge wallet renders

- **GIVEN** a student has ≥1 `SkillTreeBadge` in Convex
- **WHEN** the user navigates to `/student/<id>/badges`
- **THEN** the page displays ≥1 badge card, fetched via
  `useQuery(api.badges.listByStudent, { studentId: id })`, with the
  badge id, framework, level, subject, competency code, date earned,
  and on-chain anchor
- **AND** the page links to the public verification page for each badge
- **AND** the page links to `/student/<id>/profile`

#### Scenario: Cross-subject mastery dashboard renders

- **GIVEN** a student has badges in ≥2 subjects
- **WHEN** the user navigates to `/student/<id>/mastery`
- **THEN** the page displays a FalkorDB-backed visualisation of the
  student's mastery across the 8 NCCA subjects

#### Scenario: Public anchor verification page renders

- **GIVEN** a date `2026-07-01` has a published Merkle anchor
- **WHEN** the user navigates to `/anchor/2026-07-01`
- **THEN** the page displays the Merkle root and the Base L2 tx_hash
- **AND** the page accepts a badge `id + evidence_hash` and verifies
  the Merkle path against the on-chain root

## ADDED Requirements

### Requirement: Digital Learning Profile

The system SHALL provide a "Digital Learning Profile" route
(`/student/<id>/profile`) presenting a student's earned badges grouped
by the NCCA's 7 senior-cycle key competencies (thinking and solving
problems, being creative, communicating, working with others,
participating in society, cultivating wellbeing, managing learning and
self), per the presentation pattern described in the NCCA's own
commissioned research into digital credentials and micro-credentials
(`leaving_certificate/the-potential-of-technology-to-support-online-
certification-and-reporting.pdf`) — distinct from the plain
chronological badge wallet.

#### Scenario: Profile groups badges by key competency

- **GIVEN** a student has earned badges tagged with
  `THINKING_AND_SOLVING_PROBLEMS` and `COMMUNICATING`
- **WHEN** the user navigates to `/student/<id>/profile`
- **THEN** the page renders a section per key competency present in
  the student's badges, each containing only the badges tagged with
  that competency
- **AND** badges issued before key-competency tagging existed (empty
  `key_competencies`) render in a separate "not yet mapped" section
  rather than being silently dropped
