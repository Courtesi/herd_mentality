import json
import logging

import websockets

from ..authenticator import Authenticator

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class BasicClient:

    def __init__(self):
        self.message_id = 0
        self.ws = None
        self.auth = Authenticator()
        self.base_url = self.auth.WS_PROD_URL
        self.path = self.auth.WS_PATH

        self.channels = ["orderbook_delta", "ticker", "trade", "fill", "market_positions", "market_lifecycle_v2",
                         "multivariate", "communications"]

    async def connect(self):
        logger.info("Attempting to connect to WebSocket: %s", self.base_url)
        ws_headers = self.auth.create_headers(self.base_url, "GET")

        async with websockets.connect(self.base_url, additional_headers=ws_headers) as websocket:
            self.ws = websocket
            logger.info("Connected to WebSocket: %s", self.base_url)
            await self.on_open()
            await self.handler()

    async def on_open(self):
        logger.debug("WebSocket connection opened.")

    async def on_message(self, message: dict):
        logger.debug("Received message: %s\n", str(message))

    async def on_error(self, error):
        logger.error("An error occurred: %s", error)

    async def on_close(self, close_status_code, close_msg):
        logger.warning(
            "WebSocket connection closed with code=%s, message=%s",
            close_status_code,
            close_msg,
        )

    async def subscribe(self, channels: list[str], tickers: list[str] = []):
        subscription_message = {
            "id": self.message_id,
            "cmd": "subscribe",
            "params": {"channels": channels},
        }

        if len(tickers) > 1:
            subscription_message["params"]["market_tickers"] = tickers
        elif len(tickers) == 1:
            subscription_message["params"]["market_ticker"] = tickers[0]
        else:
            logger.info(
                "No tickers provided for subscribe command with channels=%s. Skipping.",
                channels,
            )
            return

        logger.info(
            "Subscribing with message_id=%s to channels=%s, tickers=%s",
            self.message_id,
            channels,
            tickers,
        )

        await self.ws.send(json.dumps(subscription_message))
        self.message_id += 1
        logger.debug(
            "Subscription message sent. Incremented message_id to %s",
            self.message_id,
        )
    
    async def unsubscribe(self, sids: list[int]):
        unsubscription_message = {
            "id": self.message_id,
            "cmd": "unsubscribe",
            "params": {"sids": sids},
        }

        logger.info(
            "Unsubscribing with message_id=%s from sids=%s",
            self.message_id,
            sids,
        )

        await self.ws.send(json.dumps(unsubscription_message))
        self.message_id += 1
        logger.debug(
            "Unsubscription message sent. Incremented message_id to %s",
            self.message_id,
        )

    async def list_subscriptions(self):
        list_message = {
            "id": self.message_id,
            "cmd": "list_subscriptions",
        }

        logger.info(
            "Listing subscriptions with message_id=%s",
            self.message_id,
        )

        await self.ws.send(json.dumps(list_message))
        self.message_id += 1
        logger.debug(
            "List subscriptions message sent. Incremented message_id to %s",
            self.message_id,
        )

    async def update_subscription(self, sid, action, tickers: list[str] = []):
        update_message = {
            "id": self.message_id,
            "cmd": "update_subscription",
            "params": {
                "sid": sid,
            },
            "action": action
        }

        if len(tickers) > 1:
            update_message["params"]["market_tickers"] = tickers
        elif len(tickers) == 1:
            update_message["params"]["market_ticker"] = tickers[0]
        else:
            logger.info(
                "No tickers provided for update_subscription with sid=%s. Skipping.",
                sid,
            )
            return

        logger.info(
            "Updating subscription with message_id=%s for sid=%s to tickers=%s",
            self.message_id,
            sid,
            tickers,
        )

        await self.ws.send(json.dumps(update_message))
        self.message_id += 1
        logger.debug(
            "Update subscription message sent. Incremented message_id to %s",
            self.message_id,
        )

    def add_markets_to_subscription(self, sid, tickers: list[str]):
        return self.update_subscription(sid, "add_markets", tickers)
    
    def remove_markets_from_subscription(self, sid, tickers: list[str]):
        return self.update_subscription(sid, "remove_markets", tickers)

    async def handler(self):
        try:
            async for message in self.ws:
                await self.on_message(json.loads(message))
        except websockets.ConnectionClosed as e:
            await self.on_close(e.code, e.reason)
        except Exception as e:
            await self.on_error(e)