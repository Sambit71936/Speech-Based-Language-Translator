# Speech-Based Language Translator

A Streamlit mini-project that records or uploads speech, converts it to editable text, translates it, and generates playable speech in the target language. The initial interface includes English, Tamil, Hindi, and dozens of additional languages supported by the selected providers.

## Features

- Browser microphone capture with explicit Start/Stop controls, plus audio upload.
- Faster-Whisper speech recognition with automatic language detection or a selected source language.
- Review and edit the recognized transcript before translating.
- Google Translate integration through `deep-translator` (no API key in the default configuration).
- gTTS translated-audio playback and MP3 download.
- Optional two-way conversation mode with language swap, speaker labels, and a session transcript. Turns are processed sequentially; this is not simultaneous interpretation.
- Session-only translation history with CSV export and a clear-history control.
- Audio size, file extension, basic file-signature and empty-input validation; temporary audio files are deleted after recognition.
- Service modules are separated from the Streamlit UI so providers can be replaced.

## Languages

English, Tamil, Hindi, Bengali, Gujarati, Kannada, Malayalam, Marathi, Telugu, Urdu, Arabic, Chinese (Simplified and Traditional), French, German, Spanish, Japanese, Korean, and other options in the selector. Speech recognition, translation, and TTS language coverage is not identical across providers. Whisper can recognize many more languages; translation/TTS are limited by the provider's supported language codes.

## Architecture and data flow

1. Browser mic component or uploader supplies an audio byte stream.
2. `utils/validators.py` checks that the file is non-empty, within size limits, has an accepted extension, and its signature matches that extension.
3. `utils/audio_utils.py` creates a temporary audio file; `services/speech_recognition.py` runs Faster-Whisper and returns text plus detected language. The temporary file is removed even on failure.
4. The user reviews/edits text in Streamlit. `services/translation.py` sends it to the configured translation provider.
5. `services/text_to_speech.py` generates MP3 speech, which the UI can play or download.
6. Translation text and metadata are retained only in Streamlit session state. Microphone recordings are not written to persistent storage by this app.

## Requirements and external services

- Python 3.11 (Python 3.10+ should generally work with these packages; the tested target is Python 3.11).
- Internet access is needed for the first Faster-Whisper model download, translation requests, and gTTS audio generation.
- The default Faster-Whisper `base` model runs on CPU using int8 quantization. Its weights are downloaded from Hugging Face on first use and cached outside this repository; download size and recognition speed depend on model/device.
- `deep-translator` accesses Google's translation web service. It uses no configured API key, but is an unofficial web integration and may be rate-limited, changed, or unavailable. No paid-API or uptime guarantee is implied.
- gTTS accesses Google's text-to-speech service and requires internet connectivity. Voices and quality depend on the remote service.
- The application is **not fully offline**. Only speech recognition runs locally after the model download.
- The mic recorder uses browser microphone permission. Use localhost or HTTPS; browsers generally block microphone access on insecure remote HTTP pages.

## Install and run on Windows (VS Code)

Open this project folder in VS Code. In PowerShell or the VS Code terminal, run:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a local URL, usually `http://localhost:8501`. Open it in a browser and allow microphone access when prompted. Alternatively, choose **Upload an audio file**. Supported uploads: WAV, MP3/MPEG, M4A/MP4, OGG, FLAC, and WebM. The default maximum is 25 MB.

### Optional configuration

Set environment variables before launching to customize the model or upload size:

```powershell
$env:WHISPER_MODEL_SIZE = "small"
$env:MAX_AUDIO_SIZE_MB = "40"
streamlit run app.py
```

Supported model sizes depend on Faster-Whisper/Hugging Face availability (for example, `tiny`, `base`, `small`, `medium`, `large-v3`). Larger models take more disk space and CPU time. No credentials are required by this default setup. If you replace the translation provider with a credentialed service, read its key from environment variables or `.streamlit/secrets.toml`; never commit secrets.

## Run tests

Tests mock translation/network and speech-model calls where appropriate; the test suite does not need a model download, credentials, or internet:

```powershell
python -m pytest -q
```

## Troubleshooting

- **Browser microphone denied/not available:** Allow microphone access in the browser site settings and reload. On remote deployments use HTTPS. If access remains unavailable, upload a supported audio file instead.
- **No speech recognized:** Speak clearly, check the selected source language (or use Auto-detect), and ensure the file contains audible speech. Try WAV/MP3/WebM if a container cannot be decoded.
- **Model download/load fails:** Confirm internet access to Hugging Face, disk space, and a compatible Python package install. The default CPU model can take a while on first run. Retry after connectivity returns.
- **Audio upload rejected:** Check the file extension and that its contents match it, ensure it is not empty, and keep it below the configured maximum.
- **Translation fails / rate limit:** Confirm internet connectivity and retry later. The default Google web translator is an unofficial integration and may be throttled. The adapter is isolated in `services/translation.py` for swapping providers.
- **No generated audio:** gTTS requires internet and a supported voice. Text translation may still be available if TTS fails; the app reports that failure separately.
- **Windows dependency installation issues:** Upgrade pip, use Python 3.11 64-bit, recreate the virtual environment, and reinstall from `requirements.txt`.

## Privacy and limitations

Audio bytes stay in the running app's session while needed and are sent to the local recognition engine after temporary storage; the app removes the temporary file. No audio or history is written to a permanent database. Session state may be held in server memory until the Streamlit session expires. Translation text is sent to Google's translation service, and translated text is sent to gTTS when audio is requested. Avoid submitting sensitive personal information. Deployments should use HTTPS and review provider privacy terms.

This is an educational demonstration, not a certified interpreter. Translation quality, accents/noise recognition, provider availability, browser support, and voice coverage vary. Translation, recognition and speech output are sequential, not real-time. A future version could add a self-hosted translation backend, offline TTS, persistent opt-in history, GPU support, or deployment-specific authentication.
