"""Session-history helpers and CSV export."""

import csv
from datetime import datetime
from io import StringIO
from typing import Any

HISTORY_FIELDS = (
    "timestamp",
    "speaker",
    "source_language",
    "target_language",
    "source_text",
    "translated_text",
)


def make_history_entry(
    source_text: str,
    translated_text: str,
    source_language: str,
    target_language: str,
    speaker: str = "You",
) -> dict[str, str]:
    if not source_text.strip() or not translated_text.strip():
        raise ValueError("History entries require source and translated text.")
    return {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "speaker": speaker,
        "source_language": source_language,
        "target_language": target_language,
        "source_text": source_text.strip(),
        "translated_text": translated_text.strip(),
    }


def history_to_csv(entries: list[dict[str, Any]]) -> bytes:
    """Serialize session history as UTF-8 with BOM for common spreadsheet support."""
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=HISTORY_FIELDS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(entries)
    return buffer.getvalue().encode("utf-8-sig")
