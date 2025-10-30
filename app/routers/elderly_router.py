"""高齢者管理ルーター（UI層）"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List

from app.interfaces.services import ElderlyServiceInterface, SummaryServiceInterface
from app.schemas.models import ElderlyPerson, DailySummary, RawConversation, DashboardData
from app.schemas.responses import ConversationListResponse, ErrorResponse
from app.core.exceptions import NotFoundException, ValidationException
from app.core.dependencies import get_elderly_service, get_summary_service

router = APIRouter(prefix="/elderly", tags=["elderly"])


# 依存性注入をインポート
from app.core.dependencies import get_elderly_service, get_summary_service


@router.get("/{person_id}", response_model=ElderlyPerson)
async def get_elderly_person(
    person_id: int,
    elderly_service: ElderlyServiceInterface = Depends(get_elderly_service)
) -> ElderlyPerson:
    """高齢者の基本情報を取得"""
    try:
        person = await elderly_service.get_elderly_person(person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Elderly person not found")
        return person
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{person_id}/conversations", response_model=ConversationListResponse)
async def get_conversations(
    person_id: int,
    date: str = Query(..., description="日付 (YYYY-MM-DD形式)"),
    elderly_service: ElderlyServiceInterface = Depends(get_elderly_service)
) -> ConversationListResponse:
    """指定日の会話データを取得"""
    try:
        conversations = await elderly_service.get_conversations(person_id, date)
        return ConversationListResponse(
            conversations=conversations,
            total_count=len(conversations)
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{person_id}/summaries", response_model=DailySummary)
async def get_daily_summary(
    person_id: int,
    date: str = Query(..., description="日付 (YYYY-MM-DD形式)"),
    summary_service: SummaryServiceInterface = Depends(get_summary_service)
) -> DailySummary:
    """指定日の日次サマリーを取得"""
    try:
        summary = await summary_service.get_daily_summary(person_id, date)
        if not summary:
            raise HTTPException(status_code=404, detail="Daily summary not found")
        return summary
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{person_id}/summaries", response_model=DailySummary)
async def generate_daily_summary(
    person_id: int,
    date: str = Query(None, description="日付 (YYYY-MM-DD形式)。未指定の場合は今日"),
    overwrite: bool = Query(False, description="既存サマリーを上書きするかどうか"),
    summary_service: SummaryServiceInterface = Depends(get_summary_service)
) -> DailySummary:
    """日次サマリーを自動生成"""
    try:
        from datetime import date as date_module
        target_date = date or date_module.today().isoformat()
        
        summary = await summary_service.generate_daily_summary(
            person_id=person_id,
            target_date=target_date,
            overwrite=overwrite
        )
        return summary
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{person_id}/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    person_id: int,
    date: str = Query(..., description="日付 (YYYY-MM-DD形式)"),
    elderly_service: ElderlyServiceInterface = Depends(get_elderly_service)
) -> DashboardData:
    """ダッシュボード用の統合データを取得"""
    try:
        dashboard_data = await elderly_service.get_dashboard_data(person_id, date)
        return dashboard_data
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))