package types

import (
	"errors"
	"os"
	"strings"
	"syscall"
)

// IsProcessAlive checks if a process with the given PID is alive on the given hostname.
// If hostname doesn't match the current host, it returns true (cannot verify remote, assume alive).
// If hostname matches the current host, it checks if the PID exists.
// Permission errors are treated as "alive" (fail-safe: better to skip than wrongly remove a lock).
func IsProcessAlive(pid int, hostname string) bool {
	currentHost, err := os.Hostname()
	if err != nil {
		// Can't determine current hostname, assume process is alive (fail-safe)
		return true
	}

	// Case-insensitive hostname comparison to handle FQDN vs short name differences
	if !strings.EqualFold(hostname, currentHost) {
		return true
	}

	// Check if process exists on local host
	process, err := os.FindProcess(pid)
	if err != nil {
		// On Unix, FindProcess always succeeds, so this is unlikely
		return false
	}

	// Send signal 0 to check if process exists without actually sending a signal
	err = process.Signal(syscall.Signal(0))
	if err == nil {
		return true
	}

	// Only mark as dead on ESRCH (no such process)
	// EPERM (permission denied) and other errors => assume alive (fail-safe)
	var errno syscall.Errno
	if errors.As(err, &errno) && errno == syscall.ESRCH {
		return false
	}

	return true
}
