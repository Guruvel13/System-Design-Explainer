# llm_client.py
# Stable Groq Llama client for SystemSketch AI — production-ready

import os
from typing import Optional
from groq import Groq

SYSTEM_PROMPT = """
You are a senior system architect.
Your output MUST contain EXACTLY TWO SECTIONS and NOTHING ELSE.

[EXPLANATION]
Write a clear, structured, highly detailed system design (max ~700 words).
Use plain headings, short paragraphs, simple lists. No code blocks. No decorative separators.

Mandatory subsections:
1) Problem Summary
2) Functional Breakdown
3) Non-Functional Impact
4) High-Level Architecture (justification)
5) Layered Architecture View
6) Step-by-Step Data Flow (use → arrows)
7) Component Responsibilities
8) Detailed Diagram Explanation (explain EVERY node + EVERY edge)
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

[DIAGRAM_JSON]
Return STRICT VALID JSON ONLY (only JSON, nothing else). Must include:
nodes, edges, annotations, layers, edge_types.
3-12 components. Annotations <=10 words per node.
Output must end immediately after the closing brace.
"""

def call_llm(requirement: str, model_name: Optional[str] = "llama-3.1-8b-instant") -> str:
    """
    Sends SYSTEM_PROMPT + requirement to Groq and returns assistant content.
    Defensive across Groq SDK versions.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY missing. Add in Streamlit Secrets: GROQ_API_KEY = \"gsk_your_key\""
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

    # Try common response shapes
    try:
        if hasattr(choice, "message") and hasattr(choice.message, "content"):
            return str(choice.message.content).strip()
    except Exception:
        pass

    if hasattr(choice, "message") and isinstance(choice.message, dict):
        msg = choice.message
        content = msg.get("content") or msg.get("text")
        if content:
            return str(content).strip()

    if hasattr(choice, "text") and isinstance(choice.text, str):
        return choice.text.strip()

    return str(choice).strip()
