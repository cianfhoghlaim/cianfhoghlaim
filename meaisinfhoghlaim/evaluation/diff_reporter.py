"""Regression report generator (Plan 3 UC 5).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 3, UC 5).

Generates the canonical regression report (HTML + Markdown) for a
RegressionDiff. Consumed by Plan 5\'s ``meaisin_regression_summary``
Dagster asset + the operator-facing ops dashboard.

Generalisable: same report works for any (jurisdiction, stage, subject,
board) combination.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from meaisinfhoghlaim.evaluation.regression_baseline import RegressionDiff

logger = logging.getLogger(__name__)


class DiffReporter:
    """The canonical regression diff reporter."""

    def to_markdown(self, diff: RegressionDiff) -> str:
        """Render the RegressionDiff as Markdown."""
        lines = [
            f"# Regression diff for cohort `{diff.cohort_key}`",
            "",
            f"- **diff_id**: `{diff.diff_id}`",
            f"- **baseline_old_id**: `{diff.baseline_old_id}`",
            f"- **baseline_new_id**: `{diff.baseline_new_id}`",
            f"- **content_hash_changed**: **{diff.content_hash_changed}**",
            f"- **added_topics** ({len(diff.added_topics)}): "
            + (", ".join(f"`{t}`" for t in diff.added_topics) or "(none)"),
            f"- **removed_topics** ({len(diff.removed_topics)}): "
            + (", ".join(f"`{t}`" for t in diff.removed_topics) or "(none)"),
            f"- **duration_ms**: {diff.duration_ms}",
            "",
            "## Modified concepts",
            "",
        ]
        try:
            modified = json.loads(diff.modified_concepts_json)
            for topic_id, info in modified.items():
                lines.append(f"- `{topic_id}`: {info}")
        except Exception:
            lines.append(f"```\n{diff.modified_concepts_json}\n```")
        return "\n".join(lines)

    def to_html(self, diff: RegressionDiff) -> str:
        """Render the RegressionDiff as HTML."""
        return f"""<!DOCTYPE html>
<html>
<head><title>Regression diff for {diff.cohort_key}</title></head>
<body>
<h1>Regression diff for cohort {diff.cohort_key}</h1>
<p><strong>diff_id:</strong> <code>{diff.diff_id}</code></p>
<p><strong>content_hash_changed:</strong> <strong>{diff.content_hash_changed}</strong></p>
<h2>Added topics ({len(diff.added_topics)})</h2>
<ul>{''.join(f'<li><code>{t}</code></li>' for t in diff.added_topics)}</ul>
<h2>Removed topics ({len(diff.removed_topics)})</h2>
<ul>{''.join(f'<li><code>{t}</code></li>' for t in diff.removed_topics)}</ul>
<h2>Modified concepts</h2>
<pre><code>{diff.modified_concepts_json}</code></pre>
<p><strong>duration_ms:</strong> {diff.duration_ms}</p>
</body>
</html>
"""

    def to_dict(self, diff: RegressionDiff) -> dict:
        """Render the RegressionDiff as a dict (for MLflow tags + dlt sources)."""
        return {
            "diff_id": diff.diff_id,
            "cohort_key": diff.cohort_key,
            "baseline_old_id": diff.baseline_old_id,
            "baseline_new_id": diff.baseline_new_id,
            "content_hash_changed": diff.content_hash_changed,
            "added_topics": list(diff.added_topics),
            "removed_topics": list(diff.removed_topics),
            "modified_concepts_json": diff.modified_concepts_json,
            "duration_ms": diff.duration_ms,
        }


__all__ = ["DiffReporter", "RegressionDiff"]
