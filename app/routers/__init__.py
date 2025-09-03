"""新しいRouter層の実装"""

from .conversation_router import router as conversation_router
from .elderly_router import router as elderly_router
from .health_router import router as health_router

__all__ = [
    "conversation_router",
    "elderly_router", 
    "health_router"
]