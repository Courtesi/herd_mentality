"""
FastAPI application for Prediction Investor platform.
Serves portfolio and market data through /api/python/* endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
import sys

from app.core.config import settings
from app.core.redis_client import redis_client
from app.api.v1.api import api_router
from app.services.sse_manager import sse_manager
from app.services.poll_scheduler import poll_scheduler

# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await redis_client.connect()
    await sse_manager.start()
    await poll_scheduler.start()
    # await bot_polling_service.start_polling(sse_manager)
    logger.info("All services started successfully")

    yield

    # Shutdown
    # await bot_polling_service.stop_polling()
    await poll_scheduler.stop()
    await sse_manager.stop()
    await redis_client.disconnect()
    logger.info("All services stopped successfully")


app = FastAPI(
    title="Prediction Investor API",
    description="Portfolio and market data API for prediction markets",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/python/docs",
    redoc_url="/api/python/redoc",
    openapi_url="/api/python/openapi.json"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API routes with /api/python prefix
app.include_router(api_router, prefix="/api/python")


@app.get("/api/python/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "prediction-investor-api"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )