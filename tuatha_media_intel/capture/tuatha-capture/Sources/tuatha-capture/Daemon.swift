// tuatha-capture daemon — the JSON-RPC server (unix-domain socket).
//
// Protocol (one JSON object per line, line-delimited):
//   request  → {"id": <int>, "method": <string>, "params": {...}}
//   response → {"id": <int>, "result": <any>}
//
// Methods:
//   start_run   {window_title, run_id}  → {run_dir}
//   stop_run    {}                      → {ok}
//   mark_event  {name}                  → {ok}
//   list_runs   {}                      → {runs: [...]}
//   hermes_ping {}                      → {hermes_enabled, phase}
//
// The socket path is /tmp/tuatha-capture.sock by default (env:
// TUATHA_CAPTURE_SOCKET). Phase 1 Hermes control is gated by the
// TUATHA_HERMES_ENABLED env var — defaults to false.

import Foundation
import ScreenCaptureKit

@MainActor
enum TuathaDaemon {
    static let daemon = TuathaCaptureDaemon()

    static func run() async throws {
        let sockPath = ProcessInfo.processInfo.environment["TUATHA_CAPTURE_SOCKET"]
            ?? "/tmp/tuatha-capture.sock"
        let url = URL(fileURLWithPath: sockPath)
        try? FileManager.default.removeItem(at: url)

        // AF_UNIX / POSIX listener via FileHandle (SwiftPM doesn't ship
        // a higher-level abstraction).
        let fd = socket(AF_UNIX, SOCK_STREAM, 0)
        guard fd >= 0 else {
            throw NSError(domain: "tuatha-capture", code: 10, userInfo: [
                NSLocalizedDescriptionKey: "socket() failed: \(String(cString: strerror(errno)))"
            ])
        }
        var addr = sockaddr_un()
        addr.sun_family = sa_family_t(AF_UNIX)
        let pathBytes = Array(sockPath.utf8)
        guard pathBytes.count < MemoryLayout.size(ofValue: addr.sun_path) else {
            throw NSError(domain: "tuatha-capture", code: 11, userInfo: [
                NSLocalizedDescriptionKey: "socket path too long"
            ])
        }
        withUnsafeMutablePointer(to: &addr.sun_path) { ptr in
            ptr.withMemoryRebound(to: CChar.self, capacity: pathBytes.count + 1) { dst in
                for (i, b) in pathBytes.enumerated() { dst[i] = CChar(b) }
            }
        }
        let bindResult = withUnsafePointer(to: &addr) {
            $0.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                bind(fd, $0, socklen_t(MemoryLayout<sockaddr_un>.size))
            }
        }
        guard bindResult == 0 else {
            throw NSError(domain: "tuatha-capture", code: 12, userInfo: [
                NSLocalizedDescriptionKey: "bind() failed: \(String(cString: strerror(errno)))"
            ])
        }
        guard listen(fd, 16) == 0 else {
            throw NSError(domain: "tuatha-capture", code: 13, userInfo: [
                NSLocalizedDescriptionKey: "listen() failed: \(String(cString: strerror(errno)))"
            ])
        }

        print("tuatha-capture daemon listening on unix://\(sockPath)", to: &stderr)
        Log.info("daemon up", extra: ["socket": sockPath])

        let q = DispatchQueue(label: "ci.tuatha.capture.accept")
        DispatchQueue.global(qos: .userInitiated).async {
            while true {
                let client = accept(fd, nil, nil)
                if client < 0 {
                    if errno == EINTR { continue }
                    Log.error("accept() failed", extra: ["errno": "\(errno)"])
                    continue
                }
                q.async { Task { await handle(client: client) } }
            }
        }
        // Park the main task on a long sleep — the daemon lives until killed.
        try await Task.sleep(nanoseconds: 60 * 60 * 1_000_000_000)
    }

    static func listShareableWindows() async {
        do {
            let content = try await SCShareableContent.excludingDesktopWindows(
                false,
                onScreenWindowsOnly: true
            )
            for win in content.windows {
                let title = win.title ?? "<untitled>"
                let owner = win.owningApplication?.applicationName ?? "<unknown>"
                let w = Int(win.frame.width), h = Int(win.frame.height)
                print("\(owner) — \(title) (\(w)x\(h))")
            }
        } catch {
            print("error: \(error.localizedDescription)", to: &stderr)
            exit(1)
        }
    }

    private static func handle(client fd: Int32) async {
        let handle = FileHandle(fileDescriptor: fd, closeOnDealloc: true)
        while true {
            let data: Data
            do {
                data = try handle.available().data
            } catch {
                return  // client closed
            }
            guard !data.isEmpty else { return }
            guard let raw = String(data: data, encoding: .utf8) else { continue }
            for line in raw.split(separator: "\n") {
                let trimmed = line.trimmingCharacters(in: .whitespacesAndNewlines)
                if trimmed.isEmpty { continue }
                let response = await dispatch(trimmed)
                let out = (response + "\n").data(using: .utf8)!
                try? handle.write(contentsOf: out)
            }
        }
    }

    private static func dispatch(_ line: String) async -> String {
        guard let data = line.data(using: .utf8),
              let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let id = obj["id"] as? Int,
              let method = obj["method"] as? String,
              let params = obj["params"] as? [String: Any] else {
            return #"{"id":null,"error":"invalid_request"}"#
        }
        do {
            let result: [String: Any]
            switch method {
            case "start_run":
                let runDir = try await daemon.startRun(
                    windowTitle: params["window_title"] as? String ?? "Hades",
                    runId: params["run_id"] as? String ?? ISO8601DateFormatter().string(from: Date())
                )
                result = ["run_dir": runDir.path]
            case "stop_run":
                await daemon.stopRun()
                result = ["ok": true]
            case "mark_event":
                await daemon.markEvent(params["name"] as? String ?? "event")
                result = ["ok": true]
            case "hermes_ping":
                let enabled = ProcessInfo.processInfo.environment["TUATHA_HERMES_ENABLED"] == "true"
                result = ["hermes_enabled": enabled, "phase": "1"]
            default:
                return #"{"id":\#(id),"error":"unknown_method"}"#
            }
            let resp: [String: Any] = ["id": id, "result": result]
            let json = try JSONSerialization.data(withJSONObject: resp)
            return String(data: json, encoding: .utf8) ?? #"{"id":\#(id),"error":"serialize"}"#
        } catch {
            return #"{"id":\#(id),"error":"\#(error.localizedDescription)"}"#
        }
    }
}

// MARK: - Logging

struct Log {
    static func info(_ msg: String, extra: [String: String] = [:]) {
        emit("info", msg, extra: extra)
    }
    static func error(_ msg: String, extra: [String: String] = [:]) {
        emit("error", msg, extra: extra)
    }
    private static func emit(_ level: String, _ msg: String, extra: [String: String]) {
        let payload = ["level": level, "msg": msg, "ts": ISO8601DateFormatter().string(from: Date())]
            .merging(extra) { _, n in n }
        if let data = try? JSONSerialization.data(withJSONObject: payload),
           let str = String(data: data, encoding: .utf8) {
            print(str)
        }
    }
}
