import os
import asyncio
import streamlit as st
import sounddevice
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
# load .env file
from dotenv import load_dotenv
load_dotenv()
# Import the chatbot functionality
from agent.chatbot import generate_response

# Global Variables
latest_transcription = ""
transcription_started = False
chat_history = []  # To store conversation history for the chatbot


class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, transcript_result_stream, ui_container, response_container):
        super().__init__(transcript_result_stream)
        self.ui_container = ui_container
        self.response_container = response_container

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        global latest_transcription, chat_history
        results = transcript_event.transcript.results
        for result in results:
            if result.is_partial:
                # Update the transcription dynamically
                partial_text = result.alternatives[0].transcript
                self.ui_container.markdown(f"**You:** {partial_text}")
            else:
                for alt in result.alternatives:
                    # Process finalized transcription
                    final_text = alt.transcript
                    latest_transcription = final_text

                    # Append user input to chat history
                    chat_history.append({"role": "user", "content": final_text})

                    # Generate response using the chatbot
                    bot_response, _ = generate_response(chat_history)

                    # Append bot response to chat history
                    chat_history.append({"role": "assistant", "content": bot_response})

                    # Display both the transcription and the response
                    self.ui_container.markdown(f"**You:** {final_text}")
                    self.response_container.markdown(f"**Bot:** {bot_response}")


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
        while transcription_started:
            indata, status = await input_queue.get()
            yield indata, status


async def write_chunks(stream, input_queue):
    async for chunk, status in mic_stream(input_queue):
        await stream.input_stream.send_audio_event(audio_chunk=chunk)


async def basic_transcribe(input_queue, ui_container, response_container):
    global transcription_started
    client = TranscribeStreamingClient(region="us-west-2")
    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=16000,
        media_encoding="pcm",
    )

    handler = MyEventHandler(stream.output_stream, ui_container, response_container)

    try:
        if transcription_started:
            await asyncio.gather(write_chunks(stream, input_queue), handler.handle_events())
    except Exception as e:
        print("Error:", e)
    finally:
        transcription_started = False


def main():
    global transcription_started
    st.title("Real-Time Chatbot with AWS Transcribe & Groq API")
    st.write("Press 'Start Transcription' to begin chatting.")
    
    start_button = st.button("Start Transcription")
    stop_button = st.button("Stop Transcription")

    # UI containers for transcription and chatbot responses
    transcription_container = st.empty()
    response_container = st.empty()
    
    if start_button and not transcription_started:
        transcription_started = True

    if stop_button:
        transcription_started = False

    if transcription_started:
        st.write("Listening...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        input_queue = asyncio.Queue()

        loop.run_until_complete(basic_transcribe(input_queue, transcription_container, response_container))
        loop.close()

        st.write("Transcription Stopped.")


if __name__ == "__main__":
    main()
