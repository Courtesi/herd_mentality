"""
Bot webhook endpoints for real-time status notifications.
Allows trading bot to notify FastAPI when it goes online/offline.
"""

import time
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from app.services.sse_manager import sse_manager
# from app.services.bot_polling_service import bot_polling_service

logger = logging.getLogger(__name__)

router = APIRouter()


class BotStatusWebhook(BaseModel):
    is_online: bool
    bot_id: Optional[str] = "main"  # Support for multiple bots in future
    timestamp: Optional[float] = None


class TradeWebhook(BaseModel):
    """Trade webhook payload from bot"""
    timestamp: float
    ticker: str
    side: str  # "BUY" or "SELL"
    quantity: int
    price: float
    trade_id: str
    source: str = "bot_live"
    bot_id: Optional[str] = "main"


@router.post("/webhook/online")
async def bot_online_webhook(payload: BotStatusWebhook, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for bot to notify when it comes online.

    This replaces the need for constant health check polling.
    When called, FastAPI will:
    1. Start polling for trade data
    2. Send SSE event to connected clients
    3. Update internal bot status
    """
    try:
        logger.info(f"Bot online webhook received: {payload.model_dump()}")

        # Update bot polling service status
        # bot_polling_service.handle_webhook_online(payload.bot_id or "main")

        # Send SSE event to all connected clients
        webhook_data = {
            "is_online": payload.is_online,
            "bot_id": payload.bot_id or "main",
            "timestamp": payload.timestamp or time.time(),
        }

        # Send in background to avoid blocking webhook response
        background_tasks.add_task(
            sse_manager.send_event,
            "bot_status",
            webhook_data
        )
        background_tasks.add_task(
            sse_manager.update_bot_status,
            True,
            payload.bot_id or "main"
        )

        return {
            "success": True,
            "message": "Bot online status received",
            "bot_id": payload.bot_id or "main",
            "timestamp": webhook_data["timestamp"],
        }

    except Exception as e:
        logger.error(f"Error processing bot online webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")


@router.post("/webhook/offline")
async def bot_offline_webhook(payload: BotStatusWebhook, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for bot to notify when it goes offline.

    When called, FastAPI will:
    1. Stop polling for trade data
    2. Send SSE event to connected clients
    3. Update internal bot status
    """
    try:
        logger.info(f"Bot offline webhook received: {payload.model_dump()}")

        # Update bot polling service status
        # bot_polling_service.handle_webhook_offline(payload.bot_id or "main")

        # Send SSE event to all connected clients
        webhook_data = {
            "is_online": payload.is_online,
            "bot_id": payload.bot_id or "main",
            "timestamp": payload.timestamp or time.time(),
        }

        # Send in background to avoid blocking webhook response
        background_tasks.add_task(
            sse_manager.send_event,
            "bot_status",
            webhook_data
        )

        background_tasks.add_task(
            sse_manager.update_bot_status,
            False,
            payload.bot_id or "main"
        )

        return {
            "success": True,
            "message": "Bot offline status received",
            "bot_id": payload.bot_id or "main",
            "timestamp": webhook_data["timestamp"],
        }

    except Exception as e:
        logger.error(f"Error processing bot offline webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")


@router.get("/webhook/status")
async def get_webhook_status():
    """
    Get current webhook system status and bot states.
    Useful for debugging webhook delivery.
    """
    try:
        bot_status = sse_manager.get_bot_status()

        return {
            "webhook_system": "active",
            "is_online": bot_status.get("is_online", "unknown"),
            "last_webhook_received": bot_status.get("timestamp", None),
            "connected_sse_clients": len(sse_manager.clients),
            "timestamp": time.time()
        }

    except Exception as e:
        logger.error(f"Error getting webhook status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook status")


@router.post("/webhook/test")
async def test_webhook_system(background_tasks: BackgroundTasks):
    """
    Test endpoint to verify webhook system is working.
    Simulates a bot online notification.
    """
    try:
        test_payload = BotStatusWebhook(
            is_online=False,
            bot_id="test",
            timestamp=time.time()
        )

        # Process like a real webhook
        webhook_data = {
            "is_online": "online",
            "bot_id": "test",
            "timestamp": test_payload.timestamp,
        }

        background_tasks.add_task(
            sse_manager.send_event,
            "bot_status",
            webhook_data
        )

        return {
            "success": True,
            "message": "Test webhook processed",
            "test_data": webhook_data
        }

    except Exception as e:
        logger.error(f"Error testing webhook system: {e}")
        raise HTTPException(status_code=500, detail="Failed to test webhook system")


@router.post("/webhook/trade")
async def bot_trade_webhook(payload: TradeWebhook, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for bot to notify when a trade is executed.

    This provides instant trade updates to the frontend via SSE,
    eliminating the need for frequent polling of the /trades endpoint.
    """
    try:
        logger.info(f"Trade webhook received: {payload.side} {payload.quantity} {payload.ticker} @ ${payload.price}")

        # Format trade data for SSE broadcast
        trade_data = {
            "trades": [payload.model_dump()],  # Format as list to match polling response
            "count": 1,
            "timestamp": payload.timestamp,
            "source": payload.source,
            "bot_id": payload.bot_id or "main"
        }

        # Send SSE event to all connected clients
        # Use same event type as polling system for consistency
        background_tasks.add_task(
            sse_manager.send_event,
            "new_trades",
            trade_data
        )

        return {
            "success": True,
            "message": "Trade webhook processed",
            "trade_id": payload.trade_id,
            "ticker": payload.ticker,
            "timestamp": payload.timestamp
        }

    except Exception as e:
        logger.error(f"Error processing trade webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process trade webhook")