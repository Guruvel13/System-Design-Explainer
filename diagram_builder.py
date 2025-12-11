# diagram_builder.py (FINAL FIXED)
from graphviz import Digraph

def build_graph(nodes, edges, annotations=None, layers=None, edge_types=None, dark_mode=False):

    annotations = annotations or {}
    layers = layers or {}
    edge_types = edge_types or {}

    fg = "white" if dark_mode else "black"
    bg = "#111111" if dark_mode else "white"
    node_color = "#222222" if dark_mode else "#f8f8f8"

    dot = Digraph()
    dot.attr(rankdir="LR", bgcolor=bg)

    # Layered nodes
    if layers:
        for layer, comps in layers.items():
            with dot.subgraph(name=f"cluster_{layer}") as sub:
                sub.attr(label=layer.upper(), color="#666666")
                for c in comps:
                    sub.node(c, f"{c}\n{annotations.get(c,'')}", style="filled", fillcolor=node_color, fontcolor=fg)
    else:
        for c in nodes:
            dot.node(c, f"{c}\n{annotations.get(c,'')}", style="filled", fillcolor=node_color, fontcolor=fg)

    # Edges
    for src, dst in edges:
        label = edge_types.get(f"{src}->{dst}", "")
        dot.edge(src, dst, label=label, fontcolor=fg)

    return dot
