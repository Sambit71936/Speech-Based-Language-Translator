import sys
from io import BytesIO
from types import SimpleNamespace

import pytest

from services.text_to_speech import TextToSpeechError, generate_speech


class FakeGTTS:
    def __init__(self, text, lang, slow):
        self.text = text
        self.lang = lang
        self.slow = slow

    def write_to_fp(self, output):
        output.write(b"fake-mp3-audio")


def test_tts_generates_audio_for_supported_language(monkeypatch):
    monkeypatch.setitem(sys.modules, "gtts", SimpleNamespace(gTTS=FakeGTTS))
    assert generate_speech("Hello", "en") == b"fake-mp3-audio"


def test_tts_rejects_empty_text_and_unsupported_language():
    with pytest.raises(TextToSpeechError, match="no translated text"):
        generate_speech(" ", "en")
    with pytest.raises(TextToSpeechError, match="not supported"):
        generate_speech("hello", "xx")


def test_tts_network_failure_is_reported(monkeypatch):
    class OfflineGTTS:
        def __init__(self, **kwargs):
            raise TimeoutError("network unavailable")

    monkeypatch.setitem(sys.modules, "gtts", SimpleNamespace(gTTS=OfflineGTTS))
    with pytest.raises(TextToSpeechError, match="internet connection"):
        generate_speech("hello", "en")
