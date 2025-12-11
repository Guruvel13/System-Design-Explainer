# diagram_builder.py
from graphviz import Digraph

def build_graph(nodes, edges, annotations=None, layers=None):
    dot = Digraph(format="png")
    dot.attr(rankdir="LR", concentrate="true")

    # If layers exist, place nodes into subgraphs
    if layers:
        for layer_name, comps in layers.items():
            with dot.subgraph(name=f"cluster_{layer_name}") as sub:
                sub.attr(label=layer_name.upper(), style="filled", color="#e0e0e0")
                for c in comps:
                    label = f"{c}\n{annotations.get(c, '')}" if annotations else c
                    sub.node(c, label)
    else:
        # no layers → normal nodes
        for n in nodes:
            label = f"{n}\n{annotations.get(n,'')}" if annotations else n
            dot.node(n, label)

    # Draw edges
    for src, dst in edges:
        dot.edge(src, dst)

    return dot
