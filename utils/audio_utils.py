"""Safe temporary storage for uploaded or recorded audio."""

from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterator

from utils.validators import validate_audio


@contextmanager
def temporary_audio_file(data: bytes, filename: str) -> Iterator[Path]:
    """Write validated audio to a temporary file and always remove it afterward."""
    suffix = validate_audio(data, filename)
    path: Path | None = None
    try:
        with NamedTemporaryFile(mode="wb", suffix=suffix, prefix="speech-translator-", delete=False) as audio_file:
            audio_file.write(data)
            path = Path(audio_file.name)
        yield path
    finally:
        if path is not None:
            path.unlink(missing_ok=True)
