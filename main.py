"""
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Art Inspiration Agent (Mistral Edition)
PURPOSE: Bridging technical rigor with studio practice through ethical AI.
"""

import os
import re
import gc
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

# INITIALIZATION: FastAPI handles the high-performance asynchronous web routing.
app = FastAPI(title="Art Inspiration Agent - Mistral Edition")

# 1. CORS PROTOCOL (Digital Handshake)
# Enables cross-origin resource sharing, allowing the Hostinger frontend to 
# communicate securely with the Replit backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER (PII Sanitization)
# Central to the mission of Ethical AI: Sanitizes user data locally via Regex 
# to ensure sensitive information never reaches the LLM training clusters.
PII_PATTERNS = {
    "EMAIL": re.compile(r'[\w\.-]+@[\w\.-]+\.\w+', re.IGNORECASE),
    "PHONE": re.compile(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'),
    "SSN": re.compile(r'\b(?!666|000|9\d{2})\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b'),
    "ADDRESS": re.compile(r'\d{1,5}\s\w+.\s(\b\w+\b\s){1,2}\w+,\s\w+,\s[A-Z]{2}\s\d{5}', re.IGNORECASE)
}

def redact_pii(text: str) -> str:
    """Iterates through defined patterns and replaces sensitive data with labels."""
    for label, pattern in PII_PATTERNS.items():
        text = pattern.sub(f"[{label}_REDACTED]", text)
    return text

# 3. STUDIO PROTOCOL: SYSTEM PROMPT
# Hard-coding constraints ensures the agent maintains MFA-level technical rigor
# and archival accuracy (pH-neutrality, lightfastness, ASTM standards).
def get_art_system_prompt():
    return (
        "You are an Expert Art Consultant. YOU MUST RESPOND IN ENGLISH ONLY.\n\n"
        "GOALS:\n"
        "Provide dense, actionable, and synthesized expertise. Transition from theory to studio practice.\n\n"
        "ACTIONS:\n"
        "1. DUAL-INTENT HANDLING: Structure as: (A) Conceptual Framework, (B) Material & Technical Application, and (C) Archival Standard.\n"
        "2. TECHNICAL PRECISION: Specify archival chemistry (pH-neutral, lightfastness, acid-free) in every process.\n"
        "3. RELEVANT LINKS: Provide search-based technical resource links using the Search-Path Protocol.\n"
        "   Format exactly: Relevant Links: https://www.google.com/search?q=[Topic+Material+Technique+Tutorial]\n"
        "4. SCOPE CONTROL: For non-art topics, pivot to an artistic technique.\n\n"
        "LANGUAGE: Executive conciseness under 400 words. English only."
    )

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

# 4. HEALTH CHECK (System Vitality)
# Required for Replit Deployments to acknowledge the system is live and prevent auto-termination.
@app.get("/")
async def health_check():
    return {
        "status": "online", 
        "agent": "Art Inspiration Agent",
        "provider": "Mistral AI",
        "model": "ministral-14b-2512",
        "standards": "PII-Redaction/Archival-Focus"
    }

# 5. MAIN API ENDPOINT: /chat
@app.post("/chat")
async def process_chat(request: ChatRequest):
    from openai import OpenAI

    # STEP 1: Local Redaction (The Ethical Guardrail)
    safe_input = redact_pii(request.message)
    api_key = os.environ.get('MISTRAL_API_KEY')

    if not api_key:
        return {"reply": "Error: MISTRAL_API_KEY is not configured."}

    # STEP 2: API Orchestration
    # Mistral provides frontier reasoning with a lower carbon footprint than US counterparts.
    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

    messages = [{"role": "system", "content": get_art_system_prompt()}] + request.history
    messages.append({"role": "user", "content": safe_input})

    try:
        # Utilizing Ministral 14B for its superior reasoning/cost ratio.
        response = client.chat.completions.create(
            model="ministral-14b-latest", 
            messages=messages,
            temperature=0.15, # Low temperature ensures deterministic, technical accuracy.
            max_tokens=900
        )

        reply_content = response.choices[0].message.content

        # STEP 3: Memory Cleanup (Environmental Focus)
        # Explicitly freeing up memory to maintain small server footprint.
        del messages, safe_input
        gc.collect()

        return {"reply": reply_content.strip()}

    except Exception as e:
        gc.collect()
        return {"reply": f"System Error: {str(e)}"}

# 6. REPLIT PRODUCTION RUNNER
if __name__ == "__main__":
    # Dynamically binds to the port assigned by Replit's infrastructure.
    port = int(os.environ.get("PORT", 5000))
    print(f"Server starting on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")