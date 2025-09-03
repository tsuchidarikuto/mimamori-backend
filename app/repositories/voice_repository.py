"""音声合成API操作のRepository実装"""

import httpx
from typing import Optional

from app.interfaces.repositories import VoiceRepositoryInterface


class VoiceRepository(VoiceRepositoryInterface):
    """VoiceVox音声合成リポジトリ"""
    
    def __init__(self, voicevox_url: str):
        self.voicevox_url = voicevox_url.rstrip('/')
    
    async def text_to_speech(self, text: str, speaker_id: int = 3) -> Optional[bytes]:
        """テキストを音声に変換"""
        try:
            # 音声クエリを作成
            async with httpx.AsyncClient(timeout=30.0) as client:
                query_response = await client.post(
                    f"{self.voicevox_url}/audio_query",
                    params={"text": text, "speaker": speaker_id}
                )
                query_response.raise_for_status()
                query_data = query_response.json()
                
                # 音声合成を実行
                synthesis_response = await client.post(
                    f"{self.voicevox_url}/synthesis",
                    params={"speaker": speaker_id},
                    json=query_data,
                    headers={"Content-Type": "application/json"}
                )
                synthesis_response.raise_for_status()
                
                return synthesis_response.content
                
        except Exception as e:
            print(f"Text-to-speech error: {e}")
            return None