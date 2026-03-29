"""
Behavioral analysis engine for detecting bot-like activity patterns.
Uses time-series anomaly detection, circadian pattern matching, and burst analysis.
"""

import numpy as np
from typing import List, Dict, Any
from datetime import datetime
from collections import Counter
import math


def analyze_behavior(engagements: List[Dict[str, Any]], user_id: str) -> Dict[str, Any]:
    """
    Analyze engagement behavior for anomalies.

    Returns:
        Dictionary with behavior scores, detected anomalies, and evidence.
    """
    if not engagements:
        return {"score": 0.0, "anomalies": [], "details": {}}

    timestamps = _extract_timestamps(engagements)
    if len(timestamps) < 3:
        return {"score": 0.0, "anomalies": [], "details": {"reason": "insufficient_data"}}

    # Run all behavioral checks
    burst_result = detect_burst_activity(timestamps)
    regularity_result = detect_time_regularity(timestamps)
    circadian_result = detect_circadian_pattern(timestamps)
    velocity_result = detect_velocity_anomaly(timestamps)

    # Combine scores (weighted)
    weights = {
        "burst": 0.30,
        "regularity": 0.25,
        "circadian": 0.25,
        "velocity": 0.20,
    }

    composite_score = (
        burst_result["score"] * weights["burst"]
        + regularity_result["score"] * weights["regularity"]
        + circadian_result["score"] * weights["circadian"]
        + velocity_result["score"] * weights["velocity"]
    )

    # Collect all anomalies
    anomalies = []
    for result in [burst_result, regularity_result, circadian_result, velocity_result]:
        anomalies.extend(result.get("anomalies", []))

    return {
        "score": round(min(composite_score, 1.0), 4),
        "confidence": round(0.65 + composite_score * 0.3, 4),
        "anomalies": anomalies,
        "details": {
            "burst_analysis": burst_result,
            "regularity_analysis": regularity_result,
            "circadian_analysis": circadian_result,
            "velocity_analysis": velocity_result,
        },
        "is_bot_like": composite_score >= 0.6,
    }


def detect_burst_activity(timestamps: List[datetime]) -> Dict[str, Any]:
    """
    Detect burst activity using Z-score of inter-event times.
    Bursts = sudden spikes of activity in short windows.
    """
    if len(timestamps) < 3:
        return {"score": 0.0, "anomalies": []}

    # Calculate inter-event intervals in seconds
    intervals = [(timestamps[i + 1] - timestamps[i]).total_seconds()
                 for i in range(len(timestamps) - 1)]

    intervals = np.array(intervals)
    mean_interval = np.mean(intervals)
    std_interval = np.std(intervals)

    anomalies = []
    burst_count = 0

    if std_interval > 0:
        z_scores = (intervals - mean_interval) / std_interval
        # Count intervals with very low z-scores (rapid-fire activity)
        burst_count = int(np.sum(z_scores < -2.0))

        if burst_count > 0:
            anomalies.append({
                "type": "burst_activity",
                "description": f"Detected {burst_count} burst intervals (Z-score < -2.0)",
                "evidence": {
                    "burst_intervals": burst_count,
                    "mean_interval_seconds": round(float(mean_interval), 2),
                    "min_interval_seconds": round(float(np.min(intervals)), 2),
                },
            })

    # Count rapid-fire sequences (< 2 seconds apart)
    rapid_fire = int(np.sum(intervals < 2.0))
    if rapid_fire > 3:
        anomalies.append({
            "type": "rapid_fire",
            "description": f"{rapid_fire} engagements less than 2 seconds apart",
            "evidence": {"rapid_fire_count": rapid_fire},
        })

    burst_ratio = (burst_count + rapid_fire) / max(len(intervals), 1)
    return {
        "score": round(min(burst_ratio * 2, 1.0), 4),
        "anomalies": anomalies,
    }


def detect_time_regularity(timestamps: List[datetime]) -> Dict[str, Any]:
    """
    Detect suspiciously regular timing (bot-like clock precision).
    Uses coefficient of variation of inter-event times.
    """
    if len(timestamps) < 5:
        return {"score": 0.0, "anomalies": []}

    intervals = [(timestamps[i + 1] - timestamps[i]).total_seconds()
                 for i in range(len(timestamps) - 1)]

    intervals = np.array(intervals)
    mean_interval = np.mean(intervals)
    std_interval = np.std(intervals)

    # Coefficient of variation (lower = more regular)
    cv = std_interval / max(mean_interval, 0.01)

    anomalies = []

    # Very low CV means suspiciously regular timing
    if cv < 0.1 and mean_interval < 600:  # Regular AND frequent
        anomalies.append({
            "type": "clock_precision",
            "description": "Engagement timing shows machine-like regularity",
            "evidence": {
                "coefficient_of_variation": round(float(cv), 4),
                "mean_interval": round(float(mean_interval), 2),
                "std_interval": round(float(std_interval), 2),
            },
        })
        score = 0.9
    elif cv < 0.2:
        anomalies.append({
            "type": "regular_timing",
            "description": "Engagement timing is more regular than typical human behavior",
            "evidence": {"coefficient_of_variation": round(float(cv), 4)},
        })
        score = 0.5
    else:
        score = max(0.0, 0.3 - cv * 0.1)

    return {"score": round(score, 4), "anomalies": anomalies}


def detect_circadian_pattern(timestamps: List[datetime]) -> Dict[str, Any]:
    """
    Detect non-human circadian patterns (24/7 activity, no sleep cycles).
    Humans typically have 6-8 hours of inactivity (sleep).
    """
    if len(timestamps) < 10:
        return {"score": 0.0, "anomalies": []}

    # Build hourly activity histogram
    hours = [ts.hour for ts in timestamps]
    hour_counts = Counter(hours)
    hourly_dist = [hour_counts.get(h, 0) for h in range(24)]
    total = sum(hourly_dist)

    if total == 0:
        return {"score": 0.0, "anomalies": []}

    # Normalize
    hourly_pct = [c / total for c in hourly_dist]

    # Check for activity in sleep hours (2-6 AM in any timezone)
    sleep_hours_activity = sum(hourly_pct[2:6])

    # Count hours with zero activity
    active_hours = sum(1 for c in hourly_dist if c > 0)

    anomalies = []
    score = 0.0

    # 24/7 activity pattern
    if active_hours >= 22:
        anomalies.append({
            "type": "no_sleep_pattern",
            "description": "Account shows activity across nearly all 24 hours, no sleep pattern",
            "evidence": {
                "active_hours": active_hours,
                "sleep_hours_activity_pct": round(sleep_hours_activity, 4),
            },
        })
        score = 0.8

    # High sleep-hour activity
    elif sleep_hours_activity > 0.3:
        anomalies.append({
            "type": "high_night_activity",
            "description": f"{round(sleep_hours_activity * 100, 1)}% of activity during typical sleep hours",
            "evidence": {"sleep_hours_pct": round(sleep_hours_activity, 4)},
        })
        score = 0.5

    # Very uniform distribution (bots tend to be evenly distributed)
    entropy = -sum(p * math.log2(p) for p in hourly_pct if p > 0)
    max_entropy = math.log2(24)
    normalized_entropy = entropy / max_entropy

    if normalized_entropy > 0.95:
        anomalies.append({
            "type": "uniform_activity",
            "description": "Activity is almost uniformly distributed across all hours",
            "evidence": {"normalized_entropy": round(normalized_entropy, 4)},
        })
        score = max(score, 0.7)

    return {"score": round(score, 4), "anomalies": anomalies}


def detect_velocity_anomaly(timestamps: List[datetime]) -> Dict[str, Any]:
    """
    Detect sudden velocity changes (sudden spike or drop in activity rate).
    Splits timeline into windows and compares rates.
    """
    if len(timestamps) < 10:
        return {"score": 0.0, "anomalies": []}

    # Split into windows
    total_span = (timestamps[-1] - timestamps[0]).total_seconds()
    if total_span < 60:
        return {"score": 0.0, "anomalies": []}

    window_size = max(total_span / 10, 60)  # 10 windows minimum
    window_counts = []
    window_start = timestamps[0]

    for ts in timestamps:
        elapsed = (ts - window_start).total_seconds()
        window_idx = int(elapsed / window_size)
        while len(window_counts) <= window_idx:
            window_counts.append(0)
        window_counts[window_idx] += 1

    if len(window_counts) < 3:
        return {"score": 0.0, "anomalies": []}

    window_counts = np.array(window_counts, dtype=float)
    mean_rate = np.mean(window_counts)
    std_rate = np.std(window_counts)

    anomalies = []
    score = 0.0

    if std_rate > 0:
        z_scores = (window_counts - mean_rate) / std_rate
        spikes = int(np.sum(z_scores > 3.0))

        if spikes > 0:
            anomalies.append({
                "type": "velocity_spike",
                "description": f"Detected {spikes} sudden activity spikes (>3σ from mean)",
                "evidence": {
                    "spike_count": spikes,
                    "mean_rate": round(float(mean_rate), 2),
                    "max_rate": round(float(np.max(window_counts)), 2),
                },
            })
            score = min(spikes * 0.3, 1.0)

    return {"score": round(score, 4), "anomalies": anomalies}


def _extract_timestamps(engagements: List[Dict[str, Any]]) -> List[datetime]:
    """Extract and sort timestamps from engagement records."""
    timestamps = []
    for eng in engagements:
        ts = eng.get("engagement_timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        if isinstance(ts, datetime):
            timestamps.append(ts)
    timestamps.sort()
    return timestamps
