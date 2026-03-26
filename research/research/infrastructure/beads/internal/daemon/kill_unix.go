//go:build unix

package daemon

import (
	"fmt"
	"syscall"
)

func killProcess(pid int) error {
	if err := syscall.Kill(pid, syscall.SIGTERM); err != nil {
		return fmt.Errorf("failed to send SIGTERM to PID %d: %w", pid, err)
	}
	return nil
}

func forceKillProcess(pid int) error {
	if err := syscall.Kill(pid, syscall.SIGKILL); err != nil {
		return fmt.Errorf("failed to send SIGKILL to PID %d: %w", pid, err)
	}
	return nil
}

func isProcessAlive(pid int) bool {
	// On Unix, sending signal 0 checks if process exists
	err := syscall.Kill(pid, 0)
	return err == nil
}
