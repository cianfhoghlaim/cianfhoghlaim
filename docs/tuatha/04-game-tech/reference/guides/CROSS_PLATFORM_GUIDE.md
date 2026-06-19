# Cross-Platform Development Guide

Guide to building cross-platform applications for the Tuath Celtic MMO ecosystem.

## Overview

The Tuath platform targets multiple platforms:
- **Web**: Babylon.js + TanStack Start
- **Desktop**: Godot 4 + Rust
- **Mobile**: React Native or Kotlin Multiplatform
- **Backend**: Rust (SpacetimeDB, Axum)

### Reference Materials

| Resource | Path |
|----------|------|
| Kotlin Multiplatform SDK | `taighde/game/agui_kotlin/` |
| Swift LLM Abstraction | `taighde/game/AnyLanguageModel/` |
| React Native + Godot | `taighde/game/react-native-godot/` |
| UI Components | `taighde/game/react-native-reusables/` |
| Strategy Comparison | `taighde/game/Kotlin Multiplatform vs. React Native comparison.md` |

---

## Kotlin Multiplatform (KMP)

### Project Structure

```
shared/
├── src/
│   ├── commonMain/       # Shared code
│   │   └── kotlin/
│   │       ├── network/
│   │       ├── models/
│   │       └── utils/
│   ├── androidMain/      # Android-specific
│   │   └── kotlin/
│   ├── iosMain/          # iOS-specific
│   │   └── kotlin/
│   └── jvmMain/          # Desktop JVM
│       └── kotlin/
└── build.gradle.kts

androidApp/
├── src/main/
└── build.gradle.kts

iosApp/
├── iosApp/
└── iosApp.xcodeproj
```

### build.gradle.kts

```kotlin
plugins {
    kotlin("multiplatform") version "1.9.22"
    kotlin("plugin.serialization") version "1.9.22"
    id("com.android.library")
}

kotlin {
    // Targets
    androidTarget()

    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "TuathShared"
            isStatic = true
        }
    }

    jvm("desktop")

    sourceSets {
        val commonMain by getting {
            dependencies {
                // Networking
                implementation("io.ktor:ktor-client-core:2.3.7")
                implementation("io.ktor:ktor-client-content-negotiation:2.3.7")
                implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.7")

                // Serialization
                implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.2")

                // Coroutines
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")

                // DateTime
                implementation("org.jetbrains.kotlinx:kotlinx-datetime:0.5.0")
            }
        }

        val androidMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-okhttp:2.3.7")
            }
        }

        val iosMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-darwin:2.3.7")
            }
        }

        val desktopMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-cio:2.3.7")
            }
        }
    }
}

android {
    namespace = "ie.cianfhoghlaim.tuath.shared"
    compileSdk = 34

    defaultConfig {
        minSdk = 24
    }
}
```

### Shared Models

```kotlin
// shared/src/commonMain/kotlin/models/Player.kt

package ie.cianfhoghlaim.tuath.shared.models

import kotlinx.serialization.Serializable

@Serializable
data class Player(
    val id: String,
    val name: String,
    val level: Int,
    val xp: Int,
    val currentZone: String,
    val position: Position,
    val vocabularyLearned: Int,
    val questsCompleted: Int
)

@Serializable
data class Position(
    val x: Float,
    val y: Float,
    val z: Float,
    val rotation: Float
)

@Serializable
data class GameState(
    val player: Player,
    val nearbyPlayers: List<Player>,
    val currentQuest: Quest?
)

@Serializable
data class Quest(
    val id: String,
    val title: String,
    val celticTitle: String,
    val description: String,
    val objectives: List<QuestObjective>,
    val rewards: QuestRewards
)

@Serializable
data class QuestObjective(
    val id: String,
    val description: String,
    val current: Int,
    val target: Int,
    val completed: Boolean
)

@Serializable
data class QuestRewards(
    val xp: Int,
    val items: List<String>,
    val vocabulary: List<String>
)
```

### Shared Network Layer

```kotlin
// shared/src/commonMain/kotlin/network/TuathApiClient.kt

package ie.cianfhoghlaim.tuath.shared.network

import ie.cianfhoghlaim.tuath.shared.models.*
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.plugins.websocket.*
import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.serialization.json.Json

class TuathApiClient(
    private val baseUrl: String = "https://api.tuath.cianfhoghlaim.dev"
) {
    private val httpClient = HttpClient {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                prettyPrint = true
            })
        }
        install(WebSockets)
    }

    private var sessionToken: String? = null

    // Authentication
    suspend fun getNonce(): AuthNonce {
        return httpClient.get("$baseUrl/auth/nonce").body()
    }

    suspend fun verifySignature(message: String, signature: String): AuthResult {
        val result: AuthResult = httpClient.post("$baseUrl/auth/verify") {
            contentType(ContentType.Application.Json)
            setBody(VerifyRequest(message, signature))
        }.body()

        sessionToken = result.sessionId
        return result
    }

    // Player
    suspend fun getPlayer(): Player {
        return httpClient.get("$baseUrl/game/player") {
            header("Authorization", "Bearer $sessionToken")
        }.body()
    }

    // Search
    suspend fun searchCurriculum(
        query: String,
        language: String? = null,
        level: String? = null
    ): SearchResults {
        return httpClient.get("$baseUrl/curriculum/search") {
            parameter("query", query)
            language?.let { parameter("language", it) }
            level?.let { parameter("level", it) }
        }.body()
    }

    // Streaming chat
    fun streamChat(message: String, context: Map<String, String>): Flow<AgentEvent> = flow {
        // SSE streaming implementation
        httpClient.preparePost("$baseUrl/copilotkit/stream") {
            header("X-Session-ID", sessionToken)
            contentType(ContentType.Application.Json)
            setBody(ChatRequest(message, context))
        }.execute { response ->
            // Parse SSE events
            // emit(AgentEvent(...))
        }
    }

    fun close() {
        httpClient.close()
    }
}

@Serializable
data class AuthNonce(val nonce: String, val expiresAt: String)

@Serializable
data class VerifyRequest(val message: String, val signature: String)

@Serializable
data class AuthResult(
    val success: Boolean,
    val address: String,
    val sessionId: String,
    val playerId: String
)

@Serializable
data class ChatRequest(val message: String, val context: Map<String, String>)

@Serializable
data class SearchResults(val results: List<SearchResult>, val total: Int)

@Serializable
data class SearchResult(
    val id: String,
    val title: String,
    val content: String,
    val score: Float
)
```

### Platform-Specific Implementations

```kotlin
// shared/src/commonMain/kotlin/platform/Platform.kt

package ie.cianfhoghlaim.tuath.shared.platform

expect class Platform() {
    val name: String
    val version: String

    fun getDeviceId(): String
    fun getPreferredLanguage(): String
    fun openUrl(url: String)
}

// shared/src/androidMain/kotlin/platform/Platform.kt

package ie.cianfhoghlaim.tuath.shared.platform

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import java.util.Locale

actual class Platform(private val context: Context) {
    actual val name: String = "Android"
    actual val version: String = Build.VERSION.RELEASE

    actual fun getDeviceId(): String {
        return android.provider.Settings.Secure.getString(
            context.contentResolver,
            android.provider.Settings.Secure.ANDROID_ID
        )
    }

    actual fun getPreferredLanguage(): String {
        return Locale.getDefault().language
    }

    actual fun openUrl(url: String) {
        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(intent)
    }
}

// shared/src/iosMain/kotlin/platform/Platform.kt

package ie.cianfhoghlaim.tuath.shared.platform

import platform.UIKit.UIDevice
import platform.UIKit.UIApplication
import platform.Foundation.NSURL
import platform.Foundation.NSLocale

actual class Platform {
    actual val name: String = "iOS"
    actual val version: String = UIDevice.currentDevice.systemVersion

    actual fun getDeviceId(): String {
        return UIDevice.currentDevice.identifierForVendor?.UUIDString ?: ""
    }

    actual fun getPreferredLanguage(): String {
        return NSLocale.preferredLanguages.firstOrNull() as? String ?: "en"
    }

    actual fun openUrl(url: String) {
        NSURL.URLWithString(url)?.let { nsUrl ->
            UIApplication.sharedApplication.openURL(nsUrl)
        }
    }
}
```

---

## Swift Integration

### AnyLanguageModel

```swift
// Sources/AnyLanguageModel/LLMProvider.swift

import Foundation

public protocol LLMProvider {
    func generate(prompt: String, options: GenerationOptions) async throws -> String
    func stream(prompt: String, options: GenerationOptions) -> AsyncThrowingStream<String, Error>
}

public struct GenerationOptions {
    public var maxTokens: Int
    public var temperature: Double
    public var topP: Double
    public var stopSequences: [String]

    public init(
        maxTokens: Int = 1000,
        temperature: Double = 0.7,
        topP: Double = 0.9,
        stopSequences: [String] = []
    ) {
        self.maxTokens = maxTokens
        self.temperature = temperature
        self.topP = topP
        self.stopSequences = stopSequences
    }
}

// Anthropic implementation
public class AnthropicProvider: LLMProvider {
    private let apiKey: String
    private let model: String

    public init(apiKey: String, model: String = "claude-3-haiku-20240307") {
        self.apiKey = apiKey
        self.model = model
    }

    public func generate(prompt: String, options: GenerationOptions) async throws -> String {
        let url = URL(string: "https://api.anthropic.com/v1/messages")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue(apiKey, forHTTPHeaderField: "x-api-key")
        request.setValue("2023-06-01", forHTTPHeaderField: "anthropic-version")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body: [String: Any] = [
            "model": model,
            "max_tokens": options.maxTokens,
            "messages": [
                ["role": "user", "content": prompt]
            ]
        ]

        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, _) = try await URLSession.shared.data(for: request)
        let response = try JSONDecoder().decode(AnthropicResponse.self, from: data)

        return response.content.first?.text ?? ""
    }

    public func stream(prompt: String, options: GenerationOptions) -> AsyncThrowingStream<String, Error> {
        AsyncThrowingStream { continuation in
            Task {
                // SSE streaming implementation
            }
        }
    }
}

struct AnthropicResponse: Decodable {
    let content: [ContentBlock]
}

struct ContentBlock: Decodable {
    let type: String
    let text: String
}
```

### iOS App Integration

```swift
// TuathApp/Sources/TuathClient.swift

import Foundation
import TuathShared  // KMP shared module

@MainActor
class TuathClient: ObservableObject {
    private let api: TuathApiClient
    private let llm: LLMProvider

    @Published var player: Player?
    @Published var isAuthenticated = false
    @Published var currentZone: String = "gaeltacht"

    init() {
        self.api = TuathApiClient(baseUrl: "https://api.tuath.cianfhoghlaim.dev")
        self.llm = AnthropicProvider(apiKey: Config.anthropicApiKey)
    }

    func authenticate(message: String, signature: String) async throws {
        let result = try await api.verifySignature(message: message, signature: signature)

        if result.success {
            isAuthenticated = true
            player = try await api.getPlayer()
        }
    }

    func searchCurriculum(query: String) async throws -> [SearchResult] {
        let results = try await api.searchCurriculum(
            query: query,
            language: "ga",
            level: nil
        )
        return results.results
    }

    func chat(message: String) async throws -> String {
        // Use local LLM for simple queries
        let prompt = """
        You are a Celtic language tutor helping with Irish (Gaeilge).

        User: \(message)

        Respond helpfully in both English and Irish.
        """

        return try await llm.generate(
            prompt: prompt,
            options: GenerationOptions(maxTokens: 500)
        )
    }
}
```

---

## React Native Integration

### React Native + Godot

```typescript
// src/components/GodotGame.tsx

import React, { useRef, useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import { GodotView, GodotEngine } from 'react-native-godot';

interface GodotGameProps {
  zone: string;
  onPlayerMove: (position: { x: number; y: number; z: number }) => void;
  onInteraction: (npcId: string) => void;
}

export function GodotGame({ zone, onPlayerMove, onInteraction }: GodotGameProps) {
  const godotRef = useRef<GodotEngine>(null);

  useEffect(() => {
    // Load zone when it changes
    godotRef.current?.callMethod('Game', 'load_zone', [zone]);
  }, [zone]);

  const handleGodotMessage = (method: string, args: any[]) => {
    switch (method) {
      case 'player_moved':
        onPlayerMove({
          x: args[0],
          y: args[1],
          z: args[2],
        });
        break;
      case 'npc_interaction':
        onInteraction(args[0]);
        break;
    }
  };

  return (
    <View style={styles.container}>
      <GodotView
        ref={godotRef}
        style={styles.game}
        projectPath="res://project.godot"
        onMessage={handleGodotMessage}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  game: {
    flex: 1,
  },
});
```

### Shared UI Components

```typescript
// src/components/VocabularyCard.tsx

import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Volume2 } from 'lucide-react-native';

interface VocabularyCardProps {
  english: string;
  celtic: string;
  pronunciation: string;
  language: 'ga' | 'cy' | 'gd';
  onPlayAudio?: () => void;
  onLearn?: () => void;
}

export function VocabularyCard({
  english,
  celtic,
  pronunciation,
  language,
  onPlayAudio,
  onLearn,
}: VocabularyCardProps) {
  const languageNames = {
    ga: 'Gaeilge',
    cy: 'Cymraeg',
    gd: 'Gàidhlig',
  };

  return (
    <Card>
      <CardHeader>
        <Text style={styles.languageLabel}>{languageNames[language]}</Text>
      </CardHeader>
      <CardContent>
        <Text style={styles.celtic}>{celtic}</Text>
        <Text style={styles.pronunciation}>/{pronunciation}/</Text>
        <Text style={styles.english}>{english}</Text>

        <View style={styles.actions}>
          {onPlayAudio && (
            <Pressable onPress={onPlayAudio} style={styles.audioButton}>
              <Volume2 size={20} color="#666" />
            </Pressable>
          )}
          {onLearn && (
            <Button onPress={onLearn}>Learn</Button>
          )}
        </View>
      </CardContent>
    </Card>
  );
}

const styles = StyleSheet.create({
  languageLabel: {
    fontSize: 12,
    color: '#666',
    textTransform: 'uppercase',
  },
  celtic: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  pronunciation: {
    fontSize: 14,
    color: '#888',
    fontStyle: 'italic',
    marginBottom: 8,
  },
  english: {
    fontSize: 16,
    color: '#333',
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 16,
  },
  audioButton: {
    padding: 8,
  },
});
```

---

## Shared Business Logic

### Cross-Platform State Management

```kotlin
// shared/src/commonMain/kotlin/state/GameStateManager.kt

package ie.cianfhoghlaim.tuath.shared.state

import ie.cianfhoghlaim.tuath.shared.models.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class GameStateManager {
    private val _gameState = MutableStateFlow<GameState?>(null)
    val gameState: StateFlow<GameState?> = _gameState.asStateFlow()

    private val _vocabularyProgress = MutableStateFlow<Map<String, Boolean>>(emptyMap())
    val vocabularyProgress: StateFlow<Map<String, Boolean>> = _vocabularyProgress.asStateFlow()

    fun updatePlayer(player: Player) {
        _gameState.value = _gameState.value?.copy(player = player)
            ?: GameState(player = player, nearbyPlayers = emptyList(), currentQuest = null)
    }

    fun learnWord(word: String) {
        val current = _vocabularyProgress.value.toMutableMap()
        current[word] = true
        _vocabularyProgress.value = current
    }

    fun calculateXpForLevel(level: Int): Int {
        // Exponential XP curve
        return (100 * kotlin.math.pow(1.5, (level - 1).toDouble())).toInt()
    }

    fun getXpProgress(player: Player): Float {
        val currentLevelXp = calculateXpForLevel(player.level)
        val nextLevelXp = calculateXpForLevel(player.level + 1)
        val xpInLevel = player.xp - currentLevelXp
        val xpNeeded = nextLevelXp - currentLevelXp
        return xpInLevel.toFloat() / xpNeeded.toFloat()
    }
}
```

---

## Build and Deploy

### iOS Build

```bash
# Build KMP framework
./gradlew :shared:assembleXCFramework

# Copy to iOS project
cp -R shared/build/XCFrameworks/release/TuathShared.xcframework iosApp/

# Build iOS app
cd iosApp
xcodebuild -project iosApp.xcodeproj -scheme iosApp -destination 'platform=iOS Simulator,name=iPhone 15'
```

### Android Build

```bash
# Build Android app
./gradlew :androidApp:assembleRelease

# Install on device
adb install androidApp/build/outputs/apk/release/androidApp-release.apk
```

### React Native Build

```bash
# iOS
cd TuathMobile
npx react-native run-ios

# Android
npx react-native run-android
```

---

## Related Documentation

- [iOS Strategy](../../../05-ios-ml/iOS%20App%20Development%20Ecosystem%20Strategy.md)
- [KMP vs RN Comparison](../../../07-clippings/Kotlin%20Multiplatform%20vs.%20React%20Native_%20A%20cross-platform%20comparison%20_%20Kotlin%20Multiplatform.md)
- [SpacetimeDB Guide](./SPACETIMEDB_GUIDE.md)
