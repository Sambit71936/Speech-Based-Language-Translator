"""Text-to-speech adapter backed by gTTS (requires an internet connection)."""

from io import BytesIO

from config import LANGUAGES


class TextToSpeechError(RuntimeError):
    """A user-safe text-to-speech error."""


def generate_speech(text: str, language_code: str) -> bytes:
    if not isinstance(text, str) or not text.strip():
        raise TextToSpeechError("There is no translated text to speak.")
    if language_code not in LANGUAGES.values():
        raise TextToSpeechError("A voice for the selected language is not supported.")

    try:
        from gtts import gTTS

        audio = BytesIO()
        gTTS(text=text.strip(), lang=language_code, slow=False).write_to_fp(audio)
        result = audio.getvalue()
    except ImportError as exc:
        raise TextToSpeechError(
            "The text-to-speech dependency is missing. Install project dependencies with "
            "'pip install -r requirements.txt'."
        ) from exc
    except Exception as exc:
        raise TextToSpeechError(
            "Audio generation failed. Check your internet connection or try another language voice."
        ) from exc

    if not result:
        raise TextToSpeechError("The text-to-speech service returned an empty audio file.")
    return result
