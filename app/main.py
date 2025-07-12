from fastapi import FastAPI
from api import router
from config import settings

app = FastAPI(title="Voice Assistant API")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
