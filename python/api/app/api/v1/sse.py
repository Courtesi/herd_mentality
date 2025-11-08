"""
Server-Sent Events (SSE) endpoint for real-time trading updates.
Provides SSE stream for trade notifications and bot status.
"""

import json
import logging
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.services.sse_manager import sse_manager
# from app.services.bot_polling_service import bot_polling_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.on_event("startup")
async def startup_sse():
    """Start SSE manager and bot polling when FastAPI starts"""
    await sse_manager.start()
    # await bot_polling_service.start_polling(sse_manager)
    logger.info("SSE services started")


@router.on_event("shutdown")
async def shutdown_sse():
    """Stop SSE manager and bot polling when FastAPI shuts down"""
    # await bot_polling_service.stop_polling()
    await sse_manager.stop()
    logger.info("SSE services stopped")

# @asynccontextmanager
# def on_event():
#     pass


@router.get("/sse/trading")
async def trading_sse(
    request: Request,
    events: Optional[str] = Query(None, description="Comma-separated list of events to subscribe to"),
    include_initial: bool = Query(True, description="Include initial state in stream")
):
    """
    Main SSE endpoint for real-time trading updates.

    Available events:
    - new_trades: New trade executions (BUY/SELL)
    - bot_status: Bot status changes
    - heartbeat: Keep-alive pings

    Example:
    GET /api/python/sse/trading?events=new_trades,bot_status
    """
    try:
        # Parse subscriptions
        subscriptions = []
        if events:
            subscriptions = [event.strip() for event in events.split(",") if event.strip()]
        else:
            # Default subscriptions (trades-focused)
            subscriptions = ["new_trades", "bot_status"]

        # Connect client to SSE manager
        client_id = await sse_manager.connect_client(request, subscriptions)

        # Create SSE response headers
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }

        # Get event stream generator
        event_stream = await sse_manager.get_client_stream(client_id)

        # Wrap with initial state if requested
        # if include_initial:
        event_stream = _add_initial_state(event_stream, client_id)

        return StreamingResponse(
            event_stream,
            media_type="text/event-stream",
            headers=headers
        )

    except Exception as e:
        logger.error(f"Error creating SSE stream: {e}")
        raise HTTPException(status_code=500, detail="Failed to create SSE stream")


async def _add_initial_state(event_stream, client_id: str):
    """Add initial state to the beginning of the event stream"""
    try:
        # Get current state from polling service
        bot_status = sse_manager.get_bot_status()
        logger.info(f"Sending initial state to client {client_id}: is_online={bot_status.get('is_online')}")

        # Send initial state event
        initial_event = f"event: initial_state\ndata: {json.dumps(bot_status, default=str)}\n\n"
        yield initial_event

        # Continue with regular event stream
        async for event in event_stream:
            yield event

    except Exception as e:
        logger.error(f"Error in initial state stream: {e}")
        # Continue with regular stream even if initial state fails
        async for event in event_stream:
            yield event