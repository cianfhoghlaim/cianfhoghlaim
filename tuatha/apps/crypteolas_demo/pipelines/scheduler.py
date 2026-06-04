"""
Pipeline scheduler for incremental crypto data updates.

Uses APScheduler for reliable scheduling with:
- Configurable intervals per source
- Rate limit awareness
- Failure recovery
"""

import logging
from datetime import datetime
from typing import Any, Callable, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from pipelines.shared.config_loader import load_sources_config

logger = logging.getLogger(__name__)


# Default schedules per source type
DEFAULT_SCHEDULES = {
    # Funding rates: every 8 hours (align with funding periods)
    "binance_funding": {"hours": 8},
    # Price data: hourly
    "coingecko_prices": {"hours": 1},
    # TVL/Yields: every 6 hours
    "defillama": {"hours": 6},
    # Subgraphs: every 4 hours
    "aave_subgraph": {"hours": 4},
    "pendle_subgraph": {"hours": 4},
    # Documentation: daily at 2 AM
    "firecrawl_docs": {"cron": "0 2 * * *"},
}


class CryptoDataScheduler:
    """
    Scheduler for crypto data pipelines.

    Coordinates incremental updates across all data sources
    with rate limiting and failure handling.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        timezone: str = "UTC",
    ):
        """
        Initialize scheduler.

        Args:
            config_path: Path to sources.yaml config
            timezone: Scheduler timezone
        """
        self.config = load_sources_config(config_path) if config_path else {}
        self.scheduler = BackgroundScheduler(timezone=timezone)
        self.job_history: list[dict[str, Any]] = []

        # Register event listeners
        self.scheduler.add_listener(
            self._on_job_executed,
            EVENT_JOB_EXECUTED,
        )
        self.scheduler.add_listener(
            self._on_job_error,
            EVENT_JOB_ERROR,
        )

    def _on_job_executed(self, event) -> None:
        """Log successful job execution."""
        self.job_history.append({
            "job_id": event.job_id,
            "scheduled_time": event.scheduled_run_time,
            "status": "success",
            "timestamp": datetime.utcnow(),
        })
        logger.info(f"Job {event.job_id} executed successfully")

    def _on_job_error(self, event) -> None:
        """Log job errors."""
        self.job_history.append({
            "job_id": event.job_id,
            "scheduled_time": event.scheduled_run_time,
            "status": "error",
            "error": str(event.exception),
            "timestamp": datetime.utcnow(),
        })
        logger.error(f"Job {event.job_id} failed: {event.exception}")

    def add_pipeline_job(
        self,
        job_id: str,
        func: Callable,
        schedule: Optional[dict] = None,
        **kwargs,
    ) -> None:
        """
        Add a pipeline job to the scheduler.

        Args:
            job_id: Unique job identifier
            func: Pipeline function to execute
            schedule: Schedule config (interval or cron)
            **kwargs: Arguments to pass to pipeline function
        """
        if schedule is None:
            schedule = DEFAULT_SCHEDULES.get(job_id, {"hours": 6})

        if "cron" in schedule:
            trigger = CronTrigger.from_crontab(schedule["cron"])
        else:
            trigger = IntervalTrigger(**schedule)

        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            name=job_id,
            kwargs=kwargs,
            replace_existing=True,
            max_instances=1,  # Prevent overlapping runs
            coalesce=True,  # Skip missed runs
        )

        logger.info(f"Added job {job_id} with schedule {schedule}")

    def register_all_pipelines(self) -> None:
        """Register all crypto data pipelines with default schedules."""
        from pipelines.sources.binance import run_binance_pipeline
        from pipelines.sources.coingecko import run_coingecko_pipeline
        from pipelines.sources.defillama import run_defillama_pipeline
        from pipelines.sources.subgraphs import run_subgraph_pipeline

        # Binance funding rates (critical for Ethena)
        self.add_pipeline_job(
            "binance_funding",
            run_binance_pipeline,
            symbols=["ETHUSDT", "BTCUSDT"],
            days_back=7,  # Incremental: last 7 days
        )

        # CoinGecko prices
        self.add_pipeline_job(
            "coingecko_prices",
            run_coingecko_pipeline,
            tokens=["ethena-usde", "ethena-staked-usde", "ethereum"],
            days=1,  # Last day only for incremental
        )

        # DeFiLlama yields and TVL
        self.add_pipeline_job(
            "defillama",
            run_defillama_pipeline,
            protocols=["ethena", "aave", "pendle", "lido"],
        )

        # Aave subgraph
        self.add_pipeline_job(
            "aave_subgraph",
            run_subgraph_pipeline,
            protocols=["aave"],
        )

        # Pendle subgraph
        self.add_pipeline_job(
            "pendle_subgraph",
            run_subgraph_pipeline,
            protocols=["pendle"],
        )

        logger.info("All pipelines registered")

    def start(self) -> None:
        """Start the scheduler."""
        self.scheduler.start()
        logger.info("Scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    def run_now(self, job_id: str) -> None:
        """
        Trigger immediate execution of a job.

        Args:
            job_id: Job to execute
        """
        job = self.scheduler.get_job(job_id)
        if job:
            job.modify(next_run_time=datetime.now())
            logger.info(f"Triggered immediate run of {job_id}")
        else:
            logger.warning(f"Job {job_id} not found")

    def get_status(self) -> dict[str, Any]:
        """Get scheduler and job status."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            })

        return {
            "running": self.scheduler.running,
            "jobs": jobs,
            "recent_history": self.job_history[-10:],
        }


def run_all_once() -> None:
    """
    Run all pipelines once (for initial load or manual refresh).
    """
    from pipelines.sources.binance import run_binance_pipeline
    from pipelines.sources.coingecko import run_coingecko_pipeline
    from pipelines.sources.defillama import run_defillama_pipeline
    from pipelines.sources.subgraphs import run_subgraph_pipeline

    logger.info("Running all pipelines (one-time)")

    # Run in sequence to avoid rate limiting
    pipelines = [
        ("coingecko", run_coingecko_pipeline),
        ("defillama", run_defillama_pipeline),
        ("binance", run_binance_pipeline),
        ("subgraphs", run_subgraph_pipeline),
    ]

    results = {}
    for name, func in pipelines:
        try:
            logger.info(f"Running {name}...")
            result = func()
            results[name] = {"status": "success", "result": str(result)}
            logger.info(f"Completed {name}")
        except Exception as e:
            results[name] = {"status": "error", "error": str(e)}
            logger.error(f"Error in {name}: {e}")

    return results


def create_scheduler(
    config_path: Optional[str] = None,
    register_all: bool = True,
) -> CryptoDataScheduler:
    """
    Factory function to create configured scheduler.

    Args:
        config_path: Path to sources.yaml
        register_all: Whether to register all default pipelines

    Returns:
        Configured CryptoDataScheduler instance
    """
    scheduler = CryptoDataScheduler(config_path=config_path)

    if register_all:
        scheduler.register_all_pipelines()

    return scheduler


if __name__ == "__main__":
    import time

    logging.basicConfig(level=logging.INFO)

    # Run all pipelines once
    print("Running initial data load...")
    results = run_all_once()

    for name, result in results.items():
        print(f"{name}: {result['status']}")

    # Optionally start scheduler
    # scheduler = create_scheduler()
    # scheduler.start()
    # try:
    #     while True:
    #         time.sleep(60)
    #         print(scheduler.get_status())
    # except KeyboardInterrupt:
    #     scheduler.stop()
