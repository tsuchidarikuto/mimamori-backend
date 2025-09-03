"""サマリー生成サービス"""

from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel

from app.interfaces.services import SummaryServiceInterface
from app.interfaces.repositories import (
    DatabaseRepositoryInterface,
    OpenAIRepositoryInterface
)
from app.schemas.models import DailySummary, RawConversation, EmotionalDataPoint
from app.core.exceptions import NotFoundException, ValidationException


class EmotionalGraphItem(BaseModel):
    """感情グラフアイテム（GPT応答用）"""
    time: str
    score: float
    label: str


class SummaryResponse(BaseModel):
    """サマリー応答（GPT応答用）"""
    summary_text: str
    emotional_state: str
    health_summary: str
    emotional_graph: List[EmotionalGraphItem]


class SummaryService(SummaryServiceInterface):
    """サマリー生成ビジネスロジック"""
    
    def __init__(
        self,
        db_repository: DatabaseRepositoryInterface,
        openai_repository: OpenAIRepositoryInterface
    ):
        self.db_repo = db_repository
        self.openai_repo = openai_repository
    
    async def get_daily_summary(
        self,
        person_id: int,
        target_date: str
    ) -> Optional[DailySummary]:
        """日次サマリーを取得"""
        try:
            # 高齢者の存在確認
            person = await self.db_repo.get_elderly_person(person_id)
            if not person:
                raise NotFoundException(f"Elderly person with ID {person_id} not found")
            
            summary = await self.db_repo.get_daily_summary(person_id, target_date)
            return summary
            
        except Exception as e:
            print(f"Error getting daily summary: {e}")
            return None
    
    async def generate_daily_summary(
        self,
        person_id: int,
        target_date: str,
        overwrite: bool = False
    ) -> DailySummary:
        """日次サマリーを生成"""
        try:
            # 高齢者の存在確認
            person = await self.db_repo.get_elderly_person(person_id)
            if not person:
                raise NotFoundException(f"Elderly person with ID {person_id} not found")
            
            # 既存サマリーのチェック
            existing_summary = await self.db_repo.get_daily_summary(person_id, target_date)
            if existing_summary and not overwrite:
                raise ValidationException(
                    "Summary already exists. Set overwrite=true to regenerate."
                )
            elif existing_summary:
                await self.db_repo.delete_daily_summary(person_id, target_date)
            
            # その日の会話データを取得
            conversations = await self.db_repo.get_conversations(person_id, target_date)
            if not conversations:
                raise NotFoundException("No conversations found for the specified date")
            
            # GPTでサマリーを生成
            summary_data = await self._generate_summary_with_gpt(conversations)
            if not summary_data:
                raise Exception("Failed to generate summary with GPT")
            
            # DailySummaryオブジェクトを作成
            daily_summary = DailySummary(
                id=0,  # DBで自動生成
                elderly_person_id=person_id,
                date=target_date,
                summary_text=summary_data['summary_text'],
                emotional_state=summary_data['emotional_state'],
                health_summary=summary_data['health_summary'],
                conversation_count=len(conversations),
                emotional_graph=summary_data['emotional_graph']
            )
            
            # データベースに保存
            saved_summary = await self.db_repo.save_daily_summary(daily_summary)
            if not saved_summary:
                raise Exception("Failed to save summary to database")
            
            return saved_summary
            
        except Exception as e:
            print(f"Error generating daily summary: {e}")
            raise
    
    def _format_conversations(self, conversations: List[RawConversation]) -> str:
        """会話リストを読みやすいテキスト形式に変換"""
        formatted_lines = []
        
        for conv in conversations:
            time = datetime.fromisoformat(conv.timestamp).strftime("%H:%M")
            speaker = "高齢者" if conv.speaker == "user" else "ロボット"
            formatted_lines.append(f"[{time}] {speaker}: {conv.content}")
        
        return "\n".join(formatted_lines)
    
    async def _generate_summary_with_gpt(self, conversations: List[RawConversation]) -> Optional[dict]:
        """GPT-4o-miniを使って会話からサマリーを生成"""
        
        conversation_text = self._format_conversations(conversations)
        
        system_prompt = """あなたは高齢者の見守りシステムのAIアシスタントです。
高齢者とロボットの一日の会話記録から、以下の情報を抽出して日本語でまとめてください：

1. 一日の様子の要約（summary_text）: その日の出来事や活動を2-3文でまとめる
2. 感情状態（emotional_state）: 「穏やか」「元気」「少し疲れ気味」など、簡潔に表現
3. 健康に関する要約（health_summary）: 体調、食事、睡眠などの健康関連情報をまとめる
4. 感情の変化グラフ用データ（emotional_graph）: 一日の中での感情の変化を5つの時点で数値化（0-10のスコア）"""

        user_prompt = f"以下の会話記録から、高齢者の一日の様子をまとめてください：\\n\\n{conversation_text}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response_data = await self.openai_repo.generate_structured_response(
                messages=messages,
                response_format=SummaryResponse,
                max_tokens=1000
            )
            
            if response_data:
                # emotional_graphをEmotionalDataPointのリストに変換
                emotional_graph = [
                    EmotionalDataPoint(
                        time=item['time'],
                        score=item['score'],
                        label=item['label']
                    )
                    for item in response_data['emotional_graph']
                ]
                
                return {
                    "summary_text": response_data['summary_text'],
                    "emotional_state": response_data['emotional_state'],
                    "health_summary": response_data['health_summary'],
                    "emotional_graph": emotional_graph
                }
            else:
                raise Exception("Failed to parse GPT response")
                
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