from pydantic import BaseModel
from typing import Optional

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
