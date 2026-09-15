"""HTTP client with random User-Agents, timeouts, and retries."""

from __future__ import annotations

import logging
import random
import time
from typing import Final

import requests
from fake_useragent import UserAgent
from requests import Response
from requests.exceptions import RequestException, Timeout

from quotes_scraper.config import ScraperConfig

logger = logging.getLogger(__name__)

_FALLBACK_USER_AGENTS: Final[tuple[str, ...]] = (
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0"
    ),
)


class HttpClient:
    """Thin requests wrapper with polite scraping defaults."""

    def __init__(self, config: ScraperConfig) -> None:
        self._config = config
        self._session = requests.Session()
        self._user_agent = self._build_user_agent()

    def _build_user_agent(self) -> UserAgent | None:
        try:
            return UserAgent()
        except Exception:
            logger.warning(
                "fake-useragent failed to initialize; using fallback User-Agents",
                exc_info=True,
            )
            return None

    def _random_user_agent(self) -> str:
        if self._user_agent is not None:
            try:
                return self._user_agent.random
            except Exception:
                logger.warning(
                    "Could not sample a random User-Agent; using fallback list",
                    exc_info=True,
                )
        return random.choice(_FALLBACK_USER_AGENTS)

    def get(self, url: str) -> Response | None:
        """GET a URL with retries. Returns None after exhausting retries."""
        last_error: Exception | None = None

        for attempt in range(1, self._config.max_retries + 1):
            headers = {
                "User-Agent": self._random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
            try:
                logger.info("Fetching %s (attempt %s/%s)", url, attempt, self._config.max_retries)
                response = self._session.get(
                    url,
                    headers=headers,
                    timeout=self._config.timeout_seconds,
                )
                response.raise_for_status()
                response.encoding = response.apparent_encoding or "utf-8"
                return response
            except Timeout as exc:
                last_error = exc
                logger.warning("Timeout fetching %s on attempt %s: %s", url, attempt, exc)
            except RequestException as exc:
                last_error = exc
                logger.warning("Request failed for %s on attempt %s: %s", url, attempt, exc)

            if attempt < self._config.max_retries:
                sleep_for = self._config.retry_backoff_seconds * attempt
                logger.info("Retrying %s in %.1f seconds", url, sleep_for)
                time.sleep(sleep_for)

        logger.error("Giving up on %s after %s attempts: %s", url, self._config.max_retries, last_error)
        return None

    def polite_pause(self) -> None:
        """Sleep a random interval between requests."""
        low, high = self._config.request_delay_seconds
        time.sleep(random.uniform(low, high))

    def close(self) -> None:
        self._session.close()
