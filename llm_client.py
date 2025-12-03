# llm_client.py (Streamlit Cloud + Groq) — FIXED & STABLE
import os
from groq import Groq

SYSTEM_PROMPT = """
You are a senior system architect.

Always respond in EXACTLY this format:

[EXPLANATION]
<final architecture explanation>

[DIAGRAM_JSON]
{
  "nodes": ["Component1","Component2"],
  "edges": [
    ["Component1","Component2"]
  ]
}

Do NOT add anything after the JSON.
"""


def call_llm(requirement: str) -> str:
    """Send prompt to Groq Llama-3-8B-eng safely."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "ERROR: GROQ_API_KEY is missing.\n\n"
            "Add it in Streamlit Cloud → Settings → Secrets:\n"
            'GROQ_API_KEY = "gsk_your_key_here"'
        )

    # Create Groq client only AFTER key exists
    client = Groq(api_key=api_key)

    prompt = f"{SYSTEM_PROMPT}\nUser requirement:\n{requirement}"

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-eng",   # free + supported model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )

        return completion.choices[0].message.content

    except Exception as e:
        raise RuntimeError(f"GROQ API ERROR: {str(e)}")
