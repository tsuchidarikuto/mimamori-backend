"""依存性注入のヘルパー関数"""

from app.core.container import container
from app.interfaces.services import (
    ConversationServiceInterface,
    ElderlyServiceInterface,
    SummaryServiceInterface
)


def get_conversation_service() -> ConversationServiceInterface:
    """会話サービスの依存性注入"""
    return container.get_conversation_service()


def get_elderly_service() -> ElderlyServiceInterface:
    """高齢者サービスの依存性注入"""
    return container.get_elderly_service()


def get_summary_service() -> SummaryServiceInterface:
    """サマリーサービスの依存性注入"""
    return container.get_summary_service()