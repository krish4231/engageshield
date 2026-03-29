"""
AI Insight Generator.
Converts detection engine outputs into human-readable, actionable insights.
Uses template-based generation with optional LLM integration hook.
"""

from typing import Dict, Any, List
from app.detection.insight_engine.templates import (
    INSIGHT_TEMPLATES,
    SEVERITY_TEMPLATES,
    get_severity,
    get_category,
)


def generate_insights(
    ml_result: Dict[str, Any],
    behavioral_result: Dict[str, Any],
    graph_result: Dict[str, Any],
    features: Dict[str, float] = None,
) -> Dict[str, Any]:
    """
    Generate comprehensive human-readable insights from all detection engine outputs.

    Args:
        ml_result: Output from ML engine
        behavioral_result: Output from behavioral engine
        graph_result: Output from graph engine
        features: Extracted features for the analyzed entity

    Returns:
        Structured insight with summary, details, recommendations.
    """
    features = features or {}

    # Calculate composite threat score (weighted average)
    ml_score = ml_result.get("score", 0)
    behavior_score = behavioral_result.get("score", 0)
    graph_score = graph_result.get("score", 0)

    composite_score = (
        ml_score * 0.35
        + behavior_score * 0.30
        + graph_score * 0.35
    )

    severity = get_severity(composite_score)
    category = get_category(ml_result, behavioral_result, graph_result)

    # Generate primary insight
    primary_insight = _generate_primary_insight(
        category, composite_score, ml_result, behavioral_result, graph_result, features
    )

    # Generate per-engine summaries
    engine_summaries = _generate_engine_summaries(ml_result, behavioral_result, graph_result)

    # Generate recommendations
    recommendations = _generate_recommendations(severity, category, composite_score)

    # Collect all evidence
    evidence = _collect_evidence(ml_result, behavioral_result, graph_result)

    return {
        "score": round(composite_score, 4),
        "confidence": round(
            (ml_result.get("confidence", 0.5) + behavioral_result.get("confidence", 0.5) + graph_result.get("confidence", 0.5)) / 3,
            4
        ),
        "severity": severity,
        "category": category,
        "primary_insight": primary_insight,
        "engine_summaries": engine_summaries,
        "recommendations": recommendations,
        "evidence": evidence,
    }


def _generate_primary_insight(
    category: str,
    composite_score: float,
    ml_result: Dict,
    behavioral_result: Dict,
    graph_result: Dict,
    features: Dict,
) -> str:
    """Generate the primary human-readable insight."""
    ml_score = ml_result.get("score", 0)
    behavior_score = behavioral_result.get("score", 0)
    graph_score = graph_result.get("score", 0)

    if category == "clean":
        return INSIGHT_TEMPLATES["clean_profile"].format(
            ml_score=ml_score,
            behavior_score=behavior_score,
            graph_score=graph_score,
        )

    if category == "coordinated_network":
        clusters = graph_result.get("clusters", [])
        coord = graph_result.get("coordinated_behavior", {})
        return INSIGHT_TEMPLATES["coordinated_network"].format(
            cluster_count=len(clusters),
            coord_pairs=coord.get("total_pairs", 0),
            density=graph_result.get("graph_stats", {}).get("density", 0),
        )

    if category == "bot_detected":
        reasons = ml_result.get("reasons", [])
        indicators = "; ".join(reasons[:3]) if reasons else "multiple ML feature anomalies"
        return INSIGHT_TEMPLATES["bot_account"].format(
            score=ml_score,
            indicators=indicators,
            frequency=features.get("engagement_frequency", 0),
            diversity=features.get("interaction_diversity", 0),
        )

    if category == "burst_activity":
        anomalies = behavioral_result.get("anomalies", [])
        burst_anomalies = [a for a in anomalies if "burst" in a.get("type", "")]
        burst_count = len(burst_anomalies)
        anomaly_details = "; ".join(a.get("description", "") for a in anomalies[:3])
        return INSIGHT_TEMPLATES["burst_activity"].format(
            burst_count=burst_count,
            anomaly_details=anomaly_details or "Multiple behavioral anomalies detected",
        )

    # Default fallback
    return (
        f"Analysis complete with composite threat score of {composite_score:.0%}. "
        f"ML engine scored {ml_score:.0%}, behavioral analysis scored {behavior_score:.0%}, "
        f"and graph analysis scored {graph_score:.0%}. Further investigation recommended."
    )


def _generate_engine_summaries(
    ml_result: Dict, behavioral_result: Dict, graph_result: Dict
) -> List[Dict[str, str]]:
    """Generate concise summaries for each detection engine."""
    summaries = []

    # ML Engine
    ml_method = ml_result.get("method", "unknown")
    ml_label = ml_result.get("label", "unknown")
    summaries.append({
        "engine": "ML Classification",
        "score": ml_result.get("score", 0),
        "summary": f"Model ({ml_method}) classified account as '{ml_label}' "
                   f"with {ml_result.get('confidence', 0):.0%} confidence",
    })

    # Behavioral Engine
    anomaly_count = len(behavioral_result.get("anomalies", []))
    summaries.append({
        "engine": "Behavioral Analysis",
        "score": behavioral_result.get("score", 0),
        "summary": f"Detected {anomaly_count} behavioral anomalies. "
                   f"{'Bot-like patterns confirmed.' if behavioral_result.get('is_bot_like') else 'Patterns within normal range.'}",
    })

    # Graph Engine
    clusters = graph_result.get("clusters", [])
    coord_groups = graph_result.get("coordinated_behavior", {}).get("coordinated_groups", [])
    summaries.append({
        "engine": "Graph Analysis",
        "score": graph_result.get("score", 0),
        "summary": f"Found {len(clusters)} suspicious clusters, "
                   f"{len(coord_groups)} coordinated user pairs in the engagement network",
    })

    return summaries


def _generate_recommendations(severity: str, category: str, score: float) -> List[str]:
    """Generate actionable recommendations based on detection results."""
    recs = []

    if severity == "critical":
        recs.append("IMMEDIATE ACTION: Flag account for priority review by trust & safety team")
        recs.append("Consider temporary rate limiting or engagement restrictions")
        recs.append("Investigate connected accounts in the same network cluster")

    elif severity == "high":
        recs.append("Add account to monitoring watchlist for continued observation")
        recs.append("Review recent engagement patterns for confirmation")
        recs.append("Check if account is part of a larger coordinated network")

    elif severity == "medium":
        recs.append("Monitor account activity over the next 7 days")
        recs.append("Consider implementing engagement velocity limits")

    else:
        recs.append("No immediate action required")
        recs.append("Standard monitoring will continue")

    if category == "coordinated_network":
        recs.append("Map the full network of connected accounts for bulk review")

    if category == "burst_activity":
        recs.append("Implement rate limiting for this account type")

    return recs


def _collect_evidence(
    ml_result: Dict, behavioral_result: Dict, graph_result: Dict
) -> Dict[str, Any]:
    """Collect key evidence from all engines into a unified structure."""
    return {
        "ml": {
            "score": ml_result.get("score", 0),
            "method": ml_result.get("method", "unknown"),
            "label": ml_result.get("label", "unknown"),
            "reasons": ml_result.get("reasons", []),
        },
        "behavioral": {
            "score": behavioral_result.get("score", 0),
            "anomaly_count": len(behavioral_result.get("anomalies", [])),
            "anomalies": behavioral_result.get("anomalies", [])[:5],
            "is_bot_like": behavioral_result.get("is_bot_like", False),
        },
        "graph": {
            "score": graph_result.get("score", 0),
            "cluster_count": len(graph_result.get("clusters", [])),
            "coordinated_pairs": graph_result.get("coordinated_behavior", {}).get("total_pairs", 0),
            "graph_stats": graph_result.get("graph_stats", {}),
        },
    }
