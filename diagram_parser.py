# diagram_parser.py
import json
import re

def parse_output(text: str):
    """
    Extracts:
    - explanation
    - nodes
    - edges
    - annotations
    - layers
    - edge_types
    """

    if "[EXPLANATION]" not in text or "[DIAGRAM_JSON]" not in text:
        return text.strip(), [], [], {}, {}, {}

    try:
        exp_part = text.split("[EXPLANATION]", 1)[1]
        explanation, json_part = exp_part.split("[DIAGRAM_JSON]", 1)
        explanation = explanation.strip()
    except:
        return text.strip(), [], [], {}, {}, {}

    # Extract JSON block exactly
    match = re.search(r"\{.*\}", json_part, re.DOTALL)
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
    except:
        return explanation, [], [], {}, {}, {}
