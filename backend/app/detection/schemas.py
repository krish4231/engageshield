"""Schemas for detection endpoints."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class AnalyzeRequest(BaseModel):
    target_identifier: str
    analysis_type: str = "full"  # full, quick


class AnalyzeResponse(BaseModel):
    analysis_id: str
    target: str
    status: str
    threat_score: float
    threat_level: str
    total_engagements: int = 0
    unique_accounts: int = 0
    ml_result: Optional[Dict[str, Any]] = None
    behavioral_result: Optional[Dict[str, Any]] = None
    graph_result: Optional[Dict[str, Any]] = None
    insight: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class DetectionResultResponse(BaseModel):
    id: uuid.UUID
    analysis_id: uuid.UUID
    engine: str
    score: float
    confidence: float
    details: dict
    summary: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisListItem(BaseModel):
    id: uuid.UUID
    target_identifier: str
    threat_score: float
    threat_level: str
    status: str
    total_engagements_analyzed: int
    unique_accounts_analyzed: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_analyses: int
    total_alerts: int
    active_threats: int
    avg_threat_score: float
    critical_alerts: int
    high_alerts: int
    medium_alerts: int
    low_alerts: int
    recent_analyses: List[AnalysisListItem]


class TimelinePoint(BaseModel):
    date: str
    engagements: int
    threats: int
    threat_score: float
