"""
Service layer for Kalshi API integration.
Wraps the existing Kalshi client for use in FastAPI.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import httpx
import logging
import time

import aiomysql
from datetime import datetime
import json

# Add the parent directory to sys.path to import existing Kalshi client
current_dir = Path(__file__).parent
python_dir = current_dir.parent.parent.parent  # Go up to python/ directory
sys.path.append(str(python_dir))

from exchanges.kalshi.rest.portfolio import Portfolio
from exchanges.kalshi.rest.markets import Market
from exchanges.kalshi.authenticator import Authenticator
from app.core.config import settings
from app.core.redis_client import cache_response

from .sse_manager import sse_manager

logger = logging.getLogger(__name__)


def check_bot_status() -> dict[str, Any]:
    return sse_manager.get_bot_status()


class KalshiService:
    """Service for interacting with Kalshi API"""

    def __init__(self):
        self.authenticator = Authenticator()
        self.portfolio_client = Portfolio()
        self.market_client = Market()
        self.bot_client = httpx.AsyncClient()
        self.db_pool = None  # Initialize connection pool

    async def _ensure_db_pool(self):
        if self.db_pool is None:
            self.db_pool = await aiomysql.create_pool(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                db=settings.MYSQL_DATABASE,
                autocommit=True,
                minsize=1,
                maxsize=10
            )

    async def _get_db_connection(self):
        await self._ensure_db_pool()
        return await self.db_pool.acquire()


    async def get_bot_live_data(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Get live data from the trading bot if it's online"""
        try:
            response = await self.bot_client.get(endpoint, timeout=5.0)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get bot data from {endpoint}: {e}")
            return None

    @cache_response(ttl=settings.CACHE_TTL_MEDIUM)
    async def get_portfolio_balance(self) -> Dict[str, Any]:
        logger.info("Returning portfolio balance from Kalshi API")
        try:
            balance_object = self.portfolio_client.get_balance()
            balance = balance_object.get("balance")
            portfolio_value = balance_object.get("portfolio_value")
            return {
                "balance": balance,
                "portfolio_value": portfolio_value,
                "timestamp": time.time()  # Kalshi doesn't provide timestamp
            }
        except Exception as e:
            logger.error(f"Failed to get balance from Kalshi: {e}")
            raise

    @cache_response(ttl=settings.CACHE_TTL_MEDIUM)
    async def get_portfolio_positions(self) -> Dict[str, Any]:
        logger.info("Returning positions from Kalshi API")
        try:
            positions_object = self.portfolio_client.get_positions(settlement_status="all")
            market_positions = positions_object.get("market_positions")

            # market_tickers = [market.get("ticker") for market in market_positions]

            # markets_dict = await self.get_market_data(market_tickers)

            return {
                "market_positions": market_positions,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Failed to get positions from Kalshi: {e}")
            raise

    @cache_response(ttl=settings.CACHE_TTL_MEDIUM)
    async def get_portfolio_fills(self, limit: int = 100) -> Dict[str, Any]:
        """Get recent portfolio fills (trade history) with market metadata"""
        try:
            fills_response = self.portfolio_client.get_fills(limit=limit)
            fills = fills_response.get("fills")

            # Extract unique tickers from fills
            fill_tickers = list(set([fill.get("ticker") for fill in fills if fill.get("ticker")]))

            # Get market metadata for all tickers in fills
            markets_dict = await self.get_market_data(fill_tickers) if fill_tickers else {}

            return {
                "fills": fills,
                "markets_data": markets_dict,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Failed to get fills from Kalshi: {e}")
            raise

    async def get_market_data(self, ticker_list: list[str]) -> Dict[str, Any]:

        if not ticker_list:
            return {"source": "none", "data": {}}

        # Check database for market metadata
        db_results = await self._check_multiple_tickers_in_db(ticker_list)

        # Identify which tickers are missing from database
        missing_tickers = [ticker for ticker in ticker_list if ticker not in db_results]

        final_markets_dict = db_results.copy()

        # Only fetch from API if we've never seen this ticker before
        if missing_tickers:
            # logger.error(f"New tickers not in database: {missing_tickers}. Fetching metadata from Kalshi API")

            missing_tickers_str = ','.join(missing_tickers)

            try:
                markets_object = self.market_client.get_markets(tickers=missing_tickers_str)
                markets = markets_object.get("markets", [])

                api_markets_dict = {}
                for market in markets:
                    title = market.get("title")
                    ticker = market.get("ticker")
                    yes_sub_title = market.get("yes_sub_title")
                    no_sub_title = market.get("no_sub_title")
                    api_markets_dict[ticker] = {
                        "title": title,
                        "yes_sub_title": yes_sub_title,
                        "no_sub_title": no_sub_title
                    }

                # Store metadata permanently for these tickers
                await self._store_multiple_tickers_in_db(api_markets_dict)

                final_markets_dict.update(api_markets_dict)

            except Exception as e:
                logger.error(f"Failed to get market metadata from API: {e}")
                return final_markets_dict


        return final_markets_dict


    async def _check_multiple_tickers_in_db(self, ticker_list: List[str]) -> Dict[str, Dict]:
        if not ticker_list:
            return {}

        try:
            await self._ensure_db_pool()
            async with self.db_pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    placeholders = ','.join(['%s'] * len(ticker_list))
                    query = f"""
                    SELECT ticker, data
                    FROM market_data
                    WHERE ticker IN ({placeholders})
                    """

                    await cursor.execute(query, ticker_list)
                    results = await cursor.fetchall()

                    db_markets = {}
                    for ticker, data_json in results:
                        market_data = json.loads(data_json)
                        db_markets[ticker] = market_data

                    logger.info(f"Found {len(db_markets)} tickers in database out of {len(ticker_list)} requested")
                    return db_markets
        except Exception as e:
            logger.error(f"Database check failed for multiple tickers: {e}")
            return {}


    async def _store_multiple_tickers_in_db(self, markets_dict: Dict[str, Dict]):
        if not markets_dict:
            return

        try:
            await self._ensure_db_pool()
            async with self.db_pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Store each ticker individually
                    query = """
                    INSERT INTO market_data (ticker, data, created_at)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        data = VALUES(data),
                        created_at = VALUES(created_at)
                    """

                    now = datetime.now()
                    for ticker, market_data in markets_dict.items():
                        await cursor.execute(query, (ticker, json.dumps(market_data), now))

                    logger.debug(f"Stored {len(markets_dict)} tickers in database")

        except Exception as e:
            logger.error(f"Failed to store multiple tickers: {e}")




    async def cleanup(self):
        await self.bot_client.aclose()

        # Close database pool
        if self.db_pool:
            self.db_pool.close()
            await self.db_pool.wait_closed()


# Global service instance
kalshi_service = KalshiService()