"""Repository層のインターフェース定義"""

from typing import Protocol, Optional, List
from datetime import date

from app.schemas.models import (
    ElderlyPerson,
    DailySummary,
    RawConversation
)


class DatabaseRepositoryInterface(Protocol):
    """データベース操作のインターフェース"""
    
    async def get_elderly_person(self, person_id: int) -> Optional[ElderlyPerson]:
        """高齢者情報を取得"""
        ...
    
    async def create_elderly_person(self, person: ElderlyPerson) -> Optional[ElderlyPerson]:
        """高齢者情報を作成"""
        ...
    
    async def get_daily_summary(self, person_id: int, date: str) -> Optional[DailySummary]:
        """日次サマリーを取得"""
        ...
    
    async def save_daily_summary(self, summary: DailySummary) -> Optional[DailySummary]:
        """日次サマリーを保存"""
        ...
    
    async def delete_daily_summary(self, person_id: int, date: str) -> bool:
        """日次サマリーを削除"""
        ...
    
    async def get_conversations(self, person_id: int, date: str) -> List[RawConversation]:
        """会話履歴を取得"""
        ...
    
    async def save_conversation(self, conversation: RawConversation) -> Optional[RawConversation]:
        """会話を保存"""
        ...


class OpenAIRepositoryInterface(Protocol):
    """OpenAI API操作のインターフェース"""
    
    async def transcribe_audio(self, audio_data: bytes, file_extension: str = ".wav") -> Optional[str]:
        """音声をテキストに変換"""
        ...
    
    async def generate_chat_response(
        self, 
        messages: List[dict],
        max_tokens: int = 150
    ) -> Optional[str]:
        """チャット応答を生成"""
        ...
    
    async def generate_structured_response(
        self,
        messages: List[dict],
        response_format: type,
        max_tokens: int = 1000
    ) -> Optional[dict]:
        """構造化された応答を生成"""
        ...


class VoiceRepositoryInterface(Protocol):
    """音声合成APIのインターフェース"""
    
    async def text_to_speech(self, text: str, speaker_id: int = 3) -> Optional[bytes]:
        """テキストを音声に変換"""
        ...