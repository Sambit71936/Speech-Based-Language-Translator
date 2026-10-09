"""Speech-to-text adapter backed by Faster-Whisper."""

from functools import lru_cache
from pathlib import Path
from typing import NamedTuple

from config import DEFAULT_MODEL_SIZE, LANGUAGE_BY_CODE
from utils.audio_utils import temporary_audio_file
from utils.validators import validate_audio


class SpeechRecognitionError(RuntimeError):
    """A user-safe speech recognition error."""


class RecognitionResult(NamedTuple):
    text: str
    detected_language: str | None
    language_probability: float | None


WHISPER_LANGUAGE_ALIASES = {"zh-CN": "zh", "zh-TW": "zh", "iw": "he"}
DETECTED_LANGUAGE_ALIASES = {"zh": "Chinese (Simplified)", "he": "Hebrew"}


@lru_cache(maxsize=2)
def _load_model(model_size: str):
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise SpeechRecognitionError(
            "Faster-Whisper is not installed. Install project dependencies with "
            "'pip install -r requirements.txt'."
        ) from exc

    try:
        return WhisperModel(model_size, device="cpu", compute_type="int8")
    except Exception as exc:
        raise SpeechRecognitionError(
            "The speech model could not be loaded. Check your internet connection "
            "for the first model download, available disk space, and the model name."
        ) from exc


def transcribe_audio(
    audio_data: bytes,
    filename: str = "recording.webm",
    source_language: str = "auto",
    model_size: str = DEFAULT_MODEL_SIZE,
) -> RecognitionResult:
    """Transcribe validated audio; first use downloads the selected Whisper model."""
    validate_audio(audio_data, filename)
    if source_language != "auto" and source_language not in LANGUAGE_BY_CODE:
        raise SpeechRecognitionError("The selected source language is not supported.")

    model = _load_model(model_size)
    try:
        with temporary_audio_file(audio_data, filename) as audio_path:
            segments, info = model.transcribe(
                str(audio_path),
                language=None if source_language == "auto" else WHISPER_LANGUAGE_ALIASES.get(source_language, source_language),
                beam_size=5,
                vad_filter=True,
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()
    except SpeechRecognitionError:
        raise
    except Exception as exc:
        raise SpeechRecognitionError(
            "Speech recognition failed. Try a clearer recording or a supported audio file."
        ) from exc

    if not text:
        raise SpeechRecognitionError("No speech was detected. Please record or upload audio with speech.")

    detected = getattr(info, "language", None)
    return RecognitionResult(
        text=text,
        detected_language=LANGUAGE_BY_CODE.get(detected, DETECTED_LANGUAGE_ALIASES.get(detected, detected)),
        language_probability=getattr(info, "language_probability", None),
    )
