from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class GoogleSearchConfig(BaseSettings):
    """
    Configuration for Google Search API.
    """

    GOOGLE_API_KEY: str
    GOOGLE_CX: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class OpenAIConfig(BaseSettings):
    """
    Configuration for OpenAI API.
    """

    GOOGLE_API_KEY: str
    MODEL: str
    PROMPT: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
