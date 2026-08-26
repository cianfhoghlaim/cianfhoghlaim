// swift-tools-version: 5.10
// tuatha-capture — macOS-native game capture daemon.
//
// Uses Apple's ScreenCaptureKit per-window content filter (the canonical
// Apple approach for game-window capture, per WWDC22/23 docs).
// Pipes CMSampleBuffer to AVAssetWriter with hevc_videotoolbox (Apple
// Silicon Media Engine, real-time 1080p60, ~2-5 Mbps).
//
// Phase 1: standalone daemon, you play the game normally.
// Phase 2 (stubbed): Hermes Agent computer-use controls the play via the
// same JSON-RPC socket; gate is TUATHA_HERMES_ENABLED env var.

import PackageDescription

let package = Package(
    name: "tuatha-capture",
    platforms: [
        .macOS(.v15)  // ScreenCaptureKit + AVAssetWriter HEVC path
    ],
    products: [
        .executable(name: "tuatha-capture", targets: ["tuatha-capture"])
    ],
    targets: [
        .executableTarget(
            name: "tuatha-capture",
            path: "Sources/tuatha-capture",
            resources: [],
            linkerSettings: [
                .linkedFramework("ScreenCaptureKit"),
                .linkedFramework("AVFoundation"),
                .linkedFramework("CoreMedia"),
                .linkedFramework("CoreVideo"),
                .linkedFramework("ImageIO"),
                .linkedFramework("AppKit"),
            ]
        )
    ]
)
