from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from fastapi.responses import Response
from datetime import datetime
from services import AIService, VoiceService, DatabaseService
from models.schemas import (
    HealthResponse, ElderlyPerson, DailySummary, RawConversation, DashboardData
)
from api.dependencies import get_ai_service, get_voice_service, get_database_service

router = APIRouter()

# 既存のエンドポイント
@router.post("/process_audio")
async def process_audio(
    audio: UploadFile = File(...),
    ai_service: AIService = Depends(get_ai_service),
    voice_service: VoiceService = Depends(get_voice_service),
    db_service: DatabaseService = Depends(get_database_service)
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

        # データベースに会話を保存
        # TODO: elderly_person_idは実際のユーザー認証から取得
        conversation = RawConversation(
            id=0,  # DBで自動生成
            elderly_person_id=1,  # 仮のID
            timestamp=datetime.now().isoformat(),
            speaker="user",
            content=user_text
        )
        await db_service.save_conversation(conversation)
        
        conversation_response = RawConversation(
            id=0,
            elderly_person_id=1,
            timestamp=datetime.now().isoformat(),
            speaker="robot",
            content=response_text
        )
        await db_service.save_conversation(conversation_response)
        
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
    # 並行してデータを取得
    person = await db_service.get_elderly_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Elderly person not found")
    
    summary = await db_service.get_daily_summary(person_id, date)
    if not summary:
        raise HTTPException(status_code=404, detail="Daily summary not found")
    
    conversations = await db_service.get_conversations(person_id, date)
    
    return DashboardData(
        elderlyPerson=person,
        dailySummary=summary,
        conversations=conversations
    )

# データ作成用のエンドポイント（開発・テスト用）

@router.post("/elderly-persons", response_model=ElderlyPerson)
async def create_elderly_person(
    person: ElderlyPerson,
    db_service: DatabaseService = Depends(get_database_service)
):
    """高齢者情報を作成"""
    created_person = await db_service.create_elderly_person(person)
    if not created_person:
        raise HTTPException(status_code=500, detail="Failed to create elderly person")
    return created_person

@router.post("/daily-summaries", response_model=DailySummary)
async def create_daily_summary(
    summary: DailySummary,
    db_service: DatabaseService = Depends(get_database_service)
):
    """日次サマリーを作成"""
    created_summary = await db_service.save_daily_summary(summary)
    if not created_summary:
        raise HTTPException(status_code=500, detail="Failed to create daily summary")
    return created_summary

# 日次サマリー自動生成エンドポイント
@router.post("/generate-daily-summary", response_model=DailySummary)
async def generate_daily_summary(
    person_id: int = Query(..., description="高齢者のID"),
    date: str = Query(..., description="日付 (YYYY-MM-DD形式)"),
    db_service: DatabaseService = Depends(get_database_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """指定日の会話データから日次サマリーを自動生成"""
    # 既存のサマリーがあるか確認
    existing_summary = await db_service.get_daily_summary(person_id, date)
    if existing_summary:
        raise HTTPException(
            status_code=400, 
            detail="Daily summary already exists for this date. Delete it first if you want to regenerate."
        )
    
    # サマリーを生成
    generated_summary = await ai_service.generate_daily_summary(person_id, date, db_service)
    
    if not generated_summary:
        raise HTTPException(
            status_code=404, 
            detail="No conversations found for the specified date"
        )
    
    return generated_summary

@router.post("/generate-today-summary", response_model=DailySummary)
async def generate_today_summary(
    person_id: int = Query(..., description="高齢者のID"),
    db_service: DatabaseService = Depends(get_database_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """今日の会話データから日次サマリーを自動生成"""
    from datetime import date
    today = date.today().isoformat()
    
    # 既存のサマリーがあるか確認
    existing_summary = await db_service.get_daily_summary(person_id, today)
    if existing_summary:
        raise HTTPException(
            status_code=400, 
            detail="Today's summary already exists. Delete it first if you want to regenerate."
        )
    
    # サマリーを生成
    generated_summary = await ai_service.generate_summary_for_today(person_id, db_service)
    
    if not generated_summary:
        raise HTTPException(
            status_code=404, 
            detail="No conversations found for today"
        )
    
    return generated_summary