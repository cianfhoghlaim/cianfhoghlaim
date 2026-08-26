# Change: tuatha-capture-macos-native (v1)

## Why

We need a macOS-native capture daemon that uses Apple's ScreenCaptureKit
per-window content filters + Apple Silicon `hevc_videotoolbox` for
real-time 1080p60 HEVC encoding. This is the canonical Apple approach
for low-latency game-window capture (per WWDC22/23 docs) and is the
only path that doesn't drop frames on M-series MacBooks.

The other candidate paths (OBS, Kap, VLC, ffmpeg x11grab) fail on
frame timing, multi-display support, or audio routing. Kap is what the
user currently uses; we replace it with this Swift daemon.

## What changes

- New Swift Package Manager project `tuatha_media_intel/capture/tuatha-capture/`.
- New LaunchAgent `tuatha_media_intel/capture/LaunchAgent/com.ci.tuatha.capture.plist`.

## Impact

- No affected specs (new surface).
- Affected skills:
  - `.agents/skills/browser-tools/` (no change — this is screen-capture, not browser).
  - `.agents/skills/tuatha/` (cross-reference the macOS capture path).

## Out of scope

- Hermes Agent control plane (Phase 2 stub is part of the
  `tuatha-media-intel-pipeline` change).
- Audio capture (the daemon captures screen frames only; audio is
  intentionally disabled in Phase 1).

## Verification

1. `swift build -c release` in `tuatha-capture/` succeeds.
2. `./tuatha-capture doctor` passes on M-series macOS 15+.
3. `./tuatha-capture list-windows` enumerates the visible game windows.
4. `./tuatha-capture daemon` listens on `/tmp/tuatha-capture.sock`.
5. The LaunchAgent loads and survives a `launchctl unload/load` cycle.
6. A first capture run writes a manifest + keyframes to
   `~/Library/Application Support/tuatha/captures/<run_id>/`.
