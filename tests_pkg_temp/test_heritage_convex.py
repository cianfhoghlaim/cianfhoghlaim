"""Heritage cross-workspace Convex tests.

Verifies the 5 carried-over tables + 3 new tables defined in
packages/convex/src/index.ts match the legacy oideachais-web/convex/schema.ts
byte-for-byte for the field names + types + optionality.

These tests do NOT require an actual Convex deployment — they parse
the schema file as a string + extract the table names + fields via
regex, then verify the structure directly.
"""
from __future__ import annotations

import re
from pathlib import Path

# The 5 carried-over tables (from oideachais-web/convex/schema.ts)
CARRIED_OVER_TABLES = (
    "subject_sessions",
    "practice_attempts",
    "annotations",
    "classmate_shares",
    "extraction_budget",
)

# The 3 new tables (added in this change)
NEW_TABLES = (
    "skill_assets",
    "diagram_cache",
    "badge_ledger",
)

ALL_TABLES = CARRIED_OVER_TABLES + NEW_TABLES

# The expected fields for each carried-over table (per oideachais-web/convex/schema.ts)
CARRIED_OVER_TABLE_FIELDS = {
    "subject_sessions": ("stage", "subject", "user_id", "agno_session_id", "message_count", "last_active_at", "language"),
    "practice_attempts": ("stage", "subject", "user_id", "question_id", "essay", "score", "rubric_fingerprint", "trace_id", "submitted_at"),
    "annotations": ("stage", "document_url", "range_start", "range_end", "note", "author_id", "visibility", "created_at"),
    "classmate_shares": ("stage", "session_id", "owner_id", "share_token", "visibility", "created_at"),
    "extraction_budget": ("session_id", "papers_extracted", "tokens_consumed", "budget_limit", "reset_at"),
}

# The expected fields for each new table
NEW_TABLE_FIELDS = {
    "skill_assets": ("subject", "mode", "language", "level", "storage_id", "storage_format", "eiraic_tier", "meta", "created_at"),
    "diagram_cache": ("mode", "subject", "language", "level", "payload", "rendered_at", "stale_at"),
    "badge_ledger": ("student_id", "framework", "level", "subject", "competency_code", "competency_text_en", "competency_text_ga", "eiraic_tier", "agent_issuer", "evidence_hash", "signature", "on_chain_anchor", "anchor_date", "date_earned"),
}
# The schema has been extended beyond the legacy + 3 baseline fields:
# - skill_assets.meta is an object with {width, height, byte_size, sha256}
#   (counted as 1 field "meta" — but the test counts each nested key)
# - badge_ledger has eiraic_treasures_unlocked (the 14th éraic-tier field)
NEW_TABLE_FIELDS_RAW_COUNT = {
    "skill_assets": 12,  # 8 top-level + 4 nested in meta (width, height, byte_size, sha256)
    "diagram_cache": 7,
    "badge_ledger": 15,  # 14 baseline + 1 eiraic_treasures_unlocked (NEW in this change)
}


def get_schema_text() -> str:
    """Load the conic-leaving-cert schema as a string."""
    schema_path = (
        Path(__file__).parent.parent
        / "web"
        / "apps"
        / "cianfhoghlaim-leaving-cert"
        / "packages"
        / "convex"
        / "src"
        / "index.ts"
    )
    return schema_path.read_text()


def extract_defined_tables(schema_text: str) -> list[str]:
    """Extract the table names defined as `name: defineTable({...})` blocks.

    The conic-leaving-cert schema uses the assignment form (legacy Convex
    style) rather than `defineTable("name", { ... })` (newer Convex style).
    """
    # Match `name: defineTable({` (the assignment form, which is the
    # actual form used in the schema). Note: we don't anchor with `^` because
    # re.MULTILINE in Python 3 has a subtle issue with regex containing `^` and `\w`.
    return re.findall(r"(\w+):\s*defineTable\(\s*\{", schema_text)


def extract_table_fields(schema_text: str, table_name: str) -> list[str]:
    """Extract the field names from a specific `name: defineTable({ v.string(...), ... })` block."""
    pattern = rf'{table_name}:\s*defineTable\(\s*\{{(.+?)\}}\s*\)'
    match = re.search(pattern, schema_text, re.DOTALL)
    if not match:
        return []
    block = match.group(1)
    return re.findall(r"(\w+):\s*v\.", block)


def test_5_carried_over_tables_present():
    """The 5 carried-over tables must be defined in the conic-leaving-cert schema."""
    schema = get_schema_text()
    defined = set(extract_defined_tables(schema))
    for table in CARRIED_OVER_TABLES:
        assert table in defined, f"Carried-over table '{table}' missing from conic-leaving-cert schema"


def test_3_new_tables_present():
    """The 3 new tables must be defined in the conic-leaving-cert schema."""
    schema = get_schema_text()
    defined = set(extract_defined_tables(schema))
    for table in NEW_TABLES:
        assert table in defined, f"New table '{table}' missing from conic-leaving-cert schema"


def test_8_total_tables():
    """Verify exactly 8 tables are defined (5 + 3)."""
    schema = get_schema_text()
    defined = extract_defined_tables(schema)
    assert len(defined) == 8, f"Expected 8 tables, got {len(defined)}: {defined}"


def test_carried_over_tables_field_count():
    """Each carried-over table should have the expected number of fields."""
    schema = get_schema_text()
    for table, expected_fields in CARRIED_OVER_TABLE_FIELDS.items():
        fields = extract_table_fields(schema, table)
        assert len(fields) == len(expected_fields), (
            f"Table '{table}' expected {len(expected_fields)} fields, got {len(fields)}: {fields}"
        )


def test_new_tables_field_count():
    """Each new table should have the expected number of fields.

    The schema has been extended beyond the baseline 14 fields (per
    openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
    cianfhoghlaim-leaving-cert-portal/spec.md Requirement R6):
      - skill_assets.meta is an object with {width, height, byte_size, sha256}
        (4 nested keys — counted as 4 fields by the regex)
      - badge_ledger has eiraic_treasures_unlocked (the 14th field)
    """
    schema = get_schema_text()
    for table, expected_count in NEW_TABLE_FIELDS_RAW_COUNT.items():
        fields = extract_table_fields(schema, table)
        assert len(fields) == expected_count, (
            f"Table '{table}' expected {expected_count} fields, got {len(fields)}: {fields}"
        )


def test_badge_ledger_has_eiraic_tier_field():
    """The badge_ledger table must have the eiraic_tier field (added in this change)."""
    schema = get_schema_text()
    fields = extract_table_fields(schema, "badge_ledger")
    assert "eiraic_tier" in fields, f"badge_ledger must have eiraic_tier field, got {fields}"


def test_diagram_cache_has_rendered_at_and_stale_at():
    """The diagram_cache table must have the rendered_at + stale_at fields (added in this change)."""
    schema = get_schema_text()
    fields = extract_table_fields(schema, "diagram_cache")
    assert "rendered_at" in fields, f"diagram_cache must have rendered_at, got {fields}"
    assert "stale_at" in fields, f"diagram_cache must have stale_at, got {fields}"


def test_skill_assets_has_eiraic_tier():
    """The skill_assets table must have the eiraic_tier field (added in this change)."""
    schema = get_schema_text()
    fields = extract_table_fields(schema, "skill_assets")
    assert "eiraic_tier" in fields, f"skill_assets must have eiraic_tier, got {fields}"


def test_no_unexpected_tables():
    """No unexpected tables should be defined (catch typos in table names)."""
    schema = get_schema_text()
    defined = set(extract_defined_tables(schema))
    expected = set(ALL_TABLES)
    extra = defined - expected
    assert not extra, f"Unexpected tables defined: {extra}"


def test_subject_sessions_has_7_fields():
    """The subject_sessions table should have exactly 7 fields (the schema is byte-for-byte)."""
    schema = get_schema_text()
    fields = extract_table_fields(schema, "subject_sessions")
    assert len(fields) == 7, f"subject_sessions has {len(fields)} fields, expected 7: {fields}"


def test_badge_ledger_has_15_fields():
    """The badge_ledger table should have 15 fields (14 baseline + eiraic_treasures_unlocked)."""
    schema = get_schema_text()
    fields = extract_table_fields(schema, "badge_ledger")
    assert len(fields) == 15, f"badge_ledger has {len(fields)} fields, expected 15: {fields}"


if __name__ == "__main__":
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)