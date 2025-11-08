from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .basic_rest import BasicRest
from .models.models import Action, Side, TimeInForce, CountFilter

class Portfolio(BasicRest):

    def __init__(self):
        super().__init__()

    def get_balance(self):
        url = f"{self.base_url}/portfolio/balance"

        return self._authenticated_get_request(url)
    
    def get_fills(self,
                  ticker: str = None,
                  order_id: str = None,
                  min_ts: int = None,
                  max_ts: int = None,
                  limit: int = None,
                  cursor: str = None):
        url = f"{self.base_url}/portfolio/fills"
        kwargs = self.drop_none(self.get_kwargs())

        return self._authenticated_get_request(url, **kwargs)
    
    def get_order_groups(self):
        url = f"{self.base_url}/portfolio/order_groups"

        return self._authenticated_get_request(url)

    def create_order_group(self,
                           contracts_limit: int):
        url = f"{self.base_url}/portfolio/order_groups/create"

        payload = {"contracts_limit": contracts_limit}

        return self._authenticated_post_request(url, data=payload)
    
    def get_order_group(self,
                        order_group_id: str):
        url = f"{self.base_url}/portfolio/order_groups/{order_group_id}"
        return self._authenticated_get_request(url)
    
    def delete_order_group(self,
                           order_group_id: str):
        url = f"{self.base_url}/portfolio/order_groups/{order_group_id}"
        return self._authenticated_del_request(url)
    
    def reset_order_group(self,
                          order_group_id: str):
        url = f"{self.base_url}/portfolio/order_groups/{order_group_id}/reset"
        return self._authenticated_put_request(url)
    
    def get_orders(self,
                   market_ticker: str = None,
                   event_ticker: str = None,
                   min_ts: int = None,
                   max_ts: int = None,
                   status: str = None,
                   limit: int = None,
                   cursor: str = None):
        url = f"{self.base_url}/portfolio/orders"
        kwargs = self.drop_none(self.get_kwargs())
        return self._authenticated_get_request(url, **kwargs)
    
    def create_order(self, order: dict):
        url = f"{self.base_url}/portfolio/orders"
        return self._authenticated_post_request(url, data=order)
    
    
    def batch_create_orders(self, orders: list[dict]):
        print("Advanced Access only for Batch Create Orders")

        url = f"{self.base_url}/portfolio/orders/batched"
        payload = {"orders": orders}
        return self._authenticated_post_request(url, data=payload)
    
    def batch_cancel_orders(self, order_ids: list[str]):
        print("Advanced Access Only for Batch Cancel Orders")
        url = f"{self.base_url}/portfolio/orders/batched"
        payload = {"ids", order_ids}
        return self._authenticated_del_request(url, data=payload)
    
    def get_queue_positions_for_orders(self, market_tickers: str = None, event_ticker: str = None):
        if not market_tickers and not event_ticker:
            print("Need to specify one of market_tickers or event_ticker")
            return
        
        url = f"{self.base_url}/portfolio/orders/queue_positions"

        kwargs = self.drop_none(self.get_kwargs())

        return self._authenticated_get_request(url, **kwargs)
    
    def get_order(self, order_id: str):
        url = f"{self.base_url}/portfolio/orders/{order_id}"
        return self._authenticated_get_request(url)
    
    def cancel_order(self, order_id: str):
        url = f"{self.base_url}/portfolio/orders/{order_id}"
        return self._authenticated_del_request(url)
    
    def amend_order(self, order_id: str, new_order: dict):
        url = f"{self.base_url}/portfolio/orders/{order_id}/amend"
        print(f"url: {url}\nnew_order: {new_order}")
        return self._authenticated_post_request(url, data=new_order)
    
    def decrease_order(self, order_id: str, reduce_by: int = None, reduce_to: int = None):
        if reduce_by == None and reduce_to == None:
            print("Need to specify one of reduce_by or reduce_to")
            return
        
        if reduce_by != None and reduce_to != None:
            print("Can only specify one of reduce_by and reduce_to")
            return
        
        if reduce_to == 0:
            print("Cannot decrease order to 0. Use cancel order instead")
            return
        
        url = f"{self.base_url}/portfolio/orders/{order_id}/decrease"
        payload = self.drop_none(self.get_kwargs())
        return self._authenticated_post_request(url, data=payload)
    
    def get_queue_position_for_order(self, order_id: str):
        url = f"{self.base_url}/portfolio/orders/{order_id}/queue_position"

        return self._authenticated_get_request(url)
    
    def get_positions(self,
                      cursor: str = None,
                      limit: int = None,
                      count_filter: CountFilter = None,
                      settlement_status: str = None,
                      ticker: str = None,
                      event_ticker: str = None):
        url = f"{self.base_url}/portfolio/positions"
        kwargs = self.drop_none(self.get_kwargs())
        return self._authenticated_get_request(url, **kwargs)
    
    def get_settlements(self,
                        limit: int = None,
                        ticker: str = None,
                        event_ticker: str = None,
                        min_ts: int = None,
                        max_ts: int = None,
                        cursor: str = None):
        url = f"{self.base_url}/portfolio/settlements"
        kwargs = self.drop_none(self.get_kwargs())
        return self._authenticated_get_request(url, **kwargs)
    
    def get_resting_orders_value(self):
        print("Only intended for FCM members")
        
        url = f"{self.base_url}/portfolio/summary/total_resting_order_value"
        return self._authenticated_get_request(url)