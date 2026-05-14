import os
from dotenv import load_dotenv
from pydantic import BaseSettings, Field

load_dotenv()

class Settings(BaseSettings):
    # Anthropic Claude
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    claude_model: str = "claude-3-5-sonnet-20241022"

    # Google Cloud
    google_credentials_path: str = Field(default="", env="GOOGLE_CREDENTIALS_PATH")
    google_stt_language: str = "en-US"

    # ElevenLabs TTS (optional)
    elevenlabs_api_key: str = Field(default="", env="ELEVENLABS_API_KEY")
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice

    # Picovoice Porcupine
    porcupine_access_key: str = Field(default="", env="PORCUPINE_ACCESS_KEY")
    wake_word: str = "jarvis"

    # User
    user_name: str = "Chandan"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Audio
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
