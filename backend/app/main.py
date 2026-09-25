from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.feedback import router as feedback_router
from app.api.health import router as health_router
from app.api.me import router as me_router

app = FastAPI(title="UIS CampusAI Backend")

# Dev-friendly default: the frontend runs on a different origin
# (localhost:3000 vs. this API's localhost:8000). Tightening this for a
# real deployment is a config change, not a code change.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(me_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(feedback_router)
