import os
import yaml
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import ClassVar
import streamlit as st

load_dotenv()  # Load environment variables from .env file


class Settings(BaseSettings):
    APP_NAME: str = "clinic-agent"

    # check if there is a .env file
    if os.path.exists('.env'):
        print("Using .env file")
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

    else:
        # read from st.secrets
        LANGCHAIN_TRACING_V2: str = st.secrets['LANGCHAIN_TRACING_V2']
        os.environ['LANGCHAIN_API_KEY'] = st.secrets['LANGCHAIN_API_KEY']
        os.environ['LANGCHAIN_ENDPOINT'] = st.secrets['LANGCHAIN_ENDPOINT']

        # OpenAI secrets
        # os.environ["OPENAI_API_KEY"] = st.secrets['OPENAI_API_KEY']

        MONGODB_CONNECTION_STRING: str = st.secrets['MONGODB_CONNECTION_STRING']
        DB_NAME: str = st.secrets['DB_NAME']
        PATIENTS_COL_NAME: str = st.secrets['PATIENTS_COL_NAME']
        DOCTORS_COL_NAME: str = st.secrets['DOCTORS_COL_NAME']
        APPOINTMENTS_COL_NAME: str = st.secrets['APPOINTMENTS_COL_NAME']

        DEEPGRAM_API_KEY: str = st.secrets['DEEPGRAM_API_KEY']
        GROQ_API_KEY: str = st.secrets['GROQ_API_KEY']

    # Configuration from YAML file
    CONFIG: ClassVar[dict]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open("app/config.yml", 'r') as f:
            self.__class__.CONFIG = yaml.safe_load(f)


settings = Settings()
