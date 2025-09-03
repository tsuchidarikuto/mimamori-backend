"""ヘルスチェックルーター（UI層）"""

from fastapi import APIRouter
from app.schemas.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """サービスのヘルスチェック"""
    return HealthResponse(
        status="ok",
        message="Voice Assistant & Monitoring API is running"
    )