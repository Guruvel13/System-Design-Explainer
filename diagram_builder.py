# diagram_builder.py
from graphviz import Digraph


def build_graph(
    nodes,
    edges,
    annotations=None,
    layers=None,
    edge_types=None,
    dark_mode=False
):
    """
    Builds a clean, professional architecture diagram using Graphviz.
    Supports layers, annotations, edge types, and dark/light themes.
    """

    # Theme settings
    if dark_mode:
        bg_color = "#0f0f0f"
        font_color = "white"
        cluster_color = "#2b2b2b"
        node_color = "#1e1e1e"
    else:
        bg_color = "white"
        font_color = "black"
        cluster_color = "#f0f0f0"
        node_color = "#ffffff"

    dot = Digraph(format="png")
    dot.attr(
        rankdir="LR",
        bgcolor=bg_color,
        fontcolor=font_color,
        color=font_color,
        concentrate="true"
    )

    # Build layered diagram
    if layers:
        for layer_name, comps in layers.items():
            with dot.subgraph(name=f"cluster_{layer_name}") as sub:
                sub.attr(
                    label=layer_name.upper(),
                    style="filled",
                    bgcolor=cluster_color,
                    color="#999999",
                    fontcolor=font_color
                )
                for comp in comps:
                    desc = annotations.get(comp, "") if annotations else ""
                    label = f"{comp}\n{desc}" if desc else comp
                    sub.node(
                        comp,
                        label=label,
                        style="filled",
                        fillcolor=node_color,
                        fontcolor=font_color,
                        shape="box",
                        penwidth="1.5"
                    )
    else:
        # Non-layered fallback
        for comp in nodes:
            desc = annotations.get(comp, "") if annotations else ""
            label = f"{comp}\n{desc}" if desc else comp
            dot.node(
                comp,
                label=label,
                style="filled",
                fillcolor=node_color,
                fontcolor=font_color,
                shape="box",
                penwidth="1.5"
            )

    # Draw edges with optional edge type labels (HTTP, Kafka, gRPC…)
    for src, dst in edges:
        label = ""
        if edge_types:
            key = f"{src}->{dst}"
            label = edge_types.get(key, "")

        dot.edge(
            src,
            dst,
            label=label,
            fontsize="12",
            color="#6c6c6c",
            fontcolor=font_color
        )

    return dot
