"""高齢者管理サービス"""

from typing import Optional, List

from app.interfaces.services import ElderlyServiceInterface
from app.interfaces.repositories import DatabaseRepositoryInterface
from app.schemas.models import ElderlyPerson, RawConversation, DashboardData
from app.core.exceptions import NotFoundException


class ElderlyService(ElderlyServiceInterface):
    """高齢者管理ビジネスロジック"""
    
    def __init__(self, db_repository: DatabaseRepositoryInterface):
        self.db_repo = db_repository
    
    async def get_elderly_person(self, person_id: int) -> Optional[ElderlyPerson]:
        """高齢者情報を取得"""
        try:
            person = await self.db_repo.get_elderly_person(person_id)
            if not person:
                raise NotFoundException(f"Elderly person with ID {person_id} not found")
            return person
        except Exception as e:
            print(f"Error getting elderly person: {e}")
            return None
    
    async def get_conversations(
        self, 
        person_id: int, 
        target_date: str
    ) -> List[RawConversation]:
        """指定日の会話履歴を取得"""
        try:
            # 高齢者の存在確認
            person = await self.db_repo.get_elderly_person(person_id)
            if not person:
                raise NotFoundException(f"Elderly person with ID {person_id} not found")
            
            conversations = await self.db_repo.get_conversations(person_id, target_date)
            return conversations
            
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    async def get_dashboard_data(
        self,
        person_id: int,
        target_date: str
    ) -> DashboardData:
        """ダッシュボード用データを取得"""
        try:
            # 高齢者情報を取得
            person = await self.db_repo.get_elderly_person(person_id)
            if not person:
                raise NotFoundException(f"Elderly person with ID {person_id} not found")
            
            # サマリーと会話履歴を並列で取得
            summary = await self.db_repo.get_daily_summary(person_id, target_date)
            conversations = await self.db_repo.get_conversations(person_id, target_date)
            
            return DashboardData(
                elderlyPerson=person,
                dailySummary=summary,
                conversations=conversations
            )
            
        except Exception as e:
            print(f"Error getting dashboard data: {e}")
            # エラー時は最低限のデータを返す
            return DashboardData(
                elderlyPerson=None,
                dailySummary=None,
                conversations=[]
            )