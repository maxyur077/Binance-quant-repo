from __future__ import annotations

import asyncio
import json
from typing import Dict, List, Set
from fastapi import WebSocket

from app.engine.trade_logger import TradeLogger

logger = TradeLogger()


class ConnectionManager:
    def __init__(self):
        # Map user_id -> set of WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to a specific user's active websockets."""
        if user_id in self.active_connections:
            websockets = self.active_connections[user_id]
            for ws in websockets:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending ws message to {user_id}: {e}")

    async def broadcast(self, message: dict):
        """Send a message to all connected clients."""
        for user_connections in self.active_connections.values():
            for ws in user_connections:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    pass


websocket_manager = ConnectionManager()
