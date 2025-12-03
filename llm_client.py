import os
import requests

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL_URL = os.getenv("HF_MODEL_URL")

print("DEBUG::TOKEN =", HF_API_TOKEN)
print("DEBUG::MODEL_URL =", HF_MODEL_URL)

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = """
You are a senior system architect.

[EXPLANATION]
<your explanation>

[DIAGRAM_JSON]
{
  "nodes": ["A","B"],
  "edges": [["A","B"]]
}
"""


def call_llm(requirement: str) -> str:
    if not HF_MODEL_URL:
        raise RuntimeError("HF_MODEL_URL is missing. Set it in Streamlit Secrets.")

    payload = {
        "inputs": f"{SYSTEM_PROMPT}\nUser requirement:\n{requirement}",
        "parameters": {
            "temperature": 0.3,
            "max_new_tokens": 700
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
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]

    raise RuntimeError(f"Unexpected response: {data}")
