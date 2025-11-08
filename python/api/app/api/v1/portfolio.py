"""
Portfolio endpoints for the FastAPI application.
Serves portfolio data with bot integration and caching.
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import time

from app.services.kalshi_service import kalshi_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/balance")
async def get_portfolio_balance() -> Dict[str, Any]:
    """
    Get current portfolio balance.
    Returns live data from bot if online, otherwise cached Kalshi API data.
    """
    try:
        balance_data = await kalshi_service.get_portfolio_balance()
        return {
            "success": True,
            "data": balance_data
        }
    except Exception as e:
        logger.error(f"Failed to get portfolio balance: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve portfolio balance"
        )


@router.get("/positions")
async def get_portfolio_positions() -> Dict[str, Any]:
    """
    Get current portfolio positions.
    Returns live data from bot if online, otherwise cached Kalshi API data.
    """
    try:
        positions_data = await kalshi_service.get_portfolio_positions()
        return {
            "success": True,
            "data": positions_data
        }
    except Exception as e:
        logger.error(f"Failed to get portfolio positions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve portfolio positions"
        )


@router.get("/fills")
async def get_portfolio_fills(
    limit: int = Query(default=100, ge=1, le=1000, description="Number of fills to retrieve")
) -> Dict[str, Any]:
    """
    Get recent portfolio fills (trade history).
    Data is cached for performance.
    """
    try:
        fills_data = await kalshi_service.get_portfolio_fills(limit=limit)
        return {
            "success": True,
            "data": fills_data
        }
    except Exception as e:
        logger.error(f"Failed to get portfolio fills: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve portfolio fills"
        )


@router.get("/summary")
async def get_portfolio_summary() -> Dict[str, Any]:
    """
    Get a comprehensive portfolio summary.
    Combines balance, positions, and recent activity.
    """
    try:
        # Get all portfolio data concurrently
        balance_task = kalshi_service.get_portfolio_balance()
        positions_task = kalshi_service.get_portfolio_positions()
        live_trades_task = kalshi_service.get_live_trades()

        balance_data, positions_data, live_trades_data = await asyncio.gather(
            balance_task, positions_task, live_trades_task
        )

        return {
            "success": True,
            "data": {
                "balance": balance_data,
                "positions": positions_data,
                "live_trades": live_trades_data,
                "summary_timestamp": time.time()  # Could add timestamp if needed
            }
        }
    except Exception as e:
        logger.error(f"Failed to get portfolio summary: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve portfolio summary"
        )