import csv
from io import StringIO

import pytest

from utils.history import HISTORY_FIELDS, history_to_csv, make_history_entry


def test_history_entry_includes_speaker_and_session_metadata():
    entry = make_history_entry("Hello", "வணக்கம்", "English", "Tamil", "Speaker A")
    assert entry["speaker"] == "Speaker A"
    assert entry["source_text"] == "Hello"
    assert entry["translated_text"] == "வணக்கம்"
    assert entry["timestamp"]


def test_history_rejects_empty_text():
    with pytest.raises(ValueError):
        make_history_entry("", "translation", "English", "Tamil")


def test_history_csv_export_has_headers_and_round_trips_unicode():
    entry = make_history_entry("Hello", "வணக்கம்", "English", "Tamil")
    exported = history_to_csv([entry]).decode("utf-8-sig")
    rows = list(csv.DictReader(StringIO(exported)))
    assert tuple(rows[0].keys()) == HISTORY_FIELDS
    assert rows[0]["translated_text"] == "வணக்கம்"
