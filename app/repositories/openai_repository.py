"""OpenAI API操作のRepository実装"""

import tempfile
from typing import Optional, List
from openai import AsyncOpenAI

from app.interfaces.repositories import OpenAIRepositoryInterface


class OpenAIRepository(OpenAIRepositoryInterface):
    """OpenAI APIリポジトリ"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def transcribe_audio(self, audio_data: bytes, file_extension: str = ".wav") -> Optional[str]:
        """音声をテキストに変換"""
        try:
            with tempfile.NamedTemporaryFile(suffix=file_extension) as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                
                with open(temp_file.name, 'rb') as f:
                    response = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        language="ja",
                        file=f
                    )
                
                return response.text.strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
    
    async def generate_chat_response(
        self, 
        messages: List[dict],
        max_tokens: int = 150
    ) -> Optional[str]:
        """チャット応答を生成"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Chat response generation error: {e}")
            return None
    
    async def generate_structured_response(
        self,
        messages: List[dict],
        response_format: type,
        max_tokens: int = 1000
    ) -> Optional[dict]:
        """構造化された応答を生成"""
        try:
            completion = await self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=messages,
                response_format=response_format,
                temperature=0.7,
                max_tokens=max_tokens
            )
            
            parsed_response = completion.choices[0].message.parsed
            
            if parsed_response:
                return parsed_response.model_dump()
            else:
                raise Exception("Failed to parse response")
                
        except Exception as e:
            print(f"Structured response generation error: {e}")
            return None