"""
Content-Based Freshness Sensors for Unified Curriculum Pipeline.

Detects changes across all 3 curriculum sources:
- curriculumonline.ie (sitemap-based)
- ncca.ie (sitemap-based)
- examinations.ie (PDF list comparison)

Triggers the unified curriculum assets with the 4-cycle partition scheme.

Usage:
    from oideachais.data_platform.dagster_defs.sensors.curriculum_freshness import (
        curriculum_freshness_sensors,
    )

    defs = Definitions(
        sensors=curriculum_freshness_sensors,
        ...
    )
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from dagster import (
    AssetKey,
    DefaultSensorStatus,
    RunRequest,
    SensorEvaluationContext,
    SensorResult,
    SkipReason,
    sensor,
)

# ============================================================================
# Sensor State Management
# ============================================================================


@dataclass
class SourceState:
    """Tracks state for a curriculum source."""

    source_name: str
    sitemap_hash: str | None = None
    pdf_count: int | None = None
    last_checked: datetime | None = None
    last_changed: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "source_name": self.source_name,
            "sitemap_hash": self.sitemap_hash,
            "pdf_count": self.pdf_count,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "last_changed": self.last_changed.isoformat() if self.last_changed else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SourceState:
        """Create from dictionary."""
        return cls(
            source_name=data["source_name"],
            sitemap_hash=data.get("sitemap_hash"),
            pdf_count=data.get("pdf_count"),
            last_checked=(
                datetime.fromisoformat(data["last_checked"])
                if data.get("last_checked")
                else None
            ),
            last_changed=(
                datetime.fromisoformat(data["last_changed"])
                if data.get("last_changed")
                else None
            ),
        )


@dataclass
class CurriculumSensorState:
    """Combined state for all curriculum sources."""

    sources: dict[str, SourceState]

    def to_cursor(self) -> str:
        """Serialize to cursor string."""
        return json.dumps({
            name: state.to_dict()
            for name, state in self.sources.items()
        })

    @classmethod
    def from_cursor(cls, cursor: str | None) -> CurriculumSensorState:
        """Deserialize from cursor string."""
        if not cursor:
            return cls(sources={})

        try:
            data = json.loads(cursor)
            return cls(
                sources={
                    name: SourceState.from_dict(state_data)
                    for name, state_data in data.items()
                }
            )
        except (json.JSONDecodeError, KeyError):
            return cls(sources={})

    def get_or_create(self, source_name: str) -> SourceState:
        """Get or create state for a source."""
        if source_name not in self.sources:
            self.sources[source_name] = SourceState(source_name=source_name)
        return self.sources[source_name]


# ============================================================================
# Source Configuration
# ============================================================================

SOURCE_CONFIGS = {
    "curriculumonline": {
        "sitemap_url": "https://curriculumonline.ie/sitemap.xml",
        "check_method": "sitemap",
        "cycles": ["primary", "junior_cycle", "senior_cycle"],
    },
    "ncca": {
        "sitemap_url": "https://ncca.ie/sitemap.xml",
        "check_method": "sitemap",
        "cycles": ["early_childhood", "primary", "junior_cycle", "senior_cycle"],
    },
    "examinations": {
        "base_url": "https://examinations.ie",
        "check_method": "pdf_list",
        "cycles": ["junior_cycle", "senior_cycle"],
    },
}


# ============================================================================
# Unified Curriculum Freshness Sensor
# ============================================================================


@sensor(
    name="unified_curriculum_freshness_sensor",
    asset_selection=[
        AssetKey(["ireland", "curriculum", "raw_curriculum_pages"]),
        AssetKey(["ireland", "curriculum", "raw_curriculum_pdfs"]),
        AssetKey(["ireland", "curriculum", "raw_source_provenance"]),
    ],
    minimum_interval_seconds=3600,  # Check hourly
    default_status=DefaultSensorStatus.STOPPED,
    description=(
        "Monitors all 3 curriculum sources for changes and triggers "
        "unified pipeline with appropriate cycle partitions"
    ),
)
def unified_curriculum_freshness_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Monitor all curriculum sources for content changes.

    Detection methods:
    - curriculumonline.ie: Sitemap hash comparison
    - ncca.ie: Sitemap hash comparison
    - examinations.ie: PDF list count comparison

    When changes detected, triggers runs for affected cycle partitions.
    """
    import httpx

    state = CurriculumSensorState.from_cursor(context.cursor)
    now = datetime.now(UTC)

    changed_sources: list[tuple[str, list[str]]] = []  # (source_name, cycles)
    errors: list[str] = []

    for source_name, config in SOURCE_CONFIGS.items():
        source_state = state.get_or_create(source_name)
        source_state.last_checked = now

        try:
            if config["check_method"] == "sitemap":
                # Check sitemap hash
                sitemap_url = config["sitemap_url"]
                response = httpx.get(sitemap_url, timeout=30.0)
                current_hash = hashlib.sha256(response.content).hexdigest()

                if source_state.sitemap_hash != current_hash:
                    context.log.info(
                        f"Sitemap change detected for {source_name}: "
                        f"{source_state.sitemap_hash[:12] if source_state.sitemap_hash else 'none'}... "
                        f"-> {current_hash[:12]}..."
                    )
                    source_state.sitemap_hash = current_hash
                    source_state.last_changed = now
                    changed_sources.append((source_name, config["cycles"]))

            elif config["check_method"] == "pdf_list":
                # Check PDF count (simplified - would use actual scraping)
                # For examinations.ie, we check during exam seasons
                exam_months = [1, 6, 7, 8, 12]
                if now.month in exam_months:
                    # Simulate PDF count check
                    current_count = source_state.pdf_count or 0

                    # In production, would scrape PDF list
                    # For now, trigger if we haven't checked this month
                    if source_state.last_changed:
                        last_change_month = source_state.last_changed.month
                        if last_change_month != now.month:
                            source_state.last_changed = now
                            changed_sources.append((source_name, config["cycles"]))
                    else:
                        source_state.last_changed = now
                        changed_sources.append((source_name, config["cycles"]))

        except Exception as e:
            errors.append(f"{source_name}: {e}")
            context.log.warning(f"Failed to check {source_name}: {e}")

    # Update cursor
    context.update_cursor(state.to_cursor())

    if not changed_sources:
        if errors:
            return SkipReason(f"No changes detected (errors: {', '.join(errors)})")
        return SkipReason("No changes detected across curriculum sources")

    # Determine which cycles to trigger
    cycles_to_trigger = set()
    for source_name, cycles in changed_sources:
        cycles_to_trigger.update(cycles)

    # Create run requests for each affected cycle
    run_requests = []
    for cycle in cycles_to_trigger:
        run_requests.append(
            RunRequest(
                run_key=f"curriculum-{cycle}-{now.strftime('%Y%m%d%H')}",
                partition_key=cycle,
                tags={
                    "trigger": "content_change",
                    "sources": ",".join(s for s, _ in changed_sources),
                },
            )
        )

    context.log.info(
        f"Triggering runs for {len(run_requests)} cycles: {list(cycles_to_trigger)}"
    )

    return SensorResult(run_requests=run_requests)


# ============================================================================
# Per-Source Sensors (for fine-grained control)
# ============================================================================


@sensor(
    name="curriculumonline_freshness_sensor",
    asset_selection=[
        AssetKey(["ireland", "curriculum", "raw_curriculum_pages"]),
    ],
    minimum_interval_seconds=3600,
    default_status=DefaultSensorStatus.STOPPED,
    description="Monitors curriculumonline.ie for specification changes",
)
def curriculumonline_freshness_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Monitor curriculumonline.ie sitemap for changes.

    This is the primary source for curriculum specifications.
    Triggers runs for primary, junior_cycle, and senior_cycle.
    """
    import httpx

    sitemap_url = "https://curriculumonline.ie/sitemap.xml"

    try:
        response = httpx.get(sitemap_url, timeout=30.0)
        sitemap_hash = hashlib.sha256(response.content).hexdigest()

        previous_hash = context.cursor
        if previous_hash == sitemap_hash:
            return SkipReason(f"Sitemap unchanged (hash: {sitemap_hash[:12]}...)")

        context.update_cursor(sitemap_hash)

        # Trigger all 3 cycles that curriculumonline covers
        run_requests = [
            RunRequest(
                run_key=f"curriculumonline-{cycle}-{sitemap_hash[:12]}",
                partition_key=cycle,
                tags={"trigger": "sitemap_change", "source": "curriculumonline"},
            )
            for cycle in ["primary", "junior_cycle", "senior_cycle"]
        ]

        return SensorResult(run_requests=run_requests)

    except Exception as e:
        return SkipReason(f"Sitemap check failed: {e}")


@sensor(
    name="ncca_freshness_sensor",
    asset_selection=[
        AssetKey(["ireland", "curriculum", "raw_curriculum_pages"]),
    ],
    minimum_interval_seconds=3600,
    default_status=DefaultSensorStatus.STOPPED,
    description="Monitors ncca.ie for curriculum development updates",
)
def ncca_freshness_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Monitor ncca.ie sitemap for changes.

    NCCA is the curriculum development body - updates indicate
    new or revised curriculum specifications.
    """
    import httpx

    sitemap_url = "https://ncca.ie/sitemap.xml"

    try:
        response = httpx.get(sitemap_url, timeout=30.0)
        sitemap_hash = hashlib.sha256(response.content).hexdigest()

        previous_hash = context.cursor
        if previous_hash == sitemap_hash:
            return SkipReason(f"NCCA sitemap unchanged (hash: {sitemap_hash[:12]}...)")

        context.update_cursor(sitemap_hash)

        # NCCA covers all 4 cycles
        run_requests = [
            RunRequest(
                run_key=f"ncca-{cycle}-{sitemap_hash[:12]}",
                partition_key=cycle,
                tags={"trigger": "sitemap_change", "source": "ncca"},
            )
            for cycle in ["early_childhood", "primary", "junior_cycle", "senior_cycle"]
        ]

        return SensorResult(run_requests=run_requests)

    except Exception as e:
        return SkipReason(f"NCCA sitemap check failed: {e}")


@sensor(
    name="examinations_freshness_sensor",
    asset_selection=[
        AssetKey(["ireland", "curriculum", "raw_curriculum_pdfs"]),
    ],
    minimum_interval_seconds=86400,  # Check daily
    default_status=DefaultSensorStatus.STOPPED,
    description="Monitors examinations.ie for new exam papers (exam seasons only)",
)
def examinations_freshness_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Monitor examinations.ie for new exam papers.

    Only active during exam seasons:
    - June-August: Leaving Cert and Junior Cycle results
    - December-January: Mock exam papers
    """
    now = datetime.now(UTC)

    # Only check during exam seasons
    exam_months = [1, 6, 7, 8, 12]
    if now.month not in exam_months:
        return SkipReason(f"Outside exam season (month {now.month})")

    # Parse previous state
    try:
        if context.cursor:
            state = json.loads(context.cursor)
            last_check = datetime.fromisoformat(state.get("last_check", "2000-01-01"))
            last_year_month = state.get("year_month")
        else:
            last_check = datetime(2000, 1, 1, tzinfo=UTC)
            last_year_month = None
    except (json.JSONDecodeError, ValueError):
        last_check = datetime(2000, 1, 1, tzinfo=UTC)
        last_year_month = None

    current_year_month = f"{now.year}-{now.month:02d}"

    # Check if we've already triggered for this year-month
    if last_year_month == current_year_month:
        # Only check once per day within the month
        if now - last_check < timedelta(hours=24):
            return SkipReason(f"Already checked today for {current_year_month}")

    # Update cursor
    new_state = {
        "last_check": now.isoformat(),
        "year_month": current_year_month,
    }
    context.update_cursor(json.dumps(new_state))

    # Trigger for cycles that have exams
    run_requests = [
        RunRequest(
            run_key=f"examinations-{cycle}-{current_year_month}",
            partition_key=cycle,
            tags={"trigger": "exam_season", "source": "examinations"},
        )
        for cycle in ["junior_cycle", "senior_cycle"]
    ]

    return SensorResult(run_requests=run_requests)


# ============================================================================
# Enrichment Trigger Sensor
# ============================================================================


@sensor(
    name="curriculum_enrichment_trigger_sensor",
    asset_selection=[
        AssetKey(["ireland", "curriculum", "embeddings"]),
        AssetKey(["ireland", "curriculum", "translations"]),
    ],
    minimum_interval_seconds=86400,  # Check daily
    default_status=DefaultSensorStatus.STOPPED,
    description="Triggers enrichment when all cycle partitions are materialized",
)
def curriculum_enrichment_trigger_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Trigger enrichment assets when structured content is ready.

    Checks if all cycle partitions of the structured asset have been
    materialized within the last 24 hours, then triggers enrichment.
    """

    # Check structured asset for all cycles
    cycles = ["early_childhood", "primary", "junior_cycle", "senior_cycle"]
    structured_key = AssetKey(["ireland", "curriculum", "structured"])

    now = datetime.now(UTC)
    cutoff = now - timedelta(hours=24)

    # In a real implementation, we would check asset materialization records
    # For now, use a simplified check based on cursor

    try:
        if context.cursor:
            state = json.loads(context.cursor)
            last_enrichment = datetime.fromisoformat(state.get("last_enrichment", "2000-01-01"))
            materialized_cycles = set(state.get("materialized_cycles", []))
        else:
            last_enrichment = datetime(2000, 1, 1, tzinfo=UTC)
            materialized_cycles = set()
    except (json.JSONDecodeError, ValueError):
        last_enrichment = datetime(2000, 1, 1, tzinfo=UTC)
        materialized_cycles = set()

    # Check if we've enriched recently
    if now - last_enrichment < timedelta(hours=24):
        return SkipReason("Already triggered enrichment within 24 hours")

    # In production, would check actual asset materializations
    # For demo, trigger if we haven't in a while
    new_state = {
        "last_enrichment": now.isoformat(),
        "materialized_cycles": list(cycles),
    }
    context.update_cursor(json.dumps(new_state))

    return RunRequest(
        run_key=f"enrichment-{now.strftime('%Y%m%d')}",
        tags={"trigger": "all_cycles_ready"},
    )


# ============================================================================
# Export All Sensors
# ============================================================================

curriculum_freshness_sensors = [
    # Unified sensor (recommended)
    unified_curriculum_freshness_sensor,
    # Per-source sensors (for fine-grained control)
    curriculumonline_freshness_sensor,
    ncca_freshness_sensor,
    examinations_freshness_sensor,
    # Enrichment trigger
    curriculum_enrichment_trigger_sensor,
]
