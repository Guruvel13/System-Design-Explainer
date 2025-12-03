import os
from groq import Groq

SYSTEM_PROMPT = """
You are a senior system architect.

Always respond in EXACTLY this format:

[EXPLANATION]
<architecture explanation>

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
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY in Streamlit Secrets.")

    client = Groq(api_key=api_key)

    prompt = f"{SYSTEM_PROMPT}\nUser requirement:\n{requirement}"

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # ← ✔ CORRECT MODEL
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        return completion.choices[0].message.content

    except Exception as e:
        raise RuntimeError(f"GROQ API ERROR: {str(e)}")
