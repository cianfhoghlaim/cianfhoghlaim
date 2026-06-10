# react-native-godot — KCG Summary

## What It Is
React Native Godot (`@borndotcom/react-native-godot`) embeds the Godot Engine into React Native applications on Android and iOS. Built on LibGodot, it runs Godot on a separate thread, supports starting/stopping/restarting/pausing the engine, and exposes the full Godot API to TypeScript via worklets. Used in production by Born with millions of users.

## Why This Matters for Kings' College Galway
The `tuatha/` educational MMO uses Babylon.js for 3D rendering in the browser, but React Native Godot represents an alternative native-client path for iOS/Android — particularly useful for Godot-authored Celtic particle effects, Ogham stone procedural scenes, and high-performance 3D that can reuse the same GDScript or C# game logic across platforms. The LibGodot pattern for embedding a game engine into React Native also informs our Babylon.js integration architecture in `tuatha/ui`.

## Key Patterns Preserved
- **README.md** — Full documentation: features, quick-start, Godot API usage, threading model, custom LibGodot builds, remote debugging
- **SKILL_CONTEXT.md** — AI agent context for working with this library

## Source Files
Full source code removed (2026-06-06). The 2 deleted files are `package.json` and `LICENSE`. Available at <https://github.com/migeran/react-native-godot> (npm: `@borndotcom/react-native-godot`).

## What Was Removed
- Package manifest: `package.json`
- License file (MIT — see upstream for full text)
