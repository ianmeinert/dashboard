"""
Server-Sent Events (SSE) Manager

Handles real-time event broadcasting for the family dashboard.
Manages client connections and event distribution.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from fastapi import Request
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)


class SSEManager:
    """Manages Server-Sent Events connections and broadcasting."""

    def __init__(self):
        self.connections: Dict[str, asyncio.Queue] = {}
        self.parent_connections: Dict[int, Set[str]] = {}  # parent_id -> connection_ids

    async def connect(self, request: Request, parent_id: Optional[int] = None) -> StreamingResponse:
        """Create a new SSE connection."""
        connection_id = str(uuid4())
        queue = asyncio.Queue()

        self.connections[connection_id] = queue

        # Track parent-specific connections
        if parent_id:
            if parent_id not in self.parent_connections:
                self.parent_connections[parent_id] = set()
            self.parent_connections[parent_id].add(connection_id)

        logger.info(f"SSE connection established: {connection_id} (parent_id: {parent_id})")

        async def event_generator():
            try:
                # Send initial connection event
                yield f"event: connected\n"
                yield f"data: {json.dumps({
                    'connection_id': connection_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'message': 'Connected to chore events'
                })}\n\n"

                # Keep connection alive and send events
                while True:
                    try:
                        # Wait for events with timeout for keep-alive
                        event = await asyncio.wait_for(queue.get(), timeout=30.0)
                        yield f"event: {event['event']}\n"
                        yield f"data: {event['data']}\n\n"
                    except asyncio.TimeoutError:
                        # Send keep-alive ping
                        yield f"event: ping\n"
                        yield f"data: {json.dumps({
                            'timestamp': datetime.utcnow().isoformat()
                        })}\n\n"

            except asyncio.CancelledError:
                logger.info(f"SSE connection cancelled: {connection_id}")
            except Exception as e:
                logger.error(f"SSE connection error: {connection_id}, error: {e}")
            finally:
                await self.disconnect(connection_id, parent_id)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )

    async def disconnect(self, connection_id: str, parent_id: Optional[int] = None):
        """Remove an SSE connection."""
        if connection_id in self.connections:
            del self.connections[connection_id]

        if parent_id and parent_id in self.parent_connections:
            self.parent_connections[parent_id].discard(connection_id)
            if not self.parent_connections[parent_id]:
                del self.parent_connections[parent_id]

        logger.info(f"SSE connection disconnected: {connection_id}")

    async def broadcast_to_all(self, event_type: str, data: Dict[str, Any]):
        """Broadcast an event to all connected clients."""
        if not self.connections:
            return

        event = {
            "event": event_type,
            "data": json.dumps({
                **data,
                "timestamp": datetime.utcnow().isoformat()
            })
        }

        # Send to all connections
        disconnected = []
        for connection_id, queue in self.connections.items():
            try:
                await queue.put(event)
            except Exception as e:
                logger.error(f"Failed to send event to {connection_id}: {e}")
                disconnected.append(connection_id)

        # Clean up failed connections
        for connection_id in disconnected:
            await self.disconnect(connection_id)

        logger.debug(f"Broadcasted {event_type} to {len(self.connections)} connections")

    async def broadcast_to_parent(self, parent_id: int, event_type: str, data: Dict[str, Any]):
        """Broadcast an event to all connections for a specific parent."""
        if parent_id not in self.parent_connections:
            return

        event = {
            "event": event_type,
            "data": json.dumps({
                **data,
                "timestamp": datetime.utcnow().isoformat()
            })
        }

        connection_ids = list(self.parent_connections[parent_id])
        disconnected = []

        for connection_id in connection_ids:
            if connection_id in self.connections:
                try:
                    await self.connections[connection_id].put(event)
                except Exception as e:
                    logger.error(f"Failed to send event to {connection_id}: {e}")
                    disconnected.append(connection_id)

        # Clean up failed connections
        for connection_id in disconnected:
            await self.disconnect(connection_id, parent_id)

        logger.debug(f"Broadcasted {event_type} to parent {parent_id} ({len(connection_ids)} connections)")


# Global SSE manager instance
sse_manager = SSEManager()