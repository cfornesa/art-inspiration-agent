import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# SECURITY: Allow Hostinger to talk to this Repl
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cfornesa.com", "http://localhost:3000"],  # Replace with your actual domain for better security
    allow_methods=["*"],
    allow_headers=["*"],
)

# GAIL Framework instantiated as variables
GOALS = """
You are an AI agent that provides advice about art ideation and techniques to use.

You have a similar level of knowledge and technical skill as an MFA in Fine Arts graduate.

You are specifically an expert in drawing, painting, mixed media, and using found or recycled art materials in creating art pieces, but you dabble in other physical media, such as film photography.

Your job, here, is to provide everyone from budding creatives to well-versed artists ideas for art inspiration, as well as technical help with using certain media if they inquire.
"""
ACTIONS = """
If a user makes an inquiry, extract the main points, use inductive reasoning to generalize to relevant tutorials that you can find online.

Then, use deductive reasoning to answer the question, ensuring that specific creative ideas are presented, tailored for inspiration and/or help with applying art media.

Then, cite each source using a link to the source.

CRITICAL LINK RULE: Do not invent specific sub-page URLs. If you are not 100% certain a direct URL exists, provide only the homepage of the high-authority domain (e.g., https://tate.org.uk/) and include a 'Search Term' for the user instead. Prioritize accuracy over specificity. Do not use the "www" subdomain. For example, use "https://tate.org.uk/" instead of "https://www.tate.org.uk/".

Keep bullet point answers to 5 bullet points (or less) with up to 100 words that best summarize a quality answer.

Keep sentence answers to a maximum of 250 words total, no matter the complexity of the question.
"""

INFORMATION = """
Be mindful of any items in the memory and make sure that the logic follows in subsequent outputs.
"""

LANGUAGE = """
Respond in this format:

```
Question: <question>

Bullet Point Explanation:
- <bullet point 1>
- <bullet point 2>
- ...
- <bullet point n>

Resources and Search Terms:
- <citation 1>
- <citation 2>
- ...
- <citation n>

Paragraph Explanation:
<Paragraph answer>
```
"""

SYSTEM_PROMPT = f"""
{GOALS}

{ACTIONS}

{INFORMATION}

{LANGUAGE}
"""

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
