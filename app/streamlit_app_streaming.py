import asyncio
import base64

import streamlit as st
from agent.chatbot import generate_response
from components.chat_display import display_chat_history
from components.controls import display_controls
from components.custom_css import apply_custom_css
from components.sidebar import display_sidebar_settings
from core.config import settings
from langchain.schema import AIMessage, HumanMessage
from services.stt import TranscriberFactory
from services.tts import text_to_speech_aws
from utils.logger import get_logger

logger = get_logger()  # Initialize logger with config

# -------------------------------------------------------------------
# 1. Initialize session state
# -------------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "transcription_started" not in st.session_state:
    st.session_state.transcription_started = False

if "current_partial" not in st.session_state:
    st.session_state.current_partial = ""

if "last_speech_time" not in st.session_state:
    st.session_state.last_speech_time = None

if "clear_chat" not in st.session_state:
    st.session_state.clear_chat = False

# (New) We'll store whether debug mode is on/off in session state.
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

# -------------------------------------------------------------------
# 2. Apply custom CSS
# -------------------------------------------------------------------
apply_custom_css()

# -------------------------------------------------------------------
# 3. Title
# -------------------------------------------------------------------
st.markdown(
    '<div class="title">🎙️ FM-Clinic Voice Assistant</div>',
    unsafe_allow_html=True
)

# -------------------------------------------------------------------
# 4. Left Sidebar: Language + Debug Toggle
# -------------------------------------------------------------------
language_option = display_sidebar_settings()

if st.session_state.clear_chat:
    st.session_state.chat_history = []
    st.session_state.clear_chat = False

# -------------------------------------------------------------------
# 5. Create Two Columns in the Main Area
#    col_main = for chat
#    col_debug = for debug info
# -------------------------------------------------------------------
col_main, col_debug = st.columns([4, 1])  # Adjust ratio as desired (3,1 or 4,1, etc.)

# Create a SINGLE placeholder for debug info in the right column
debug_placeholder = col_debug.empty()

# Create a container in the main column for our chat
with col_main:
    # Display the existing chat history
    chat_container = st.container()
    partial_placeholder = chat_container.empty()
    display_chat_history(st.session_state.chat_history, chat_container)

    # Control Buttons
    button_container = st.container()
    start_button, stop_button = display_controls(button_container)

# Create a container in the right column for debug info
debug_container = col_debug.container()

# -------------------------------------------------------------------
# 6. Utility to show debug info
# -------------------------------------------------------------------
def display_debug_info(langchain_history, intermediate_steps):
    """
    Display debug info in the right column if debug mode is enabled.
    Overwrites any existing debug content each time it's called.
    """
    # 1) Clear everything in that placeholder
    debug_placeholder.empty()

    if not st.session_state.debug_mode:
        return  # Do nothing if debug mode is off

    # 3) Write fresh info into that same placeholder
    with debug_placeholder.container():
        st.markdown("## Debug Info")
        st.markdown("**Chat History Used by the Assistant**")
        for msg in langchain_history:
            if isinstance(msg, HumanMessage):
                st.markdown(
                    f'<div class="user"><b>You (history):</b> {msg.content}</div>',
                    unsafe_allow_html=True
                )
            elif isinstance(msg, AIMessage):
                st.markdown(
                    f'<div class="assistant"><b>Assistant (history):</b> {msg.content}</div>',
                    unsafe_allow_html=True
                )

        st.markdown("---")
        st.markdown("**Tools Used by the Assistant**")
        if intermediate_steps:
            for tool_name, tool_input in intermediate_steps:
                st.markdown(
                    f'<div class="assistant">🛠️ Tool: <b>{tool_name}</b> | Input: {tool_input}</div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown("_No tools were used._")

# -------------------------------------------------------------------
# 7. Callbacks for partial/final transcripts
# -------------------------------------------------------------------
def on_partial_transcript(partial_text: str):
    st.session_state.current_partial = partial_text
    partial_placeholder.markdown(
        f'<div class="user"><b>🧑‍💻 Speaking:</b> {partial_text}</div>',
        unsafe_allow_html=True
    )
    st.session_state.last_speech_time = asyncio.get_event_loop().time()
    logger.debug(f"Partial transcript received: {partial_text}")

def on_final_transcript(final_text: str):
    partial_placeholder.empty()
    st.session_state.current_partial = ""
    st.session_state.chat_history.append({"role": "user", "content": final_text})

    # Show final user message
    with col_main:
        st.markdown(
            f'<div class="user"><b>🧑‍💻 You:</b> {final_text}</div>',
            unsafe_allow_html=True
        )

    # Build truncated conversation for LLM
    langchain_history = []
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            langchain_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_history.append(AIMessage(content=msg["content"]))

    # Keep only last N turns
    llm_provider = settings.CONFIG["llm"]["llm_provider"]

    num_history_turns_to_keep = settings.CONFIG["llm"][llm_provider]["num_history_turns"]
    langchain_history = langchain_history[-num_history_turns_to_keep * 2:]

    # Generate assistant response
    try:
        bot_response, intermediate_steps = generate_response(langchain_history)
    except Exception as e:
        with col_main:
            st.markdown(
                '<div class="error">❌ Failed to generate a response. Please try again.</div>',
                unsafe_allow_html=True
            )
        logger.error(f"Failed to generate response: {e}")
        return

    if not bot_response:
        with col_main:
            st.markdown(
                '<div class="error">❌ Failed to generate a response. Please try again.</div>',
                unsafe_allow_html=True
            )
        logger.error("No response generated by the chatbot.")
        return

    st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

    # Display assistant response
    with col_main:
        st.markdown(
            f'<div class="assistant"><b>🤖 Assistant:</b> {bot_response}</div>',
            unsafe_allow_html=True
        )

    # Show debug info in the right column
    display_debug_info(langchain_history, intermediate_steps)

    # Text-to-Speech
    audio_bytes = text_to_speech_aws(bot_response, language=language_option)
    if audio_bytes:
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """
        with col_main:
            st.markdown(audio_html, unsafe_allow_html=True)

    logger.info("Assistant response displayed and TTS audio generated.")

# -------------------------------------------------------------------
# 8. Start & Stop Listening Logic
# -------------------------------------------------------------------
if start_button and not st.session_state.transcription_started:
    st.session_state.transcription_started = True
    with col_main:
        with st.spinner("🎙️ Listening... Speak now!"):
            st.session_state.transcriber = TranscriberFactory.get_transcriber(language=language_option)
            asyncio.run(
                st.session_state.transcriber.transcribe_stream(
                    on_partial=on_partial_transcript,
                    on_final=on_final_transcript
                )
            )
    logger.info("Transcription started.")

if stop_button and st.session_state.transcription_started:
    if "transcriber" in st.session_state and st.session_state.transcriber:
        st.session_state.transcriber.stop_transcription()
        st.session_state.transcription_started = False
        st.session_state.transcriber = None
        with col_main:
            st.success("🛑 Listening stopped.")
        logger.info("Transcription stopped by user.")
    else:
        with col_main:
            st.error("❌ No active transcription process to stop.")