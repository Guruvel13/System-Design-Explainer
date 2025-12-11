# llm_client.py
import os
from typing import Optional
from groq import Groq

SYSTEM_PROMPT = """
You are a senior system architect.

You MUST output ONLY the following two sections, in this exact order:

[EXPLANATION]
Plain text only. No markdown (#, *, -, =). No lists. No arrows. 
Use simple section titles like:
Problem Summary
Architecture Overview
Components
Data Flow
Scaling
Storage
Security
Monitoring
Tech Stack

NO markdown formatting allowed.
NO symbols like →, —, ###, **.
Short sentences only.

Next section:

[DIAGRAM_JSON]
STRICT VALID JSON ONLY. NO COMMENTS.

JSON RULES:
- Use double quotes only.
- Commas required between items.
- No trailing commas.
- No semicolons.
- No extra text after JSON.
- No markdown formatting.
- No arrows like → inside JSON.

The JSON MUST match this shape EXACTLY:

{
  "nodes": ["A", "B"],
  "edges": [["A", "B"]],
  "annotations": { "A": "desc", "B": "desc" },
  "layers": {
    "frontend": [],
    "backend": [],
    "data": [],
    "infrastructure": []
  },
  "edge_types": { "A->B": "HTTP" }
}

ANNOTATION RULE:
- Each description must be <= 10 words.

EDGES RULE:
- Edge keys MUST follow exact format: "Source->Target"

Ensure JSON is VALID and PARSEABLE.
"""

def call_llm(requirement: str, model_name: str = "llama-3.1-8b-instant") -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY missing in Streamlit Secrets.")

    client = Groq(api_key=api_key)

    prompt = f"{SYSTEM_PROMPT}\n\nUSER REQUIREMENT:\n{requirement}"

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1400,
            top_p=0.9
        )

        choice = completion.choices[0]
        msg = choice.message

        # Safely extract message across all SDK variations
        if hasattr(msg, "content"):
            return msg.content.strip()
        if isinstance(msg, dict):
            return msg.get("content", "").strip()
        if hasattr(choice, "text"):
            return choice.text.strip()

        return str(choice).strip()

    except Exception as e:
        raise RuntimeError(f"GROQ API ERROR: {e}")
