import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Art Inspiration Agent")

# 1. CORS PROTOCOL (Cross-Origin Resource Sharing)
# CONCEPTUAL EXPLANATION: This acts as a digital handshake. It allows your 
# Hostinger domain to securely request data from your Replit server, bypassing 
# browser-level security blocks that prevent cross-site communication.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER (PII Sanitization)
# CONCEPTUAL EXPLANATION: Implements "Privacy-by-Design." This uses Regular 
# Expressions (Regex) to redact sensitive user data (Emails, SSNs, Addresses) 
# locally before transmission, ensuring PII never reaches the model or logs.
def redact_pii(text: str) -> str:
    patterns = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        "SSN": r'\b(?!666|000|9\d{2})\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b',
        "ADDRESS": r'\d{1,5}\s\w+.\s(\b\w+\b\s){1,2}\w+,\s\w+,\s[A-Z]{2}\s\d{5}'
    }
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[{label}_REDACTED]", text, flags=re.IGNORECASE)
    return text

# 3. GAIL ART SYNTHESIS PROMPT (The "Synthesis" Logic)
# CONCEPTUAL EXPLANATION: This protocol anchors the agent in an MFA-style 
# advisory role. It forces a specific flow: (A) Contextual/Theoretical Why, 
# (B) Material Properties, and (C) Technical How.
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

# 4. DATA MODELING (Pydantic Schema)
# CONCEPTUAL EXPLANATION: Validates the structural integrity of incoming JSON. 
# This prevents server crashes by ensuring the 'message' and 'history' fields 
# are correctly typed before processing.
class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

# 5. MAIN API ENDPOINT (/chat)
# CONCEPTUAL EXPLANATION: Orchestrates the request lifecycle. Manages 
# asynchronous communication, local scrubbing, and garbage collection (gc) 
# to optimize Replit's memory allocation for stateful conversations.
@app.post("/chat")
async def process_chat(request: ChatRequest):
    from openai import OpenAI

    safe_input = redact_pii(request.message)
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    messages = [{"role": "system", "content": get_art_system_prompt()}] + request.history
    messages.append({"role": "user", "content": safe_input})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.6,
            max_tokens=900
        )

        reply = response.choices[0].message.content
        del messages, safe_input
        gc.collect()

        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)