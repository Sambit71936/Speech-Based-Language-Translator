"""Replaceable text translation adapter (Google Translate via deep-translator)."""

from collections.abc import Callable

from config import LANGUAGES, TRANSLATION_TIMEOUT_SECONDS


class TranslationError(RuntimeError):
    """A user-safe translation error."""


def validate_language_codes(source_language: str, target_language: str) -> None:
    valid_sources = {"auto", *LANGUAGES.values()}
    if source_language not in valid_sources:
        raise TranslationError("The selected source language is not supported by this application.")
    if target_language not in LANGUAGES.values():
        raise TranslationError("The selected target language is not supported by this application.")
    if source_language != "auto" and source_language == target_language:
        raise TranslationError("Choose different source and target languages to translate.")


def translate_text(
    text: str,
    source_language: str,
    target_language: str,
    translator_factory: Callable | None = None,
) -> str:
    """Translate text, raising an explicit error rather than pretending on failure."""
    if not isinstance(text, str) or not text.strip():
        raise TranslationError("Enter or recognize some text before translating.")
    validate_language_codes(source_language, target_language)

    try:
        if translator_factory is None:
            from deep_translator import GoogleTranslator

            translator_factory = GoogleTranslator
        translator = translator_factory(
            source=source_language,
            target=target_language,
            timeout=TRANSLATION_TIMEOUT_SECONDS,
        )
        translated = translator.translate(text.strip())
    except ImportError as exc:
        raise TranslationError(
            "The translation dependency is missing. Install project dependencies with "
            "'pip install -r requirements.txt'."
        ) from exc
    except Exception as exc:
        raise TranslationError(
            "Translation failed. Check your internet connection, then try again. "
            "The translation provider may also be temporarily rate-limiting requests."
        ) from exc

    if not isinstance(translated, str) or not translated.strip():
        raise TranslationError("The translation provider returned no translated text. Please try again.")
    return translated.strip()
