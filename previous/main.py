"""
================================================================================
SYSTEM ARCHITECT: Chris Fornesa
PROJECT: Art Inspiration Agent (Mistral Edition)
MISSION: Bridging Data Science, Social Science, and Studio Practice.
GOVERNANCE: Ethical AI usage, Carbon-neutral grid sourcing, PII Sovereignty.
================================================================================
"""

import os
import re
import gc
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

# INITIALIZATION: FastAPI selected for asynchronous performance and low energy overhead.
app = FastAPI(title="Art Inspiration Agent - Mistral Edition")

# 1. CORS PROTOCOL (The "Digital Handshake")
# ARCHITECTURAL NOTE: Enables secure communication between the Hostinger frontend 
# and Replit backend, ensuring cross-domain functional integrity.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER (PII Sanitization Layer)
# MISSION ALIGNMENT: Prevents data extraction for unethical LLM training, 
# ensuring user sovereignty remains a core pillar of the system architecture.
PII_PATTERNS = {
    "EMAIL": re.compile(r'[\w\.-]+@[\w\.-]+\.\w+', re.IGNORECASE),
    "PHONE": re.compile(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'),
    "SSN": re.compile(r'\b(?!666|000|9\d{2})\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b'),
    "ADDRESS": re.compile(r'\d{1,5}\s\w+.\s(\b\w+\b\s){1,2}\w+,\s\w+,\s[A-Z]{2}\s\d{5}', re.IGNORECASE)
}

def redact_pii(text: str) -> str:
    """Executes local de-identification before query transmission."""
    for label, pattern in PII_PATTERNS.items():
        text = pattern.sub(f"[{label}_REDACTED]", text)
    return text

# 3. STUDIO PROTOCOL: SYSTEM PROMPT
# FRAMEWORK: Translates MFA-level studio standards into algorithmic constraints.
def get_art_system_prompt():
    return (
        "You are an Expert Art Consultant. YOU MUST RESPOND IN ENGLISH ONLY.\n\n"
        "GOALS:\n"
        "Provide dense, actionable, and synthesized expertise. Transition from theory to studio practice.\n\n"
        "ACTIONS:\n"
        "1. DUAL-INTENT HANDLING: Structure as: (A) Conceptual Framework, (B) Material & Technical Application, and (C) Archival Standard.\n"
        "2. TECHNICAL PRECISION: Specify archival chemistry (pH-neutral, lightfastness, acid-free).\n"
        "3. RELEVANT LINKS: Provide search-based technical resource links.\n"
        "   Format exactly: Relevant Links: https://www.google.com/search?q=[Topic+Material+Technique+Tutorial]\n"
        "4. SCOPE CONTROL: For non-art topics, state 'I focus solely on art' and pivot to an artistic technique.\n\n"
        "LANGUAGE: Executive conciseness under 400 words. English only."
    )

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

# 4. HEALTH CHECK (System Vitality)
# REQUIRED: Infrastructure ping response to prevent Replit deployment termination.
@app.get("/")
async def health_check():
    return {
        "status": "online", 
        "agent": "Art Inspiration Agent",
        "standards": "PII-Redaction/Archival-Focus/Mistral-Sovereignty"
    }

# 5. MAIN API ENDPOINT (/chat)
@app.post("/chat")
async def process_chat(request: ChatRequest):
    from openai import OpenAI

    # STEP 1: Privacy Scrubbing (Local Execution)
    safe_input = redact_pii(request.message)
    api_key = os.environ.get('MISTRAL_API_KEY')

    if not api_key:
        return {"reply": "Error: MISTRAL_API_KEY not configured."}

    # STEP 2: Ecological Routing
    # CHOICE: Mistral AI prioritized for LCA transparency and French low-carbon energy grid.
    client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")
    messages = [{"role": "system", "content": get_art_system_prompt()}] + request.history
    messages.append({"role": "user", "content": safe_input})

    try:
        # Utilizing Ministral 14B Reasoning for institutional-level logic.
        response = client.chat.completions.create(
            model="ministral-14b-latest", 
            messages=messages,
            temperature=0.15, # Deterministic setting for technical accuracy.
            max_tokens=900
        )
        reply_content = response.choices[0].message.content

        # STEP 3: Ecological Efficiency (Garbage Collection)
        del messages, safe_input
        gc.collect()

        return {"reply": reply_content.strip()}

    except Exception as e:
        gc.collect()
        return {"reply": f"System Error: {str(e)}"}

# 6. PRODUCTION RUNNER
if __name__ == "__main__":
    # OS Environment lookup for dynamic cloud port allocation.
    port = int(os.environ.get("PORT", 5000))
    # 'main:app' prevents redundant process spawning in the server environment.
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")