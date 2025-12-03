import json

def parse_output(text: str):
    if "[EXPLANATION]" not in text or "[DIAGRAM_JSON]" not in text:
        return text, [], []

    explanation_part = text.split("[EXPLANATION]", 1)[1]
    explanation, json_section = explanation_part.split("[DIAGRAM_JSON]", 1)

    explanation = explanation.strip()

    start = json_section.find("{")
    end = json_section.rfind("}")

    try:
        obj = json.loads(json_section[start:end+1])
        return explanation, obj.get("nodes", []), obj.get("edges", [])
    except:
        return explanation, [], []
