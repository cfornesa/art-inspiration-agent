import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# SECURITY: Allow your Hostinger site to talk to this Repl
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your actual domain for better security
    allow_methods=["*"],
    allow_headers=["*"],
)

# GAIL Framework instantiated as variables
GOALS = """You are an AI agent that provides advice about art ideation..."""
ACTIONS = """If a user makes an inquiry, extract the main points..."""
INFORMATION = """Be mindful of any items in the memory..."""
LANGUAGE = """Respond in this format: Question, Bullet Point Answer, Resources, Paragraph Answer."""

SYSTEM_PROMPT = f"{GOALS}\n\n{ACTIONS}\n\n{INFORMATION}\n\n{LANGUAGE}"

# Data model for incoming requests
class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

@app.post("/chat")
async def chat(request: ChatRequest):
    # Replit Secrets: Set 'DEEPSEEK_API_KEY' in the Secrets tool
    client = OpenAI(api_key=os.environ['DEEPSEEK_API_KEY'], base_url="https://api.deepseek.com")
    
    # Constructing the GAIL prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + request.history
    messages.append({"role": "user", "content": request.message})
    
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages,
        max_tokens=1024
    )
    
    agent_reply = response.choices[0].message.content
    return {"reply": agent_reply}
