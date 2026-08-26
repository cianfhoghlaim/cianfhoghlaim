// tuatha-capture — the main entry point.
//
// Two responsibilities:
//   1. Print doctor + version output (the SwiftCLI "doctor" pattern)
//   2. Boot the JSON-RPC daemon over a unix-domain socket
//
// The actual capture loop lives in Capture.swift; the JSON-RPC server
// lives in Daemon.swift; the launchd handshake in Launchd.swift.

import Foundation

@main
struct TuathaCapture {
    static func main() async {
        let args = CommandLine.arguments
        let subcommand = args.dropFirst().first ?? "doctor"

        switch subcommand {
        case "doctor":
            await TuathaDoctor.run()
        case "daemon":
            try? await TuathaDaemon.run()
        case "list-windows":
            await TuathaDaemon.listShareableWindows()
        case "version":
            print("tuatha-capture 0.1.0 (Phase 1 stub)")
        case "help", "--help", "-h":
            print("""
            tuatha-capture — Mac-native game capture for the Tuatha media-intel pipeline.

            Subcommands:
              doctor            Verify permissions + dependencies + write sample frame
              daemon            Start the JSON-RPC capture daemon (unix socket)
              list-windows      Enumerate the shareable windows on this Mac
              version           Print the version

            See ../README.md and ../LaunchAgent/com.ci.tuatha.capture.plist
            for the launchd setup.
            """)
        default:
            FileHandle.standardError.write(
                "unknown subcommand: \(subcommand)\n".data(using: .utf8)!
            )
            exit(2)
        }
    }
}
