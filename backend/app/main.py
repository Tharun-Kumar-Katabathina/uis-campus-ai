from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.me import router as me_router

app = FastAPI(title="UIS CampusAI Backend")

app.include_router(health_router)
app.include_router(me_router)
app.include_router(chat_router)
