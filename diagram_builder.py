# diagram_builder.py
from graphviz import Digraph
import textwrap


def _wrap(text: str, width: int = 18) -> str:
    """Wrap text so long node labels look clean."""
    return "\n".join(textwrap.wrap(text, width))


def build_graph(
    nodes,
    edges,
    annotations=None,
    layers=None,
    edge_types=None,
    dark_mode=False
):
    """
    Build a clean, professional architecture diagram.
    Works without system Graphviz (Streamlit Cloud safe because we export via Kroki).
    """

    # Theme
    bg = "#0f0f0f" if dark_mode else "white"
    font = "white" if dark_mode else "black"
    cluster_bg = "#202020" if dark_mode else "#f5f5f5"
    node_bg = "#1b1b1b" if dark_mode else "#ffffff"

    dot = Digraph(format="svg")   # safe default for Streamlit UI
    dot.attr(rankdir="LR", bgcolor=bg)

    annotations = annotations or {}
    layers = layers or {}
    edge_types = edge_types or {}

    # -----------------------------------------
    # LAYERED MODE
    # -----------------------------------------
    if layers:
        for layer_name, comps in layers.items():

            with dot.subgraph(name=f"cluster_{layer_name}") as sub:
                sub.attr(
                    label=layer_name.upper(),
                    style="filled",
                    bgcolor=cluster_bg,
                    color="#888888",
                    fontcolor=font
                )

                for comp in comps:
                    desc = annotations.get(comp, "").strip()
                    label = _wrap(f"{comp}\n{desc}" if desc else comp)

                    sub.node(
                        comp,
                        label=label,
                        fillcolor=node_bg,
                        style="filled",
                        fontcolor=font,
                        shape="box",
                        penwidth="1.8"
                    )

    # -----------------------------------------
    # NON-LAYERED MODE
    # -----------------------------------------
    else:
        for comp in nodes:
            desc = annotations.get(comp, "").strip()
            label = _wrap(f"{comp}\n{desc}" if desc else comp)

            dot.node(
                comp,
                label=label,
                style="filled",
                fillcolor=node_bg,
                fontcolor=font,
                shape="box",
                penwidth="1.8"
            )

    # -----------------------------------------
    # EDGES WITH TYPE LABELS
    # -----------------------------------------
    for src, dst in edges:
        etype = edge_types.get(f"{src}->{dst}", "")
        dot.edge(
            src,
            dst,
            label=etype,
            fontsize="12",
            color="#b3b3b3",
            fontcolor=font
        )

    return dot
