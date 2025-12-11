# llm_client.py (FINAL FIXED VERSION)
import os
from typing import Optional
from groq import Groq

SYSTEM_PROMPT = """
You are a senior system architect. 
You MUST output ONLY TWO SECTIONS in this exact order:

[EXPLANATION]
(Plain text explanation. No markdown headings. No ###, no **bold**, no = lines.)

Keep it simple:
- Title: Problem Summary
- Title: Architecture Overview
- Title: Components
- Title: Data Flow
- Title: Scaling
- Title: Storage
- Title: Security
- Title: Fault Tolerance
- Title: Monitoring
- Title: Tech Stack

NO other formatting. NO markdown. NO symbols.

Then output section #2:

[DIAGRAM_JSON]
Strict JSON with these EXACT fields:

{
  "nodes": ["A","B"],
  "edges": [["A","B"]],
  "annotations": {"A":"desc", "B":"desc"},
  "layers": {
    "frontend": [],
    "backend": [],
    "data": [],
    "infrastructure": []
  },
  "edge_types": {
    "A->B": "HTTP"
  }
}

RULES:
- JSON ONLY. No comments.
- No trailing commas.
- No extra text after JSON.
- annotation descriptions <= 10 words.
- Only real components referenced in explanation.
"""

def call_llm(requirement: str, model_name: Optional[str] = "llama-3.1-8b-instant") -> str:

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY in Streamlit Secrets")

    client = Groq(api_key=api_key)

    prompt = f"{SYSTEM_PROMPT}\n\nUSER REQUIREMENT:\n{requirement}"

    try:
        result = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.10,
            max_tokens=1200,
        )

        choice = result.choices[0]

        # Safe extraction across SDKs
        if hasattr(choice, "message") and hasattr(choice.message, "content"):
            return choice.message.content.strip()

        if hasattr(choice, "message") and isinstance(choice.message, dict):
            return choice.message.get("content", "").strip()

        if hasattr(choice, "text"):
            return choice.text.strip()

        return str(choice).strip()

    except Exception as e:
        raise RuntimeError(f"GROQ API ERROR: {str(e)}")
