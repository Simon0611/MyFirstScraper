"""Runtime configuration for the quotes scraper."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScraperConfig:
    """Immutable scraper settings."""

    base_url: str = "http://quotes.toscrape.com"
    timeout_seconds: float = 15.0
    max_retries: int = 3
    retry_backoff_seconds: float = 1.5
    request_delay_seconds: tuple[float, float] = (0.4, 1.2)
    output_csv: Path = Path("quotes_clean.csv")
    output_json: Path = Path("quotes_clean.json")
    log_file: Path = Path("scraper.log")
