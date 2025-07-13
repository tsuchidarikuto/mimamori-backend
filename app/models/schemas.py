from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AudioProcessRequest(BaseModel):
    text: Optional[str] = None

class AudioProcessResponse(BaseModel):
    user_text: str
    response_text: str
    success: bool
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: Optional[str] = None

# みまもりダッシュボード用のスキーマ

class ElderlyPerson(BaseModel):
    id: int
    last_name: str
    first_name: str
    age: int

class EmotionalDataPoint(BaseModel):
    time: str
    score: int
    label: str

class DailySummary(BaseModel):
    id: int
    elderly_person_id: int
    date: str
    summary_text: str
    emotional_state: str
    health_summary: str
    conversation_count: int
    emotional_graph: List[EmotionalDataPoint]

class RawConversation(BaseModel):
    id: int
    elderly_person_id: int
    timestamp: str
    speaker: str  # "user" or "robot"
    content: str

class DashboardData(BaseModel):
    elderlyPerson: ElderlyPerson
    dailySummary: DailySummary
    conversations: List[RawConversation]
