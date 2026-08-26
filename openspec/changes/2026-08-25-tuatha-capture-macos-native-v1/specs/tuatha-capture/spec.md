# Spec Delta: tuatha-capture

## ADDED Requirements

### Requirement: The capture daemon uses Apple ScreenCaptureKit for low-latency game capture

The system SHALL wrap Apple's ScreenCaptureKit per-window content
filter for game capture (the canonical Apple approach, per WWDC22/23).

#### Scenario: The daemon streams a game window at 60 fps

- **WHEN** the operator calls
  `{"method":"start_run","params":{"window_title":"Hades"}}`
  via the JSON-RPC socket
- **THEN** the daemon SHALL attach a `SCStream` with a
  `SCContentFilter(desktopIndependentWindow:)` for the named window
- **AND** configure `SCStreamConfiguration` with
  `minimumFrameInterval = CMTime(1, 60)`, `queueDepth = 5`, BGRA
  pixel format, audio off
- **AND** write each captured frame to
  `~/Library/Application Support/tuatha/captures/<run_id>/keyframes/frame-NNNNNN.jpg`.
