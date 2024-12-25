import re
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from core.config import settings

from utils.logger import get_logger

logger = get_logger()


class AWSTTSService:
    """
    AWSTTSService uses Amazon Polly to convert text to speech.
    """
    def __init__(self):
        """
        Initialize the AWSTTSService with the given region name.
        """
        config = settings.CONFIG["text_to_speech"]["AWS"]
        self.polly = boto3.client("polly", region_name=config["region"])
        self.voice_id_ar = config["voice_id_ar"]
        self.voice_id_en = config["voice_id_en"]
        self.voice_id_other = config["voice_id_other"]
        self.english_code = config["languages"]["english_code"]
        self.arabic_code = config["languages"]["arabic_code"]

    def synthesize_speech(self, text: str, language: str) -> Optional[bytes]:
        """
        Synthesize speech using Amazon Polly.
        
        Args:
            text (str): The text to be converted to speech.
            language (str): The language of the text. 

        Returns:
            bytes|None: The audio data in mp3 format, or None if an error occurs.
        """

        voice_id = self.voice_id_en if language == "English" else self.voice_id_ar if language == "Arabic" else self.voice_id_other

        try:
            response = self.polly.synthesize_speech(
                Text=text,
                OutputFormat="mp3",
                VoiceId=voice_id,
                LanguageCode=self.english_code if language == "English" else self.arabic_code if language == "Arabic" else self.english_code
            )

            # Extract audio stream from the response
            if "AudioStream" in response:
                return response["AudioStream"].read()
            else:
                logger.error("No audio stream in Polly response.")
                return None
        except (BotoCoreError, ClientError) as error:
            logger.error(f"Error in Polly synthesize_speech: {error}")
            return None


# Function used by app.py
def text_to_speech_aws(text: str, language: str) -> Optional[bytes]:
    """
    Convert the given text to speech using the AWSTTSService and return the mp3 bytes.

    Args:
        text (str): Text to convert.
        language (str|None): Language ('English', 'Arabic', or 'Auto Detect").

    Returns:
        bytes|None: MP3 audio bytes or None if error.
    """
    # Check if the text contains any Arabic characters, if so, set the language to Arabic, otherwise, use English
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    if arabic_pattern.search(text):
        language = 'Arabic'
        logger.info("---------------- Arabic text detected -----------------")
    else:
        language = 'English'
        logger.info("---------------- English text detected -----------------")

    tts_service = AWSTTSService()
    return tts_service.synthesize_speech(text, language)