from __future__ import annotations

import json
import logging
from collections import defaultdict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, match_id: str, websocket: WebSocket):
        await websocket.accept()
        self._connections[match_id].append(websocket)
        logger.info(f"WebSocket connected for match {match_id}")

    def disconnect(self, match_id: str, websocket: WebSocket):
        if match_id in self._connections:
            self._connections[match_id] = [
                ws for ws in self._connections[match_id] if ws != websocket
            ]
            if not self._connections[match_id]:
                del self._connections[match_id]
        logger.info(f"WebSocket disconnected for match {match_id}")

    async def broadcast(self, match_id: str, data: dict):
        if match_id not in self._connections:
            return

        dead = []
        for ws in self._connections[match_id]:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)

        for ws in dead:
            self._connections[match_id].remove(ws)


manager = ConnectionManager()


@router.websocket("/match/{match_id}")
async def websocket_match(websocket: WebSocket, match_id: str):
    await manager.connect(match_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(match_id, websocket)
    except Exception:
        manager.disconnect(match_id, websocket)
