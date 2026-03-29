"""Schemas for insight endpoints."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class InsightResponse(BaseModel):
    id: uuid.UUID
    analysis_id: uuid.UUID
    engine: str
    score: float
    confidence: float
    details: dict
    summary: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class InsightListResponse(BaseModel):
    insights: List[InsightResponse]
    total: int
