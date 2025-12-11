# llm_client.py
# Stable Groq Llama client for SystemSketch AI — fully fixed, production-ready

import os
from typing import Optional
from groq import Groq


SYSTEM_PROMPT = """
You are a senior system architect.  
Your output MUST contain EXACTLY TWO SECTIONS and NOTHING ELSE.

==================================================
[EXPLANATION]
==================================================
Write a clear, structured, highly detailed system design (max ~700 words).

Format rules:
- Use plain headings (no markdown syntax like ###, **, or code blocks).
- Use short paragraphs and simple lists.
- Do NOT output separators like ==== or code fences.
- Only ONE explanation section.

Required subsections:
1) Problem Summary
2) Functional Breakdown
3) Non-Functional Impact
4) High-Level Architecture (justification required)
5) Layered Architecture View
6) Step-by-Step Data Flow (use → arrows)
7) Component Responsibilities
8) Detailed Diagram Explanation (each node + each edge explained)
9) Scalability & Partitioning
10) Storage Strategy
11) Caching Strategy
12) Load Balancing & Traffic Management
13) Security & Compliance
14) Fault Tolerance & Recovery
15) Observability & SLOs
16) Deployment & DevOps
17) Trade-offs & Alternatives
18) Recommended Tech Stack

==================================================
[DIAGRAM_JSON]
==================================================
Return STRICT VALID JSON ONLY.  
No explanation, no comments, no trailing commas, no text after JSON.

JSON MUST follow this schema:

{
  "nodes": ["A", "B"],
  "edges": [["A", "B"]],
  "annotations": {
    "A": "Short description",
    "B": "Short description"
  },
  "layers": {
    "frontend": ["Browser", "Mobile App"],
    "backend": ["API Gateway", "Auth Service"],
    "data": ["DB", "Cache"],
    "infrastructure": ["Load Balancer", "Monitoring"]
  },
  "edge_types": {
    "A->B": "HTTP"
  }
}

STRICT RULES:
- JSON must be valid.
- 3–12 components.
- Annotation text ≤ 10 words.
- Edges must match the explanation.
- Output MUST end immediately after the closing curly brace.
"""


def call_llm(requirement: str, model_name: Optional[str] = "llama-3.1-8b-instant") -> str:
    """
    Sends the SYSTEM_PROMPT + USER REQUIREMENT to Groq and returns clean output.
    Fully defensive across all Groq SDK variations.
    """

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY missing. Add inside Streamlit Secrets:\n"
            'GROQ_API_KEY = "gsk_your_real_key_here"\n'
        )

    client = Groq(api_key=api_key)

    prompt = f"{SYSTEM_PROMPT}\n\nUSER REQUIREMENT:\n{requirement}"

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.15,
            max_tokens=1400,
            top_p=0.9
        )
    except Exception as e:
        raise RuntimeError(f"GROQ API request failed: {e}")

    if not getattr(completion, "choices", None):
        raise RuntimeError("Groq API returned no choices.")

    choice = completion.choices[0]

    # PRIMARY: Modern SDK → choice.message.content
    if hasattr(choice, "message") and hasattr(choice.message, "content"):
        return str(choice.message.content).strip()

    # SECONDARY: some SDKs return message as dict
    if hasattr(choice, "message") and isinstance(choice.message, dict):
        msg = choice.message
        content = msg.get("content") or msg.get("text")
        if content:
            return str(content).strip()

    # TERTIARY: older `.text` models
    if hasattr(choice, "text") and isinstance(choice.text, str):
        return choice.text.strip()

    # FINAL fallback
    return str(choice).strip()
