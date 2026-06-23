---
title: "AG-UI Goes Mobile: The Kotlin SDK Unlocks Full Agent Connectivity Across Android, iOS, and JVM"
source: "https://webflow.copilotkit.ai/blog/ag-ui-goes-mobile-the-kotlin-sdk-unlocks-full-agent-connectivity-across-android-ios-and-jvm"
author:
published:
created: 2025-12-29
description: "Mark Fogle’s recent contribution of the Kotlin SDK to AG-UI is a big step forward: developers can now integrate AG-UI directly into Android, iOS, and JVM environments through a single, unified SDK.This means users can now connect to agents directly from mobile with no custom bridges, wrappers, or per-platform workarounds."
tags:
  - "clippings"
---
BY

Nathan Tarbert

November 4, 2025

[Mark Fogle’s](https://www.linkedin.com/in/markfogle/) recent contribution of the [**Kotlin SDK**](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/kotlin) to AG-UI is a big step forward: developers can now integrate AG-UI directly into **Android, iOS, and JVM** environments through a single, unified SDK.

This means users can now connect to agents directly from mobile with no custom bridges, wrappers, or per-platform workarounds.

What it looks like in practice:

**User → UI (Compose KMP / Swift / MDC) → Kotlin SDK → AG-UI → Agent → Android / IOS / JVM**

This flow enables real-time agent interactions from native apps, instead of relying on browser-based clients or webviews. AG-UI now lives natively inside your mobile stack, powered by [Kotlin’s multiplatform](https://kotlinlang.org/docs/multiplatform.html) capabilities.

### Why It Matters

Until now, AG-UI integrations were primarily web-first. That left mobile developers with either:

- Building custom wrappers, or
- Waiting for mobile SDK parity.

The Kotlin SDK eliminates both problems. You can now embed AG-UI agents in native mobile apps with full feature parity, minimal setup, and consistent behavior across all platforms.

Check out Mark's SDK walkthrough 👇

![](https://www.youtube.com/watch?v=QCYOIdDBdEw)

### Technical Benefits

1. **Unified API surface** → Same AG-UI methods across Android, iOS, and JVM.
2. **Native performance** → No JavaScript bridge or runtime overhead.
3. **Consistent agent UX** → Whether on mobile or desktop, the agent context and message flow remain identical.

### What This Enables

- **On-device AI copilots** that interact with app context in real time.
- **Cross-platform assistants** that maintain session state between web, Android, and iOS.
- **Seamless integration into existing mobile UIs** (Jetpack Compose, SwiftUI, etc.) through the AG-UI abstraction layer.

### The Bigger Picture

This Kotlin SDK moves AG-UI closer to its goal: being the universal interface layer for agentic systems.

Developers can now connect users and agents anywhere-from a mobile app, web app, or JVM service-through a single, consistent pipeline.

### Try It Out

Start building with the Kotlin SDK:

- [Kotlin SDK Getting Started](https://github.com/ag-ui-protocol/ag-ui/blob/main/docs/sdk/kotlin/overview.mdx)

If you’ve been waiting to bring AG-UI agents to mobile, the time has arrived.  

Don’t miss what’s next! Follow CopilotKit on [Twitter](https://x.com/CopilotKit) for real-time updates and join our [Discord](https://go.copilotkit.ai/discord-community) to collaborate with fellow agent builders.  
  
Happy building!

## Top posts

[See All](https://webflow.copilotkit.ai/blog)