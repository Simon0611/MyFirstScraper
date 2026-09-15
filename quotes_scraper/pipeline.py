"""End-to-end scrape pipeline."""

from __future__ import annotations

import logging
from urllib.parse import urljoin

from quotes_scraper.config import ScraperConfig
from quotes_scraper.exporter import export_records
from quotes_scraper.http_client import HttpClient
from quotes_scraper.parser import find_next_page, parse_quotes

logger = logging.getLogger(__name__)


def run_scraper(config: ScraperConfig | None = None) -> list[dict[str, object]]:
    """Crawl all listing pages, clean records, and write CSV/JSON outputs."""
    config = config or ScraperConfig()
    client = HttpClient(config)
    records: list[dict[str, object]] = []
    seen_quotes: set[tuple[str, str]] = set()
    page_url = urljoin(config.base_url, "/")
    page_number = 0

    try:
        while page_url:
            page_number += 1
            logger.info("Scraping page %s: %s", page_number, page_url)
            response = client.get(page_url)
            if response is None:
                logger.error("Stopping crawl because %s could not be fetched", page_url)
                break

            page_records = parse_quotes(response.text, page_url)
            for record in page_records:
                key = (str(record["quote"]), str(record["author"]))
                if key in seen_quotes:
                    continue
                seen_quotes.add(key)
                records.append(record)

            next_url = find_next_page(response.text, page_url)
            if next_url and next_url != page_url:
                client.polite_pause()
                page_url = next_url
            else:
                page_url = None
    except Exception:
        logger.exception("Unexpected error while crawling quotes")
        raise
    finally:
        client.close()

    if not records:
        logger.warning("No quotes were collected; output files will be empty")

    export_records(records, config.output_csv, config.output_json)
    logger.info("Scrape complete: %s unique quotes from %s pages", len(records), page_number)
    return records
