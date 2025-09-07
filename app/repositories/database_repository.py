"""データベース操作のRepository実装"""

from typing import List, Optional
from datetime import datetime
from supabase import create_client, Client

from app.schemas.models import ElderlyPerson, DailySummary, RawConversation, EmotionalDataPoint
from app.interfaces.repositories import DatabaseRepositoryInterface


class DatabaseRepository(DatabaseRepositoryInterface):
    """Supabaseデータベースリポジトリ"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    async def get_elderly_person(self, person_id: int) -> Optional[ElderlyPerson]:
        """高齢者情報を取得"""
        try:
            response = self.supabase.table('elderly_persons').select('*').eq('id', person_id).execute()
            
            if response.data and len(response.data) > 0:
                data = response.data[0]
                return ElderlyPerson(
                    id=data['id'],
                    last_name=data['last_name'],
                    first_name=data['first_name'],
                    age=data['age']
                )
            return None
        except Exception as e:
            print(f"Error fetching elderly person: {e}")
            return None
    
    async def create_elderly_person(self, person: ElderlyPerson) -> Optional[ElderlyPerson]:
        """高齢者情報を作成"""
        try:
            response = self.supabase.table('elderly_persons').insert({
                'last_name': person.last_name,
                'first_name': person.first_name,
                'age': person.age
            }).execute()
            
            if response.data and len(response.data) > 0:
                data = response.data[0]
                return ElderlyPerson(
                    id=data['id'],
                    last_name=data['last_name'],
                    first_name=data['first_name'],
                    age=data['age']
                )
            return None
        except Exception as e:
            print(f"Error creating elderly person: {e}")
            return None
    
    async def get_daily_summary(self, person_id: int, date: str) -> Optional[DailySummary]:
        """日次サマリーを取得"""
        try:
            response = self.supabase.table('daily_summaries').select('*').eq('elderly_person_id', person_id).eq('date', date).execute()
            
            if response.data and len(response.data) > 0:
                data = response.data[0]
                
                # 感情グラフデータを取得
                emotional_response = self.supabase.table('emotional_data').select('*').eq('daily_summary_id', data['id']).order('time').execute()
                
                emotional_graph = []
                if emotional_response.data:
                    emotional_graph = [
                        EmotionalDataPoint(
                            time=item['time'],
                            score=float(item['score']),
                            label=item['label']
                        )
                        for item in emotional_response.data
                    ]
                
                return DailySummary(
                    id=data['id'],
                    elderly_person_id=data['elderly_person_id'],
                    date=data['date'],
                    summary_text=data['summary_text'],
                    emotional_state=data['emotional_state'],
                    health_summary=data['health_summary'],
                    conversation_count=data['conversation_count'],
                    emotional_graph=emotional_graph
                )
            return None
        except Exception as e:
            print(f"Error fetching daily summary: {e}")
            return None
    
    async def save_daily_summary(self, summary: DailySummary) -> Optional[DailySummary]:
        """日次サマリーを保存"""
        try:
            # サマリー本体を保存
            response = self.supabase.table('daily_summaries').insert({
                'elderly_person_id': summary.elderly_person_id,
                'date': summary.date,
                'summary_text': summary.summary_text,
                'emotional_state': summary.emotional_state,
                'health_summary': summary.health_summary,
                'conversation_count': summary.conversation_count
            }).execute()
            
            if response.data and len(response.data) > 0:
                summary_data = response.data[0]
                summary_id = summary_data['id']
                
                # 感情グラフデータを保存
                if summary.emotional_graph:
                    emotional_data = [
                        {
                            'daily_summary_id': summary_id,
                            'time': point.time,
                            'score': int(round(float(point.score))),
                            'label': point.label
                        }
                        for point in summary.emotional_graph
                    ]
                    self.supabase.table('emotional_data').insert(emotional_data).execute()
                
                return DailySummary(
                    id=summary_id,
                    elderly_person_id=summary_data['elderly_person_id'],
                    date=summary_data['date'],
                    summary_text=summary_data['summary_text'],
                    emotional_state=summary_data['emotional_state'],
                    health_summary=summary_data['health_summary'],
                    conversation_count=summary_data['conversation_count'],
                    emotional_graph=summary.emotional_graph
                )
            return None
        except Exception as e:
            print(f"Error saving daily summary: {e}")
            return None
    
    async def delete_daily_summary(self, person_id: int, date: str) -> bool:
        """日次サマリーを削除"""
        try:
            # まず該当するサマリーを取得
            summary = await self.get_daily_summary(person_id, date)
            if not summary:
                return False
            
            # 関連する感情データを削除
            self.supabase.table('emotional_data').delete().eq('daily_summary_id', summary.id).execute()
            
            # サマリー本体を削除
            self.supabase.table('daily_summaries').delete().eq('id', summary.id).execute()
            
            return True
        except Exception as e:
            print(f"Error deleting daily summary: {e}")
            return False
    
    async def get_conversations(self, person_id: int, date: str) -> List[RawConversation]:
        """会話履歴を取得"""
        try:
            # その日の会話を時系列順で取得
            response = self.supabase.table('conversations').select('*').eq('elderly_person_id', person_id).gte('timestamp', f'{date}T00:00:00').lt('timestamp', f'{date}T23:59:59').order('timestamp').execute()
            
            conversations = []
            if response.data:
                conversations = [
                    RawConversation(
                        id=item['id'],
                        elderly_person_id=item['elderly_person_id'],
                        timestamp=item['timestamp'],
                        speaker=item['speaker'],
                        content=item['content']
                    )
                    for item in response.data
                ]
            
            return conversations
        except Exception as e:
            print(f"Error fetching conversations: {e}")
            return []
    
    async def save_conversation(self, conversation: RawConversation) -> Optional[RawConversation]:
        """会話を保存"""
        try:
            response = self.supabase.table('conversations').insert({
                'elderly_person_id': conversation.elderly_person_id,
                'timestamp': conversation.timestamp,
                'speaker': conversation.speaker,
                'content': conversation.content
            }).execute()
            
            if response.data and len(response.data) > 0:
                data = response.data[0]
                return RawConversation(
                    id=data['id'],
                    elderly_person_id=data['elderly_person_id'],
                    timestamp=data['timestamp'],
                    speaker=data['speaker'],
                    content=data['content']
                )
            return None
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return None