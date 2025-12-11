# llm_client.py
# Stable Groq Llama client for SystemSketch AI — fully fixed version

import os
from typing import Optional
from groq import Groq


SYSTEM_PROMPT = """
You are a senior system architect with expert-level experience designing fault-tolerant, highly scalable distributed systems.

Your output MUST contain ONLY the two sections shown below.

==================================================
[EXPLANATION]
==================================================
Provide a deeply detailed, highly practical system design (max ~700 words).
Write clearly, visually, and with strong architectural reasoning. Use headings, short paragraphs, and bullets.

Include the following subsections:
1) Problem Summary
2) Functional Breakdown
3) Non-Functional Impact
4) High-Level Architecture (with justification)
5) Layered Architecture View
6) Step-by-Step Data Flow (with arrows →)
7) Component Responsibilities
8) Detailed Diagram Explanation (every node + every edge explained)
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

Rules:
- No code.
- Keep paragraphs short.
- Use clear heading labels, not markdown symbols like ### or **.
- The Detailed Diagram Explanation MUST map each component and each edge to its purpose.

==================================================
[DIAGRAM_JSON]
==================================================
Return STRICT VALID JSON ONLY.

{
  "nodes": ["ComponentA", "ComponentB"],
  "edges": [["ComponentA", "ComponentB"]],
  "annotations": {
    "ComponentA": "Short description (<= 10 words)",
    "ComponentB": "Short description (<= 10 words)"
  },
  "layers": {
    "frontend": ["Browser", "Mobile App"],
    "backend": ["API Gateway", "Auth Service", "X Service"],
    "data": ["DB", "Cache"],
    "infrastructure": ["Load Balancer", "Monitoring"]
  },
  "edge_types": {
    "ComponentA->ComponentB": "HTTP",
    "ComponentB->ComponentC": "Async Event"
  }
}

STRICT RULES:
- JSON must be valid.
- No comments.
- No trailing commas.
- No text after JSON.
- 3–12 meaningful components.
- Annotation text <= 10 words.
- Edges must reflect the data flow described in the explanation.

Output must be exactly:
[EXPLANATION]
<text>
[DIAGRAM_JSON]
<json>
"""


def call_llm(requirement: str, model_name: Optional[str] = "llama-3.1-8b-instant") -> str:
    """
    Sends the SYSTEM_PROMPT + USER REQUIREMENT to Groq and returns clean assistant content.
    Fully compatible with all Groq SDK versions.
    """

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY missing. Add it in Streamlit Secrets:\n"
            'GROQ_API_KEY = "gsk_your_real_key_here"'
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

        # -------------------------------
        # UNIVERSAL SAFE CONTENT EXTRACTOR
        # -------------------------------
        choice = completion.choices[0]

        # Case 1: response.choice.message.content exists
        if hasattr(choice, "message") and hasattr(choice.message, "content"):
            return choice.message.content.strip()

        # Case 2: some Groq SDKs return message as dict
        if hasattr(choice, "message") and isinstance(choice.message, dict):
            msg = choice.message
            content = msg.get("content") or msg.get("text") or str(msg)
            return content.strip()

        # Case 3: fallback older `.text` attribute
        if hasattr(choice, "text"):
            return choice.text.strip()

        # Case 4: last fallback
        return str(choice).strip()

    except Exception as e:
        raise RuntimeError(f"GROQ API ERROR: {str(e)}")
