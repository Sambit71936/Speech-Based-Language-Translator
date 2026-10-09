import pytest

from config import LANGUAGES
from services.translation import TranslationError, validate_language_codes
from utils.validators import AudioValidationError, validate_audio


def wav_bytes(payload=b"audio"):
    body = b"WAVE" + payload
    return b"RIFF" + (len(body)).to_bytes(4, "little") + body


def test_valid_audio_is_accepted_and_suffix_normalized():
    assert validate_audio(wav_bytes(), "speech.WAV") == ".wav"


@pytest.mark.parametrize(
    ("data", "filename", "message"),
    [
        (b"", "speech.wav", "empty"),
        (wav_bytes(), "speech.exe", "Unsupported"),
        (b"not a wav", "speech.wav", "do not match"),
    ],
)
def test_audio_rejects_empty_invalid_type_and_mismatched_signature(data, filename, message):
    with pytest.raises(AudioValidationError, match=message):
        validate_audio(data, filename)


def test_audio_size_limit_is_enforced():
    with pytest.raises(AudioValidationError, match="upload limit"):
        validate_audio(wav_bytes(), "speech.wav", max_size_bytes=4)


def test_language_selection_accepts_auto_and_supported_pairs():
    validate_language_codes("auto", LANGUAGES["Tamil"])
    validate_language_codes(LANGUAGES["English"], LANGUAGES["Hindi"])


@pytest.mark.parametrize(
    ("source", "target"),
    [("unknown", "ta"), ("en", "unknown"), ("ta", "ta")],
)
def test_language_selection_rejects_invalid_or_identical_pair(source, target):
    with pytest.raises(TranslationError):
        validate_language_codes(source, target)
