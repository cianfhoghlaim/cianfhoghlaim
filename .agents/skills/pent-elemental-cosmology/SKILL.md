---
name: pent-elemental-cosmology
description: The KCG Pent-Elemental Cosmology in the Tuatha MMO. Covers the 5 realms (Spirit / Water / Fire / Earth / Air), the Anam Cara (soul friend) social bond mechanic, the 5 SpacetimeDB tables (Player, NPC, RealmConfig, AnamCara, RealmEdge), the Geasa system (the binding + status rules), the 5 quest tracks (one per element), the Babylon.js scene graph integration, and the canonical add-a-new-quest-pack workflow. Use when adding a new quest pack, configuring an Anam Cara bond, wiring a new Babylon.js zone to its SpacetimeDB namespace, designing a Geasa rule, or asking "what is the Pent-Elemental Cosmology?".
---

# Pent-Elemental Cosmology

## Purpose

The Tuatha MMO is built around the **Pent-Elemental Cosmology**:
five realms (Spirit / Water / Fire / Earth / Air) joined by the
**Anam Cara** (Irish for "soul friend") social bond mechanic.
This skill captures the 5 realms + the 5 SpacetimeDB tables + the
Geasa system + the 5 quest tracks + the Babylon.js scene graph
integration, and the canonical add-a-new-quest-pack workflow.

## When to use this skill

Use when you need to:

- "Add a new quest pack"
- "Configure an Anam Cara bond"
- "Wire a new Babylon.js zone to its SpacetimeDB namespace"
- "Design a Geasa rule"
- "Understand the 5 realms"
- "Understand the relationship between the 5 realms + the curriculum frameworks"

## The 5 realms (the cosmology)

| Element | Realm | Subject | Curriculum framework | Quest pack |
|:--|:--|:--|:--|:--|
| **Spirit** | `Tír na Spiorad` | The invisible + the contemplative | NCCA Senior Cycle (the highest level) | `quest-pack-spirit/` |
| **Water** | `Muir na gCloch` | The Celtic + the sea | NCCA Junior Cycle + CfE Senior Phase | `quest-pack-water/` |
| **Fire** | `Tine na Laoch` | The transformation + the hero | CCEA KS3-4 + SQA Higher | `quest-pack-fire/` |
| **Earth** | `Talamh na bhFocal` | The language + the land | NCCA Primary + CfE First/Second | `quest-pack-earth/` (the default for new players) |
| **Air** | `Gaoth na nEala` | The wind + the voice | CfW Foundation + CfE Early | `quest-pack-air/` |

The 5 realms are configured in `tuatha/crates/services/src/cosmos.rs:RealmConfig`
(the canonical SpacetimeDB table home).

## The 5 SpacetimeDB tables (the state)

| Table | Description | Key fields |
|:--|:--|:--|
| `Player` | The player state | `id: u64`, `name: String`, `realm: Realm`, `level: u32`, `xp: u64`, `geasa: Geasa[]`, `anam_cara: AnamCara` |
| `NPC` | The non-player character state (5 per realm = 25 total) | `id: u64`, `name: String`, `realm: Realm`, `lore: Lore`, `quests: Quest[]` |
| `RealmConfig` | The per-realm configuration (5 rows total) | `realm: Realm`, `world_size: f32`, `lighting: Lighting`, `physics: Physics` |
| `AnamCara` | The soul-friend bond (one per player) | `player_id: u64`, `companion_id: u64`, `bonded_at: i64`, `bond_strength: f32` |
| `RealmEdge` | The inter-realm connection (10 edges total) | `from_realm: Realm`, `to_realm: Realm`, `edge_type: EdgeType`, `unlock_condition: UnlockCondition` |

The 5 tables are defined in `tuatha/crates/services/src/schema.rs` (the
canonical SpacetimeDB schema home).

## The Anam Cara (the soul-friend bond)

The **Anam Cara** is an Irish concept of "soul friend" — a deep,
transformative friendship. In the Tuatha MMO, every player has
exactly 1 Anam Cara companion (a non-player character from a
different realm). The bond mechanic:

- **bond_strength** (0.0 to 1.0) — starts at 0.1, grows with
  shared quests + dialogue + gifting
- **bonded_at** — the timestamp of the initial bond
- **companion_id** — the NPC id of the Anam Cara
- **max_bond_strength** — 0.95 (the last 0.05 is reserved for the
  "Anam Cara NFT" memento)

The Anam Cara is implemented in
`tuatha/crates/services/src/anam.rs:AnamCaraService`.

## The Geasa system (the binding + status)

A **Geasa** (Irish for "binding") is a vow the player makes to an
NPC. The Geasa system has 4 statuses:

| Status | Description |
|:--|:--|
| `PENDING` | The player has spoken the vow but not yet completed the trial |
| `ACTIVE` | The player has completed the trial; the vow is in effect |
| `BROKEN` | The player has failed the trial; the vow is dissolved + a 24h penalty applies |
| `FULFILLED` | The vow has been completed; the reward is granted |

The Geasa is implemented in
`tuatha/crates/services/src/geasa.rs:GeasaService`.

## The 5 quest tracks (one per element)

| Track | Subject | Difficulty | Default for |
|:--|:--|:--|:--|
| `Spirit` | The invisible + the contemplative | Senior | Post-Leaving-Cert students |
| `Water` | The Celtic + the sea | Upper-secondary | JC + CfE Senior Phase |
| `Fire` | The transformation + the hero | Mid-secondary | CCEA KS3-4 + SQA Higher |
| `Earth` | The language + the land | Primary | NCCA Primary + CfE First/Second (the default) |
| `Air` | The wind + the voice | Foundation | CfW Foundation + CfE Early |

The 5 tracks are configured in `tuatha/crates/services/src/quests.rs:QuestTrack`.

## The Babylon.js scene graph integration

Each of the 5 realms is a **Babylon.js scene** loaded from
`tuatha/game/scenes/<realm>/`:

```
tuatha/game/
├── scenes/
│   ├── spirit/
│   │   ├── scene.babylon     # the Babylon.js scene file
│   │   ├── textures/
│   │   ├── meshes/
│   │   └── audio/
│   ├── water/
│   ├── fire/
│   ├── earth/    # the default
│   └── air/
├── shared/
│   ├── anam_cara.glb    # the Anam Cara companion model
│   └── geasa_hud.json   # the Geasa HUD config
└── client/
    └── scene_loader.ts # the client-side scene loader
```

The 5 scene files are loaded by the Babylon.js client at
`tuatha/game/client/scene_loader.ts:loadScene(realm)`.

## Worked example: add a new quest pack

1. Choose the realm (e.g. `fire` for the "Tine na Laoch" track).

2. Create the quest pack at `tuatha/crates/services/src/quests/fire.rs`:

   ```rust
   // tuatha/crates/services/src/quests/fire.rs
   pub fn fire_quests() -> Vec<Quest> {
       vec![
           Quest {
               id: 100,
               name: "The First Flame".to_string(),
               realm: Realm::Fire,
               difficulty: 5,
               geasa: Geasa::PENDING,
               ...
           },
           // ... more quests
       ]
   }
   ```

3. Add the BAML extraction at
   `tuatha/baml_src/fire_quest_extraction.baml`:

   ```baml
   class FireQuest {
       id int
       name string
       realm string
       difficulty int
       geasa string
       dialogue string[]
   }

   function ExtractFireQuest(text: string) -> FireQuest {
       client ExtractEn
       prompt #"Extract the Fire quest from: {{ text }}"#
   }
   ```

4. Add the Babylon.js scene at `tuatha/game/scenes/fire/scene.babylon`.

5. Add the asset to `tuatha/crates/services/src/quests/mod.rs:QuestRegistry`.

6. Update `tuatha/knowledge_graph/` with the new NPC + dialogue
   (the BAML extraction feeds the knowledge graph).

7. Add the new achievements to the
   `tuatha/crypteolas/achievements/` ledger (per
   `.agents/skills/tuatha-achievement-ledger/SKILL.md`).

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| The player is stuck in a realm | The RealmConfig `unlock_condition` is too strict | Relax the unlock condition in `RealmConfig` |
| The Anam Cara bond_strength is 0.0 | The companion NPC has no `lore.dialogue` | Add at least 3 dialogue lines to the NPC |
| The Geasa is stuck in `PENDING` | The trial quest has no `geasa_complete` callback | Add the callback to the quest |
| The quest pack won't compile | The Rust struct has a missing `Clone` derive | Add `#[derive(Clone, Debug)]` to the struct |
| The Babylon.js scene is black | The `world_size` is 0.0 | Set `world_size: 100.0` in the `RealmConfig` |

## Cross-references

- `.agents/skills/tuatha-mmo/SKILL.md` — the MMO tech stack (Babylon.js + SpacetimeDB + x402)
- `.agents/skills/british-isles-formative-assessment/SKILL.md` — the pedagogical framework (5 curriculum frameworks)
- `.agents/skills/celtic-asset-generation/SKILL.md` — how curriculum content becomes in-game assets
- `.agents/skills/tuatha-achievement-ledger/SKILL.md` — the skill-tree badge ledger (round 6 Phase 6)
- `.agents/skills/tuatha-mcp-server-tools/SKILL.md` — the 5 MCP tools + the shim pattern
- `tuatha/crates/services/src/schema.rs` — the 5 SpacetimeDB tables
- `tuatha/crates/services/src/cosmos.rs` — the RealmConfig home
- `tuatha/crates/services/src/anam.rs` — the AnamCaraService
- `tuatha/crates/services/src/geasa.rs` — the GeasaService
- `tuatha/game/scenes/` — the 5 Babylon.js scenes
- `tuatha/baml_src/` — the 5 BAML files
- `openspec/specs/tuatha-platform/spec.md` — the canonical spec
