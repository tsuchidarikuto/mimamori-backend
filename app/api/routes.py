from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import Response
from services import AIService, VoiceService
from models import HealthResponse
from api.dependencies import get_ai_service, get_voice_service
from db import add_log # ★ データベースログ記録関数をインポート

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

        # ★★★ ここからログ記録処理を追加 ★★★
        conversation_log = f"User: {user_text} | Assistant: {response_text}"
        await add_log(conversation_log) # ★ 会話ログを非同期で記録
        # ★★★ ログ記録処理ここまで ★★★
        
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