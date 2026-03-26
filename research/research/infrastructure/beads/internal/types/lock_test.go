package types

import (
	"encoding/json"
	"testing"
	"time"
)

func TestExclusiveLock_MarshalJSON(t *testing.T) {
	lock := &ExclusiveLock{
		Holder:    "test-tool",
		PID:       12345,
		Hostname:  "test-host",
		StartedAt: time.Date(2025, 10, 25, 12, 0, 0, 0, time.UTC),
		Version:   "1.0.0",
	}

	data, err := json.Marshal(lock)
	if err != nil {
		t.Fatalf("failed to marshal lock: %v", err)
	}

	expected := `{"holder":"test-tool","pid":12345,"hostname":"test-host","started_at":"2025-10-25T12:00:00Z","version":"1.0.0"}`
	if string(data) != expected {
		t.Errorf("unexpected JSON:\ngot:  %s\nwant: %s", string(data), expected)
	}
}

func TestExclusiveLock_UnmarshalJSON(t *testing.T) {
	data := []byte(`{"holder":"test-tool","pid":12345,"hostname":"test-host","started_at":"2025-10-25T12:00:00Z","version":"1.0.0"}`)

	var lock ExclusiveLock
	err := json.Unmarshal(data, &lock)
	if err != nil {
		t.Fatalf("failed to unmarshal lock: %v", err)
	}

	if lock.Holder != "test-tool" {
		t.Errorf("unexpected holder: got %s, want test-tool", lock.Holder)
	}
	if lock.PID != 12345 {
		t.Errorf("unexpected PID: got %d, want 12345", lock.PID)
	}
	if lock.Hostname != "test-host" {
		t.Errorf("unexpected hostname: got %s, want test-host", lock.Hostname)
	}
	if lock.Version != "1.0.0" {
		t.Errorf("unexpected version: got %s, want 1.0.0", lock.Version)
	}

	expected := time.Date(2025, 10, 25, 12, 0, 0, 0, time.UTC)
	if !lock.StartedAt.Equal(expected) {
		t.Errorf("unexpected started_at: got %v, want %v", lock.StartedAt, expected)
	}
}

func TestExclusiveLock_Validate(t *testing.T) {
	tests := []struct {
		name    string
		lock    *ExclusiveLock
		wantErr bool
	}{
		{
			name: "valid lock",
			lock: &ExclusiveLock{
				Holder:    "test-tool",
				PID:       12345,
				Hostname:  "test-host",
				StartedAt: time.Now(),
				Version:   "1.0.0",
			},
			wantErr: false,
		},
		{
			name: "missing holder",
			lock: &ExclusiveLock{
				PID:       12345,
				Hostname:  "test-host",
				StartedAt: time.Now(),
				Version:   "1.0.0",
			},
			wantErr: true,
		},
		{
			name: "invalid PID (zero)",
			lock: &ExclusiveLock{
				Holder:    "test-tool",
				PID:       0,
				Hostname:  "test-host",
				StartedAt: time.Now(),
				Version:   "1.0.0",
			},
			wantErr: true,
		},
		{
			name: "invalid PID (negative)",
			lock: &ExclusiveLock{
				Holder:    "test-tool",
				PID:       -1,
				Hostname:  "test-host",
				StartedAt: time.Now(),
				Version:   "1.0.0",
			},
			wantErr: true,
		},
		{
			name: "missing hostname",
			lock: &ExclusiveLock{
				Holder:    "test-tool",
				PID:       12345,
				StartedAt: time.Now(),
				Version:   "1.0.0",
			},
			wantErr: true,
		},
		{
			name: "missing started_at",
			lock: &ExclusiveLock{
				Holder:   "test-tool",
				PID:      12345,
				Hostname: "test-host",
				Version:  "1.0.0",
			},
			wantErr: true,
		},
		{
			name: "missing version (allowed)",
			lock: &ExclusiveLock{
				Holder:    "test-tool",
				PID:       12345,
				Hostname:  "test-host",
				StartedAt: time.Now(),
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.lock.Validate()
			if (err != nil) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestNewExclusiveLock(t *testing.T) {
	lock, err := NewExclusiveLock("test-tool", "1.0.0")
	if err != nil {
		t.Fatalf("NewExclusiveLock failed: %v", err)
	}

	if lock.Holder != "test-tool" {
		t.Errorf("unexpected holder: got %s, want test-tool", lock.Holder)
	}
	if lock.Version != "1.0.0" {
		t.Errorf("unexpected version: got %s, want 1.0.0", lock.Version)
	}
	if lock.PID <= 0 {
		t.Errorf("PID should be positive, got %d", lock.PID)
	}
	if lock.Hostname == "" {
		t.Error("hostname should not be empty")
	}
	if lock.StartedAt.IsZero() {
		t.Error("started_at should not be zero")
	}

	// Validate should pass
	if err := lock.Validate(); err != nil {
		t.Errorf("newly created lock should be valid: %v", err)
	}
}
