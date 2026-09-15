"""Structured logging configuration."""

from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(log_file: Path, level: int = logging.INFO) -> None:
    """Configure console and file logging with a consistent format."""
    log_format = (
        "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
