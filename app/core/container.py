"""依存性注入コンテナ"""

from functools import lru_cache
from typing import Dict, Any

from app.config import settings

# Repository implementations
from app.repositories.database_repository import DatabaseRepository
from app.repositories.openai_repository import OpenAIRepository
from app.repositories.voice_repository import VoiceRepository

# Service implementations
from app.services.conversation_service import ConversationService
from app.services.elderly_service import ElderlyService
from app.services.summary_service import SummaryService

# Interfaces
from app.interfaces.repositories import (
    DatabaseRepositoryInterface,
    OpenAIRepositoryInterface,
    VoiceRepositoryInterface
)
from app.interfaces.services import (
    ConversationServiceInterface,
    ElderlyServiceInterface,
    SummaryServiceInterface
)


class DIContainer:
    """依存性注入コンテナ"""
    
    def __init__(self):
        self._instances: Dict[str, Any] = {}
    
    @lru_cache()
    def get_database_repository(self) -> DatabaseRepositoryInterface:
        """データベースリポジトリのシングルトンインスタンスを取得"""
        if "database_repository" not in self._instances:
            self._instances["database_repository"] = DatabaseRepository(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_key
            )
        return self._instances["database_repository"]
    
    @lru_cache()
    def get_openai_repository(self) -> OpenAIRepositoryInterface:
        """OpenAIリポジトリのシングルトンインスタンスを取得"""
        if "openai_repository" not in self._instances:
            self._instances["openai_repository"] = OpenAIRepository(
                api_key=settings.openai_api_key
            )
        return self._instances["openai_repository"]
    
    @lru_cache()
    def get_voice_repository(self) -> VoiceRepositoryInterface:
        """音声リポジトリのシングルトンインスタンスを取得"""
        if "voice_repository" not in self._instances:
            self._instances["voice_repository"] = VoiceRepository(
                voicevox_url=settings.voicevox_url
            )
        return self._instances["voice_repository"]
    
    @lru_cache()
    def get_conversation_service(self) -> ConversationServiceInterface:
        """会話サービスのシングルトンインスタンスを取得"""
        if "conversation_service" not in self._instances:
            self._instances["conversation_service"] = ConversationService(
                db_repository=self.get_database_repository(),
                openai_repository=self.get_openai_repository(),
                voice_repository=self.get_voice_repository()
            )
        return self._instances["conversation_service"]
    
    @lru_cache()
    def get_elderly_service(self) -> ElderlyServiceInterface:
        """高齢者サービスのシングルトンインスタンスを取得"""
        if "elderly_service" not in self._instances:
            self._instances["elderly_service"] = ElderlyService(
                db_repository=self.get_database_repository()
            )
        return self._instances["elderly_service"]
    
    @lru_cache()
    def get_summary_service(self) -> SummaryServiceInterface:
        """サマリーサービスのシングルトンインスタンスを取得"""
        if "summary_service" not in self._instances:
            self._instances["summary_service"] = SummaryService(
                db_repository=self.get_database_repository(),
                openai_repository=self.get_openai_repository()
            )
        return self._instances["summary_service"]


# グローバルコンテナインスタンス
container = DIContainer()