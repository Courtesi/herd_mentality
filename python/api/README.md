# Prediction Investor FastAPI Backend

FastAPI backend for serving portfolio and market data through `/api/python/*` endpoints.

## Architecture

This FastAPI service works alongside the Spring Boot authentication service:
- **Spring Boot** (`/api/auth/*`) - User authentication and management
- **FastAPI** (`/api/python/*`) - Portfolio and market data (public endpoints)

## Features

- **Real-time Trade Updates**: Server-Sent Events (SSE) for live trade executions (BUY/SELL)
- **Trade-Focused Architecture**: Tracks individual trades rather than position aggregations
- **Bot Polling**: Polls trading bot every 3 seconds for new trades
- **Smart Fallback**: Bot live data → Redis cache → Kalshi API fallback chain
- **Change Detection**: Only sends SSE events when new trades are detected
- **Multiple SSE Streams**: Separate streams for trades, bot status, and general trading activity
- **Frontend Trade Management**: Frontend handles position calculations from trade history
- **Redis Caching**: Shares Redis instance with Spring Boot using different key prefixes (`python:*`)
- **Kalshi Integration**: Uses existing Kalshi client from parent directory

## Project Structure

```
api/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── app/
│   ├── core/
│   │   ├── config.py      # Settings and configuration
│   │   └── redis_client.py # Redis caching client
│   ├── services/
│   │   └── kalshi_service.py # Kalshi API integration
│   ├── api/v1/
│   │   ├── portfolio.py   # Portfolio endpoints
│   │   ├── markets.py     # Market data endpoints
│   │   └── api.py         # Router aggregator
│   ├── models/            # Data models (future)
│   └── utils/             # Utilities (future)
```

## Installation

1. Install dependencies:
```bash
cd python/api
pip install -r requirements.txt
```

2. Copy environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the application:
```bash
python main.py
```

The API will be available at: `http://localhost:8000`

## API Endpoints

All endpoints are prefixed with `/api/python`:

### Portfolio Endpoints (REST)
- `GET /api/python/portfolio/balance` - Current portfolio balance
- `GET /api/python/portfolio/positions` - Current positions
- `GET /api/python/portfolio/fills?limit=100` - Trade history
- `GET /api/python/portfolio/trades/live` - Live trades from bot
- `GET /api/python/portfolio/summary` - Complete portfolio overview

### Market Endpoints (REST)
- `GET /api/python/markets/` - Available markets
- `GET /api/python/markets/{ticker}` - Specific market data

### Real-time Endpoints (SSE)
- `GET /api/python/sse/trading` - Main trading stream (new trades + bot status)
- `GET /api/python/sse/portfolio` - Trade activity stream (same as trades)
- `GET /api/python/sse/trades` - Trade executions only (BUY/SELL events)
- `GET /api/python/sse/status` - Bot status and heartbeat only
- `GET /api/python/sse/stats` - SSE statistics and performance metrics
- `GET /api/python/sse/clients` - Connected clients information

### Utility Endpoints
- `GET /api/python/health` - Health check
- `GET /api/python/` - API information

## Real-time Architecture

### Data Flow
```
Trading Bot (port 9000) ←3sec polling← FastAPI ←SSE← Frontend
     ↓ (in-memory trades)                   ↓
                                      Redis Cache
                                           ↓
                                     Kalshi API (fallback)
```

### Trade-Focused Architecture
- **Frontend Responsibility**: Calculates positions from trade history
- **Backend Responsibility**: Streams individual trade executions (BUY/SELL)
- **Bot Polling**: Every 3 seconds (less aggressive than position tracking)
- **SSE Events**: Only triggered by new trade executions, not position changes

### Bot Communication
- FastAPI polls bot every **3 seconds** for new trades
- Only sends SSE events when new trades are detected
- Automatic fallback to Kalshi API when bot is offline
- Bot exposes simple HTTP endpoints:
  - `GET /health` - Bot status and trade count
  - `GET /trades` - Recent trade history (last 100 trades)

### SSE Events
- `new_trades` - New trade executions (BUY/SELL with ticker, quantity, price)
- `bot_status` - Bot online/offline status changes
- `heartbeat` - Keep-alive pings (every 30s)

## Caching Strategy

- **Short Cache (5min)**: Market data
- **Medium Cache (1hr)**: Portfolio balance, positions
- **Long Cache (1day)**: Trade history, fills
- **No Cache**: Live trades from bot

## Configuration

Key environment variables:

```env
# Redis (shared with Spring Boot)
REDIS_HOST=localhost
REDIS_KEY_PREFIX=python:

# Bot Integration
BOT_STATUS_ENDPOINT=http://localhost:9000/status
BOT_TRADES_ENDPOINT=http://localhost:9000/trades

# Kalshi API (inherits from parent .env)
KALSHI_API_KEY=your-api-key
KALSHI_RSA_KEY_PATH=path/to/key
```

## Docker Integration

This service will be containerized to work with:
- Shared Redis container (for caching and Spring Boot sessions)
- MySQL container (for data persistence)
- Apache reverse proxy (for `/api/python/*` routing)

## Development

- **Hot Reload**: Enabled by default in development
- **API Docs**: Available at `/api/python/docs`
- **Logging**: Configured for debugging Redis and Kalshi integration

## Testing

### Test SSE Functionality
```bash
# 1. Start the FastAPI server
python main.py

# 2. Run SSE tests
python test_sse.py

# 3. Test with curl
curl -N http://localhost:8000/api/python/sse/trading

# 4. Check SSE statistics
curl http://localhost:8000/api/python/sse/stats
```

### Frontend SSE Connection
```javascript
// Connect to trade-focused SSE stream
const eventSource = new EventSource('/api/python/sse/trading');

eventSource.addEventListener('new_trades', (event) => {
    const data = JSON.parse(event.data);
    console.log('New trades:', data.trades);

    // Frontend manages position calculation
    data.trades.forEach(trade => {
        updateTradeHistory(trade);
        recalculatePositions(trade.ticker);
    });
});

eventSource.addEventListener('bot_status', (event) => {
    const data = JSON.parse(event.data);
    console.log('Bot status:', data.status);
    updateBotStatusIndicator(data.status);
});

// Example trade data structure:
// {
//   "trades": [
//     {
//       "timestamp": 1698676800.123,
//       "ticker": "PRES24-GOP",
//       "side": "BUY",
//       "quantity": 50,
//       "price": 0.65,
//       "trade_id": "abc123"
//     }
//   ],
//   "count": 1,
//   "source": "bot_live"
// }
```

## Phase 1 Complete ✅

**What's Working:**
- ✅ Trade-focused SSE streaming infrastructure
- ✅ Bot polling service (3 second intervals)
- ✅ Change detection for new trade executions only
- ✅ Multiple SSE endpoints for different event types
- ✅ Fallback to Kalshi API when bot offline
- ✅ Redis caching integration
- ✅ Frontend-managed position calculation architecture

**Architecture Benefits:**
- 🚀 **Simplified Backend**: No complex position tracking or aggregation
- 📊 **Frontend Control**: Frontend calculates and displays positions from trades
- 🔄 **Trade History**: Shows all BUY/SELL events, even for closed positions
- ⚡ **Performance**: 3-second polling is sufficient for trade-level updates
- 🛠️ **Maintenance**: Easier to debug and maintain trade-only tracking

**Next: Phase 2** - Build the trading bot with in-memory trades and HTTP interface

## Next Steps

- [ ] **Phase 2**: Trading bot with in-memory storage and HTTP endpoints
- [ ] **Phase 3**: Frontend SSE integration
- [ ] Add MySQL database integration for historical data
- [ ] Set up Docker containerization
- [ ] Production deployment