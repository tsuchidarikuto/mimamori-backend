from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.dirname(__file__))

from api import router
from config import settings

app = FastAPI(title="Voice Assistant & Monitoring API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # フロントエンドのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを登録
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)