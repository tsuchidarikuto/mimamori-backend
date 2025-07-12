from fastapi import FastAPI
from api import router
from config import settings

app = FastAPI(title="Voice Assistant API")

app.include_router(router)

<<<<<<< HEAD
#test
@app.get("/")
async def root():
    return {"message": "Hello, Teraoka!"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # WebSocket処理をここに書く
    #test 
=======
>>>>>>> origin/dev

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)

    
