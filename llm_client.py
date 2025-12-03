import os
from groq import Groq

SYSTEM_PROMPT = """
You are a senior system architect with 15+ years designing large-scale distributed systems.

Your job is to produce:
1. A clear, structured architecture explanation (max 650 words)
2. A clean and accurate DIAGRAM_JSON block

Follow the exact format below:

[EXPLANATION]
Provide a detailed but concise system design including:
- Problem summary
- Key components
- High-level architecture
- Step-by-step data flow
- Scalability considerations
- Database/storage strategy
- Caching strategy
- Load balancing approach
- Security mechanisms
- Fault tolerance
- Monitoring + observability
- Trade-offs
- Technology suggestions

Use short paragraphs and bullet points only.

[DIAGRAM_JSON]
Return a strict JSON object:
{
  "nodes": ["ComponentA", "ComponentB"],
  "edges": [
    ["ComponentA", "ComponentB"]
  ]
}

Rules:
- JSON must be valid
- No comments
- No trailing commas
- Never include explanation inside the JSON
- Do NOT add anything after the JSON
"""


def call_llm(requirement: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY in Streamlit Secrets.")

    client = Groq(api_key=api_key)

    prompt = f"{SYSTEM_PROMPT}\n\nUser requirement:\n{requirement}"

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # free + fast + detailed
            messages=[{"role": "user", "content": prompt}],
            temperature=0.18,              # accurate & structured
            max_tokens=1200,               # ✔ under limit, rich detail
            top_p=0.9
        )
        return completion.choices[0].message.content

    except Exception as e:
        raise RuntimeError(f"GROQ API ERROR: {str(e)}")
