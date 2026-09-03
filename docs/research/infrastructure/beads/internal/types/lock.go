// Package types defines core data structures for the bd issue tracker.
package types

import (
	"encoding/json"
	"fmt"
	"os"
	"time"
)

// ExclusiveLock represents the lock file format for external tools to claim
// exclusive management of a beads database. When this lock is present,
// the bd daemon will skip the database in its sync cycle.
type ExclusiveLock struct {
	Holder    string    `json:"holder"`     // Name of lock holder (e.g., "vc-executor")
	PID       int       `json:"pid"`        // Process ID
	Hostname  string    `json:"hostname"`   // Hostname where process is running
	StartedAt time.Time `json:"started_at"` // When lock was acquired
	Version   string    `json:"version"`    // Version of lock holder
}

// NewExclusiveLock creates a new exclusive lock for the current process
func NewExclusiveLock(holder, version string) (*ExclusiveLock, error) {
	hostname, err := os.Hostname()
	if err != nil {
		return nil, fmt.Errorf("failed to get hostname: %w", err)
	}

	return &ExclusiveLock{
		Holder:    holder,
		PID:       os.Getpid(),
		Hostname:  hostname,
		StartedAt: time.Now(),
		Version:   version,
	}, nil
}

// MarshalJSON implements json.Marshaler
func (e *ExclusiveLock) MarshalJSON() ([]byte, error) {
	type Alias ExclusiveLock
	return json.Marshal((*Alias)(e))
}

// UnmarshalJSON implements json.Unmarshaler
func (e *ExclusiveLock) UnmarshalJSON(data []byte) error {
	type Alias ExclusiveLock
	aux := (*Alias)(e)
	return json.Unmarshal(data, aux)
}

// Validate checks if the lock has valid field values
func (e *ExclusiveLock) Validate() error {
	if e.Holder == "" {
		return fmt.Errorf("holder is required")
	}
	if e.PID <= 0 {
		return fmt.Errorf("pid must be positive (got %d)", e.PID)
	}
	if e.Hostname == "" {
		return fmt.Errorf("hostname is required")
	}
	if e.StartedAt.IsZero() {
		return fmt.Errorf("started_at is required")
	}
	return nil
}
