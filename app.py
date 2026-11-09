
import streamlit as st
import whisper
import hashlib
import tempfile
import os
import subprocess

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
# 3. SPEECH-TO-TEXT USING WHISPER
# --------------------------------------------------

def transcribe_audio(audio_file):

    audio_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_audio:

            temp_audio.write(audio_file.getvalue())
            audio_path = temp_audio.name

        model = load_whisper_model()

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

        return question

    finally:

        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


# --------------------------------------------------
# 4. TEXT-TO-SPEECH USING ESPEAK
# --------------------------------------------------

def generate_speech(text):

    audio_path = None

    try:

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_audio:

            audio_path = temp_audio.name

        result = subprocess.run(
            [
                "espeak",
                "-s", "160",
                "-a", "100",
                "-w", audio_path,
                text
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:

            raise RuntimeError(
                result.stderr or
                "eSpeak speech generation failed."
            )

        if not os.path.exists(audio_path):
            raise RuntimeError("Audio file was not created.")

        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        if not audio_bytes:
            raise RuntimeError("Generated audio is empty.")

        return audio_bytes

    finally:

        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


# --------------------------------------------------
# 5. SESSION STATE INITIALIZATION
# --------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "api_history" not in st.session_state:
    st.session_state.api_history = []

if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None


# --------------------------------------------------
# 6. SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("⚙️ Chat Settings")

    st.write(
        "Department FAQ Voice Chatbot"
    )

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.history = []
        st.session_state.api_history = []
        st.session_state.last_audio_hash = None

        st.rerun()


# --------------------------------------------------
# 7. MAIN APPLICATION
# --------------------------------------------------

st.title("🎓 Department FAQ Voice Chatbot")

st.write(
    "Welcome! Ask questions about academics, placements, "
    "internships, events and department facilities."
)

st.caption(
    "You can ask questions using text or voice."
)

st.divider()


# --------------------------------------------------
# 8. DISPLAY CHAT HISTORY
# --------------------------------------------------

for message in st.session_state.history:

    with st.chat_message(message["role"]):
        st.markdown(message["text"])


# --------------------------------------------------
# 9. TEXT INPUT
# --------------------------------------------------

user_question = st.chat_input(
    "Ask your department-related question..."
)


# --------------------------------------------------
# 10. VOICE INPUT
# --------------------------------------------------

st.subheader("🎤 Ask using your voice")

st.write(
    "Click the microphone, speak your question "
    "and stop recording."
)

audio_file = st.audio_input(
    "Record your question"
)


# --------------------------------------------------
# 11. PROCESS USER QUESTION
# --------------------------------------------------

question = None

# Text input takes priority
if user_question:

    question = user_question.strip()

# Otherwise, process voice input
elif audio_file is not None:

    audio_bytes = audio_file.getvalue()

    current_audio_hash = hashlib.sha256(
        audio_bytes
    ).hexdigest()

    # Avoid processing the same recording again
    if current_audio_hash != st.session_state.last_audio_hash:

        st.session_state.last_audio_hash = current_audio_hash

        try:

            with st.spinner("🎧 Transcribing your voice..."):

                question = transcribe_audio(audio_file)

            if question:

                st.success("Voice transcription completed!")

                st.write("**You said:**", question)

            else:

                st.warning(
                    "No speech detected. Please try recording again."
                )

        except Exception as error:

            st.error("Voice transcription failed.")

            st.code(repr(error))


# --------------------------------------------------
# 12. GET CHATBOT RESPONSE
# --------------------------------------------------

if question:

    # Display user message
    st.session_state.history.append(
        {
            "role": "user",
            "text": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    try:

        with st.spinner("🤖 Generating response..."):

            answer, updated_api_history = get_bot_response(
                question,
                st.session_state.api_history
            )

            st.session_state.api_history = updated_api_history

        # Save chatbot response
        st.session_state.history.append(
            {
                "role": "assistant",
                "text": answer
            }
        )

        with st.chat_message("assistant"):

            st.markdown(answer)

            # Generate speech for the response
            try:

                with st.spinner("🔊 Generating voice response..."):

                    audio_bytes = generate_speech(answer)

                st.audio(
                    audio_bytes,
                    format="audio/wav"
                )

            except Exception as error:

                st.warning(
                    "Text response is available, "
                    "but voice generation is temporarily unavailable."
                )

                st.code(repr(error))

    except Exception as error:

        st.error(
            "Something went wrong while generating the chatbot response."
        )

        st.code(repr(error))

    st.rerun()


# --------------------------------------------------
# 13. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Department FAQ Voice Chatbot | "
    "Powered by Gemini, Whisper and Sentence-BERT"
)

st.caption(
    "Demonstration FAQ dataset – verify official information "
    "with the department."
)

st.caption(
    "Please avoid entering personal or confidential information."
)
