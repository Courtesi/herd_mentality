#!/usr/bin/env python3
"""
Test script for SSE functionality.
Run this to test the SSE endpoints without a real trading bot.
"""

import asyncio
import httpx
import json
import time


async def test_sse_connection():
    """Test SSE connection to the FastAPI server"""
    print("Testing SSE connection...")

    try:
        async with httpx.AsyncClient() as client:
            # Test trade-focused SSE endpoint
            print("Connecting to trade-focused SSE endpoint...")

            async with client.stream(
                "GET",
                "http://localhost:8000/api/python/sse/trading?events=new_trades,bot_status,heartbeat",
                timeout=30.0
            ) as response:

                if response.status_code == 200:
                    print("✅ SSE connection established")

                    # Read a few events
                    event_count = 0
                    async for line in response.aiter_lines():
                        if line.strip():
                            print(f"Received: {line}")
                            event_count += 1

                            if event_count >= 5:  # Stop after 5 events
                                break

                    print(f"✅ Received {event_count} events successfully")

                else:
                    print(f"❌ SSE connection failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Error testing SSE: {e}")


async def test_sse_endpoints():
    """Test various SSE endpoints"""
    endpoints = [
        "/api/python/sse/trading",
        "/api/python/sse/portfolio",
        "/api/python/sse/trades",
        "/api/python/sse/status"
    ]

    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            try:
                print(f"Testing {endpoint}...")
                response = await client.get(f"http://localhost:8000{endpoint}", timeout=5.0)

                # For SSE endpoints, we expect them to start streaming
                # We'll just check if they respond correctly
                if response.status_code == 200:
                    print(f"✅ {endpoint} - OK")
                else:
                    print(f"❌ {endpoint} - Failed ({response.status_code})")

            except httpx.TimeoutException:
                print(f"✅ {endpoint} - OK (timeout expected for streaming endpoint)")
            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")


async def test_sse_stats():
    """Test SSE statistics endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/python/sse/stats")

            if response.status_code == 200:
                stats = response.json()
                print("✅ SSE Stats:")
                print(f"  - Connected clients: {stats['sse']['connected_clients']}")
                print(f"  - Total connections: {stats['sse']['total_connections']}")
                print(f"  - Polling active: {stats['polling']['is_polling']}")
                print(f"  - Bot status: {stats['polling']['bot_status']}")
            else:
                print(f"❌ Stats endpoint failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Error getting stats: {e}")


async def test_broadcast():
    """Test manual event broadcast"""
    try:
        async with httpx.AsyncClient() as client:
            # Send test trade event
            test_data = {
                "trades": [
                    {
                        "timestamp": time.time(),
                        "ticker": "TEST-TICKER",
                        "side": "BUY",
                        "quantity": 10,
                        "price": 0.55,
                        "trade_id": "test_123"
                    }
                ],
                "count": 1,
                "source": "test_script"
            }

            response = await client.post(
                "http://localhost:8000/api/python/sse/broadcast",
                params={"event_type": "new_trades"},
                json=test_data
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Broadcast successful to {result['clients_targeted']} clients")
            else:
                print(f"❌ Broadcast failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Error broadcasting: {e}")


async def main():
    """Run all tests"""
    print("🧪 Starting SSE Tests")
    print("=" * 50)

    # First, test if the server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/python/health")
            if response.status_code == 200:
                print("✅ FastAPI server is running")
            else:
                print("❌ FastAPI server not responding correctly")
                return
    except Exception as e:
        print(f"❌ Cannot connect to FastAPI server: {e}")
        print("💡 Make sure to run: python main.py")
        return

    print("\n1. Testing SSE endpoints...")
    await test_sse_endpoints()

    print("\n2. Testing SSE statistics...")
    await test_sse_stats()

    print("\n3. Testing event broadcast...")
    await test_broadcast()

    print("\n4. Testing live SSE connection...")
    await test_sse_connection()

    print("\n🎉 SSE tests completed!")
    print("\n💡 To test with a real frontend, connect to:")
    print("   http://localhost:8000/api/python/sse/trading")
    print("\n📝 Expected SSE events:")
    print("   - new_trades: Trade executions (BUY/SELL)")
    print("   - bot_status: Bot online/offline status")
    print("   - heartbeat: Keep-alive pings")
    print("\n🎯 Frontend should calculate positions from trade history")


if __name__ == "__main__":
    asyncio.run(main())