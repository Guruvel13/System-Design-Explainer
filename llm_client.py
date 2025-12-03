# llm_client.py  (USE GROQ — completely free)
import os
from groq import Groq

# Load Groq API Key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a senior system architect.

Always respond in EXACTLY this format:

[EXPLANATION]
<bullet point architecture breakdown>

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
    """Call Llama-3-8B via Groq API."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to Streamlit Secrets.")

    prompt = f"{SYSTEM_PROMPT}\nUser requirement:\n{requirement}"

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=800
    )

    return completion.choices[0].message.content
