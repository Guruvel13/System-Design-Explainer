import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("")
HF_MODEL_URL = os.getenv("https://router.huggingface.co/hf-inference/models/google/gemma-2-2b-it")

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = """
You are a senior system architect.

Your response MUST follow this exact format:

[EXPLANATION]
<bullet point architecture explanation>

[DIAGRAM_JSON]
{
  "nodes": ["A","B","C"],
  "edges": [
    ["A","B"],
    ["B","C"]
  ]
}
Do NOT add extra text after the JSON.
"""


def call_llm(requirement: str) -> str:
    payload = {
        "inputs": f"{SYSTEM_PROMPT}\nUser requirement:\n{requirement}",
        "parameters": {
            "temperature": 0.3,
            "max_new_tokens": 700,
            "return_full_text": False
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

    # Router ALWAYS returns list with generated_text
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]

    raise RuntimeError(f"Unexpected HF response: {data}")
