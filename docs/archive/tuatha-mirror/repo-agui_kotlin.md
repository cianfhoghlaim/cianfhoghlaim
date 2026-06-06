# agui_kotlin — KCG Summary

## What It Is
The AG-UI Kotlin SDK is a production-ready Kotlin Multiplatform client library for connecting applications to AI agents that implement the Agent User Interaction Protocol (AG-UI). It supports Android, iOS, and JVM targets, providing streaming agent communication, protocol message types, event handling, and an extensible tool execution framework.

## Why This Matters for Kings' College Galway
The `tuatha/` educational MMO uses AG-UI protocol for its agent-to-UI communication — the CopilotKit frontend in `tuatha/ui` streams agent responses via AG-UI events. This Kotlin SDK informs the protocol compliance of our custom TypeScript AG-UI client, validates message serialization patterns, and provides a reference implementation for the tool-calling framework used by the Celtic Tutor, Mythology Narrator, and Quest Guide agents.

## Key Patterns Preserved
- **README.md** — Overview, quick-start, and dependency setup
- **OVERVIEW.md** — High-level architecture and design decisions
- **PERFORMANCE.md** — Performance characteristics and optimization guidance
- **CHANGELOG.md** — Release history (v0.2.x)
- **library/README.md** — Library module documentation
- **examples/chatapp/README.md** — Reference chat application (Kotlin Multiplatform + Compose)
- **examples/chatapp-java/README.md** — Java client example
- **examples/chatapp-shared/README.md** — Shared module example
- **examples/chatapp-swiftui/README.md** — SwiftUI interop example
- **examples/chatapp-wearos/README.md** — Wear OS integration example

## Source Files
Full source code removed (2026-06-06). The 278 deleted files include Kotlin source (`*.kt`, `*.kts`), Gradle build files (`build.gradle.kts`, `libs.versions.toml`, `gradle-wrapper.jar`), Android manifest (`AndroidManifest.xml`), `publish.sh` script, and the `LICENSE` file. Available at <https://github.com/ag-ui-protocol/ag-ui>.

## What Was Removed
- Kotlin source: `*.kt`, `*.kts`
- Gradle: `build.gradle.kts`, `libs.versions.toml`, `settings.gradle.kts`, `gradle-wrapper.jar`
- Android config: `AndroidManifest.xml`
- Scripts: `publish.sh`
- License file (MIT — see upstream for full text)
