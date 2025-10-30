import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        # 必須環境変数
        self.openai_api_key = self._get_required_env("OPENAI_API_KEY")
        self.supabase_url = self._get_required_env("SUPABASE_URL")
        self.supabase_key = self._get_required_env("SUPABASE_KEY")
        
        # オプション設定（デフォルト値あり）
        self.voicevox_url = os.getenv("VOICEVOX_URL", "http://localhost:50021")
        self.speaker_id = int(os.getenv("SPEAKER_ID", "3"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "150"))
        self.transcribe_model = os.getenv("TRANSCRIBE_MODEL", "whisper-1")
        self.chat_model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
        self.language = os.getenv("LANGUAGE", "ja")
        self.host = os.getenv("SERVER_HOST", "0.0.0.0")
        self.port = int(os.getenv("SERVER_PORT", "8000"))
    
    def _get_required_env(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"{key} not set in .env file")
        return value

settings = Settings()
