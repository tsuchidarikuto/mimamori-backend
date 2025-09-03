"""会話処理サービス"""

from typing import Optional
from datetime import datetime
from fastapi import UploadFile

from app.interfaces.services import ConversationServiceInterface
from app.interfaces.repositories import (
    DatabaseRepositoryInterface,
    OpenAIRepositoryInterface,
    VoiceRepositoryInterface
)
from app.schemas.models import RawConversation


class ConversationService(ConversationServiceInterface):
    """会話処理ビジネスロジック"""
    
    def __init__(
        self,
        db_repository: DatabaseRepositoryInterface,
        openai_repository: OpenAIRepositoryInterface,
        voice_repository: VoiceRepositoryInterface
    ):
        self.db_repo = db_repository
        self.openai_repo = openai_repository
        self.voice_repo = voice_repository
    
    async def process_voice_conversation(
        self, 
        audio_file: UploadFile,
        elderly_person_id: int = 1
    ) -> Optional[bytes]:
        """音声会話を処理して応答音声を返す"""
        try:
            # 音声をテキストに変換
            audio_data = await audio_file.read()
            user_text = await self.openai_repo.transcribe_audio(audio_data, ".wav")
            
            if not user_text:
                return None
            
            # AIから応答を生成
            messages = [
                {"role": "system", "content": "You are a helpful voice assistant. Keep responses concise."},
                {"role": "user", "content": user_text}
            ]
            
            response_text = await self.openai_repo.generate_chat_response(messages, max_tokens=150)
            
            if not response_text:
                return None
            
            # 会話ペアを保存
            await self.save_conversation_pair(elderly_person_id, user_text, response_text)
            
            # テキストを音声に変換
            audio_response = await self.voice_repo.text_to_speech(response_text, speaker_id=3)
            
            return audio_response
            
        except Exception as e:
            print(f"Voice conversation processing error: {e}")
            return None
    
    async def save_conversation_pair(
        self,
        elderly_person_id: int,
        user_text: str,
        robot_text: str
    ) -> None:
        """会話ペアを保存"""
        try:
            timestamp = datetime.now().isoformat()
            
            # ユーザーの発言を保存
            user_conversation = RawConversation(
                id=0,
                elderly_person_id=elderly_person_id,
                timestamp=timestamp,
                speaker="user",
                content=user_text
            )
            
            # ロボットの応答を保存
            robot_conversation = RawConversation(
                id=0,
                elderly_person_id=elderly_person_id,
                timestamp=timestamp,
                speaker="robot",
                content=robot_text
            )
            
            # 両方保存
            await self.db_repo.save_conversation(user_conversation)
            await self.db_repo.save_conversation(robot_conversation)
            
        except Exception as e:
            print(f"Error saving conversation pair: {e}")