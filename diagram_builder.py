# diagram_builder.py
from graphviz import Digraph

def build_graph(nodes, edges, annotations=None, layers=None, edge_types=None, dark_mode=False):
    bg = "#0f0f0f" if dark_mode else "white"
    font = "white" if dark_mode else "black"
    cluster_bg = "#2b2b2b" if dark_mode else "#f5f5f5"
    node_bg = "#1e1e1e" if dark_mode else "#ffffff"

    dot = Digraph()
    dot.attr(rankdir="LR", bgcolor=bg)

    if layers:
        for lname, comps in layers.items():
            with dot.subgraph(name=f"cluster_{lname}") as sub:
                sub.attr(label=lname.upper(), style="filled", bgcolor=cluster_bg)
                for comp in comps:
                    desc = (annotations or {}).get(comp, "")
                    sub.node(comp, f"{comp}\n{desc}", fillcolor=node_bg, style="filled", fontcolor=font)
    else:
        for comp in nodes:
            desc = (annotations or {}).get(comp, "")
            dot.node(comp, f"{comp}\n{desc}", fillcolor=node_bg, style="filled", fontcolor=font)

    for src, dst in edges:
        etype = (edge_types or {}).get(f"{src}->{dst}", "")
        dot.edge(src, dst, label=etype)

    return dot
