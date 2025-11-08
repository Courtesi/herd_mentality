"""
Server-Sent Events (SSE) Manager for real-time updates to frontend clients.
Handles multiple SSE connections and broadcasts events efficiently.
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from fastapi import Request
from fastapi.responses import StreamingResponse
import uuid

logger = logging.getLogger(__name__)


@dataclass
class SSEClient:
    """Represents a single SSE connection"""
    id: str
    request: Request
    connected_at: float = field(default_factory=time.time)
    last_ping: float = field(default_factory=time.time)
    message_count: int = 0
    subscriptions: Set[str] = field(default_factory=set)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


class SSEManager:
    """
    Manages Server-Sent Events connections and broadcasts.

    Features:
    - Multiple client connections
    - Event filtering by subscription
    - Automatic client cleanup on disconnect
    - Message batching and throttling
    - Connection health monitoring
    """

    def __init__(self):
        self.clients: Dict[str, SSEClient] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()

        # Performance settings
        self.max_clients = 100
        self.heartbeat_interval = 30  # seconds
        self.client_timeout = 60  # seconds
        self.max_queue_size = 1000

        # Background tasks
        self.cleanup_task = None
        self.heartbeat_task = None
        self.is_running = False

        # Statistics
        self.total_connections = 0
        self.total_messages_sent = 0
        self.total_events_processed = 0

        #Bot Status
        self.bot_status = {
            "is_online": False,
            "timestamp": time.time(),
            "bot_id": "main"
        }


    async def start(self):
        """Start the SSE manager background tasks"""
        if self.is_running:
            return

        self.is_running = True

        # Start background tasks
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        logger.info("SSE Manager started")

    async def stop(self):
        """Stop the SSE manager and close all connections"""
        self.is_running = False

        # Cancel background tasks
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.heartbeat_task:
            self.heartbeat_task.cancel()

        # Close all client connections
        for client_id in list(self.clients.keys()):
            await self.disconnect_client(client_id)

        logger.info("SSE Manager stopped")

    async def connect_client(self, request: Request, subscriptions: Optional[List[str]] = None) -> str:
        """
        Connect a new SSE client.

        Args:
            request: FastAPI request object
            subscriptions: List of event types to subscribe to

        Returns:
            client_id: Unique identifier for the client
        """
        # Check client limit
        if len(self.clients) >= self.max_clients:
            # logger.warning(f"Client limit reached: {len(self.clients)}")
            raise Exception("Maximum client connections reached")

        # Create new client
        client = SSEClient(
            id=str(uuid.uuid4()),
            request=request,
            subscriptions=set(subscriptions) if subscriptions else set()
        )

        self.clients[client.id] = client
        self.total_connections += 1

        logger.info(f"Client connected: {client.id} (total: {len(self.clients)})")

        return client.id

    async def disconnect_client(self, client_id: str):
        """Disconnect and remove a client"""
        if client_id in self.clients:
            client = self.clients[client_id]
            del self.clients[client_id]

            connection_duration = time.time() - client.connected_at
            logger.info(f"Client disconnected: {client_id} "
                       f"(duration: {connection_duration:.1f}s, "
                       f"messages: {client.message_count})")

    async def subscribe_client(self, client_id: str, event_types: List[str]):
        """Subscribe client to specific event types"""
        if client_id in self.clients:
            self.clients[client_id].subscriptions.update(event_types)
            logger.debug(f"Client {client_id} subscribed to: {event_types}")

    async def unsubscribe_client(self, client_id: str, event_types: List[str]):
        """Unsubscribe client from specific event types"""
        if client_id in self.clients:
            self.clients[client_id].subscriptions.difference_update(event_types)
            logger.debug(f"Client {client_id} unsubscribed from: {event_types}")

    async def send_event(self, event_type: str, data: Any, client_ids: Optional[List[str]] = None):
        """
        Send an event to all clients or specific clients.

        Args:
            event_type: Type of event (e.g., 'position_update', 'new_trades')
            data: Event data (will be JSON serialized)
            client_ids: Optional list of specific client IDs to send to
        """
        if not self.clients:
            return

        # event_data = {
        #     "type": event_type,
        #     "data": data,
        #     "timestamp": time.time()
        # }

        event_data = data
        # logger.info(f"event_data: {event_data}")

        # Determine target clients
        target_clients = []
        if client_ids:
            # Send to specific clients
            target_clients = [
                client for client_id, client in self.clients.items()
                if client_id in client_ids
            ]
        else:
            # Send to all subscribed clients
            target_clients = [
                client for client in self.clients.values()
                if not client.subscriptions or event_type in client.subscriptions
            ]

        if not target_clients:
            return

        # Format SSE message
        message = self._format_sse_message(event_type, event_data)

        # Send to all target clients
        failed_clients = []
        for client in target_clients:
            try:
                await self._send_to_client(client, message)
                client.message_count += 1
                self.total_messages_sent += 1
            except Exception as e:
                logger.error(f"Failed to send to client {client.id}: {e}")
                failed_clients.append(client.id)

        # Clean up failed clients
        for client_id in failed_clients:
            await self.disconnect_client(client_id)

        self.total_events_processed += 1

        if failed_clients:
            logger.warning(f"Removed {len(failed_clients)} failed clients")

        logger.debug(f"Sent {event_type} to {len(target_clients) - len(failed_clients)} clients")

    async def send_to_client(self, client_id: str, event_type: str, data: Any):
        """Send event to a specific client"""
        if client_id not in self.clients:
            logger.warning(f"Client {client_id} not found")
            return

        client = self.clients[client_id]
        event_data = {
            "type": event_type,
            "data": data,
            "timestamp": time.time()
        }

        message = self._format_sse_message(event_type, event_data)

        try:
            await self._send_to_client(client, message)
            client.message_count += 1
            self.total_messages_sent += 1
        except Exception as e:
            logger.error(f"Failed to send to client {client_id}: {e}")
            await self.disconnect_client(client_id)

    def _format_sse_message(self, event_type: str, data: Dict[str, Any]) -> str:
        """Format data as SSE message"""
        json_data = json.dumps(data, default=str)  # Handle datetime objects
        return f"event: {event_type}\ndata: {json_data}\n\n"

    async def _send_to_client(self, client: SSEClient, message: str):
        """Send message to a single client (override in subclass)"""
        # This is handled by the streaming response generator
        # We'll store messages in a queue for each client
        if not hasattr(client, 'message_queue'):
            client.message_queue = asyncio.Queue(maxsize=100)

        try:
            client.message_queue.put_nowait(message)
        except asyncio.QueueFull:
            logger.warning(f"Message queue full for client {client.id}")
            raise Exception("Client message queue full")

    async def _cleanup_loop(self):
        """Background task to clean up stale clients"""
        while self.is_running:
            try:
                current_time = time.time()
                stale_clients = []

                for client_id, client in self.clients.items():
                    # Check if client has been inactive
                    if current_time - client.last_ping > self.client_timeout:
                        stale_clients.append(client_id)

                # Remove stale clients
                for client_id in stale_clients:
                    logger.info(f"Removing stale client: {client_id}")
                    await self.disconnect_client(client_id)

                # Clean up event queue if it gets too large
                if self.event_queue.qsize() > self.max_queue_size:
                    logger.warning("Event queue size exceeded, clearing old events")
                    # Clear half the queue
                    for _ in range(self.max_queue_size // 2):
                        try:
                            self.event_queue.get_nowait()
                        except asyncio.QueueEmpty:
                            break

                await asyncio.sleep(30)  # Clean up every 30 seconds

            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(30)

    async def _heartbeat_loop(self):
        """Background task to send heartbeat to all clients"""
        while self.is_running:
            try:
                if self.clients:
                    await self.send_event("heartbeat", {
                        "timestamp": time.time(),
                        "connected_clients": len(self.clients)
                    })

                await asyncio.sleep(self.heartbeat_interval)

            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                await asyncio.sleep(self.heartbeat_interval)

    async def get_client_stream(self, client_id: str):
        """
        Get SSE stream generator for a client.
        This is used by FastAPI's StreamingResponse.
        """
        if client_id not in self.clients:
            raise Exception(f"Client {client_id} not found")

        client = self.clients[client_id]

        # Create message queue if it doesn't exist
        if not hasattr(client, 'message_queue'):
            client.message_queue = asyncio.Queue(maxsize=100)

        async def event_stream():
            try:
                # Send connection confirmation
                initial_message = self._format_sse_message("connected", {
                    "client_id": client_id,
                    "timestamp": time.time(),
                    "message": "SSE connection established"
                })
                yield initial_message

                # Stream messages from queue
                while client_id in self.clients:
                    try:
                        # Wait for message with timeout
                        message = await asyncio.wait_for(
                            client.message_queue.get(),
                            timeout=self.heartbeat_interval
                        )
                        yield message
                        client.last_ping = time.time()

                    except asyncio.TimeoutError:
                        # Send keep-alive ping
                        ping_message = self._format_sse_message("ping", {
                            "timestamp": time.time()
                        })
                        yield ping_message

            except Exception as e:
                logger.error(f"Stream error for client {client_id}: {e}")
            finally:
                await self.disconnect_client(client_id)

        return event_stream()

    def get_stats(self) -> Dict[str, Any]:
        """Get SSE manager statistics"""
        return {
            "is_running": self.is_running,
            "connected_clients": len(self.clients),
            "total_connections": self.total_connections,
            "total_messages_sent": self.total_messages_sent,
            "total_events_processed": self.total_events_processed,
            "event_queue_size": self.event_queue.qsize(),
            "max_clients": self.max_clients,
            "heartbeat_interval": self.heartbeat_interval,
            "clients": [
                {
                    "id": client.id,
                    "connected_at": client.connected_at,
                    "message_count": client.message_count,
                    "subscriptions": list(client.subscriptions),
                    "last_ping": client.last_ping
                }
                for client in self.clients.values()
            ]
        }

    def update_bot_status(self, is_online: bool, bot_id: str):
        self.bot_status["is_online"] = is_online
        self.bot_status["bot_id"] = bot_id
        self.bot_status["timestamp"] = time.time()

    def get_bot_status(self) -> Any:
        return self.bot_status.copy()


# Global SSE manager instance
sse_manager = SSEManager()