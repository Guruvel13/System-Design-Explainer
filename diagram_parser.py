# diagram_parser.py
# Robust parser with multi-strategy JSON extraction + safe auto-repair
import json
import re
from typing import Tuple, List, Dict, Any


def _normalize_quotes(s: str) -> str:
    """Replace smart quotes and single quotes in keys/strings with double quotes when safe."""
    # replace unicode smart quotes
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    # quick attempt: replace single-quoted JSON property/value to double quotes only when likely JSON
    # but avoid changing apostrophes inside words by a conservative regex: replace ' "key': 'value' ' -> "key": "value"
    s = re.sub(r"(?<=\{|,)\s*'([^']+)'\s*:", r'"\1":', s)   # keys
    s = re.sub(r':\s*\'([^\']*)\'(?=\s*[,\}])', r': "\1"', s)  # values
    return s


def _remove_trailing_commas(s: str) -> str:
    """Remove trailing commas before } or ]"""
    s = re.sub(r",\s*}", "}", s)
    s = re.sub(r",\s*\]", "]", s)
    return s


def _fix_semicolons(s: str) -> str:
    """Replace semicolons used as separators with commas (common model mistake)."""
    # Only replace semicolons that appear between JSON-like tokens (naive but useful)
    s = re.sub(r";\s*(?=[\]\}\"])", ",", s)
    s = s.replace(";\n", ",\n")
    return s


def _collapse_multiple_commas(s: str) -> str:
    """Collapse sequences of commas into a single comma."""
    return re.sub(r",\s*,+", ",", s)


def _extract_json_candidates(text: str) -> List[str]:
    """
    Return list of all {...} substrings (non-overlapping).
    Uses a stack to find balanced braces to avoid greedy regex pitfalls.
    """
    candidates = []
    stack = []
    start_idx = None
    for i, ch in enumerate(text):
        if ch == "{":
            if not stack:
                start_idx = i
            stack.append("{")
        elif ch == "}":
            if stack:
                stack.pop()
                if not stack and start_idx is not None:
                    candidates.append(text[start_idx:i + 1])
                    start_idx = None
    return candidates


def _try_load_candidate(raw: str) -> Any:
    """Try loading JSON after several conservative repair attempts."""
    attempts = [
        raw,
        _normalize_quotes(raw),
        _normalize_quotes(_fix_semicolons(raw)),
        _normalize_quotes(_fix_semicolons(_remove_trailing_commas(raw))),
        _normalize_quotes(_fix_semicolons(_remove_trailing_commas(_collapse_multiple_commas(raw)))),
    ]
    for attempt in attempts:
        try:
            return json.loads(attempt)
        except Exception:
            continue
    # final attempt: try to extract only substring from first '{' to last '}' and retry normalized
    try:
        first = raw.find("{")
        last = raw.rfind("}")
        if first != -1 and last != -1 and last > first:
            sub = raw[first:last+1]
            sub2 = _normalize_quotes(_fix_semicolons(_remove_trailing_commas(sub)))
            return json.loads(sub2)
    except Exception:
        pass
    return None


def parse_output(text: str) -> Tuple[str, List[str], List[List[str]], Dict[str, str], Dict[str, List[str]], Dict[str, str]]:
    """
    Parse LLM output and return:
      explanation (str),
      nodes (list[str]),
      edges (list[list[str]]),
      annotations (dict),
      layers (dict),
      edge_types (dict)

    Always returns valid types (empty lists/dicts when missing).
    """
    # default safe returns
    EMPTY_RETURN = ("", [], [], {}, {}, {})

    if not isinstance(text, str) or not text.strip():
        return EMPTY_RETURN

    # normalize CRLF to LF
    text = text.replace("\r\n", "\n")

    # 1) Try robustly splitting explanation and diagram marker
    explanation = ""
    after_json_section = ""
    if "[EXPLANATION]" in text and "[DIAGRAM_JSON]" in text:
        try:
            after_exp = text.split("[EXPLANATION]", 1)[1]
            explanation_part, json_part = after_exp.split("[DIAGRAM_JSON]", 1)
            explanation = explanation_part.strip()
            after_json_section = json_part.strip()
        except Exception:
            # fallback to simple behavior below
            pass

    # If markers missing or split failed, try to salvage: find first occurrence of [DIAGRAM_JSON]
    if not explanation and "[DIAGRAM_JSON]" in text:
        try:
            idx = text.index("[DIAGRAM_JSON]")
            # everything before that (but after [EXPLANATION] if present) is explanation
            pre = text[:idx]
            if "[EXPLANATION]" in pre:
                explanation = pre.split("[EXPLANATION]", 1)[1].strip()
            else:
                # take portion before DIAGRAM_JSON as explanation
                explanation = pre.strip()
            after_json_section = text[idx + len("[DIAGRAM_JSON]"):].strip()
        except Exception:
            pass

    # If still empty, and [EXPLANATION] present, try to extract explanation only
    if not explanation and "[EXPLANATION]" in text:
        try:
            explanation = text.split("[EXPLANATION]", 1)[1].strip()
        except Exception:
            explanation = text.strip()

    # 2) Find JSON candidates in after_json_section; if empty, search entire text as fallback
    candidates = []
    if after_json_section:
        candidates = _extract_json_candidates(after_json_section)
    if not candidates:
        candidates = _extract_json_candidates(text)

    if not candidates:
        # nothing that looks like JSON found
        return explanation, [], [], {}, {}, {}

    # 3) Try parsing candidates one by one, using repair attempts
    parsed_obj = None
    for cand in candidates:
        parsed = _try_load_candidate(cand)
        if parsed is not None and isinstance(parsed, dict):
            parsed_obj = parsed
            break

    if parsed_obj is None:
        # last resort: attempt to join multiple nearby braces into one JSON (rare)
        joined = "".join(candidates)
        parsed = _try_load_candidate(joined)
        if parsed is not None and isinstance(parsed, dict):
            parsed_obj = parsed

    if parsed_obj is None:
        # give up, return explanation only
        return explanation, [], [], {}, {}, {}

    # 4) Extract expected fields with safe defaults and type checks
    nodes = parsed_obj.get("nodes") if isinstance(parsed_obj.get("nodes"), list) else []
    edges = parsed_obj.get("edges") if isinstance(parsed_obj.get("edges"), list) else []
    annotations = parsed_obj.get("annotations") if isinstance(parsed_obj.get("annotations"), dict) else {}
    layers = parsed_obj.get("layers") if isinstance(parsed_obj.get("layers"), dict) else {}
    edge_types = parsed_obj.get("edge_types") if isinstance(parsed_obj.get("edge_types"), dict) else {}

    # ensure edges are list of pairs
    cleaned_edges = []
    for e in edges:
        if isinstance(e, (list, tuple)) and len(e) >= 2:
            # take first two items and cast to str
            cleaned_edges.append([str(e[0]), str(e[1])])
    edges = cleaned_edges

    # ensure nodes are strings
    nodes = [str(n) for n in nodes if isinstance(n, (str, int))]

    # ensure annotations strings
    annotations = {str(k): str(v) for k, v in annotations.items()}

    # ensure layers lists of strings
    cleaned_layers = {}
    for k, v in layers.items():
        if isinstance(v, list):
            cleaned_layers[str(k)] = [str(x) for x in v]
    layers = cleaned_layers

    # ensure edge_types keys and values stringified
    edge_types = {str(k): str(v) for k, v in edge_types.items()}

    return explanation, nodes, edges, annotations, layers, edge_types
