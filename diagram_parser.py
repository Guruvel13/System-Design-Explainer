# diagram_parser.py
import json
import re


def parse_output(text: str):
    """
    Extracts clean [EXPLANATION] and [DIAGRAM_JSON] sections.
    Works even if model adds formatting or equals lines.
    Returns: explanation, nodes, edges, annotations, layers, edge_types
    """

    # Normalize spaces + remove decorative lines
    cleaned = text.replace("=", "").strip()

    # ---------------------------------------------------
    # 1. Extract EXPLANATION safely
    # ---------------------------------------------------
    exp_match = re.search(
        r"\[EXPLANATION\](.*?)(?=\[DIAGRAM_JSON\])",
        cleaned,
        re.DOTALL
    )

    if not exp_match:
        # Cannot parse explanation → return raw text
        return text, [], [], {}, {}, {}

    explanation = exp_match.group(1).strip()

    # ---------------------------------------------------
    # 2. Extract DIAGRAM JSON block safely
    # ---------------------------------------------------
    json_match = re.search(
        r"\[DIAGRAM_JSON\]\s*(\{.*\})",
        cleaned,
        re.DOTALL
    )

    if not json_match:
        # JSON section missing
        return explanation, [], [], {}, {}, {}

    json_text = json_match.group(1)

    try:
        obj = json.loads(json_text)
        return (
            explanation,
            obj.get("nodes", []),
            obj.get("edges", []),
            obj.get("annotations", {}),
            obj.get("layers", {}),
            obj.get("edge_types", {})
        )
    except Exception:
        # JSON invalid
        return explanation, [], [], {}, {}, {}
