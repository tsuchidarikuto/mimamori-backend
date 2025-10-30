"""新しいアーキテクチャのメインアプリケーション"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import sys
import os

# パスを追加
sys.path.append(os.path.dirname(__file__))

# 新しいルーター
from app.routers.conversation_router import router as conversation_router
from app.routers.elderly_router import router as elderly_router  
from app.routers.health_router import router as health_router

# 設定とDIコンテナ
from app.config import settings
from app.core.container import container
from app.core.exceptions import AppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # 起動時の処理
    print("Starting Voice Assistant & Monitoring API")
    
    # DIコンテナの初期化確認
    try:
        db_repo = container.get_database_repository()
        print("Database repository initialized")
        
        openai_repo = container.get_openai_repository()
        print("OpenAI repository initialized")
        
        voice_repo = container.get_voice_repository()
        print("Voice repository initialized")
        
        print("All repositories initialized successfully")
    except Exception as e:
        print(f"Failed to initialize repositories: {e}")
    
    yield
    
    # 終了時の処理
    print("Shutting down Voice Assistant & Monitoring API")


# FastAPIアプリケーションの作成
app = FastAPI(
    title="Voice Assistant & Monitoring API",
    description="高齢者見守りシステムAPI（3層アーキテクチャ）",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンを設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバル例外ハンドラー
@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    """アプリケーション例外ハンドラー"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    """一般的な例外ハンドラー"""
    print(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# API V1ルーターの登録
api_v1_prefix = "/api/v1"
app.include_router(conversation_router, prefix=api_v1_prefix)
app.include_router(elderly_router, prefix=api_v1_prefix)
app.include_router(health_router)

# 旧システムは完全に削除されました

# ルート
@app.get("/")
async def root():
    """APIルート"""
    return {
        "message": "Voice Assistant & Monitoring API v1.0",
        "architecture": "3-layer (UI/Service/Repository)",
        "api_prefix": "/api/v1",
        "health": "/health",
        "docs": "/docs"
    }


if __name__ == "__main__":
    print("Starting development server...")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )