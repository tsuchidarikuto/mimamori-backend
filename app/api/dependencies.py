from config import settings
from services import AIService, VoiceService

def get_ai_service() -> AIService:
    return AIService(
        api_key=settings.openai_api_key,
        transcribe_model=settings.transcribe_model,
        chat_model=settings.chat_model,
        language=settings.language,
        max_tokens=settings.max_tokens
    )

def get_voice_service() -> VoiceService:
    return VoiceService(
        voicevox_url=settings.voicevox_url,
        speaker_id=settings.speaker_id
    )
