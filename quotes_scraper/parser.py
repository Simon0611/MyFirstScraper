"""HTML parsing for quote listing pages."""

from __future__ import annotations

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from quotes_scraper.cleaning import clean_tags, clean_text

logger = logging.getLogger(__name__)


def parse_quotes(html: str, page_url: str) -> list[dict[str, object]]:
    """Extract cleaned quote records from a listing page."""
    soup = BeautifulSoup(html, "lxml")
    records: list[dict[str, object]] = []

    for quote_el in soup.select("div.quote"):
        try:
            record = _parse_quote_block(quote_el, page_url)
        except Exception:
            logger.exception("Failed to parse a quote block on %s", page_url)
            continue

        if record:
            records.append(record)

    logger.info("Parsed %s quotes from %s", len(records), page_url)
    return records


def find_next_page(html: str, page_url: str) -> str | None:
    """Return the absolute URL of the next page, if pagination continues."""
    soup = BeautifulSoup(html, "lxml")
    next_link = soup.select_one("li.next > a")
    if not next_link or not next_link.get("href"):
        return None
    return urljoin(page_url, str(next_link["href"]))


def _parse_quote_block(quote_el: Tag, page_url: str) -> dict[str, object] | None:
    text_el = quote_el.select_one("span.text")
    author_el = quote_el.select_one("small.author")
    author_link_el = quote_el.select_one("span a[href*='/author/']") or quote_el.select_one("a[href*='/author/']")

    quote_text = clean_text(text_el.get_text() if text_el else "")
    author = clean_text(author_el.get_text() if author_el else "")
    author_profile_url = ""
    if author_link_el and author_link_el.get("href"):
        author_profile_url = urljoin(page_url, str(author_link_el["href"]))

    tags = clean_tags(tag.get_text() for tag in quote_el.select("div.tags a.tag"))

    if not quote_text or not author:
        logger.warning("Skipping incomplete quote on %s", page_url)
        return None

    return {
        "quote": quote_text,
        "author": author,
        "tags": tags,
        "author_profile_url": author_profile_url,
        "source_page": page_url,
    }
