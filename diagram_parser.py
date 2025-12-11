# diagram_parser.py
import json
import re

def parse_output(text: str):
    """
    Extracts [EXPLANATION] and [DIAGRAM_JSON] sections.
    Returns: explanation, nodes, edges, annotations, layers, edge_types
    """

    # ========== Extract EXPLANATION ==========
    exp_match = re.search(
        r"\[EXPLANATION\](.*?)(?=\[DIAGRAM_JSON\])",
        text,
        re.DOTALL
    )

    if not exp_match:
        # No explanation section found
        return text, [], [], {}, {}, {}

    explanation = exp_match.group(1).strip()

    # ========== Extract JSON ==========
    json_match = re.search(
        r"\[DIAGRAM_JSON\]\s*(\{.*\})",
        text,
        re.DOTALL
    )

    if not json_match:
        return explanation, [], [], {}, {}, {}

    json_text = json_match.group(1).strip()

    # ========== Parse JSON safely ==========
    try:
        data = json.loads(json_text)
    except Exception:
        return explanation, [], [], {}, {}, {}

    # ========== Extract fields safely ==========
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    annotations = data.get("annotations", {})
    layers = data.get("layers", {})
    edge_types = data.get("edge_types", {})

    # Guarantee correct return types
    if not isinstance(nodes, list):
        nodes = []
    if not isinstance(edges, list):
        edges = []
    if not isinstance(annotations, dict):
        annotations = {}
    if not isinstance(layers, dict):
        layers = {}
    if not isinstance(edge_types, dict):
        edge_types = {}

    return explanation, nodes, edges, annotations, layers, edge_types
