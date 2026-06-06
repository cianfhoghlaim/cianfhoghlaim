# react-native-godot — Skill Context

**Upstream:** [migeran/react-native-godot](https://github.com/migeran/react-native-godot)  
**License:** MIT  
**Purpose:** Embeds the Godot Engine inside React Native applications with full bidirectional JS↔Godot API access.

## How We Use react-native-godot

This is the **sole bridge** between the tuatha educational MMO's two UI layers:
- **Godot 4** — 3D game world rendering on a dedicated thread
- **React Native / Expo** — UI shell, menus, agent chat, inventory management

Production-proven at scale (serving millions at Born.com). Supports Android and iOS via LibGodot.

## Key Integration Points

- **Tuatha MMO mobile app** — React Native shell with embedded Godot viewport
- **JS → Godot API** — player actions, inventory changes, quest triggers
- **Godot → JS API** — game events, NPC state, world position
- **Platform builds** — `react-native.config.js`, podspec for iOS, gradle for Android

## Reference Files (preserved)

- `README.md` — full API documentation
- `LICENSE` — MIT
- `package.json` — npm package manifest

## Related Docs

- `docs/tuatha/game/` — MMO game design and architecture docs
- `tuatha/` — root tuatha workspace
- `.agents/skills/irish-edtech/SKILL.md` — Irish edtech skill
