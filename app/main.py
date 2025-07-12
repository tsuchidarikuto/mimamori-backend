from fastapi import FastAPI
from api import router
from config import settings

server = FastAPI(title="Voice Assistant API")

server.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server, host=settings.host, port=settings.port)
