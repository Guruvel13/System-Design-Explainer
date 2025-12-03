from graphviz import Digraph

def build_graph(nodes, edges):
    dot = Digraph(format="png")
    dot.attr(rankdir="LR")

    for n in nodes:
        dot.node(n, n)

    for src, dst in edges:
        dot.edge(src, dst)

    return dot
