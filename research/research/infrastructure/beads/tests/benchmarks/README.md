# Beads Benchmarks

Automated benchmarks for measuring Beads performance and Agent Mail coordination efficiency.

## Git Traffic Reduction Benchmark

**File:** `git_traffic.py`

### Purpose

Measures the reduction in git operations (pulls, commits, pushes) when using Agent Mail for multi-agent coordination compared to pure git-based synchronization.

### Usage

```bash
# Run with default settings (50 issues)
python3 tests/benchmarks/git_traffic.py

# Customize number of issues
python3 tests/benchmarks/git_traffic.py -n 100

# Verbose output
python3 tests/benchmarks/git_traffic.py -v

# Save report to file
python3 tests/benchmarks/git_traffic.py -o report.md
```

### How It Works

The benchmark compares two workflows:

**Without Agent Mail (Git-only mode):**
- Each issue update requires git pull + commit + push
- Other agents pull to check for updates
- Total: ~4 git operations per issue

**With Agent Mail:**
- Coordination via HTTP messages (no git operations)
- Status updates, reservations, notifications via Agent Mail
- Single batched commit/push at end of workflow
- Total: 3 git operations for entire batch

### Expected Results

For 50 issues:
- **Without Agent Mail:** ~200 git operations
- **With Agent Mail:** 3 git operations
- **Reduction:** ≥70% (typically 95-98%)

### Exit Codes

- `0`: Success - achieved ≥70% reduction
- `1`: Failure - regression detected

### Example Output

```
======================================================================
SUMMARY
======================================================================
Without Agent Mail: 200 git operations
With Agent Mail:    3 git operations
Reduction:          98.5%
Target:             70%
Status:             ✅ PASS
======================================================================
```

## Requirements

- Python 3.7+
- bd (beads) CLI installed
- git
- Agent Mail server (optional - falls back to simulation if unavailable)

## CI Integration

This benchmark can be used in CI to detect regressions in Agent Mail coordination efficiency:

```bash
python3 tests/benchmarks/git_traffic.py -n 50
# Exits with status 1 if reduction < 70%
```
