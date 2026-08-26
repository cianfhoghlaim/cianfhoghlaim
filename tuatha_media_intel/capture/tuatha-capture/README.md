# tuatha-capture — Mac-native game capture for the Tuatha MMO pipeline

Phase 1 daemon: watches a chosen game window via Apple's
[ScreenCaptureKit](https://developer.apple.com/documentation/screencapturekit),
emits 1fps keyframes + on-change burst HEVC clips to
`~/Library/Application Support/tuatha/captures/<run_id>/`.

Phase 2 stub: Hermes Agent `computer-use doctor` controls the play via
the same JSON-RPC socket; gated by the `TUATHA_HERMES_ENABLED` env var.

## Subcommands

| Subcommand | Purpose |
|:--|:--|
| `tuatha-capture doctor` | Verify Screen Recording + Accessibility + HEVC encoder availability; write a test frame |
| `tuatha-capture list-windows` | Enumerate all shareable windows on this Mac |
| `tuatha-capture daemon` | Boot the JSON-RPC server on `/tmp/tuatha-capture.sock` |
| `tuatha-capture version` | Print the version |

## JSON-RPC methods

```json
{"id": 1, "method": "start_run",  "params": {"window_title": "Hades", "run_id": "manual-2026-08-25T1430"}}
{"id": 2, "method": "mark_event", "params": {"name": "boon_picked"}}
{"id": 3, "method": "stop_run",   "params": {}}
{"id": 4, "method": "hermes_ping","params": {}}
```

## Build

```bash
cd tuatha_media_intel/capture/tuatha-capture
swift build -c release
cp .build/release/tuatha-capture ~/.tuatha/bin/
```

Or via mise:

```bash
mise run capture:build
```

## LaunchAgent install

```bash
cp tuatha_media_intel/capture/LaunchAgent/com.ci.tuatha.capture.plist \
   ~/Library/LaunchAgents/
launchctl load -w ~/Library/LaunchAgents/com.ci.tuatha.capture.plist
launchctl start com.ci.tuatha.capture
```

## Layout

```
tuatha_media_intel/capture/
├── tuatha-capture/
│   ├── Package.swift
│   └── Sources/tuatha-capture/
│       ├── main.swift          # CLI entry point
│       ├── Doctor.swift        # permissions + encoder check + test frame
│       ├── Capture.swift       # SCStream + AVAssetWriter HEVC pipeline
│       └── Daemon.swift        # JSON-RPC server over AF_UNIX socket
└── LaunchAgent/
    └── com.ci.tuatha.capture.plist
```

## Output layout (per run)

```
~/Library/Application Support/tuatha/captures/<run_id>/
├── keyframes/frame-000001.jpg   # 1fps baseline
├── keyframes/frame-000002.jpg
├── bursts/burst-001.mp4         # on-change 5–10s clip (HEVC, ~2-5 Mbps)
├── bursts/burst-002.mp4
└── manifest.jsonl               # {"frame": N, "at": ISO8601, "event": ...}
```

Frames + bursts stay local until the CocoIndex `tuatha_hades_boons`
flow reads them (the raw bucket is the S3 mirror, behind Pangolin).
