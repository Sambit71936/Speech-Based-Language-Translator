from pathlib import Path

import pytest

from utils.audio_utils import temporary_audio_file
from utils.validators import AudioValidationError


def wav_bytes():
    body = b"WAVEdata"
    return b"RIFF" + len(body).to_bytes(4, "little") + body


def test_temporary_audio_file_exists_during_context_and_is_removed_afterward():
    path = None
    with temporary_audio_file(wav_bytes(), "clip.wav") as temp_path:
        path = temp_path
        assert path.is_file()
        assert path.read_bytes() == wav_bytes()
    assert path is not None
    assert not path.exists()


def test_temporary_audio_file_rejects_invalid_upload():
    with pytest.raises(AudioValidationError):
        with temporary_audio_file(b"bad", "clip.wav"):
            pytest.fail("invalid audio should not be written")
