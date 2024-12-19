import logging
import streamlit as st
from agent.chatbot import generate_response
from langchain.schema import AIMessage, HumanMessage
from utils.tts import text_to_speech_aws
from utils.stt import TranscriberFactory

logger = logging.getLogger(__name__)

# ---- Custom CSS and Layout ----
st.markdown("""
    <style>
        body {
            background: linear-gradient(to right, #f2f6f8, #e8edf3);
            color: #333;
            font-family: Arial, sans-serif;
        }
        .title {
            background-color: #0f4c81;
            color: white;
            padding: 15px;
            text-align: center;
            border-radius: 10px;
            font-size: 2em;
            margin-bottom: 20px;
        }
        .chat-box {
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            font-size: 1.1em;
        }
        .user {
            background-color: #cce5ff;
        }
        .assistant {
            background-color: #d4edda;
        }
        .error {
            color: red;
            font-weight: bold;
        }
        .sidebar-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        /* Adjusting the spacing for sidebar elements */
        .css-1lcbmhc, .css-9s5bis {
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ---- Title ----
st.markdown('<div class="title">🎙️ Voice Assistant</div>', unsafe_allow_html=True)

# ---- Sidebar Settings ----
st.sidebar.markdown('<div class="sidebar-title">⚙️ Settings</div>', unsafe_allow_html=True)
language_option = st.sidebar.radio("🌍 Choose language:", ["Auto Detect", "English", "Arabic"])
language = "en" if language_option == "English" else "ar" if language_option == "Arabic" else None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'last_audio_bytes' not in st.session_state:
    st.session_state.last_audio_bytes = None

if st.sidebar.button("🗑️ Clear Chat / New Session"):
    st.session_state.chat_history = []
    st.session_state.last_audio_bytes = None
    st.experimental_rerun()

# ---- Display Chat History ----
if st.session_state.chat_history:
    st.markdown("### 🗨️ Conversation")
for message in st.session_state.chat_history:
    role_class = "user" if message["role"] == "user" else "assistant"
    icon = "🧑‍💻" if message["role"] == "user" else "🤖"
    st.markdown(f'<div class="chat-box {role_class}"><b>{icon} {message["role"].capitalize()}:</b> {message["content"]}</div>', unsafe_allow_html=True)

# ---- Audio Recording ----
st.markdown("### 🎤 Record your message:")
audio_data = st.audio_input("Record your message")

# If there's new audio, we handle transcription and response
new_audio_bytes = audio_data.getvalue() if audio_data else None

# Only process if we have audio and it's not the same as previously processed
if audio_data and new_audio_bytes != st.session_state.last_audio_bytes:
    # We have a new audio recording
    transcriber = TranscriberFactory().get_transcriber(model="whisper", language=language)

    # Transcription
    with st.spinner("🔄 Transcribing your message..."):
        transcript = transcriber.transcribe_audio(audio_data, language)
    if not transcript:
        st.markdown('<p class="error">❌ Failed to transcribe your message. Please try again.</p>', unsafe_allow_html=True)
        st.stop()

    # Display User Message
    st.markdown(f'<div class="chat-box user"><b>🧑‍💻 You:</b> {transcript}</div>', unsafe_allow_html=True)

    # Prepare LangChain History
    langchain_history = []
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            langchain_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_history.append(AIMessage(content=msg["content"]))

    langchain_history.append(HumanMessage(content=transcript))

    # Generate Assistant Response
    with st.spinner("🤖 Generating assistant's response..."):
        response, intermediate_steps = generate_response(chat_history=langchain_history)
    if not response:
        st.markdown('<p class="error">❌ Failed to generate a response. Please try again.</p>', unsafe_allow_html=True)
        st.stop()

    # Display Assistant Response
    st.markdown(f'<div class="chat-box assistant"><b>🤖 Assistant:</b> {response}</div>', unsafe_allow_html=True)

    # Update Chat History
    st.session_state.chat_history.append({"role": "user", "content": transcript})
    st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Generate Audio Response
    with st.spinner("🔊 Generating audio response..."):
        audio_file = text_to_speech_aws(response, language)
    if not audio_file:
        st.markdown('<p class="error">❌ Failed to generate an audio response. Please try again.</p>', unsafe_allow_html=True)
        st.stop()

    # Play Audio
    st.audio(audio_file, format="audio/mp3")

    # Update last_audio_bytes to indicate we've processed this audio
    st.session_state.last_audio_bytes = new_audio_bytes
