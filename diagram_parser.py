# diagram_parser.py (FINAL FIXED)
import json
import re

def parse_output(text: str):
    if "[EXPLANATION]" not in text or "[DIAGRAM_JSON]" not in text:
        return text, [], [], {}, {}, {}

    # Extract explanation
    exp_part = text.split("[EXPLANATION]", 1)[1]
    explanation, json_part = exp_part.split("[DIAGRAM_JSON]", 1)
    explanation = explanation.strip()

    # Extract JSON using the FIRST {...} block
    match = re.search(r"\{[\s\S]*\}", json_part)
    if not match:
        return explanation, [], [], {}, {}, {}

    try:
        obj = json.loads(match.group())
        return (
            explanation,
            obj.get("nodes", []),
            obj.get("edges", []),
            obj.get("annotations", {}),
            obj.get("layers", {}),
            obj.get("edge_types", {})
        )
    except Exception:
        return explanation, [], [], {}, {}, {}
