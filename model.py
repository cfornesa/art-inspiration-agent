"""
model.py - Core logic for the Art Inspiration Agent.

Contains PII redaction, user preference context building, and the main
chat generation function. Uses the Mistral SDK beta conversations API
with a La Plateforme agent_id. Imported by main.py.
"""

import os
import re
import gc
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

PII_PATTERNS = {
    "EMAIL":   re.compile(r'[\w\.-]+@[\w\.-]+\.\w+', re.IGNORECASE),
    "PHONE":   re.compile(r'\+?\d{1,4}?[-.\\s]?\(?\d{1,3}?\)?[-.\\s]?\d{1,4}[-.\\s]?\d{1,4}[-.\\s]?\d{1,9}'),
    "SSN":     re.compile(r'\b(?!666|000|9\d{2})\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b'),
    "ADDRESS": re.compile(r'\d{1,5}\s\w+.\s(\b\w+\b\s){1,2}\w+,\s\w+,\s[A-Z]{2}\s\d{5}', re.IGNORECASE),
}


def redact_pii(text: str) -> str:
    for label, pattern in PII_PATTERNS.items():
        text = pattern.sub(f"[{label}_REDACTED]", text)
    return text


def strip_markdown(text: str) -> str:
    """
    Strip markdown formatting from agent responses for clean plain-text display.

    Removes headers, bold/italic, underline, normalizes unicode dashes to
    hyphens, strips emoji blocks, and collapses excess blank lines.
    """
    text = re.sub(r'#{1,6}\s*', '', text)                    # headers
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)    # bold/italic
    text = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', text)      # underline
    text = re.sub(r'[\u2013\u2014]', '-', text)              # normalize unicode dashes
    text = re.sub(r'[\U00002600-\U000027BF]', '', text)      # common symbols/emoji
    text = re.sub(r'[\U0001F000-\U0001FFFF]', '', text)      # extended emoji
    text = re.sub(r'\n{3,}', '\n\n', text)                   # collapse excess blank lines
    return text.strip()


def build_preference_context(preferences: Optional[Dict] = None) -> str:
    if not preferences:
        return ""

    lines = ["USER PREFERENCES (apply to this and all subsequent responses):"]

    if preferences.get("style"):
        lines.append(f"- Artistic Style: Prioritize {preferences['style']} aesthetics and historical references.")
    if preferences.get("medium"):
        lines.append(f"- Medium Focus: Tailor all technical advice specifically to {preferences['medium']}.")
    if preferences.get("skill_level"):
        level = preferences["skill_level"].lower()
        if level == "beginner":
            lines.append("- Skill Level: Use accessible language; avoid jargon; explain fundamentals first.")
        elif level == "intermediate":
            lines.append("- Skill Level: Assume foundational knowledge; introduce nuanced techniques.")
        elif level == "advanced":
            lines.append("- Skill Level: Use professional terminology; focus on refinement and mastery.")
        else:
            lines.append(f"- Skill Level: Calibrate for a {preferences['skill_level']} practitioner.")
    if preferences.get("focus"):
        lines.append(f"- Topic Focus: Emphasize {preferences['focus']} in both conceptual and technical guidance.")

    return "\n".join(lines) if len(lines) > 1 else ""


def generate_response(
    user_input: str,
    history: List[Dict],
    preferences: Optional[Dict] = None,
) -> Dict:
    from mistralai import Mistral

    safe_input = redact_pii(user_input)
    api_key  = os.environ.get("MISTRAL_API_KEY")
    agent_id = os.environ.get("AGENT_ID")

    if not api_key:
        return {"reply": "Error: MISTRAL_API_KEY not configured."}
    if not agent_id:
        return {"reply": "Error: AGENT_ID not configured."}

    client = Mistral(api_key=api_key)

    preference_context = build_preference_context(preferences)
    user_content = (
        f"{preference_context}\n\n{safe_input}"
        if preference_context
        else safe_input
    )

    inputs = history + [{"role": "user", "content": user_content}]

    try:
        response = client.beta.conversations.start(
            agent_id=agent_id, 
            agent_version="latest", 
            inputs=inputs,
        )

        reply_text = ""
        for output in response.outputs:
            if hasattr(output, "role") and output.role == "assistant":
                content = output.content
                reply_text = content[0].text if isinstance(content, list) else content
                break

        if not reply_text:
            return {"reply": "Error: Empty response from agent."}

        gc.collect()
        return {"reply": strip_markdown(reply_text), "metadata": {"status": "success"}}

    except Exception as e:
        gc.collect()
        return {"reply": f"System Error: {str(e)}"}
