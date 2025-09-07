"""会話処理ルーター（UI層）"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import Response

from app.interfaces.services import ConversationServiceInterface
from app.schemas.responses import ErrorResponse
from app.core.dependencies import get_conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


# 依存性注入をインポート
from app.core.dependencies import get_conversation_service


@router.post("/process-audio", response_class=Response)
async def process_audio(
    audio: UploadFile = File(..., description="音声ファイル"),
    elderly_person_id: int = 1,
    conversation_service: ConversationServiceInterface = Depends(get_conversation_service)
) -> Response:
    """
    音声を処理して応答音声を返す
    
    - 音声ファイルをアップロード
    - テキストに変換してAI応答を生成
    - 応答を音声に変換して返却
    """
    try:
        # ファイル形式チェック
        if not audio.content_type or not audio.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=400, 
                detail="Audio file required"
            )
        
        # サービス層で音声処理を実行
        audio_response = await conversation_service.process_voice_conversation(
            audio_file=audio,
            elderly_person_id=elderly_person_id
        )
        
        if not audio_response:
            raise HTTPException(
                status_code=500,
                detail="Failed to process audio conversation"
            )
        
        return Response(
            content=audio_response,
            media_type="audio/wav"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )