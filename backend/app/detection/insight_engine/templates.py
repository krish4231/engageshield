"""
Insight templates for generating human-readable explanations from detection results.
"""

SEVERITY_TEMPLATES = {
    "critical": "🚨 CRITICAL THREAT: {description}",
    "high": "⚠️ HIGH RISK: {description}",
    "medium": "⚡ MODERATE CONCERN: {description}",
    "low": "ℹ️ LOW RISK: {description}",
}

INSIGHT_TEMPLATES = {
    "coordinated_network": (
        "High likelihood of coordinated fake engagement detected. "
        "{cluster_count} dense clusters identified with {coord_pairs} coordinated user pairs. "
        "Synchronized activity patterns and dense cluster formation suggest organized manipulation. "
        "Graph density of {density} significantly exceeds normal engagement patterns."
    ),
    "bot_account": (
        "Account exhibits strong bot-like characteristics with a threat score of {score:.0%}. "
        "Key indicators: {indicators}. "
        "Engagement frequency of {frequency:.1f} actions/hour with {diversity:.0%} interaction diversity "
        "falls outside normal human behavioral ranges."
    ),
    "burst_activity": (
        "Abnormal burst activity detected with {burst_count} rapid engagement spikes. "
        "{anomaly_details}. "
        "This pattern is characteristic of automated engagement tools that execute "
        "mass actions in short windows."
    ),
    "temporal_anomaly": (
        "Temporal analysis reveals non-human activity patterns. "
        "{circadian_detail}. "
        "Activity shows {entropy_level} time entropy ({entropy:.2f}), indicating "
        "{entropy_interpretation}."
    ),
    "engagement_manipulation": (
        "Engagement manipulation indicators present. "
        "The account shows {pattern_count} known bot pattern matches: {patterns}. "
        "Combined with a behavioral score of {behavior_score:.0%} and ML score of {ml_score:.0%}, "
        "this strongly suggests artificial engagement inflation."
    ),
    "clean_profile": (
        "Account appears legitimate based on comprehensive analysis. "
        "All detection engines report low risk scores (ML: {ml_score:.0%}, "
        "Behavioral: {behavior_score:.0%}, Graph: {graph_score:.0%}). "
        "Engagement patterns are consistent with organic human activity."
    ),
}


def get_severity(score: float) -> str:
    """Determine severity level from composite threat score."""
    if score >= 0.85:
        return "critical"
    elif score >= 0.65:
        return "high"
    elif score >= 0.40:
        return "medium"
    else:
        return "low"


def get_category(ml_result: dict, behavioral_result: dict, graph_result: dict) -> str:
    """Determine the primary threat category based on which engine scored highest."""
    scores = {
        "bot_detected": ml_result.get("score", 0),
        "burst_activity": behavioral_result.get("score", 0),
        "coordinated_network": graph_result.get("score", 0),
    }

    if max(scores.values()) < 0.3:
        return "clean"

    return max(scores, key=scores.get)
