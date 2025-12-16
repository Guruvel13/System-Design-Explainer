# diagram_builder.py
# Enhanced diagram builder with multiple themes, node types, and advanced styling

from graphviz import Digraph
import textwrap
import logging
from typing import List, Dict, Optional, Literal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Color themes
THEMES = {
    "dark": {
        "bg": "#0f0f0f",
        "font": "white",
        "cluster_bg": "#202020",
        "node_bg": "#1b1b1b",
        "node_border": "#667eea",
        "edge_color": "#b3b3b3"
    },
    "light": {
        "bg": "white",
        "font": "black",
        "cluster_bg": "#f5f5f5",
        "node_bg": "#ffffff",
        "node_border": "#667eea",
        "edge_color": "#666666"
    },
    "blue": {
        "bg": "#0a1929",
        "font": "#e3f2fd",
        "cluster_bg": "#1e3a5f",
        "node_bg": "#1565c0",
        "node_border": "#42a5f5",
        "edge_color": "#90caf9"
    },
    "purple": {
        "bg": "#1a0033",
        "font": "#e1bee7",
        "cluster_bg": "#4a148c",
        "node_bg": "#6a1b9a",
        "node_border": "#ab47bc",
        "edge_color": "#ce93d8"
    },
    "green": {
        "bg": "#0d1b0d",
        "font": "#c8e6c9",
        "cluster_bg": "#1b5e20",
        "node_bg": "#2e7d32",
        "node_border": "#66bb6a",
        "edge_color": "#a5d6a7"
    }
}

# Node shapes for different component types
NODE_SHAPES = {
    "default": "box",
    "database": "cylinder",
    "service": "component",
    "user": "person",
    "cache": "folder",
    "queue": "box3d",
    "storage": "cylinder",
    "api": "hexagon",
    "load_balancer": "diamond",
    "gateway": "trapezium"
}


def _wrap(text: str, width: int = 18) -> str:
    """Wrap text to specified width for better readability."""
    if not text:
        return ""
    return "\n".join(textwrap.wrap(text, width))


def _detect_node_type(node_name: str) -> str:
    """
    Auto-detect node type based on name keywords.
    
    Returns:
        Shape name from NODE_SHAPES
    """
    node_lower = node_name.lower()
    
    if any(kw in node_lower for kw in ["db", "database", "postgres", "mysql", "mongo"]):
        return "database"
    if any(kw in node_lower for kw in ["cache", "redis", "memcached"]):
        return "cache"
    if any(kw in node_lower for kw in ["queue", "kafka", "rabbitmq", "sqs"]):
        return "queue"
    if any(kw in node_lower for kw in ["storage", "s3", "blob", "bucket"]):
        return "storage"
    if any(kw in node_lower for kw in ["api", "gateway", "endpoint"]):
        return "api"
    if any(kw in node_lower for kw in ["balancer", "lb", "load"]):
        return "load_balancer"
    if any(kw in node_lower for kw in ["user", "client", "customer"]):
        return "user"
    if any(kw in node_lower for kw in ["service", "microservice", "server"]):
        return "service"
    
    return "default"


def _get_node_shape(
    node_name: str,
    node_types: Optional[Dict[str, str]] = None,
    auto_detect: bool = True
) -> str:
    """
    Get the appropriate shape for a node.
    
    Args:
        node_name: Name of the node
        node_types: Manual mapping of node names to types
        auto_detect: Whether to auto-detect type from name
    
    Returns:
        Graphviz shape name
    """
    # Check manual mapping first
    if node_types and node_name in node_types:
        node_type = node_types[node_name]
        return NODE_SHAPES.get(node_type, NODE_SHAPES["default"])
    
    # Auto-detect if enabled
    if auto_detect:
        detected_type = _detect_node_type(node_name)
        return NODE_SHAPES[detected_type]
    
    return NODE_SHAPES["default"]


def build_graph(
    nodes: List[str],
    edges: List[List[str]],
    annotations: Optional[Dict[str, str]] = None,
    layers: Optional[Dict[str, List[str]]] = None,
    edge_types: Optional[Dict[str, str]] = None,
    dark_mode: bool = False,
    theme: Literal["dark", "light", "blue", "purple", "green"] = None,
    node_types: Optional[Dict[str, str]] = None,
    auto_detect_types: bool = True,
    rankdir: Literal["LR", "TB", "RL", "BT"] = "LR",
    output_format: Literal["svg", "png", "pdf"] = "svg"
) -> Digraph:
    """
    Build a professional architecture diagram using Graphviz.
    
    Args:
        nodes: List of node names
        edges: List of [source, target] pairs
        annotations: Optional node descriptions
        layers: Optional layer grouping {layer_name: [nodes]}
        edge_types: Optional edge labels {src->dst: label}
        dark_mode: Use dark theme (deprecated, use theme instead)
        theme: Color theme name
        node_types: Manual node type mapping {node_name: type}
        auto_detect_types: Auto-detect node types from names
        rankdir: Graph direction (LR, TB, RL, BT)
        output_format: Output format
    
    Returns:
        Graphviz Digraph object
    """
    # Validate inputs
    if not nodes:
        raise ValueError("Node list cannot be empty")
    
    if not all(isinstance(n, str) for n in nodes):
        raise ValueError("All nodes must be strings")
    
    # Determine theme
    if theme:
        if theme not in THEMES:
            logger.warning(f"Unknown theme '{theme}', falling back to 'dark'")
            theme = "dark"
        colors = THEMES[theme]
    else:
        theme_name = "dark" if dark_mode else "light"
        colors = THEMES[theme_name]
    
    logger.info(f"Building graph with theme '{theme or ('dark' if dark_mode else 'light')}'")
    
    # Initialize graph
    dot = Digraph(format=output_format)
    dot.attr(
        rankdir=rankdir,
        bgcolor=colors["bg"],
        fontname="Inter, Arial, sans-serif",
        fontsize="12",
        splines="ortho",  # Orthogonal edges for cleaner look
        nodesep="0.8",
        ranksep="1.2"
    )
    
    # Set default node attributes
    dot.attr(
        'node',
        style="filled,rounded",
        fontname="Inter, Arial, sans-serif",
        fontsize="11",
        margin="0.2,0.1"
    )
    
    # Set default edge attributes
    dot.attr(
        'edge',
        fontname="Inter, Arial, sans-serif",
        fontsize="10",
        penwidth="2.0"
    )
    
    # Initialize containers
    annotations = annotations or {}
    layers = layers or {}
    edge_types = edge_types or {}
    
    # Build nodes with layers
    if layers:
        logger.info(f"Creating {len(layers)} layer(s)")
        for layer_idx, (lname, comps) in enumerate(layers.items()):
            with dot.subgraph(name=f"cluster_{layer_idx}_{lname}") as sub:
                sub.attr(
                    label=lname.upper(),
                    style="filled,rounded",
                    bgcolor=colors["cluster_bg"],
                    color=colors["node_border"],
                    fontcolor=colors["font"],
                    fontsize="14",
                    fontname="Inter, Arial, sans-serif",
                    penwidth="2.0"
                )
                
                for comp in comps:
                    if comp not in nodes:
                        logger.warning(f"Layer '{lname}' references non-existent node '{comp}'")
                        continue
                    
                    desc = annotations.get(comp, "").strip()
                    label = _wrap(f"{comp}\n{desc}" if desc else comp, width=20)
                    shape = _get_node_shape(comp, node_types, auto_detect_types)
                    
                    sub.node(
                        comp,
                        label=label,
                        fillcolor=colors["node_bg"],
                        fontcolor=colors["font"],
                        shape=shape,
                        penwidth="2.0",
                        color=colors["node_border"]
                    )
    else:
        # Create nodes without layers
        logger.info(f"Creating {len(nodes)} node(s) without layers")
        for comp in nodes:
            desc = annotations.get(comp, "").strip()
            label = _wrap(f"{comp}\n{desc}" if desc else comp, width=20)
            shape = _get_node_shape(comp, node_types, auto_detect_types)
            
            dot.node(
                comp,
                label=label,
                style="filled,rounded",
                fillcolor=colors["node_bg"],
                fontcolor=colors["font"],
                shape=shape,
                penwidth="2.0",
                color=colors["node_border"]
            )
    
    # Build edges
    logger.info(f"Creating {len(edges)} edge(s)")
    for src, dst in edges:
        if src not in nodes:
            logger.warning(f"Edge source '{src}' not in node list")
            continue
        if dst not in nodes:
            logger.warning(f"Edge destination '{dst}' not in node list")
            continue
        
        edge_key = f"{src}->{dst}"
        label = edge_types.get(edge_key, "")
        
        dot.edge(
            src,
            dst,
            label=label,
            fontsize="10",
            color=colors["edge_color"],
            fontcolor=colors["font"],
            penwidth="2.0"
        )
    
    logger.info("Graph built successfully")
    return dot


def get_available_themes() -> List[str]:
    """Get list of available color themes."""
    return list(THEMES.keys())


def get_available_node_types() -> List[str]:
    """Get list of available node types."""
    return list(NODE_SHAPES.keys())


def preview_theme(theme_name: str) -> Dict[str, str]:
    """
    Preview a theme's color palette.
    
    Returns:
        Theme colors or None if theme doesn't exist
    """
    return THEMES.get(theme_name, None)
