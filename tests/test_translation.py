import pytest

from services.translation import TranslationError, translate_text


class FakeTranslator:
    def __init__(self, **kwargs):
        self.options = kwargs

    def translate(self, text):
        return f"translated:{text}"


def test_translation_returns_provider_result_and_passes_selected_languages():
    result = translate_text("  Hello!  ", "en", "ta", FakeTranslator)
    assert result == "translated:Hello!"


def test_empty_translation_input_is_rejected():
    with pytest.raises(TranslationError, match="some text"):
        translate_text("   ", "en", "ta", FakeTranslator)


def test_translation_network_failure_is_reported_without_faking_success():
    class OfflineTranslator:
        def __init__(self, **kwargs):
            pass

        def translate(self, text):
            raise TimeoutError("provider is offline")

    with pytest.raises(TranslationError, match="internet connection"):
        translate_text("hello", "en", "hi", OfflineTranslator)


def test_missing_translation_dependency_is_reported():
    def missing_dependency(**kwargs):
        raise ImportError("missing package")

    with pytest.raises(TranslationError, match="dependency is missing"):
        translate_text("hello", "en", "ta", missing_dependency)


def test_empty_provider_response_is_not_treated_as_translation():
    class EmptyTranslator:
        def __init__(self, **kwargs):
            pass

        def translate(self, text):
            return " "

    with pytest.raises(TranslationError, match="returned no translated text"):
        translate_text("hello", "en", "ta", EmptyTranslator)
