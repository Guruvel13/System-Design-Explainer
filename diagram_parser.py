# diagram_parser.py
import json
import re

def repair_json(text: str) -> str:
    """Auto-repair common JSON issues."""
    text = text.replace(";", ",")              # fix semicolon usage
    text = text.replace(",,", ",")             # double commas
    text = re.sub(r",\s*}", "}", text)         # trailing comma in object
    text = re.sub(r",\s*]", "]", text)         # trailing comma in array
    return text

def parse_output(text: str):
    if "[EXPLANATION]" not in text or "[DIAGRAM_JSON]" not in text:
        return text, [], [], {}, {}, {}

    try:
        exp_part = text.split("[EXPLANATION]", 1)[1]
        explanation, json_part = exp_part.split("[DIAGRAM_JSON]", 1)
        explanation = explanation.strip()
    except:
        return text, [], [], {}, {}, {}

    # Extract JSON
    json_match = re.search(r"\{[\s\S]*\}", json_part)
    if not json_match:
        return explanation, [], [], {}, {}, {}

    raw_json = repair_json(json_match.group())

    try:
        obj = json.loads(raw_json)
    except:
        # JSON still invalid
        return explanation, [], [], {}, {}, {}

    return (
        explanation,
        obj.get("nodes", []),
        obj.get("edges", []),
        obj.get("annotations", {}),
        obj.get("layers", {}),
        obj.get("edge_types", {})
    )
