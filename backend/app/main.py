"""
EngageShield — FastAPI Application Factory
Main application entry point with CORS, middleware, and router registration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.utils.logging import setup_logging
from app.websockets.manager import ws_manager

# Import routers
from app.auth.router import router as auth_router
from app.ingestion.router import router as ingestion_router
from app.detection.router import router as detection_router
from app.alerts.router import router as alerts_router
from app.insights.router import router as insights_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    setup_logging()
    await init_db()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Fake Engagement Detection System for Social Media Platforms",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(ingestion_router)
app.include_router(detection_router)
app.include_router(alerts_router)
app.include_router(insights_router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for real-time alert streaming."""
    # Optional: validate token from query params
    # token = websocket.query_params.get("token")
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, process any incoming messages
            data = await websocket.receive_text()
            # Client can send ping/pong or filter requests
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
