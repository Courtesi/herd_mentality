from .basic_rest import BasicRest

class Market(BasicRest):
    def __init__(self):
        super().__init__()
    
    def get_events(self,
                   limit: int = None,
                   cursor: str = None,
                   with_nested_markets: bool = None,
                   status: str = None,
                   series_ticker: str = None,
                   min_close_ts: int = None,
                   with_milestones: bool = None):
        url = f"{self.base_url}/events"
        kwargs = self.drop_none(self.get_kwargs())
        return self.get(url, **kwargs)
    
    def get_event(self,
                  event_ticker: str, with_nested_markets: bool = None):
        url = f"{self.base_url}/events/{event_ticker}"
        return self.get(url, with_nested_markets=with_nested_markets)
    
    def get_event_metadata(self, event_ticker: str):
        url = f"{self.base_url}/events/{event_ticker}/metadata"
        return self.get(url)
    
    def get_markets(self,
                    limit: int = None,
                    cursor: str = None,
                    event_ticker: str = None,
                    series_ticker: str = None,
                    max_close_ts: int = None,
                    min_close_ts: int = None,
                    status: str = None,
                    tickers: str = None):
        url = f"{self.base_url}/markets"
        kwargs = self.drop_none(self.get_kwargs())
        return self.get(url, **kwargs)
    
    def get_trades(self,
                   limit: int = None,
                   cursor: str = None,
                   ticker: str = None,
                   min_ts: int = None,
                   max_ts: int = None):
        url = f"{self.base_url}/markets/trades"
        kwargs = self.drop_none(self.get_kwargs())
        return self.get(url, **kwargs)
    
    def get_market(self, ticker: str):
        url = f"{self.base_url}/markets/{ticker}"
        return self.get(url)
    
    def get_market_order_book(self, ticker: str, depth: int = None):
        url = f"{self.base_url}/markets/{ticker}/orderbook"

        #kwargs works here because ticker is not optional
        kwargs = self.drop_none(self.get_kwargs())
        return self.get(url, **kwargs)
    
    def get_series_list(self, category: str,
                        include_product_metadata: bool = None,
                        tags: str = None):
        url = f"{self.base_url}/series"

        #kwargs should only capture include_product_metadata and tags
        kwargs = self.drop_none(self.get_kwargs())
        return self.get(url, category=category, **kwargs)
    
    def get_series(self, series_ticker: str):
        url = f"{self.base_url}/series/{series_ticker}"
        return self.get(url)
    
    def get_market_candlesticks(self, series_ticker: str,
                                ticker: str,
                                start_ts: int,
                                end_ts: int,
                                period_interval: int):
        url = f"{self.base_url}/series/{series_ticker}/markets/{ticker}/candlesticks"
        return self.get(url,
                        start_ts=start_ts,
                        end_ts=end_ts,
                        period_interval=period_interval)