import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Art Inspiration Agent")

# 1. CORS MIDDLEWARE (Kept global for Pre-flight OPTIONS checks)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your specific domain for production
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER (PII REDACTION)
def redact_pii(text: str) -> str:
    """
    Blazing-fast regex-based redaction for PII. 
    Uses standard re module to avoid heavy library overhead.
    """
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        # Matches various phone formats (US and International)
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        # Dedicated SSN Pattern (XXX-XX-XXXX or XXXXXXXXX)
        "SSN": r'\b(?!666|000|9\d{2})\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b',
        "CREDIT_CARD": r'\b(?:\d[ -]*?){13,16}\b',
    }

    redacted_text = text
    for label, pattern in patterns.items():
        redacted_text = re.sub(pattern, f"[{label}_REDACTED]", redacted_text, flags=re.IGNORECASE)

    return redacted_text

# 3. DEFERRED SYSTEM PROMPT
def get_art_system_prompt():
    """Returns the full GAIL framework prompt only when needed for a chat."""
    GOALS = """
    You are a creative Art Inspiration Agent. 
    Your role is to help artists overcome blocks by providing unique, 
    challenging, and thought-provoking prompts based on their preferred style.
    """
    ACTIONS = """
    - Analyze the user's mood and medium.
    - Provide three distinct 'vibe' options: Experimental, Classical, or Abstract.
    - Suggest specific color palettes and techniques.
    """
    INFORMATION = "Respect any [REDACTED] tags; focus on the creative essence, not private data."
    LANGUAGE = "Respond in a supportive, poetic, yet professional tone."

    return f"{GOALS}\n{ACTIONS}\n{INFORMATION}\n{LANGUAGE}"

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

# 4. HEALTH CHECK (Prevents 404 leakage and verifies server status)
@app.get("/")
async def health():
    return {"status": "Art Agent Active", "privacy": "Enabled"}

# 5. MAIN CHAT ENDPOINT
@app.post("/chat")
async def process_chat(request: ChatRequest):
    # Deferred Import: Keeps RAM low until a request is actually made
    from openai import OpenAI

    # Redact sensitive data before it ever hits the API
    safe_input = redact_pii(request.message)

    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        return {"error": "API Key not configured"}

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    system_prompt = get_art_system_prompt()
    messages = [{"role": "system", "content": system_prompt}] + request.history
    messages.append({"role": "user", "content": safe_input})

    try:
        # Using DeepSeek-Reasoner for "Thinking" capabilities
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages
        )

        reply = response.choices[0].message.content

        # 6. MEMORY MANAGEMENT (GARBAGE COLLECTION)
        # Explicitly delete large objects and force a cleanup
        del messages
        del safe_input
        gc.collect()

        return {"reply": reply}

    except Exception as e:
        gc.collect()
        return {"reply": f"Art Agent encountered a hiccup: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    # High performance uvicorn deployment
    uvicorn.run(app, host="0.0.0.0", port=5000)