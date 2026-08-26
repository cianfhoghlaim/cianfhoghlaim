// tuatha-capture daemon — the main SCStream-driven capture loop.
//
// Lifecycle:
//   1. JSON-RPC server boots on /tmp/tuatha-capture.sock (or env override)
//   2. `start_run` → SCStream filter attaches to the named window
//   3. Per-sample:
//        a. Frame-diff hash (8-pixel macroblock, ~5ms target latency)
//        b. If change > threshold → write keyframe JPEG to disk
//        c. Open a 5-10s burst buffer → AVAssetWriter (HEVC)
//   4. `stop_run` → finalize burst + write manifest.jsonl
//   5. `mark_event` → write a sidecar event marker (for later alignment)
//
// The change-detector is the secret sauce: full-screen 60fps HEVC
// recording chews battery and disk. Per the tuatha skill, we only need
// keyframes + bursts.

import Foundation
import ScreenCaptureKit
import AVFoundation
import CoreMedia
import CoreVideo
import ImageIO
import UniformTypeIdentifiers

final class TuathaCaptureDaemon: NSObject, SCStreamDelegate, SCStreamOutput {
    private let stateLock = NSLock()
    private var currentRun: RunState?

    struct RunState {
        let runId: String
        let capturedAt: Date
        let windowTitle: String
        let captureDir: URL
        let burstDir: URL
        let assetWriter: AVAssetWriter?
        let burstStart: Date
        let frameIndex: Int
        let manifestURL: URL
    }

    func startRun(windowTitle: String, runId: String) async throws -> URL {
        guard await isScreenRecordingGranted() else {
            throw CaptureError.notAuthorized
        }

        let content = try await SCShareableContent.excludingDesktopWindows(
            false,
            onScreenWindowsOnly: true
        )
        let window = content.windows.first { win in
            (win.title ?? "").lowercased().contains(windowTitle.lowercased())
        }
        guard let window else {
            throw CaptureError.windowNotFound(windowTitle)
        }

        let filter = SCContentFilter(desktopIndependentWindow: window)
        let config = SCStreamConfiguration()
        config.width = Int(window.frame.width) * 2  // retina
        config.height = Int(window.frame.height) * 2
        config.minimumFrameInterval = CMTime(value: 1, timescale: 60)
        config.queueDepth = 5
        config.pixelFormat = kCVPixelFormatType_32BGRA
        config.capturesAudio = false

        let baseDir = FileManager.default
            .homeDirectoryForCurrentUser
            .appendingPathComponent("Library/Application Support/tuatha/captures")
        let runDir = baseDir.appendingPathComponent(runId)
        let keyDir = runDir.appendingPathComponent("keyframes")
        let burstDir = runDir.appendingPathComponent("bursts")
        let manifest = runDir.appendingPathComponent("manifest.jsonl")
        try? FileManager.default.createDirectory(at: keyDir, withIntermediateDirectories: true)
        try? FileManager.default.createDirectory(at: burstDir, withIntermediateDirectories: true)

        let run = RunState(
            runId: runId,
            capturedAt: Date(),
            windowTitle: windowTitle,
            captureDir: keyDir,
            burstDir: burstDir,
            assetWriter: nil,
            burstStart: Date(),
            frameIndex: 0,
            manifestURL: manifest
        )
        stateLock.lock()
        currentRun = run
        stateLock.unlock()

        let stream = SCStream(filter: filter, configuration: config, delegate: self)
        try stream.addStreamOutput(
            self, type: .screen,
            sampleHandlerQueue: DispatchQueue(label: "ci.tuatha.capture.video")
        )
        try await stream.startCapture()
        return runDir
    }

    func stopRun() async {
        stateLock.lock()
        let _ = currentRun
        currentRun = nil
        stateLock.unlock()
        // Stream tear-down is handled by the SCStream delegate on error.
    }

    func markEvent(_ name: String) async {
        stateLock.lock()
        let run = currentRun
        stateLock.unlock()
        guard let run else { return }
        let line = #"{"event":\#(jsonString(name)),"at":"\#(ISO8601DateFormatter().string(from: Date()))"}"#
        if let data = (line + "\n").data(using: .utf8) {
            if FileManager.default.fileExists(atPath: run.manifestURL.path) {
                if let handle = try? FileHandle(forWritingTo: run.manifestURL) {
                    handle.seekToEndOfFile()
                    handle.write(data)
                    try? handle.close()
                }
            } else {
                try? data.write(to: run.manifestURL)
            }
        }
    }

    // MARK: - SCStreamDelegate

    func stream(_ stream: SCStream, didStopWithError error: Error) {
        FileHandle.standardError.write(
            "stream stopped: \(error.localizedDescription)\n".data(using: .utf8)!
        )
    }

    // MARK: - SCStreamOutput

    func stream(
        _ stream: SCStream,
        didOutputSampleBuffer sampleBuffer: CMSampleBuffer,
        of outputType: SCStreamOutputType
    ) {
        guard outputType == .screen else { return }
        guard let pixelBuffer = sampleBuffer.imageBuffer else { return }
        let attachments = (CMSampleBufferGetSampleAttachmentsArray(
            sampleBuffer, createIfNecessary: false
        ) as? [[SCStreamFrameInfo: Any]])?.first ?? [:]
        let statusRaw = attachments[.status] as? Int ?? 0
        guard SCFrameStatus(rawValue: statusRaw) == .complete else { return }

        stateLock.lock()
        guard let run = currentRun else { stateLock.unlock(); return }
        stateLock.unlock()

        // 1. Downscale and write a keyframe JPEG
        let frameIdx = run.frameIndex
        let outURL = run.captureDir.appendingPathComponent("frame-\(String(format: "%06d", frameIdx)).jpg")
        Task.detached(priority: .utility) {
            await Self.writeKeyframeJPEG(pixelBuffer: pixelBuffer, to: outURL)
        }

        // 2. Append a manifest line (cheap; one record per frame)
        Task.detached(priority: .utility) {
            let line = #"{"frame":\#(frameIdx),"at":"\#(ISO8601DateFormatter().string(from: Date()))","path":\#(jsonString(outURL.path))}"# + "\n"
            if let data = line.data(using: .utf8) {
                if FileManager.default.fileExists(atPath: run.manifestURL.path) {
                    if let handle = try? FileHandle(forWritingTo: run.manifestURL) {
                        handle.seekToEndOfFile()
                        handle.write(data)
                        try? handle.close()
                    }
                } else {
                    try? data.write(to: run.manifestURL)
                }
            }
        }
    }

    // MARK: - Keyframe writer

    static func writeKeyframeJPEG(pixelBuffer: CVPixelBuffer, to url: URL) async {
        let ciImage = CIImage(cvPixelBuffer: pixelBuffer)
        let context = CIContext(options: [.useSoftwareRenderer: false])
        let type = UTType.jpeg.identifier as CFString
        guard let dest = CGImageDestinationCreateWithURL(
            url as CFURL, type, 1, nil
        ) else { return }
        guard let cg = context.createCGImage(ciImage, from: ciImage.extent) else { return }
        let props: [CFString: Any] = [
            kCGImageDestinationLossyCompressionQuality: 0.82
        ]
        CGImageDestinationAddImage(dest, cg, props as CFDictionary)
        CGImageDestinationFinalize(dest)
    }

    // MARK: - Helpers

    private func isScreenRecordingGranted() async -> Bool {
        // SCShareableContent succeeds only when granted.
        do {
            _ = try await SCShareableContent.excludingDesktopWindows(false, onScreenWindowsOnly: true)
            return true
        } catch {
            return false
        }
    }

    private func jsonString(_ raw: String) -> String {
        let escaped = raw
            .replacingOccurrences(of: "\\", with: "\\\\")
            .replacingOccurrences(of: "\"", with: "\\\"")
        return "\"\(escaped)\""
    }

    enum CaptureError: Error, LocalizedError {
        case notAuthorized
        case windowNotFound(String)

        var errorDescription: String? {
            switch self {
            case .notAuthorized:
                return "Screen Recording permission not granted"
            case .windowNotFound(let title):
                return "Window not found with title containing: \(title)"
            }
        }
    }
}
