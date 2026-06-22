"""
DLT source for Beaconcha.in API - Ethereum staking data.

API Reference: https://beaconcha.in/api/v1/docs

Provides access to:
- Ethereum staking APR
- Validator statistics
- Network metrics
"""

from datetime import datetime, timezone
from typing import Any, Iterator, Optional

import dlt
import httpx

# Beaconcha.in API base URL
BEACONCHAIN_API_URL = "https://beaconcha.in/api/v1"


def _get_client() -> httpx.Client:
    """Get HTTP client for Beaconcha.in API."""
    return httpx.Client(base_url=BEACONCHAIN_API_URL, timeout=30.0)


@dlt.resource(
    name="eth_staking_apr",
    primary_key=["day"],
    write_disposition="merge",
)
def eth_staking_apr(
    days: int = 30,
) -> Iterator[dict[str, Any]]:
    """
    Fetch Ethereum staking APR history.

    Args:
        days: Number of days of history

    Yields:
        Daily staking APR records
    """
    with _get_client() as client:
        try:
            # Get latest store data
            response = client.get("/ethstore/latest")
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK":
                import logging
                logging.warning(f"Beaconchain ethstore API status: {data.get('status')}")
                return

            store_data = data.get("data", {})
            yield {
                "day": store_data.get("day"),
                "effective_balance_gwei": store_data.get("effectiveBalanceGwei"),
                "total_valid_balance_gwei": store_data.get("totalValidBalanceGwei"),
                "average_validator_balance_gwei": store_data.get("avgValidatorBalanceGwei"),
                "validator_count": store_data.get("validatorsCount"),
                "apr": store_data.get("apr"),
                "apr_percent": float(store_data.get("apr", 0)) * 100,
                "network": "ethereum",
                "data_source": "beaconchain",
                "data_status": "success",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            # Log error but don't yield - errors shouldn't go to the eth_staking_apr table
            import logging
            logging.warning(f"Beaconchain staking APR API error: {e}")


@dlt.resource(
    name="eth_network_stats",
    primary_key=["timestamp"],
    write_disposition="replace",
)
def eth_network_stats() -> Iterator[dict[str, Any]]:
    """
    Fetch current Ethereum network statistics.

    Yields:
        Network statistics record
    """
    with _get_client() as client:
        try:
            response = client.get("/epoch/latest")
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK":
                return

            epoch_data = data.get("data", {})
            yield {
                "epoch": epoch_data.get("epoch"),
                "finalized": epoch_data.get("finalized"),
                "voted_ether": epoch_data.get("votedether"),
                "eligible_ether": epoch_data.get("eligibleether"),
                "global_participation_rate": epoch_data.get("globalparticipationrate"),
                "attestations_count": epoch_data.get("attestationscount"),
                "proposer_slashings_count": epoch_data.get("proposerslashingscount"),
                "attester_slashings_count": epoch_data.get("attesterslashingscount"),
                "deposits_count": epoch_data.get("depositscount"),
                "voluntary_exits_count": epoch_data.get("voluntaryexitscount"),
                "validators_count": epoch_data.get("validatorscount"),
                "average_validator_balance": epoch_data.get("averagevalidatorbalance"),
                "total_validator_balance": epoch_data.get("totalvalidatorbalance"),
                "network": "ethereum",
                "data_source": "beaconchain",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data_status": "success",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            # Log error but don't yield - errors shouldn't go to the eth_network_stats table
            import logging
            logging.warning(f"Beaconchain network stats API error: {e}")


@dlt.resource(
    name="eth_validator_queue",
    primary_key=["timestamp"],
    write_disposition="replace",
)
def eth_validator_queue() -> Iterator[dict[str, Any]]:
    """
    Fetch validator queue statistics.

    Yields:
        Queue statistics record
    """
    with _get_client() as client:
        try:
            response = client.get("/validators/queue")
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK":
                return

            queue_data = data.get("data", {})
            yield {
                "beaconchain_entering": queue_data.get("beaconchain_entering"),
                "beaconchain_exiting": queue_data.get("beaconchain_exiting"),
                "validators_count": queue_data.get("validatorscount"),
                "entry_wait_time_epochs": queue_data.get("entry_waittime"),
                "exit_wait_time_epochs": queue_data.get("exit_waittime"),
                "estimated_entry_wait_days": queue_data.get("entry_waittime", 0) * 6.4 / 60 / 24 if queue_data.get("entry_waittime") else None,
                "estimated_exit_wait_days": queue_data.get("exit_waittime", 0) * 6.4 / 60 / 24 if queue_data.get("exit_waittime") else None,
                "network": "ethereum",
                "data_source": "beaconchain",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data_status": "success",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            # Log error but don't yield - errors shouldn't go to the eth_validator_queue table
            import logging
            logging.warning(f"Beaconchain validator queue API error: {e}")


@dlt.resource(
    name="eth_rewards_chart",
    primary_key=["timestamp"],
    write_disposition="merge",
)
def eth_rewards_chart(
    days: int = 30,
) -> Iterator[dict[str, Any]]:
    """
    Fetch historical rewards/APR chart data.

    Args:
        days: Number of days of history

    Yields:
        Daily rewards records
    """
    with _get_client() as client:
        try:
            response = client.get(
                "/chart/staking_rewards",
                params={"days": days},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK":
                return

            for point in data.get("data", []):
                yield {
                    "timestamp": point.get("time"),
                    "apr": point.get("apr"),
                    "apr_percent": float(point.get("apr", 0)) * 100,
                    "effective_balance": point.get("effectiveBalance"),
                    "total_balance": point.get("totalBalance"),
                    "network": "ethereum",
                    "data_source": "beaconchain",
                    "data_status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            # Log error but don't yield - errors shouldn't go to the eth_rewards_chart table
            import logging
            logging.warning(f"Beaconchain rewards chart API error: {e}")


@dlt.source(name="beaconchain_source")
def beaconchain_source(
    include_apr: bool = True,
    include_network_stats: bool = True,
    include_queue: bool = True,
    include_rewards_chart: bool = False,
    days: int = 30,
) -> Iterator[Any]:
    """
    Beaconcha.in data source for Ethereum staking metrics.

    Args:
        include_apr: Include current staking APR
        include_network_stats: Include network statistics
        include_queue: Include validator queue
        include_rewards_chart: Include historical rewards chart
        days: Days of history for charts

    Yields:
        Beaconchain data resources
    """
    if include_apr:
        yield eth_staking_apr()
    if include_network_stats:
        yield eth_network_stats()
    if include_queue:
        yield eth_validator_queue()
    if include_rewards_chart:
        yield eth_rewards_chart(days=days)


def run_beaconchain_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "defi_raw",
):
    """Run Beaconcha.in pipeline standalone."""
    pipeline = dlt.pipeline(
        pipeline_name="beaconchain_data",
        destination=destination,
        dataset_name=dataset_name,
    )

    source = beaconchain_source()
    load_info = pipeline.run(source)
    print(f"Beaconchain pipeline completed: {load_info}")
    return pipeline


if __name__ == "__main__":
    run_beaconchain_pipeline()
