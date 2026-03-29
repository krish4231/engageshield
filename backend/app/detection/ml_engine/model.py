"""
ML model inference for fake engagement detection.
Uses XGBoost with fallback to a rule-based heuristic when no trained model is available.
"""

import os
import numpy as np
from typing import Dict, Any, Optional
import structlog

from app.detection.ml_engine.features import FEATURE_NAMES, extract_features
from app.config import settings

logger = structlog.get_logger()

# Try to load model at module level
_model = None


def _load_model():
    """Load the trained XGBoost model from disk."""
    global _model
    model_path = settings.ML_MODEL_PATH
    if os.path.exists(model_path):
        try:
            import joblib
            _model = joblib.load(model_path)
            logger.info("ml_model_loaded", path=model_path)
        except Exception as e:
            logger.warning("ml_model_load_failed", error=str(e))
            _model = None
    else:
        logger.info("ml_model_not_found", path=model_path, fallback="heuristic")


def predict(features: Dict[str, float]) -> Dict[str, Any]:
    """
    Run ML prediction on extracted features.

    Returns:
        Dictionary with score, confidence, prediction label, and feature importances.
    """
    global _model

    feature_vector = np.array([[features.get(f, 0.0) for f in FEATURE_NAMES]])

    if _model is not None:
        return _predict_with_model(feature_vector, features)
    else:
        return _predict_heuristic(features)


def _predict_with_model(feature_vector: np.ndarray, features: Dict[str, float]) -> Dict[str, Any]:
    """Predict using trained XGBoost model."""
    try:
        proba = _model.predict_proba(feature_vector)[0]
        fake_probability = float(proba[1]) if len(proba) > 1 else float(proba[0])

        # Get feature importances
        importances = {}
        if hasattr(_model, 'feature_importances_'):
            for name, imp in zip(FEATURE_NAMES, _model.feature_importances_):
                importances[name] = round(float(imp), 4)

        return {
            "score": round(fake_probability, 4),
            "confidence": round(max(proba), 4),
            "label": "fake" if fake_probability >= settings.DETECTION_THRESHOLD else "legitimate",
            "feature_importances": importances,
            "method": "xgboost",
        }
    except Exception as e:
        logger.error("ml_prediction_failed", error=str(e))
        return _predict_heuristic(features)


def _predict_heuristic(features: Dict[str, float]) -> Dict[str, Any]:
    """
    Heuristic-based prediction fallback.
    Uses weighted scoring of suspicious indicators.
    """
    score = 0.0
    reasons = []
    weights = {
        "high_frequency": 0.20,
        "low_diversity": 0.15,
        "low_temporal_variance": 0.15,
        "high_burst": 0.15,
        "abnormal_ratio": 0.10,
        "new_account": 0.10,
        "low_entropy": 0.10,
        "high_night": 0.05,
    }

    # High engagement frequency (>50 actions/hour is suspicious)
    if features.get("engagement_frequency", 0) > 50:
        score += weights["high_frequency"]
        reasons.append("Extremely high engagement frequency")
    elif features.get("engagement_frequency", 0) > 20:
        score += weights["high_frequency"] * 0.5
        reasons.append("High engagement frequency")

    # Low interaction diversity (<0.1 means engaging with few unique accounts)
    diversity = features.get("interaction_diversity", 1.0)
    if diversity < 0.05:
        score += weights["low_diversity"]
        reasons.append("Very low interaction diversity")
    elif diversity < 0.15:
        score += weights["low_diversity"] * 0.5
        reasons.append("Low interaction diversity")

    # Low temporal variance (highly regular timing = bot-like)
    temp_var = features.get("temporal_variance", 1000)
    if 0 < temp_var < 5:
        score += weights["low_temporal_variance"]
        reasons.append("Suspiciously regular engagement timing")
    elif 0 < temp_var < 30:
        score += weights["low_temporal_variance"] * 0.5
        reasons.append("Somewhat regular engagement timing")

    # High burst score (>10 = massive spikes)
    burst = features.get("burst_score", 1.0)
    if burst > 10:
        score += weights["high_burst"]
        reasons.append("Extreme burst activity detected")
    elif burst > 5:
        score += weights["high_burst"] * 0.5
        reasons.append("Notable burst activity")

    # Abnormal follower/following ratio
    ratio = features.get("follower_following_ratio", 1.0)
    if ratio < 0.01 or ratio > 100:
        score += weights["abnormal_ratio"]
        reasons.append("Abnormal follower/following ratio")

    # New account
    age = features.get("account_age_days", 365)
    if age < 7:
        score += weights["new_account"]
        reasons.append("Very new account")
    elif age < 30:
        score += weights["new_account"] * 0.5
        reasons.append("Relatively new account")

    # Low time entropy (activity concentrated in few hours)
    entropy = features.get("time_entropy", 0.5)
    if entropy < 0.15:
        score += weights["low_entropy"]
        reasons.append("Activity concentrated in very few hours")
    elif entropy < 0.3:
        score += weights["low_entropy"] * 0.5
        reasons.append("Limited activity time distribution")

    # High night activity
    night = features.get("night_ratio", 0.1)
    if night > 0.5:
        score += weights["high_night"]
        reasons.append("Majority of activity during nighttime hours")

    return {
        "score": round(min(score, 1.0), 4),
        "confidence": round(0.6 + score * 0.3, 4),  # Heuristic confidence range 0.6-0.9
        "label": "fake" if score >= settings.DETECTION_THRESHOLD else "legitimate",
        "reasons": reasons,
        "method": "heuristic",
    }


# Load model on import
_load_model()
