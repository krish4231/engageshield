"""Detection router — /analyze, /detect, /dashboard endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.analysis import Analysis, AnalysisResult
from app.models.alert import Alert
from app.models.engagement import Engagement
from app.detection.schemas import (
    AnalyzeRequest, AnalyzeResponse, DetectionResultResponse,
    DashboardStats, AnalysisListItem, TimelinePoint,
)
from app.detection.orchestrator import run_full_analysis

router = APIRouter(prefix="/api", tags=["Detection"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_target(
    request: AnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run full analysis on a target identifier (account/post/hashtag)."""
    result = await run_full_analysis(
        db=db,
        target_identifier=request.target_identifier,
        user_id=current_user.id,
    )
    return AnalyzeResponse(**result)


@router.get("/detect/{analysis_id}")
async def get_detection_results(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detailed detection results for a specific analysis."""
    # Fetch analysis
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Fetch results
    results_query = select(AnalysisResult).where(
        AnalysisResult.analysis_id == analysis_id
    )
    results = await db.execute(results_query)
    engine_results = results.scalars().all()

    return {
        "analysis": AnalysisListItem.model_validate(analysis),
        "results": [DetectionResultResponse.model_validate(r) for r in engine_results],
    }


@router.get("/network/{analysis_id}")
async def get_network_graph(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get network graph data for visualization."""
    result = await db.execute(
        select(AnalysisResult).where(
            AnalysisResult.analysis_id == analysis_id,
            AnalysisResult.engine == "graph",
        )
    )
    graph_result = result.scalar_one_or_none()

    if not graph_result:
        raise HTTPException(status_code=404, detail="Graph data not found")

    return graph_result.details.get("graph_data", {"nodes": [], "edges": []})


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard summary statistics."""
    # Total analyses
    total_q = await db.execute(select(func.count(Analysis.id)))
    total_analyses = total_q.scalar() or 0

    # Total alerts
    alerts_q = await db.execute(select(func.count(Alert.id)))
    total_alerts = alerts_q.scalar() or 0

    # Active (unresolved) threats
    active_q = await db.execute(
        select(func.count(Alert.id)).where(Alert.is_resolved == False)
    )
    active_threats = active_q.scalar() or 0

    # Average threat score
    avg_q = await db.execute(
        select(func.avg(Analysis.threat_score)).where(Analysis.status == "completed")
    )
    avg_threat_score = avg_q.scalar() or 0.0

    # Alert counts by severity
    for sev in ["critical", "high", "medium", "low"]:
        count_q = await db.execute(
            select(func.count(Alert.id)).where(Alert.severity == sev)
        )
        locals()[f"{sev}_count"] = count_q.scalar() or 0

    # Recent analyses
    recent_q = await db.execute(
        select(Analysis)
        .where(Analysis.status == "completed")
        .order_by(desc(Analysis.created_at))
        .limit(10)
    )
    recent = recent_q.scalars().all()

    return DashboardStats(
        total_analyses=total_analyses,
        total_alerts=total_alerts,
        active_threats=active_threats,
        avg_threat_score=round(float(avg_threat_score), 4),
        critical_alerts=locals().get("critical_count", 0),
        high_alerts=locals().get("high_count", 0),
        medium_alerts=locals().get("medium_count", 0),
        low_alerts=locals().get("low_count", 0),
        recent_analyses=[AnalysisListItem.model_validate(a) for a in recent],
    )


@router.get("/dashboard/timeline")
async def get_dashboard_timeline(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get engagement & threat timeline for the last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Fetch raw data and aggregate in Python (works with any DB)
    eng_query = await db.execute(
        select(Engagement.engagement_timestamp)
        .where(Engagement.engagement_timestamp >= cutoff)
    )
    eng_dates = {}
    for row in eng_query:
        day_str = str(row[0].date()) if row[0] else None
        if day_str:
            eng_dates[day_str] = eng_dates.get(day_str, 0) + 1

    analysis_query = await db.execute(
        select(Analysis.created_at, Analysis.threat_score)
        .where(Analysis.created_at >= cutoff, Analysis.status == "completed")
    )
    analysis_dates: dict = {}
    for row in analysis_query:
        day_str = str(row[0].date()) if row[0] else None
        if day_str:
            if day_str not in analysis_dates:
                analysis_dates[day_str] = {"count": 0, "total_score": 0.0}
            analysis_dates[day_str]["count"] += 1
            analysis_dates[day_str]["total_score"] += float(row[1] or 0)

    # Build timeline
    timeline = []
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days - 1 - i)).date()
        date_str = str(date)
        a_data = analysis_dates.get(date_str, {"count": 0, "total_score": 0})
        avg_score = a_data["total_score"] / a_data["count"] if a_data["count"] > 0 else 0
        timeline.append({
            "date": date_str,
            "engagements": eng_dates.get(date_str, 0),
            "threats": a_data["count"],
            "threat_score": round(avg_score, 4),
        })

    return {"timeline": timeline}
