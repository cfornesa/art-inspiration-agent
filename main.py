import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Art Inspiration Agent - Mistral Edition")

# 1. CORS PROTOCOL (Digital Handshake)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER (PII Sanitization)
PII_PATTERNS = {
    "EMAIL": re.compile(r'[\w\.-]+@[\w\.-]+\.\w+', re.IGNORECASE),
    "PHONE": re.compile(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'),
    "SSN": re.compile(r'\b(?!666|000|9\d{2})\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b'),
    "ADDRESS": re.compile(r'\d{1,5}\s\w+.\s(\b\w+\b\s){1,2}\w+,\s\w+,\s[A-Z]{2}\s\d{5}', re.IGNORECASE)
}

def redact_pii(text: str) -> str:
    for label, pattern in PII_PATTERNS.items():
        text = pattern.sub(f"[{label}_REDACTED]", text)
    return text

# 3. GAIL ART SYNTHESIS PROMPT
def get_art_system_prompt():
    return (
        "You are an Expert Art Consultant. YOU MUST RESPOND IN ENGLISH ONLY.\n\n"
        "GOALS:\n"
        "Provide dense, actionable, and synthesized expertise. Transition from theory to studio practice.\n\n"
        "ACTIONS:\n"
        "1. DUAL-INTENT HANDLING: Structure as: (A) Conceptual Framework, (B) Material & Technical Application, and (C) Archival Standard.\n"
        "2. TECHNICAL PRECISION: Specify archival chemistry (pH-neutral, lightfastness, acid-free) in every process.\n"
        "3. RELEVANT LINKS: At the end of every response, provide a search-based technical resource link.\n"
        "   Format exactly: Relevant Links: https://www.google.com/search?q=[Topic+Material+Technique+Tutorial]\n"
        "4. SCOPE CONTROL: For non-art topics, state 'I focus solely on art' and pivot to an artistic technique.\n\n"
        "LANGUAGE:\n"
        "EXECUTIVE CONCISCENESS. Keep responses high-density and under 400 words. STRICTLY ENGLISH ONLY."
    )

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

# --- UPDATED: HEALTH CHECK ROUTE ---
@app.get("/")
async def health_check():
    return {
        "status": "online", 
        "agent": "Art Inspiration Agent",
        "system_version": "1.1.0",
        "provider": "Mistral AI",
        "model": "ministral-14b-reasoning-2512"
    }

# 4. MAIN API ENDPOINT (/chat)
@app.post("/chat")
async def process_chat(request: ChatRequest):
    from openai import OpenAI

    safe_input = redact_pii(request.message)
    # Ensure you set MISTRAL_API_KEY in your Replit/Environment Secrets
    api_key = os.environ.get('MISTRAL_API_KEY')

    if not api_key:
        return {"error": "Mistral API Key missing in environment variables."}

    # Mistral's API is OpenAI-compatible. Use the standard v1 endpoint.
    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

    messages = [{"role": "system", "content": get_art_system_prompt()}] + request.history
    messages.append({"role": "user", "content": safe_input})

    try:
        response = client.chat.completions.create(
            # Using the 14B Reasoning model for high-integrity studio advice
            model="ministral-14b-reasoning-2512",
            messages=messages,
            temperature=0.15, # Lower temperature for higher technical precision
            max_tokens=900
        )

        reply = response.choices[0].message.content

        # Explicit memory cleanup
        del messages, safe_input
        gc.collect()

        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)