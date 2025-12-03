# llm_client.py
import os
from groq import Groq

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

Do NOT add text after the JSON.
"""


def call_llm(requirement: str) -> str:
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
