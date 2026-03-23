"""
main.py – FastAPI application entry point for the Art Inspiration Agent.

Configures the app, registers CORS middleware and static files, defines
all routes, and delegates core generation logic to model.py.
"""

import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional

from model import generate_response
from rag_module import get_art_context 

# Operational Transparency Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Art Inspiration Agent - Mistral Edition",
    description="An expert art consultant chatbot with preference-based fine-tuning.",
    version="1.0",
)

# CORS Middleware: allow cross-origin access for Hostinger frontend / UI clients.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets (CSS, JS, images) served alongside the frontend.
app.mount("/static", StaticFiles(directory="static"), name="static")


class UserPreferences(BaseModel):
    """
    Fine-tuning preferences to calibrate the assistant's responses.

    All fields are optional; unset fields leave that dimension at default.
    Accepted values are open-ended strings — the model interprets them
    via the preference context block built in model.py.
    """
    style: Optional[str] = None        # e.g., "impressionist", "abstract", "realist"
    medium: Optional[str] = None       # e.g., "oil paint", "watercolor", "charcoal"
    skill_level: Optional[str] = None  # "beginner", "intermediate", or "advanced"
    focus: Optional[str] = None        # e.g., "color theory", "composition", "texture"


class ArtChatRequest(BaseModel):
    """Request model for the Art Inspiration Agent chat endpoint."""
    message: str
    history: List[Dict] = []
    preferences: Optional[UserPreferences] = None


@app.get("/")
async def index():
    """Serve the frontend HTML entry point."""
    return FileResponse("templates/index.html")


@app.get("/health")
async def health_check():
    """Infrastructure ping to confirm deployment vitality."""
    return {
        "status": "online",
        "agent": "Art Inspiration Agent",
        "version": "1.0",
        "features": [
            "pii_redaction",
            "preference_fine_tuning",
            "archival_standards",
            "mistral_sovereignty",
        ],
    }


@app.post("/chat")
async def process_chat(request: ArtChatRequest):
    """
    Accept a user art inspiration request and return a calibrated response.

    Delegates all generation and PII-scrubbing logic to model.generate_response,
    passing the sanitized message, conversation history, and optional user
    preferences for session-level fine-tuning.
    """
    try:
        # ── RAG: retrieve relevant art knowledge and prepend to user input ──
        art_context = get_art_context(request.message)
        augmented_input = (
            f"[Retrieved Reference Material]\n{art_context}\n\n"
            f"[User Message]\n{request.message}"
        )
        # ────────────────────────────────────────────────────────────────────
        preferences_dict = request.preferences.model_dump() if request.preferences else None
        result = generate_response(
            user_input=augmented_input,   # ← was: request.message
            history=request.history,
            preferences=preferences_dict,
        )
        return result
    except Exception as e:
        return {"reply": f"System Error: {str(e)}"}


if __name__ == "__main__":
    # OS environment lookup for dynamic cloud port allocation (e.g., Replit).
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
