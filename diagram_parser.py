# diagram_parser.py
import json
import re

def parse_output(text: str):
    """
    Extracts [EXPLANATION] and [DIAGRAM_JSON] sections.
    Returns: explanation, nodes, edges, annotations, layers, edge_types
    """
    if "[EXPLANATION]" not in text or "[DIAGRAM_JSON]" not in text:
        return text, [], [], {}, {}, {}

    # Split explanation
    try:
        exp_section = text.split("[EXPLANATION]", 1)[1]
        explanation, json_section = exp_section.split("[DIAGRAM_JSON]", 1)
        explanation = explanation.strip()
    except:
        return text, [], [], {}, {}, {}

    # Extract JSON block
    json_match = re.search(r"\{.*\}", json_section, re.DOTALL)
    if not json_match:
        return explanation, [], [], {}, {}, {}

    try:
        obj = json.loads(json_match.group())
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
