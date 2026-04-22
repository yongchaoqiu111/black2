"""
WebSocket Manager - Centralized WebSocket connection management
"""
import asyncio
import json
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_rooms: Dict[str, List[str]] = {}  # room_id -> [user_ids]
        self.room_connections: Dict[str, List[WebSocket]] = {}  # room_id -> [connections]

    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a user to WebSocket"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected to WebSocket")

    def disconnect(self, user_id: str):
        """Disconnect a user from WebSocket"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected from WebSocket")

    async def broadcast_to_room(self, room_id: str, message: dict):
        """Broadcast message to all connections in a room"""
        if room_id in self.room_connections:
            for connection in self.room_connections[room_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to room {room_id}: {e}")

    async def send_personal_message(self, user_id: str, message: dict):
        """Send personal message to a specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {user_id}: {e}")

    def join_room(self, user_id: str, room_id: str, websocket: WebSocket):
        """Add user to a room"""
        if room_id not in self.user_rooms:
            self.user_rooms[room_id] = []
        if user_id not in self.user_rooms[room_id]:
            self.user_rooms[room_id].append(user_id)

        if room_id not in self.room_connections:
            self.room_connections[room_id] = []
        if websocket not in self.room_connections[room_id]:
            self.room_connections[room_id].append(websocket)

    def leave_room(self, user_id: str, room_id: str, websocket: WebSocket):
        """Remove user from a room"""
        if room_id in self.user_rooms and user_id in self.user_rooms[room_id]:
            self.user_rooms[room_id].remove(user_id)
        if room_id in self.room_connections and websocket in self.room_connections[room_id]:
            self.room_connections[room_id].remove(websocket)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()