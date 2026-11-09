
import streamlit as st
import whisper
import hashlib
import tempfile
import os
import pyttsx3

from chatbot import get_bot_response


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Department FAQ Voice Chatbot",
    page_icon="🎓",
    layout="centered"
)


# --------------------------------------------------
# 2. LOAD WHISPER MODEL
# --------------------------------------------------

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")


# --------------------------------------------------
# 3. TEXT-TO-SPEECH
# --------------------------------------------------

def generate_speech(text):

    engine = pyttsx3.init()

    engine.setProperty("rate", 160)
    engine.setProperty("volume", 1.0)

    audio_path = None

    try:

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_audio:

            audio_path = temp_audio.name

        engine.save_to_file(text, audio_path)
        engine.runAndWait()

        if not os.path.exists(audio_path):
            raise RuntimeError("Audio file was not generated.")

        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        if not audio_bytes:
            raise RuntimeError("Generated audio file is empty.")

        return audio_bytes

    finally:

        engine.stop()

        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


# --------------------------------------------------
# 4. INITIALIZE SESSION STATE
# --------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "api_history" not in st.session_state:
    st.session_state.api_history = []

if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None

if "voice_recorder_version" not in st.session_state:
    st.session_state.voice_recorder_version = 0


# --------------------------------------------------
# 5. SIDEBAR SETTINGS
# --------------------------------------------------

st.sidebar.title("Chat Settings")

if st.sidebar.button(
    "🗑️ Clear Chat",
    use_container_width=True
):

    st.session_state.history = []
    st.session_state.api_history = []
    st.session_state.last_audio_hash = None

    st.session_state.voice_recorder_version += 1

    st.rerun()

st.sidebar.caption(
    "Clear Chat starts a new conversation."
)


# --------------------------------------------------
# 6. APPLICATION HEADER
# --------------------------------------------------

st.title("🎓 Department FAQ Voice Chatbot")

st.write(
    "Welcome! Ask questions about academics, placements, "
    "internships, events and department facilities."
)

st.info(
    "Demonstration FAQ dataset – verify official information "
    "with the department."
)

st.caption(
    "Please avoid entering personal or confidential information."
)


# --------------------------------------------------
# 7. DISPLAY CHAT HISTORY
# --------------------------------------------------

for message in st.session_state.history:

    with st.chat_message(message["role"]):
        st.markdown(message["text"])


# --------------------------------------------------
# 8. VOICE INPUT - STREAMLIT NATIVE RECORDER
# --------------------------------------------------

st.divider()

st.subheader("🎤 Ask using your voice")

st.write(
    "Click the record button, speak your question and stop recording."
)

audio_value = st.audio_input(
    "Record your question",
    sample_rate=16000,
    key=f"voice_input_{st.session_state.voice_recorder_version}"
)

audio_bytes = (
    audio_value.getvalue()
    if audio_value is not None
    else None
)


# --------------------------------------------------
# 9. TEXT INPUT
# --------------------------------------------------

user_input = st.chat_input(
    "Or type your department-related question..."
)

question = ""


# --------------------------------------------------
# 10. PROCESS TEXT OR VOICE INPUT
# --------------------------------------------------

# Give priority to typed questions.

if user_input:

    question = user_input.strip()

    # Mark existing audio as processed.

    if audio_bytes:

        st.session_state.last_audio_hash = hashlib.sha256(
            audio_bytes
        ).hexdigest()


# Process voice only when no text question is submitted.

elif audio_bytes:

    audio_hash = hashlib.sha256(audio_bytes).hexdigest()

    # Prevent repeated processing of the same recording.

    if audio_hash != st.session_state.last_audio_hash:

        st.session_state.last_audio_hash = audio_hash

        audio_path = None

        try:

            with st.spinner(
                "Loading Whisper and recognizing speech..."
            ):

                model = load_whisper_model()

                # Save audio temporarily.

                with tempfile.NamedTemporaryFile(
                    suffix=".wav",
                    delete=False
                ) as temp_audio:

                    temp_audio.write(audio_bytes)
                    audio_path = temp_audio.name

                # Transcribe English speech.

                result = model.transcribe(
                    audio_path,
                    language="en",
                    fp16=False,
                    task="transcribe",
                    temperature=0,
                    condition_on_previous_text=False,
                    initial_prompt=(
                        "Department FAQ about academics, placements, "
                        "internships, events and facilities."
                    )
                )

                question = result["text"].strip()

            if question:

                st.success(
                    "Speech recognized successfully!"
                )

                st.write("**Transcribed question:**")
                st.info(question)

            else:

                st.warning(
                    "No speech detected. Please record again."
                )

                st.session_state.last_audio_hash = None

        except Exception as error:

            st.error(
                f"Speech recognition error: {error}"
            )

            st.session_state.last_audio_hash = None

        finally:

            # Remove temporary audio.

            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)


# --------------------------------------------------
# 11. GENERATE CHATBOT RESPONSE
# --------------------------------------------------

if question:

    try:

        # Display user question.

        with st.chat_message("user"):
            st.markdown(question)

        # Save user message.

        st.session_state.history.append({
            "role": "user",
            "text": question
        })

        # Generate chatbot answer.

        with st.chat_message("assistant"):

            with st.spinner("Finding an answer..."):

                answer, updated_api_history = get_bot_response(
                    question,
                    st.session_state.api_history
                )

                st.session_state.api_history = updated_api_history

                st.session_state.history.append({
                    "role": "assistant",
                    "text": answer
                })

            # Display text answer.

            st.markdown(answer)

            # Generate voice answer.

            try:

                with st.spinner("Generating voice response..."):

                    audio_response = generate_speech(answer)

                st.audio(
                    audio_response,
                    format="audio/wav"
                )

            except Exception as error:

                st.warning(
                    "Text response is available, but voice generation "
                    "is temporarily unavailable."
                )

                print("TTS Error:", error)

    except Exception as error:

        st.error(
            f"Unable to generate a response. Error: {error}"
        )

        # Remove incomplete user message.

        if (
            st.session_state.history
            and st.session_state.history[-1]["role"] == "user"
        ):

            st.session_state.history.pop()
