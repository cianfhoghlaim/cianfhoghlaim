# meaisinfhoghlaim-agent-frameworks

## ADDED Requirements

### Requirement: 8 NCCA subject specialists migrated from back-compat

The 8 NCCA subject specialists SHALL be migrated from the
back-compat wiring in `agents/tuatha/wiring.py` to the new
`CelticAgentOpsComponent` (per the `meaisinfhoghlaim-platform` spec +
the `dagster-5-layer-component-architecture` spec).

| Specialist | Subject | Tuatha Dé | New wiring layer |
|:--|:--|:--|:--|
| `gael_agent` | Gaeilge | Ogma | `orchestration/defs/5_agent_ops/adk/gael_agent/defs.yaml` |
| `math_agent` | Mathematics | The Dagda | `orchestration/defs/5_agent_ops/adk/math_agent/defs.yaml` |
| `appm_agent` | Applied Mathematics | Lugh | `orchestration/defs/5_agent_ops/adk/appm_agent/defs.yaml` |
| `chem_agent` | Chemistry | Dian Cecht | `orchestration/defs/5_agent_ops/adk/chem_agent/defs.yaml` |
| `comp_agent` | Computer Science | — (modern) | `orchestration/defs/5_agent_ops/adk/comp_agent/defs.yaml` |
| `engl_agent` | English | Brigid | `orchestration/defs/5_agent_ops/adk/engl_agent/defs.yaml` |
| `geog_agent` | Geography | Manannán mac Lir | `orchestration/defs/5_agent_ops/adk/geog_agent/defs.yaml` |
| `hist_agent` | History | The Morrígan | `orchestration/defs/5_agent_ops/adk/hist_agent/defs.yaml` |

Each specialist SHALL emit 5 Dagster assets per the
`meaisinfhoghlaim-platform` spec (12 agents × 5 = 60 L5 assets total).

After migration, `agents/tuatha/wiring.py` SHALL only re-export
back-compat for the 3 educational agents (`academic_history_agent`,
`celtic_grammar_agent`, `celtic_morphology_agent`) — the 8 NCCA
specialists are removed from the back-compat surface.

#### Scenario: 8 specialists are wired via CelticAgentOpsComponent

- **WHEN** `agents/STATUS.md` is regenerated (per the
  `meaisinfhoghlaim-platform` spec)
- **THEN** all 8 NCCA specialists show status `Wired` (not
  `Back-compat`)
- **AND** `dg list defs --location 5_agent_ops` shows 8 agent mounts
  (one per specialist)

#### Scenario: agents/STATUS.md reflects migration

- **WHEN** the migration completes
- **THEN** `agents/STATUS.md` shows:
  - The 12 main agents (root, curriculum, translation, corpus,
    research, education_research, bunchloch_research, geospatial,
    statistics, curriculum_comparison, agui_curriculum, mcp_curriculum)
    — `Wired`
  - The 8 NCCA subject specialists — `Wired` (no longer `Back-compat`)
  - The 3 educational agents (`academic_history_agent`,
    `celtic_grammar_agent`, `celtic_morphology_agent`) — `Wired`
- **AND** `agents/tuatha/wiring.py` re-exports only the 3 educational
  agents (not the 8 NCCA specialists)