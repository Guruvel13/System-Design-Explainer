# llm_client.py
import os
from typing import Optional
from groq import Groq

SYSTEM_PROMPT = """
You are a senior system architect with expert-level experience designing fault-tolerant, highly scalable distributed systems.

Your output MUST contain ONLY the two sections shown below.  
Write clearly, visually, and with a strong architectural mindset.

==================================================
[EXPLANATION]
==================================================
Produce a deeply detailed yet concise system design (max ~650 words).  
Your explanation MUST be extremely clear, structured, and easy to understand even for beginners.

Write using **visual-friendly formatting**, including:
- Descriptive headings
- Mini-sections with short paragraphs
- Bullet points
- Layer-based explanations
- Arrows (→) to show flow
- Real-world system analogies where useful

(… explanation prompt continues …)

==================================================
[DIAGRAM_JSON]
==================================================
Return STRICT VALID JSON describing the architecture:

{
  "nodes": ["ComponentA", "ComponentB"],
  "edges": [
    ["ComponentA", "ComponentB"]
  ],
  "annotations": {
    "ComponentA": "Short description",
    "ComponentB": "Short description"
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

JSON RULES:
- MUST include nodes, edges, annotations, layers, edge_types
- MUST be valid JSON
- No trailing commas or comments
- No text after JSON block
- 2–12 components only
"""



def call_llm(requirement: str, model_name: Optional[str] = "llama-3.1-8b-instant") -> str:
    """
    Calls the Groq API and returns ONLY the model response text.
    Handles all message formats safely across Groq SDK versions.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY missing. Add it in Streamlit Secrets:\n"
            'GROQ_API_KEY="gsk_your_key_here"'
        )

    client = Groq(api_key=api_key)
    prompt = f"{SYSTEM_PROMPT}\n\nUSER REQUIREMENT:\n{requirement}"

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.15,
            max_tokens=1200,
            top_p=0.9
        )

        choice = completion.choices[0]

        # -------- SAFE CONTENT EXTRACTION -------- #
        if hasattr(choice, "message"):
            msg = choice.message

            # Case 1: message is pure string
            if isinstance(msg, str):
                return msg.strip()

            # Case 2: new Groq API → message.content
            if hasattr(msg, "content"):
                return msg.content.strip()

            # Case 3: unknown object → convert to string
            return str(msg).strip()

        # Older fallback API style
        if hasattr(choice, "text"):
            return choice.text.strip()

        return str(choice).strip()

    except Exception as e:
        raise RuntimeError(f"GROQ API ERROR: {e}")
