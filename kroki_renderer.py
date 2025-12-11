# kroki_renderer.py
# Use kroki.io to render diagram source (dot) to png/pdf/svg without local dot executable.

import requests

KROKI_BASE = "https://kroki.io"

def _post_kroki(format: str, diagram_type: str, source: str) -> bytes:
    """
    format: 'png','svg','pdf'
    diagram_type: 'graphviz' for dot
    """
    url = f"{KROKI_BASE}/{diagram_type}/{format}"
    headers = {"Content-Type": "text/plain"}
    resp = requests.post(url, data=source.encode("utf-8"), headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.content

def generate_png_from_dot(dot_source: str) -> bytes:
    return _post_kroki("png", "graphviz", dot_source)

def generate_svg_from_dot(dot_source: str) -> bytes:
    return _post_kroki("svg", "graphviz", dot_source)

def generate_pdf_from_dot(dot_source: str) -> bytes:
    return _post_kroki("pdf", "graphviz", dot_source)
