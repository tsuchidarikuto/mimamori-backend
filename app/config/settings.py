import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.voicevox_url = "http://localhost:50021"
        self.speaker_id = 81
        self.max_tokens = 150
        self.transcribe_model = "gpt-4o-mini-transcribe"
        self.chat_model = "gpt-4o-mini"
        self.language = "ja"
        self.host = os.getenv("SERVER_HOST", "0.0.0.0")
        self.port = int(os.getenv("SERVER_PORT", "8000"))

settings = Settings()
