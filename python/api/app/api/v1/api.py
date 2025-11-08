"""
Main API router that aggregates all v1 endpoints.
"""

from fastapi import APIRouter

from . import portfolio, sse, bot_webhooks, polls

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
# api_router.include_router(markets.router, prefix="/markets", tags=["markets"])
api_router.include_router(sse.router, prefix="", tags=["sse", "real-time"])
api_router.include_router(bot_webhooks.router, prefix="/bot", tags=["bot", "webhooks"])
api_router.include_router(polls.router, prefix="/polls", tags=["polls"])


@api_router.get("/")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Prediction Investor API",
        "version": "1.0.0",
        "description": "Portfolio and market data API for prediction markets",
        "endpoints": {
            "portfolio": {
                "balance": "/portfolio/balance",
                "positions": "/portfolio/positions",
                "fills": "/portfolio/fills",
                "summary": "/portfolio/summary"
            },
            "polls": {
                "history_with_candlesticks": "/polls/history-with-candlesticks (closed polls with Kalshi candlesticks)"
            },
            "sse": {
                "trading_stream": "/sse/trading (new_trades + bot_status)",
            },
            "bot_webhooks": {
                "online": "/bot/webhook/online (bot startup notification)",
                "offline": "/bot/webhook/offline (bot shutdown notification)",
                "status": "/bot/webhook/status (webhook system status)",
                "test": "/bot/webhook/test (test webhook delivery)"
            }
        }
    }