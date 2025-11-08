from .basic_rest import BasicRest

class Reference(BasicRest):
    def __init__(self):
        super().__init__()
    
    def get_forecast_history(self, ticker):
        url = f"{self.base_url}/cached/events/{ticker}/forecast_history"
        return self.get(url)

    def get_exchange_announcements(self):
        url = f"{self.base_url}/exchange/announcements"
        return self.get(url)
    
    def get_exchange_schedule(self):
        url = f"{self.base_url}/exchange/schedule"
        return self.get(url)
    
    def get_exchange_status(self):
        url = f"{self.base_url}/exchange/status"
        return self.get(url)
    
    def get_user_data_timestamp(self):
        url = f"{self.base_url}/exchange/user_data_timestamp"
        return self.get(url)
    
    def get_series_fee_changes(self):
        url = f"{self.base_url}/series/fee_changes"
        return self.get(url)
    
    def get_series_event_candlesticks(self, 
        series_ticker, ticker, #Path parameters
        start_ts, end_ts, period_interval): #Query parameters
        url = f"{self.base_url}/series/{series_ticker}/events/{ticker}/candlesticks"
        return self.get(url, 
            start_ts=start_ts,
            end_ts=end_ts,
            period_interval=period_interval)