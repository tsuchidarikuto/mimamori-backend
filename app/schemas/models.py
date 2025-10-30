from pydantic import BaseModel
from typing import Optional, List


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

# みまもりダッシュボード用のモデル

class ElderlyPerson(BaseModel):
    id: int
    last_name: str
    first_name: str
    age: int

class RawConversation(BaseModel):
    id: int
    elderly_person_id: int
    timestamp: str
    speaker: str  # "user" or "robot"
    content: str

class EmotionalDataPoint(BaseModel):
    time: str
    score: float
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

class DashboardData(BaseModel):
    elderlyPerson: Optional[ElderlyPerson]
    dailySummary: Optional[DailySummary]
    conversations: List[RawConversation]