"""Service層のインターフェース定義"""

from typing import Protocol, Optional, List
from datetime import date
from fastapi import UploadFile

from app.schemas.models import (
    ElderlyPerson,
    DailySummary,
    RawConversation,
    DashboardData
)


class ConversationServiceInterface(Protocol):
    """会話処理サービスのインターフェース"""
    
    async def process_voice_conversation(
        self, 
        audio_file: UploadFile,
        elderly_person_id: int = 1
    ) -> Optional[bytes]:
        """音声会話を処理して応答音声を返す"""
        ...
    
    async def save_conversation_pair(
        self,
        elderly_person_id: int,
        user_text: str,
        robot_text: str
    ) -> None:
        """会話ペアを保存"""
        ...


class ElderlyServiceInterface(Protocol):
    """高齢者管理サービスのインターフェース"""
    
    async def get_elderly_person(self, person_id: int) -> Optional[ElderlyPerson]:
        """高齢者情報を取得"""
        ...
    
    async def get_conversations(
        self, 
        person_id: int, 
        target_date: str
    ) -> List[RawConversation]:
        """指定日の会話履歴を取得"""
        ...
    
    async def get_dashboard_data(
        self,
        person_id: int,
        target_date: str
    ) -> DashboardData:
        """ダッシュボード用データを取得"""
        ...


class SummaryServiceInterface(Protocol):
    """サマリー生成サービスのインターフェース"""
    
    async def get_daily_summary(
        self,
        person_id: int,
        target_date: str
    ) -> Optional[DailySummary]:
        """日次サマリーを取得"""
        ...
    
    async def generate_daily_summary(
        self,
        person_id: int,
        target_date: str,
        overwrite: bool = False
    ) -> DailySummary:
        """日次サマリーを生成"""
        ...