"""Service layer for engagement data ingestion."""

import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.engagement import Engagement
from app.ingestion.schemas import EngagementInput


async def ingest_batch(
    engagements: List[EngagementInput], db: AsyncSession
) -> tuple[uuid.UUID, int]:
    """Ingest a batch of engagement records into the database."""
    batch_id = uuid.uuid4()
    count = 0

    for eng_input in engagements:
        engagement = Engagement(
            source_user_id=eng_input.source_user_id,
            source_username=eng_input.source_username,
            target_user_id=eng_input.target_user_id,
            target_username=eng_input.target_username,
            engagement_type=eng_input.engagement_type,
            content=eng_input.content,
            platform=eng_input.platform,
            engagement_value=eng_input.engagement_value,
            source_follower_count=eng_input.source_follower_count,
            source_following_count=eng_input.source_following_count,
            source_account_age_days=eng_input.source_account_age_days,
            source_total_posts=eng_input.source_total_posts,
            engagement_timestamp=eng_input.engagement_timestamp,
            batch_id=batch_id,
        )
        db.add(engagement)
        count += 1

    await db.flush()
    return batch_id, count
