"""レスポンススキーマ定義"""

from pydantic import BaseModel, Field
from typing import List, Optional

from .models import RawConversation


class ConversationListResponse(BaseModel):
    """会話履歴リストレスポンス"""
    conversations: List[RawConversation]
    total_count: int


class ErrorResponse(BaseModel):
    """エラーレスポンス"""
    error: str = Field(..., description="エラーメッセージ")
    detail: Optional[str] = Field(None, description="詳細情報")
    error_code: Optional[str] = Field(None, description="エラーコード")