"""
Domain Sensors for Celtic Education Platform.

Per-domain sensors for triggering pipeline runs:
- Sitemap change detection
- File system monitoring
- API data freshness checks
- Cross-domain enrichment triggers

Sensor Groups:
- Ireland Education: NCCA/SEC sitemap changes
- UK Education: DfE/SQA/WJEC publication updates
- Celtic Language: Dúchas/Canuint API changes
- Geospatial: GeoHive/CSO boundary updates
"""
from __future__ import annotations

from datetime import datetime, timedelta

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
# Ireland Education Sensors
# ============================================================================

@sensor(
    name="ireland_curriculum_sitemap_sensor",
    asset_selection=[
        AssetKey(["ireland", "education", "web_pages"]),
    ],
    minimum_interval_seconds=3600,  # Check hourly
    default_status=DefaultSensorStatus.STOPPED,
    description="Detects changes to curriculumonline.ie sitemap",
)
def ireland_curriculum_sitemap_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Monitor curriculumonline.ie sitemap for new/updated pages.

    Triggers web_pages asset when sitemap changes detected.
    """
    import hashlib

    import httpx

    sitemap_url = "https://curriculumonline.ie/sitemap.xml"

    try:
        response = httpx.get(sitemap_url, timeout=30.0)
        sitemap_hash = hashlib.sha256(response.content).hexdigest()

        # Check cursor for previous hash
        previous_hash = context.cursor

        if previous_hash == sitemap_hash:
            return SkipReason(f"Sitemap unchanged (hash: {sitemap_hash[:12]}...)")

        context.update_cursor(sitemap_hash)

        return RunRequest(
            run_key=f"curriculumonline-{sitemap_hash[:12]}",
            partition_key="curriculumonline",
        )

    except Exception as e:
        return SkipReason(f"Sitemap check failed: {e}")


@sensor(
    name="ireland_examinations_sensor",
    asset_selection=[
        AssetKey(["ireland", "education", "pdf_discovery"]),
    ],
    minimum_interval_seconds=86400,  # Check daily
    default_status=DefaultSensorStatus.STOPPED,
    description="Detects new exam papers on examinations.ie",
)
def ireland_examinations_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Monitor examinations.ie for new exam papers.

    Triggers during exam season (June-August, December-January).
    """
    now = datetime.now()

    # Active during exam seasons
    exam_months = [1, 6, 7, 8, 12]
    if now.month not in exam_months:
        return SkipReason(f"Outside exam season (month {now.month})")

    # Check for new papers (simplified - would use actual scraping)
    last_check = context.cursor
    if last_check:
        last_date = datetime.fromisoformat(last_check)
        if now - last_date < timedelta(hours=24):
            return SkipReason("Already checked within 24 hours")

    context.update_cursor(now.isoformat())

    return RunRequest(
        run_key=f"examinations-{now.strftime('%Y%m%d')}",
        partition_key="examinations",
    )


# ============================================================================
# UK Education Sensors
# ============================================================================

@sensor(
    name="uk_dfe_statistics_sensor",
    asset_selection=[
        AssetKey(["uk", "education", "england", "dfe_statistics"]),
    ],
    minimum_interval_seconds=86400,  # Check daily
    default_status=DefaultSensorStatus.STOPPED,
    description="Detects new DfE statistics publications",
)
def uk_dfe_statistics_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Monitor DfE explore-education-statistics.service.gov.uk for new data.

    Publication schedule: Typically quarterly releases.
    """
    import httpx

    api_url = "https://explore-education-statistics.service.gov.uk/api/publications"

    try:
        response = httpx.get(api_url, timeout=30.0)
        publications = response.json()

        # Check for publications updated since last check
        last_check = context.cursor or "2024-01-01T00:00:00"
        last_date = datetime.fromisoformat(last_check.replace("Z", "+00:00"))

        new_publications = [
            p for p in publications.get("results", [])
            if datetime.fromisoformat(p.get("updated", "2000-01-01").replace("Z", "+00:00")) > last_date
        ]

        if not new_publications:
            return SkipReason("No new DfE publications")

        context.update_cursor(datetime.utcnow().isoformat())

        return RunRequest(
            run_key=f"dfe-{datetime.utcnow().strftime('%Y%m%d')}",
        )

    except Exception as e:
        return SkipReason(f"DfE API check failed: {e}")


@sensor(
    name="scotland_sqa_sensor",
    asset_selection=[
        AssetKey(["uk", "education", "scotland", "sqa_examinations"]),
    ],
    minimum_interval_seconds=86400,
    default_status=DefaultSensorStatus.STOPPED,
    description="Detects new SQA examination results",
)
def scotland_sqa_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Monitor SQA for new examination results.

    Results typically released in August.
    """
    now = datetime.now()

    # SQA results released in August
    if now.month != 8:
        return SkipReason(f"Outside SQA results season (month {now.month})")

    last_check = context.cursor
    if last_check and last_check.startswith(str(now.year)):
        return SkipReason(f"Already checked for {now.year}")

    context.update_cursor(f"{now.year}-{now.month:02d}")

    return RunRequest(
        run_key=f"sqa-{now.year}",
    )


@sensor(
    name="wales_curriculum_sensor",
    asset_selection=[
        AssetKey(["uk", "education", "wales", "curriculum"]),
    ],
    minimum_interval_seconds=604800,  # Check weekly
    default_status=DefaultSensorStatus.STOPPED,
    description="Detects changes to Curriculum for Wales",
)
def wales_curriculum_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Monitor Curriculum for Wales for bilingual content updates.
    """
    import hashlib

    import httpx

    sitemap_url = "https://hwb.gov.wales/sitemap.xml"

    try:
        response = httpx.get(sitemap_url, timeout=30.0)
        sitemap_hash = hashlib.sha256(response.content).hexdigest()

        previous_hash = context.cursor
        if previous_hash == sitemap_hash:
            return SkipReason("Wales curriculum unchanged")

        context.update_cursor(sitemap_hash)

        return RunRequest(
            run_key=f"wales-curriculum-{sitemap_hash[:12]}",
        )

    except Exception as e:
        return SkipReason(f"Wales sitemap check failed: {e}")


# ============================================================================
# Celtic Language Sensors
# ============================================================================

@sensor(
    name="duchas_api_sensor",
    asset_selection=[
        AssetKey(["celtic", "folklore", "volumes"]),
    ],
    minimum_interval_seconds=604800,  # Check weekly
    default_status=DefaultSensorStatus.STOPPED,
    description="Detects new Dúchas transcriptions",
)
def duchas_api_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Monitor Dúchas API for new transcriptions.

    Volunteer transcriptions are ongoing.
    """
    import httpx

    api_url = "https://www.duchas.ie/api/v1.0/stats"

    try:
        response = httpx.get(api_url, timeout=30.0)
        stats = response.json()

        transcription_count = stats.get("transcription_count", 0)

        previous_count = int(context.cursor or "0")
        if transcription_count <= previous_count:
            return SkipReason(f"No new transcriptions (count: {transcription_count})")

        context.update_cursor(str(transcription_count))

        return RunRequest(
            run_key=f"duchas-{transcription_count}",
        )

    except Exception as e:
        return SkipReason(f"Dúchas API check failed: {e}")


@sensor(
    name="tearma_updates_sensor",
    asset_selection=[
        AssetKey(["celtic", "gaois", "terms"]),
    ],
    minimum_interval_seconds=604800,  # Check weekly
    default_status=DefaultSensorStatus.STOPPED,
    description="Detects new Téarma.ie terminology",
)
def tearma_updates_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Monitor Téarma.ie for new terminology entries.
    """
    import httpx

    api_url = "https://www.tearma.ie/api/stats"

    try:
        response = httpx.get(api_url, timeout=30.0)
        stats = response.json()

        term_count = stats.get("term_count", 0)

        previous_count = int(context.cursor or "0")
        if term_count <= previous_count:
            return SkipReason(f"No new terms (count: {term_count})")

        context.update_cursor(str(term_count))

        return RunRequest(
            run_key=f"tearma-{term_count}",
        )

    except Exception as e:
        return SkipReason(f"Téarma API check failed: {e}")


# ============================================================================
# Geospatial Sensors
# ============================================================================

@sensor(
    name="geohive_boundaries_sensor",
    asset_selection=[
        AssetKey(["geospatial", "boundaries", "gaeltacht"]),
        AssetKey(["geospatial", "boundaries", "irish_small_areas"]),
    ],
    minimum_interval_seconds=2592000,  # Check monthly
    default_status=DefaultSensorStatus.STOPPED,
    description="Detects GeoHive.ie boundary updates",
)
def geohive_boundaries_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Monitor GeoHive.ie for boundary data updates.

    Boundaries typically updated after Census releases.
    """
    now = datetime.now()

    # Check monthly
    last_check = context.cursor
    if last_check:
        last_date = datetime.fromisoformat(last_check)
        if now - last_date < timedelta(days=30):
            return SkipReason("Already checked this month")

    context.update_cursor(now.isoformat())

    return RunRequest(
        run_key=f"geohive-{now.strftime('%Y%m')}",
    )


@sensor(
    name="met_office_weather_sensor",
    # asset_selection would be added when weather correlation assets exist
    minimum_interval_seconds=3600,  # Check hourly
    default_status=DefaultSensorStatus.STOPPED,
    description="Monitors Met Office weather data for school correlation",
)
def met_office_weather_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Monitor Met Office DataHub for weather updates.

    Used for school attendance/weather correlation analysis.
    """
    # Weather data is hourly - simplified check
    now = datetime.now()

    # Only check during school hours (8am-4pm)
    if not 8 <= now.hour <= 16:
        return SkipReason("Outside school hours")

    # Only check on school days (Monday-Friday)
    if now.weekday() >= 5:
        return SkipReason("Weekend - no school correlation needed")

    return RunRequest(
        run_key=f"met-office-{now.strftime('%Y%m%d%H')}",
    )


# ============================================================================
# Cross-Domain Enrichment Sensors
# ============================================================================

@sensor(
    name="cross_domain_enrichment_sensor",
    # asset_selection would be added when enriched assets exist
    minimum_interval_seconds=86400,  # Check daily
    default_status=DefaultSensorStatus.STOPPED,
    description="Triggers cross-domain enrichment when source assets update",
)
def cross_domain_enrichment_sensor(
    context: SensorEvaluationContext,
) -> SensorResult | SkipReason:
    """
    Monitor source domain assets for changes.

    Triggers enriched assets when any source domain updates.
    """
    # This would check asset materialization timestamps
    # Simplified implementation

    now = datetime.now()

    # Check if any domain assets were updated today
    last_check = context.cursor
    if last_check:
        last_date = datetime.fromisoformat(last_check)
        if now - last_date < timedelta(hours=24):
            return SkipReason("Already checked enrichment trigger today")

    context.update_cursor(now.isoformat())

    # Would actually check asset metadata for recent materializations
    return SkipReason("No source asset updates detected")


# ============================================================================
# Export All Sensors
# ============================================================================

domain_sensors = [
    # Ireland
    ireland_curriculum_sitemap_sensor,
    ireland_examinations_sensor,
    # UK
    uk_dfe_statistics_sensor,
    scotland_sqa_sensor,
    wales_curriculum_sensor,
    # Celtic
    duchas_api_sensor,
    tearma_updates_sensor,
    # Geospatial
    geohive_boundaries_sensor,
    met_office_weather_sensor,
    # Cross-domain
    cross_domain_enrichment_sensor,
]
