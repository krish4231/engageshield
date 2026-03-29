"""Alert service for creating and managing alerts."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.models.alert import Alert
from app.websockets.manager import ws_manager


async def create_alert(
    db: AsyncSession,
    title: str,
    description: str,
    severity: str,
    category: str,
    analysis_id: Optional[uuid.UUID] = None,
    target_identifier: Optional[str] = None,
    threat_score: float = 0.0,
    evidence: Optional[dict] = None,
) -> Alert:
    """Create a new alert and broadcast it via WebSocket."""
    alert = Alert(
        analysis_id=analysis_id,
        title=title,
        description=description,
        severity=severity,
        category=category,
        target_identifier=target_identifier,
        threat_score=threat_score,
        evidence=evidence or {},
    )
    db.add(alert)
    await db.flush()
    await db.refresh(alert)

    # Broadcast to WebSocket clients
    await ws_manager.broadcast_alert({
        "id": str(alert.id),
        "title": alert.title,
        "description": alert.description,
        "severity": alert.severity,
        "category": alert.category,
        "threat_score": alert.threat_score,
        "created_at": alert.created_at.isoformat(),
    })

    return alert


async def get_alerts(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    severity: Optional[str] = None,
    category: Optional[str] = None,
) -> tuple[list[Alert], int]:
    """Get paginated, filtered alerts."""
    query = select(Alert)

    if severity:
        query = query.where(Alert.severity == severity)
    if category:
        query = query.where(Alert.category == category)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Fetch page
    query = query.order_by(desc(Alert.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    alerts = result.scalars().all()

    return alerts, total
