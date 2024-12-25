import os
import yaml
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import ClassVar

load_dotenv()  # Load environment variables from .env file


class Settings(BaseSettings):
    APP_NAME: str = "clinic-agent"

    # Langchain secrets
    LANGCHAIN_TRACING_V2: str = os.getenv('LANGCHAIN_TRACING_V2')
    os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')
    os.environ['LANGCHAIN_ENDPOINT'] = os.getenv('LANGCHAIN_ENDPOINT')

    # OpenAI secrets
    # os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

    MONGODB_CONNECTION_STRING: str = os.getenv('MONGODB_CONNECTION_STRING')
    DB_NAME: str = os.getenv('DB_NAME')
    PATIENTS_COL_NAME: str = os.getenv('PATIENTS_COL_NAME')
    DOCTORS_COL_NAME: str = os.getenv('DOCTORS_COL_NAME')
    APPOINTMENTS_COL_NAME: str = os.getenv('APPOINTMENTS_COL_NAME')

    DEEPGRAM_API_KEY: str = os.getenv('DEEPGRAM_API_KEY')
    GROQ_API_KEY: str = os.getenv('GROQ_API_KEY')

    # Configuration from YAML file
    CONFIG: ClassVar[dict]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open("app/config.yml", 'r') as f:
            self.__class__.CONFIG = yaml.safe_load(f)


settings = Settings()
