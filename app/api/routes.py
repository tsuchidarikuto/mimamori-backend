from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from fastapi.responses import Response
from datetime import datetime, date
from services import AIService, VoiceService, DatabaseService
from models.schemas import (
    HealthResponse, ElderlyPerson, DailySummary, RawConversation, DashboardData
)
from api.dependencies import get_ai_service, get_voice_service, get_database_service

router = APIRouter()

# 共通ヘルパー関数
async def save_conversation_pair(db_service: DatabaseService, elderly_person_id: int, user_text: str, response_text: str):
    """ユーザーとロボットの会話ペアを保存"""
    timestamp = datetime.now().isoformat()
    
    conversations = [
        RawConversation(id=0, elderly_person_id=elderly_person_id, timestamp=timestamp, speaker="user", content=user_text),
        RawConversation(id=0, elderly_person_id=elderly_person_id, timestamp=timestamp, speaker="robot", content=response_text)
    ]
    
    for conv in conversations:
        await db_service.save_conversation(conv)

async def handle_summary_generation(
    person_id: int, target_date: str, overwrite: bool, 
    db_service: DatabaseService, ai_service: AIService
) -> DailySummary:
    """サマリー生成の共通処理"""
    existing_summary = await db_service.get_daily_summary(person_id, target_date)
    if existing_summary and not overwrite:
        raise HTTPException(
            status_code=400, 
            detail="Summary already exists. Set overwrite=true to regenerate."
        )
    elif existing_summary:
        await db_service.delete_daily_summary(person_id, target_date)
    
    generated_summary = await ai_service.generate_daily_summary(person_id, target_date, db_service)
    if not generated_summary:
        raise HTTPException(status_code=404, detail="No conversations found for the specified date")
    
    return generated_summary

@router.post("/process_audio")
async def process_audio(
    audio: UploadFile = File(...),
    ai_service: AIService = Depends(get_ai_service),
    voice_service: VoiceService = Depends(get_voice_service),
    db_service: DatabaseService = Depends(get_database_service)
):
    """音声を処理して応答音声を返す"""
    user_text = await ai_service.transcribe_audio(audio)
    if not user_text:
        raise HTTPException(status_code=400, detail="Could not transcribe audio")
    
    response_text = await ai_service.generate_response(user_text)
    if not response_text:
        raise HTTPException(status_code=500, detail="Could not generate response")
    
    # 会話を保存（TODO: elderly_person_idは認証から取得）
    await save_conversation_pair(db_service, 1, user_text, response_text)
    
    audio_data = await voice_service.text_to_speech(response_text)
    if not audio_data:
        raise HTTPException(status_code=500, detail="Could not synthesize speech")
    
    return Response(content=audio_data, media_type="audio/wav")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", message="Voice Assistant API is running")

# みまもりダッシュボード用のエンドポイント

@router.get("/elderly-persons", response_model=ElderlyPerson)
async def get_elderly_person(
    person_id: int = Query(..., description="高齢者のID"),
    db_service: DatabaseService = Depends(get_database_service)
):
    """高齢者の基本情報を取得"""
    person = await db_service.get_elderly_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Elderly person not found")
    return person

@router.get("/daily-summaries", response_model=DailySummary)
async def get_daily_summary(
    person_id: int = Query(..., description="高齢者のID"),
    date: str = Query(..., description="日付 (YYYY-MM-DD形式)"),
    db_service: DatabaseService = Depends(get_database_service)
):
    """指定日の日次サマリーを取得"""
    summary = await db_service.get_daily_summary(person_id, date)
    if not summary:
        raise HTTPException(status_code=404, detail="Daily summary not found")
    return summary

@router.get("/conversations", response_model=list[RawConversation])
async def get_conversations(
    person_id: int = Query(..., description="高齢者のID"),
    date: str = Query(..., description="日付 (YYYY-MM-DD形式)"),
    db_service: DatabaseService = Depends(get_database_service)
):
    """指定日の会話データを取得"""
    conversations = await db_service.get_conversations(person_id, date)
    return conversations

@router.get("/dashboard-data", response_model=DashboardData)
async def get_dashboard_data(
    person_id: int = Query(..., description="高齢者のID"),
    date: str = Query(..., description="日付 (YYYY-MM-DD形式)"),
    db_service: DatabaseService = Depends(get_database_service)
):
    """ダッシュボード用の統合データを取得"""
    person = await db_service.get_elderly_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Elderly person not found")
    
    summary = await db_service.get_daily_summary(person_id, date)
    conversations = await db_service.get_conversations(person_id, date)
    
    return DashboardData(
        elderlyPerson=person,
        dailySummary=summary,
        conversations=conversations
    )


@router.post("/generate-daily-summary", response_model=DailySummary)
async def generate_daily_summary(
    person_id: int = Query(..., description="高齢者のID"),
    date_param: str = Query(None, alias="date", description="日付 (YYYY-MM-DD形式)。未指定の場合は今日"),
    overwrite: bool = Query(False, description="既存サマリーを上書きするかどうか"),
    db_service: DatabaseService = Depends(get_database_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """指定日（または今日）の会話データから日次サマリーを自動生成"""
    target_date = date_param or date.today().isoformat()
    return await handle_summary_generation(person_id, target_date, overwrite, db_service, ai_service)