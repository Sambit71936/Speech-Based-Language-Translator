"""Shared configuration for Speech-Based Language Translator."""

import os

APP_NAME = "Speech-Based Language Translator"
DEFAULT_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
MAX_AUDIO_SIZE_MB = int(os.getenv("MAX_AUDIO_SIZE_MB", "25"))
MAX_AUDIO_SIZE_BYTES = MAX_AUDIO_SIZE_MB * 1024 * 1024
TRANSLATION_TIMEOUT_SECONDS = 15

# Codes are accepted by Whisper, GoogleTranslator and gTTS in the usual cases.
# Providers may have small differences in their long-tail language coverage.
LANGUAGES = {
    "Afrikaans": "af",
    "Arabic": "ar",
    "Bengali": "bn",
    "Bulgarian": "bg",
    "Chinese (Simplified)": "zh-CN",
    "Chinese (Traditional)": "zh-TW",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Dutch": "nl",
    "English": "en",
    "Finnish": "fi",
    "French": "fr",
    "German": "de",
    "Greek": "el",
    "Gujarati": "gu",
    "Hebrew": "iw",
    "Hindi": "hi",
    "Hungarian": "hu",
    "Indonesian": "id",
    "Italian": "it",
    "Japanese": "ja",
    "Kannada": "kn",
    "Korean": "ko",
    "Malay": "ms",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Nepali": "ne",
    "Norwegian": "no",
    "Persian": "fa",
    "Polish": "pl",
    "Portuguese": "pt",
    "Punjabi": "pa",
    "Romanian": "ro",
    "Russian": "ru",
    "Spanish": "es",
    "Swahili": "sw",
    "Swedish": "sv",
    "Tamil": "ta",
    "Telugu": "te",
    "Thai": "th",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Urdu": "ur",
    "Vietnamese": "vi",
}

AUTO_DETECT = "Auto-detect"
LANGUAGE_BY_CODE = {code: name for name, code in LANGUAGES.items()}
SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".mp4", ".ogg", ".flac", ".webm", ".mpeg"}
