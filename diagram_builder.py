# diagram_builder.py
from graphviz import Digraph

def build_graph(nodes, edges, annotations=None, layers=None, edge_types=None, dark_mode=True):
    if dark_mode:
        bg = "#0f0f0f"
        font = "white"
        cluster = "#2b2b2b"
        box = "#1e1e1e"
    else:
        bg = "white"
        font = "black"
        cluster = "#f0f0f0"
        box = "#ffffff"

    dot = Digraph()
    dot.attr(rankdir="LR", bgcolor=bg, fontcolor=font)

    # Draw layers
    if layers:
        for lname, comps in layers.items():
            with dot.subgraph(name=f"cluster_{lname}") as sub:
                sub.attr(label=lname.upper(), style="filled", bgcolor=cluster)

                for c in comps:
                    desc = annotations.get(c, "") if annotations else ""
                    label = f"{c}\n{desc}" if desc else c
                    sub.node(c, label=label, style="filled", fillcolor=box, fontcolor=font)
    else:
        for c in nodes:
            desc = annotations.get(c, "") if annotations else ""
            label = f"{c}\n{desc}" if desc else c
            dot.node(c, label=label, style="filled", fillcolor=box, fontcolor=font)

    # Edges
    for src, dst in edges:
        elabel = edge_types.get(f"{src}->{dst}", "") if edge_types else ""
        dot.edge(src, dst, label=elabel, fontcolor=font)

    return dot
