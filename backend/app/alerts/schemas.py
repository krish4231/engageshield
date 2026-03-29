"""Schemas for alert endpoints."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class AlertResponse(BaseModel):
    id: uuid.UUID
    analysis_id: Optional[uuid.UUID] = None
    title: str
    description: str
    severity: str
    category: str
    target_identifier: Optional[str] = None
    threat_score: float
    evidence: dict
    is_read: bool
    is_resolved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_resolved: Optional[bool] = None


class AlertListResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int
    page: int
    page_size: int
