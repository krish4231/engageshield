"""
Graph metrics calculation for node-level and community-level analysis.
"""

import networkx as nx
from typing import Dict, Any, List


def calculate_node_metrics(G: nx.DiGraph) -> Dict[str, Dict[str, float]]:
    """
    Calculate per-node metrics for identifying suspicious accounts.

    Returns:
        Dictionary mapping node_id to metric dictionary.
    """
    if G.number_of_nodes() == 0:
        return {}

    metrics = {}

    # Degree centrality
    in_degree = nx.in_degree_centrality(G)
    out_degree = nx.out_degree_centrality(G)

    # Betweenness centrality (limited for large graphs)
    try:
        if G.number_of_nodes() <= 500:
            betweenness = nx.betweenness_centrality(G)
        else:
            betweenness = nx.betweenness_centrality(G, k=min(100, G.number_of_nodes()))
    except Exception:
        betweenness = {n: 0.0 for n in G.nodes()}

    # PageRank
    try:
        pagerank = nx.pagerank(G, max_iter=100)
    except Exception:
        pagerank = {n: 1.0 / G.number_of_nodes() for n in G.nodes()}

    # Clustering coefficient (on undirected version)
    G_undirected = G.to_undirected()
    clustering = nx.clustering(G_undirected)

    for node in G.nodes():
        metrics[node] = {
            "in_degree_centrality": round(in_degree.get(node, 0), 6),
            "out_degree_centrality": round(out_degree.get(node, 0), 6),
            "betweenness_centrality": round(betweenness.get(node, 0), 6),
            "pagerank": round(pagerank.get(node, 0), 6),
            "clustering_coefficient": round(clustering.get(node, 0), 6),
            "in_degree": G.in_degree(node),
            "out_degree": G.out_degree(node),
        }

        # Suspicion score based on metrics
        suspicion = _calculate_node_suspicion(metrics[node])
        metrics[node]["suspicion_score"] = round(suspicion, 4)

    return metrics


def _calculate_node_suspicion(metrics: Dict[str, float]) -> float:
    """
    Calculate a suspicion score for a node based on its graph metrics.
    High out-degree + low in-degree + high clustering = potential bot.
    """
    score = 0.0

    # Very high out-degree relative to in-degree = pushing content out
    out_in_ratio = metrics["out_degree"] / max(metrics["in_degree"], 1)
    if out_in_ratio > 10:
        score += 0.3
    elif out_in_ratio > 5:
        score += 0.15

    # Very high clustering = part of a tight-knit group (potential bot farm)
    if metrics["clustering_coefficient"] > 0.8:
        score += 0.25
    elif metrics["clustering_coefficient"] > 0.6:
        score += 0.1

    # High betweenness but low pagerank = bridge between bot clusters
    if metrics["betweenness_centrality"] > 0.1 and metrics["pagerank"] < 0.01:
        score += 0.2

    # Very high out-degree centrality
    if metrics["out_degree_centrality"] > 0.3:
        score += 0.25

    return min(score, 1.0)


def get_community_stats(G: nx.DiGraph, communities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """
    Calculate statistics for each detected community.
    """
    stats = []

    for comm_id, members in communities.items():
        if len(members) < 2:
            continue

        subgraph = G.subgraph(members)
        density = nx.density(subgraph)
        edges = subgraph.number_of_edges()

        stats.append({
            "community_id": comm_id,
            "size": len(members),
            "edges": edges,
            "density": round(density, 4),
            "avg_out_degree": round(sum(subgraph.out_degree(n) for n in members) / len(members), 2),
            "avg_in_degree": round(sum(subgraph.in_degree(n) for n in members) / len(members), 2),
        })

    return stats
