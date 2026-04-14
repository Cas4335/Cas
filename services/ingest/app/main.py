"""
PHX Ingest Service — main entry point.

Loads sources from sources.yaml and runs the ingest pipeline on a schedule.
Can also be triggered for a single run with --once flag.
"""

import argparse
import sys
import time
import os
from pathlib import Path
import yaml
import structlog

from app.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger(__name__)


def load_sources(config_path: str) -> list:
    """Load and validate sources from sources.yaml."""
    path = Path(config_path)
    if not path.exists():
        logger.error("sources_config_not_found", path=config_path)
        return []

    with open(path) as f:
        data = yaml.safe_load(f)

    sources = data.get("sources", [])
    enabled = [s for s in sources if s.get("enabled", True)]
    logger.info("sources_loaded", total=len(sources), enabled=len(enabled))
    return enabled


def run_once(sources: list) -> None:
    """Run ingest for all enabled sources once."""
    from app.pipeline import run_source_sync

    if not sources:
        logger.warning("no_enabled_sources")
        return

    for source in sources:
        source_id = source.get("id", "unknown")
        logger.info("syncing_source", source_id=source_id)
        try:
            counts = run_source_sync(source)
            logger.info("source_sync_done", source_id=source_id, **counts)
        except Exception as e:
            logger.error("source_sync_error", source_id=source_id, error=str(e))


def run_scheduled(sources: list, interval_seconds: int) -> None:
    """Run ingest on a schedule until interrupted."""
    logger.info("scheduler_starting", interval_seconds=interval_seconds)
    while True:
        logger.info("sync_cycle_start")
        run_once(sources)
        logger.info("sync_cycle_done", next_in_seconds=interval_seconds)
        time.sleep(interval_seconds)


def main():
    parser = argparse.ArgumentParser(description="PHX Ingest Service")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    sources = load_sources(settings.SOURCES_CONFIG_PATH)

    if args.once:
        run_once(sources)
        sys.exit(0)
    else:
        run_scheduled(sources, settings.INGEST_SCHEDULE_SECONDS)


if __name__ == "__main__":
    main()
