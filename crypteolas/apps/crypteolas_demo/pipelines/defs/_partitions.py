"""
Shared partition definitions for crypteolas assets.
"""

from datetime import datetime, timedelta

from dagster import (
    DailyPartitionsDefinition,
    HourlyPartitionsDefinition,
    StaticPartitionsDefinition,
)


# Daily partitions for historical data
daily_partitions = DailyPartitionsDefinition(
    start_date="2024-01-01",
    end_offset=1,
)

# Hourly partitions for real-time data
hourly_partitions = HourlyPartitionsDefinition(
    start_date=datetime.utcnow() - timedelta(days=7),
    end_offset=1,
)

# Protocol partitions for documentation
protocol_partitions = StaticPartitionsDefinition(
    ["ethena", "aave", "pendle", "lido", "eigenlayer", "curve"]
)
