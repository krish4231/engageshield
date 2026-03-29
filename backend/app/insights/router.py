"""Insights router — query AI-generated insights."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional
import uuid

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.analysis import AnalysisResult
from app.insights.schemas import InsightResponse, InsightListResponse

router = APIRouter(prefix="/api/insights", tags=["Insights"])


@router.get("", response_model=InsightListResponse)
async def list_insights(
    limit: int = Query(50, ge=1, le=200),
    engine: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List recent insights across all analyses."""
    query = select(AnalysisResult)
    if engine:
        query = query.where(AnalysisResult.engine == engine)
    query = query.order_by(desc(AnalysisResult.created_at)).limit(limit)

    result = await db.execute(query)
    insights = result.scalars().all()

    return InsightListResponse(
        insights=[InsightResponse.model_validate(i) for i in insights],
        total=len(insights),
    )


@router.get("/{analysis_id}", response_model=InsightListResponse)
async def get_analysis_insights(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all insights for a specific analysis."""
    query = select(AnalysisResult).where(
        AnalysisResult.analysis_id == analysis_id
    ).order_by(AnalysisResult.engine)

    result = await db.execute(query)
    insights = result.scalars().all()

    return InsightListResponse(
        insights=[InsightResponse.model_validate(i) for i in insights],
        total=len(insights),
    )
