"""
WebSocket Manager

Manages WebSocket connections and broadcasts live F1 data to connected clients.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Set
from uuid import UUID, uuid4

import aioredis
from loguru import logger
from websockets.server import WebSocketServerProtocol


class WebSocketManager:
    """Manages WebSocket connections and message broadcasting."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.connections: Dict[str, WebSocketServerProtocol] = {}
        self.session_subscribers: Dict[str, Set[str]] = {}  # session_id -> set of connection_ids
        self.redis_url = redis_url
        self.redis: aioredis.Redis = None
        self.pubsub = None

    async def initialize(self):
        """Initialize Redis connection and pub/sub."""
        try:
            self.redis = await aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
            self.pubsub = self.redis.pubsub()
            logger.info("Redis connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise

    async def close(self):
        """Close all connections and Redis."""
        # Close all WebSocket connections
        for connection_id, ws in list(self.connections.items()):
            try:
                await ws.close()
            except Exception as e:
                logger.error(f"Error closing connection {connection_id}: {e}")

        # Close Redis
        if self.pubsub:
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()

        logger.info("WebSocketManager closed")

    async def register(self, websocket: WebSocketServerProtocol, session_id: str) -> str:
        """
        Register a new WebSocket connection.

        Args:
            websocket: WebSocket connection
            session_id: F1 session ID to subscribe to

        Returns:
            connection_id: Unique connection identifier
        """
        connection_id = str(uuid4())
        self.connections[connection_id] = websocket

        # Add to session subscribers
        if session_id not in self.session_subscribers:
            self.session_subscribers[session_id] = set()
        self.session_subscribers[session_id].add(connection_id)

        logger.info(f"Connection {connection_id} registered for session {session_id}")
        return connection_id

    async def unregister(self, connection_id: str, session_id: str):
        """Unregister a WebSocket connection."""
        if connection_id in self.connections:
            del self.connections[connection_id]

        # Remove from session subscribers
        if session_id in self.session_subscribers:
            self.session_subscribers[session_id].discard(connection_id)
            if not self.session_subscribers[session_id]:
                del self.session_subscribers[session_id]

        logger.info(f"Connection {connection_id} unregistered from session {session_id}")

    async def broadcast_to_session(self, session_id: str, message: Dict):
        """
        Broadcast a message to all connections subscribed to a session.

        Args:
            session_id: F1 session ID
            message: Message data to broadcast
        """
        if session_id not in self.session_subscribers:
            return

        # Add timestamp and session_id to message
        message["timestamp"] = datetime.utcnow().isoformat()
        message["session_id"] = session_id

        message_json = json.dumps(message)
        dead_connections = []

        for connection_id in self.session_subscribers[session_id]:
            if connection_id not in self.connections:
                dead_connections.append(connection_id)
                continue

            websocket = self.connections[connection_id]
            try:
                await websocket.send(message_json)
            except Exception as e:
                logger.error(f"Error sending to connection {connection_id}: {e}")
                dead_connections.append(connection_id)

        # Clean up dead connections
        for connection_id in dead_connections:
            await self.unregister(connection_id, session_id)

    async def publish_to_redis(self, channel: str, message: Dict):
        """
        Publish a message to Redis pub/sub channel.

        Args:
            channel: Redis channel name
            message: Message data to publish
        """
        try:
            message_json = json.dumps(message)
            await self.redis.publish(channel, message_json)
        except Exception as e:
            logger.error(f"Error publishing to Redis channel {channel}: {e}")

    async def subscribe_to_redis(self, channel: str, callback):
        """
        Subscribe to a Redis pub/sub channel.

        Args:
            channel: Redis channel name
            callback: Async function to call with received messages
        """
        try:
            await self.pubsub.subscribe(channel)
            logger.info(f"Subscribed to Redis channel: {channel}")

            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await callback(data)
                    except Exception as e:
                        logger.error(f"Error processing Redis message: {e}")

        except Exception as e:
            logger.error(f"Error in Redis subscription to {channel}: {e}")

    async def get_connection_count(self, session_id: Optional[str] = None) -> int:
        """
        Get the number of active connections.

        Args:
            session_id: Optional session ID to count connections for

        Returns:
            Number of active connections
        """
        if session_id:
            return len(self.session_subscribers.get(session_id, set()))
        return len(self.connections)

    async def send_to_connection(self, connection_id: str, message: Dict):
        """
        Send a message to a specific connection.

        Args:
            connection_id: Connection ID
            message: Message data to send
        """
        if connection_id not in self.connections:
            logger.warning(f"Connection {connection_id} not found")
            return

        websocket = self.connections[connection_id]
        try:
            message["timestamp"] = datetime.utcnow().isoformat()
            message_json = json.dumps(message)
            await websocket.send(message_json)
        except Exception as e:
            logger.error(f"Error sending to connection {connection_id}: {e}")
