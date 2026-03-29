"""
Graph builder for engagement network analysis.
Constructs a NetworkX directed graph from engagement data.
"""

import networkx as nx
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime


def build_graph(engagements: List[Dict[str, Any]]) -> nx.DiGraph:
    """
    Build a directed engagement graph.

    Nodes = users
    Edges = engagement interactions (with weight = count, type annotations)
    """
    G = nx.DiGraph()

    # Aggregate edges
    edge_data = defaultdict(lambda: {"weight": 0, "types": [], "timestamps": []})

    for eng in engagements:
        source = eng.get("source_user_id", "")
        target = eng.get("target_user_id", "")

        if not source or not target or source == target:
            continue

        edge_key = (source, target)
        edge_data[edge_key]["weight"] += 1
        edge_data[edge_key]["types"].append(eng.get("engagement_type", "unknown"))

        ts = eng.get("engagement_timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        if isinstance(ts, datetime):
            edge_data[edge_key]["timestamps"].append(ts)

        # Add/update node attributes
        if source not in G:
            G.add_node(source, node_type="user", engagement_count=0)
        G.nodes[source]["engagement_count"] = G.nodes[source].get("engagement_count", 0) + 1

        # Add metadata if available
        for field in ["source_follower_count", "source_following_count", "source_account_age_days"]:
            val = eng.get(field)
            if val is not None:
                node_field = field.replace("source_", "")
                G.nodes[source][node_field] = val

        if target not in G:
            G.add_node(target, node_type="user", engagement_count=0)

    # Add edges with attributes
    for (source, target), data in edge_data.items():
        G.add_edge(
            source, target,
            weight=data["weight"],
            types=list(set(data["types"])),
            interaction_count=data["weight"],
        )

    return G


def graph_to_serializable(G: nx.DiGraph) -> Dict[str, Any]:
    """
    Convert graph to a JSON-serializable format for frontend visualization.
    """
    nodes = []
    for node_id, attrs in G.nodes(data=True):
        nodes.append({
            "id": node_id,
            "label": attrs.get("username", node_id[:8]),
            **{k: v for k, v in attrs.items() if k != "username"},
        })

    edges = []
    for source, target, attrs in G.edges(data=True):
        edges.append({
            "source": source,
            "target": target,
            "weight": attrs.get("weight", 1),
            "types": attrs.get("types", []),
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "node_count": G.number_of_nodes(),
        "edge_count": G.number_of_edges(),
    }
