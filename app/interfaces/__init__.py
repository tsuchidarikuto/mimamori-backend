"""インターフェース定義モジュール"""

from .repositories import (
    DatabaseRepositoryInterface,
    OpenAIRepositoryInterface,
    VoiceRepositoryInterface
)

from .services import (
    ConversationServiceInterface,
    ElderlyServiceInterface,
    SummaryServiceInterface
)

__all__ = [
    # Repository interfaces
    "DatabaseRepositoryInterface",
    "OpenAIRepositoryInterface", 
    "VoiceRepositoryInterface",
    # Service interfaces
    "ConversationServiceInterface",
    "ElderlyServiceInterface",
    "SummaryServiceInterface"
]