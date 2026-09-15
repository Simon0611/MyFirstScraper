"""CLI entry point for the quotes.toscrape.com scraper."""

from __future__ import annotations

import logging
import sys

from quotes_scraper.config import ScraperConfig
from quotes_scraper.logging_setup import configure_logging
from quotes_scraper.pipeline import run_scraper

logger = logging.getLogger(__name__)


def main() -> int:
    """Run the scraper and return a process exit code."""
    config = ScraperConfig()
    configure_logging(config.log_file)

    try:
        records = run_scraper(config)
    except Exception:
        logger.exception("Scraper failed")
        return 1

    print(f"Saved {len(records)} quotes to {config.output_csv} and {config.output_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
