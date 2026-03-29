"""Schemas for engagement data ingestion."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class EngagementInput(BaseModel):
    source_user_id: str
    source_username: Optional[str] = None
    target_user_id: str
    target_username: Optional[str] = None
    engagement_type: str  # like, follow, comment, share, retweet
    content: Optional[str] = None
    platform: str = "generic"
    engagement_value: float = 1.0
    source_follower_count: Optional[int] = None
    source_following_count: Optional[int] = None
    source_account_age_days: Optional[int] = None
    source_total_posts: Optional[int] = None
    engagement_timestamp: datetime


class EngagementBatch(BaseModel):
    engagements: List[EngagementInput]


class IngestionResponse(BaseModel):
    batch_id: uuid.UUID
    total_ingested: int
    status: str = "success"
