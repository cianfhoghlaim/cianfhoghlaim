## ADDED Requirements

### Requirement: Gaois + Celtic language pipeline cross-referenced from british-isles-education-pipeline

The `british-isles-education-pipeline` capability MUST cross-reference the
new [`celtic-language-pipeline`](../celtic-language-pipeline/spec.md)
capability in the `## Cross-references` section, since the 7 language/
source groups (Gaois, Dúchas, Heritage, Canuint, UD Celtic, Local documents,
Celtic curriculum) are consumed by the bilingual alignment with the
Irish education stages (Aistear, Primary, Junior Cycle, Senior Cycle,
Tertiary).

#### Scenario: A new file in the language expansion obeys the cross-region contract

- **WHEN** a developer reads the `british-isles-education-pipeline` spec
- **THEN** the `## Cross-references` section MUST list `celtic-language-pipeline`