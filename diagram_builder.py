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
    Supports layers, annotations, and edge-type labels.
    Works for both layered and non-layered diagrams.
    """

    annotations = annotations or {}
    layers = layers or {}
    edge_types = edge_types or {}

    # Theme settings
    if dark_mode:
        bg_color = "#0f0f0f"
        font_color = "white"
        cluster_color = "#2b2b2b"
        node_color = "#1e1e1e"
        edge_color = "#bfbfbf"
    else:
        bg_color = "white"
        font_color = "black"
        cluster_color = "#f0f0f0"
        node_color = "#ffffff"
        edge_color = "#333333"

    dot = Digraph(format="png")
    dot.attr(
        rankdir="LR",
        bgcolor=bg_color,
        fontcolor=font_color,
        color=font_color,
        concentrate="true",
        splines="spline"
    )

    # Build layered diagram if available
    if layers:
        for layer_name, comps in layers.items():
            with dot.subgraph(name=f"cluster_{layer_name}") as sub:
                sub.attr(
                    label=layer_name.upper(),
                    style="filled",
                    bgcolor=cluster_color,
                    color="#888888",
                    fontcolor=font_color
                )

                for comp in comps:
                    desc = annotations.get(comp, "")
                    label = f"{comp}\n{desc}" if desc else comp
                    sub.node(
                        comp,
                        label=label,
                        style="filled",
                        fillcolor=node_color,
                        fontcolor=font_color,
                        shape="box",
                        penwidth="1.8"
                    )
    else:
        # Fallback → draw nodes normally
        for comp in nodes:
            desc = annotations.get(comp, "")
            label = f"{comp}\n{desc}" if desc else comp
            dot.node(
                comp,
                label=label,
                style="filled",
                fillcolor=node_color,
                fontcolor=font_color,
                shape="box",
                penwidth="1.8"
            )

    # Draw edges with types
    for src, dst in edges:
        if not src or not dst:
            continue

        label = edge_types.get(f"{src}->{dst}", "")

        dot.edge(
            src,
            dst,
            label=label,
            fontsize="12",
            color=edge_color,
            fontcolor=font_color
        )

    return dot
