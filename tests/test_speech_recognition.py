import sys
from types import SimpleNamespace

import pytest

from services import speech_recognition as speech
from services.speech_recognition import SpeechRecognitionError


def wav_bytes():
    body = b"WAVEdata"
    return b"RIFF" + len(body).to_bytes(4, "little") + body


class FakeModel:
    def transcribe(self, path, **kwargs):
        assert path.endswith(".wav")
        assert kwargs["language"] == "en"
        return iter([SimpleNamespace(text=" Hello "), SimpleNamespace(text="world.")]), SimpleNamespace(
            language="en", language_probability=0.99
        )


def test_speech_recognition_uses_model_and_returns_detected_language(monkeypatch):
    monkeypatch.setattr(speech, "_load_model", lambda _size: FakeModel())
    result = speech.transcribe_audio(wav_bytes(), "clip.wav", "en")
    assert result.text == "Hello world."
    assert result.detected_language == "English"
    assert result.language_probability == 0.99


def test_missing_faster_whisper_dependency_has_helpful_message(monkeypatch):
    monkeypatch.setitem(sys.modules, "faster_whisper", None)
    speech._load_model.cache_clear()
    with pytest.raises(SpeechRecognitionError, match="not installed"):
        speech._load_model("base")
    speech._load_model.cache_clear()


def test_speech_model_download_or_load_failure_is_actionable(monkeypatch):
    class BrokenModel:
        def __init__(self, *args, **kwargs):
            raise OSError("model download failed")

    monkeypatch.setitem(sys.modules, "faster_whisper", SimpleNamespace(WhisperModel=BrokenModel))
    speech._load_model.cache_clear()
    with pytest.raises(SpeechRecognitionError, match="first model download"):
        speech._load_model("broken-model")
    speech._load_model.cache_clear()
