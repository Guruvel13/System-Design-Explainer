# diagram_parser.py
# Enhanced robust parser with metrics, validation, and comprehensive error handling

import json
import re
import logging
from typing import Tuple, List, Dict, Any, Optional, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parsing metrics
_parse_metrics = {
    "total_attempts": 0,
    "successful_parses": 0,
    "failed_parses": 0,
    "auto_repairs": 0
}


def _normalize_quotes(s: str) -> str:
    """Normalize all quote types to standard double quotes."""
    # Replace smart quotes with regular quotes
    s = s.replace(""", '"').replace(""", '"').replace("'", "'").replace("'", "'")
    # Replace single quotes around keys with double quotes
    s = re.sub(r"(?<=\{|,)\s*'([^']+)'\s*:", r'"\1":', s)
    # Replace single quotes around values with double quotes
    s = re.sub(r':\s*\'([^\']*)\'(?=\s*[,\}])', r': "\1"', s)
    return s


def _remove_trailing_commas(s: str) -> str:
    """Remove trailing commas before closing braces/brackets."""
    s = re.sub(r",\s*}", "}", s)
    s = re.sub(r",\s*\]", "]", s)
    return s


def _fix_semicolons(s: str) -> str:
    """Replace semicolons with commas where appropriate."""
    s = re.sub(r";\s*(?=[\]\}\"])", ",", s)
    s = s.replace(";\n", ",\n")
    return s


def _collapse_multiple_commas(s: str) -> str:
    """Collapse multiple consecutive commas into one."""
    return re.sub(r",\s*,+", ",", s)


def _fix_missing_quotes(s: str) -> str:
    """Add quotes around unquoted keys and values."""
    # Fix unquoted keys (basic heuristic)
    s = re.sub(r'(\{|,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', s)
    return s


def _extract_json_candidates(text: str) -> List[str]:
    """
    Extract all potential JSON objects from text using bracket matching.
    
    Returns:
        List of candidate JSON strings
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


def _try_load_candidate(raw: str, track_repairs: bool = True) -> Optional[Dict[str, Any]]:
    """
    Attempt to parse JSON with progressive auto-repair strategies.
    
    Args:
        raw: Raw JSON string to parse
        track_repairs: Whether to track repair metrics
    
    Returns:
        Parsed dict or None if all attempts fail
    """
    attempts = [
        ("raw", raw),
        ("normalize_quotes", _normalize_quotes(raw)),
        ("fix_semicolons", _normalize_quotes(_fix_semicolons(raw))),
        ("remove_trailing_commas", _normalize_quotes(_fix_semicolons(_remove_trailing_commas(raw)))),
        ("collapse_commas", _normalize_quotes(_fix_semicolons(_remove_trailing_commas(_collapse_multiple_commas(raw))))),
        ("fix_missing_quotes", _fix_missing_quotes(_normalize_quotes(_fix_semicolons(_remove_trailing_commas(raw)))))
    ]
    
    for strategy, attempt in attempts:
        try:
            result = json.loads(attempt)
            if strategy != "raw" and track_repairs:
                _parse_metrics["auto_repairs"] += 1
                logger.info(f"JSON parsed successfully using strategy: {strategy}")
            return result
        except json.JSONDecodeError:
            continue
        except Exception:
            continue
    
    # Last resort: try extracting inner JSON
    first = raw.find("{")
    last = raw.rfind("}")
    if first != -1 and last != -1 and last > first:
        sub = raw[first:last + 1]
        try:
            return json.loads(_normalize_quotes(_fix_semicolons(_remove_trailing_commas(sub))))
        except Exception:
            return None
    
    return None


def _validate_diagram_data(
    nodes: List[str],
    edges: List[List[str]],
    annotations: Dict[str, str],
    layers: Dict[str, List[str]],
    edge_types: Dict[str, str]
) -> Tuple[bool, Optional[str]]:
    """
    Validate parsed diagram data for consistency and completeness.
    
    Returns:
        (is_valid, error_message)
    """
    # Check minimum requirements
    if not nodes:
        return False, "No nodes found in diagram"
    
    if len(nodes) < 2:
        return False, "Diagram must have at least 2 nodes"
    
    if len(nodes) > 20:
        return False, f"Too many nodes ({len(nodes)}), maximum is 20"
    
    # Validate edges reference existing nodes
    node_set = set(nodes)
    for edge in edges:
        if len(edge) != 2:
            return False, f"Invalid edge format: {edge}"
        src, dst = edge
        if src not in node_set:
            return False, f"Edge references non-existent source node: {src}"
        if dst not in node_set:
            return False, f"Edge references non-existent destination node: {dst}"
    
    # Validate layers reference existing nodes
    for layer_name, layer_nodes in layers.items():
        for node in layer_nodes:
            if node not in node_set:
                return False, f"Layer '{layer_name}' references non-existent node: {node}"
    
    # Check for reasonable annotation lengths
    for node, annotation in annotations.items():
        if len(annotation) > 100:
            logger.warning(f"Annotation for '{node}' is very long ({len(annotation)} chars)")
    
    return True, None


def parse_output(
    text: str,
    *,
    enable_llm_repair: bool = False,
    llm_repair_fn: Optional[Callable[[str], str]] = None,
    strict_validation: bool = False
) -> Tuple[str, List[str], List[List[str]], Dict[str, str], Dict[str, List[str]], Dict[str, str]]:
    """
    Parse LLM output and extract structured architecture data.
    
    Args:
        text: Raw LLM output text
        enable_llm_repair: Enable LLM-based JSON repair (advanced)
        llm_repair_fn: Function to repair malformed JSON using LLM
        strict_validation: Enable strict validation (raises errors)
    
    Returns:
        Tuple of (explanation, nodes, edges, annotations, layers, edge_types)
        Returns safe defaults on failure unless strict_validation=True
    """
    EMPTY = ("", [], [], {}, {}, {})
    _parse_metrics["total_attempts"] += 1
    
    # Input validation
    if not isinstance(text, str) or not text.strip():
        logger.warning("Received empty or invalid input text")
        _parse_metrics["failed_parses"] += 1
        return EMPTY
    
    # Normalize line endings
    text = text.replace("\r\n", "\n")
    cleaned = re.sub(r"=+\s*\n", "", text)
    
    # Extract explanation section
    explanation = ""
    after_json_section = ""
    
    # Strategy 1: Both sections present
    if "[EXPLANATION]" in cleaned and "[DIAGRAM_JSON]" in cleaned:
        try:
            after_exp = cleaned.split("[EXPLANATION]", 1)[1]
            explanation_part, json_part = after_exp.split("[DIAGRAM_JSON]", 1)
            explanation = explanation_part.strip()
            after_json_section = json_part.strip()
            logger.info("Extracted both EXPLANATION and DIAGRAM_JSON sections")
        except Exception as e:
            logger.warning(f"Failed to split sections: {e}")
    
    # Strategy 2: Only DIAGRAM_JSON present
    if not explanation and "[DIAGRAM_JSON]" in cleaned:
        try:
            idx = cleaned.index("[DIAGRAM_JSON]")
            pre = cleaned[:idx]
            if "[EXPLANATION]" in pre:
                explanation = pre.split("[EXPLANATION]", 1)[1].strip()
            else:
                explanation = pre.strip()
            after_json_section = cleaned[idx + len("[DIAGRAM_JSON]"):].strip()
        except Exception as e:
            logger.warning(f"Failed to extract DIAGRAM_JSON section: {e}")
    
    # Strategy 3: Only EXPLANATION present
    if not explanation and "[EXPLANATION]" in cleaned:
        try:
            explanation = cleaned.split("[EXPLANATION]", 1)[1].strip()
        except Exception:
            explanation = cleaned.strip()
    
    # Extract JSON candidates
    candidates = _extract_json_candidates(after_json_section) if after_json_section else []
    if not candidates:
        candidates = _extract_json_candidates(cleaned)
    
    if not candidates:
        logger.warning("No JSON candidates found in text")
        _parse_metrics["failed_parses"] += 1
        return explanation, [], [], {}, {}, {}
    
    logger.info(f"Found {len(candidates)} JSON candidate(s)")
    
    # Try to parse each candidate
    parsed_obj = None
    for i, cand in enumerate(candidates):
        parsed = _try_load_candidate(cand)
        if isinstance(parsed, dict):
            parsed_obj = parsed
            logger.info(f"Successfully parsed candidate {i + 1}")
            break
    
    # Optional LLM-based repair
    if parsed_obj is None and enable_llm_repair and llm_repair_fn is not None:
        logger.info("Attempting LLM-based JSON repair")
        joined = "\n\n".join(candidates)
        try:
            repaired = llm_repair_fn(joined)
            if repaired and isinstance(repaired, str):
                try:
                    parsed_obj = json.loads(repaired)
                    logger.info("LLM repair successful")
                except Exception:
                    parsed_obj = _try_load_candidate(repaired, track_repairs=False)
        except Exception as e:
            logger.warning(f"LLM repair failed: {e}")
            parsed_obj = None
    
    if parsed_obj is None:
        logger.error("All JSON parsing attempts failed")
        _parse_metrics["failed_parses"] += 1
        return explanation, [], [], {}, {}, {}
    
    # Extract and clean diagram components
    nodes = parsed_obj.get("nodes") if isinstance(parsed_obj.get("nodes"), list) else []
    edges = parsed_obj.get("edges") if isinstance(parsed_obj.get("edges"), list) else []
    annotations = parsed_obj.get("annotations") if isinstance(parsed_obj.get("annotations"), dict) else {}
    layers = parsed_obj.get("layers") if isinstance(parsed_obj.get("layers"), dict) else {}
    edge_types = parsed_obj.get("edge_types") if isinstance(parsed_obj.get("edge_types"), dict) else {}
    
    # Clean and validate node data
    nodes = [str(n).strip() for n in nodes if isinstance(n, (str, int)) and str(n).strip()]
    
    # Clean and validate edge data
    cleaned_edges = []
    for e in edges:
        if isinstance(e, (list, tuple)) and len(e) >= 2:
            src, dst = str(e[0]).strip(), str(e[1]).strip()
            if src and dst:
                cleaned_edges.append([src, dst])
    edges = cleaned_edges
    
    # Clean annotations
    annotations = {str(k).strip(): str(v).strip() for k, v in annotations.items() if str(k).strip()}
    
    # Clean layers
    layers = {
        str(k).strip(): [str(x).strip() for x in v if str(x).strip()]
        for k, v in layers.items()
        if isinstance(v, list) and str(k).strip()
    }
    
    # Clean edge types
    edge_types = {str(k).strip(): str(v).strip() for k, v in edge_types.items() if str(k).strip()}
    
    # Validate diagram data
    is_valid, error_msg = _validate_diagram_data(nodes, edges, annotations, layers, edge_types)
    
    if not is_valid:
        logger.error(f"Diagram validation failed: {error_msg}")
        if strict_validation:
            raise ValueError(f"Diagram validation failed: {error_msg}")
        _parse_metrics["failed_parses"] += 1
        return explanation, [], [], {}, {}, {}
    
    _parse_metrics["successful_parses"] += 1
    logger.info(f"Successfully parsed diagram: {len(nodes)} nodes, {len(edges)} edges")
    
    return explanation, nodes, edges, annotations, layers, edge_types


def get_parse_metrics() -> Dict[str, Any]:
    """Get parsing metrics for monitoring and debugging."""
    success_rate = (
        _parse_metrics["successful_parses"] / _parse_metrics["total_attempts"] * 100
        if _parse_metrics["total_attempts"] > 0
        else 0
    )
    
    return {
        **_parse_metrics,
        "success_rate": round(success_rate, 2)
    }


def reset_metrics() -> None:
    """Reset parsing metrics."""
    global _parse_metrics
    _parse_metrics = {
        "total_attempts": 0,
        "successful_parses": 0,
        "failed_parses": 0,
        "auto_repairs": 0
    }
    logger.info("Parse metrics reset")
