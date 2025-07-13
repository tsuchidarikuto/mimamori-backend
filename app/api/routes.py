from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from fastapi.responses import Response
from services import AIService, VoiceService
from services.database_service import DatabaseService, get_database_service
from models import HealthResponse, ElderlyPerson, DailySummary, RawConversation, DashboardData, EmotionalDataPoint
from api.dependencies import get_ai_service, get_voice_service
from typing import List
from datetime import datetime

router = APIRouter()

@router.post("/process_audio")
async def process_audio(
    audio: UploadFile = File(...),
    ai_service: AIService = Depends(get_ai_service),
    voice_service: VoiceService = Depends(get_voice_service)
):
    try:
        user_text = await ai_service.transcribe_audio(audio)
        if not user_text:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
        print(f"User: {user_text}")
        
        response_text = await ai_service.generate_response(user_text)
        if not response_text:
            raise HTTPException(status_code=500, detail="Could not generate response")
        
        print(f"Assistant: {response_text}")
        
        audio_data = await voice_service.text_to_speech(response_text)
        if not audio_data:
            raise HTTPException(status_code=500, detail="Could not synthesize speech")
        
        return Response(content=audio_data, media_type="audio/wav")
    
    except Exception as e:
        print(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", message="Voice Assistant API is running")

# みまもりダッシュボード用API

@router.get("/elderly-persons", response_model=ElderlyPerson)
async def get_elderly_person(
    person_id: int = Query(...),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    高齢者の基本情報を取得
    """
    person = await db_service.get_elderly_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Elderly person not found")
    return person

@router.get("/daily-summaries", response_model=DailySummary)
async def get_daily_summary(
    person_id: int = Query(...), 
    date: str = Query(...),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    指定日の日次サマリーを取得
    """
    summary = await db_service.get_daily_summary(person_id, date)
    if not summary:
        raise HTTPException(status_code=404, detail="Daily summary not found")
    return summary

@router.get("/conversations", response_model=List[RawConversation])
async def get_conversations(
    person_id: int = Query(...), 
    date: str = Query(...),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    指定日の会話データを取得
    """
    conversations = await db_service.get_conversations(person_id, date)
    return conversations

@router.get("/dashboard-data", response_model=DashboardData)
async def get_dashboard_data(
    person_id: int = Query(...), 
    date: str = Query(...),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    ダッシュボード用の統合データを取得
    """
    # 並行してデータを取得
    elderly_person = await db_service.get_elderly_person(person_id)
    daily_summary = await db_service.get_daily_summary(person_id, date)
    conversations = await db_service.get_conversations(person_id, date)
    
    if not elderly_person:
        raise HTTPException(status_code=404, detail="Elderly person not found")
    
    if not daily_summary:
        raise HTTPException(status_code=404, detail="Daily summary not found")
    
    return DashboardData(
        elderlyPerson=elderly_person,
        dailySummary=daily_summary,
        conversations=conversations
    )
