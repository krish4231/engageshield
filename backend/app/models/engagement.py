"""Engagement model for storing social media interaction data."""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.guid import GUID


class Engagement(Base):
    __tablename__ = "engagements"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    source_user_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    source_username: Mapped[str] = mapped_column(String(255), nullable=True)
    target_user_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    target_username: Mapped[str] = mapped_column(String(255), nullable=True)
    engagement_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, default="generic")
    engagement_value: Mapped[float] = mapped_column(Float, default=1.0)
    source_follower_count: Mapped[int] = mapped_column(Integer, nullable=True)
    source_following_count: Mapped[int] = mapped_column(Integer, nullable=True)
    source_account_age_days: Mapped[int] = mapped_column(Integer, nullable=True)
    source_total_posts: Mapped[int] = mapped_column(Integer, nullable=True)
    engagement_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    batch_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=True, index=True)
