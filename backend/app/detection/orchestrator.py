"""
Detection Orchestrator — coordinates all 4 detection engines and produces unified results.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.engagement import Engagement
from app.models.analysis import Analysis, AnalysisResult
from app.models.alert import Alert
from app.detection.ml_engine.features import extract_features
from app.detection.ml_engine.model import predict
from app.detection.behavioral_engine.analyzer import analyze_behavior
from app.detection.behavioral_engine.patterns import check_patterns
from app.detection.graph_engine.builder import build_graph, graph_to_serializable
from app.detection.graph_engine.detector import detect_suspicious_clusters
from app.detection.graph_engine.metrics import calculate_node_metrics
from app.detection.insight_engine.generator import generate_insights
from app.alerts.service import create_alert
from app.websockets.manager import ws_manager

logger = structlog.get_logger()


async def run_full_analysis(
    db: AsyncSession,
    target_identifier: str,
    user_id: Optional[uuid.UUID] = None,
) -> Dict[str, Any]:
    """
    Run all 4 detection engines on engagement data for a target.

    This is the main orchestration function that:
    1. Fetches engagement data
    2. Runs ML, Behavioral, and Graph engines in parallel
    3. Passes results to the Insight engine
    4. Stores results and creates alerts
    5. Broadcasts updates via WebSocket
    """
    logger.info("analysis_started", target=target_identifier)

    # Create analysis record
    analysis = Analysis(
        target_identifier=target_identifier,
        analysis_type="full",
        status="processing",
        requested_by=user_id,
    )
    db.add(analysis)
    await db.flush()
    await db.refresh(analysis)

    try:
        # Fetch engagement data
        engagements = await _fetch_engagements(db, target_identifier)
        engagement_dicts = [_engagement_to_dict(e) for e in engagements]

        if not engagement_dicts:
            analysis.status = "completed"
            analysis.threat_score = 0.0
            analysis.threat_level = "low"
            analysis.total_engagements_analyzed = 0
            await db.flush()
            return {
                "analysis_id": str(analysis.id),
                "status": "completed",
                "threat_score": 0.0,
                "threat_level": "low",
                "message": "No engagement data found for this target",
            }

        # Extract unique source users
        source_users = set(e.get("source_user_id") for e in engagement_dicts)

        # === Run detection engines ===
        # 1. ML Engine — per-user feature extraction + prediction
        ml_results = {}
        for user in source_users:
            user_engagements = [e for e in engagement_dicts if e.get("source_user_id") == user]
            features = extract_features(user_engagements, user)
            prediction = predict(features)
            ml_results[user] = {"features": features, "prediction": prediction}

        # Aggregate ML score (average of individual user scores)
        ml_scores = [r["prediction"]["score"] for r in ml_results.values()]
        avg_ml_score = sum(ml_scores) / max(len(ml_scores), 1)
        ml_aggregate = {
            "score": round(avg_ml_score, 4),
            "confidence": round(sum(r["prediction"]["confidence"] for r in ml_results.values()) / max(len(ml_results), 1), 4),
            "label": "fake" if avg_ml_score >= 0.5 else "legitimate",
            "method": list(ml_results.values())[0]["prediction"]["method"] if ml_results else "none",
            "reasons": [],
            "suspicious_users": [uid for uid, r in ml_results.items() if r["prediction"]["score"] >= 0.5],
            "user_count": len(ml_results),
        }
        # Collect reasons from top suspicious users
        for uid, r in sorted(ml_results.items(), key=lambda x: x[1]["prediction"]["score"], reverse=True)[:5]:
            ml_aggregate["reasons"].extend(r["prediction"].get("reasons", []))

        # 2. Behavioral Engine — per-user analysis
        behavioral_results = {}
        for user in source_users:
            user_engagements = [e for e in engagement_dicts if e.get("source_user_id") == user]
            behavioral_results[user] = analyze_behavior(user_engagements, user)

        # Also check patterns
        pattern_matches = check_patterns(engagement_dicts, target_identifier)

        behav_scores = [r["score"] for r in behavioral_results.values()]
        avg_behav_score = sum(behav_scores) / max(len(behav_scores), 1)
        behavioral_aggregate = {
            "score": round(avg_behav_score, 4),
            "confidence": round(sum(r.get("confidence", 0.5) for r in behavioral_results.values()) / max(len(behavioral_results), 1), 4),
            "anomalies": [],
            "pattern_matches": pattern_matches,
            "is_bot_like": any(r.get("is_bot_like", False) for r in behavioral_results.values()),
        }
        for r in behavioral_results.values():
            behavioral_aggregate["anomalies"].extend(r.get("anomalies", []))

        # 3. Graph Engine
        graph = build_graph(engagement_dicts)
        graph_result = detect_suspicious_clusters(graph)
        node_metrics = calculate_node_metrics(graph)
        graph_data = graph_to_serializable(graph)

        # Apply node metrics as suspicion scores
        for node in graph_data["nodes"]:
            if node["id"] in node_metrics:
                node["metrics"] = node_metrics[node["id"]]
                node["suspicion_score"] = node_metrics[node["id"]].get("suspicion_score", 0)

        # 4. Insight Engine
        features_agg = {}
        if ml_results:
            first_user = list(ml_results.values())[0]
            features_agg = first_user.get("features", {})

        insight_result = generate_insights(
            ml_aggregate, behavioral_aggregate, graph_result, features_agg
        )

        # === Store results ===
        composite_score = insight_result["score"]
        severity = insight_result["severity"]

        analysis.threat_score = composite_score
        analysis.threat_level = severity
        analysis.status = "completed"
        analysis.completed_at = datetime.utcnow()
        analysis.total_engagements_analyzed = len(engagement_dicts)
        analysis.unique_accounts_analyzed = len(source_users)

        # Store per-engine results
        for engine_name, engine_data, summary in [
            ("ml", ml_aggregate, f"ML score: {avg_ml_score:.2%}"),
            ("behavioral", behavioral_aggregate, f"Behavioral score: {avg_behav_score:.2%}, {len(behavioral_aggregate['anomalies'])} anomalies"),
            ("graph", {**graph_result, "graph_data": graph_data}, f"Graph score: {graph_result['score']:.2%}"),
            ("insight", insight_result, insight_result.get("primary_insight", "")),
        ]:
            result = AnalysisResult(
                analysis_id=analysis.id,
                engine=engine_name,
                score=engine_data.get("score", 0),
                confidence=engine_data.get("confidence", 0),
                details=_make_serializable(engine_data),
                summary=summary,
            )
            db.add(result)

        # === Create alerts for significant threats ===
        if composite_score >= 0.4:
            await create_alert(
                db=db,
                title=f"Threat Detected: {target_identifier}",
                description=insight_result.get("primary_insight", "Suspicious engagement detected"),
                severity=severity,
                category=insight_result.get("category", "general"),
                analysis_id=analysis.id,
                target_identifier=target_identifier,
                threat_score=composite_score,
                evidence=insight_result.get("evidence", {}),
            )

        await db.flush()

        # Broadcast analysis complete
        await ws_manager.broadcast_analysis_complete({
            "analysis_id": str(analysis.id),
            "target": target_identifier,
            "threat_score": composite_score,
            "threat_level": severity,
        })

        logger.info(
            "analysis_completed",
            analysis_id=str(analysis.id),
            target=target_identifier,
            threat_score=composite_score,
            threat_level=severity,
        )

        return {
            "analysis_id": str(analysis.id),
            "target": target_identifier,
            "status": "completed",
            "threat_score": round(composite_score, 4),
            "threat_level": severity,
            "total_engagements": len(engagement_dicts),
            "unique_accounts": len(source_users),
            "ml_result": ml_aggregate,
            "behavioral_result": behavioral_aggregate,
            "graph_result": {**graph_result, "graph_data": graph_data},
            "insight": insight_result,
        }

    except Exception as e:
        logger.error("analysis_failed", target=target_identifier, error=str(e))
        analysis.status = "failed"
        await db.flush()
        raise


async def _fetch_engagements(db: AsyncSession, target_identifier: str) -> list:
    """Fetch engagements related to the target (as either source or target)."""
    query = select(Engagement).where(
        (Engagement.target_user_id == target_identifier)
        | (Engagement.source_user_id == target_identifier)
    ).order_by(Engagement.engagement_timestamp)

    result = await db.execute(query)
    return result.scalars().all()


def _engagement_to_dict(eng: Engagement) -> dict:
    """Convert ORM object to dictionary for engine processing."""
    return {
        "source_user_id": eng.source_user_id,
        "source_username": eng.source_username,
        "target_user_id": eng.target_user_id,
        "target_username": eng.target_username,
        "engagement_type": eng.engagement_type,
        "content": eng.content,
        "platform": eng.platform,
        "engagement_value": eng.engagement_value,
        "source_follower_count": eng.source_follower_count,
        "source_following_count": eng.source_following_count,
        "source_account_age_days": eng.source_account_age_days,
        "source_total_posts": eng.source_total_posts,
        "engagement_timestamp": eng.engagement_timestamp,
    }


def _make_serializable(data):
    """Recursively convert non-serializable types."""
    if isinstance(data, dict):
        return {k: _make_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_make_serializable(item) for item in data]
    elif isinstance(data, set):
        return list(data)
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, (int, float, str, bool, type(None))):
        return data
    else:
        return str(data)
