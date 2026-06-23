from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
# In a real setup, we would parse a token from query params or headers
# since standard WebSockets don't easily send authorization headers initially from browsers.
# For now, we simulate user_id extraction.

from app.services.websocket_manager import websocket_manager
from app.engine.trade_logger import TradeLogger

logger = TradeLogger()

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            # We just wait for incoming messages (e.g., ping) or to keep the connection open
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        websocket_manager.disconnect(websocket, user_id)
