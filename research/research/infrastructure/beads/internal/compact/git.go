package compact

import (
	"bytes"
	"os/exec"
	"strings"
)

// GetCurrentCommitHash returns the current git HEAD commit hash.
// Returns empty string if not in a git repository or if git command fails.
func GetCurrentCommitHash() string {
	cmd := exec.Command("git", "rev-parse", "HEAD")
	var out bytes.Buffer
	cmd.Stdout = &out
	
	if err := cmd.Run(); err != nil {
		return ""
	}
	
	return strings.TrimSpace(out.String())
}
