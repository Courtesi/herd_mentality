"""
Poll endpoints for the FastAPI application.
Serves poll history with market candlestick data.
"""

import asyncio
import logging
import httpx
from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from app.core.config import settings
from app.core.redis_client import cache_response
from exchanges.kalshi.rest.markets import Market

logger = logging.getLogger(__name__)

router = APIRouter()


async def fetch_polls_from_springboot() -> List[Dict[str, Any]]:
    """Fetch all closed polls from Spring Boot API"""
    url = f"{settings.SPRINGBOOT_URL}/api/polls/closed"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            polls = response.json()

            logger.info(f"Fetched {len(polls)} closed polls from Spring Boot")
            return polls

    except Exception as e:
        logger.error(f"Failed to fetch polls from Spring Boot: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch polls: {str(e)}"
        )


async def fetch_candlesticks_for_poll(poll: Dict[str, Any], market_client: Market) -> Dict[str, Any]:
    """
    Fetch candlestick data for a single poll from Kalshi API.

    Args:
        poll: Poll object with seriesTicker, marketTicker, and closedAt
        market_client: Kalshi Market API client

    Returns:
        Dict with poll and candlesticks data
    """
    series_ticker = poll.get('seriesTicker')
    market_ticker = poll.get('marketTicker')
    closed_at_raw = poll.get('closedAt')

    # Validate required fields (check for empty string too)
    if not series_ticker or not market_ticker or not closed_at_raw:
        logger.warning(f"Poll {poll.get('id')} missing required fields for candlesticks")
        return {
            "poll": poll,
            "candlesticks": [],
            "error": "Missing required fields (seriesTicker, marketTicker, or closedAt)"
        }

    try:
        # Parse closedAt timestamp and convert to Unix timestamp
        # Spring Boot sends LocalDateTime as array: [year, month, day, hour, minute, second, nanoseconds]
        if isinstance(closed_at_raw, list):
            # Convert array format to datetime
            year, month, day, hour, minute, second, nanos = closed_at_raw
            closed_at = datetime(year, month, day, hour, minute, second, nanos // 1000)  # Convert nanos to micros
        elif isinstance(closed_at_raw, str):
            # Handle ISO format string with optional microseconds
            closed_at = datetime.fromisoformat(closed_at_raw.replace('Z', '+00:00'))
        else:
            raise ValueError(f"Unexpected closedAt format: {type(closed_at_raw)}")

        start_ts = int(closed_at.timestamp())

        # Current time as end timestamp
        end_ts = int(datetime.now().timestamp())

        # Fetch candlesticks with 60-minute interval
        logger.info(f"Fetching candlesticks for poll {poll.get('id')}: {series_ticker}/{market_ticker}")

        candlestick_data = await asyncio.wait_for(
            asyncio.to_thread(
                market_client.get_market_candlesticks,
                series_ticker=series_ticker,
                ticker=market_ticker,
                start_ts=start_ts,
                end_ts=end_ts,
                period_interval=60
            ),
            timeout=45.0
        )

        candlesticks = candlestick_data.get('candlesticks', [])
        logger.info(f"Fetched {len(candlesticks)} candlesticks for poll {poll.get('id')}")

        return {
            "poll": poll,
            "candlesticks": candlesticks
        }

    except asyncio.TimeoutError:
        logger.error(f"Timeout fetching candlesticks for poll {poll.get('id')}")
        return {
            "poll": poll,
            "candlesticks": [],
            "error": "API timeout"
        }
    except Exception as e:
        logger.error(f"Error fetching candlesticks for poll {poll.get('id')}: {e}", exc_info=True)
        return {
            "poll": poll,
            "candlesticks": [],
            "error": str(e)
        }


@router.get("/history-with-candlesticks")
@cache_response(ttl=21600)  # 6 hours = 21600 seconds
async def get_poll_history_with_candlesticks() -> Dict[str, Any]:
    """
    Get all closed polls with their market candlestick data.

    Returns array of objects containing poll data and candlesticks.
    Cached for 6 hours to reduce Kalshi API load.

    Response format:
    {
        "success": true,
        "data": [
            {
                "poll": { ... poll object ... },
                "candlesticks": [ ... candlestick array ... ]
            }
        ]
    }
    """
    try:
        logger.info("Fetching poll history with candlesticks")

        # 1. Fetch all closed polls from Spring Boot
        closed_polls = await fetch_polls_from_springboot()

        if not closed_polls:
            return {
                "success": True,
                "data": []
            }

        # 2. Filter out tied polls (where yes_votes == no_votes)
        non_tied_polls = [ poll for poll in closed_polls if poll.get("optionAVotes") != poll.get("optionBVotes") ]
        logger.info(f"Filtered out {len(closed_polls) - len(non_tied_polls)} tied polls")

        # 3. Initialize Kalshi Market client
        market_client = Market()

        # 4. Fetch candlesticks for all non-tied polls in parallel
        tasks = [
            fetch_candlesticks_for_poll(poll, market_client)
            for poll in non_tied_polls
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 4. Filter out exceptions and only include polls with candlesticks
        poll_data = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Exception in candlestick fetch: {result}")
                continue
            # Only include polls that successfully fetched candlesticks
            if result.get('candlesticks') and len(result['candlesticks']) > 0:
                poll_data.append(result)
            elif result.get('error'):
                logger.warning(f"Skipping poll {result['poll'].get('id')}: {result['error']}")

        logger.info(f"Successfully fetched candlesticks for {len(poll_data)} polls")

        return {
            "success": True,
            "data": poll_data
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in poll history endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while fetching poll history"
        )
