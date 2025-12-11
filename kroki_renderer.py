import requests

def generate_svg_from_dot(dot_source: str):
    url = "https://kroki.io/graphviz/svg"
    response = requests.post(url, data=dot_source.encode("utf-8"))
    response.raise_for_status()
    return response.content

def generate_png_from_dot(dot_source: str):
    url = "https://kroki.io/graphviz/png"
    response = requests.post(url, data=dot_source.encode("utf-8"))
    response.raise_for_status()
    return response.content

def generate_pdf_from_dot(dot_source: str):
    url = "https://kroki.io/graphviz/pdf"
    response = requests.post(url, data=dot_source.encode("utf-8"))
    response.raise_for_status()
    return response.content
