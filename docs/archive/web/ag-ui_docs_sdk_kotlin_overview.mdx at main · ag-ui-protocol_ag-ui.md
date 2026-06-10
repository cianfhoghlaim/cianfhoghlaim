---
title: "ag-ui/docs/sdk/kotlin/overview.mdx at main · ag-ui-protocol/ag-ui"
source: "https://github.com/ag-ui-protocol/ag-ui/blob/main/docs/sdk/kotlin/overview.mdx"
author:
  - "[[contextablemark]]"
published:
created: 2025-12-29
description: "AG-UI: the Agent-User Interaction Protocol. Bring Agents into Frontend Applications. - ag-ui/docs/sdk/kotlin/overview.mdx at main · ag-ui-protocol/ag-ui"
tags:
  - "clippings"
---
[Open in github.dev](https://github.dev/) [Open in a new github.dev tab](https://github.dev/) [Open in codespace](https://github.com/codespaces/new/ag-ui-protocol/ag-ui/tree/main?resume=1)

[\[Kotlin\] Major enhancements and refactoring (](https://github.com/ag-ui-protocol/ag-ui/commit/9b266e30089476ecfcda3a3d0386dde64bc9ed45)[#600](https://github.com/ag-ui-protocol/ag-ui/pull/600)[)](https://github.com/ag-ui-protocol/ag-ui/commit/9b266e30089476ecfcda3a3d0386dde64bc9ed45)

[9b266e3](https://github.com/ag-ui-protocol/ag-ui/commit/9b266e30089476ecfcda3a3d0386dde64bc9ed45) ·

| title | description |
| --- | --- |
| Kotlin SDK Overview | Kotlin Multiplatform SDK for building AI agent user interfaces with the AG-UI protocol |

## Kotlin SDK

The AG-UI Kotlin SDK is a Kotlin Multiplatform library for building AI agent user interfaces that implement the Agent User Interaction Protocol (AG-UI). It provides real-time streaming communication between Kotlin applications and AI agents across Android, iOS, and JVM platforms.*Note:* This SDK is community contributed and maintained. Please reach out to mefinsf in the AG-UI Discord with any questions.

## Installation

Add the SDK to your Gradle project:

The client module automatically includes both `kotlin-core` and `kotlin-tools` as dependencies, giving you access to the complete SDK functionality.

For advanced use cases where you only need specific modules:

```
dependencies {
    // Core protocol types only (advanced)
    implementation("com.agui:kotlin-core:0.2.1")
    
    // Tools framework only (advanced) 
    implementation("com.agui:kotlin-tools:0.2.1")
}
```

## Architecture

The SDK follows a modular architecture with three main components:

### kotlin-client

High-level agent implementations and client infrastructure.

- **AgUiAgent**: Stateless client for cases where no ongoing context is needed or the agent manages all state server-side
- **StatefulAgUiAgent**: Stateful client that maintains conversation history and sends it with each request
- **HttpAgent**: Low-level HTTP transport implementation
- **AbstractAgent**: Base class for custom agent implementations

[Learn more about the Client module →](https://github.com/ag-ui-protocol/ag-ui/blob/main/docs/sdk/kotlin/client/overview)

### kotlin-core

Protocol types, events, and message definitions.

- **Events**: All AG-UI protocol event types and serialization
- **Types**: Protocol message types and state management
- **Serialization**: JSON handling with kotlinx.serialization

[Learn more about the Core module →](https://github.com/ag-ui-protocol/ag-ui/blob/main/docs/sdk/kotlin/core/overview)

### kotlin-tools

Tool execution framework for extending agent capabilities.

- **ToolExecutor**: Interface for implementing custom tools
- **ToolRegistry**: Tool registration and management
- **ToolExecutionManager**: Tool execution with circuit breaker patterns

[Learn more about the Tools module →](https://github.com/ag-ui-protocol/ag-ui/blob/main/docs/sdk/kotlin/tools/overview)

## Supported Platforms

| Platform | Status | Minimum Version |
| --- | --- | --- |
| Android | ✅ Stable | API 26+ |
| iOS | ✅ Stable | iOS 13+ |
| JVM | ✅ Stable | Java 11+ |

## Quick Start

### Conversational Agent

```
// Create a stateful agent for conversations
val chatAgent = StatefulAgUiAgent("https://your-agent-api.com/agent") {
    bearerToken = "your-api-token"
    systemPrompt = "You are a friendly conversational AI"
}

// Have a conversation with context
chatAgent.chat("Hello!").collect { /* ... */ }
chatAgent.chat("What's my name?").collect { state ->
    // Agent remembers previous context
}
```

Chunked protocol events (`TEXT_MESSAGE_CHUNK`, `TOOL_CALL_CHUNK`) are automatically rewritten into their corresponding start/content/end sequences, so Kotlin clients see the same structured events as non-chunked streams.

Thinking telemetry (`THINKING_*` events) is surfaced alongside normal messages, allowing UIs to indicate when an agent is reasoning internally before responding.

```
import com.agui.client.builders.*

// Create an agent with client-side tools
val agent = agentWithTools(
    url = "https://your-agent-api.com/agent",
    toolRegistry = toolRegistry {
        addTool(WeatherToolExecutor())    // Executes locally on client
        addTool(CalculatorToolExecutor()) // Executes locally on client
    }
) {
    bearerToken = "your-api-token"
}

// Agent can request client-side tool execution during conversation
agent.sendMessage("What's 15% tip on $85.50?").collect { state ->
    // Agent requests calculator tool, which runs locally on the client
}
```

**Note**: Tools registered with the SDK execute on the client device, not on the agent's server. This enables secure access to local device capabilities (location, camera, file system) while maintaining privacy and reducing server load.

## Authentication

The SDK supports multiple authentication methods:

```
// Bearer Token
AgUiAgent(url) {
    bearerToken = "your-token"
}

// API Key
AgUiAgent(url) {
    apiKey = "your-api-key"
}

// Basic Auth
AgUiAgent(url) {
    basicAuth("username", "password")
}
```

## Error Handling

```
agent.sendMessage("Hello").collect { state ->
    state.errors.forEach { error ->
        println("Error: ${error.message}")
    }
}
```

## State Management

```
// Access current state
val currentState = agent.currentState
println("Messages: ${currentState.messages.size}")

// Monitor state changes
agent.sendMessage("Hello").collect { state ->
    println("Updated state: ${state.messages.last()}")
}

// RAW and CUSTOM protocol events are surfaced for inspection
state.rawEvents?.forEach { raw ->
    println("Raw event from ${raw.source ?: "unknown"}: ${raw.event}")
}
state.customEvents?.forEach { custom ->
    println("Custom event ${custom.name}: ${custom.value}")
}

// Thinking telemetry stream
state.thinking?.let { thinking ->
    if (thinking.isThinking) {
        val latest = thinking.messages.lastOrNull().orEmpty()
        println("Agent is thinking: $latest")
    } else if (thinking.messages.isNotEmpty()) {
        println("Agent finished thinking: ${thinking.messages.joinToString()}")
    }
}
```