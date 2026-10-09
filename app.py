"""Streamlit UI for the Speech-Based Language Translator project."""

import streamlit as st
from streamlit_mic_recorder import mic_recorder

from config import (
    APP_NAME,
    AUTO_DETECT,
    LANGUAGES,
    LANGUAGE_BY_CODE,
    MAX_AUDIO_SIZE_MB,
    SUPPORTED_AUDIO_EXTENSIONS,
)
from services.speech_recognition import SpeechRecognitionError, transcribe_audio
from services.text_to_speech import TextToSpeechError, generate_speech
from services.translation import TranslationError, translate_text
from utils.history import history_to_csv, make_history_entry
from utils.validators import AudioValidationError, validate_audio

st.set_page_config(page_title=APP_NAME, page_icon="🌐", layout="wide")
st.markdown(
    """
    <style>
    :root { --blue: #1769aa; --pale: #edf6ff; }
    .stApp { background: linear-gradient(180deg, #f7fbff 0%, #ffffff 42%); }
    .block-container { max-width: 1120px; padding-top: 2rem; }
    .hero { padding: 1.6rem 1.8rem; border-radius: 22px; color: #123d67;
            background: linear-gradient(115deg, #e4f2ff, #f5faff 65%, #e8f5ff);
            border: 1px solid #d7eaff; margin-bottom: 1.2rem; }
    .hero h1 { margin: 0 0 .4rem 0; font-size: clamp(1.8rem, 4vw, 2.65rem); }
    .hero p { margin: 0; color: #42627f; font-size: 1.05rem; }
    div[data-testid="stButton"] > button[kind="primary"] { background: var(--blue); border-color: var(--blue); }
    .hint { color: #52677a; font-size: .92rem; }
    [data-testid="stMetric"] { background: #fff; padding: .8rem; border-radius: 12px; border: 1px solid #e6eef5; }
    @media (max-width: 640px) { .block-container { padding: 1rem .8rem; } .hero { padding: 1.2rem; } }
    </style>
    <section class="hero">
      <h1>🎙️ Speech-Based Language Translator</h1>
      <p>Speak naturally, review the words, translate them, and listen to the result.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "conversation_a" not in st.session_state:
    st.session_state.conversation_a = "English"
if "conversation_b" not in st.session_state:
    st.session_state.conversation_b = "Tamil"


def _audio_input(prefix: str) -> tuple[bytes | None, str | None]:
    input_kind = st.radio(
        "Choose audio input",
        ("Record with microphone", "Upload an audio file"),
        horizontal=True,
        key=f"{prefix}_input_kind",
        label_visibility="collapsed",
    )
    audio_data = None
    filename = None
    if input_kind == "Record with microphone":
        st.caption("Use Start recording, speak, then Stop recording. Your browser will ask for microphone access.")
        try:
            recording = mic_recorder(
                start_prompt="🎙️ Start recording",
                stop_prompt="⏹️ Stop recording",
                just_once=True,
                use_container_width=True,
                key=f"{prefix}_microphone",
            )
        except Exception:
            st.error("Microphone capture could not start. Allow microphone access in your browser, or use audio upload instead.")
            recording = None
        if recording and recording.get("bytes"):
            st.session_state[f"{prefix}_audio"] = recording["bytes"]
            # streamlit-mic-recorder returns WAV-encoded bytes.
            st.session_state[f"{prefix}_filename"] = "microphone-recording.wav"
        audio_data = st.session_state.get(f"{prefix}_audio")
        filename = st.session_state.get(f"{prefix}_filename")
    else:
        extensions = sorted(ext.lstrip(".") for ext in SUPPORTED_AUDIO_EXTENSIONS)
        upload = st.file_uploader(
            "Choose an audio file",
            type=extensions,
            max_upload_size=MAX_AUDIO_SIZE_MB,
            key=f"{prefix}_upload",
            help=f"Maximum size: {MAX_AUDIO_SIZE_MB} MB. Accepted: {', '.join(extensions)}.",
        )
        if upload is not None:
            audio_data = upload.getvalue()
            filename = upload.name
            st.session_state[f"{prefix}_audio"] = audio_data
            st.session_state[f"{prefix}_filename"] = filename
    if audio_data:
        st.audio(audio_data)
    return audio_data, filename


def _language_label(code: str | None, fallback: str = "Auto-detect") -> str:
    if not code:
        return fallback
    return LANGUAGE_BY_CODE.get(code, code)


def _recognize(audio_data: bytes, filename: str, source_code: str):
    validate_audio(audio_data, filename)
    with st.spinner("Listening and converting speech to text… The first run may download the speech model."):
        return transcribe_audio(audio_data, filename, source_code)


def _save_history(source_text: str, translated: str, source_name: str, target_name: str, speaker: str = "You"):
    st.session_state.history.insert(
        0,
        make_history_entry(source_text, translated, source_name, target_name, speaker=speaker),
    )


tab_translate, tab_conversation, tab_history, tab_about = st.tabs(
    ["🌐 Translate", "💬 Conversation", "🕘 History", "ℹ️ About"]
)

with tab_translate:
    st.subheader("Translate speech or text")
    source_col, target_col = st.columns(2)
    with source_col:
        source_name = st.selectbox("Source language", [AUTO_DETECT, *LANGUAGES.keys()], key="main_source")
    with target_col:
        target_name = st.selectbox("Translate into", list(LANGUAGES), index=list(LANGUAGES).index("Tamil"), key="main_target")
    source_code = "auto" if source_name == AUTO_DETECT else LANGUAGES[source_name]

    st.markdown("#### 1. Add speech")
    audio_data, filename = _audio_input("main")
    recognize_col, clear_col = st.columns([1, 4])
    with recognize_col:
        recognize_clicked = st.button("📝 Recognize speech", type="primary", key="main_recognize", use_container_width=True)
    with clear_col:
        if st.button("Clear audio", key="main_clear_audio"):
            st.session_state.pop("main_audio", None)
            st.session_state.pop("main_filename", None)
            st.rerun()
    if recognize_clicked:
        if not audio_data or not filename:
            st.warning("Record or upload audio before starting speech recognition.")
        else:
            try:
                result = _recognize(audio_data, filename, source_code)
                st.session_state.recognized_text = result.text
                st.session_state.recognized_language = result.detected_language
                st.session_state.recognition_probability = result.language_probability
                st.success(f"Speech recognized. Detected language: **{_language_label(result.detected_language)}**.")
            except (AudioValidationError, SpeechRecognitionError) as exc:
                st.error(str(exc))

    st.markdown("#### 2. Review and translate")
    if "recognized_text" not in st.session_state:
        st.session_state.recognized_text = ""
    source_text = st.text_area(
        "Recognized text (editable) — you can also type or paste text here",
        key="recognized_text",
        height=135,
        placeholder="Recognized words will appear here. Edit them before translating if needed.",
    )
    effective_source_code = (
        LANGUAGES.get(st.session_state.get("recognized_language"), source_code)
        if source_name == AUTO_DETECT and st.session_state.get("recognized_language")
        else source_code
    )
    if st.button("✨ Translate and create speech", type="primary", key="main_translate"):
        try:
            with st.spinner("Translating text…"):
                translated = translate_text(source_text, effective_source_code, LANGUAGES[target_name])
            st.session_state.main_translation = translated
            _save_history(
                source_text,
                translated,
                _language_label(st.session_state.get("recognized_language")) if source_name == AUTO_DETECT else source_name,
                target_name,
            )
            try:
                with st.spinner("Generating translated audio…"):
                    st.session_state.main_speech = generate_speech(translated, LANGUAGES[target_name])
                st.session_state.main_speech_error = None
            except TextToSpeechError as exc:
                st.session_state.main_speech = None
                st.session_state.main_speech_error = str(exc)
            st.success("Translation complete.")
        except TranslationError as exc:
            st.error(str(exc))

    if st.session_state.get("main_translation"):
        st.markdown("#### Translation")
        st.text_area("Translated text", value=st.session_state.main_translation, height=115, disabled=True, key="main_translation_display")
        if st.session_state.get("main_speech"):
            st.audio(st.session_state.main_speech, format="audio/mp3")
            st.download_button(
                "⬇️ Download translated audio",
                data=st.session_state.main_speech,
                file_name="translated-speech.mp3",
                mime="audio/mpeg",
                key="main_download_audio",
            )
        elif st.session_state.get("main_speech_error"):
            st.warning(st.session_state.main_speech_error)

with tab_conversation:
    st.subheader("Two-way conversation")
    st.caption("Translate one speaker's turn at a time. This is not simultaneous or real-time interpretation.")
    lang_a_col, swap_col, lang_b_col = st.columns([5, 1, 5], vertical_alignment="bottom")
    with lang_a_col:
        language_a = st.selectbox("Language A", list(LANGUAGES), key="conversation_a")
    with swap_col:
        def _swap_languages():
            st.session_state.conversation_a, st.session_state.conversation_b = (
                st.session_state.conversation_b,
                st.session_state.conversation_a,
            )
        st.button("⇄ Swap", on_click=_swap_languages, key="swap_languages", help="Reverse the selected languages")
    with lang_b_col:
        language_b = st.selectbox("Language B", list(LANGUAGES), key="conversation_b")

    direction = st.radio(
        "Who is speaking?",
        (f"A → B ({language_a} to {language_b})", f"B → A ({language_b} to {language_a})"),
        horizontal=True,
        key="conversation_direction",
    )
    if direction.startswith("A"):
        turn_source_name, turn_target_name, speaker = language_a, language_b, f"Speaker A ({language_a})"
    else:
        turn_source_name, turn_target_name, speaker = language_b, language_a, f"Speaker B ({language_b})"
    st.markdown(f"**Current turn:** {turn_source_name} → {turn_target_name}")
    turn_audio, turn_filename = _audio_input("conversation")
    if st.button("🎧 Recognize and translate this turn", type="primary", key="conversation_process"):
        if not turn_audio or not turn_filename:
            st.warning("Record or upload a speaker turn first.")
        else:
            try:
                with st.spinner("Recognizing speech…"):
                    recognition = _recognize(turn_audio, turn_filename, LANGUAGES[turn_source_name])
                with st.spinner("Translating conversation turn…"):
                    translated = translate_text(
                        recognition.text,
                        LANGUAGES[turn_source_name],
                        LANGUAGES[turn_target_name],
                    )
                _save_history(recognition.text, translated, turn_source_name, turn_target_name, speaker)
                st.session_state.conversation.insert(
                    0,
                    {
                        "speaker": speaker,
                        "source_language": turn_source_name,
                        "target_language": turn_target_name,
                        "source_text": recognition.text,
                        "translated_text": translated,
                        "detected_language": recognition.detected_language,
                    },
                )
                try:
                    st.session_state.conversation_speech = generate_speech(translated, LANGUAGES[turn_target_name])
                    st.session_state.conversation_speech_error = None
                except TextToSpeechError as exc:
                    st.session_state.conversation_speech = None
                    st.session_state.conversation_speech_error = str(exc)
                st.success("Conversation turn translated.")
            except (AudioValidationError, SpeechRecognitionError, TranslationError) as exc:
                st.error(str(exc))
    if st.session_state.get("conversation_speech"):
        st.audio(st.session_state.conversation_speech, format="audio/mp3")
    elif st.session_state.get("conversation_speech_error"):
        st.warning(st.session_state.conversation_speech_error)
    st.markdown("#### Conversation transcript")
    if not st.session_state.conversation:
        st.info("Your translated turns will appear here for this session only.")
    else:
        for turn in reversed(st.session_state.conversation):
            with st.container(border=True):
                st.markdown(f"**{turn['speaker']}** · {turn['source_language']} → {turn['target_language']}")
                st.write(turn["source_text"])
                st.markdown(f"**Translation:** {turn['translated_text']}")
                st.caption(f"Speech language detected: {_language_label(turn['detected_language'])}")

with tab_history:
    st.subheader("Session translation history")
    st.caption("History remains in this browser session and is cleared when the session ends or you clear it.")
    history_col, clear_history_col = st.columns([4, 1])
    with history_col:
        st.metric("Translations this session", len(st.session_state.history))
    with clear_history_col:
        if st.button("🗑️ Clear history", key="clear_history", disabled=not st.session_state.history):
            st.session_state.history.clear()
            st.rerun()
    if st.session_state.history:
        st.download_button(
            "⬇️ Export history as CSV",
            data=history_to_csv(st.session_state.history),
            file_name="translation-history.csv",
            mime="text/csv",
            key="history_csv",
        )
        for item in st.session_state.history:
            with st.container(border=True):
                st.caption(f"{item['timestamp']} · {item['speaker']} · {item['source_language']} → {item['target_language']}")
                st.write(item["source_text"])
                st.markdown(f"**Translation:** {item['translated_text']}")
    else:
        st.info("No translations yet. Completed translations are added here automatically.")

with tab_about:
    st.subheader("About this project")
    st.write(
        "A beginner-friendly speech translation demo using Faster-Whisper for speech recognition, "
        "Google Translate through deep-translator for text translation, and gTTS for translated speech."
    )
    st.markdown(
        """
        **Privacy and connectivity**
        - Microphone capture is provided by a browser component. Grant microphone permission, or upload an audio file.
        - Audio is processed temporarily and is not saved to disk after recognition. It is not added to translation history.
        - Translation requests go to Google's translation web service through `deep-translator`; gTTS also contacts Google's service.
        - The Faster-Whisper model is downloaded on first use and runs locally on CPU afterward. Model size affects download time and speed.
        - The application needs internet access for translation, speech generation, and the first model download. It is not fully offline.
        """
    )
