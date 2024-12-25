import asyncio
import io
from time import time
from typing import AsyncGenerator, Callable

import httpx
import librosa
import numpy as np
import sounddevice as sd
import soundfile as sf
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from core.config import settings
from deepgram import (DeepgramClient, DeepgramClientOptions, FileSource,
                      PrerecordedOptions)
from deepgram.utils import verboselogs
from services.whisper_streaming_repo.whisper_online import (FasterWhisperASR,
                                                       VACOnlineASRProcessor)

from utils.logger import get_logger

logger = get_logger()


class DeepgramTranscriber:
    """
    DeepgramTranscriber handles the transcription of prerecorded audio files using Deepgram's API.
    """

    def __init__(self, language: str = None):
        """
        Initialize the DeepgramTranscriber.
        
        Args:
            language: The language code to use for transcription.

        """

        config = settings.CONFIG["speech_to_text"]["prerecorded"]["Deepgram"]
        self.model = config["model"]
        if language == "English":
            self.language_code = config["languages"]["english_code"]
        elif language == "Arabic":
            self.language_code = config["languages"]["arabic_code"]
        else:
            self.language_code = None
        
        self.config: DeepgramClientOptions = DeepgramClientOptions(
            verbose=verboselogs.SPAM,
        )
        self.deepgram: DeepgramClient = DeepgramClient("", self.config)


    # Transcribe audio
    def transcribe_audio(self, audio_bytes: bytes) -> str:
        payload: FileSource = {
            "buffer": audio_bytes,
        }
        options: PrerecordedOptions = PrerecordedOptions(
            model=self.model,
            punctuate=True,
            language=self.language_code,
            detect_language=not bool(self.language_code),
        )
        try:
            response = self.deepgram.listen.rest.v("1").transcribe_file(
                payload, options, timeout=httpx.Timeout(300.0, connect=10.0)
            )
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return ""
        try:
            transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
            logger.info(f"Transcript: {transcript}")
        except:
            transcript = ""
            logger.warning("No transcript found!")
        return transcript


class WhisperStreamingTranscriber:
    """
    Handles streaming audio capture from the microphone and real-time transcription using FasterWhisperASR.
    """

    def __init__(self, language: str = "English"):
        """
        Initialize the WhisperStreamingTranscriber.
        """
        config = settings.CONFIG["speech_to_text"]["streaming"]["FasterWhisperASR"]
        
        # if Auto Detect, set the language code to "English" as a default, as AWS Transcribe requires a language input
        self.language_code = config["languages"].get(f"{language.lower()}_code", None)
        self.model_size = config["model_size"]
        self.sample_rate = config["sample_rate"]
        self.device = config["device"]
        self.transcription_started = False
        self.model_lock = asyncio.Lock()
        self.silence_timeout = config["silence_timeout"]
        self.buffer = []  # For buffering recognized text
        self.last_update_time = None  # Last time a word was added to the buffer

        # Initialize the Whisper ASR model
        self.model = FasterWhisperASR(
            lan=self.language_code,
            modelsize=self.model_size,
        )
        if config.get("use_vad"):
            self.model.use_vad()

    async def transcribe_stream(
        self, on_partial: Callable[[str], None], on_final: Callable[[str], None]
    ) -> None:
        """
        Begin real-time transcription of microphone audio using FasterWhisperASR.

        This function:
          - Captures audio chunks asynchronously from the mic.
          - Processes each chunk with FasterWhisperASR.
          - Buffers the text until a silence timeout or natural sentence break occurs.

        Args:
            on_partial: Callback function for partial transcripts.
            on_final: Callback function for final transcripts.
        """
        self.transcription_started = True

        # Create an ASR processor for this transcription session
        online_asr_processor = VACOnlineASRProcessor(
            online_chunk_size=1,
            asr=self.model,
            tokenizer=None,
            buffer_trimming=("segment", 15),
            logfile=None,
        )

        async for audio_chunk in self._get_audio_chunk_from_stream():
            if not self.transcription_started:
                break
            await self._process_audio_chunk(audio_chunk, online_asr_processor, on_partial)

            # Check for silence timeout
            if self.last_update_time and time() - self.last_update_time > self.silence_timeout:
                await self._finalize_buffer(on_final)

        await self._finalize_buffer(on_final)
        final_text = online_asr_processor.flush().strip()
        if final_text:
            logger.info(f"Finalized sentence: {final_text}")
            on_final(final_text)

    async def _get_audio_chunk_from_stream(self) -> AsyncGenerator[bytes, None]:
        audio_queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def callback(indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags) -> None:
            """
            Callback function for sounddevice stream.
            """
            if status:
                logger.warning(f"Sounddevice status: {status}")
            asyncio.run_coroutine_threadsafe(audio_queue.put(indata.copy()), loop)

        stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=callback,
            blocksize=1024,
            dtype="int16",
        )

        with stream:
            while self.transcription_started:
                yield await audio_queue.get()

    async def _process_audio_chunk(
        self, audio_chunk: bytes, processor: VACOnlineASRProcessor, on_partial: Callable[[str], None]
    ) -> None:
        """
        Process a single audio chunk using FasterWhisperASR.
        Buffers the recognized text until a silence timeout or natural sentence break occurs.

        Args:
            audio_chunk: The audio chunk to process.
            processor: The ASR processor.
            on_partial: Callback function for partial transcripts.
        """
            # Convert raw audio to the format needed for Whisper
        file_like = io.BytesIO(audio_chunk)
        with sf.SoundFile(file_like, channels=1, samplerate=self.sample_rate, format="RAW", subtype="PCM_16") as sfile:
            audio, _ = librosa.load(sfile, sr=self.sample_rate, mono=True, dtype=np.float32)

        async with self.model_lock:
            # Insert chunk, run the ASR
            processor.insert_audio_chunk(audio)
            output = processor.process_iter()

            # output is typically (start_time, end_time, text)
            # e.g.: (0.316, 1.196, "Hello world")
        if output and output[0] is not None and output[2]:
            recognized_text = output[2].strip()
            on_partial(recognized_text)
            self.last_update_time = time()  # Update the time of last recognition
            self.buffer.append(recognized_text)  # Add the text to the buffer

    async def _finalize_buffer(self, on_final: Callable[[str], None]) -> None:
        """
        Finalizes the buffered text and sends it to `on_final`.
        """
        if self.buffer:
            final_sentence = " ".join(self.buffer).strip()
            if final_sentence:
                print(f"[Whisper] Finalized sentence: {final_sentence}")
                on_final(final_sentence)
            self.buffer = []

    def stop_transcription(self):
        """
        Stop the transcription process.
        """
        self.transcription_started = False


class AWSStreamingTranscriber:
    """
    Handles streaming audio capture from the microphone and real-time transcription using AWS Transcribe.
    """

    def __init__(self, language: str) -> None:
        """
        Initialize the AWSStreamingTranscriber.
        """
        config = settings.CONFIG["speech_to_text"]["streaming"]["AWS"]
        self.region = config["region"]
        self.sample_rate = config["sample_rate"]
        self.transcription_started = False
        self.language_code = config["languages"].get(f"{language.lower()}_code", config["languages"]["english_code"])

    async def transcribe_stream(
        self, on_partial: Callable[[str], None], on_final: Callable[[str], None]
    ) -> None:
        """
        Begin transcription of microphone audio using AWS Transcribe Streaming.

        Args:
            on_partial: Callback function for partial transcripts.
            on_final: Callback function for final transcripts.
        """
        self.transcription_started = True

        async def mic_stream(input_queue: asyncio.Queue) -> AsyncGenerator[bytes, None]:
            """
            Stream audio from the microphone.
            
            Args:
                input_queue: The queue to store audio chunks.
                
            Yields:
                bytes: The audio chunk.
            """
            loop = asyncio.get_event_loop()

            def callback(indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags) -> None:
                """
                Callback function for sounddevice stream.
                """
                loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

            stream = sd.RawInputStream(
                channels=1,
                samplerate=self.sample_rate,
                callback=callback,
                blocksize=2048,
                dtype="int16",
            )

            with stream:
                while self.transcription_started:
                    chunk, status = await input_queue.get()
                    yield chunk, status
        async def stream_audio(transcribe_stream: TranscribeStreamingClient, input_queue: asyncio.Queue) -> None:
            """
            Reads mic_stream(...) chunks and sends them to AWS Transcribe.
            """
            async for chunk, status in mic_stream(input_queue):
                # Send each chunk to Transcribe
                await transcribe_stream.input_stream.send_audio_event(audio_chunk=chunk)

            # When done, end the stream
            await transcribe_stream.input_stream.end_stream()
            

        class MyEventHandler(TranscriptResultStreamHandler):
            """
            Handler to process transcript events from Amazon Transcribe.
            """
            def __init__(self, output_stream: io.BytesIO) -> None:
                """
                Initialize the event handler.
                
                Args:
                    output_stream: The output stream to write the transcript to.
                """
                super().__init__(output_stream)

            async def handle_transcript_event(self, transcript_event: TranscriptEvent) -> None:
                """
                Process a transcript event from Amazon Transcribe.

                Args:
                    transcript_event: Transcript event object.
                """
                for result in transcript_event.transcript.results:
                    if result.is_partial:
                        on_partial(result.alternatives[0].transcript.strip())
                    else:
                        final_text = result.alternatives[0].transcript.strip()
                        if final_text:
                            on_final(final_text)

        async def basic_transcribe():
            """
            Orchestrates the AWS streaming transcription process.
            """
            client = TranscribeStreamingClient(region=self.region)
            stream = await client.start_stream_transcription(
                language_code=self.language_code,
                media_sample_rate_hz=self.sample_rate,
                media_encoding="pcm",
            )

            handler = MyEventHandler(stream.output_stream)
            input_queue = asyncio.Queue()

            try:
                # Launch both tasks in parallel:
                # 1) stream_audio -> feeds audio chunks to AWS
                # 2) handler.handle_events -> consumes partial/final transcripts
                await asyncio.gather(
                    stream_audio(stream, input_queue),
                    handler.handle_events(),  # This must be awaited
                )
            except Exception as e:
                logger.error(f"Error during transcription: {e}")
            finally:
                self.transcription_started = False

        await basic_transcribe()


    def stop_transcription(self):
        """
        Stop the transcription process.
        """
        self.transcription_started = False

class TranscriberFactory:
    @staticmethod
    def get_transcriber(language: str = None) -> object:
        """
        Get the appropriate transcriber based on the configuration in the config file.

        Args:
        
        """
        config = settings.CONFIG["speech_to_text"]["transcriber"]
        if config == "WhisperStreaming":
            return WhisperStreamingTranscriber(language=language)
        elif config == "AWSStreaming":
            return AWSStreamingTranscriber(language=language)
        else:
            raise ValueError("Unsupported transcriber type in configuration.")
