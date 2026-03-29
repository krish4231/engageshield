"""WebSocket connection manager for real-time alert broadcasting."""

import json
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
import structlog

logger = structlog.get_logger()


class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("ws_connected", total_connections=len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("ws_disconnected", total_connections=len(self.active_connections))

    async def send_personal(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Clean up broken connections
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_alert(self, alert_data: dict):
        """Broadcast a new alert to all connected clients."""
        await self.broadcast({
            "type": "new_alert",
            "data": alert_data,
        })

    async def broadcast_analysis_complete(self, analysis_data: dict):
        """Broadcast analysis completion."""
        await self.broadcast({
            "type": "analysis_complete",
            "data": analysis_data,
        })


# Singleton instance
ws_manager = ConnectionManager()
