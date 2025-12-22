import os
import re
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Art Inspiration Agent")

# 1. CORS CONFIGURATION (Essential for Replit to Hostinger communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PRIVACY SCRUBBER (Redacts PII, SSNs, and Physical Addresses)
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

# 3. INTEGRATED GAIL FRAMEWORK (With Diversity & Originality Protocols)
def get_art_system_prompt():
    """
    GOALS: Empower artists to overcome blocks with sophisticated, high-concept prompts.
    ACTIONS: 
        - Provide three 'vibes': Experimental, Classical, or Abstract.
        - DIVERSITY PROTOCOL: Actively pull inspiration from non-Western canons 
          (e.g., Islamic geometry, Indigenous patterns, or African futurism).
        - ORIGINALITY PROTOCOL: Avoid overused cliches; prioritize sensory 
          descriptions (textures/smells) to drive visual imagination.
    INFORMATION: 
        - Reference global art history and technical terminology (Sfumato, Impasto).
        - Respect [REDACTED] placeholders; focus on the artistic essence.
    LANGUAGE: Poetic, encouraging, intellectually sophisticated, and non-judgmental.
    """
    return (
        "You are an Expert Art Consultant and Historian.\n\n"
        "GOALS:\n"
        "Help the artist navigate creative exhaustion by providing rigorous and diverse inspiration.\n\n"
        "ACTIONS (ORIGINALITY & DIVERSITY PROTOCOL):\n"
        "1. Identify and bypass Western-centric cliches. Instead of 'Starry Nights,' "
        "suggest concepts based on 'Wabi-sabi' (the beauty of imperfection) or "
        "'Horror Vacui' (the fear of empty space).\n"
        "2. Synthesis: Combine two unrelated concepts (e.g., 'Biomorphic architecture' "
        "meets 'Byzantine gold-leaf techniques').\n"
        "3. Cross-Sensory Prompts: Describe a scent or a sound and ask the artist to "
        "render it as a texture.\n\n"
        "INFORMATION & LANGUAGE:\n"
        "Use precise historical terminology. Maintain an inspiring yet academic tone. "
        "If you encounter [REDACTED], treat it as a 'mysterious void' that adds to the art."
    )

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

# 4. HEALTH CHECK (Verifies server status and privacy layers)
@app.get("/")
async def health():
    return {
        "status": "Art Consultant Agent Online", 
        "framework": "GAIL + Originality Protocol",
        "privacy": "Full-Scrub-Active"
    }

# 5. MAIN CHAT ENDPOINT
@app.post("/chat")
async def process_chat(request: ChatRequest):
    # DEFERRED IMPORT: Minimizes RAM usage during idle time
    from openai import OpenAI

    # Redact input locally
    safe_input = redact_pii(request.message)

    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        return {"error": "DeepSeek API Key missing in Replit Secrets."}

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    # Construct message chain for DeepSeek-V3
    messages = [{"role": "system", "content": get_art_system_prompt()}] + request.history
    messages.append({"role": "user", "content": safe_input})

    try:
        # Utilizing DeepSeek-V3 for creative prose and artistic synthesis
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )

        reply = response.choices[0].message.content

        # 6. MEMORY MANAGEMENT (GARBAGE COLLECTION)
        del messages, safe_input
        gc.collect()

        return {"reply": reply}
    except Exception as e:
        gc.collect()
        return {"error": f"Creative process interrupted: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    # Optimized run for Replit
    uvicorn.run(app, host="0.0.0.0", port=5000)