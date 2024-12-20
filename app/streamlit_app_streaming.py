import os
import asyncio
import logging
import streamlit as st
import sounddevice
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from dotenv import load_dotenv
from langchain.schema import AIMessage, HumanMessage
from agent.chatbot import generate_response
from utils.tts import text_to_speech_aws
import base64  # Import base64 for encoding audio

load_dotenv()
logger = logging.getLogger(__name__)

# ---- Custom CSS for Enhanced UI ----
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

        /* Chat Container */
        .chat-container {
            max-height: 60vh;
            overflow-y: auto;
            padding: 10px;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }

        /* User Message Styling */
        .user {
            background-color: #cce5ff;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            align-self: flex-end;
            max-width: 80%;
        }

        /* Assistant Message Styling */
        .assistant {
            background-color: #d4edda;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            align-self: flex-start;
            max-width: 80%;
        }

        /* Error Message Styling */
        .error {
            color: red;
            font-weight: bold;
        }

        /* Sidebar Title */
        .sidebar-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
        }

        /* Button Styling */
        .stButton > button {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            border: none;
            font-size: 1em;
            cursor: pointer;
        }

        /* Start Listening Button */
        #start-listening {
            background-color: #28a745;
            color: white;
        }

        /* Stop Listening Button */
        #stop-listening {
            background-color: #dc3545;
            color: white;
        }

    </style>
""", unsafe_allow_html=True)

# ---- Title ----
st.markdown('<div class="title">🎙️ Voice Assistant with Real-Time AWS Transcription</div>', unsafe_allow_html=True)

# ---- Sidebar Settings ----
st.sidebar.markdown('<div class="sidebar-title">⚙️ Settings</div>', unsafe_allow_html=True)
language_option = st.sidebar.radio("🌍 Choose language:", ["Auto Detect", "English", "Arabic"])
language = "en" if language_option == "English" else "ar" if language_option == "Arabic" else None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'transcription_started' not in st.session_state:
    st.session_state.transcription_started = False

if 'current_partial' not in st.session_state:
    st.session_state.current_partial = ""

if 'last_speech_time' not in st.session_state:
    st.session_state.last_speech_time = None

if st.sidebar.button("🗑️ Clear Chat / New Session"):
    st.session_state.chat_history = []
    st.session_state.last_audio_bytes = None
    st.rerun()

# ---- Display Chat History ----
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        role_class = "user" if message["role"] == "user" else "assistant"
        st.markdown(
            f'<div class="{role_class}"><b>{"🧑‍💻 You" if message["role"] == "user" else "🤖 Assistant"}:</b> {message["content"]}</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ---- Control Buttons ----
button_container = st.container()
with button_container:
    cols = st.columns(2)
    with cols[0]:
        start_button = st.button("Start Listening", key="start-listening", help="Start real-time transcription and assistant responses")
    with cols[1]:
        stop_button = st.button("Stop Listening", key="stop-listening", help="Stop transcription and assistant responses")

# ---- AWS Transcribe Real-Time Code ----
class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, transcript_result_stream, chat_container):
        super().__init__(transcript_result_stream)
        self.chat_container = chat_container

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        global silence_timer
        results = transcript_event.transcript.results
        for result in results:
            if result.is_partial:
                partial_text = result.alternatives[0].transcript
                st.session_state.current_partial = partial_text
                st.session_state.last_speech_time = asyncio.get_event_loop().time()
            else:
                for alt in result.alternatives:
                    final_text = alt.transcript.strip()
                    if final_text:
                        st.session_state.current_partial = ""
                        st.session_state.chat_history.append({"role": "user", "content": final_text})

                        # Display user message
                        with self.chat_container:
                            st.markdown(
                                f'<div class="user"><b>🧑‍💻 You:</b> {final_text}</div>',
                                unsafe_allow_html=True
                            )

                        # Prepare LangChain History
                        langchain_history = []
                        for msg in st.session_state.chat_history:
                            if msg["role"] == "user":
                                langchain_history.append(HumanMessage(content=msg["content"]))
                            elif msg["role"] == "assistant":
                                langchain_history.append(AIMessage(content=msg["content"]))

                        # Generate Assistant Response
                        bot_response, intermediate_steps = generate_response(langchain_history)
                        if not bot_response:
                            with self.chat_container:
                                st.markdown(
                                    '<div class="error">❌ Failed to generate a response. Please try again.</div>',
                                    unsafe_allow_html=True
                                )
                            continue

                        # Update chat history with assistant response
                        st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

                        # Display Assistant Response
                        with self.chat_container:
                            st.markdown(
                                f'<div class="assistant"><b>🤖 Assistant:</b> {bot_response}</div>',
                                unsafe_allow_html=True
                            )

                        # Generate Audio Response
                        audio_bytes = text_to_speech_aws(bot_response, language)
                        if audio_bytes:
                            # Encode audio to base64
                            audio_base64 = base64.b64encode(audio_bytes).decode()
                            # Embed audio in HTML with autoplay and no controls
                            audio_html = f"""
                            <audio autoplay>
                                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                            </audio>
                            """
                            st.markdown(audio_html, unsafe_allow_html=True)

async def mic_stream(input_queue):
    loop = asyncio.get_event_loop()

    def callback(indata, frame_count, time_info, status):
        loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

    stream = sounddevice.RawInputStream(
        channels=1,
        samplerate=16000,
        callback=callback,
        blocksize=1024 * 2,
        dtype="int16",
    )

    with stream:
        while st.session_state.transcription_started:
            indata, status = await input_queue.get()
            yield indata, status

async def write_chunks(stream, input_queue):
    async for chunk, status in mic_stream(input_queue):
        await stream.input_stream.send_audio_event(audio_chunk=chunk)

async def basic_transcribe(chat_container):
    client = TranscribeStreamingClient(region="us-west-2")
    stream = await client.start_stream_transcription(
        language_code="en-US" if language_option == "English" else "ar-SA",
        media_sample_rate_hz=16000,
        media_encoding="pcm",
    )

    handler = MyEventHandler(stream.output_stream, chat_container)

    try:
        input_queue = asyncio.Queue()
        await asyncio.gather(write_chunks(stream, input_queue), handler.handle_events())
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
    finally:
        st.session_state.transcription_started = False

def run_transcription():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(basic_transcribe(chat_container))
    loop.close()

# ---- Start and Stop Listening Logic ----
if start_button and not st.session_state.transcription_started:
    st.session_state.transcription_started = True
    with st.spinner("🎙️ Listening... Speak now!"):
        run_transcription()

if stop_button and st.session_state.transcription_started:
    st.session_state.transcription_started = False
    st.success("🛑 Listening stopped.")
