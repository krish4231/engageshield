"""
Feature extraction for ML-based fake engagement detection.
Extracts 12+ features from engagement data for each user account.
"""

import numpy as np
from typing import List, Dict, Any
from datetime import datetime
from collections import Counter
import math


def extract_features(engagements: List[Dict[str, Any]], user_id: str) -> Dict[str, float]:
    """
    Extract features for a single user from their engagement history.

    Args:
        engagements: List of engagement records for this user.
        user_id: The user to extract features for.

    Returns:
        Dictionary of feature name -> value.
    """
    if not engagements:
        return _empty_features()

    # Parse timestamps
    timestamps = []
    for eng in engagements:
        ts = eng.get("engagement_timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        if isinstance(ts, datetime):
            timestamps.append(ts)

    timestamps.sort()

    # Basic counts
    total_engagements = len(engagements)
    unique_targets = set(eng.get("target_user_id", "") for eng in engagements)
    engagement_types = [eng.get("engagement_type", "unknown") for eng in engagements]
    type_counts = Counter(engagement_types)

    # Time span
    if len(timestamps) >= 2:
        time_span_hours = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
    else:
        time_span_hours = 1.0

    time_span_hours = max(time_span_hours, 0.01)  # Avoid division by zero

    # === Feature 1: Engagement Frequency (actions per hour) ===
    engagement_frequency = total_engagements / time_span_hours

    # === Feature 2: Growth Rate (follower increase rate) ===
    follower_counts = [eng.get("source_follower_count", 0) for eng in engagements if eng.get("source_follower_count")]
    if len(follower_counts) >= 2:
        growth_rate = (follower_counts[-1] - follower_counts[0]) / max(time_span_hours / 24, 1)
    else:
        growth_rate = 0.0

    # === Feature 3: Interaction Diversity ===
    interaction_diversity = len(unique_targets) / max(total_engagements, 1)

    # === Feature 4: Temporal Variance ===
    if len(timestamps) >= 2:
        intervals = [(timestamps[i + 1] - timestamps[i]).total_seconds()
                     for i in range(len(timestamps) - 1)]
        temporal_variance = float(np.std(intervals)) if intervals else 0.0
    else:
        temporal_variance = 0.0

    # === Feature 5: Follower/Following Ratio ===
    follower_count = engagements[0].get("source_follower_count", 0) or 0
    following_count = engagements[0].get("source_following_count", 0) or 0
    follower_following_ratio = follower_count / max(following_count, 1)

    # === Feature 6: Account Age ===
    account_age_days = engagements[0].get("source_account_age_days", 365) or 365

    # === Feature 7: Average Engagement Interval ===
    if len(timestamps) >= 2:
        avg_engagement_interval = float(np.mean(intervals))
    else:
        avg_engagement_interval = 3600.0  # Default 1 hour

    # === Feature 8: Burst Score ===
    burst_score = _calculate_burst_score(timestamps)

    # === Feature 9: Unique Targets Ratio ===
    unique_targets_ratio = len(unique_targets) / max(total_engagements, 1)

    # === Feature 10: Time Entropy ===
    time_entropy = _calculate_time_entropy(timestamps)

    # === Feature 11: Weekend Ratio ===
    weekend_count = sum(1 for ts in timestamps if ts.weekday() >= 5)
    weekend_ratio = weekend_count / max(total_engagements, 1)

    # === Feature 12: Night Ratio (00:00 - 06:00) ===
    night_count = sum(1 for ts in timestamps if 0 <= ts.hour < 6)
    night_ratio = night_count / max(total_engagements, 1)

    return {
        "engagement_frequency": round(engagement_frequency, 4),
        "growth_rate": round(growth_rate, 4),
        "interaction_diversity": round(interaction_diversity, 4),
        "temporal_variance": round(temporal_variance, 4),
        "follower_following_ratio": round(follower_following_ratio, 4),
        "account_age_days": account_age_days,
        "avg_engagement_interval": round(avg_engagement_interval, 4),
        "burst_score": round(burst_score, 4),
        "unique_targets_ratio": round(unique_targets_ratio, 4),
        "time_entropy": round(time_entropy, 4),
        "weekend_ratio": round(weekend_ratio, 4),
        "night_ratio": round(night_ratio, 4),
    }


def _calculate_burst_score(timestamps: List[datetime]) -> float:
    """Calculate burst score: max actions in any 1-minute window / avg per minute."""
    if len(timestamps) < 2:
        return 0.0

    # Count actions per minute
    minute_counts = Counter()
    for ts in timestamps:
        minute_key = ts.strftime("%Y-%m-%d %H:%M")
        minute_counts[minute_key] += 1

    if not minute_counts:
        return 0.0

    max_per_minute = max(minute_counts.values())
    avg_per_minute = sum(minute_counts.values()) / len(minute_counts)

    return max_per_minute / max(avg_per_minute, 0.01)


def _calculate_time_entropy(timestamps: List[datetime]) -> float:
    """Calculate Shannon entropy of hourly activity distribution."""
    if not timestamps:
        return 0.0

    hour_counts = Counter(ts.hour for ts in timestamps)
    total = sum(hour_counts.values())

    entropy = 0.0
    for count in hour_counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    # Normalize by max entropy (log2(24) ≈ 4.585)
    max_entropy = math.log2(24)
    return entropy / max_entropy if max_entropy > 0 else 0.0


def _empty_features() -> Dict[str, float]:
    """Return empty features for users with no engagements."""
    return {
        "engagement_frequency": 0.0,
        "growth_rate": 0.0,
        "interaction_diversity": 0.0,
        "temporal_variance": 0.0,
        "follower_following_ratio": 0.0,
        "account_age_days": 0,
        "avg_engagement_interval": 0.0,
        "burst_score": 0.0,
        "unique_targets_ratio": 0.0,
        "time_entropy": 0.0,
        "weekend_ratio": 0.0,
        "night_ratio": 0.0,
    }


FEATURE_NAMES = [
    "engagement_frequency",
    "growth_rate",
    "interaction_diversity",
    "temporal_variance",
    "follower_following_ratio",
    "account_age_days",
    "avg_engagement_interval",
    "burst_score",
    "unique_targets_ratio",
    "time_entropy",
    "weekend_ratio",
    "night_ratio",
]
