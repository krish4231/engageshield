"""Ingestion router — submit engagement data batches."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.ingestion.schemas import EngagementBatch, IngestionResponse
from app.ingestion.service import ingest_batch

router = APIRouter(prefix="/api/ingest", tags=["Data Ingestion"])


@router.post("", response_model=IngestionResponse)
async def ingest_engagements(
    batch: EngagementBatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ingest a batch of engagement data for analysis."""
    batch_id, count = await ingest_batch(batch.engagements, db)
    return IngestionResponse(batch_id=batch_id, total_ingested=count)
