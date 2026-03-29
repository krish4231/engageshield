"""Alerts router — list, update, and manage alerts."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime
import uuid

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.alert import Alert
from app.alerts.schemas import AlertResponse, AlertUpdate, AlertListResponse
from app.alerts.service import get_alerts

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List alerts with pagination and optional filtering."""
    alerts, total = await get_alerts(db, page, page_size, severity, category)
    return AlertListResponse(
        alerts=[AlertResponse.model_validate(a) for a in alerts],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: uuid.UUID,
    update: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update alert status (read/resolved)."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if update.is_read is not None:
        alert.is_read = update.is_read
    if update.is_resolved is not None:
        alert.is_resolved = update.is_resolved
        if update.is_resolved:
            alert.resolved_at = datetime.utcnow()

    await db.flush()
    await db.refresh(alert)
    return alert
