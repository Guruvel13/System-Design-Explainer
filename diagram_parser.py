# diagram_parser.py
# Robust parser for SystemSketch AI output
# Extracts explanation + strict JSON diagram block safely

import json
import re


def parse_output(text: str):
    """
    Parses the LLM output into:
    explanation, nodes, edges, annotations, layers, edge_types

    Returns safe defaults if:
    - Sections are missing
    - JSON is malformed
    - Extra text appears after JSON
    """

    # ----------------------------------------------------------
    # 1. Validate presence of both markers
    # ----------------------------------------------------------
    if "[EXPLANATION]" not in text or "[DIAGRAM_JSON]" not in text:
        return text.strip(), [], [], {}, {}, {}

    # ----------------------------------------------------------
    # 2. Extract explanation section
    # ----------------------------------------------------------
    try:
        after_exp = text.split("[EXPLANATION]", 1)[1]
        explanation, after_json = after_exp.split("[DIAGRAM_JSON]", 1)
        explanation = explanation.strip()
    except Exception:
        # fallback, return raw text
        return text.strip(), [], [], {}, {}, {}

    # ----------------------------------------------------------
    # 3. Extract JSON block using largest {...} block
    # (LLM may sometimes add whitespace, newlines, etc.)
    # ----------------------------------------------------------
    json_match = re.search(r"\{[\s\S]*\}", after_json)
    if not json_match:
        return explanation, [], [], {}, {}, {}

    json_text = json_match.group()

    # ----------------------------------------------------------
    # 4. Parse JSON
    # ----------------------------------------------------------
    try:
        obj = json.loads(json_text)
    except Exception:
        return explanation, [], [], {}, {}, {}

    # ----------------------------------------------------------
    # 5. Extract fields with safe fallbacks
    # ----------------------------------------------------------
    nodes = obj.get("nodes", [])
    edges = obj.get("edges", [])
    annotations = obj.get("annotations", {})
    layers = obj.get("layers", {})
    edge_types = obj.get("edge_types", {})

    # ----------------------------------------------------------
    # 6. Return structured data
    # ----------------------------------------------------------
    return explanation, nodes, edges, annotations, layers, edge_types
