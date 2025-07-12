import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        # 既存のOpenAI APIキーの読み込み
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Supabaseの設定を追加
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        # 必須の環境変数が設定されているかチェック
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in .env file")
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and/or SUPABASE_KEY not set in .env file")
        
        # 既存のその他の設定
        self.voicevox_url = "http://localhost:50021"
        self.speaker_id = 81
        self.max_tokens = 150
        self.transcribe_model = "gpt-4o-mini-transcribe"
        self.chat_model = "gpt-4o-mini"
        self.language = "ja"
        self.host = os.getenv("SERVER_HOST", "0.0.0.0")
        self.port = int(os.getenv("SERVER_PORT", "8000"))

settings = Settings()
