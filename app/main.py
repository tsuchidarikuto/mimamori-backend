from fastapi import FastAPI

app = FastAPI()

@app.get('/api/data')
async def get_data():
    response = {
        'message': 'Hello World!'
    }
    return response
