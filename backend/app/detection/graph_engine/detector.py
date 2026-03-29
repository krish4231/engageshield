"""
Graph-based detection for coordinated fake engagement networks.
Uses community detection, cycle analysis, and synchronized behavior detection.
"""

import networkx as nx
import numpy as np
from typing import List, Dict, Any, Set
from collections import defaultdict
from datetime import datetime, timedelta

try:
    import community as community_louvain
    HAS_LOUVAIN = True
except ImportError:
    HAS_LOUVAIN = False


def detect_suspicious_clusters(G: nx.DiGraph) -> Dict[str, Any]:
    """
    Run all graph-based detection algorithms.

    Returns:
        Combined results from community detection, cycle analysis,
        and coordinated behavior detection.
    """
    if G.number_of_nodes() < 3:
        return {"score": 0.0, "clusters": [], "details": {}}

    # Convert to undirected for community detection
    G_undirected = G.to_undirected()

    # Run detection algorithms
    communities = detect_communities(G_undirected)
    dense_clusters = find_dense_clusters(G, communities)
    cycles = detect_repetitive_loops(G)
    coordinated = detect_coordinated_behavior(G)

    # Calculate composite score
    scores = []
    if dense_clusters:
        scores.append(min(len(dense_clusters) * 0.2, 0.8))
    if cycles["suspicious_cycles"]:
        scores.append(min(len(cycles["suspicious_cycles"]) * 0.15, 0.6))
    if coordinated["coordinated_groups"]:
        scores.append(min(len(coordinated["coordinated_groups"]) * 0.25, 0.9))

    composite_score = max(scores) if scores else 0.0

    return {
        "score": round(composite_score, 4),
        "confidence": round(0.7 + composite_score * 0.25, 4),
        "clusters": dense_clusters,
        "communities": communities,
        "cycles": cycles,
        "coordinated_behavior": coordinated,
        "graph_stats": {
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "density": round(nx.density(G), 6),
        },
    }


def detect_communities(G_undirected: nx.Graph) -> Dict[str, Any]:
    """
    Detect communities using Louvain method with fallback to connected components.
    """
    if G_undirected.number_of_nodes() < 2:
        return {"method": "none", "communities": {}, "modularity": 0.0}

    if HAS_LOUVAIN and G_undirected.number_of_nodes() > 2:
        try:
            partition = community_louvain.best_partition(G_undirected)
            modularity = community_louvain.modularity(partition, G_undirected)

            # Group nodes by community
            communities = defaultdict(list)
            for node, comm_id in partition.items():
                communities[str(comm_id)].append(node)

            return {
                "method": "louvain",
                "communities": dict(communities),
                "modularity": round(modularity, 4),
                "num_communities": len(communities),
            }
        except Exception:
            pass

    # Fallback to connected components
    components = list(nx.connected_components(G_undirected))
    communities = {str(i): list(comp) for i, comp in enumerate(components)}

    return {
        "method": "connected_components",
        "communities": communities,
        "modularity": 0.0,
        "num_communities": len(communities),
    }


def find_dense_clusters(
    G: nx.DiGraph, community_result: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Identify suspiciously dense clusters within detected communities.
    A cluster is suspicious if its density is significantly higher than expected.
    """
    suspicious = []
    communities = community_result.get("communities", {})

    for comm_id, members in communities.items():
        if len(members) < 3:
            continue

        # Get subgraph for this community
        subgraph = G.subgraph(members)
        density = nx.density(subgraph)
        avg_degree = sum(dict(subgraph.degree()).values()) / max(len(members), 1)

        # A cluster is suspicious if:
        # 1. High density (> 0.5 for groups of 5+)
        # 2. High average degree relative to group size
        is_suspicious = False
        reasons = []

        if density > 0.5 and len(members) >= 5:
            is_suspicious = True
            reasons.append(f"Very high density ({density:.2f}) for {len(members)} members")

        if avg_degree > len(members) * 0.6:
            is_suspicious = True
            reasons.append(f"High avg degree ({avg_degree:.1f}) relative to group size")

        if is_suspicious:
            suspicious.append({
                "community_id": comm_id,
                "members": members[:20],  # Limit for response size
                "member_count": len(members),
                "density": round(density, 4),
                "avg_degree": round(avg_degree, 2),
                "reasons": reasons,
            })

    return suspicious


def detect_repetitive_loops(G: nx.DiGraph) -> Dict[str, Any]:
    """
    Detect repetitive interaction cycles (A→B→C→A patterns).
    These indicate coordinated engagement rings.
    """
    try:
        cycles = list(nx.simple_cycles(G))
        # Limit to short cycles (2-5 nodes) which are most suspicious
        short_cycles = [c for c in cycles if 2 <= len(c) <= 5]

        suspicious_cycles = []
        for cycle in short_cycles[:20]:  # Limit output
            # Check if cycle edges have high weight (repeated interactions)
            cycle_weight = 0
            for i in range(len(cycle)):
                src = cycle[i]
                dst = cycle[(i + 1) % len(cycle)]
                if G.has_edge(src, dst):
                    cycle_weight += G[src][dst].get("weight", 1)

            if cycle_weight > len(cycle) * 2:  # Average weight > 2 per edge
                suspicious_cycles.append({
                    "nodes": cycle,
                    "length": len(cycle),
                    "total_weight": cycle_weight,
                    "avg_weight": round(cycle_weight / len(cycle), 2),
                })

        return {
            "total_cycles": len(short_cycles),
            "suspicious_cycles": suspicious_cycles,
        }
    except Exception:
        return {"total_cycles": 0, "suspicious_cycles": []}


def detect_coordinated_behavior(G: nx.DiGraph) -> Dict[str, Any]:
    """
    Detect coordinated engagement: groups of users targeting the same accounts
    with similar patterns.
    """
    # Find users that share many targets
    user_targets = defaultdict(set)
    for source, target in G.edges():
        user_targets[source].add(target)

    coordinated_groups = []
    users = list(user_targets.keys())

    for i in range(len(users)):
        for j in range(i + 1, len(users)):
            if len(users) > 100 and j > i + 50:
                break  # Limit pairwise comparisons for large graphs

            shared = user_targets[users[i]] & user_targets[users[j]]
            total = user_targets[users[i]] | user_targets[users[j]]

            if len(total) == 0:
                continue

            jaccard = len(shared) / len(total)

            if jaccard > 0.6 and len(shared) >= 3:
                coordinated_groups.append({
                    "users": [users[i], users[j]],
                    "shared_targets": list(shared)[:10],
                    "shared_count": len(shared),
                    "jaccard_similarity": round(jaccard, 4),
                })

    # Sort by similarity
    coordinated_groups.sort(key=lambda x: x["jaccard_similarity"], reverse=True)

    return {
        "coordinated_groups": coordinated_groups[:20],
        "total_pairs": len(coordinated_groups),
    }
