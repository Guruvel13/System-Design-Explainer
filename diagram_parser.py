# diagram_parser.py
# Robust parser with conservative auto-repair (no automatic LLM repair by default)

import json
import re
from typing import Tuple, List, Dict, Any, Optional, Callable

def _normalize_quotes(s: str) -> str:
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    s = re.sub(r"(?<=\{|,)\s*'([^']+)'\s*:", r'"\1":', s)
    s = re.sub(r':\s*\'([^\']*)\'(?=\s*[,\}])', r': "\1"', s)
    return s

def _remove_trailing_commas(s: str) -> str:
    s = re.sub(r",\s*}", "}", s)
    s = re.sub(r",\s*\]", "]", s)
    return s

def _fix_semicolons(s: str) -> str:
    s = re.sub(r";\s*(?=[\]\}\"])", ",", s)
    s = s.replace(";\n", ",\n")
    return s

def _collapse_multiple_commas(s: str) -> str:
    return re.sub(r",\s*,+", ",", s)

def _extract_json_candidates(text: str) -> List[str]:
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

def _try_load_candidate(raw: str) -> Optional[Dict[str, Any]]:
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
    first = raw.find("{")
    last = raw.rfind("}")
    if first != -1 and last != -1 and last > first:
        sub = raw[first:last+1]
        try:
            return json.loads(_normalize_quotes(_fix_semicolons(_remove_trailing_commas(sub))))
        except Exception:
            return None
    return None

def parse_output(
    text: str,
    *,
    enable_llm_repair: bool = False,
    llm_repair_fn: Optional[Callable[[str], str]] = None
) -> Tuple[str, List[str], List[List[str]], Dict[str, str], Dict[str, List[str]], Dict[str, str]]:
    """
    Parse LLM output and return:
    explanation, nodes, edges, annotations, layers, edge_types
    Returns safe defaults on failure.
    """
    EMPTY = ("", [], [], {}, {}, {})

    if not isinstance(text, str) or not text.strip():
        return EMPTY

    text = text.replace("\r\n", "\n")
    cleaned = re.sub(r"=+\s*\n", "", text)

    explanation = ""
    after_json_section = ""

    if "[EXPLANATION]" in cleaned and "[DIAGRAM_JSON]" in cleaned:
        try:
            after_exp = cleaned.split("[EXPLANATION]", 1)[1]
            explanation_part, json_part = after_exp.split("[DIAGRAM_JSON]", 1)
            explanation = explanation_part.strip()
            after_json_section = json_part.strip()
        except Exception:
            pass

    if not explanation and "[DIAGRAM_JSON]" in cleaned:
        try:
            idx = cleaned.index("[DIAGRAM_JSON]")
            pre = cleaned[:idx]
            if "[EXPLANATION]" in pre:
                explanation = pre.split("[EXPLANATION]", 1)[1].strip()
            else:
                explanation = pre.strip()
            after_json_section = cleaned[idx + len("[DIAGRAM_JSON]"):].strip()
        except Exception:
            pass

    if not explanation and "[EXPLANATION]" in cleaned:
        try:
            explanation = cleaned.split("[EXPLANATION]", 1)[1].strip()
        except Exception:
            explanation = cleaned.strip()

    candidates = _extract_json_candidates(after_json_section) if after_json_section else []
    if not candidates:
        candidates = _extract_json_candidates(cleaned)

    if not candidates:
        return explanation, [], [], {}, {}, {}

    parsed_obj = None
    for cand in candidates:
        parsed = _try_load_candidate(cand)
        if isinstance(parsed, dict):
            parsed_obj = parsed
            break

    if parsed_obj is None and enable_llm_repair and llm_repair_fn is not None:
        joined = "\n\n".join(candidates)
        try:
            repaired = llm_repair_fn(joined)
            if repaired and isinstance(repaired, str):
                try:
                    parsed_obj = json.loads(repaired)
                except Exception:
                    parsed_obj = _try_load_candidate(repaired)
        except Exception:
            parsed_obj = None

    if parsed_obj is None:
        return explanation, [], [], {}, {}, {}

    nodes = parsed_obj.get("nodes") if isinstance(parsed_obj.get("nodes"), list) else []
    edges = parsed_obj.get("edges") if isinstance(parsed_obj.get("edges"), list) else []
    annotations = parsed_obj.get("annotations") if isinstance(parsed_obj.get("annotations"), dict) else {}
    layers = parsed_obj.get("layers") if isinstance(parsed_obj.get("layers"), dict) else {}
    edge_types = parsed_obj.get("edge_types") if isinstance(parsed_obj.get("edge_types"), dict) else {}

    nodes = [str(n) for n in nodes if isinstance(n, (str, int))]
    cleaned_edges = []
    for e in edges:
        if isinstance(e, (list, tuple)) and len(e) >= 2:
            cleaned_edges.append([str(e[0]), str(e[1])])
    edges = cleaned_edges
    annotations = {str(k): str(v) for k, v in annotations.items()}
    layers = {str(k): [str(x) for x in v] for k, v in layers.items() if isinstance(v, list)}
    edge_types = {str(k): str(v) for k, v in edge_types.items()}

    return explanation, nodes, edges, annotations, layers, edge_types
