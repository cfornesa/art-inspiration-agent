import os
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# 1. SECURITY: Keep this global as it's needed for every pre-flight request
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cfornesa.com", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. LIGHTWEIGHT HEALTH ROUTE: Stops the 404 logs and costs near zero
@app.get("/")
async def health():
    return {"status": "ok"}

# Data model for incoming requests
class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

# 3. DEFERRED LOGIC FUNCTION
def get_system_prompt():
    # Keep the large strings here so they aren't loaded into RAM until /chat is hit
    GOALS = "..." # (Paste your full GOALS string here)
    ACTIONS = "..." # (Paste your full ACTIONS string here)
    INFORMATION = "..." # (Paste your full INFORMATION string here)
    LANGUAGE = "..." # (Paste your full LANGUAGE string here)
    return f"{GOALS}\n{ACTIONS}\n{INFORMATION}\n{LANGUAGE}"

@app.post("/chat")
async def chat(request: ChatRequest):
    # DEFERRED IMPORT: OpenAI client only loads when a user actually chats
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ['DEEPSEEK_API_KEY'], 
        base_url="https://api.deepseek.com"
    )

    # Constructing prompt locally
    system_content = get_system_prompt()
    messages = [{"role": "system", "content": system_content}] + request.history
    messages.append({"role": "user", "content": request.message})

    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
            max_tokens=1024
        )

        agent_reply = response.choices[0].message.content

        # MANUAL CLEANUP
        del messages
        gc.collect()

        return {"reply": agent_reply}

    except Exception as e:
        gc.collect()
        return {"reply": f"An error occurred: {str(e)}"}