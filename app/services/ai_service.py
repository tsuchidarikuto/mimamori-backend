import tempfile
from typing import List, Optional
from datetime import datetime, date
from fastapi import UploadFile
from openai import AsyncOpenAI
from pydantic import BaseModel
from models.schemas import RawConversation, DailySummary, EmotionalDataPoint
from services.database_service import DatabaseService

class EmotionalGraphItem(BaseModel):
    time: str
    score: float
    label: str

class SummaryResponse(BaseModel):
    summary_text: str
    emotional_state: str
    health_summary: str
    emotional_graph: List[EmotionalGraphItem]

class AIService:
    def __init__(self, api_key: str, transcribe_model: str, chat_model: str, language: str, max_tokens: int):
        self.client = AsyncOpenAI(api_key=api_key)
        self.transcribe_model = transcribe_model
        self.chat_model = chat_model
        self.language = language
        self.max_tokens = max_tokens
    
    async def transcribe_audio(self, audio_file: UploadFile) -> Optional[str]:
        """音声ファイルをテキストに変換"""
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
        """ユーザーのテキストに対する応答を生成"""
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

    async def generate_daily_summary(
        self, 
        elderly_person_id: int, 
        target_date: str,
        db_service: DatabaseService
    ) -> Optional[DailySummary]:
        """指定日の会話データから日次サマリーを生成"""
        
        # その日の会話データを取得
        conversations = await db_service.get_conversations(elderly_person_id, target_date)
        
        if not conversations:
            return None
        
        # 会話を時系列順のテキストに変換
        conversation_text = self._format_conversations(conversations)
        
        # GPT-4o-miniを使ってサマリーを生成
        summary_data = await self._generate_summary_with_gpt(conversation_text)
        
        if not summary_data:
            return None
        
        # DailySummaryオブジェクトを作成
        daily_summary = DailySummary(
            id=0,  # DBで自動生成
            elderly_person_id=elderly_person_id,
            date=target_date,
            summary_text=summary_data['summary_text'],
            emotional_state=summary_data['emotional_state'],
            health_summary=summary_data['health_summary'],
            conversation_count=len(conversations),
            emotional_graph=summary_data['emotional_graph']
        )
        
        # データベースに保存
        saved_summary = await db_service.save_daily_summary(daily_summary)
        
        return saved_summary
    
    def _format_conversations(self, conversations: List[RawConversation]) -> str:
        """会話リストを読みやすいテキスト形式に変換"""
        formatted_lines = []
        
        for conv in conversations:
            time = datetime.fromisoformat(conv.timestamp).strftime("%H:%M")
            speaker = "高齢者" if conv.speaker == "user" else "ロボット"
            formatted_lines.append(f"[{time}] {speaker}: {conv.content}")
        
        return "\n".join(formatted_lines)
    
    async def _generate_summary_with_gpt(self, conversation_text: str) -> Optional[dict]:
        """GPT-4o-miniを使って会話からサマリーを生成（Structured Outputs使用）"""
        
        system_prompt = """あなたは高齢者の見守りシステムのAIアシスタントです。
高齢者とロボットの一日の会話記録から、以下の情報を抽出して日本語でまとめてください：

1. 一日の様子の要約（summary_text）: その日の出来事や活動を2-3文でまとめる
2. 感情状態（emotional_state）: 「穏やか」「元気」「少し疲れ気味」など、簡潔に表現
3. 健康に関する要約（health_summary）: 体調、食事、睡眠などの健康関連情報をまとめる
4. 感情の変化グラフ用データ（emotional_graph）: 一日の中での感情の変化を5つの時点で数値化（0-10のスコア）"""

        user_prompt = f"以下の会話記録から、高齢者の一日の様子をまとめてください：\n\n{conversation_text}"
        
        try:
            completion = await self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=SummaryResponse,
                temperature=0.7,
                max_tokens=1000
            )
            
            parsed_response = completion.choices[0].message.parsed
            
            if parsed_response:
                # emotional_graphをEmotionalDataPointのリストに変換
                emotional_graph = [
                    EmotionalDataPoint(
                        time=item.time,
                        score=item.score,
                        label=item.label
                    )
                    for item in parsed_response.emotional_graph
                ]
                
                return {
                    "summary_text": parsed_response.summary_text,
                    "emotional_state": parsed_response.emotional_state,
                    "health_summary": parsed_response.health_summary,
                    "emotional_graph": emotional_graph
                }
            else:
                raise Exception("Failed to parse response")
            
        except Exception as e:
            print(f"Error generating summary with GPT: {e}")
            # エラー時のデフォルト値を返す
            return {
                "summary_text": "本日の会話記録からサマリーを生成できませんでした。",
                "emotional_state": "不明",
                "health_summary": "健康状態の詳細は不明です。",
                "emotional_graph": [
                    EmotionalDataPoint(time="9:00", score=5.0, label="朝"),
                    EmotionalDataPoint(time="12:00", score=5.0, label="昼"),
                    EmotionalDataPoint(time="15:00", score=5.0, label="午後"),
                    EmotionalDataPoint(time="18:00", score=5.0, label="夕方"),
                    EmotionalDataPoint(time="21:00", score=5.0, label="夜")
                ]
            }
    
    async def generate_summary_for_today(
        self, 
        elderly_person_id: int,
        db_service: DatabaseService
    ) -> Optional[DailySummary]:
        """今日の日次サマリーを生成"""
        today = date.today().isoformat()
        return await self.generate_daily_summary(elderly_person_id, today, db_service)