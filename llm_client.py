import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL_URL = os.getenv("HF_MODEL_URL")

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = """
You are a senior system architect.

Follow this exact response format:

[EXPLANATION]
<bullet points explaining architecture>

[DIAGRAM_JSON]
{
  "nodes": ["A", "B", "C"],
  "edges": [
     ["A", "B"],
     ["B", "C"]
  ]
}

No extra text after JSON.
"""


def call_llm(requirement: str) -> str:
    prompt = f"{SYSTEM_PROMPT}\nUser requirement:\n{requirement}"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 700,
            "temperature": 0.3
        }
    }

    response = requests.post(
        HF_MODEL_URL,
        headers=HEADERS,
        json=payload,
        timeout=200
    )

    response.raise_for_status()
    data = response.json()

    if isinstance(data, list):
        return data[0]["generated_text"]
    return data["generated_text"]
