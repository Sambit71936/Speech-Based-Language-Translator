"""Input validation helpers shared by the UI and service layer."""

from pathlib import Path

from config import MAX_AUDIO_SIZE_BYTES, SUPPORTED_AUDIO_EXTENSIONS


class AudioValidationError(ValueError):
    """Raised when an audio upload is empty, too large, or not a supported type."""


def validate_audio(
    data: bytes | bytearray | None,
    filename: str,
    max_size_bytes: int = MAX_AUDIO_SIZE_BYTES,
) -> str:
    """Validate size, extension, and basic file signature; return normalized suffix."""
    if not data:
        raise AudioValidationError("The audio recording is empty. Please record or upload audio again.")
    if not isinstance(data, (bytes, bytearray)):
        raise AudioValidationError("Audio data must be a valid file upload or recording.")
    if len(data) > max_size_bytes:
        size_mb = max_size_bytes / (1024 * 1024)
        raise AudioValidationError(f"Audio exceeds the {size_mb:g} MB upload limit.")

    suffix = Path(filename or "").suffix.lower()
    if suffix not in SUPPORTED_AUDIO_EXTENSIONS:
        allowed = ", ".join(sorted(SUPPORTED_AUDIO_EXTENSIONS))
        raise AudioValidationError(f"Unsupported audio format. Supported formats: {allowed}.")

    valid_signature = {
        ".wav": lambda content: content.startswith(b"RIFF") and content[8:12] == b"WAVE",
        ".mp3": lambda content: content.startswith(b"ID3") or (
            len(content) > 1 and content[0] == 0xFF and content[1] & 0xE0 == 0xE0
        ),
        ".mpeg": lambda content: content.startswith(b"ID3") or (
            len(content) > 1 and content[0] == 0xFF and content[1] & 0xE0 == 0xE0
        ),
        ".m4a": lambda content: len(content) >= 8 and content[4:8] == b"ftyp",
        ".mp4": lambda content: len(content) >= 8 and content[4:8] == b"ftyp",
        ".ogg": lambda content: content.startswith(b"OggS"),
        ".flac": lambda content: content.startswith(b"fLaC"),
        ".webm": lambda content: content.startswith(b"\x1aE\xdf\xa3"),
    }[suffix]
    if not valid_signature(data):
        raise AudioValidationError("The file contents do not match the selected audio format.")
    return suffix
