## ADDED Requirements

### Requirement: Babylon.js Retired from Active Web Apps

The system SHALL NOT use Babylon.js in any active web app.

#### Scenario: Babylon.js absent from tuatha-ui
- **WHEN** the user runs `grep -r "@babylonjs" web/apps/tuatha-ui/`
- **THEN** the command SHALL return 0 results

#### Scenario: babylonjs skill redirects
- **WHEN** the user reads `.agents/skills/babylonjs/SKILL.md`
- **THEN** the file SHALL contain a DEPRECATED notice with a redirect