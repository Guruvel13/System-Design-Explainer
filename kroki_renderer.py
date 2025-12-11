# kroki_renderer.py
import requests

KROKI_URL = "https://kroki.io/graphviz"

def _send_kroki(diagram_source, out_format):
    url = f"{KROKI_URL}/{out_format}"
    resp = requests.post(url, data=diagram_source.encode("utf-8"))
    resp.raise_for_status()
    return resp.content

def generate_svg_from_dot(dot_source):
    return _send_kroki(dot_source, "svg")

def generate_png_from_dot(dot_source):
    return _send_kroki(dot_source, "png")

def generate_pdf_from_dot(dot_source):
    return _send_kroki(dot_source, "pdf")
