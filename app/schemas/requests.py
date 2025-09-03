"""リクエストスキーマ定義"""

from pydantic import BaseModel, Field
from typing import Optional


class GenerateSummaryRequest(BaseModel):
    """サマリー生成リクエスト"""
    person_id: int = Field(..., description="高齢者のID")
    date: Optional[str] = Field(None, description="日付 (YYYY-MM-DD形式)")
    overwrite: bool = Field(False, description="既存サマリーを上書きするか")


class ProcessAudioRequest(BaseModel):
    """音声処理リクエスト"""
    elderly_person_id: Optional[int] = Field(1, description="高齢者のID")