import tempfile
from fastapi import UploadFile
from openai import AsyncOpenAI
from typing import Optional

class AIService:
    def __init__(self, api_key: str, transcribe_model: str, chat_model: str, language: str, max_tokens: int):
        self.client = AsyncOpenAI(api_key=api_key)
        self.transcribe_model = transcribe_model
        self.chat_model = chat_model
        self.language = language
        self.max_tokens = max_tokens
    
    async def transcribe_audio(self, audio_file: UploadFile) -> Optional[str]:
        try:
            audio_data = await audio_file.read()
            with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                
                with open(temp_file.name, 'rb') as f:
                    response = await self.client.audio.transcriptions.create(
                        model=self.transcribe_model,
                        language=self.language,
                        file=f
                    )
                
                return response.text.strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
    
    async def generate_response(self, user_text: str) -> Optional[str]:
        try:
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You are a helpful voice assistant. Keep responses concise."},
                    {"role": "user", "content": user_text}
                ],
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Response generation error: {e}")
            return None
