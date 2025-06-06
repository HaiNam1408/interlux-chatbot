from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import Optional
import uuid
import time
from datetime import datetime, timedelta

from src.chatbot import Chatbot
from src.models import UserSession
from src.database import initialize_data_files

load_dotenv()

# Initialize data files
initialize_data_files()

# Initialize FastAPI app
app = FastAPI(title="Interlux Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

chatbot = Chatbot()

# Store user sessions with cleanup mechanism
user_sessions = {}
SESSION_TIMEOUT = timedelta(hours=24)  # Sessions expire after 24 hours

def cleanup_expired_sessions():
    """Remove expired sessions to prevent memory overflow"""
    current_time = datetime.now()
    expired_sessions = []

    for user_id, session in user_sessions.items():
        if hasattr(session, 'last_activity'):
            if current_time - session.last_activity > SESSION_TIMEOUT:
                expired_sessions.append(user_id)

    for user_id in expired_sessions:
        del user_sessions[user_id]

    if expired_sessions:
        print(f"Cleaned up {len(expired_sessions)} expired sessions")

def get_or_create_session(user_id: str) -> UserSession:
    """Get existing session or create new one"""
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession(user_id=user_id)

    # Update last activity
    session = user_sessions[user_id]
    session.last_activity = datetime.now()

    # Cleanup expired sessions periodically
    if len(user_sessions) > 100:  # Cleanup when we have too many sessions
        cleanup_expired_sessions()

    return session

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(
    message: str = Form(...),
    user_id: Optional[str] = Form(None)
):
    if not user_id:
        user_id = str(uuid.uuid4())

    session = get_or_create_session(user_id)
    session.add_message("user", message)

    structured_response = chatbot.process_message(message, session)
    session.add_message("bot", structured_response["message"])

    return {
        "response": structured_response["message"],
        "data": structured_response["data"],
        "user_id": user_id,
        "history": session.get_messages()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
