import base64
import json
import urllib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding

import requests
import datetime

import os
from dotenv import load_dotenv

import websockets
import asyncio

load_dotenv()

class Authenticator:
    def __init__(self):
        self.name = "Kalshi"
        self.api_key = os.getenv("KALSHI_API_KEY")
        self.rsa_key_path = os.getenv('KALSHI_RSA_KEY_PATH')
        self.jsonstore_path = "kalshi_jsonstore.json"

        self.PROD_URL = 'https://api.elections.kalshi.com'
        self.DEMO_URL = 'https://demo-api.kalshi.co'
        self.PROD_PATH = "/trade-api/v2"

        self.WS_PROD_URL = 'wss://api.elections.kalshi.com/trade-api/ws/v2'
        self.WS_BASE_URL = self.WS_PROD_URL

        self.WS_PATH = "/trade-api/ws/v2"

    def load_private_key(self, key_path):
        """Load the private key from file."""
        with open(key_path, "rb") as f:
            # print("Loaded private key from:", key_path)
            # print(f.read())
            return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

    def create_signature(self, private_key, timestamp, method, path):
        """Create the request signature."""
        # Strip query parameters before signing
        path_without_query = path.split('?')[0]
        message = f"{timestamp}{method}{path_without_query}".encode('utf-8')
        signature = private_key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    
    def create_headers(self, url, method):
        private_key = self.load_private_key(self.rsa_key_path)
        timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
        path = urllib.parse.urlparse(url).path
        signature = self.create_signature(private_key, timestamp, method, path)

        headers = {
            "Content-Type": "application/json",
            "KALSHI-ACCESS-KEY": self.api_key,
            "KALSHI-ACCESS-SIGNATURE": signature,
            "KALSHI-ACCESS-TIMESTAMP": timestamp
        }

        return headers
    
    # def get(self, path, base_url=BASE_URL):
    #     """Make an authenticated GET request to the Kalshi API."""
    #     headers = self.create_headers(path, base_url)

    #     return requests.get(base_url + path, headers=headers)
    

    # def get_markets(self):
    #     response = self.get("/trade-api/v2/markets")

    #     print(response.json())

    #     return response.json()
    
    # def get_balance(self):
    #     response = self.get("/trade-api/v2/portfolio/balance")

    #     print(f"Your balance: ${response.json()['balance'] / 100:.2f}")

    # def subscribe_to_orderbook(self, market_ticker):
    #     subscribe_msg = {
    #         "id": 1,
    #         "cmd": "subscribe",
    #         "params": {
    #             "channels": ["orderbook_delta"],
    #             "market_ticker": market_ticker
    #         }
    #     }

    #     return subscribe_msg

    # def start_trading(self, base_url=WS_BASE_URL):

    #     async def orderbook_websocket():
    #         ws_headers = self.create_headers("/orderbook_delta", base_url)

    #         async with websockets.connect(base_url, additional_headers=ws_headers) as websocket:
                
    #             while True:
    #                 # subscribe_msg = self.subscribe_to_orderbook("KXNFLANYTD-25OCT20TBDET-DETASTBROWN14")
                    
    #                 # await websocket.send(json.dumps(subscribe_msg))

    #                 # Process messages
    #                 async for message in websocket:
    #                     data = json.loads(message)
    #                     msg_type = data.get("type")

    #                     if msg_type == "subscribed":
    #                         print(f"Subscribed: {data}")

    #                     elif msg_type == "orderbook_snapshot":
    #                         print(f"Orderbook snapshot: {data}")

    #                     elif msg_type == "orderbook_delta":
    #                         # The client_order_id field is optional - only present when you caused the change
    #                         if 'client_order_id' in data.get('data', {}):
    #                             print(f"Orderbook update (your order {data['data']['client_order_id']}): {data}")
    #                         else:
    #                             print(f"Orderbook update: {data}")
                        
    #                     elif msg_type == "orderbook_snapshot":

    #                     elif msg_type == "error":
    #                         print(f"Error: {data}")

        
        
    #     asyncio.run(orderbook_websocket())
