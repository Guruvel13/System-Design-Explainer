import json

def parse_output(text: str):
    if "[EXPLANATION]" not in text or "[DIAGRAM_JSON]" not in text:
        return text, [], []

    part = text.split("[EXPLANATION]", 1)[1]
    explanation, json_part = part.split("[DIAGRAM_JSON]", 1)

    explanation = explanation.strip()

    start = json_part.find("{")
    end = json_part.rfind("}")

    json_str = json_part[start:end+1]

    try:
        data = json.loads(json_str)
        return explanation, data["nodes"], data["edges"]
    except:
        return explanation, [], []
