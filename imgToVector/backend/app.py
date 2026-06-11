from fastapi import FastAPI
from routes.vectorize import router

app = FastAPI(
    title="Vectorizer API"
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "status": "online"
    }