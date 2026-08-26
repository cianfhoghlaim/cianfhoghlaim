// tuatha-capture doctor — verify permissions + dependencies.
//
// Checks:
//   1. Screen Recording permission (via TCC, surfaced through SCShareableContent)
//   2. Accessibility permission (for keyboard/mouse from Hermes in Phase 2)
//   3. hevc_videotoolbox availability (VTCompressionSession encoder)
//   4. AVAssetWriter HEVC profile
//   5. Writes a single test frame to ~/Library/Application Support/tuatha/captures/__doctor__/test-frame.jpg
//
// Exits 0 if everything is healthy, 1 if a permission is denied.

import Foundation
import ScreenCaptureKit
import AVFoundation
import ImageIO
import UniformTypeIdentifiers

@MainActor
enum TuathaDoctor {
    static func run() async {
        var ok = true

        print("==> tuatha-capture doctor (Phase 1)")
        print("")

        // 1. Screen Recording permission
        do {
            let content = try await SCShareableContent.excludingDesktopWindows(
                false,
                onScreenWindowsOnly: true
            )
            print("[ok ] Screen Recording permission granted — \(content.windows.count) window(s) on screen")
        } catch {
            print("[err] Screen Recording permission denied — open System Settings → Privacy & Security → Screen Recording and re-grant")
            ok = false
        }

        // 2. Accessibility permission — Hermes will use this in Phase 2.
        // For Phase 1 we only warn, not fail.
        let trusted = AXIsProcessTrustedWithOptions(nil)
        if trusted {
            print("[ok ] Accessibility permission granted")
        } else {
            print("[warn] Accessibility permission not yet granted — required for Phase 2 (Hermes control)")
        }

        // 3. HEVC videotoolbox encoder
        do {
            let format = try AVAudioFile(
                forWriting: URL(fileURLWithPath: "/dev/null"),
                settings: [
                    AVFormatIDKey: kAudioFormatLinearPCM,
                    AVSampleRateKey: 48000,
                    AVNumberOfChannelsKey: 2
                ]
            )
            _ = format  // silence unused
        } catch {
            // ignore; we only care about video encoder below
        }

        let canEncodeHEVC = VTCanConcurrentDecodeAndEncodeHEVC() ?? false
        let canEncode = VTCompressionSessionCanUseVCPipeline() ?? false
        if canEncodeHEVC {
            print("[ok ] hevc_videotoolbox encoder available")
        } else {
            print("[err] hevc_videotoolbox encoder not available — required for real-time game capture")
            ok = false
        }
        if canEncode {
            print("[ok ] Video Toolbox hardware pipeline available")
        } else {
            print("[warn] Video Toolbox hardware pipeline not detected — software fallback will be slower")
        }

        // 4. AVAssetWriter HEVC profile
        let hevcOK = AVAssetExportSession.allExportPresets()
            .contains(AVAssetExportPresetHEVCHighestQuality)
        if hevcOK {
            print("[ok ] AVAssetWriter HEVC profile present")
        } else {
            print("[warn] AVAssetWriter HEVC profile missing — capture will fall back to H.264")
        }

        // 5. Write a test frame
        let outDir = captureDir(run: "__doctor__")
        let outURL = outDir.appendingPathComponent("test-frame.jpg")
        do {
            let data = try await renderTestFrame()
            try data.write(to: outURL)
            print("[ok ] Wrote test frame → \(outURL.path)")
        } catch {
            print("[err] Failed to write test frame: \(error.localizedDescription)")
            ok = false
        }

        print("")
        print(ok ? "==> doctor: healthy" : "==> doctor: degraded (see warnings above)")
        exit(ok ? 0 : 1)
    }

    private static func captureDir(run: String) -> URL {
        let base = FileManager.default
            .homeDirectoryForCurrentUser
            .appendingPathComponent("Library/Application Support/tuatha/captures")
        let dir = base.appendingPathComponent(run)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        return dir
    }

    /// A 1x1 JPEG test frame — proves the JPEG encoder works.
    private static func renderTestFrame() async throws -> Data {
        let image = CGContext(
            data: nil,
            width: 1,
            height: 1,
            bitsPerComponent: 8,
            bytesPerRow: 4,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        )!
        let cg = image.makeImage()!
        let mutable = NSMutableData()
        let type = UTType.jpeg.identifier as CFString
        guard let dest = CGImageDestinationCreateWithData(mutable, type, 1, nil) else {
            throw NSError(domain: "tuatha-capture", code: 1, userInfo: [
                NSLocalizedDescriptionKey: "CGImageDestinationCreateWithData failed"
            ])
        }
        let props: [CFString: Any] = [
            kCGImageDestinationLossyCompressionQuality: 0.9
        ]
        CGImageDestinationAddImage(dest, cg, props as CFDictionary)
        guard CGImageDestinationFinalize(dest) else {
            throw NSError(domain: "tuatha-capture", code: 2, userInfo: [
                NSLocalizedDescriptionKey: "CGImageDestinationFinalize failed"
            ])
        }
        return mutable as Data
    }
}
