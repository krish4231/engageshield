"""
Known bot pattern signatures for rule-based detection.
These complement the ML and behavioral engines with domain-specific rules.
"""

from typing import List, Dict, Any
from collections import Counter


def check_patterns(engagements: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
    """
    Check engagement data against known bot pattern signatures.

    Returns:
        List of matched patterns with descriptions.
    """
    matched = []

    matched.extend(_check_copy_paste_comments(engagements))
    matched.extend(_check_follow_unfollow_cycle(engagements))
    matched.extend(_check_mass_action_pattern(engagements))
    matched.extend(_check_single_target_focus(engagements))

    return matched


def _check_copy_paste_comments(engagements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect repeated identical comments (copy-paste bot behavior)."""
    comments = [
        eng.get("content", "").strip().lower()
        for eng in engagements
        if eng.get("engagement_type") == "comment" and eng.get("content")
    ]

    if len(comments) < 3:
        return []

    content_counts = Counter(comments)
    duplicates = {text: count for text, count in content_counts.items() if count >= 3}

    if duplicates:
        return [{
            "pattern": "copy_paste_comments",
            "severity": "high",
            "description": f"Detected {len(duplicates)} repeated comment(s) posted {sum(duplicates.values())} times",
            "evidence": {
                "repeated_comments": {k: v for k, v in list(duplicates.items())[:5]},
            },
        }]
    return []


def _check_follow_unfollow_cycle(engagements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect follow/unfollow cycling (follow-back farming)."""
    follows = [e for e in engagements if e.get("engagement_type") == "follow"]
    unfollows = [e for e in engagements if e.get("engagement_type") == "unfollow"]

    if len(follows) > 10 and len(unfollows) > 5:
        ratio = len(unfollows) / len(follows)
        if ratio > 0.4:
            return [{
                "pattern": "follow_unfollow_cycle",
                "severity": "medium",
                "description": f"Follow/unfollow cycle detected: {len(follows)} follows, {len(unfollows)} unfollows ({ratio:.0%} ratio)",
                "evidence": {
                    "follow_count": len(follows),
                    "unfollow_count": len(unfollows),
                    "ratio": round(ratio, 4),
                },
            }]
    return []


def _check_mass_action_pattern(engagements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect mass-action patterns (same action type in rapid succession)."""
    sorted_engs = sorted(engagements, key=lambda e: str(e.get("engagement_timestamp", "")))

    streak_count = 1
    max_streak = 1
    streak_type = None

    for i in range(1, len(sorted_engs)):
        if sorted_engs[i].get("engagement_type") == sorted_engs[i - 1].get("engagement_type"):
            streak_count += 1
            max_streak = max(max_streak, streak_count)
            streak_type = sorted_engs[i].get("engagement_type")
        else:
            streak_count = 1

    if max_streak >= 20:
        return [{
            "pattern": "mass_action",
            "severity": "high",
            "description": f"Mass {streak_type} pattern: {max_streak} consecutive {streak_type} actions",
            "evidence": {
                "streak_length": max_streak,
                "action_type": streak_type,
            },
        }]
    return []


def _check_single_target_focus(engagements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect obsessive single-target engagement (stalker/bot pattern)."""
    target_counts = Counter(eng.get("target_user_id") for eng in engagements)

    if len(target_counts) < 2:
        return []

    total = sum(target_counts.values())
    most_common_target, most_common_count = target_counts.most_common(1)[0]
    focus_ratio = most_common_count / total

    if focus_ratio > 0.7 and most_common_count > 10:
        return [{
            "pattern": "single_target_focus",
            "severity": "medium",
            "description": f"{focus_ratio:.0%} of engagement directed at a single target ({most_common_count} actions)",
            "evidence": {
                "target_id": most_common_target,
                "action_count": most_common_count,
                "focus_ratio": round(focus_ratio, 4),
            },
        }]
    return []
