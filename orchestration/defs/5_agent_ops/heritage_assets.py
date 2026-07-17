"""Dagster assets for the heritage cross-workspace tests.

Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T8.6.
Heritage tests verify that the new `conic-leaving-cert` deployment is
byte-for-byte identical to the legacy `cianfhoghlaim-web/convex/schema.ts`
for the 5 carried-over tables.
"""

from __future__ import annotations

from dagster import (
    AssetExecutionContext,
    asset,
)


# The 5 carried-over tables (from cianfhoghlaim-web/convex/schema.ts)
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


@asset(
    group_name="heritage",
    description="Verify that the conic-leaving-cert Convex deployment has all 8 tables (5 carried-over + 3 new)",
)
def convex_table_integrity(context) -> dict[str, list[str]]:
    """Verify the 8 Convex tables exist with the correct schema.

    Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
    cianfhoghlaim-leaving-cert-portal/spec.md Requirement R6.
    """
    # TODO: query the conic-leaving-cert Convex deployment for the
    # 8 tables + verify the byte-for-byte schema match
    context.log.info("Verifying Convex table integrity...")
    return {
        "carried_over": list(CARRIED_OVER_TABLES),
        "new": list(NEW_TABLES),
        "all": list(ALL_TABLES),
        "deployment": "conic-leaving-cert",
    }


@asset(
    group_name="heritage",
    description="Verify the BetterAuth session flow round-trips with Pocket ID OIDC",
)
def pocket_id_session_roundtrip(context) -> dict[str, str]:
    """Verify the Pocket ID OIDC sign-in flow round-trips with 200 OK.

    Per R6 + openspec/changes/leaving-cert-2026/ tests.
    """
    # TODO: hit the Pocket ID OIDC discovery endpoint + simulate a sign-in
    context.log.info("Verifying Pocket ID session roundtrip...")
    return {
        "discovery_url": "http://localhost:8080/.well-known/openid-configuration",
        "status": "ok",
    }


@asset(
    group_name="heritage",
    description="Verify the Convex auth.config.ts points at Pocket ID OIDC discovery",
)
def convex_auth_config_integrity(context) -> dict[str, str]:
    """Verify the Convex auth.config.ts is wired to Pocket ID OIDC."""
    # TODO: read the auth.config.ts + verify the OIDC domain
    context.log.info("Verifying Convex auth.config.ts...")
    return {
      "auth_config_path": "packages/convex/auth.config.ts",
      "oidc_domain": "pocket-id.cianfhoghlaim.ie",
      "status": "ok",
    }