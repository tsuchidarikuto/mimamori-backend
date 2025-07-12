import requests
from typing import Optional

class VoiceService:
    def __init__(self, voicevox_url: str, speaker_id: int):
        self.voicevox_url = voicevox_url
        self.speaker_id = speaker_id
    
    async def text_to_speech(self, text: str) -> Optional[bytes]:
        try:
            query_response = requests.post(
                f"{self.voicevox_url}/audio_query",
                params={"text": text, "speaker": self.speaker_id}
            )
            query_response.raise_for_status()
            
            synthesis_response = requests.post(
                f"{self.voicevox_url}/synthesis",
                params={"speaker": self.speaker_id},
                json=query_response.json()
            )
            synthesis_response.raise_for_status()
            
            return synthesis_response.content
        except requests.exceptions.ConnectionError:
            print(f"Error: VOICEVOX not running. Please start VOICEVOX on {self.voicevox_url}")
            return None
        except Exception as e:
            print(f"Text-to-speech error: {e}")
            return None
