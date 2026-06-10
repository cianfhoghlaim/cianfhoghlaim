---
title: "🌉 How to Use Swift Inside Kotlin Multiplatform: The iOS Bridge Explained (with a Real Example)"
source: "https://medium.com/@houssembababendermel/how-to-use-swift-inside-kotlin-multiplatform-the-ios-bridge-explained-with-a-real-example-63fea919d355"
author:
  - "[[Houssam Eddine Baba Bendermel]]"
published: 2025-10-19
created: 2025-12-29
description: "🌉 How to Use Swift Inside Kotlin Multiplatform: The iOS Bridge Explained (with App Review Dialog as Example) Kotlin Multiplatform (KMP) lets you share business logic between Android and iOS — …"
tags:
  - "clippings"
---
[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*pEn5RZ7INq0xkHaHQ4Wlwg.png)

Kotlin Multiplatform (KMP) lets you share business logic between Android and iOS — but what about **iOS-only features**, like asking users to rate your app?  
KMP doesn’t have direct access to Swift APIs such as `SKStoreReviewController`.

That’s where **Swift bridges** come in.

In this article, we’ll take a **practical use case** — asking users for a review — and show how to build a Swift bridge, connect it to Kotlin, and call it seamlessly from shared code.

By the end, you’ll be able to:

- Call Swift or Objective-C code directly from Kotlin
- Share it across your iOS app
- Do it all without Cocoapods 🎉

## 🧠 Why You Need a Bridge

KMP can’t directly talk to iOS-only APIs (like `StoreKit`, `UIKit`, or `AppKit`), so you need a way to “bridge” them.

A **bridge** is a tiny Swift class that’s exposed to Kotlin via the `swiftklib` Gradle plugin.  
Think of it as saying:

> *“Hey Kotlin, this Swift class exists — and you can call it just like any other Kotlin function.”*

## ⚙️ Step 1: Create the Swift Bridge File

In your iOS project, create a new file at:

```c
iosApp/iosApp/bridges/ReviewBridge.swift
```

Add this code:

```c
import StoreKit
import UIKit

@objc public class ReviewBridge: NSObject {
    @objc public static func requestReview() {
        if #available(iOS 14.0, *) {
            if let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene {
                SKStoreReviewController.requestReview(in: scene)
            }
        } else {
            // Fallback for iOS < 14 (optional)
            SKStoreReviewController.requestReview()
        }
    }
}
```

✅ **What this does:**

- Uses Apple’s native `SKStoreReviewController`
- Works on both modern and older iOS versions
- Can be triggered from Kotlin shared code

## 🧩 Step 2: Define the Expect Class in Kotlin

In your **commonMain** source set, define what you “expect” to exist:

```c
package core.presentation.utils

expect class FeedbackManager(context: Any = Unit) {
    fun showFeedBackDialog()
}
```

This tells Kotlin that there will be platform-specific implementations on Android and iOS.

## 🧩 Step 3: Set Up Gradle (The Secret Sauce)

To connect your Swift bridge to Kotlin, add this to your `libs.versions.toml`:

```c
[plugins]
swiftklib = { id = "io.github.ttypic.swiftklib", version = "0.5.4" }
```

Then in your shared module `build.gradle.kts`:

```c
plugins {
    ...
    alias(libs.plugins.swiftklib)
}
```

## Register the Swift Bridge

at the bottom of your shared module `build.gradle.kts` file:

```c
swiftklib {
      create("bridges") {
          path = file("../iosApp/iosApp/bridges")
          packageName("com.company.project.bridges")
      }
  }
```

## Link the Bridge to iOS Targets

```c
kotlin {
  ...
   listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "ComposeApp"
            isStatic = true
            // Add linker flags to resolve duplicate library warnings
            linkerOpts("-dead_strip")
        }

        iosTarget.compilations {
            val main by getting {
                cinterops {
                    create("bridges")
                }
            }
        }
    }
  ...
}
```

## 🍎 Step 4: Implement It on iOS

After syncing:

In your **iosMain** source set:

```c
package core.presentation.utils

import kotlinx.cinterop.ExperimentalForeignApi
import com.company.project.bridges.ReviewBridge

actual class FeedbackManager actual constructor(context: Any) {
    @OptIn(ExperimentalForeignApi::class)
    actual fun showFeedBackDialog() {
        ReviewBridge.requestReview()
    }
}
```

✅ This calls your **Swift bridge** directly when `showFeedBackDialog()` is called from Kotlin.

## 🤖 Step 5: Implement It on Android

In your **androidMain** source set:

```c
package core.presentation.utils

import android.content.Context
import com.google.android.play.core.review.ReviewManagerFactory
actual class FeedbackManager actual constructor(private val context: Any) {
    fun context(): Context = context as Context
    actual fun showFeedBackDialog() {
        val manager = ReviewManagerFactory.create(context())
        val request = manager.requestReviewFlow()
        ActivityProvider.getActivity()?.let { activity ->
            request.addOnCompleteListener { task ->
                if (task.isSuccessful) {
                    val reviewInfo = task.result
                    manager.launchReviewFlow(activity, reviewInfo)
                }
            }
        }
    }
}
```

✅ This uses **Google Play Core’s in-app review API**, so both platforms behave natively.

## 🧰 Don’t Forget the Dependencies

Add these to your `**libs.versions.toml**`:

```c
android-review = "2.0.2"

android-review = { module = "com.google.android.play:review", version = "android-review" }
android-review-ktx = { module = "com.google.android.play:review-ktx", version = "android-review" }
```

Then include them in your shared module `build.gradle.kts` file, either in the android scope or in the androidMain depencencies scope:

```c
dependencies {
    implementation(libs.android.review)
    implementation(libs.android.review.ktx)
}
```

📝 **Note:** These libraries are required to access the Google Play review API (`ReviewManagerFactory`, `ReviewInfo`, etc.). Without them, your Android implementation won’t compile.

## 🧱 Step 6 (Optional): Add Koin Dependency Injection

If you’re using **Koin**, you can inject the platform-specific FeedbackManager easily:

**iOS**

```c
package core.di

import core.data.local.dataStore.createDataStore
import core.data.utils.NetworkChecker
import core.presentation.utils.FeedbackManager
import org.koin.dsl.module
actual val corePlatformSpecificModule = module {
    single { createDataStore() }
    single { NetworkChecker() }
    single { FeedbackManager() }
}
```

**Android**

```c
package core.di

import core.presentation.utils.FeedbackManager
import org.koin.android.ext.koin.androidContext
import org.koin.dsl.module

actual val corePlatformSpecificModule = module {
    single { FeedbackManager(androidContext()) }
}
```

## 🎬 Step 7: Use It From Kotlin (e.g. ViewModel)

You can call this from your shared `ViewModel` or `UseCase`:

```c
class SettingsViewModel(
    private val feedbackManager: FeedbackManager
) : ViewModel() {
    fun askForReview() {
        feedbackManager.showFeedBackDialog()
    }
}
```

✅ On Android → Opens Google Play review dialog  
✅ On iOS → Triggers native `SKStoreReviewController`

### 📱 Notes on Using the iOS Review Dialog

It’s best to call `feedbackManager.showFeedBackDialog()` only after the user has meaningfully interacted with your app — for example, after completing several tasks, for example: using a feature multiple times.  
This ensures Apple’s review prompt feels natural and isn’t dismissed immediately.

🧩 **System-Controlled Behavior**

- `SKStoreReviewController` is fully controlled by iOS — you can *ask* for a review, but the system decides whether to actually show the dialog based on factors like usage frequency and previous prompts.
- You **cannot force** it to appear every time, even in production.
- During development or on the simulator, the dialog may appear visually, but you **can’t actually submit** a review — that’s only possible in a fully deployed App Store build.

💡 **Testing Tip:**  
To verify your integration, just call `feedbackManager.showFeedBackDialog()` and confirm that no errors occur — that’s enough to ensure it will work once the app is live.

📝 **Note:**  
Both `SKStoreReviewController` (iOS) and the Google Play review API (Android) are **system-controlled** — you can only *request* a review, not force it.

If you want to add a dedicated “Leave a Review” button instead, just open the store link directly:

**iOS:**

```c
val uriHandler = LocalUriHandler.current
uriHandler.openUri("https://apps.apple.com/app/id{your_app_id}?action=write-review")
```

**Android:**

```c
val uriHandler = LocalUriHandler.current
uriHandler.openUri("https://play.google.com/store/apps/details?id=$appPackageName")
```

This will take users straight to your app’s review page on the store.

## 🔁 (Optional) Adapting Existing Tasks

If you’ve followed the approach from my previous article  
👉 [*\[How I Fixed My KMP iOS Build: From 20-Minute Builds to Lightning Fast\]*](https://medium.com/@houssembababendermel/how-i-fixed-my-kmp-ios-build-from-20-minute-builds-to-lightning-fast-c4f0f5c102b0),  
you can adapt the same **packForXcode** task to include your Swift bridges like this:

```c
val bridgeDir = file("bridges/iosMain/swift")

tasks.register("packForXcode", Sync::class) {
    // --- Task setup ---
    group = "build" // Appears under the "Build" group in Gradle
    description = "Package Kotlin framework and Swift bridges for Xcode"

    val targetDir = layout.buildDirectory.dir("xcode-frameworks").get().asFile // Output folder for Xcode

    // --- Build configuration ---
    val mode = (project.findProperty("configuration") as? String)?.uppercase() ?: "DEBUG" // Build mode: DEBUG/RELEASE
    val sdkName = (project.findProperty("sdk") as? String) ?: "iphonesimulator"           // SDK passed by Xcode
    val isDevice = sdkName.startsWith("iphoneos")                                         // True if real device build
    val target = if (isDevice) "iosArm64" else "iosSimulatorArm64"                        // Select target platform

    // --- Framework setup ---
    val framework = kotlin.targets
        .getByName<KotlinNativeTarget>(target)
        .binaries
        .getFramework(mode) // Fetch correct .framework binary

    // --- Gradle optimizations ---
    dependsOn(framework.linkTaskProvider)              // Make sure the framework is built before packaging
    dependsOn("prepareComposeResourcesTaskForCommonMain") // Ensure Compose resources are ready

    from({ framework.outputDirectory }) // Include the compiled .framework files
    from(bridgeDir) {                   // Include Swift bridge files
        include("*.swift")              // Only Swift files
        into("Sources")                 // Place them under Sources/ for Xcode visibility
    }

    into(targetDir) // Destination directory for final output

    // --- Hooks ---
    doFirst {
        println("📦 Including Swift bridges from: $bridgeDir")
    }

    doLast {
        println("✅ Framework and bridges packaged to: $targetDir")
    }
}
```

## 🧠 When to Use Swift Bridges

Use this approach for:

- Native dialogs (`SKStoreReviewController`, `UIAlertController`)
- Native SDKs without Kotlin wrappers (e.g., Sign in with Apple)
- iOS-specific utilities (permissions, Apple Pay, Haptics)

Avoid it for shared logic like data or networking — keep that in Kotlin.

## 🏁 Final Thoughts

With Swift bridges, you can **unlock 100% of iOS features** while keeping your core logic shared in Kotlin.  
No Cocoapods. No manual frameworks. No frustration.

You can reuse this same pattern for:

In-app updates

- Push notification settings
- Apple Sign-In
- Payment integrations

Once you get the hang of this setup, **Swift becomes just another tool in your Kotlin toolbox** 🧰

I’m a software engineer with experience in mobile and backend development, working with Kotlin Multiplatform, Spring Boot.

## More from Houssam Eddine Baba Bendermel

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--63fea919d355---------------------------------------)