"""Write cleaned quote records to CSV and JSON."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Sequence

logger = logging.getLogger(__name__)

_FIELDNAMES = ("quote", "author", "tags", "author_profile_url", "source_page")


def export_records(
    records: Sequence[dict[str, object]],
    csv_path: Path,
    json_path: Path,
) -> None:
    """Persist records to CSV (tags as pipe-separated) and JSON (tags as arrays)."""
    _write_csv(records, csv_path)
    _write_json(records, json_path)
    logger.info("Exported %s records to %s and %s", len(records), csv_path, json_path)


def _write_csv(records: Sequence[dict[str, object]], path: Path) -> None:
    try:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=_FIELDNAMES)
            writer.writeheader()
            for record in records:
                row = dict(record)
                tags = record.get("tags", [])
                row["tags"] = "|".join(str(tag) for tag in tags) if isinstance(tags, list) else tags
                writer.writerow(row)
    except OSError:
        logger.exception("Failed to write CSV file %s", path)
        raise


def _write_json(records: Sequence[dict[str, object]], path: Path) -> None:
    try:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(list(records), handle, ensure_ascii=False, indent=2)
    except OSError:
        logger.exception("Failed to write JSON file %s", path)
        raise
